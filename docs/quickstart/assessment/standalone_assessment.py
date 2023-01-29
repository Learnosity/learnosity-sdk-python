# Copyright (c) 2021 Learnosity, Apache 2.0 License
# SPDX-License-Identifier: Apache-2.0
#
# Basic example of embedding a standalone assessment using Items API
# with `rendering_type: "assess"`.

# Include server side Learnosity SDK, and set up variables related to user access
from learnosity_sdk.request import Init
from learnosity_sdk.utils import Uuid
from .. import config # Load consumer key and secret from config.py
# Include web server and Jinja templating libraries.
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template

# - - - - - - Section 1: Learnosity server-side configuration - - - - - - #

# Generate the user ID and session ID as UUIDs.
user_id = Uuid.generate()
session_id = Uuid.generate()

# Set variables for the web server.
host = "localhost"
port = 8000

# Public & private security keys required to access Learnosity APIs and
# data. These keys grant access to Learnosity's public demos account.
# Learnosity will provide keys for your own account.
security = {
    "user_id" : "abc",
    'consumer_key': config.consumer_key,
    # Change to the domain used in the browser, e.g. 127.0.0.1, learnosity.com
    'domain': host,
} 

# Items API configuration parameters.
items_request = {
       # Unique student identifier, a UUID generated above.
    "user_id": user_id,
    # A reference of the Activity to retrieve from the Item bank, defining
    # which Items will be served in this assessment.
    "activity_template_id": "quickstart_examples_activity_template_001",
    # Uniquely identifies this specific assessment attempt session for 
    # save/resume, data retrieval and reporting purposes. A UUID generated above.
    "session_id": session_id,
    # Used in data retrieval and reporting to compare results
    # with other users submitting the same assessment.
    "activity_id": "quickstart_examples_activity_001",
    # Selects a rendering mode, `assess` type is a "standalone" mode (loading a
    # complete assessment player for navigation, VS `inline`, for embedded).
    "rendering_type": "assess",
    # Selects the context for the student response storage. `submit_practice` 
    # mode means student response storage in the Learnosity cloud, for grading.
    "type": "submit_practice",
    # Human-friendly display name to be shown in reporting.
    "name": "Items API Quickstart",
    # Can be set to `initial, `resume` or `review`. Optional. Default = `initial`.
    "state": "initial"
}

# Questions API configuration parameters.
questions_request = {
    "id": "f0001",
    "name": "Intro Activity - French 101",
    "questions": [
         {
             "response_id": "60005",
             "type": "association",
             "stimulus": "Match the cities to the parent nation.",
             "stimulus_list": ["London", "Dublin", "Paris", "Sydney"],
             "possible_responses": ["Australia", "France", "Ireland", "England"
             ],
             "validation": {
                "valid_responses": [
                    ["England"],["Ireland"],["France"],["Australia"]
                ]
            },
            "instant_feedback": True
        }
    ],
}

# Author API configuration parameters.
# mode can be changed by item_list and item_edit
author_request = {
        "mode": "item_edit",
        "reference": "a15ac409-f6d5-42de-a491-a1e4ab03c826",
        "user": {
            "id" : "brianmoser",
            "firstname" : "Test",
            "lastname" : "Test",
            "email" : "test@test.com"
        },
        "config": {
            "global": {
                "disable_onbeforeunload": True,
                "hide_tags":
                [
                  {
                    "type": "internal_category_uuid"
                  }
                ]
            },
            "item_edit": {
                "item": {
                    "back": True,
                    "columns": True,
                    "answers": True,
                    "scoring": True,
                    "reference": {
                        "edit": False,
                        "show": False,
                        "prefix": "LEAR_" 
                    },
                    "save": True,
                    "status": False,
                    "dynamic_content": True,
                    "shared_passage": True
                },
                "widget": {
                    "delete": False,
                    "edit": True
                }
            },
            "item_list": {
                "item": {
                    "status": True,
                    "url": "http://myApp.com/items/:reference/edit"
                },
                "toolbar": {
                    "add": True,
                    "browse": {
                      "controls": [
                        {
                          "type": "hierarchy",
                          "hierarchies": [
                            {
                              "reference": "CCSS_Math_Hierarchy",
                              "label": "CCSS Math"
                            },
                            {
                              "reference": "CCSS_ELA_Hierarchy",
                              "label": "CCSS ELA"
                            },
                            {
                              "reference": "Demo_Items_Hierarchy",
                              "label": "Demo Items"
                            }
                          ]
                        },
                        {
                          "type": "tag",
                          "tag": {
                             "type": "Alignment",
                             "label": "def456"
                          }
                        },
                        {
                          "type": "tag",
                          "tag": {
                             "type": "Course",
                             "label": "commoncore"
                          }
                        }
                      ]
                    }
                },
                "filter": {
                    "restricted": {
                        "current_user": True,
                        "tags": {
                            "all": [
                                {
                                    "type": "Alignment",
                                    "name": ["def456", "abc123"]
                                },
                                {
                                    "type": "Course"
                                }
                            ],
                            "either": [
                                {
                                    "type": "Grade",
                                    "name": "4"
                                },
                                {
                                    "type": "Grade",
                                    "name": "5"
                                },
                                {
                                    "type": "Subject",
                                    "name": ["Math", "Science"]
                                }
                            ],
                            "none": [
                                {
                                    "type": "Grade",
                                    "name": "6"
                                }
                            ]
                        }
                    }
                }
            },
            "dependencies": {
                "question_editor_api": {
                    "init_options": {}
                },
                "questions_api": {
                    "init_options": {}
                }
            },
            "widget_templates": {
                "back": True,
                "save": True,
                "widget_types": {
                    "default": "questions",
                    "show": True
                }
            },
            "container": {
                "height": "auto",
                "fixed_footer_height": 0,
                "scroll_into_view_selector": "body"
            },
            "label_bundle": { 
                
                "backButton": "Zurück",
                "loadingText": "Wird geladen",
                "modalClose": "Schließen",
                "saveButton": "Speichern",
                "duplicateButton": "Duplikat",

                
                "dateTimeLocale": "en-us",
                "toolTipDateTimeSeparator": "um",
                "toolTipDateFormat": "DD-MM-YYYY",
                "toolTipTimeFormat": "HH:MM:SS",
            }
        },
    }

# Assess API configuration parameters.
assess_request = {
	"items": [
	{
		"content": "<span class=\"learnosity-response question-demoscience1234\"></span>",
		"response_ids": ["demoscience1234"],
		"workflow": "",
		"reference": "question-demoscience1"
	},
	{
		"content": "<span class=\"learnosity-response question-demoscience5678\"></span>",
		"response_ids": ["demoscience5678"],
		"workflow": "",
		"reference": "question-demoscience2"
	}],
	"ui_style": "horizontal",
	"name": "Demo (2 questions)",
	"state": "initial",
	"metadata": [],
	"navigation":
	{
		"show_next": True,
		"toc": True,
		"show_submit": True,
		"show_save": False,
		"show_prev": True,
		"show_title": True,
		"show_intro": True
	},
	"time":
	{
		"max_time": 600,
		"limit_type": "soft",
		"show_pause": True,
		"warning_time": 60,
		"show_time": True
	},
	"configuration":
	{
		"onsubmit_redirect_url": "/assessment/",
		"onsave_redirect_url": "/assessment/",
		"idle_timeout": True,
		"questionsApiVersion": "v2"
	},
	"questionsApiActivity":
	{
		"user_id": "abc",
		"type": "submit_practice",
		"state": "initial",
		"id": "assessdemo",
		"name": "Assess API - Demo",
		"questions": [
		{
			"response_id": "demoscience1234",
			"type": "sortlist",
			"description": "In this question, the student needs to sort the events, chronologically earliest to latest.",
			"list": ["Russian Revolution", "Discovery of the Americas", "Storming of the Bastille", "Battle of Plataea", "Founding of Rome", "First Crusade"],
			"instant_feedback": True,
			"feedback_attempts": 2,
			"validation":
			{
				"valid_response": [4, 3, 5, 1, 2, 0],
				"valid_score": 1,
				"partial_scoring": True,
				"penalty_score": -1
			}
		},
		{
			"response_id": "demoscience5678",
			"type": "highlight",
			"description": "The student needs to mark one of the flowers anthers in the image.",
			"img_src": "http://www.learnosity.com/static/img/flower.jpg",
			"line_color": "rgb(255, 20, 0)",
			"line_width": "4"
		}]
	},
	"type": "activity"
}

# Reports API configuration parameters.
report_request = {
    "reports" : [{
        "id": "session-detail",
        "type": "session-detail-by-item",
        "user_id": "906d564c-39d4-44ba-8ddc-2d44066e2ba9",
        "session_id": "906d564c-39d4-44ba-8ddc-2d44066e2ba9"
    }]
}

# Question Editor API configuration parameters.
question_editor_request = {
    "configuration" : {
       "consumer_key": config.consumer_key,
    },
    "widget_conversion": True,
    "ui" : {
        "search_field" : True,
    },
    "layout":{
        "global_template": "edit_preview",
        "mode": "advanced"
    }
    }

# Set up Learnosity initialization data.
initItems = Init(
    'items', security, config.consumer_secret,
    request = items_request
)

initQuestions = Init(
    'questions', security, config.consumer_secret,
    request = questions_request
)

initAuthor = Init(
    'author',security,config.consumer_secret,
    request = author_request
)

initAssess = Init(
    'assess',security,config.consumer_secret,
    request = assess_request
)

initReports = Init(
    'reports',security,config.consumer_secret,
    request = report_request
)

initQuestionEditor = Init(
    'questions',security,config.consumer_secret,
    request = question_editor_request
)

# Generated request(initOptions) w.r.t all apis
generated_request_Items = initItems.generate()
generated_request_Questions = initQuestions.generate()
generated_request_Author = initAuthor.generate()
generated_request_Assess = initAssess.generate()
generated_request_Reports = initReports.generate()
generated_request_QuestionEditor = initQuestionEditor.generate()

# - - - - - - Section 2: your web page configuration - - - - - -#

# Set up the HTML page template, for serving to the built-in Python web server
class LearnosityServer(BaseHTTPRequestHandler):

    def createResponse(self,response):
         # Send headers and data back to the client.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Send the response to the client.
            self.wfile.write(response.encode("utf-8"))

    def do_GET(self):

        if self.path.endswith('/'):

        # Define the page HTML, as a Jinja template, with {{variables}} passed in.
            template = Template("""<!DOCTYPE html>
            <html>
                <head>
                    <style>
                      .tb { border-collapse: collapse; }
                      .tb th, .tb td { padding: 5px; border: solid 1px #777; text-align: center;}
                      .tb th { background-color: lightblue; }
                    </style>
                </head>
                <body>
                    <h1>{{ name }}</title></h1>
                    <table class="tb" style="width:300px;">
                        <tr>
                            <th>API's</th>
                            <th>Links</th>
                        </tr>
                        <tr>
                            <td>Author Api</td>
                            <td><a href="/authorapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Questions Api</td>
                            <td><a href="/questionsapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Items Api</td>
                            <td><a href="/itemsapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Reports Api</td>
                            <td><a href="/reportsapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Question Editor Api</td>
                            <td><a href="/questioneditorapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Assess Api</td>
                            <td><a href="/assessapi">Here</a></td>
                        </tr>
                    </table>
                </body>
            </html>
            """)

            # Render the page template and grab the variables needed.
            response = template.render(name='Standalone APIs Examples')
            self.createResponse(response)

        if self.path.endswith('/itemsapi'):
        # Define the page HTML, as a Jinja template, with {{variables}} passed in.
            template = Template("""<!DOCTYPE html>
            <html>
                <body>
                    <h1>{{ name }}</title></h1>
                    <!-- Items API will render the assessment app into this div. -->
                    <div id="learnosity_assess"></div>
                    <!-- Load the Items API library. -->
                    <script src=\"https://items.learnosity.com/?latest\"></script>
                    <!-- Initiate Items API  -->
                    <script>
                        var itemsApp = LearnosityItems.init( {{ generated_request }} );
                    </script>
                </body>
            </html>
            """)

            # Render the page template and grab the variables needed.
            response = template.render(name='Standalone Items API Example', generated_request=generated_request_Items)

            self.createResponse(response)

        if self.path.endswith('/questionsapi'):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Questions API  will render here -->
                                        <span class="learnosity-response question-60005"></span>
                                        <!-- Load the Questions API library. -->
                                        <script src=\"https://questions.learnosity.com/?latest\"></script>
                                        <!-- Initiate Questions API  -->
                                        <script>
                                            var questionsApp = LearnosityApp.init( {{ generated_request }} );
                                        </script>
                                    </body>
                                </html>
                                """)

             response = template.render(name='Standalone Questions API Example', generated_request=generated_request_Questions)
             self.createResponse(response)

        if self.path.endswith('/authorapi'):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Author API will render here into the div -->
                                        <div id="learnosity-author"></div>
                                        <!-- Load the Author API library. -->
                                        <script src=\"https://authorapi.learnosity.com?latest\"></script>
                                        <!-- Initiate Author Api -->
                                        <script>
                                        var callbacks = {
                                            readyListener: function () {
                                                console.log("Author API has successfully initialized.");
                                            },
                                            errorListener: function (err) {
                                                console.log(err);
                                            }
                                        }; 
                                            var authorApp = LearnosityAuthor.init( {{ generated_request }} );
                                        </script>
                                    </body>
                                </html>
                                """)

             response = template.render(name='Standalone Author API Example', generated_request=generated_request_Author)
             self.createResponse(response)

        if self.path.endswith('/assessapi'):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <head>
                                        <link rel="stylesheet" type="text/css" href="../css/style.css">
                                    </head>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Assess API will render here into the div -->
                                        <div id="learnosity_assess"></div>
                                        <!-- Load the Assess API library. -->
                                        <script src=\"https://assess.learnosity.com?latest\"></script>
                                        <!-- Initiate Assessment Api -->
                                        <script>
                                        const callbacks = {
                                            errorListener: function(e) {
                                                // Adds a listener to all error codes.
                                                console.log("Error Code ", e.code);
                                                console.log("Error Message ", e.msg);
                                                console.log("Error Detail ", e.detail);
                                            },

                                            readyListener: function() {
                                                console.log("Learnosity Questions API is ready");
                                            }
                                        }; 
                                            const assessApp = LearnosityAssess.init( {{ generated_request }},"learnosity_assess" ,callbacks);
                                        </script>
                                    </body>
                                </html>
                                """)

             response = template.render(name='Standalone Assess API Example', generated_request=generated_request_Assess)
             self.createResponse(response)

        if self.path.endswith('/reportsapi'):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Reports API will render into this span -->
                                        <span class="learnosity-report" id="session-detail"></span>
                                        <!-- Load the Reports Api library. -->
                                        <script src=\"https://reports.learnosity.com?latest\"></script>
                                        <!-- Initiate Reports Api -->
                                        <script>
                                        var callbacks = {
                                            readyListener: function () {
                                                console.log("Learnosity Reports has successfully initialized.");
                                            },
                                            errorListener: function (err) {
                                                console.log(err);
                                            }
                                        }; 
                                            reportsApp = LearnosityReports.init( {{ generated_request }} );
                                        </script>
                                    </body>
                                </html>
                                """)

             response = template.render(name='Standalone Reports API Example', generated_request=generated_request_Reports)
             self.createResponse(response)

        if self.path.endswith('/questioneditorapi'):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Question Editor API will render into this div. -->
                                        <div class="learnosity-question-editor"></div>
                                        <!-- Load the Question Editor Api library. -->
                                        <script src=\"https://questioneditor.learnosity.com/?latest\"></script>
                                        <!-- Initiate Question Editor Api -->
                                        <script>
                                        var callbacks = {
                                            readyListener: init,
                                            errorListener: errors
                                        };

                                        function init() {
                                            console.log('API has successfully initialized.');
                                        }

                                        function errors(err) {
                                            console.log(err);
                                        } 
                                            var questionEditorApp = LearnosityQuestionEditor.init( {{ generated_request }} );
                                        </script>
                                    </body>
                                </html>
                                """)

             response = template.render(name='Standalone Question Editor API Example', generated_request=generated_request_QuestionEditor)
             self.createResponse(response)

def main():
    web_server = HTTPServer((host, port), LearnosityServer)
    print("Server started http://%s:%s. Press Ctrl-c to quit." % (host, port))
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()

# Run the web server.
if __name__ == "__main__":
    main()