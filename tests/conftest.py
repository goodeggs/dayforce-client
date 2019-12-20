import pytest

from dayforce_client.client import Dayforce, DayforceSFTP


@pytest.fixture(scope='session')
def client():
    return Dayforce(username="foo",
                    password="bar",
                    client_namespace="foobar")


@pytest.fixture(scope='session')
def sftpclient():
    return DayforceSFTP(hostname="sftp://foo.bar.com",
                        username="foo",
                        password="bar",
                        port=22)
