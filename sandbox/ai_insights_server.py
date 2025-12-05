from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from jinja2 import Template

from learnosity_sdk.request import Init
from docs.quickstart import config


host = "localhost"
port = 8001

security = {
    "consumer_key": config.consumer_key,
    "domain": host,
}

def build_report_request(user_id: str, session_id: str):
    return {
        "reports": [
        {
            "id": "session-detail",
            "type": "session-detail-by-item",
            "user_id": user_id,
            "session_id": session_id,
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

initItems = Init("items", security, config.consumer_secret, request=items_request)
# Build reports init per request using query parameters
generated_request_Items = initItems.generate()


class Server(BaseHTTPRequestHandler):
    def _ok(self, body: str):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api-report":
            qs = parse_qs(parsed.query)
            user_id = (qs.get("user_id") or ["demo-user"]).pop(0)
            session_id = (qs.get("session_id") or ["demo-session"]).pop(0)

            initReports = Init(
                "reports",
                security,
                config.consumer_secret,
                request=build_report_request(user_id, session_id),
            )
            generated_request_Reports = initReports.generate()
            with open('sandbox/views/report.html', 'r', encoding='utf-8') as f:
                tpl = Template(f.read())
            self._ok(tpl.render(generated_request=generated_request_Reports))
            return
        
        if parsed.path == "/report-feedback":
            qs = parse_qs(parsed.query)
            user_id = (qs.get("user_id") or ["demo-user"]).pop(0)
            session_id = (qs.get("session_id") or ["demo-session"]).pop(0)

            initReports = Init(
                "reports",
                security,
                config.consumer_secret,
                request=build_report_request(user_id, session_id),
            )
            generated_request_Reports = initReports.generate()

            with open('sandbox/views/report_feedback.html', 'r', encoding='utf-8') as f:
                tpl = Template(f.read())
            self._ok(tpl.render(generated_request=generated_request_Reports))
            return

        if parsed.path == "/items":
            with open('sandbox/views/items.html', 'r', encoding='utf-8') as f:
                tpl = Template(f.read())
            self._ok(tpl.render(generated_request=generated_request_Items))
            return

        # Index with simple form submitting to /reports
        with open('sandbox/views/index.html', 'r', encoding='utf-8') as f:
            tpl = Template(f.read())
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
