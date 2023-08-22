import copy

import gridfs
import mongomock
import pytest
from mongomock.gridfs import enable_gridfs_integration
from tests.data_for_tests.agent_plugin.manifests import (
    CREDENTIALS_COLLECTOR_MANIFEST_1,
    CREDENTIALS_COLLECTOR_NAME_1,
    EXPLOITER_MANIFEST_1,
    EXPLOITER_MANIFEST_2,
    EXPLOITER_NAME_1,
)
from tests.unit_tests.common.agent_plugins.test_agent_plugin_manifest import FAKE_NAME
from tests.unit_tests.monkey_island.cc.fake_agent_plugin_data import FAKE_AGENT_PLUGIN_1

from common import OperatingSystem
from common.agent_plugins import AgentPluginManifest, AgentPluginType
from monkey_island.cc.repositories import RetrievalError, UnknownRecordError
from monkey_island.cc.services.agent_plugin_service.mongo_agent_plugin_repository import (
    MongoAgentPluginRepository,
)

enable_gridfs_integration()

EXPECTED_MANIFEST = EXPLOITER_MANIFEST_1


@pytest.fixture
def mongo_client():
    client = mongomock.MongoClient()

    return client


plugin_manifest_dict = EXPLOITER_MANIFEST_1.dict(simplify=True)

basic_plugin_dict = {
    "plugin_manifest": plugin_manifest_dict,
    "config_schema": {},
    "supported_operating_systems": ("windows",),
}

malformed_plugin_dict = copy.deepcopy(basic_plugin_dict)
del malformed_plugin_dict["plugin_manifest"]["title"]
malformed_plugin_dict["plugin_manifest"]["tile"] = "dummy-exploiter"


@pytest.fixture
def insert_plugin(mongo_client):
    def impl(file, operating_system: OperatingSystem, plugin_dict=None):
        if plugin_dict is None:
            plugin_dict = copy.deepcopy(basic_plugin_dict)
        binaries_collection = gridfs.GridFS(
            mongo_client.monkey_island, f"agent_plugins_binaries_{operating_system.value}"
        )
        id = binaries_collection.put(file)
        plugin_dict["binaries"] = {f"{operating_system.value}": id}
        mongo_client.monkey_island.agent_plugins.insert_one(plugin_dict)

    return impl


@pytest.fixture
def agent_plugin_repository(mongo_client) -> MongoAgentPluginRepository:
    return MongoAgentPluginRepository(mongo_client)


@pytest.mark.slow
def test_get_plugin(
    plugin_file, insert_plugin, agent_plugin_repository: MongoAgentPluginRepository
):
    with open(plugin_file, "rb") as file:
        insert_plugin(file, OperatingSystem.WINDOWS)
    plugin = agent_plugin_repository.get_plugin(
        OperatingSystem.WINDOWS, AgentPluginType.EXPLOITER, EXPLOITER_NAME_1
    )

    assert plugin.plugin_manifest == EXPECTED_MANIFEST
    assert isinstance(plugin.config_schema, dict)
    assert len(plugin.source_archive) == 10240


def test_get_plugin__UnknownRecordError_if_not_exist(agent_plugin_repository):
    with pytest.raises(UnknownRecordError):
        agent_plugin_repository.get_plugin(
            OperatingSystem.WINDOWS, AgentPluginType.EXPLOITER, "does_not_exist"
        )


def test_get_plugin__RetrievalError_if_bad_plugin(
    plugin_file, insert_plugin, agent_plugin_repository: MongoAgentPluginRepository
):
    with open(plugin_file, "rb") as file:
        insert_plugin(file, OperatingSystem.WINDOWS, malformed_plugin_dict)

    with pytest.raises(RetrievalError):
        agent_plugin_repository.get_plugin(
            OperatingSystem.WINDOWS, AgentPluginType.EXPLOITER, EXPLOITER_NAME_1
        )


def test_get_plugin__RetrievalError_if_unsupported_os(
    plugin_file, insert_plugin, mongo_client, agent_plugin_repository: MongoAgentPluginRepository
):
    with open(plugin_file, "rb") as file:
        insert_plugin(file, OperatingSystem.WINDOWS)
    with pytest.raises(RetrievalError):
        agent_plugin_repository.get_plugin(
            OperatingSystem.LINUX, AgentPluginType.EXPLOITER, EXPLOITER_NAME_1
        )


def test_get_all_plugin_manifests(
    plugin_file, insert_plugin, agent_plugin_repository):
    dict1 = copy.deepcopy(basic_plugin_dict)
    dict2 = copy.deepcopy(basic_plugin_dict)
    dict2['manifest'] = EXPLOITER_MANIFEST_2.dict(simplify=True)
    dict3 = copy.deepcopy(basic_plugin_dict)
    dict3['manifest'] = CREDENTIALS_COLLECTOR_MANIFEST_1.dict(simplify=True)

    with open(plugin_file, "rb") as file:
        insert_plugin(file, OperatingSystem.WINDOWS, dict1)
        insert_plugin(file, OperatingSystem.WINDOWS, dict2)
        insert_plugin(file, OperatingSystem.WINDOWS, dict3)
        insert_plugin(file, OperatingSystem.LINUX, dict3)

    retrieved_plugin_manifests = agent_plugin_repository.get_all_plugin_manifests()

    assert retrieved_plugin_manifests[AgentPluginType.EXPLOITER][EXPLOITER_NAME_1] == EXPECTED_MANIFEST
    assert retrieved_plugin_manifests[AgentPluginType.CREDENTIALS_COLLECTOR] == {
        CREDENTIALS_COLLECTOR_NAME_1: CREDENTIALS_COLLECTOR_MANIFEST_1
    }


# def test_get_all_plugin_manifests__RetrievalError_if_bad_plugin_type(
#     plugin_file, file_repository: InMemoryFileRepository, agent_plugin_repository
# ):
#     with open(plugin_file, "rb") as file:
#         file_repository.save_file("ssh-bogus.tar", file)

#     with pytest.raises(RetrievalError):
#         agent_plugin_repository.get_all_plugin_manifests()


def test_store_agent_plugin(agent_plugin_repository: MongoAgentPluginRepository):
    agent_plugin_repository.store_agent_plugin(OperatingSystem.LINUX, FAKE_AGENT_PLUGIN_1)

    plugin = agent_plugin_repository.get_plugin(
        OperatingSystem.LINUX, AgentPluginType.EXPLOITER, FAKE_NAME
    )
    assert plugin == FAKE_AGENT_PLUGIN_1


# def test_remove_agent_plugin():
#     pass
