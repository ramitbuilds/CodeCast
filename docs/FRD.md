# CodeCast — FRD

### Core Functionality

**FR-01: Agent Monitoring**
- Detect task start, tool execution, failures, permission requests, and task completion.
- Record timestamps and event types.

**FR-02: Commentary Engine**
- Map events to cricket-style reactions.
- Generate context-aware commentary using AI.
- Fall back to predefined lines if generation fails.

**FR-03: Voice**
- Narrate commentary automatically using ElevenLabs.
- Support mute/unmute.
- Avoid overlapping speech.

**FR-04: Live Dashboard**
- Display current agent status.
- Show total tool calls, files edited, and confirmed failures.
- Display commentary and recent event history.

**FR-05: Replay Mode**
- Replay predefined sample events.
- Clearly label simulated events.

### Event Mapping
| Event | Reaction |
|---|---|
| Task started | Match begins |
| File edited | Attacking shot |
| Tool failed | Wicket falls |
| Tests confirmed passed | Boundary! |
| Permission required | Third umpire |
| Task completed | Match ends |

### Acceptance Criteria
- Events appear without manually refreshing.
- Statistics reflect actual observed events.
- Voice matches displayed commentary.
- Coding continues even if CodeCast crashes.
- Replay works independently of Claude Code.