#!/bin/bash

python -m backend.queue.worker &

python -c "from http.server import BaseHTTPRequestHandler, HTTPServer; \
class handler(BaseHTTPRequestHandler): \
    def do_GET(self): \
        self.send_response(200); self.end_headers(); self.wfile.write(b'OK'); \
HTTPServer(('', int('${PORT:-8080}')), handler).serve_forever()"