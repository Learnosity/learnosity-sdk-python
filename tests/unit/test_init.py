import collections
import unittest

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
        '$02$8de51b7601f606a7f32665541026580d09616028dde9a929ce81cf2e88f56eb8',
    ),

    ServiceTestSpec(
        "data", True, None, {"limit": 100}, "get",
        '$02$e19c8a62fba81ef6baf2731e2ab0512feaf573ca5ca5929c2ee9a77303d2e197',
    ),

    ServiceTestSpec(
        "assess", True, {"user_id": "$ANONYMIZED_USER_ID"}, {"foo": "bar"}, None,
            '$02$8de51b7601f606a7f32665541026580d09616028dde9a929ce81cf2e88f56eb8',
    ),

    ServiceTestSpec(  # string
        "items", True, {"user_id": "$ANONYMIZED_USER_ID"},
        '{ "user_id" : "$ANONYMIZED_USER_ID", "activity_id": "8E9859C2-CBCF-427B-A478-B8FFC5222DEB", "session_id": "E637AC08-7BF1-48AF-B264-0F40D5BF8898", "rendering_type": "assess", "items": [ "item_1" ] }',
        None,
        '$02$57bfc14e7d1c66d1f370546120dda2195b3ad8ad866c5fcd818c4051389f6df2',
    ),
    ServiceTestSpec(  # Dict
        "items", True, {"user_id": "$ANONYMIZED_USER_ID"},
        { "user_id" : "$ANONYMIZED_USER_ID", "activity_id": "8E9859C2-CBCF-427B-A478-B8FFC5222DEB", "session_id": "E637AC08-7BF1-48AF-B264-0F40D5BF8898", "rendering_type": "assess", "items": [ "item_1" ] },
        None,
        '$02$57bfc14e7d1c66d1f370546120dda2195b3ad8ad866c5fcd818c4051389f6df2',
    ),

    ServiceTestSpec(
        "events", True, None,
        {"users": [ "$ANONYMIZED_USER_ID_1", "$ANONYMIZED_USER_ID_2", "$ANONYMIZED_USER_ID_3", "$ANONYMIZED_USER_ID_4" ] }, None,
        '$02$5c3160dbb9ab4d01774b5c2fc3b01a35ce4f9709c84571c27dfe333d1ca9d349'
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
        """
        Test that Init.generate() generates the desired initOptions
        """
        learnosity_sdk.request.Init.disable_telemetry()
        for t in ServiceTests:
            with self.subTest(repr(t), t=t):
                security = self._prepare_security(t.security)
                init = learnosity_sdk.request.Init(
                    t.service, security, self.secret, request=t.request, action=t.action)

                self.assertFalse(init.is_telemetry_enabled(), 'Telemetry still enabled')
                self.assertEqual(t.signature, init.generate_signature(), 'Signature mismatch')

    def test_no_parameter_mangling(self):
        """ Test that Init.generate() does not modify its parameters """
        learnosity_sdk.request.Init.enable_telemetry()
        for t in ServiceTests:
            with self.subTest(repr(t), t=t):
                request_copy = t.request
                if hasattr(t.request, 'copy'):
                        request_copy = t.request.copy()

                security = self._prepare_security(t.security)
                security_copy = security.copy()

                learnosity_sdk.request.Init(
                    t.service, security_copy, self.secret, request=request_copy, action=t.action)

                self.assertEqual(security, security_copy, 'Original security modified by SDK')
                self.assertEqual(t.request, request_copy, 'Original request modified by SDK')

    def _prepare_security(self, add_security=None):
        # TODO(cera): Much more validation
        security = {
            'consumer_key': self.key,
            'domain': self.domain,
            'timestamp': self.timestamp,
        }
        if add_security is not None:
            security.update(add_security)
        return security
