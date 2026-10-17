#!/usr/bin/env node
/**
 * Claude Code Hook integration script
 * Fires on tool execution, reads hook arguments/env, and posts to CodeCast.
 */

async function main() {
  const args = process.argv.slice(2);
  const toolName = process.env.CLAUDE_TOOL_NAME || args[0] || 'Tool';
  const filePath = process.env.CLAUDE_FILE_PATH || args[1] || '';
  const exitCode = parseInt(process.env.CLAUDE_EXIT_CODE || '0', 10);
  const eventType = process.env.CLAUDE_HOOK_EVENT || (exitCode !== 0 ? 'TOOL_FAILED' : 'TOOL_EXECUTION');

  const payload = {
    hook_event_name: eventType,
    tool_name: toolName,
    file_path: filePath,
    exit_code: exitCode,
    timestamp: new Date().toISOString()
  };

  try {
    const res = await fetch('http://localhost:3001/api/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      // 500ms timeout so Claude Code never waits
      signal: AbortSignal.timeout(500)
    });
  } catch (err) {
    // Silently continue so Claude Code is never interrupted
  }
}

main();
