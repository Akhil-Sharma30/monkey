import json
from http import HTTPStatus
from typing import Sequence
from urllib.parse import urljoin

import pytest
from tests.common import StubDIContainer
from tests.data_for_tests.propagation_credentials import (
    PROPAGATION_CREDENTIALS_1,
    PROPAGATION_CREDENTIALS_2,
    PROPAGATION_CREDENTIALS_3,
    PROPAGATION_CREDENTIALS_4,
)
from tests.monkey_island import InMemoryCredentialsRepository

from common.credentials import Credentials
from monkey_island.cc.repository import ICredentialsRepository
from monkey_island.cc.resources import PropagationCredentials
from monkey_island.cc.resources.propagation_credentials import (
    _configured_collection,
    _stolen_collection,
)

ALL_CREDENTIALS_URL = PropagationCredentials.urls[0]
CONFIGURED_CREDENTIALS_URL = urljoin(ALL_CREDENTIALS_URL, _configured_collection)
STOLEN_CREDENTIALS_URL = urljoin(ALL_CREDENTIALS_URL, _stolen_collection)


@pytest.fixture
def credentials_repository():
    return InMemoryCredentialsRepository()


@pytest.fixture
def flask_client(build_flask_client, credentials_repository):
    container = StubDIContainer()

    container.register_instance(ICredentialsRepository, credentials_repository)

    with build_flask_client(container) as flask_client:
        yield flask_client


def test_propagation_credentials_endpoint_get(flask_client, credentials_repository):
    credentials_repository.save_configured_credentials(
        [PROPAGATION_CREDENTIALS_1, PROPAGATION_CREDENTIALS_3]
    )
    credentials_repository.save_stolen_credentials(
        [PROPAGATION_CREDENTIALS_2, PROPAGATION_CREDENTIALS_4]
    )

    resp = flask_client.get(ALL_CREDENTIALS_URL)
    actual_propagation_credentials = [Credentials.from_mapping(creds) for creds in resp.json]

    assert resp.status_code == HTTPStatus.OK
    assert len(actual_propagation_credentials) == 4
    assert PROPAGATION_CREDENTIALS_1 in actual_propagation_credentials
    assert PROPAGATION_CREDENTIALS_2 in actual_propagation_credentials
    assert PROPAGATION_CREDENTIALS_3 in actual_propagation_credentials
    assert PROPAGATION_CREDENTIALS_4 in actual_propagation_credentials


def pre_populate_repository(
    url: str, credentials_repository: ICredentialsRepository, credentials: Sequence[Credentials]
):
    if "configured" in url:
        credentials_repository.save_configured_credentials(credentials)
    else:
        credentials_repository.save_stolen_credentials(credentials)


@pytest.mark.parametrize("url", [CONFIGURED_CREDENTIALS_URL, STOLEN_CREDENTIALS_URL])
def test_propagation_credentials_endpoint__get_stolen(flask_client, credentials_repository, url):
    pre_populate_repository(
        url, credentials_repository, [PROPAGATION_CREDENTIALS_1, PROPAGATION_CREDENTIALS_2]
    )

    resp = flask_client.get(url)
    actual_propagation_credentials = [Credentials.from_mapping(creds) for creds in resp.json]

    assert resp.status_code == HTTPStatus.OK
    assert len(actual_propagation_credentials) == 2
    assert actual_propagation_credentials[0] == PROPAGATION_CREDENTIALS_1
    assert actual_propagation_credentials[1] == PROPAGATION_CREDENTIALS_2


@pytest.mark.parametrize("url", [CONFIGURED_CREDENTIALS_URL, STOLEN_CREDENTIALS_URL])
def test_propagation_credentials_endpoint__post_stolen(flask_client, credentials_repository, url):
    pre_populate_repository(url, credentials_repository, [PROPAGATION_CREDENTIALS_1])

    resp = flask_client.post(
        url,
        json=[
            Credentials.to_json(PROPAGATION_CREDENTIALS_2),
            Credentials.to_json(PROPAGATION_CREDENTIALS_3),
        ],
    )
    assert resp.status_code == HTTPStatus.NO_CONTENT

    resp = flask_client.get(url)
    retrieved_propagation_credentials = [Credentials.from_mapping(creds) for creds in resp.json]

    assert resp.status_code == HTTPStatus.OK
    assert len(retrieved_propagation_credentials) == 3
    assert PROPAGATION_CREDENTIALS_1 in retrieved_propagation_credentials
    assert PROPAGATION_CREDENTIALS_2 in retrieved_propagation_credentials
    assert PROPAGATION_CREDENTIALS_3 in retrieved_propagation_credentials


@pytest.mark.parametrize("url", [CONFIGURED_CREDENTIALS_URL, STOLEN_CREDENTIALS_URL])
def test_stolen_propagation_credentials_endpoint_delete(flask_client, credentials_repository, url):
    pre_populate_repository(
        url, credentials_repository, [PROPAGATION_CREDENTIALS_1, PROPAGATION_CREDENTIALS_2]
    )
    resp = flask_client.delete(url)
    assert resp.status_code == HTTPStatus.NO_CONTENT

    resp = flask_client.get(url)
    assert len(json.loads(resp.text)) == 0


def test_propagation_credentials_endpoint__propagation_credentials_post_not_allowed(flask_client):
    resp = flask_client.post(ALL_CREDENTIALS_URL, json=[])
    assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED


NON_EXISTENT_COLLECTION_URL = urljoin(ALL_CREDENTIALS_URL, "bogus-credentials")


def test_propagation_credentials_endpoint__get_not_found(flask_client):
    resp = flask_client.get(NON_EXISTENT_COLLECTION_URL)
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_propagation_credentials_endpoint__post_not_found(flask_client):
    resp = flask_client.post(
        NON_EXISTENT_COLLECTION_URL,
        json=[
            Credentials.to_json(PROPAGATION_CREDENTIALS_2),
            Credentials.to_json(PROPAGATION_CREDENTIALS_3),
        ],
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_propagation_credentials_endpoint__delete_not_found(flask_client):
    resp = flask_client.delete(NON_EXISTENT_COLLECTION_URL)
    assert resp.status_code == HTTPStatus.NOT_FOUND
