from typing import Any, Dict, cast
import unittest
import responses
from learnosity_sdk.request import DataApi
from learnosity_sdk.exceptions import DataApiException

class UnitTestDataApiClient(unittest.TestCase):
    """
    Tests to ensure that the Data API client functions correctly.
    """

    def setUp(self) -> None:
        # This test uses the consumer key and secret for the demos consumer
        # this is the only consumer with publicly available keys
        self.security = {
            'consumer_key': 'yis0TYCu7U9V4o7M',
            'domain': 'demos.learnosity.com'
        }
        # WARNING: Normally the consumer secret should not be committed to a public
        # repository like this one. Only this specific key is publicly available.
        self.consumer_secret = '74c5fd430cf1242a527f6223aebd42d30464be22'
        self.request = {
            # These items should already exist for the demos consumer
            'references': ['item_2', 'item_3'],
            'limit': 1
        }
        self.action = 'get'
        self.endpoint = 'https://data.learnosity.com/v1/itembank/items'
        self.dummy_responses = [{
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
        self.invalid_json = "This is not valid JSON!"

    @responses.activate
    def test_request(self) -> None:
        """
        Verify that `request` sends a request after it has been signed
        """
        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json=dummy)
        client = DataApi()
        res = client.request(self.endpoint, self.security, self.consumer_secret, self.request,
                             self.action)
        assert res.json() == self.dummy_responses[0]
        assert responses.calls[0].request.url == self.endpoint
        assert 'signature' in cast(Dict[str, Any], responses.calls[0].request.body)

    @responses.activate
    def test_request_iter(self) -> None:
        """Verify that `request_iter` returns an iterator of pages"""
        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json=dummy)
        client = DataApi()
        pages = client.request_iter(self.endpoint, self.security, self.consumer_secret,
                                    self.request, self.action)
        results = []
        for page in pages:
            results.append(page)

        assert len(results) == 2
        assert results[0]['data'][0]['id'] == 'a'
        assert results[1]['data'][0]['id'] == 'b'

    @responses.activate
    def test_results_iter(self) -> None:
        """Verify that `result_iter` returns an iterator of results"""
        self.dummy_responses[1]['data'] = {'id': 'b'}
        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json=dummy)
        client = DataApi()
        result_iter = client.results_iter(self.endpoint, self.security, self.consumer_secret,
                                          self.request, self.action)
        results = list(result_iter)

        assert len(results) == 2
        assert results[0]['id'] == 'a'
        assert results[1]['id'] == 'b'

    @responses.activate
    def test_results_iter_error_status(self) -> None:
        """Verify that a DataApiException is raised http status is not ok"""
        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json={}, status=500)
        client = DataApi()
        with self.assertRaisesRegex(DataApiException, "server returned HTTP status 500"):
            list(client.results_iter(self.endpoint, self.security, self.consumer_secret,
                                     self.request, self.action))

    @responses.activate
    def test_results_iter_no_meta_status(self) -> None:
        """Verify that a DataApiException is raised when 'meta' 'status' is None"""
        for response in self.dummy_responses:
            # This is for typing purposes only, and should always be True
            if isinstance(response['meta'], dict):
                response['meta']['status'] = None

        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json=dummy)
        client = DataApi()
        with self.assertRaisesRegex(DataApiException, "server returned unsuccessful status:"):
            list(client.results_iter(self.endpoint, self.security, self.consumer_secret,
                                     self.request, self.action))

    @responses.activate
    def test_results_iter_invalid_response_data(self) -> None:
        """Verify that a DataApiException is raised response data isn't valid JSON"""
        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json=None)
        client = DataApi()
        with self.assertRaisesRegex(DataApiException, "server returned invalid json: "):
            list(client.results_iter(self.endpoint, self.security, self.consumer_secret,
                                     self.request, self.action))
