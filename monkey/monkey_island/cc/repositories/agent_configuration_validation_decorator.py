from jsonschema import validate

from common.agent_configuration import AgentConfiguration
from monkey_island.cc.repositories import (
    IAgentConfigurationRepository,
    PluginConfigurationValidationError,
    RetrievalError,
)
from monkey_island.cc.repositories.utils import AgentConfigurationSchemaCompiler


class AgentConfigurationValidationDecorator(IAgentConfigurationRepository):
    """
    A IAgentConfigurationRepository decorator that validates the agent configuration
    """

    def __init__(
        self,
        agent_configuration_repository: IAgentConfigurationRepository,
        agent_configuration_schema_compiler: AgentConfigurationSchemaCompiler,
    ):
        self._agent_configuration_repository = agent_configuration_repository
        self._agent_configuration_schema_compiler = agent_configuration_schema_compiler

    def get_configuration(self) -> AgentConfiguration:
        try:
            agent_configuration_schema = self._agent_configuration_schema_compiler.get_schema()
            agent_configuration = self._agent_configuration_repository.get_configuration()
            validate(
                instance=agent_configuration.dict(simplify=True), schema=agent_configuration_schema
            )
            return agent_configuration
        except Exception as err:
            raise RetrievalError(
                f"Agent configuration couldn't be validated against the schema: {err}"
            )

    def update_configuration(self, agent_configuration: AgentConfiguration):
        try:
            agent_configuration_dict = agent_configuration.dict(simplify=True)
            agent_configuration_schema = self._agent_configuration_schema_compiler.get_schema()

            validate(instance=agent_configuration_dict, schema=agent_configuration_schema)

            self._agent_configuration_repository.update_configuration(agent_configuration)
        except Exception as err:
            raise PluginConfigurationValidationError(
                f"Agent configuration couldn't be validated against the schema: {err}"
            )

    def reset_to_default(self):
        self._agent_configuration_repository.reset_to_default()
