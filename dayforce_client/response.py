import collections
import time
from typing import Dict, Iterator, Optional, Tuple

import attr
import requests


@attr.s
class DayforceResponse(object):

    client = attr.ib()
    resp: requests.Response = attr.ib()
    params: Optional[Dict] = attr.ib(default=None)
    data: Optional[Dict] = attr.ib(default=None)

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
                self.resp = self.client._request(
                    method="GET", url=next_page, params=self.params
                )
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

    @staticmethod
    def _rate_limit(times: collections.deque, limit: Tuple[int, int]):
        if len(times) >= limit[0]:
            start = times.pop()
            now = time.time()
            sleep_time = limit[1] - (now - start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def yield_records(self, limit: Optional[Tuple[int, int]] = None) -> Iterator[Tuple]:
        """Paginates the response and yields relevant records.

        Args:
            limit (Tuple[int, int]): A tuple dictating the number of requests to be made
                                     in a given number of seconds. For example, if it is
                                     only possible to make 100 requests per minute, the
                                     supplied value should be (100, 60). If a response is
                                     paginated, a single HTTP request will be made per page.
        """
        times: collections.deque = collections.deque()

        for page in self:
            times.appendleft(time.time())
            for record in self.get("Data"):
                yield page, record

            if limit is not None:
                self._rate_limit(times, limit)

    def yield_report_rows(
        self, limit: Optional[Tuple[int, int]] = None
    ) -> Iterator[Tuple]:
        """Paginates the response and yields relevant rows for Report objects.

        Args:
            limit (Tuple[int, int]): A tuple dictating the number of requests to be made
                                     in a given number of seconds. For example, if it is
                                     only possible to make 100 requests per minute, the
                                     supplied value should be (100, 60). If a response is
                                     paginated, a single HTTP request will be made per page.
        """
        times: collections.deque = collections.deque()

        for page in self:
            times.appendleft(time.time())
            for row in self.get("Data").get("Rows"):
                yield page, row

            if limit is not None:
                self._rate_limit(times, limit)
