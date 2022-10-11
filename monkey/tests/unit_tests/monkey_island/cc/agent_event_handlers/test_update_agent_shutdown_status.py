from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from tests.monkey_island import InMemoryAgentRepository

from common.agent_events import AgentShutdownEvent
from common.types import SocketAddress
from monkey_island.cc.agent_event_handlers import update_agent_shutdown_status
from monkey_island.cc.models import Agent
from monkey_island.cc.repository import IAgentRepository, StorageError, UnknownRecordError

AGENT_ID = UUID("1d8ce743-a0f4-45c5-96af-91106529d3e2")
MACHINE_ID = 11
CC_SERVER = SocketAddress(ip="10.10.10.100", port="5000")


def get_agent_object() -> Agent:
    return Agent(
        id=AGENT_ID, machine_id=MACHINE_ID, start_time=0, parent_id=None, cc_server=CC_SERVER
    )


TIMESTAMP = 123.321
AGENT_SHUTDOWN_EVENT = AgentShutdownEvent(source=AGENT_ID, timestamp=TIMESTAMP)


@pytest.fixture
def agent_repository() -> IAgentRepository:
    agent_repository = InMemoryAgentRepository()
    agent_repository.upsert_agent(get_agent_object())
    return agent_repository


def test_update_agent_shutdown_status(agent_repository):
    update_agent_shutdown_status_handler = update_agent_shutdown_status(agent_repository)

    update_agent_shutdown_status_handler(AGENT_SHUTDOWN_EVENT)

    assert agent_repository.get_agent_by_id(AGENT_ID).stop_time == datetime.utcfromtimestamp(
        TIMESTAMP
    )


def test_update_agent_shutdown_status__storage_error_caught(agent_repository):
    agent_repository.upsert_agent = MagicMock(side_effect=StorageError())
    update_agent_shutdown_status_handler = update_agent_shutdown_status(agent_repository)

    # error should not be raised
    update_agent_shutdown_status_handler(AGENT_SHUTDOWN_EVENT)


def test_update_agent_shutdown_status__unknown_record_error_raised(agent_repository):
    another_agent_shutdown_event = AgentShutdownEvent(
        source=UUID("012e7238-7b81-4108-8c7f-0787bc3f3c10"), timestamp=TIMESTAMP
    )
    update_agent_shutdown_status_handler = update_agent_shutdown_status(agent_repository)

    with pytest.raises(UnknownRecordError):
        update_agent_shutdown_status_handler(another_agent_shutdown_event)
