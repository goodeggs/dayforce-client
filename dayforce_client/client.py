import base64
from typing import Dict, Optional, Set

import attr
import paramiko
import pysftp
import requests

from dayforce_client.response import DayforceResponse
from dayforce_client.version import __version__


@attr.s
class Dayforce(object):

    username: str = attr.ib()
    password: str = attr.ib(repr=False)
    client_namespace: str = attr.ib()
    dayforce_release: int = attr.ib(default=57)
    api_version: str = attr.ib(default="V1")
    url: str = attr.ib(init=False)

    @classmethod
    def from_config(cls, config):
        return cls(username=config.get("username"),
                   password=config.get("password"),
                   client_namespace=config.get("client_namespace"),
                   dayforce_release=config.get("dayforce_release"),
                   api_version=config.get("api_version"))

    def __attrs_post_init__(self):
        self.url = f"https://usr{self.dayforce_release}-services.dayforcehcm.com/Api/{self.client_namespace}/{self.api_version}"

    def _construct_headers(self) -> Dict:
        '''Constructs a standard set of headers for HTTP requests.'''
        headers = requests.utils.default_headers()
        headers["User-Agent"] = f"python-dayforce-client/{__version__}"
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        return headers

    def _get(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        headers = self._construct_headers()
        response = requests.get(url, auth=(self.username, self.password), headers=headers, params=params)
        response.raise_for_status()
        return response

    def _post(self, data: Optional[Dict] = None) -> requests.Response:
        '''Constructs a standard way of making
        a POST request to the Dayforce REST API.
        '''
        headers = self._construct_headers()
        response = requests.post(self.url, headers=headers, data=data)
        response.raise_for_status()
        return response

    def _get_resource(self, resource: str, **kwargs) -> DayforceResponse:
        url = f"{self.url}/{resource}"
        resp = self._get(url=url, params=kwargs)
        return DayforceResponse(client=self, params=kwargs, resp=resp)

    def get_employee_raw_punches(self, *, filterTransactionStartTimeUTC: str, filterTransactionEndTimeUTC: str, **kwargs) -> DayforceResponse:
        kwargs.update({"filterTransactionStartTimeUTC": filterTransactionStartTimeUTC, "filterTransactionEndTimeUTC": filterTransactionEndTimeUTC})
        return self._get_resource(resource='EmployeeRawPunches', **kwargs)

    def get_employee_punches(self, *, filterTransactionStartTimeUTC: str, filterTransactionEndTimeUTC: str, **kwargs) -> DayforceResponse:
        kwargs.update({"filterTransactionStartTimeUTC": filterTransactionStartTimeUTC, "filterTransactionEndTimeUTC": filterTransactionEndTimeUTC})
        return self._get_resource(resource='EmployeePunches', **kwargs)

    def get_employees(self, **kwargs) -> DayforceResponse:
        return self._get_resource(resource='Employees', **kwargs)

    def get_employee_details(self, *, xrefcode: str, **kwargs) -> DayforceResponse:
        return self._get_resource(resource=f"Employees/{xrefcode}", **kwargs)

    def get_employee_schedules(self, *, xrefcode: str, filterScheduleStartDate: str, filterScheduleEndDate: str, **kwargs) -> DayforceResponse:
        kwargs.update({"filterScheduleStartDate": filterScheduleStartDate, "filterScheduleEndDate": filterScheduleEndDate})
        return self._get_resource(resource=f"Employees/{xrefcode}/Schedules", **kwargs)

    def get_reports(self) -> DayforceResponse:
        return self._get_resource(resource='ReportMetadata')

    def get_report_metadata(self, *, xrefcode: str) -> DayforceResponse:
        return self._get_resource(resource=f"ReportMetadata/{xrefcode}")

    def get_report(self, *, xrefcode: str, **kwargs) -> DayforceResponse:
        return self._get_resource(resource=f"Reports/{xrefcode}", **kwargs)


@attr.s
class DayforceSFTP(object):

    hostname: str = attr.ib()
    username: str = attr.ib()
    password: str = attr.ib(repr=False)
    port: int = attr.ib(default=22)
    # the host key can be retrieved with ssh-keyscan (pass just the base64 encoded part of the line beginning with ssh-rsa)
    host_key: str = attr.ib(default=None)
    disable_host_key_checking: bool = attr.ib(default=False)
    cnopts: pysftp.CnOpts = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.cnopts = pysftp.CnOpts()
        if self.disable_host_key_checking is True:
            self.cnopts.hostkeys = None
        elif self.host_key is not None:
            key_b = self.host_key.encode()
            key = paramiko.RSAKey(data=base64.decodebytes(key_b))
            self.cnopts.hostkeys.add(self.hostname, 'ssh-rsa', key)
        else:
            raise RuntimeError('disable_host_key_checking or host_key must be set')

    def listdir(self):
        with pysftp.Connection(host=self.hostname, username=self.username, password=self.password, port=self.port, cnopts=self.cnopts) as sftp:
            return sftp.pwd
