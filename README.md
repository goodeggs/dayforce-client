# dayforce-client
[![PyPI version](https://badge.fury.io/py/dayforce-client.svg)](https://badge.fury.io/py/dayforce-client)
![PyPI - Status](https://img.shields.io/pypi/status/dayforce-client)
[![Build Status](https://travis-ci.com/goodeggs/dayforce-client.svg?branch=master)](https://travis-ci.com/goodeggs/dayforce-client.svg?branch=master)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dayforce-client)
![PyPI - License](https://img.shields.io/pypi/l/dayforce-client)

dayforce-client is a python SDK for interfacing with the Dayforce REST API.

## Installation

```bash
$ pip3 install dayforce-client
```

## Basic Usage

The main interface to the Dayforce REST API is the `Dayforce` class. You can instantiate the `Dayforce` class by supplying a few authentication and configuration arguments:

```python
import os

from dayforce_client.client import Dayforce

DAYFORCE_USERNAME = os.environ["DAYFORCE_USERNAME"]
DAYFORCE_PASSWORD = os.environ["DAYFORCE_PASSWORD"]
DAYFORCE_CLIENT_NAMESPACE = os.environ["DAYFORCE_CLIENT_NAMESPACE"]

df = Dayforce(username=DAYFORCE_USERNAME,
              password=DAYFORCE_PASSWORD,
              client_namespace=DAYFORCE_CLIENT_NAMESPACE)
```

All `get_` methods on the `Dayforce` class will return a `DayforceReponse` object. A `DayforceReponse` object contains the `Dayforce` instance used to make the call, the parameters used in the request, and the response received from the API:

```python
resp = df.get_employee_details(xrefcode='12345')
print(resp.client)
print(type(resp.client))
print(resp.params)
print(type(resp.resp))
print(resp.resp.url)
print(resp.resp.status_code)
print(resp.resp.ok)
print(resp.resp.elapsed)
```

Output:
```
Dayforce(username='your-username', client_namespace='your-client-namespace', dayforce_release=57, api_version='V1', url='https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1')
<class 'dayforce_client.client.Dayforce'>
{}
<class 'requests.models.Response'>
https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1/Employees/12345
200
True
0:00:00.550066
```

### Query Parameters

Certain methods also accept keyword arguments that will be used as query parameters for the request:

```python
resp = df.get_employee_details(xrefcode='12345', expand='WorkAssignments')
print(resp.resp.url)
```

Output:
```
https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1/Employees/12345?expand=WorkAssignments
```

### Accessing Response Content

Response contents can accessed using `.get()` syntax:

```python
resp = df.get_employee_details(xrefcode='12345')
print(resp.get("Data"))
```

### Pagination

Responses can also optionally be paginated using iteration syntax:

```python
for page in df.get_employee_raw_punches():
  for raw_punch in page.get("Data"):
    print(raw_punch)
```

### Yielding Resource Records

Optionally, you can use the `DayforceResponse` `.yield_records()` method to handle response pagination and yieliding resource records. The method will paginate the response and iterate through response content to yield single resource records for the given resource and the corresponding `DayforceResponse` instance:

```python
for page, employee in df.get_employees().yield_records():
    print(employee)
    print(page)
```

Output:
```
{'XRefCode': '12345'}
DayforceResponse(client=Dayforce(username='your-username', client_namespace='your-client-namespace', dayforce_release=57, api_version='V1', url='https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1'), params={}, resp=<Response [200]>)
{'XRefCode': '67891'}
DayforceResponse(client=Dayforce(username='your-username', client_namespace='your-client-namespace', dayforce_release=57, api_version='V1', url='https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1'), params={}, resp=<Response [200]>)
```
