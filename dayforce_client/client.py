from typing import Dict, Iterator, Optional, Tuple

import attr
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

    def _paginate_and_yield(self, resp: DayforceResponse) -> Iterator[Tuple[Dict, DayforceResponse]]:
        for page in resp:
            for record in page.get("Data"):
                yield record, page

    def _paginate_and_yield_reports(self, resp: DayforceResponse) -> Iterator[Tuple[Dict, DayforceResponse]]:
        for page in resp:
            for row in page.get("Data").get("Rows"):
                yield row, page

    # Employee Raw Punches
    def yield_employee_raw_punches(self, **kwargs):
        req_params = {"filterTransactionStartTimeUTC", "filterTransactionEndTimeUTC"}
        supplied_params = set(kwargs.keys())
        if not req_params.issubset(supplied_params):
            raise KeyError(f"Missing required query parameters: {req_params.difference(supplied_params)}")

        resp = self._get_resource(resource='EmployeeRawPunches', **kwargs)
        return self._paginate_and_yield(resp)

    # Employee Punches
    def yield_employee_punches(self, **kwargs):
        req_params = {"filterTransactionStartTimeUTC", "filterTransactionEndTimeUTC"}
        supplied_params = set(kwargs.keys())
        if not req_params.issubset(supplied_params):
            raise KeyError(f"Missing required query parameters: {req_params.difference(supplied_params)}")

        resp = self._get_resource(resource='EmployeePunches', **kwargs)
        return self._paginate_and_yield(resp)

    # Employees
    def get_employees(self, **kwargs):
        return self._get_resource(resource='Employees', **kwargs)

    def yield_employees(self, **kwargs):
        resp = self._get_resource(resource='Employees', **kwargs)
        return self._paginate_and_yield(resp)

    def get_employee_details(self, xrefcode: str, **kwargs):
        return self._get_resource(resource=f"Employees/{xrefcode}", **kwargs)

    # Reports
    def get_reports(self):
        return self._get_resource(resource='ReportMetadata')

    def get_report_metadata(self, xrefcode: str):
        return self._get_resource(resource=f"ReportMetadata/{xrefcode}")

    def get_report(self, xrefcode: str, **kwargs):
        return self._get_resource(resource=f"Reports/{xrefcode}", **kwargs)

    def yield_report_rows(self, xrefcode: str, **kwargs):
        resp = self._get_resource(resource=f"Reports/{xrefcode}", **kwargs)
        return self._paginate_and_yield_reports(resp)
