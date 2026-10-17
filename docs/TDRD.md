# CodeCast — Testing & Demo Requirements

### Functional Tests
- [ ] Claude Code hook successfully sends an event.
- [ ] Dashboard receives live updates.
- [ ] Counters reflect actual events.
- [ ] AI produces relevant commentary.
- [ ] ElevenLabs speech plays successfully.
- [ ] Mute prevents playback.
- [ ] Multiple events don't overlap audio.
- [ ] API failures don't interrupt coding.
- [ ] Replay mode works without the coding agent.

### Live Demonstration
1. Introduce CodeCast in one sentence.
2. Start a real Claude Code task.
3. Show the live scoreboard responding to agent activity.
4. Trigger a file edit or tool event.
5. Play the corresponding ElevenLabs commentary.
6. Complete the task and show the match-ending reaction.

### Failure Fallbacks
- AI unavailable → Prewritten commentary.
- ElevenLabs unavailable → Text-only commentary.
- Claude unavailable → Clearly labelled replay mode.
- WebSocket disconnected → Reconnect without crashing.

### Definition of Done
A working live agent-to-commentary pipeline, functional dashboard, voice narration, reliable fallback, and GitHub README.

**Submission deadline: 2:30 PM.**