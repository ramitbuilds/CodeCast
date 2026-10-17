#!/usr/bin/env python3
"""
CodeCast Claude Code Hook Integration
Invoked by Claude Code lifecycle hooks (PostToolUse, PreToolUse, UserPromptSubmit, Notification, Stop).
Reads JSON payload from stdin, extracts tool names & parameters, and dispatches to the CodeCast Dynamic Notch.
"""

import sys
import os
import json
import urllib.request
import datetime

EVENT_ENDPOINT = "http://127.0.0.1:3001/api/event"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hook.log")

def log(msg):
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")
    except Exception:
        pass

def parse_input():
    hook_type = sys.argv[1] if len(sys.argv) > 1 else "PostToolUse"
    payload = {
        "hook_event_name": hook_type,
        "tool_name": "",
        "file_path": "",
        "command": "",
        "error": None,
        "exit_code": 0,
        "prompt": ""
    }

    # Read JSON payload passed by Claude Code via stdin
    raw_stdin = ""
    try:
        if not sys.stdin.isatty():
            raw_stdin = sys.stdin.read()
    except Exception:
        pass

    if raw_stdin.strip():
        try:
            data = json.loads(raw_stdin)
            payload["raw"] = data
            
            # Extract tool information
            payload["tool_name"] = data.get("tool_name") or data.get("tool") or ""
            
            # Tool input arguments (file_path, command, etc.)
            tool_input = data.get("tool_input") or {}
            if isinstance(tool_input, dict):
                payload["file_path"] = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("file") or tool_input.get("pattern") or ""
                payload["command"] = tool_input.get("command") or tool_input.get("cmd") or ""
                payload["prompt"] = tool_input.get("prompt") or tool_input.get("query") or ""

            # Prompt event
            if "prompt" in data:
                payload["prompt"] = data["prompt"]

            # Notification event
            if "message" in data:
                payload["context"] = data["message"]

            # Response and error checks
            tool_response = data.get("tool_response") or data.get("response") or {}
            if isinstance(tool_response, dict):
                if tool_response.get("error") or tool_response.get("exit_code", 0) > 0:
                    payload["error"] = str(tool_response.get("error") or "Tool failed")
                    payload["exit_code"] = tool_response.get("exit_code", 1)
            elif isinstance(tool_response, str) and ("error" in tool_response.lower() or "exception" in tool_response.lower() or "failed" in tool_response.lower()):
                if "0 failed" not in tool_response:
                    payload["error"] = tool_response[:100]

        except Exception as e:
            log(f"Error parsing stdin JSON: {e}")

    # Fallbacks to environment variables if provided
    if not payload["tool_name"]:
        payload["tool_name"] = os.environ.get("CLAUDE_TOOL_NAME", "")
    if not payload["file_path"]:
        payload["file_path"] = os.environ.get("CLAUDE_FILE_PATH", "")

    return payload

def main():
    payload = parse_input()
    tool = payload.get("tool_name") or payload.get("hook_event_name")
    target = payload.get("file_path") or payload.get("command") or payload.get("prompt") or ""
    log(f"Hook Triggered: {payload.get('hook_event_name')} | Tool: {tool} | Target: {target[:40]}")

    # Dispatch to CodeCast Dynamic Island
    try:
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            EVENT_ENDPOINT,
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=0.35) as resp:
            log(f"Dispatched -> Status: {resp.status}")
    except Exception as e:
        log(f"Dispatch failed, attempting to auto-start main.py: {e}")
        try:
            import subprocess
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            main_py = os.path.join(base_dir, "main.py")
            subprocess.Popen(["C:\\Python314\\pythonw.exe", main_py], cwd=base_dir)
            time.sleep(0.4)
            with urllib.request.urlopen(req, timeout=0.35) as resp:
                log(f"Dispatched after auto-start -> Status: {resp.status}")
        except Exception:
            pass

    sys.exit(0)

if __name__ == "__main__":
    main()
