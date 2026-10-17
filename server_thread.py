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
    tool = (body.get("tool_name") or body.get("tool") or "").strip()
    tool_lower = tool.lower()
    file_path = (body.get("file_path") or body.get("file") or body.get("target") or "").strip()
    if file_path:
        file_name = file_path.replace("\\", "/").split("/")[-1]
    else:
        file_name = ""
    command = (body.get("command") or "").strip()
    is_error = body.get("error") or (body.get("exit_code", 0) > 0) or body.get("failed")
    is_test = "test" in command.lower() or "test" in tool_lower
    prompt = (body.get("prompt") or "").strip()

    # UserPromptSubmit: prompt submitted by user (minor event)
    if event in ["UserPromptSubmit", "task_start", "TASK_STARTED"]:
        return {
            "type": "TASK_STARTED",
            "badge": "NEW OVER",
            "title": "Match Begins",
            "context": f"Prompt: {prompt[:38]}" if prompt else "Claude on strike",
            "runs": 0,
            "wickets": 0,
            "is_major_action": False
        }

    # Stop: end of turn (minor event, do not overwrite active tool alerts)
    if event in ["Stop", "task_complete", "TASK_COMPLETED"]:
        return {
            "type": "TASK_COMPLETED",
            "badge": "MAIDEN OVER",
            "title": "Turn Finished",
            "context": "Waiting for next delivery",
            "runs": 0,
            "wickets": 0,
            "is_major_action": False
        }

    # ==========================================
    # TOOL CALL ACTIONS (MAJOR CRICKET EVENTS!)
    # ==========================================
    if is_error:
        err_msg = str(body.get("error") or "Exit code non-zero")[:36]
        return {
            "type": "TOOL_FAILED",
            "badge": "WICKET FALLS",
            "title": "Dismissal",
            "context": f"{tool or 'Command'} failed: {err_msg}",
            "runs": 0,
            "wickets": 1,
            "is_major_action": True
        }

    if is_test and not is_error:
        cmd_str = command[:35] if command else (tool or "tests passed")
        return {
            "type": "TESTS_PASSED",
            "badge": "HUGE SIX!",
            "title": "Tests Green",
            "context": f"Green: {cmd_str}",
            "runs": 6,
            "wickets": 0,
            "is_major_action": True
        }

    if any(k in tool_lower for k in ["edit", "write", "replace", "patch", "notebook"]) or file_path:
        ctx = f"{tool or 'Edit'}: {file_name or file_path[:30]}"
        return {
            "type": "FILE_EDITED",
            "badge": "ATTACKING SHOT",
            "title": "Boundary Attempt",
            "context": ctx,
            "runs": 4,
            "wickets": 0,
            "is_major_action": True
        }

    if any(k in tool_lower for k in ["view", "read", "glob", "grep", "search", "list"]):
        ctx = f"{tool}: {file_name or command[:28] or 'Codebase'}"
        return {
            "type": "TOOL_EXECUTION",
            "badge": "FIELD SCOUTING",
            "title": "Field Inspection",
            "context": ctx,
            "runs": 1,
            "wickets": 0,
            "is_major_action": True
        }

    if "ask" in tool_lower or "permission" in event.lower() or "notification" in event.lower():
        return {
            "type": "PERMISSION_REQUIRED",
            "badge": "3RD UMPIRE",
            "title": "Review",
            "context": "Permission requested",
            "runs": 1,
            "wickets": 0,
            "is_major_action": True
        }

    # Routine command (Bash, git, etc.)
    cmd_desc = command[:32] if command else (file_name or "Command run")
    return {
        "type": "TOOL_EXECUTION",
        "badge": "QUICK SINGLE",
        "title": "Tool Run",
        "context": f"{tool or 'Bash'}: {cmd_desc}",
        "runs": 1,
        "wickets": 0,
        "is_major_action": True
    }

class EventServerHandler(BaseHTTPRequestHandler):
    dispatcher_callback = None

    def log_message(self, format, *args):
        pass

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def finish(self):
        try:
            super().finish()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def do_GET(self):
        try:
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(b'{"status":"ok","mode":"native-desktop"}')
            else:
                self.send_response(404)
                self.end_headers()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def do_POST(self):
        if self.path == "/api/event":
            body_bytes = b"{}"
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 0:
                    body_bytes = self.rfile.read(content_length)
                
                # Immediate HTTP 200 response to unblock Claude Code
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(b'{"status":"received"}')
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                pass

            # Asynchronous background AI commentary generation (never stalls HTTP)
            def process_event_async(data_bytes):
                try:
                    body = json.loads(data_bytes.decode("utf-8")) if data_bytes else {}
                    norm = normalize_event(body)

                    if norm.get("is_major_action"):
                        commentary = body.get("commentary") or generate_commentary(
                            norm["type"], norm["context"], norm["title"], body
                        )
                        norm["commentary"] = commentary
                    else:
                        norm["commentary"] = ""

                    if EventServerHandler.dispatcher_callback:
                        EventServerHandler.dispatcher_callback(norm)
                except Exception:
                    pass

            threading.Thread(target=process_event_async, args=(body_bytes,), daemon=True).start()
        else:
            try:
                self.send_response(404)
                self.end_headers()
            except Exception:
                pass

def start_event_server(callback, port=3001):
    EventServerHandler.dispatcher_callback = callback
    server = HTTPServer(("127.0.0.1", port), EventServerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
