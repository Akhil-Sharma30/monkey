from common import DIContainer
from common.utils.code_utils import PeriodicCaller
from monkey_island.cc.event_queue import IIslandEventQueue, IslandEventTopic
from monkey_island.cc.island_event_handlers import (
    AgentHeartbeatHandler,
    handle_agent_registration,
    reset_agent_configuration,
    reset_machine_repository,
    set_agent_configuration_per_island_mode,
)
from monkey_island.cc.repositories import (
    AgentMachineFacade,
    IAgentEventRepository,
    IAgentLogRepository,
    IAgentRepository,
    ICredentialsRepository,
    INodeRepository,
    ISimulationRepository,
    NetworkModelUpdateFacade,
)
from monkey_island.cc.services import AgentSignalsService


def setup_island_event_handlers(container: DIContainer):
    island_event_queue = container.resolve(IIslandEventQueue)

    _subscribe_agent_heartbeat_events(island_event_queue, container)
    _subscribe_agent_registration_events(island_event_queue, container)
    _subscribe_reset_agent_configuration_events(island_event_queue, container)
    _subscribe_clear_simulation_data_events(island_event_queue, container)
    _subscribe_set_island_mode_events(island_event_queue, container)
    _subscribe_terminate_agents_events(island_event_queue, container)


def _subscribe_agent_heartbeat_events(
    island_event_queue: IIslandEventQueue, container: DIContainer
):
    topic = IslandEventTopic.AGENT_HEARTBEAT

    agent_heartbeat_handler = container.resolve(AgentHeartbeatHandler)

    PeriodicCaller(agent_heartbeat_handler.update_agents_stop_time_from_heartbeat, 30).start()

    island_event_queue.subscribe(topic, agent_heartbeat_handler.update_agent_last_heartbeat)


def _subscribe_agent_registration_events(
    island_event_queue: IIslandEventQueue, container: DIContainer
):
    topic = IslandEventTopic.AGENT_REGISTERED

    island_event_queue.subscribe(topic, container.resolve(handle_agent_registration))


def _subscribe_reset_agent_configuration_events(
    island_event_queue: IIslandEventQueue, container: DIContainer
):
    topic = IslandEventTopic.RESET_AGENT_CONFIGURATION

    island_event_queue.subscribe(topic, container.resolve(reset_agent_configuration))


def _subscribe_clear_simulation_data_events(
    island_event_queue: IIslandEventQueue, container: DIContainer
):
    topic = IslandEventTopic.CLEAR_SIMULATION_DATA

    credentials_repository = container.resolve(ICredentialsRepository)
    island_event_queue.subscribe(topic, credentials_repository.remove_stolen_credentials)

    island_event_queue.subscribe(topic, container.resolve(reset_machine_repository))

    network_model_update_facade = container.resolve(NetworkModelUpdateFacade)
    island_event_queue.subscribe(topic, network_model_update_facade.reset_cache)

    agent_machine_facade = container.resolve(AgentMachineFacade)
    island_event_queue.subscribe(topic, agent_machine_facade.reset_cache)

    for i_repository in [
        IAgentEventRepository,
        IAgentLogRepository,
        IAgentRepository,
        INodeRepository,
    ]:
        repository = container.resolve(i_repository)
        island_event_queue.subscribe(topic, repository.reset)


def _subscribe_set_island_mode_events(
    island_event_queue: IIslandEventQueue, container: DIContainer
):
    topic = IslandEventTopic.SET_ISLAND_MODE

    island_event_queue.subscribe(topic, container.resolve(set_agent_configuration_per_island_mode))

    simulation_repository = container.resolve(ISimulationRepository)
    island_event_queue.subscribe(topic, simulation_repository.set_mode)


def _subscribe_terminate_agents_events(
    island_event_queue: IIslandEventQueue, container: DIContainer
):
    topic = IslandEventTopic.TERMINATE_AGENTS

    agent_signals_service = container.resolve(AgentSignalsService)

    island_event_queue.subscribe(topic, agent_signals_service.on_terminate_agents_signal)
