# CodeCast — Product Requirements Document

**Tagline:** Your AI codes. We commentate.

### 1. Overview
CodeCast turns AI coding sessions into hilarious live sports commentary using ElevenLabs-generated voices.

### 2. Core Features
- **Agent Integration:** Detect Claude Code activity through hooks.
- **Live Commentary:** Generate humorous cricket-style commentary based on actual coding events.
- **Voice Narration:** Use ElevenLabs TTS to narrate events.
- **Live Dashboard:** Display a scoreboard, event feed, and animated reactions.
- **Game Stats:** Track tool calls, files edited, test failures, and task completions.
- **Replay Mode:** Simulate events for reliable demonstrations.

### 3. Event → Commentary
| Event | Example |
|---|---|
| File edited | "He's going on the attack!" |
| Test failed | "Absolute disaster!" |
| Test passed | "WHAT A COMEBACK!" |
| Permission requested | "Third umpire review!" |
| Task completed | "WHAT A FINISH!" |

### 4. Tech Stack
- **Frontend:** React + Tailwind CSS
- **Backend:** Node.js + WebSocket
- **Integration:** Claude Code Hooks
- **AI:** LLM for contextual commentary
- **Voice:** ElevenLabs API

### 5. MVP Success Criteria
- Real Claude Code events update the dashboard.
- Commentary matches actual events.
- ElevenLabs narrates commentary automatically.
- Dashboard works smoothly during live demonstrations.
- Demo/replay mode works without Claude Code.

### 6. Out of Scope
Authentication, accounts, analytics, multiplayer, support for additional coding agents, and mobile apps.

**Deadline:** Functional MVP and GitHub submission by 2:30 PM.