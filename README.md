Learnosity Python SDK
=====================

This package was based off the [PHP
SDK](https://github.com/Learnosity/learnosity-sdk-php], with some small
adjustments to be more pythonic.

Supports:

* generating init packets for Learnosity JavaScript APIs

Does not yet support:

* server-side Data API usage

Installation
------------

To install from PyPi:

    pip install learnosity_sdk

Or, from a checkout of this repo:

    python setup.py install

Usage
-----

Simple example:

```python
import learnosity_sdk.request

# consumer secret for API access
secret = 'MY_API_SECRET'

# Security packet including consumer key
security = {
  'consumer_key': 'MY_API_KEY',
  'domain': 'localhost',
  'user_id': 'demo_student'
}

# request data for Questions API
request = {
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
	request=request
)

# Get the JSON that can be rendered into the page and passed to LearnosityApp.init
request = init.generate()
```

Tests
-----

To run the tests, run `tox` from the project directory. This will run tests in both Python 2.7 and Python 3.4.

If you don't have `tox` installed, run:

	pip install tox
