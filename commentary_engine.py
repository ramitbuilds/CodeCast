"""
CodeCast Commentary Engine (Python Native)
Implements HRD.md cricket commentary guidelines:
- Sarcastic, quick-witted, dramatic cricket commentator
- Uses LLM (Gemini / OpenAI) when available, falls back to rich cricket matrix
"""

import os
import json
import random
import urllib.request
import urllib.error

FALLBACK_COMMENTARY = {
    "TASK_STARTED": [
        "The pitch is ready. The code is not. Claude strides out to the middle!",
        "Massive crowd in the terminal today as the innings gets underway!",
        "A fresh pitch rolled out, and Claude takes strike under overcast skies!",
        "The coin has been tossed and Claude has elected to code first!"
    ],
    "FILE_EDITED": [
        "He's touched the CSS! An absolute daredevil move through extra cover!",
        "He's gone straight after the source file! High risk, high reward!",
        "A delicate late cut past backward point! That file didn't see it coming!",
        "Stepping down the track and taking on the legacy codebase directly!"
    ],
    "TOOL_FAILED": [
        "AND HE'S GONE! Bowled him neck and crop straight into the stack trace!",
        "Absolute disaster! A peach of an in-swinger knocks the build clean over!",
        "Caught behind on the unhandled exception! The umpire's finger goes straight up!",
        "Timber! The syntax error crashes clean through the gate!"
    ],
    "TESTS_PASSED": [
        "IT'S GREEN! That has cleared the stadium roof! Six runs!",
        "WHAT A COMEBACK! Right off the meat of the bat, all tests green!",
        "Boundary! Glorious stroke play through the covers!",
        "Nobody knows how that passed, but the scoreboard doesn't lie!"
    ],
    "PERMISSION_REQUIRED": [
        "Third umpire review! The human operator has been summoned to the screen!",
        "Upstairs we go! The on-field umpire is checking the front foot!",
        "DRS review! The crowd holds its breath waiting for sudo permission!",
        "The decision is sent to the third umpire! Checking clean authorization!"
    ],
    "REPEATED_EDITS": [
        "Fourth attempt at the exact same file! Incredible dogged persistence!",
        "He's defending stubbornly against this tricky bug outside off-stump!",
        "Refusing to give his wicket away on this pesky function!"
    ],
    "TASK_COMPLETED": [
        "HE'S DONE IT! WHAT A FINISH! A historic century in the terminal!",
        "The arms go up in the air! Whether it works in production is another matter!",
        "Match-winning knock from Claude Code under extreme stadium pressure!"
    ],
    "DEFAULT": [
        "Solid defensive stroke back down the ground.",
        "Rotating the strike with a quick single in the terminal.",
        "Working the ball into the gap for another routine tool execution."
    ]
}

def get_random_commentary(event_type, context=""):
    lines = FALLBACK_COMMENTARY.get(event_type, FALLBACK_COMMENTARY["DEFAULT"])
    picked = random.choice(lines)
    if context and event_type == "FILE_EDITED" and context not in picked:
        return f"{picked} ({context})"
    return picked

def generate_commentary(event_type, context="", title="", raw_data=None):
    """Generates commentary using Gemini/OpenAI if API keys exist, else fallback"""
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if not gemini_key and not openai_key:
        return get_random_commentary(event_type, context)

    prompt = f"""You are an overdramatic, witty, sarcastic international cricket commentator commentating on a live coding session by Claude Code.
Event Type: {event_type}
Event Title: {title}
Context: {context}
Raw: {str(raw_data)[:120] if raw_data else ''}

CRITICAL RULES:
1. Treat this coding action like an intense international cricket moment (boundary, wicket, 3rd umpire, bouncer, yorker).
2. Sarcastic, hilarious, but never invent fake errors.
3. Length: Strictly 5 to 18 words. ONE single punchy sentence.
4. Output ONLY the commentary text. No quotes, no preamble."""

    try:
        if gemini_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 50, "temperature": 0.9}
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                if text:
                    return text.strip('"\'')
    except Exception as e:
        pass

    return get_random_commentary(event_type, context)
