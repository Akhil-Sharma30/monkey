from common.types import AgentID
from monkey_island.cc.repository import IAgentLogRepository, UnknownRecordError


class InMemoryAgentLogRepository(IAgentLogRepository):
    def __init__(self):
        self._agent_logs = {}

    def upsert_agent_log(self, agent_id: AgentID, log_contents: str):
        if agent_id not in self._agent_logs.keys():
            self._agent_logs[agent_id] = log_contents

    def get_agent_log(self, agent_id: AgentID) -> str:
        if agent_id not in self._agent_logs:
            raise UnknownRecordError("Error occured while getting agent")
        return self._agent_logs[agent_id]

    def reset(self):
        self._agent_logs = {}
