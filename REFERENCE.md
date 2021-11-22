# Learnosity Python-SDK: Reference guide

## Usage

The following examples show how to use the SDK with the various Learnosity APIs.

## Questions API

```python
import learnosity_sdk.request
from learnosity_sdk.utils import Uuid
from .. import config # Load config.py, which stores the consumer key and secret.

# Generate the user ID and session ID as UUIDs.
user_id = Uuid.generate()
session_id = Uuid.generate()

# Set variables for the web server.
# Change to your domain, e.g. 127.0.0.1, learnosity.com
host = 'localhost'
port = 8000

# Security packet including consumer key
security = {
  'consumer_key': config.consumer_key,
  'domain': host,
  'user_id': user_id
}

# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
secret = config.consumer_secret

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
from learnosity_sdk.utils import Uuid
from .. import config # Load config.py, which stores the consumer key and secret.

# Generate the user ID and session ID as UUIDs.
user_id = Uuid.generate()
session_id = Uuid.generate()

# Set variables for the web server.
# Change to your domain, e.g. 127.0.0.1, learnosity.com
host = 'localhost'
port = 8000

# Security packet including consumer key
security = {
  'consumer_key': config.consumer_key,
  'domain': host,
}
# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
secret = config.consumer_secret

# example request data for Items API
items_request = items_request = {
    "rendering_type": "inline",
    "user_id": user_id,
    "session_id": session_id,
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


## Data API 1

```python
import json
from learnosity_sdk.request import DataApi
from learnosity_sdk.utils import Uuid
from .. import config # Load config.py, which stores the consumer key and secret.

# Generate the user ID and session ID as UUIDs.
user_id = Uuid.generate()
session_id = Uuid.generate()

# Set variables for the web server.
# Change to your domain, e.g. 127.0.0.1, learnosity.com
host = 'localhost'
port = 8000

# consumer key for API access, and domain
security = {
    'consumer_key': config.consumer_key,
    'domain': host
}
# WARNING: The consumer secret should not be committed to source control.
consumer_secret = config.consumer_secret

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

## Data API 2

``` python
#!/usr/bin/env python
import json

from learnosity_sdk.request import DataApi # Load Learnosity SDK
from .. import config # Load config.py, which stores the consumer key and secret.

# Set variables for the web server.
# Change to your domain, e.g. 127.0.0.1, learnosity.com
host = 'localhost'
port = 8000

# consumer key for API access, and domain
security = {
    # XXX: This is a Learnosity Demos consumer; replace it with your own consumer key
    'consumer_key': config.consumer_key,
    'domain': host
}
# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
consumer_secret = consumer_secret = config.consumer_secret

data_request = { 'limit': 1 }

action = 'get'
itembankUri = 'https://data.learnosity.com/latest/itembank/items'

client = DataApi()

# iterate over all results
# this returns an iterator of results, abstracting away the paging
i = 0
for item in client.results_iter(itembankUri, security, consumer_secret, data_request, action):
    i += 1
    print(">>> [%s (%d)] %s" % (
        itembankUri,
        i,
        json.dumps(item)
        ))
    if i > 5:
        break

# iterate over each page of results
# this can be useful if the result set is too big to practically fit in memory all at once
i = 0
data_request = { "limit": 2 }
for result in client.request_iter(itembankUri, security, consumer_secret, data_request, action):
    i+=1
    # print the length of each page of the items list (will print a line for each page in the results)
    print(">>> [%s (%d)] %s" % (
        itembankUri,
        i,
        json.dumps(item)
        ))
    if i > 5:
        break
```

## Events API

```python
import learnosity_sdk.request
from learnosity_sdk.utils import Uuid
from .. import config # Load config.py, which stores the consumer key and secret.

# Generate the user ID and session ID as UUIDs.
user_id_1 = Uuid.generate()
user_id_2 = Uuid.generate()
user_id_3 = Uuid.generate()
session_id = Uuid.generate()

# Set variables for the web server.
host = 'localhost'
port = 8000

# Security packet including consumer key
security = {
  'consumer_key': config.consumer_key,
  'domain': host,
  'user_id': user_id
}
# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
secret = config.consumer_secret

# request data for Questions API
events_request = {
	"users": [ user_id_1, user_id_2, user_id_3  ]
}

events_init = learnosity_sdk.request.Init(
    'events', security, secret,
    request=events_request
)

# Get the JSON that can be rendered into the page and passed to LearnosityApp.init
signed_request = events_init.generate()
print(signed_request)
```

## Further reading
Thanks for reading to the end! Find more information about developing an app with Learnosity on our documentation sites: 
<ul>
<li><a href="http://help.learnosity.com">help.learnosity.com</a> -- general help portal and tutorials,
<li><a href="http://reference.learnosity.com">reference.learnosity.com</a> -- developer reference site, and
<li><a href="http://authorguide.learnosity.com">authorguide.learnosity.com</a> -- authoring documentation for content creators.
</ul>

Back to [README.md](README.md)