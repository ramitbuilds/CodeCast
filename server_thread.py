"""
CodeCast Local Background Event Server
Listens on http://localhost:3001/api/event for Claude Code hook payloads
and dispatches them to the PyQt Dynamic Notch.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from commentary_engine import generate_commentary

def normalize_event(body):
    event = body.get("event") or body.get("type") or body.get("hook_event_name") or "TOOL_EXECUTION"
    tool = (body.get("tool_name") or body.get("tool") or "").lower()
    file_path = body.get("file_path") or body.get("file") or body.get("target") or ""
    is_error = body.get("error") or (body.get("exit_code", 0) > 0) or body.get("failed")
    is_test = "test" in (body.get("command") or "") or "test" in tool

    if event in ["task_start", "TASK_STARTED"]:
        return {
            "type": "TASK_STARTED",
            "badge": "MATCH COMMENCES",
            "color": "#f59e0b",
            "title": "Match Begins",
            "context": body.get("prompt", "Claude takes strike")[:40],
            "runs": 0,
            "wickets": 0
        }

    if event in ["task_complete", "TASK_COMPLETED"]:
        return {
            "type": "TASK_COMPLETED",
            "badge": "🏆 HISTORIC FINISH",
            "color": "#eab308",
            "title": "Match Complete",
            "context": "All tasks completed",
            "runs": 10,
            "wickets": 0
        }

    if is_error:
        return {
            "type": "TOOL_FAILED",
            "badge": "⚡ WICKET FALLS",
            "color": "#ef4444",
            "title": "Dismissal",
            "context": str(body.get("error") or tool or "Command failed")[:45],
            "runs": 0,
            "wickets": 1
        }

    if is_test and not is_error:
        return {
            "type": "TESTS_PASSED",
            "badge": "🏏 HUGE SIX!",
            "color": "#10b981",
            "title": "Tests Green",
            "context": body.get("command", "Tests passed")[:40],
            "runs": 6,
            "wickets": 0
        }

    if any(k in tool for k in ["edit", "write", "replace"]) or file_path:
        return {
            "type": "FILE_EDITED",
            "badge": "ATTACKING SHOT",
            "color": "#3b82f6",
            "title": "Boundary Attempt",
            "context": file_path or tool or "File modified",
            "runs": 4,
            "wickets": 0
        }

    if "ask" in tool or "permission" in event.lower():
        return {
            "type": "PERMISSION_REQUIRED",
            "badge": "📺 3RD UMPIRE",
            "color": "#f59e0b",
            "title": "Review",
            "context": "Human permission requested",
            "runs": 1,
            "wickets": 0
        }

    return {
        "type": "TOOL_EXECUTION",
        "badge": "QUICK SINGLE",
        "color": "#64748b",
        "title": "Tool Run",
        "context": tool or body.get("command", "Routine play")[:35],
        "runs": 1,
        "wickets": 0
    }

class EventServerHandler(BaseHTTPRequestHandler):
    dispatcher_callback = None

    def log_message(self, format, *args):
        # Silence standard HTTP logging in terminal
        pass

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","mode":"native-desktop"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/event":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            
            # Respond immediately to unblock Claude Code
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"received"}')

            try:
                body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
                norm = normalize_event(body)
                commentary = body.get("commentary") or generate_commentary(
                    norm["type"], norm["context"], norm["title"], body
                )
                norm["commentary"] = commentary

                if EventServerHandler.dispatcher_callback:
                    EventServerHandler.dispatcher_callback(norm)
            except Exception as e:
                pass
        else:
            self.send_response(404)
            self.end_headers()

def start_event_server(callback, port=3001):
    EventServerHandler.dispatcher_callback = callback
    server = HTTPServer(("127.0.0.1", port), EventServerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
