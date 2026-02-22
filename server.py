import os
import json
import http.server
import socketserver
from http import HTTPStatus
from dotenv import load_dotenv
from app.api.feed_student_data import feed
from app.api.webhook import verify_webhook, handle_webhook
from app.modules.container import Container

load_dotenv()

container = Container()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"GET {self.path}")
        if self.path.startswith("/webhook"):
            params = dict(p.split("=") for p in self.path.split("?")[1].split("&")) if "?" in self.path else {}
            response, status = verify_webhook(params)
            self.send_response(status)
            self.end_headers()
            self.wfile.write(response.encode())
        elif self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "static/index.html"), "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            self.wfile.write(b"School App is running")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        print(f"POST {self.path} - body: {body[:500]}")

        try:
            args = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        if self.path.startswith('/feed'):
            result = feed(args.get("ocr_text", ""), container.ai_client(), container.student_repository())
            self.send_response(result.get("statusCode", 200))
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result.get("body")).encode())
        elif self.path.startswith('/webhook'):
            # Respond 200 immediately as Meta requires fast response
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            handle_webhook(args)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()


port = int(os.getenv('PORT', 8080))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)
httpd.serve_forever()
