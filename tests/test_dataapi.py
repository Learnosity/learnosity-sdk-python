import unittest
import responses
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
endpoint = 'https://data.learnosity.com/v1/itembank/items'
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


class UnitTestDataApiClient(unittest.TestCase):
    """
    Tests to ensure that the Data API client functions correctly.
    """

    @responses.activate
    def test_request(self):
        """
        Verify that `request` sends a request after it has been signed
        """
        for dummy in dummy_responses:
            responses.add(responses.POST, endpoint, json=dummy)
        client = DataApi()
        res = client.request(endpoint, security, consumer_secret, request,
                             action)
        assert res.json() == dummy_responses[0]
        assert responses.calls[0].request.url == endpoint
        assert 'signature' in responses.calls[0].request.body

    @responses.activate
    def test_request_iter(self):
        """Verify that `request_iter` returns an iterator of pages"""
        for dummy in dummy_responses:
            responses.add(responses.POST, endpoint, json=dummy)
        client = DataApi()
        pages = client.request_iter(endpoint, security, consumer_secret,
                                    request, action)
        results = []
        for page in pages:
            results.append(page)

        assert len(results) == 2
        assert results[0]['data'][0]['id'] == 'a'
        assert results[1]['data'][0]['id'] == 'b'

    @responses.activate
    def test_results_iter(self):
        """Verify that `result_iter` returns an iterator of results"""
        for dummy in dummy_responses:
            responses.add(responses.POST, endpoint, json=dummy)
        client = DataApi()
        result_iter = client.results_iter(endpoint, security, consumer_secret,
                                          request, action)
        results = list(result_iter)

        assert len(results) == 2
        assert results[0]['id'] == 'a'
        assert results[1]['id'] == 'b'


class IntegrationTestDataApiClient(unittest.TestCase):

    def test_real_request(self):
        """Make a request against Data Api to ensure the SDK works"""
        client = DataApi()
        res = client.request(endpoint, security, consumer_secret, request,
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
        pages = client.request_iter(endpoint, security, consumer_secret,
                                    request, action)
        results = set()
        for page in pages:
            if page['data']:
                results.add(page['data'][0]['reference'])

        assert len(results) == 2
        assert results == {'item_2', 'item_3'}

