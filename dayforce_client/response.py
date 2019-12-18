from typing import Dict, Iterator, Optional, Tuple

import attr
import requests


@attr.s
class DayforceResponse(object):

    client = attr.ib()
    params: Optional[Dict] = attr.ib()
    resp: requests.Response = attr.ib()

    def __iter__(self):
        self._iteration = 0
        return self

    def __next__(self):
        self._iteration += 1
        if self._iteration == 1:
            return self
        if self._is_paginated(self.resp) is True:
            next_page = self.resp.json().get("Paging").get("Next")
            if next_page != "" and next_page is not None:
                self.resp = self.client._get(url=next_page, params=self.params)
                return self
            else:
                raise StopIteration
        else:
            raise StopIteration

    def get(self, key, default=None):
        """Overrides get method to allow end users to retrieve any key in the
        response data in an intuitive way.
        """
        return self.resp.json().get(key, default)

    @staticmethod
    def _is_paginated(resp) -> bool:
        return resp.json().get("Paging") is not None

    def yield_records(self):
        for page in self:
            for record in self.get("Data"):
                yield page, record

    def yield_report_rows(self):
        for page in self:
            for row in self.get("Data").get("Rows"):
                yield page, row
