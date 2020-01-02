import base64
import platform
import sys
from typing import Dict, Optional

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

    @staticmethod
    def _construct_user_agent() -> str:
        client = f"dayforce-client/{__version__}"
        python_version = f"Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        system_info = f"{platform.system()}/{platform.release()}"
        user_agent = " ".join([python_version, client, system_info])
        return user_agent

    def _construct_headers(self) -> Dict:
        '''Constructs a standard set of headers for HTTP requests.'''
        headers = requests.utils.default_headers()
        headers["User-Agent"] = self._construct_user_agent()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        return headers

    def _request(self, *, method: str, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> requests.Response:
        headers = self._construct_headers()
        response = requests.request(method=method, url=url, auth=(self.username, self.password), headers=headers, params=params, data=data, timeout=30)
        response.raise_for_status()
        return response

    def _get_resource(self, *, resource: str, params: Optional[Dict] = None) -> DayforceResponse:
        url = f"{self.url}/{resource}"
        resp = self._request(method="GET", url=url, params=params)
        return DayforceResponse(client=self, params=params, resp=resp)

    def _create_resource(self, *, resource: str, data: Optional[Dict] = None) -> DayforceResponse:
        url = f"{self.url}/{resource}"
        resp = self._request(method="POST", url=url, data=data)
        return DayforceResponse(client=self, data=data, resp=resp)

    def get_employee_raw_punches(self, *, filterTransactionStartTimeUTC: str, filterTransactionEndTimeUTC: str, **kwargs) -> DayforceResponse:
        kwargs.update({"filterTransactionStartTimeUTC": filterTransactionStartTimeUTC, "filterTransactionEndTimeUTC": filterTransactionEndTimeUTC})
        return self._get_resource(resource='EmployeeRawPunches', params=kwargs)

    def get_employee_punches(self, *, filterTransactionStartTimeUTC: str, filterTransactionEndTimeUTC: str, **kwargs) -> DayforceResponse:
        kwargs.update({"filterTransactionStartTimeUTC": filterTransactionStartTimeUTC, "filterTransactionEndTimeUTC": filterTransactionEndTimeUTC})
        return self._get_resource(resource='EmployeePunches', params=kwargs)

    def get_employees(self, **kwargs) -> DayforceResponse:
        return self._get_resource(resource='Employees', params=kwargs)

    def create_employee(self, *, xrefcode: str, **kwargs) -> DayforceResponse:
        kwargs.update({"XRefCode": xrefcode})
        return self._create_resource(resource='Employees', data=kwargs)

    def get_employee_details(self, *, xrefcode: str, **kwargs) -> DayforceResponse:
        return self._get_resource(resource=f"Employees/{xrefcode}", params=kwargs)

    def get_employee_schedules(self, *, xrefcode: str, filterScheduleStartDate: str, filterScheduleEndDate: str, **kwargs) -> DayforceResponse:
        kwargs.update({"filterScheduleStartDate": filterScheduleStartDate, "filterScheduleEndDate": filterScheduleEndDate})
        return self._get_resource(resource=f"Employees/{xrefcode}/Schedules", params=kwargs)

    def get_reports(self) -> DayforceResponse:
        return self._get_resource(resource='ReportMetadata')

    def get_report_metadata(self, *, xrefcode: str) -> DayforceResponse:
        return self._get_resource(resource=f"ReportMetadata/{xrefcode}")

    def get_report(self, *, xrefcode: str, **kwargs) -> DayforceResponse:
        return self._get_resource(resource=f"Reports/{xrefcode}", params=kwargs)


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
