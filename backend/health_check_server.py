import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Responds with a 200 OK status for health checks."""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')


def run_server():
    """Starts the simple HTTP server."""
    port = int(os.getenv('PORT', 8080))
    server_address = ('', port)

    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"Health check server starting on port {port}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
