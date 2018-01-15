#!/usr/bin/env python
import learnosity_sdk.request

# Security packet including consumer key
security = {
  'consumer_key': 'yis0TYCu7U9V4o7M',
  'domain': 'localhost',
}
# consumer secret for API access
# WARNING: The consumer secret should not be committed to source control.
secret = '74c5fd430cf1242a527f6223aebd42d30464be22'

# request data for Questions API
items_request = { 'limit': 50 }

init = learnosity_sdk.request.Init(
    'items', security, secret,
    request=items_request
)

# Get the JSON that can be rendered into the page and passed to LearnosityApp.init
print(init.generate())
