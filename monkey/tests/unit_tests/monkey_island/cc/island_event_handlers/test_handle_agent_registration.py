from ipaddress import IPv4Address, IPv4Interface
from itertools import count
from typing import Sequence
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from common import AgentRegistrationData
from monkey_island.cc.island_event_handlers import handle_agent_registration
from monkey_island.cc.models import Agent, Machine
from monkey_island.cc.repository import IAgentRepository, IMachineRepository, UnknownRecordError

AGENT_ID = UUID("860aff5b-d2af-43ea-afb5-62bac3d30b7e")

SEED_ID = 10

MACHINE = Machine(
    id=2,
    hardware_id=5,
    network_interfaces=[IPv4Interface("192.168.2.2/24")],
)

AGENT_REGISTRATION_DATA = AgentRegistrationData(
    id=AGENT_ID,
    machine_hardware_id=MACHINE.hardware_id,
    start_time=0,
    parent_id=None,
    cc_server="192.168.1.1:5000",
    network_interfaces=[IPv4Interface("192.168.1.2/24")],
)


@pytest.fixture
def machine_repository() -> IMachineRepository:
    machine_repository = MagicMock(spec=IMachineRepository)
    machine_repository.get_new_id = MagicMock(side_effect=count(SEED_ID))
    machine_repository.upsert_machine = MagicMock()
    machine_repository.get_machine_by_hardware_id = MagicMock(side_effect=UnknownRecordError)
    machine_repository.get_machines_by_ip = MagicMock(side_effect=UnknownRecordError)
    return machine_repository


@pytest.fixture
def agent_repository() -> IAgentRepository:
    agent_repository = MagicMock(spec=IAgentRepository)
    agent_repository.upsert_agent = MagicMock()
    return agent_repository


@pytest.fixture
def handler(machine_repository, agent_repository) -> handle_agent_registration:
    return handle_agent_registration(machine_repository, agent_repository)


def test_new_machine_added(handler, machine_repository):
    expected_machine = Machine(
        id=SEED_ID,
        hardware_id=AGENT_REGISTRATION_DATA.machine_hardware_id,
        network_interfaces=AGENT_REGISTRATION_DATA.network_interfaces,
    )
    machine_repository.get_machine_by_hardware_id = MagicMock(side_effect=UnknownRecordError)
    machine_repository.get_machines_by_ip = MagicMock(side_effect=UnknownRecordError)
    handler(AGENT_REGISTRATION_DATA)

    machine_repository.upsert_machine.assert_called_once()
    new_machine = machine_repository.upsert_machine.call_args_list[0][0][0]

    assert new_machine == expected_machine


def test_existing_machine_updated__hardware_id(handler, machine_repository):
    expected_updated_machine = Machine(
        id=MACHINE.id,
        hardware_id=MACHINE.hardware_id,
        network_interfaces=[
            AGENT_REGISTRATION_DATA.network_interfaces[0],
            MACHINE.network_interfaces[0],
        ],
    )
    machine_repository.get_machine_by_hardware_id = MagicMock(return_value=MACHINE)
    handler(AGENT_REGISTRATION_DATA)

    machine_repository.upsert_machine.assert_called_once()
    machine_repository.upsert_machine.assert_called_with(expected_updated_machine)


def test_existing_machine_updated__find_by_ip(handler, machine_repository):
    agent_registration_data = AgentRegistrationData(
        id=AGENT_ID,
        machine_hardware_id=5,
        start_time=0,
        parent_id=None,
        cc_server="192.168.1.1:5000",
        network_interfaces=[
            IPv4Interface("192.168.1.2/24"),
            IPv4Interface("192.168.1.4/24"),
            IPv4Interface("192.168.1.5/24"),
        ],
    )

    existing_machine = Machine(
        id=1,
        network_interfaces=[agent_registration_data.network_interfaces[-1]],
    )

    def get_machines_by_ip(ip: IPv4Address) -> Sequence[Machine]:
        if ip == existing_machine.network_interfaces[0].ip:
            return [existing_machine]

        raise UnknownRecordError

    expected_updated_machine = existing_machine.copy()
    expected_updated_machine.hardware_id = agent_registration_data.machine_hardware_id
    expected_updated_machine.network_interfaces = agent_registration_data.network_interfaces

    machine_repository.get_machine_by_hardware_id = MagicMock(side_effect=UnknownRecordError)
    machine_repository.get_machines_by_ip = MagicMock(side_effect=get_machines_by_ip)

    handler(agent_registration_data)

    machine_repository.upsert_machine.assert_called_once()
    machine_repository.upsert_machine.assert_called_with(expected_updated_machine)


def test_hardware_id_mismatch(handler, machine_repository):
    existing_machine = Machine(
        id=1,
        hardware_id=AGENT_REGISTRATION_DATA.machine_hardware_id + 99,
        network_interfaces=AGENT_REGISTRATION_DATA.network_interfaces,
    )

    machine_repository.get_machine_by_hardware_id = MagicMock(side_effect=UnknownRecordError)
    machine_repository.get_machines_by_ip = MagicMock(return_value=[existing_machine])

    with pytest.raises(Exception):
        handler(AGENT_REGISTRATION_DATA)


def test_add_agent(handler, agent_repository):
    expected_agent = Agent(
        id=AGENT_REGISTRATION_DATA.id,
        machine_id=SEED_ID,
        start_time=AGENT_REGISTRATION_DATA.start_time,
        parent_id=AGENT_REGISTRATION_DATA.parent_id,
        cc_server=AGENT_REGISTRATION_DATA.cc_server,
    )
    handler(AGENT_REGISTRATION_DATA)

    agent_repository.upsert_agent.assert_called_with(expected_agent)
