import collections
import unittest

import learnosity_sdk.request

ServiceTestSpec = collections.namedtuple(
    "TestSpec", ["service", "valid", "security", "request", "action", "signature"])

ServiceTests = [
    ServiceTestSpec(
        "questions", True, {"user_id": "$ANONYMIZED_USER_ID"}, {
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
        }, None,
        '03f4869659eeaca81077785135d5157874f4800e57752bf507891bf39c4d4a90',
    ),

    ServiceTestSpec(
        "data", True, None, {"limit": 100}, "get",
        'e1eae0b86148df69173cb3b824275ea73c9c93967f7d17d6957fcdd299c8a4fe',
    ),

#     ServiceTestSpec(
#         "assess", True, {"user_id": "$ANONYMIZED_USER_ID"}, {"foo": "bar"}, None,
            # '03f4869659eeaca81077785135d5157874f4800e57752bf507891bf39c4d4a90',
#     ),
#         $request = [
#             "items" => [
#                 [
#                     "content" => '<span class="learnosity-response question-demoscience1234"></span>',
#                     "response_ids" => [
#                         "demoscience1234"
#                     ],
#                     "workflow" => "",
#                     "reference" => "question-demoscience1"
#                 ],
#                 [
#                     "content" => '<span class="learnosity-response question-demoscience5678"></span>',
#                     "response_ids" => [
#                         "demoscience5678"
#                     ],
#                     "workflow" => "",
#                     "reference" => "question-demoscience2"
#                 ]
#             ],
#             "ui_style" =>"horizontal",
#             "name" => "Demo (2 questions)",
#             "state" => "initial",
#             "metadata" => [],
#             "navigation" => [
#                 "show_next" => true,
#                 "toc" => true,
#                 "show_submit" => true,
#                 "show_save" => false,
#                 "show_prev" => true,
#                 "show_title" => true,
#                 "show_intro" => true,
#             ],
#             "time" => [
#                 "max_time" => 600,
#                 "limit_type" => "soft",
#                 "show_pause" => true,
#                 "warning_time" => 60,
#                 "show_time" => true
#             ],
#             "configuration" => [
#                 "onsubmit_redirect_url" => "/assessment/",
#                 "onsave_redirect_url" => "/assessment/",
#                 "idle_timeout" => true,
#                 "questionsApiVersion" => "v2"
#             ],
#             "questionsApiActivity" => [
#                 "user_id" => "$ANONYMIZED_USER_ID",
#                 "type" => "submit_practice",
#                 "state" => "initial",
#                 "id" => "assessdemo",
#                 "name" => "Assess API - Demo",
#                 "questions" => [
#                     [
#                         "response_id" => "demoscience1234",
#                         "type" => "sortlist",
#                         "description" => "In this question, the student needs to sort the events, chronologically earliest to latest.",
#                         "list" => ["Russian Revolution", "Discovery of the Americas", "Storming of the Bastille", "Battle of Plataea", "Founding of Rome", "First Crusade"],
#                         "instant_feedback" => true,
#                         "feedback_attempts" => 2,
#                         "validation" => [
#                             "valid_response" => [4, 3, 5, 1, 2, 0],
#                             "valid_score" => 1,
#                             "partial_scoring" => true,
#                             "penalty_score" => -1
#                         ]
#                     ],
#                     [
#                         "response_id" => "demoscience5678",
#                         "type" => "highlight",
#                         "description" => "The student needs to mark one of the flowers anthers in the image.",
#                         "img_src" => "http://www.learnosity.com/static/img/flower.jpg",
#                         "line_color" => "rgb(255, 20, 0)",
#                         "line_width" => "4"
#                     ]
#                 ]
#             ],
#             "type" => "activity"
#         ];

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
        learnosity_sdk.request.Init.disable_telemetry()
        for t in ServiceTests:
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

            self.assertFalse(init.is_telemetry_enabled())
            self.assertEqual(t.signature, init.generate_signature())
            self.assertTrue(init.generate() is not None)
