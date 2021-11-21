# Copyright (c) 2021 Learnosity, Apache 2.0 License
# SPDX-License-Identifier: Apache-2.0
#
# Basic example of embedding a standalone assessment using Items API
# with `rendering_type: "assess"`.

# Include server side Learnosity SDK, and set up variables related to user access
from learnosity_sdk.request import Init
from learnosity_sdk.utils import Uuid
from .. import config # Load consumer key and secret from config.py
# Include web server, time, and Jinja templating libraries.
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from jinja2 import Template

# - - - - - - Section 1: Learnosity server-side configuration - - - - - - #

# Generate the user ID and session ID as UUIDs.
user_id = Uuid.generate()
session_id = Uuid.generate()

# Set variables for the web server.
host = "localhost"
port = 8000

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

# Public & private security keys required to access Learnosity APIs and
# data. These keys grant access to Learnosity's public demos account.
# Learnosity will provide keys for your own account.
security = {
    'consumer_key': config.consumer_key,
    # Change to the domain used in the browser, e.g. 127.0.0.1, learnosity.com
    'domain': host,
} 

# Set up Learnosity initialization data.
init = Init(
    'items', security, config.consumer_secret,
    request=items_request
)
generated_request = init.generate()

# - - - - - - Section 2: your web page configuration - - - - - -#

# Set up the HTML page template, for serving to the built-in Python web server
class LearnosityServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Define the page HTML, as a Jinja template, with {{variables}} passed in.
        template = Template("""<!DOCTYPE html>
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="../css/style.css">
            </head>
            <body>
                <h1>{{ name }}</title></h1>
                <!-- Items API will render the assessment app into this div. -->
                <div id="learnosity_assess"></div>
                <!-- Load the Items API library. -->
                <script src=\"https://items.learnosity.com/?v2021.2.LTS/\"></script>
                <!-- Initiate Items API assessment rendering, using the signed parameters. -->
                <script>
                    var itemsApp = LearnosityItems.init( {{ generated_request }} );
                </script>
            </body>
        </html>
        """)

        # Render the page template and grab the variables needed.
        response = template.render(name='Standalone Assessment Example', generated_request=generated_request)
        # Send headers and data back to the client.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # Send the response to the client.
        self.wfile.write(response.encode("utf-8"))

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