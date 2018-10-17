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

## Questions API

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

questions_init = learnosity_sdk.request.Init(
    'questions', security, secret,
    request=questions_request
)

# Get the JSON that can be rendered into the page and passed to LearnosityApp.init
signed_request = questions_init.generate()
```

## Items API

Request packet generation containing signature could look as follows:
```python
#!/usr/bin/env python
from learnosity_sdk.request import Init
from learnosity_sdk.uuid import Uuid

# Security packet including consumer key
security = {
  'consumer_key': 'yis0TYCu7U9V4o7M',
  # Change to your domain, e.g. 127.0.0.1, learnosity.com
  'domain': 'localhost',
}
# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
secret = '74c5fd430cf1242a527f6223aebd42d30464be22'

# example request data for Items API
items_request = items_request = {
    "rendering_type": "inline",
    "user_id": "12345678",
    "session_id": Uuid.generate()
    "type": "submit_practice",
    "activity_id": "exampleActivity",
    "name": "Items API demo - inline activity.",
    "items": [
        "classification_1",
        "multiple_choice_1"
    ]
}

init = Init(
    'items', security, secret,
    request=items_request
)

# Get the JSON that can be rendered into the page and passed to LearnosityItems.init
print(init.generate())
```
Corresponding HTML template (using Django template markup):
```html
<html>
    <head>
    </head>
    <body>
        <script src="https://items.learnosity.com/?v1"></script>
        <span class="learnosity-item" data-reference="multiple_choice_1"></span>
        <span class="learnosity-item" data-reference="classification_1"></span>
        <script>
            <!-- `generated` should be the unescaped string obtained from Init.generate() method -->
            var itemsApp = LearnosityItems.init({{ generated|safe }});
        </script>
    </body>
</html>
```


## Data API

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

## Events API

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
events_request = {
	"users": [ "diego", "manny", "sid"  ]
}

events_init = learnosity_sdk.request.Init(
    'events', security, secret,
    request=events_request
)

# Get the JSON that can be rendered into the page and passed to LearnosityApp.init
signed_request = events_init.generate()
print(signed_request)
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
2. Install the dev requirements `pip install -r requirements-dev.txt`
3. Run `python setup.py sdist` to create the source distribution
4. Run `python setup.py bdist_wheel --universal` to create the binary distribution
5. Run `twine upload dist/*` to deploy the distributions to PyPi

You will need to be set up as a maintainer in order to do this.
