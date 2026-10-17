#!/usr/bin/env python3
"""
CodeCast Claude Code Hook Integration (Pure Python)
Called by Claude Code lifecycle hooks.
Sends event JSON to http://127.0.0.1:3001/api/event in under 100ms.
"""

import sys
import os
import json
import urllib.request

def main():
    args = sys.argv[1:]
    tool_name = os.environ.get("CLAUDE_TOOL_NAME", args[0] if len(args) > 0 else "Tool")
    file_path = os.environ.get("CLAUDE_FILE_PATH", args[1] if len(args) > 1 else "")
    exit_code = int(os.environ.get("CLAUDE_EXIT_CODE", "0"))
    event_type = os.environ.get("CLAUDE_HOOK_EVENT", "TOOL_FAILED" if exit_code != 0 else "TOOL_EXECUTION")

    payload = {
        "hook_event_name": event_type,
        "tool_name": tool_name,
        "file_path": file_path,
        "exit_code": exit_code
    }

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:3001/api/event",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=0.25)
    except Exception:
        # Silently pass so Claude Code is never blocked
        pass

if __name__ == "__main__":
    main()
