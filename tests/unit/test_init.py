import collections
import unittest
import json

import learnosity_sdk.request

ServiceTestSpec = collections.namedtuple(
    "TestSpec", [
            "service",
            "valid",
            "security",  # security can be None to use the default, or an Dict to extend the default
            "request",
            "action",
            "signature",
    ]
)

ServiceTests = [
    ServiceTestSpec(
        "questions",
        True,
        {"user_id": "$ANONYMIZED_USER_ID"},
        {
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
        },
        None,
        '03f4869659eeaca81077785135d5157874f4800e57752bf507891bf39c4d4a90',
    ),

    ServiceTestSpec(
        "data", True, None, {"limit": 100}, "get",
        'e1eae0b86148df69173cb3b824275ea73c9c93967f7d17d6957fcdd299c8a4fe',
    ),

    ServiceTestSpec(
        "assess", True, {"user_id": "$ANONYMIZED_USER_ID"}, {"foo": "bar"}, None,
            '03f4869659eeaca81077785135d5157874f4800e57752bf507891bf39c4d4a90',
    ),

    ServiceTestSpec(  # string
        "items", True, {"user_id": "$ANONYMIZED_USER_ID"},
        '{ "user_id" : "$ANONYMIZED_USER_ID", "activity_id": "8E9859C2-CBCF-427B-A478-B8FFC5222DEB", "session_id": "E637AC08-7BF1-48AF-B264-0F40D5BF8898", "rendering_type": "assess", "items": [ "item_1" ] }',
        None,
        '584e9c7cae8530e92b258b3ac4361e58484a5e604f0b17d0acd8d7298cb8230a',
    ),
    ServiceTestSpec(  # Dict
        "items", True, {"user_id": "$ANONYMIZED_USER_ID"},
        { "user_id" : "$ANONYMIZED_USER_ID", "activity_id": "8E9859C2-CBCF-427B-A478-B8FFC5222DEB", "session_id": "E637AC08-7BF1-48AF-B264-0F40D5BF8898", "rendering_type": "assess", "items": [ "item_1" ] },
        None,
        '584e9c7cae8530e92b258b3ac4361e58484a5e604f0b17d0acd8d7298cb8230a',
    ),

    ServiceTestSpec(
        "events", True, None,
        {"users": [ "$ANONYMIZED_USER_ID_1", "$ANONYMIZED_USER_ID_2", "$ANONYMIZED_USER_ID_3", "$ANONYMIZED_USER_ID_4" ] }, None,
        '20739eed410d54a135e8cb3745628834886ab315bfc01693ce9acc0d14dc98bf'
    ),
]


class TestServiceRequests(unittest.TestCase):
    """
    Tests instantiating a request for each service.
    """

    key = 'yis0TYCu7U9V4o7M'
    secret = '74c5fd430cf1242a527f6223aebd42d30464be22'
    domain = 'localhost'
    timestamp = '20140626-0528'

    def test_init_generate(self):
        """ Test that Init.generate() generates the desired initOptions """
        learnosity_sdk.request.Init.disable_telemetry()
        for t in ServiceTests:
            with self.subTest(repr(t), t=t):
                # TODO(cera): Much more validation
                security = {
                    'consumer_key': self.key,
                    'domain': self.domain,
                    'timestamp': self.timestamp,
                }
                if t.security is not None:
                    security.update(t.security)

                init = learnosity_sdk.request.Init(
                    t.service, security, self.secret, request=t.request, action=t.action)

                self.assertFalse(init.is_telemetry_enabled(), 'Telemetry still enabled')
                self.assertEqual(t.signature, init.generate_signature(), 'Signature mismatch')
