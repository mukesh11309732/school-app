import os
import json
import http.server
import socketserver
from http import HTTPStatus
from dotenv import load_dotenv
from app.extract_student_data import main
from app.feed_student_data import main as feed_main

load_dotenv()


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = 'Hello! you requested %s' % (self.path)
        self.wfile.write(msg.encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            args = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        if self.path == '/extract':
            result = main(args)
        elif self.path == '/feed':
            result = feed_main(args)
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        self.send_response(result.get("statusCode", 200))
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result.get("body")).encode())


port = int(os.getenv('PORT', 80))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)
httpd.serve_forever()
