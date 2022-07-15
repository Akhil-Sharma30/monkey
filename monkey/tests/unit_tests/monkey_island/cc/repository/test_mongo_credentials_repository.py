from typing import Any, Iterable, List, Mapping, Sequence
from unittest.mock import MagicMock

import mongomock
import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from tests.data_for_tests.propagation_credentials import PROPAGATION_CREDENTIALS

from common.credentials import Credentials
from monkey_island.cc.repository import MongoCredentialsRepository
from monkey_island.cc.server_utils.encryption import ILockableEncryptor

CONFIGURED_CREDENTIALS = PROPAGATION_CREDENTIALS[0:3]
STOLEN_CREDENTIALS = PROPAGATION_CREDENTIALS[3:6]


def reverse(data: bytes) -> bytes:
    return bytes(reversed(data))


@pytest.fixture
def repository_encryptor():
    repository_encryptor = MagicMock(spec=ILockableEncryptor)
    repository_encryptor.encrypt = MagicMock(side_effect=reverse)
    repository_encryptor.decrypt = MagicMock(side_effect=reverse)

    return repository_encryptor


@pytest.fixture
def mongo_client():
    return mongomock.MongoClient()


@pytest.fixture
def mongo_repository(mongo_client, repository_encryptor):
    return MongoCredentialsRepository(mongo_client, repository_encryptor)


def test_mongo_repository_get_configured(mongo_repository):
    actual_configured_credentials = mongo_repository.get_configured_credentials()

    assert actual_configured_credentials == []


def test_mongo_repository_get_stolen(mongo_repository):
    actual_stolen_credentials = mongo_repository.get_stolen_credentials()

    assert actual_stolen_credentials == []


def test_mongo_repository_get_all(mongo_repository):
    actual_credentials = mongo_repository.get_all_credentials()

    assert actual_credentials == []


def test_mongo_repository_configured(mongo_repository):
    mongo_repository.save_configured_credentials(PROPAGATION_CREDENTIALS)
    actual_configured_credentials = mongo_repository.get_configured_credentials()
    assert actual_configured_credentials == PROPAGATION_CREDENTIALS

    mongo_repository.remove_configured_credentials()
    actual_configured_credentials = mongo_repository.get_configured_credentials()
    assert actual_configured_credentials == []


def test_mongo_repository_stolen(mongo_repository):
    mongo_repository.save_stolen_credentials(STOLEN_CREDENTIALS)
    actual_stolen_credentials = mongo_repository.get_stolen_credentials()
    assert actual_stolen_credentials == STOLEN_CREDENTIALS

    mongo_repository.remove_stolen_credentials()
    actual_stolen_credentials = mongo_repository.get_stolen_credentials()
    assert actual_stolen_credentials == []


def test_mongo_repository_all(mongo_repository):
    mongo_repository.save_configured_credentials(CONFIGURED_CREDENTIALS)
    mongo_repository.save_stolen_credentials(STOLEN_CREDENTIALS)
    actual_credentials = mongo_repository.get_all_credentials()
    assert actual_credentials == PROPAGATION_CREDENTIALS

    mongo_repository.remove_all_credentials()

    assert mongo_repository.get_all_credentials() == []
    assert mongo_repository.get_stolen_credentials() == []
    assert mongo_repository.get_configured_credentials() == []


# NOTE: The following tests are complicated, but they work. Rather than spend the effort to improve
#       them now, we can revisit them when we resolve #2072. Resolving #2072 will make it easier to
#       simplify these tests.
@pytest.mark.parametrize("credentials", PROPAGATION_CREDENTIALS)
def test_configured_secrets_encrypted(
    mongo_repository: MongoCredentialsRepository,
    mongo_client: MongoClient,
    credentials: Sequence[Credentials],
):
    mongo_repository.save_configured_credentials([credentials])
    check_if_stored_credentials_encrypted(mongo_client, credentials)


@pytest.mark.parametrize("credentials", PROPAGATION_CREDENTIALS)
def test_stolen_secrets_encrypted(mongo_repository, mongo_client, credentials: Credentials):
    mongo_repository.save_stolen_credentials([credentials])
    check_if_stored_credentials_encrypted(mongo_client, credentials)


def check_if_stored_credentials_encrypted(mongo_client: MongoClient, original_credentials):
    original_credentials_mapping = Credentials.to_mapping(original_credentials)
    raw_credentials = get_all_credentials_in_mongo(mongo_client)

    for rc in raw_credentials:
        for identity_or_secret, credentials_component in rc.items():
            for key, value in credentials_component.items():
                assert original_credentials_mapping[identity_or_secret][key] != value.decode()


def get_all_credentials_in_mongo(
    mongo_client: MongoClient,
) -> Iterable[Mapping[str, Mapping[str, Any]]]:
    encrypted_credentials = []

    # Loop through all databases and collections and search for credentials. We don't want the tests
    # to assume anything about the internal workings of the repository.
    for collection in get_all_collections_in_mongo(mongo_client):
        mongo_credentials = collection.find({})
        for mc in mongo_credentials:
            del mc["_id"]
            encrypted_credentials.append(mc)

    return encrypted_credentials


def get_all_collections_in_mongo(mongo_client: MongoClient) -> Iterable[Collection]:
    collections: List[Collection] = []

    databases = get_all_databases_in_mongo(mongo_client)
    for db in databases:
        collections.extend(get_all_collections_in_database(db))

    return collections


def get_all_databases_in_mongo(mongo_client) -> Iterable[Database]:
    return (mongo_client[db_name] for db_name in mongo_client.list_database_names())


def get_all_collections_in_database(db: Database) -> Iterable[Collection]:
    return (db[collection_name] for collection_name in db.list_collection_names())
