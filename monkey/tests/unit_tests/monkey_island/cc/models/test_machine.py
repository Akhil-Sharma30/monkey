import uuid
from ipaddress import IPv4Interface
from types import MappingProxyType
from typing import MutableSequence

import pytest

from common import OperatingSystem
from monkey_island.cc.models import Machine

MACHINE_OBJECT_DICT = MappingProxyType(
    {
        "id": 1,
        "hardware_id": uuid.getnode(),
        "network_interfaces": [IPv4Interface("10.0.0.1/24"), IPv4Interface("192.168.5.32/16")],
        "operating_system": OperatingSystem.WINDOWS,
        "operating_system_version": "eXtra Problems",
        "hostname": "my.host",
    }
)

MACHINE_SIMPLE_DICT = MappingProxyType(
    {
        "id": 1,
        "hardware_id": uuid.getnode(),
        "network_interfaces": ["10.0.0.1/24", "192.168.5.32/16"],
        "operating_system": "windows",
        "operating_system_version": "eXtra Problems",
        "hostname": "my.host",
    }
)


def test_constructor():
    # Raises exception_on_failure
    Machine(**MACHINE_OBJECT_DICT)


def test_from_dict():
    # Raises exception_on_failure
    Machine(**MACHINE_SIMPLE_DICT)


def test_to_dict():
    m = Machine(**MACHINE_OBJECT_DICT)

    assert m.dict(simplify=True) == dict(MACHINE_SIMPLE_DICT)


@pytest.mark.parametrize(
    "key, value",
    [
        ("id", "not-an-int"),
        ("hardware_id", "not-an-int"),
        ("network_interfaces", "not-a-list"),
        ("operating_system", 2.1),
        ("operating_system", "bsd"),
        ("operating_system_version", {}),
        ("hostname", []),
    ],
)
def test_construct_invalid_field__type_error(key, value):
    invalid_type_dict = MACHINE_SIMPLE_DICT.copy()
    invalid_type_dict[key] = value

    with pytest.raises(TypeError):
        Machine(**invalid_type_dict)


@pytest.mark.parametrize(
    "key, value",
    [
        ("id", -1),
        ("hardware_id", 0),
        ("network_interfaces", [1, "stuff", 3]),
        ("network_interfaces", ["10.0.0.1/16", 2, []]),
    ],
)
def test_construct_invalid_field__value_error(key, value):
    invalid_type_dict = MACHINE_SIMPLE_DICT.copy()
    invalid_type_dict[key] = value

    with pytest.raises(ValueError):
        Machine(**invalid_type_dict)


def test_construct__extra_fields_forbidden():
    extra_field_dict = MACHINE_SIMPLE_DICT.copy()
    extra_field_dict["extra_field"] = 99  # red balloons

    with pytest.raises(ValueError):
        Machine(**extra_field_dict)


def test_id_immutable():
    m = Machine(**MACHINE_OBJECT_DICT)
    with pytest.raises(TypeError):
        m.id = 2


@pytest.mark.parametrize("hardware_id", [None, 1, 100])
def test_hardware_id_set_valid_value(hardware_id):
    m = Machine(**MACHINE_OBJECT_DICT)

    # Raises exception_on_failure
    m.hardware_id = hardware_id


def test_hardware_id_validate_on_set():
    m = Machine(**MACHINE_OBJECT_DICT)
    with pytest.raises(ValueError):
        m.hardware_id = -50


def test_network_interfaces_set_valid_value():
    m = Machine(**MACHINE_OBJECT_DICT)

    # Raises exception_on_failure
    m.network_interfaces = [IPv4Interface("172.1.2.3/24")]


def test_network_interfaces_set_invalid_value():
    m = Machine(**MACHINE_OBJECT_DICT)

    with pytest.raises(ValueError):
        m.network_interfaces = [IPv4Interface("172.1.2.3/24"), None]


def test_network_interfaces_sequence_is_immutable():
    m = Machine(**MACHINE_OBJECT_DICT)

    assert not isinstance(m.network_interfaces, MutableSequence)


def test_operating_system_set_valid_value():
    m = Machine(**MACHINE_OBJECT_DICT)

    # Raises exception_on_failure
    m.operating_system = OperatingSystem.LINUX


def test_operating_system_set_invalid_value():
    m = Machine(**MACHINE_OBJECT_DICT)

    with pytest.raises(ValueError):
        m.operating_system = "MacOS"


def test_set_operating_system_version():
    m = Machine(**MACHINE_OBJECT_DICT)

    # Raises exception_on_failure
    m.operating_system_version = "1234"


def test_set_hostname():
    m = Machine(**MACHINE_OBJECT_DICT)

    # Raises exception_on_failure
    m.operating_system_version = "wopr"