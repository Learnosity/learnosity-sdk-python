import collections
import unittest

import learnosity_sdk.request

ServiceTestSpec = collections.namedtuple(
    "TestSpec", ["service", "valid", "security", "request"])

ServiceTests = [
    ServiceTestSpec(
        "questions", True, {"user_id": "demo_student"}, {
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
    ),

    ServiceTestSpec(
        "data", True, None, {"limit": 100}
    ),

    ServiceTestSpec(
        "assess", True, None, {"foo": "bar"}
    )
]


class TestServiceRequests(unittest.TestCase):
    """
    Tests instantiating a request for each service.
    """

    key = 'foo'
    secret = 'bar'
    domain = 'localhost'

    def test_init_generate(self):
        for t in ServiceTests:
            # TODO(cera): Much more validation
            security = {
                'consumer_key': self.key,
                'domain': self.domain,
            }
            if t.security is not None:
                security.update(t.security)
            init = learnosity_sdk.request.Init(
                t.service, security, self.secret, request=t.request)

            self.assertTrue(init.generate() is not None)
