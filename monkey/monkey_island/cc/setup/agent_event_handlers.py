from common import DIContainer
from common.agent_events import (
    AgentShutdownEvent,
    CredentialsStolenEvent,
    ExploitationEvent,
    PingScanEvent,
    TCPScanEvent,
)
from common.event_queue import IAgentEventQueue
from monkey_island.cc.agent_event_handlers import (
    ScanEventHandler,
    save_event_to_event_repository,
    save_stolen_credentials_to_repository,
    update_agent_shutdown_status,
    update_nodes_on_exploitation,
)


def setup_agent_event_handlers(container: DIContainer):
    agent_event_queue = container.resolve(IAgentEventQueue)

    _subscribe_and_store_to_event_repository(container, agent_event_queue)
    _subscribe_scan_events(container, agent_event_queue)
    _subscribe_exploitation_events(container, agent_event_queue)


def _subscribe_and_store_to_event_repository(
    container: DIContainer, agent_event_queue: IAgentEventQueue
):
    agent_event_queue.subscribe_all_events(container.resolve(save_event_to_event_repository))

    agent_event_queue.subscribe_type(
        CredentialsStolenEvent, container.resolve(save_stolen_credentials_to_repository)
    )
    agent_event_queue.subscribe_type(
        AgentShutdownEvent, container.resolve(update_agent_shutdown_status)
    )


def _subscribe_scan_events(container: DIContainer, agent_event_queue: IAgentEventQueue):
    scan_event_handler = container.resolve(ScanEventHandler)

    agent_event_queue.subscribe_type(PingScanEvent, scan_event_handler.handle_ping_scan_event)
    agent_event_queue.subscribe_type(TCPScanEvent, scan_event_handler.handle_tcp_scan_event)


def _subscribe_exploitation_events(container: DIContainer, agent_event_queue: IAgentEventQueue):
    agent_event_queue.subscribe_type(
        ExploitationEvent, container.resolve(update_nodes_on_exploitation)
    )
