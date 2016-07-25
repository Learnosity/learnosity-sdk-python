Learnosity Python SDK
=====================

[![Build Status](https://travis-ci.org/Learnosity/learnosity-sdk-python.svg?branch=master)](https://travis-ci.org/Learnosity/learnosity-sdk-python)

This package was based off the [PHP
SDK](https://github.com/Learnosity/learnosity-sdk-php), with some small
adjustments to be more pythonic.

Supports:

* generating init packets for Learnosity JavaScript APIs

Does not yet support:

* server-side Data API usage

# Supported Python Versions

These are the versions we test for:

* 2.7.x
* 3.3.x
* 3.4.x
* 3.5.x

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

# Tests

To run the tests, run `tox` from the project directory. This will run tests several different versions of python.

If you don't have `tox` installed, run:

	pip install tox

This assumes that you have `pyenv` or a similar tool set up to provide python binaries for 2.7, 3.3, 3.4 and 3.5.

Alternatively, if you only care about the version you're currently running, you can just:

	python setup.py test
