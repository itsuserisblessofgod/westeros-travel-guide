"""Westeros Travel Guide API: a tiny HTTP service using only the standard library."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from locations import LOCATIONS


def route(path):
    """Map a request path to (status_code, json_body). Pure function: easy to test."""
    path = path.split("?", 1)[0].rstrip("/") or "/"

    if path == "/":
        return 200, {"message": "Welcome to the Westeros Travel Guide. Try /locations"}
    if path == "/healthz":
        return 200, {"status": "ok"}
    if path == "/locations":
        return 200, {"locations": sorted(LOCATIONS)}
    if path.startswith("/locations/"):
        slug = path[len("/locations/"):].lower()
        if slug in LOCATIONS:
            return 200, LOCATIONS[slug]
        return 404, {"error": f"Unknown location: {slug}"}
    return 404, {"error": "Not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, body = route(self.path)
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


def make_server(port):
    return ThreadingHTTPServer(("0.0.0.0", port), Handler)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Westeros Travel Guide listening on port {port}", flush=True)
    make_server(port).serve_forever()
