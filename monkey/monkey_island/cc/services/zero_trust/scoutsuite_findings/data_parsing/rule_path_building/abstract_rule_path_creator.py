from abc import ABC, abstractmethod
from typing import List

from ...consts.service_consts import FINDINGS, SERVICE_TYPES, SERVICES


class AbstractRulePathCreator(ABC):

    @property
    @abstractmethod
    def service_type(self) -> SERVICE_TYPES:
        pass

    @property
    @abstractmethod
    def supported_rules(self) -> List:
        pass

    @classmethod
    def build_rule_path(cls, rule_name) -> List[str]:
        assert(rule_name in cls.supported_rules)
        return [SERVICES, cls.service_type.value, FINDINGS, rule_name.value]
