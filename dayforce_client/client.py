from typing import Dict, Optional, Set

import attr
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

    def _check_required_params(self, req_params: Set[str], params: Dict):
        supplied_params = set(params.keys())
        if not req_params.issubset(supplied_params):
            raise KeyError(f"Missing required query parameters: {req_params.difference(supplied_params)}")

    def get_employee_raw_punches(self, **kwargs):
        req_params = {"filterTransactionStartTimeUTC", "filterTransactionEndTimeUTC"}
        self._check_required_params(req_params, params=kwargs)
        return self._get_resource(resource='EmployeeRawPunches', **kwargs)

    def get_employee_punches(self, **kwargs):
        req_params = {"filterTransactionStartTimeUTC", "filterTransactionEndTimeUTC"}
        self._check_required_params(req_params, params=kwargs)
        return self._get_resource(resource='EmployeePunches', **kwargs)

    def get_employees(self, **kwargs):
        return self._get_resource(resource='Employees', **kwargs)

    def get_employee_details(self, xrefcode: str, **kwargs):
        return self._get_resource(resource=f"Employees/{xrefcode}", **kwargs)

    def get_employee_schedules(self, xrefcode: str, **kwargs):
        req_params = {"filterScheduleStartDate", "filterScheduleEndDate"}
        self._check_required_params(req_params, params=kwargs)
        return self._get_resource(resource=f"Employees/{xrefcode}/Schedules", **kwargs)

    def get_reports(self):
        return self._get_resource(resource='ReportMetadata')

    def get_report_metadata(self, xrefcode: str):
        return self._get_resource(resource=f"ReportMetadata/{xrefcode}")

    def get_report(self, xrefcode: str, **kwargs):
        return self._get_resource(resource=f"Reports/{xrefcode}", **kwargs)


@attr.s
class DayforceSFTP(object):

    hostname: str = attr.ib()
    username: str = attr.ib()
    password: str = attr.ib(repr=False)
    port: int = attr.ib(default=22)
    known_hosts: str = attr.ib(default='~/.ssh/known_hosts')
    disable_host_key_checking: bool = attr.ib(default=False)

    def __attrs_post_init__(self):
        if self.disable_host_key_checking is True:
            self.cnopts = pysftp.CnOpts()
            self.cnopts.hostkeys = None
        else:
            self.cnopts = pysftp.CnOpts(knownhosts=self.known_hosts)
            self.cnopts.hostkeys = None

    def listdir(self):
        with pysftp.Connection(host=self.hostname, username=self.username, password=self.password, port=self.port, cnopts=self.cnopts) as sftp:
            return sftp.pwd
