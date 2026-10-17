#!/usr/bin/env python3
"""
CodeCast Automated Match Simulator (Pure Python)
Simulates a live 6-ball cricket over with realistic pauses,
triggering live reactions on the Native CodeCast Dynamic Island.
Usage: python simulate.py
"""

import time
import json
import urllib.request

MATCH_SCRIPT = [
    {
        "event": "task_start",
        "prompt": "Fix JWT token expiry and refactor auth controller",
        "delay": 1.0
    },
    {
        "tool_name": "FileEdit",
        "file_path": "src/controllers/auth.py",
        "delay": 3.5
    },
    {
        "tool_name": "pytest",
        "command": "pytest tests/test_auth.py",
        "error": "AssertionError: expected 401 to equal 200",
        "exit_code": 1,
        "delay": 4.5
    },
    {
        "event": "permission_request",
        "tool_name": "AskUser",
        "command": "Allow write access to production database config?",
        "delay": 4.0
    },
    {
        "tool_name": "Replace",
        "file_path": "src/controllers/auth.py",
        "delay": 3.5
    },
    {
        "tool_name": "pytest",
        "command": "pytest -v",
        "exit_code": 0,
        "delay": 4.5
    },
    {
        "event": "task_complete",
        "prompt": "Successfully resolved auth bug and verified all 16 tests!",
        "delay": 3.0
    }
]

def send_event(data):
    url = "http://127.0.0.1:3001/api/event"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            print(f" [Sent Event] -> {data.get('tool_name') or data.get('event')}")
    except Exception as e:
        print(f" [Error] Could not connect to http://127.0.0.1:3001. Is CodeCast running? ({e})")

def main():
    print("=" * 60)
    print("🏏 CodeCast — Starting Match Replay Simulation...")
    print("=" * 60)

    for i, step in enumerate(MATCH_SCRIPT):
        time.sleep(step.get("delay", 2.0))
        send_event(step)

    print("\n🏆 Match Simulation Complete!")

if __name__ == "__main__":
    main()
