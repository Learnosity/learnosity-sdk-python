import requests
import copy

from learnosity_sdk.exceptions import DataApiException
from learnosity_sdk.request import Init


class DataApi(object):

    def request(self, endpoint, security_packet,
                secret, request_packet={}, action='get'):
        """
        Make a request to Data API

        Uses the `requests` library to make a single call against Data API.
        If the data spans multiple pages, then the meta.next property
        of the response will need to be used to obtain the rest of the data.

        see https://docs.learnosity.com/analytics/data/quickstart

        Args:
            endpoint (string): The full url to the endpoint
            security_packet (dict): The security object
            secret (string): The consumer secret key
            request_packet (dict): The request parameters
            action (string): 'get', 'set', 'update', etc.

        Returns:
            requests.Response: The response object

            see http://docs.python-requests.org/en/master/api/#requests.Request
        """
        init = Init('data', security_packet, secret, request_packet, action)
        return requests.post(endpoint, data=init.generate())

    def results_iter(self, endpoint, security_packet,
                     secret, request_packet={},
                     action='get'):
        """
        Return an iterator of all results from a request to Data API

        This method yields each element of the `data` result array,
        automatically fetching the next page of results when needed.

        Args:
            endpoint (string): The full url to the endpoint
            security_packet (dict): The security object
            secret (string): The consumer secret key
            request_packet (dict): The request parameters
            action (string): 'get', 'set', 'update', etc.

        Yields:
            dict: An individual result (item, question, etc.) from the server

        Raises:
            DataApiException: Raised if there was a problem fetching
            data or if the server returns an invalid response.
        """
        for response in self.request_iter(endpoint, security_packet,
                                          secret, request_packet,
                                          action):
            if type(response['data']) == dict:
                for key, value in response['data'].iteritems():
                    yield {key: value}
            else:
                for result in response['data']:
                    yield result

    def request_iter(self, endpoint, security_packet,
                     secret, request_packet={},
                     action='get'):
        """
        Iterate over the pages of results of a query to data api

        Additional requests are sent to to Data API to fetch pages as needed.

        Args:
            endpoint (string): The full url to the endpoint
            security_packet (dict): The security object
            secret (string): The consumer secret key
            request_packet (dict): The request parameters
            action (string): 'get', 'set', 'update', etc.

        Yields:
            dict: The response from the server

            A typical response contains `meta` and `data` keys.

        Raises:
            DataApiException: Raised if there was a problem fetching
            data or if the server returns an invalid response.
        """

        # just in case the security_packet or request_packet
        # are modified between yields
        security_packet = copy.deepcopy(security_packet)
        request_packet = copy.deepcopy(request_packet)

        data_end = False

        while not data_end:
            res = self.request(
                endpoint,
                security_packet,
                secret,
                request_packet,
                action
            )

            if not res.ok:
                raise DataApiException(
                    'server returned HTTP status ' + str(res.status_code)
                    + ': ' + res.text)

            try:
                data = res.json()
            except ValueError:
                raise DataApiException(
                    'server returned invalid json: ' + res.text)

            if 'next' in data['meta'] and len(data['data']) > 0:
                request_packet['next'] = data['meta']['next']
            else:
                data_end = True

            if not data['meta']['status']:
                raise DataApiException(
                    'server returned unsuccessful status: ' + res.text)
            else:
                yield data
