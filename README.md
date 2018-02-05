Learnosity Python SDK
=====================

[![Build Status](https://travis-ci.org/Learnosity/learnosity-sdk-python.svg?branch=master)](https://travis-ci.org/Learnosity/learnosity-sdk-python)

This package was based off the [PHP
SDK](https://github.com/Learnosity/learnosity-sdk-php), with some small
adjustments to be more pythonic.

Supports:

* generating init packets for Learnosity JavaScript APIs
* server-side Data API usage

# Supported Python Versions

These are the versions we test for:

* 2.7.x
* 3.3.x
* 3.4.x
* 3.5.x
* 3.6.x

# Installation

To install from PyPi:

    pip install learnosity_sdk

Or, from a checkout of this repo:

    pip install .

# Upgrading

If installed from pypi:

    pip install --upgrade learnosity_sdk

Or just do a pull from GitHub and run again in the repo:

    pip install .

# Usage

Simple example:

```python
import learnosity_sdk.request

# Security packet including consumer key
security = {
  'consumer_key': 'MY_API_KEY',
  'domain': 'localhost',
  'user_id': 'demo_student'
}
# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
secret = 'MY_API_SECRET'

# request data for Questions API
questions_request = {
    "type": "local_practice", "state": "initial",
    "questions": [
        {
            "response_id": "60005",
            "type": "association",
            "stimulus": "Match the cities to the parent nation",
            "stimulus_list": [
                "London", "Dublin", "Paris", "Sydney"
            ],
            "possible_responses": [
                "Australia", "France",
                "Ireland", "England"
            ],
            "validation": {
                "valid_responses": [
                    ["England"], ["Ireland"], ["France"], ["Australia"]
                ]
            }
        }
    ]
}

init = learnosity_sdk.request.Init(
    'questions', security, secret,
    request=questions_request
)

# Get the JSON that can be rendered into the page and passed to LearnosityApp.init
signed_request = init.generate()
```

Data API example:

```python
import json

from learnosity_sdk.request import DataApi

security = {
    'consumer_key': 'MY_API_KEY',
    'domain': 'localhost'
}
# WARNING: The consumer secret should not be committed to source control.
consumer_secret = 'MY_API_SECRET'

endpoint = 'https://data.learnosity.com/latest/itembank/items'
data_request = {
    'references': ['item_1', 'item_2'],
}
action = 'get'

client = DataApi()

# make a single request for the first page of results
# returns a requests.Response object
res = client.request(endpoint, security, consumer_secret, data_request, action)
# print the length of the items list (for the first page)
print(len(res.json()['data']))

# iterate over all results
# this returns an iterator of results, abstracting away the paging
for item in client.results_iter(endpoint, security, consumer_secret, data_request, action):
    # prints each item in the result
    print(json.dumps(item))

# request all results as a list
# using `list` we can easily download all the results into a single list
items = list(client.results_iter(endpoint, security, consumer_secret, data_request, action))
# print the length of the items list (will print the total number of items)
print(len(items))

# iterate over each page of results
# this can be useful if the result set is too big to practically fit in memory all at once
for result in client.request_iter(endpoint, security, consumer_secret, data_request, action):
    # print the length of each page of the items list (will print a line for each page in the results)
    print(len(result['data']))
```

# Tests

To run the tests, run `tox` from the project directory. This will run tests several different versions of python.

If you don't have `tox` installed, run:

    pip install tox

This assumes that you have `pyenv` or a similar tool set up to provide python binaries for 2.7, 3.3, 3.4, 3.5 and 3.6.

Alternatively, if you only care about the version you're currently running, you can just:

    pip install -r requirements-dev.txt
    python setup.py test

# Deploying to PyPi

1. Update the version number in `setup.py`
2. Install `twine` (`pip install twine`) and set up `~/.pypirc` (See https://packaging.python.org/tutorials/distributing-packages/)
3. Run `python setup.py sdist` to create the source distribution
4. Run `python setup.py bdist_wheel --universal` to create the binary distribution
5. Run `twine upload dist/*` to deploy the distributions to PyPi

You will need to be set up as a maintainer in order to do this.

