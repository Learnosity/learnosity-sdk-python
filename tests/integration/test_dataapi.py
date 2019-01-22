import unittest
import os
from learnosity_sdk.request import DataApi

# This test uses the consumer key and secret for the demos consumer
# this is the only consumer with publicly available keys
security = {
    'consumer_key': 'yis0TYCu7U9V4o7M',
    'domain': 'demos.learnosity.com'
}
# WARNING: Normally the consumer secret should not be committed to a public
# repository like this one. Only this specific key is publically available.
consumer_secret = '74c5fd430cf1242a527f6223aebd42d30464be22'
request = {
    # These items should already exist for the demos consumer
    'references': ['item_2', 'item_3'],
    'limit': 1
}
action = 'get'
endpoint = '/itembank/items'
dummy_responses = [{
    'meta': {
        'status': True,
        'timestamp': 1514874527,
        'records': 2,
        'next': '1'
    },
    'data': [{'id': 'a'}]
}, {
    'meta': {
        'status': True,
        'timestamp': 1514874527,
        'records': 2
    },
    'data': [{'id': 'b'}]
}]


class IntegrationTestDataApiClient(unittest.TestCase):

    def _build_base_url(self):
        env = os.environ
        env_domain = ''
        region_domain = '.learnosity.com'
        if 'ENV' in env.keys() and env['ENV'] != 'prod':
            env_domain = '.' + env['ENV']
        elif 'REGION' in env.keys() and env['REGION'] != 'prod':
            region_domain = env['REGION']

        version_path = 'v1'
        if 'ENV' in env.keys() and env['ENV'] == 'vg':
            version_path = 'latest'
        elif 'VER' in env.keys():
            version_path = env['VER']

        base_url = "https://data%s%s/%s" % (env_domain, region_domain, version_path)

        print('Using base URL: ' + base_url)

        return base_url


    def test_real_request(self):
        """Make a request against Data Api to ensure the SDK works"""
        client = DataApi()
        res = client.request(self._build_base_url() + endpoint, security, consumer_secret, request,
                             action)
        print(res.request.url)
        print(res.request.body)
        print(res.content)
        returned_json = res.json()
        assert len(returned_json['data']) > 0
        returned_ref = returned_json['data'][0]['reference']
        assert returned_ref in request['references']

    def test_paging(self):
        """Verify that paging works"""
        client = DataApi()
        pages = client.request_iter(self._build_base_url() + endpoint, security, consumer_secret,
                                    request, action)
        results = set()
        for page in pages:
            if page['data']:
                results.add(page['data'][0]['reference'])

        assert len(results) == 2
        assert results == {'item_2', 'item_3'}

