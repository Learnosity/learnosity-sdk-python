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
action = 'get'

items_request = {
    # These items should already exist for the demos consumer
    'references': ['item_2', 'item_3'],
    'limit': 1
}
items_endpoint = '/itembank/items'

questions_request = {
    # These items should already exist for the demos consumer
    'item_references': ['py-sdk-test-2019-1', 'py-sdk-test-2019-2'],
    'limit': 1
}
questions_endpoint = '/itembank/questions'


class IntegrationTestDataApiClient(unittest.TestCase):

    @staticmethod
    def __build_base_url():
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

        return base_url

    def test_real_request(self):
        """Make a request against Data Api to ensure the SDK works"""
        client = DataApi()
        res = client.request(self.__build_base_url() + items_endpoint, security, consumer_secret, items_request,
                             action)
        returned_json = res.json()

        assert len(returned_json['data']) > 0

        returned_ref = returned_json['data'][0]['reference']
        assert returned_ref in items_request['references']

    def test_paging(self):
        """Verify that paging works"""
        client = DataApi()
        pages = client.request_iter(self.__build_base_url() + items_endpoint, security, consumer_secret,
                                    items_request, action)
        results = set()

        for page in pages:
            if page['data']:
                results.add(page['data'][0]['reference'])

        assert len(results) == 2
        assert results == {'item_2', 'item_3'}

    def test_real_request_with_special_characters(self):
        """Make a request against Data Api to ensure the SDK works"""
        client = DataApi()

        # Add a reference containing special characters to ensure
        # signature creation works with special characters in the request
        local_items_request = items_request.copy()  # prevent modifying the base fixture
        local_items_request['references'] = items_request['references'].copy()  # prevent modifying the base fixture's list
        local_items_request['references'].append('тест')

        res = client.request(self.__build_base_url() + items_endpoint, security, consumer_secret, items_request,
                             action)
        returned_json = res.json()

        assert len(returned_json['data']) > 0

        returned_ref = returned_json['data'][0]['reference']
        assert returned_ref in items_request['references']

    def test_real_question_request(self):
        """Make a request against Data Api to ensure the SDK works"""
        client = DataApi()

        questions_request['limit'] = 3
        res = client.request(self.__build_base_url() + questions_endpoint, security, consumer_secret, questions_request,
                             action)

        returned_json = res.json()
        assert len(returned_json['data']) > 0

        keys = set()
        for key in returned_json['data']:
            keys.add(key)

        assert keys == {'py-sdk-test-2019-1', 'py-sdk-test-2019-2'}

    def test_question_paging(self):
        """Verify that paging works"""
        client = DataApi()

        pages = client.request_iter(self.__build_base_url() + questions_endpoint, security, consumer_secret,
                                    questions_request, action)

        results = []
        for page in pages:
            if page['data']:
                results.append(page['data'])

        keys = set()
        for row in results:
            for key in row.keys():
                keys.add(key)

        assert len(results) == 3
        assert keys == {'py-sdk-test-2019-1', 'py-sdk-test-2019-2'}
