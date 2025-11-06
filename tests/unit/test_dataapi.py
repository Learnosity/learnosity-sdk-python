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

        # Verify metadata headers are present
        assert 'X-Learnosity-Consumer' in responses.calls[0].request.headers
        assert responses.calls[0].request.headers['X-Learnosity-Consumer'] == 'yis0TYCu7U9V4o7M'
        assert 'X-Learnosity-Action' in responses.calls[0].request.headers
        assert responses.calls[0].request.headers['X-Learnosity-Action'] == 'get_/itembank/items'
        assert 'X-Learnosity-SDK' in responses.calls[0].request.headers
        # Verify SDK header format is "Python:X.Y.Z" (without 'v' prefix)
        sdk_header = responses.calls[0].request.headers['X-Learnosity-SDK']
        assert sdk_header.startswith('Python:')
        assert not sdk_header.startswith('Python:v')

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

    def test_extract_consumer(self) -> None:
        """Verify that consumer key is correctly extracted from security packet"""
        client = DataApi()
        consumer = client._extract_consumer(self.security)
        assert consumer == 'yis0TYCu7U9V4o7M'

    def test_extract_consumer_missing(self) -> None:
        """Verify that empty string is returned when consumer_key is missing"""
        client = DataApi()
        consumer = client._extract_consumer({})
        assert consumer == ''

    def test_derive_action_with_version(self) -> None:
        """Verify that action is correctly derived from endpoint with version"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v1/itembank/items', 'get')
        assert action == 'get_/itembank/items'

    def test_derive_action_with_latest(self) -> None:
        """Verify that action is correctly derived from endpoint with 'latest' version"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/latest/itembank/questions', 'get')
        assert action == 'get_/itembank/questions'

    def test_derive_action_without_version(self) -> None:
        """Verify that action is correctly derived from endpoint without version"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/itembank/activities', 'set')
        assert action == 'set_/itembank/activities'

    def test_derive_action_session_scores(self) -> None:
        """Verify that action is correctly derived for session_scores endpoint"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v1/session_scores', 'get')
        assert action == 'get_/session_scores'

    def test_derive_action_route_starting_with_v(self) -> None:
        """Verify that routes starting with 'v' but not version numbers are not stripped"""
        client = DataApi()
        # Routes like /valid, /vendors, /version should NOT be treated as version prefixes
        action = client._derive_action('https://data.learnosity.com/valid/route', 'get')
        assert action == 'get_/valid/route'

    def test_derive_action_with_v2(self) -> None:
        """Verify that v2 version prefix is correctly stripped"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v2/itembank/items', 'get')
        assert action == 'get_/itembank/items'

    def test_derive_action_with_v_only(self) -> None:
        """Verify that a route segment of just 'v' is not treated as a version"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v/items', 'get')
        assert action == 'get_/v/items'

    def test_derive_action_with_lts_version(self) -> None:
        """Verify that LTS version format like v2025.1.LTS is correctly stripped"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v2025.1.LTS/sessions/responses', 'get')
        assert action == 'get_/sessions/responses'

    def test_derive_action_with_latest_lts(self) -> None:
        """Verify that latest-lts version is correctly stripped"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/latest-lts/itembank/items', 'get')
        assert action == 'get_/itembank/items'

    def test_derive_action_with_developer(self) -> None:
        """Verify that developer version is correctly stripped"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/developer/sessions/responses', 'get')
        assert action == 'get_/sessions/responses'

    def test_derive_action_with_preview_version(self) -> None:
        """Verify that preview version format like v2025.3.preview1 is correctly stripped"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v2025.3.preview1/itembank/items', 'get')
        assert action == 'get_/itembank/items'

    def test_derive_action_with_preview_version_multi_digit(self) -> None:
        """Verify that preview version with multi-digit preview number is correctly stripped"""
        client = DataApi()
        action = client._derive_action('https://data.learnosity.com/v2025.1.preview123/itembank/questions', 'get')
        assert action == 'get_/itembank/questions'


    @responses.activate
    def test_metadata_headers_in_paginated_requests(self) -> None:
        """Verify that metadata headers are sent in all paginated requests"""
        for dummy in self.dummy_responses:
            responses.add(responses.POST, self.endpoint, json=dummy)
        client = DataApi()
        # Consume the iterator to trigger the requests
        list(client.request_iter(self.endpoint, self.security, self.consumer_secret,
                                 self.request, self.action))

        # Verify both requests have the metadata headers
        assert len(responses.calls) == 2
        for call in responses.calls:
            assert 'X-Learnosity-Consumer' in call.request.headers
            assert call.request.headers['X-Learnosity-Consumer'] == 'yis0TYCu7U9V4o7M'
            assert 'X-Learnosity-Action' in call.request.headers
            assert call.request.headers['X-Learnosity-Action'] == 'get_/itembank/items'
            assert 'X-Learnosity-SDK' in call.request.headers
            # Verify SDK header format is "Python:X.Y.Z" (without 'v' prefix)
            sdk_header = call.request.headers['X-Learnosity-SDK']
            assert sdk_header.startswith('Python:')
            assert not sdk_header.startswith('Python:v')
