# dayforce-client
[![PyPI version](https://badge.fury.io/py/dayforce-client.svg)](https://badge.fury.io/py/dayforce-client)
![PyPI - Status](https://img.shields.io/pypi/status/dayforce-client)
[![Build Status](https://travis-ci.com/goodeggs/dayforce-client.svg?branch=master)](https://travis-ci.com/goodeggs/dayforce-client.svg?branch=master)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dayforce-client)
![PyPI - License](https://img.shields.io/pypi/l/dayforce-client)

dayforce-client is a python SDK for interfacing with the Dayforce REST API and SFTP server.

## Installation

```bash
$ pip3 install dayforce-client
```

## Basic Usage (Rest API)

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

...


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

...

{'XRefCode': '12345'}
DayforceResponse(client=Dayforce(username='your-username', client_namespace='your-client-namespace', dayforce_release=57, api_version='V1', url='https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1'), params={}, resp=<Response [200]>)
{'XRefCode': '67891'}
DayforceResponse(client=Dayforce(username='your-username', client_namespace='your-client-namespace', dayforce_release=57, api_version='V1', url='https://usr57-services.dayforcehcm.com/Api/your-client-namespace/V1'), params={}, resp=<Response [200]>)
```

## Basic Usage (SFTP client)

```python
client = DayforceSFTP(
  hostname='foo01.dayforcehcm.com',
  username='mycompany',
  password='sekret',
  disable_host_key_checking=True,
)
client.connect()
```

Using `disable_host_key_checking` is discouraged, however. Instead, use `ssh-keyscan` to retrieve a known-good key (better yet, see if Dayforce will provide it to you!) and pass it in to the construtor.

```shell
ssh-keyscan foo01.dayforcehcm.com
# foo01.dayforcehcm.com:22 SSH-2.0-9.99 FlowSsh: Bitvise SSH Server (WinSSHD)
foo01.dayforcehcm.com ssh-rsa AAAAB3...snip...XYZ
```

```python
client = DayforceSFTP(
  hostname='foo01.dayforcehcm.com',
  username='mycompany',
  password='sekret',
  host_key='AAAAB3...snip...XYZ',
)
client.connect()
```

### Batch Imports

Dayforce provides the ability to batch import data via SFTP. This client wraps up most of the business logic around this process, and exposes a simple, high-level API.

```python
from dayforce import DayforceSFTP, ImportError, ImportPending

client = DayforceSFTP(hostname=...)
with client.connect():
  batch_token = client.put_import('./local/path/to/batch-20191225T000000.csv', type='KpiTargetImport')
  while True:
    try:
      client.raise_for_import_status(batch_token)
      print('batch import succeeded')
      break
    except ImportPending e:
      sleep 10
      continue
    except ImportError e:
      print('batch import failed')
      break
```

## Development

```shell
python3 -m venv install .venv
source .venv/bin/activate
make dev_install
make test
```
