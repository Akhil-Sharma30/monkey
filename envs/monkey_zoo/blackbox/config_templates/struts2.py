from copy import copy

from envs.monkey_zoo.blackbox.config_templates.base_template import BaseTemplate
from envs.monkey_zoo.blackbox.config_templates.config_template import ConfigTemplate


class Struts2(ConfigTemplate):

    config_values = copy(BaseTemplate.config_values)

    config_values.update(
        {
            "basic.exploiters.exploiter_classes": ["Struts2Exploiter"],
            "basic_network.scope.depth": 2,
            "basic_network.scope.subnet_scan_list": ["10.2.2.23", "10.2.2.24"],
            "internal.network.tcp_scanner.HTTP_PORTS": [80, 8080],
            "internal.network.tcp_scanner.tcp_target_ports": [80, 8080],
        }
    )
