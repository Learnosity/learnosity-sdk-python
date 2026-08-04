import collections
import json
from typing import Any, Dict, List, Optional, Tuple
import unittest

import learnosity_sdk.request


def as_dict(value: object) -> Dict[str, Any]:
    """
    Narrow ``value`` to ``Dict[str, Any]`` for both mypy and the test runner.

    Unlike ``typing.cast``, ``isinstance`` here is a real, always-executed
    check: mismatches fail the test with a clear message instead of being
    silently trusted.
    """
    if not isinstance(value, dict):
        raise AssertionError(f'Expected a dict, got {type(value).__name__}: {value!r}')
    return value

ServiceTestSpec = collections.namedtuple(
    "ServiceTestSpec", [
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

    ServiceTestSpec(
        "annotations", True, None,
            {"group_id":"a91faa6e-8bd2-4365-872d-f644f1f41853","modules":{"drawing":True},"editable":True},
            "get",
            '$02$13592f855c1f52f8d1c534c3816b54790786555e217be62db46117899df8387e',
    ),
    ServiceTestSpec(
        "authoraide",
        True,
        {
            "consumer_key": "yis0TYCu7U9V4o7M",
            "domain": "labs.dev.learnosity.com"
        },
        {
            "user": {
                "id": "$ANONYMIZED_USER_ID",
                "firstname": "test_fn",
                "lastname": "test_ln",
                "email": "test@learnosity.com"
            }
        },
        None,
        '$02$1d86da491734ddf1dbc16b4fe039fb1fd1be9babe3af52c4a0a916b4ede47a58',
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

    def test_init_generate(self) -> None:
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

    def test_no_parameter_mangling(self) -> None:
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

    def _prepare_security(self, add_security: Optional[Dict[str, str]]=None) -> Dict[str, str]:
        # TODO(cera): Much more validation
        security = {
            'consumer_key': self.key,
            'domain': self.domain,
            'timestamp': self.timestamp,
        }
        if add_security is not None:
            security.update(add_security)
        return security


class TestRequestTypeHandling(unittest.TestCase):
    """
    Tests for the ``isinstance(self.request, dict)`` guards added to ``Init``.

    These guards make request handling robust when ``self.request`` is ``None``
    or a non-dict value (e.g. a JSON array passed as a string), and when nested
    keys such as ``questionsApiActivity`` are not dicts. Before the guards these
    inputs raised at runtime:
      * an events request that parsed to a list raised
        ``AttributeError: 'list' object has no attribute 'get'``
      * a non-dict ``questionsApiActivity`` raised
        ``AttributeError: 'str' object has no attribute 'keys'``
    The tests below lock in the defensive behaviour so it cannot regress.
    """

    key = 'yis0TYCu7U9V4o7M'
    secret = '74c5fd430cf1242a527f6223aebd42d30464be22'
    domain = 'localhost'
    timestamp = '20140626-0528'

    def setUp(self) -> None:
        # Behaviour under test is independent of telemetry. Disable it for
        # determinism and restore the default (enabled) afterwards so test
        # ordering (pytest-randomly) cannot leak state between tests.
        learnosity_sdk.request.Init.disable_telemetry()
        self.addCleanup(learnosity_sdk.request.Init.enable_telemetry)

    def _security(self, add: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        security = {
            'consumer_key': self.key,
            'domain': self.domain,
            'timestamp': self.timestamp,
        }
        if add is not None:
            security.update(add)
        return security

    def test_none_request_does_not_raise(self) -> None:
        """A ``None`` request must be handled by every service without raising."""
        cases: List[Tuple[str, Dict[str, str]]] = [
            ('items', self._security()),
            ('reports', self._security()),
            ('events', self._security()),
            ('assess', self._security({'user_id': '$ANONYMIZED_USER_ID'})),
            ('questions', self._security({'user_id': '$ANONYMIZED_USER_ID'})),
        ]
        for service, security in cases:
            with self.subTest(service=service):
                init = learnosity_sdk.request.Init(
                    service, security, self.secret, request=None)
                # A signature must still be produced and be well-formed.
                self.assertTrue(init.generate_signature().startswith('$02$'))

    def test_events_non_dict_request_is_ignored(self) -> None:
        """
        An events request that parses to a non-dict (JSON array) must not add
        hashed users to the security packet and must not raise. Regression for
        ``AttributeError: 'list' object has no attribute 'get'``.
        """
        init = learnosity_sdk.request.Init(
            'events', self._security(), self.secret, request='[1, 2, 3]')
        self.assertNotIn('users', init.security)

    def test_non_dict_request_is_ignored_in_generate(self) -> None:
        """
        For 'questions' and 'assess', a request that parses to a non-dict must
        be skipped by ``generate()`` rather than merged into the output.
        """
        for service in ('questions', 'assess'):
            with self.subTest(service=service):
                init = learnosity_sdk.request.Init(
                    service, self._security({'user_id': '$ANONYMIZED_USER_ID'}),
                    self.secret, request='[1, 2, 3]')
                output = init.generate(encode=False)
                # A request passed as a string is always JSON-encoded on output.
                parsed = json.loads(output) if isinstance(output, str) else output
                self.assertIsInstance(parsed, dict)
                self.assertNotIn(1, parsed.values())

    def test_questions_generate_merges_dict_request(self) -> None:
        """
        'questions' ``generate()`` must merge a dict request into the output
        (and strip ``domain`` from the security packet).
        """
        init = learnosity_sdk.request.Init(
            'questions', self._security({'user_id': '$ANONYMIZED_USER_ID'}),
            self.secret, request={'foo': 'bar'})
        output = as_dict(init.generate(encode=False))
        self.assertEqual(output['foo'], 'bar')
        self.assertNotIn('domain', output)

    def test_assess_generate_merges_dict_request(self) -> None:
        """'assess' ``generate()`` must merge a dict request into the output."""
        init = learnosity_sdk.request.Init(
            'assess', self._security({'user_id': '$ANONYMIZED_USER_ID'}),
            self.secret, request={'foo': 'bar'})
        output = as_dict(init.generate(encode=False))
        self.assertEqual(output['foo'], 'bar')

    def test_assess_questions_api_activity_is_signed(self) -> None:
        """
        When an 'assess' request contains a ``questionsApiActivity`` dict, it
        must be replaced with a signed activity (consumer_key, timestamp,
        user_id, signature) while preserving any additional keys.
        """
        init = learnosity_sdk.request.Init(
            'assess', self._security({'user_id': '$ANONYMIZED_USER_ID'}),
            self.secret, request={'questionsApiActivity': {'foo': 'bar'}})

        request = as_dict(init.request)
        activity = request['questionsApiActivity']
        self.assertEqual(activity['consumer_key'], self.key)
        self.assertEqual(activity['user_id'], '$ANONYMIZED_USER_ID')
        self.assertEqual(activity['timestamp'], self.timestamp)
        self.assertTrue(activity['signature'].startswith('$02$'))
        # Extra keys supplied by the caller must be retained.
        self.assertEqual(activity['foo'], 'bar')

    def test_assess_questions_api_activity_non_dict_is_ignored(self) -> None:
        """
        A non-dict ``questionsApiActivity`` must be left untouched and must not
        raise. Regression for ``AttributeError: 'str' object has no attribute
        'keys'``.
        """
        init = learnosity_sdk.request.Init(
            'assess', self._security({'user_id': '$ANONYMIZED_USER_ID'}),
            self.secret, request={'questionsApiActivity': 'not-a-dict'})

        request = as_dict(init.request)
        self.assertEqual(request['questionsApiActivity'], 'not-a-dict')

    def test_assess_activity_uses_activity_domain_and_strips_stale_keys(self) -> None:
        """
        When the security packet has no ``domain``, the domain from
        ``questionsApiActivity`` is used for signing; stale identity keys
        supplied by the caller are stripped and replaced, while other keys are
        preserved.
        """
        security = {
            'consumer_key': self.key,
            'timestamp': self.timestamp,
            'user_id': '$ANONYMIZED_USER_ID',
        }
        init = learnosity_sdk.request.Init(
            'assess', security, self.secret,
            request={'questionsApiActivity': {
                'domain': 'custom.learnosity.com',
                'consumer_key': 'STALE',
                'signature': 'STALE_SIG',
                'extra': 'keep-me',
            }})

        request = as_dict(init.request)
        activity = request['questionsApiActivity']
        # Stale identity keys are replaced with freshly generated values.
        self.assertEqual(activity['consumer_key'], self.key)
        self.assertTrue(activity['signature'].startswith('$02$'))
        self.assertNotEqual(activity['signature'], 'STALE_SIG')
        # Non-identity keys supplied by the caller survive.
        self.assertEqual(activity['extra'], 'keep-me')

    def test_assess_activity_falls_back_to_default_domain(self) -> None:
        """
        When neither the security packet nor the activity supplies a domain,
        the activity is still signed using the default assess domain.
        """
        security = {
            'consumer_key': self.key,
            'timestamp': self.timestamp,
            'user_id': '$ANONYMIZED_USER_ID',
        }
        init = learnosity_sdk.request.Init(
            'assess', security, self.secret,
            request={'questionsApiActivity': {'extra': 'keep-me'}})

        request = as_dict(init.request)
        activity = request['questionsApiActivity']
        self.assertTrue(activity['signature'].startswith('$02$'))
        self.assertEqual(activity['extra'], 'keep-me')

    def test_items_user_id_copied_from_request(self) -> None:
        """
        For 'items'/'reports', when security lacks ``user_id`` but the request
        provides one, it must be copied into the security packet.
        """
        for service in ('items', 'reports'):
            with self.subTest(service=service):
                init = learnosity_sdk.request.Init(
                    service, self._security(), self.secret,
                    request={'user_id': 'req-user', 'items': ['item_1']})
                self.assertEqual(init.security['user_id'], 'req-user')

    def test_items_user_id_in_security_not_overwritten(self) -> None:
        """An existing security ``user_id`` must take precedence over the request."""
        init = learnosity_sdk.request.Init(
            'items', self._security({'user_id': 'sec-user'}), self.secret,
            request={'user_id': 'req-user', 'items': ['item_1']})
        self.assertEqual(init.security['user_id'], 'sec-user')


class TestTelemetryMetaHandling(unittest.TestCase):
    """
    Tests for the ``meta`` guards in ``Init.add_telemetry_data()``.

    The SDK meta block must attach safely whether or not the request already
    contains a ``meta`` key and regardless of that key's type. A non-dict
    ``meta`` previously raised ``TypeError: 'str' object does not support item
    assignment``.
    """

    key = 'yis0TYCu7U9V4o7M'
    secret = '74c5fd430cf1242a527f6223aebd42d30464be22'

    def setUp(self) -> None:
        learnosity_sdk.request.Init.enable_telemetry()
        self.addCleanup(learnosity_sdk.request.Init.enable_telemetry)

    def _security(self) -> Dict[str, str]:
        return {
            'consumer_key': self.key,
            'domain': 'localhost',
            'timestamp': '20140626-0528',
        }

    def test_sdk_meta_added_when_no_meta_present(self) -> None:
        """When telemetry is enabled and no ``meta`` exists, one is created."""
        init = learnosity_sdk.request.Init(
            'items', self._security(), self.secret, request={'items': ['item_1']})
        request = as_dict(init.request)
        self.assertIn('sdk', request['meta'])

    def test_existing_meta_dict_is_preserved(self) -> None:
        """An existing ``meta`` dict must keep its keys and gain the sdk block."""
        init = learnosity_sdk.request.Init(
            'items', self._security(), self.secret,
            request={'items': ['item_1'], 'meta': {'existing': 'value'}})
        request = as_dict(init.request)
        self.assertEqual(request['meta']['existing'], 'value')
        self.assertIn('sdk', request['meta'])

    def test_non_dict_meta_is_replaced(self) -> None:
        """
        A non-dict ``meta`` must be replaced with a dict holding the sdk block.
        Regression for ``TypeError: 'str' object does not support item
        assignment``.
        """
        init = learnosity_sdk.request.Init(
            'items', self._security(), self.secret,
            request={'items': ['item_1'], 'meta': 'not-a-dict'})
        request = as_dict(init.request)
        self.assertIsInstance(request['meta'], dict)
        self.assertIn('sdk', request['meta'])
