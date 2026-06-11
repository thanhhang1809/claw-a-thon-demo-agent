"""Simple browser UI and local API for the medieval story agent."""

from __future__ import annotations

import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.request import Request, urlopen

from medieval_story_agent import MedievalStoryAgent

PORT = 8501
AGENT_PORT = 8080
ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    agent = MedievalStoryAgent()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in {"/", "/index.html"}:
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if self.path != "/invocations":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode("utf-8") or "{}")
        result = self._call_agent(payload)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def _call_agent(self, payload):
        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(
                f"http://localhost:{AGENT_PORT}/invocations",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            return self._local_response(payload)

    def _local_response(self, payload):
        try:
            story_request = self.agent.normalize_request(payload)
        except ValueError as exc:
            return {"status": "error", "message": str(exc)}

        return {
            "status": "success",
            "agent": "medieval_story_writer",
            "result": self.agent.write_story(story_request),
            "llm": {
                "enabled": False,
                "message": "Using local browser-server fallback.",
            },
            "session_id": "browser-local",
        }


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server running at http://localhost:{PORT}")
    print(f"Web UI: http://localhost:{PORT}/")
    server.serve_forever()
