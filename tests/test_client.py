from collections.abc import Iterable

import pytest
import requests
import responses

from dayforce_client.client import Dayforce
from dayforce_client.response import DayforceResponse


def test_url(client):
    expected = "https://usr57-services.dayforcehcm.com/Api/foobar/V1"
    assert client.url == expected


def test_get_request(client):
    url = f"{client.url}/ClientMetadata"
    with responses.RequestsMock() as rsps:
        expected = {
            "ServiceVersion": "57.3.2.35215",
            "ServiceUri": "https://usr57-services.dayforcehcm.com/api"
        }
        rsps.add(responses.GET, url, json=expected, status=200)
        resp = client._request(method="GET", url=url)
        assert type(resp) == requests.Response
        assert resp.json() == expected
        assert resp.status_code == 200
        assert resp.ok


def test_get_resource(client):
    url = f"{client.url}/Employees"
    with responses.RequestsMock() as rsps:
        expected = {"Data": [{"XRefCode": "12345"}, {"XRefCode": "34567"}]}
        rsps.add(responses.GET, url, json=expected, status=200)
        resp = client._get_resource(resource='Employees')
        assert type(resp) == DayforceResponse
        assert type(resp.client) == Dayforce
        assert type(resp.resp) == requests.Response
        assert resp.resp.url == url
        assert resp.resp.json() == expected
        assert not resp.params


@pytest.mark.parametrize('params', [{"employeeNumber": "12"}, {"employeeNumber": "12", "filterHireStartDate": "2019-01-01T00:00:00Z"}])
def test_get_resource_params(client, params):
    url = f"{client.url}/Employees"
    with responses.RequestsMock() as rsps:
        expected = {"Data": [{"XRefCode": "12345"}, {"XRefCode": "34567"}]}
        rsps.add(responses.GET, url, json=expected, status=200)
        resp = client._get_resource(resource='Employees', params=params)
        assert type(resp) == DayforceResponse
        assert type(resp.client) == Dayforce
        assert type(resp.resp) == requests.Response
        assert resp.resp.json() == expected
        assert resp.params == params


@pytest.mark.parametrize(
    'params',
    [{"filterTransactionStartTimeUTC": "2019/11/01", "filterTransactionEndTimeUTC": "2019/11/05"},
     pytest.param({"filterTransactionStartTimeUTC": "2019/11/01"}, marks=pytest.mark.xfail)]
)
def test_get_employee_raw_punches(client, params):
    url = f"{client.url}/EmployeeRawPunches"
    with responses.RequestsMock() as rsps:
        expected = {
            "Data": [
                {
                    "RawPunchXRefCode": "#DF_1234",
                    "PunchState": "Processed"
                },
                {
                    "RawPunchXRefCode": "#DF_3456",
                    "PunchState": "Procssed"
                }
            ],
            "Paging": {
                "Next": ""
            }
        }
        rsps.add(responses.GET, url, json=expected, status=200)
        resp = client.get_employee_raw_punches(**params)
        assert type(resp) == DayforceResponse
        assert type(resp.client) == Dayforce
        assert type(resp.resp) == requests.Response
        assert resp.resp.json() == expected
        assert resp.params == params
        assert isinstance(resp, Iterable)
