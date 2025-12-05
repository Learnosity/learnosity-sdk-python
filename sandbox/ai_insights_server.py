# Minimal server exposing two pages: Reports and Items
# Copyright (c) 2025 Learnosity, Apache 2.0 License
# SPDX-License-Identifier: Apache-2.0

from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template

from learnosity_sdk.request import Init
from docs.quickstart import config


host = "localhost"
port = 8001

security = {
    "consumer_key": config.consumer_key,
    "domain": host,
}

# Simple example reports request (adjust with real session/user as needed)
report_request = {
    "reports": [
        {
            "id": "session-detail",
            "type": "session-detail-by-item",
            "user_id": "2985e2d7-426d-4576-8015-56de188923e8",
            "session_id": "41cc9e84-6176-48a6-ac14-38f4c34705af"
        }
    ]
}

# Simple example items request
items_request = {
    "user_id": "demo-user",
    "activity_id": "quickstart_examples_activity_001",
    "activity_template_id": "quickstart_examples_activity_template_001",
    "session_id": "demo-session",
    "rendering_type": "assess",
    "type": "submit_practice",
    "name": "Items API Quickstart",
    "state": "initial",
}

initReports = Init("reports", security, config.consumer_secret, request=report_request)
initItems = Init("items", security, config.consumer_secret, request=items_request)

generated_request_Reports = initReports.generate()
generated_request_Items = initItems.generate()


class Server(BaseHTTPRequestHandler):
    def _ok(self, body: str):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        if self.path == "/reports":
            tpl = Template(
                """<!DOCTYPE html>
                <html>
                  <body>
                    <h1>Reports Page</h1>
                    <div id="reports-container">
                      <span class="learnosity-report" id="session-detail"></span>
                    </div>
                    <div id="secondary-container"></div>
                    <script src="https://reports.learnosity.com?latest-lts"></script>
                    <script>
                      var reportsApp = LearnosityReports.init({{ generated_request }});
                    </script>
                  </body>
                </html>
                """
            )
            self._ok(tpl.render(generated_request=generated_request_Reports))
            return

        if self.path == "/items":
            tpl = Template(
                """<!DOCTYPE html>
                <html>
                  <body>
                    <h1>Items Page</h1>
                    <div id="learnosity_assess"></div>
                    <script src="https://items.learnosity.com/?latest-lts"></script>
                    <script>
                      var itemsApp = LearnosityItems.init({{ generated_request }});
                    </script>
                  </body>
                </html>
                """
            )
            self._ok(tpl.render(generated_request=generated_request_Items))
            return

        # Index
        tpl = Template(
            """<!DOCTYPE html>
            <html>
              <body>
                <h1>Demo Server</h1>
                <ul>
                  <li><a href="/reports">Reports Page</a></li>
                  <li><a href="/items">Items Page</a></li>
                </ul>
              </body>
            </html>
            """
        )
        self._ok(tpl.render())


def main():
    server = HTTPServer((host, port), Server)
    print(f"Server started http://{host}:{port}. Press Ctrl-C to quit.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
