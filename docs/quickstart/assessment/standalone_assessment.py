# Copyright (c) 2023 Learnosity, Apache 2.0 License
# SPDX-License-Identifier: Apache-2.0
#
# Basic example of embedding a standalone assessment using Items API
# with `rendering_type: "assess"`.

# Include server side Learnosity SDK, and set up variables related to user access
from learnosity_sdk.request import Init, DataApi
from learnosity_sdk.utils import Uuid
from .. import config # Load consumer key and secret from config.py
# Include web server and Jinja templating libraries.
from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template
import json
import os

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
    "consumer_key": config.consumer_key,
    # Change to the domain used in the browser, e.g. 127.0.0.1, learnosity.com
    "domain": host,
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
    "items", security, config.consumer_secret,
    request = items_request
)

initQuestions = Init(
    "questions", security, config.consumer_secret,
    request = questions_request
)

initAuthor = Init(
    "author", security, config.consumer_secret,
    request = author_request
)

initReports = Init(
    "reports", security, config.consumer_secret,
    request = report_request
)

initQuestionEditor = Init(
    "questions", security, config.consumer_secret,
    request = question_editor_request
)

# Generated request(initOptions) w.r.t all apis
generated_request_Items = initItems.generate()
generated_request_Questions = initQuestions.generate()
generated_request_Author = initAuthor.generate()
generated_request_Reports = initReports.generate()
generated_request_QuestionEditor = initQuestionEditor.generate()

# - - - - - - Section 2: your web page configuration - - - - - -#

# Set up the HTML page template, for serving to the built-in Python web server
class LearnosityServer(BaseHTTPRequestHandler):

    def createResponse(self, response: str) -> None:
         # Send headers and data back to the client.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # Send the response to the client.
            self.wfile.write(response.encode("utf-8"))

    def do_GET(self) -> None:

        # Serve CSS file
        if self.path == "/css/style.css":
            try:
                # Get the directory where this script is located
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Navigate to the CSS file location
                css_path = os.path.join(script_dir, "..", "css", "style.css")

                with open(css_path, 'r') as f:
                    css_content = f.read()

                self.send_response(200)
                self.send_header("Content-type", "text/css")
                self.end_headers()
                self.wfile.write(css_content.encode("utf-8"))
                return
            except FileNotFoundError:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"CSS file not found")
                return

        if self.path.endswith("/"):

        # Define the page HTML, as a Jinja template, with {{variables}} passed in.
            template = Template("""<!DOCTYPE html>
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="/css/style.css">
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
                            <th>APIs</th>
                            <th>Links</th>
                        </tr>
                        <tr>
                            <td>Author API</td>
                            <td><a href="/authorapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Questions API</td>
                            <td><a href="/questionsapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Items API</td>
                            <td><a href="/itemsapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Reports API</td>
                            <td><a href="/reportsapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Question Editor API</td>
                            <td><a href="/questioneditorapi">Here</a></td>
                        </tr>
                        <tr>
                            <td>Data API</td>
                            <td><a href="/dataapi">Here</a></td>
                        </tr>
                    </table>
                </body>
            </html>
            """)

            # Render the page template and grab the variables needed.
            response = template.render(name='Standalone API Examples')
            self.createResponse(response)

        if self.path.endswith("/itemsapi"):
        # Define the page HTML, as a Jinja template, with {{variables}} passed in.
            template = Template("""<!DOCTYPE html>
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="/css/style.css">
                </head>
                <body>
                    <h1>{{ name }}</title></h1>
                    <!-- Items API will render the assessment app into this div. -->
                    <div id="learnosity_assess"></div>
                    <!-- Load the Items API library. -->
                    <script src=\"https://items.learnosity.com/?latest-lts\"></script>
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

        if self.path.endswith("/questionsapi"):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <head>
                                        <link rel="stylesheet" type="text/css" href="/css/style.css">
                                    </head>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Questions API  will render here -->
                                        <span class="learnosity-response question-60005"></span>
                                        <!-- Load the Questions API library. -->
                                        <script src=\"https://questions.learnosity.com/?latest-lts\"></script>
                                        <!-- Initiate Questions API  -->
                                        <script>
                                            var questionsApp = LearnosityApp.init( {{ generated_request }} );
                                        </script>
                                    </body>
                                </html>
                                """)

             response = template.render(name='Standalone Questions API Example', generated_request=generated_request_Questions)
             self.createResponse(response)

        if self.path.endswith("/authorapi"):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <head>
                                        <link rel="stylesheet" type="text/css" href="/css/style.css">
                                    </head>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Author API will render here into the div -->
                                        <div id="learnosity-author"></div>
                                        <!-- Load the Author API library. -->
                                        <script src=\"https://authorapi.learnosity.com?latest-lts\"></script>
                                        <!-- Initiate Author API -->
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

        if self.path.endswith("/reportsapi"):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <head>
                                        <link rel="stylesheet" type="text/css" href="/css/style.css">
                                    </head>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Reports API will render into this span -->
                                        <span class="learnosity-report" id="session-detail"></span>
                                        <!-- Load the Reports API library. -->
                                        <script src=\"https://reports.learnosity.com?latest-lts\"></script>
                                        <!-- Initiate Reports API -->
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

        if self.path.endswith("/questioneditorapi"):
            # Define the page HTML, as a Jinja template, with {{variables}} passed in.
             template = Template("""<!DOCTYPE html>
                                <html>
                                    <head>
                                        <link rel="stylesheet" type="text/css" href="/css/style.css">
                                    </head>
                                    <body>
                                        <h1>{{ name }}</title></h1>
                                        <!-- Question Editor API will render into this div. -->
                                        <div class="learnosity-question-editor"></div>
                                        <!-- Load the Question Editor API library. -->
                                        <script src=\"https://questioneditor.learnosity.com/?latest-lts\"></script>
                                        <!-- Initiate Question Editor API -->
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

        if self.path.endswith("/dataapi"):
            # Data API demo - retrieve items from the itembank
            template = Template("""<!DOCTYPE html>
            <html>
                <head>
                    <link rel="stylesheet" type="text/css" href="/css/style.css">
                </head>
                <body>
                    <h1>{{ name }}</h1>
                    <p>This demo shows how to use the Data API to retrieve items from the Learnosity itembank.</p>

                    <div class="demo-section">
                        <h2>Demo 1: Manual Iteration (5 items)</h2>
                        <p>Using <code>request()</code> method with manual pagination via the 'next' pointer.</p>
                        {{ demo1_output }}
                    </div>

                    <div class="demo-section">
                        <h2>Demo 2: Page Iteration (5 pages)</h2>
                        <p>Using <code>request_iter()</code> method to automatically iterate over pages.</p>
                        {{ demo2_output }}
                    </div>

                    <div class="demo-section">
                        <h2>Demo 3: Results Iteration (5 items)</h2>
                        <p>Using <code>results_iter()</code> method to automatically iterate over individual items.</p>
                        {{ demo3_output }}
                    </div>

                    <p><a href="/">Back to API Examples</a></p>
                </body>
            </html>
            """)

            # Run the Data API demos
            itembank_uri = 'https://data.learnosity.com/latest-lts/itembank/items'
            security_packet = {
                'consumer_key': config.consumer_key,
                'domain': host,
            }
            data_api = DataApi()

            # Demo 1: Manual iteration
            demo1_html = ""
            try:
                data_request = {'limit': 1}
                for i in range(5):
                    result = data_api.request(itembank_uri, security_packet,
                                             config.consumer_secret, data_request, 'get')
                    response = result.json()

                    if response.get('data'):
                        item = response['data'][0]
                        demo1_html += f"""
                        <div class="item">
                            <div class="item-reference">Item {i+1}: {item.get('reference', 'N/A')}</div>
                            <div class="item-status">Status: {item.get('status', 'N/A')}</div>
                        </div>
                        """

                    if response.get('meta', {}).get('next'):
                        data_request['next'] = response['meta']['next']
                    else:
                        break
            except Exception as e:
                demo1_html = f'<div class="error">Error: {str(e)}</div>'

            # Demo 2: Page iteration
            demo2_html = ""
            try:
                data_request = {'limit': 1}
                page_count = 0
                for page in data_api.request_iter(itembank_uri, security_packet,
                                                  config.consumer_secret, data_request, 'get'):
                    page_count += 1
                    demo2_html += f"""
                    <div class="meta-info">
                        Page {page_count}: {len(page.get('data', []))} items
                    </div>
                    """
                    if page.get('data'):
                        for item in page['data']:
                            demo2_html += f"""
                            <div class="item">
                                <div class="item-reference">{item.get('reference', 'N/A')}</div>
                                <div class="item-status">Status: {item.get('status', 'N/A')}</div>
                            </div>
                            """
                    if page_count >= 5:
                        break
            except Exception as e:
                demo2_html = f'<div class="error">Error: {str(e)}</div>'

            # Demo 3: Results iteration
            demo3_html = ""
            try:
                data_request = {'limit': 1}
                result_count = 0
                for item in data_api.results_iter(itembank_uri, security_packet,
                                                  config.consumer_secret, data_request, 'get'):
                    result_count += 1
                    demo3_html += f"""
                    <div class="item">
                        <div class="item-reference">Item {result_count}: {item.get('reference', 'N/A')}</div>
                        <div class="item-status">Status: {item.get('status', 'N/A')}</div>
                        <pre>{json.dumps(item, indent=2)[:500]}...</pre>
                    </div>
                    """
                    if result_count >= 5:
                        break
            except Exception as e:
                demo3_html = f'<div class="error">Error: {str(e)}</div>'

            response = template.render(
                name='Data API Example',
                demo1_output=demo1_html,
                demo2_output=demo2_html,
                demo3_output=demo3_html
            )
            self.createResponse(response)

def main() -> None:
    web_server = HTTPServer((host, port), LearnosityServer)
    print("Server started http://%s:%s. Press Ctrl-c to quit." % (host, port))
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()

# Run the web server.
if __name__ == "__main__":
    main()
