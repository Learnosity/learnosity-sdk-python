#!/usr/bin/env python
import json

from learnosity_sdk.request import DataApi

security = {
    # XXX: This is a Learnosity Demos consumer; replace it with your own consumer key
    'consumer_key': 'yis0TYCu7U9V4o7M',
    'domain': 'localhost'
}
consumer_secret = '74c5fd430cf1242a527f6223aebd42d30464be22'
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
