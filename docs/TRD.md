# CodeCast — TRD

### Architecture
Claude Code Hooks → Node.js Server → Event Processor → LLM → ElevenLabs TTS → React Dashboard

### Tech Stack
- Frontend: React, Tailwind CSS
- Backend: Node.js, Express, WebSocket
- Agent Integration: Claude Code Hooks
- AI: LLM for contextual commentary
- Voice: ElevenLabs TTS
- Storage: In-memory session state (no database)

### Technical Requirements
1. Receive real Claude Code hook events through a local HTTP endpoint.
2. Process events asynchronously without blocking Claude.
3. Broadcast events and statistics over WebSocket.
4. Generate short commentary using event context.
5. Convert commentary to speech using ElevenLabs.
6. Queue audio to prevent overlapping announcements.
7. Keep API keys server-side; exclude secrets and sensitive code from AI requests.
8. Provide fallback commentary when AI or TTS fails.

### Constraints
- Local-first application.
- One active coding session for MVP.
- No authentication or database.
- Must run without paid infrastructure.