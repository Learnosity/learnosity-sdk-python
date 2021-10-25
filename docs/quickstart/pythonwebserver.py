#!/usr/bin/env python                                       # from LRN SDK example
from learnosity_sdk.request import Init                     # from LRN SDK example
from learnosity_sdk.utils import Uuid                       # from LRN SDK example

from http.server import BaseHTTPRequestHandler, HTTPServer  # web server code
import time                                                 # web server code

# Security packet including consumer key                    # from LRN SDK example
security = {                                                # from LRN SDK example
  'consumer_key': 'yis0TYCu7U9V4o7M',                       # from LRN SDK example
  # Change to your domain, e.g. 127.0.0.1, learnosity.com   # from LRN SDK example
  'domain': 'localhost',                                    # from LRN SDK example
}
# consumer secret for API access                            # from LRN SDK example
# WARNING: The consumer secret should not be committed to source control. # from LRN SDK example
secret = '74c5fd430cf1242a527f6223aebd42d30464be22'         # from LRN SDK example

# example request data for Items API                        # from LRN SDK example
items_request = items_request = {                           # from LRN SDK example
    "rendering_type": "inline",                             # from LRN SDK example
    "user_id": "$ANONYMIZED_USER_ID",                       # from LRN SDK example
    "session_id": Uuid.generate(),                          # from LRN SDK example
    "type": "submit_practice",                              # from LRN SDK example
    "activity_id": "exampleActivity",                       # from LRN SDK example
    "name": "Items API demo - inline activity.",            # from LRN SDK example
    "items": [                                              # from LRN SDK example
        "classification_1",                                 # from LRN SDK example
        "multiple_choice_1"                                 # from LRN SDK example
    ]                                                       # from LRN SDK example
}                                                           # from LRN SDK example

init = Init(                                                # from LRN SDK example
    'items', security, secret,                              # from LRN SDK example
    request=items_request                                   # from LRN SDK example
)                                                           # from LRN SDK example

# Get the JSON that can be rendered into the page and passed to LearnosityItems.init
generatedRequest = init.generate()                    # Edwin code

# ============= WEB SERVER CODE BEGINS ============== #
hostName = "localhost"                                # web server code
serverPort = 8000                                     # web server code

class MyServer(BaseHTTPRequestHandler):               # web server code
    def do_GET(self):                                 # web server code
        self.send_response(200)                       # web server code
        self.send_header("Content-type", "text/html") # web server code
        self.end_headers()                            # web server code
        self.wfile.write(bytes("<html><head><title>Learnosity Python SDK Quick Start Guide</title></head>", "utf-8")) #Edwincode
        self.wfile.write(bytes("<body><h1>Learnosity Python SDK Quick Start Guide</title></h1>", "utf-8")) # Edwin code
        self.wfile.write(bytes("<script src=\"https://items.learnosity.com/?v1/\"></script>", "utf-8")) # from LRN SDK example
        self.wfile.write(bytes("<span class=\"learnosity-item\" data-reference=\"multiple_choice_1\"></span>", "utf-8")) #LRN
        self.wfile.write(bytes("<span class=\"learnosity-item\" data-reference=\"classification_1\"></span>", "utf-8"))  #LRN
        self.wfile.write(bytes("<script>", "utf-8")) # Edwin code
        # `generatedRequest` below is the string from the Init.generate() method # LRN
        self.wfile.write(bytes("var itemsApp = LearnosityItems.init( %s );" % generatedRequest, "utf-8")) # Edwin
        self.wfile.write(bytes("</script></body></html>", "utf-8")) # Edwin code

if __name__ == "__main__":                                        # web server code
    webServer = HTTPServer((hostName, serverPort), MyServer)      # web server code
    print("Server started http://%s:%s" % (hostName, serverPort)) # web server code

    try:                                                          # web server code
        webServer.serve_forever()                                 # web server code
    except KeyboardInterrupt:                                     # web server code
        pass                                                      # web server code

    webServer.server_close()                                      # web server code
    print("Server stopped.")                                      # web server code
