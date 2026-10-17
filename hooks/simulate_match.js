#!/usr/bin/env node
/**
 * CodeCast Full Match Replay Simulator
 * Runs a realistic live commentary sequence to demonstrate the entire pipeline.
 * Usage: node hooks/simulate_match.js
 */

const matchScript = [
  {
    event: 'task_start',
    prompt: 'Refactor authentication middleware and fix token expiry bug',
    delay: 1000
  },
  {
    tool_name: 'FileEdit',
    file_path: 'src/auth/jwt.js',
    delay: 4000
  },
  {
    tool_name: 'bash',
    command: 'npm run test:auth',
    error: 'AssertionError: expected 401 to equal 200',
    exit_code: 1,
    delay: 5000
  },
  {
    event: 'permission_request',
    tool_name: 'AskUser',
    command: 'Allow write access to .env.production?',
    delay: 4500
  },
  {
    tool_name: 'Replace',
    file_path: 'src/auth/jwt.js',
    delay: 4000
  },
  {
    tool_name: 'bash',
    command: 'npm test',
    exit_code: 0,
    delay: 5000
  },
  {
    event: 'task_complete',
    prompt: 'Successfully fixed token expiry bug and verified test suite!',
    delay: 3000
  }
];

async function sendEvent(data) {
  try {
    const res = await fetch('http://localhost:3001/api/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    console.log(`[Simulator Sent] ${data.tool_name || data.event}`);
  } catch (err) {
    console.error(`[Simulator Error] Could not connect to http://localhost:3001. Is the server running?`);
  }
}

async function run() {
  console.log('🏏 Starting CodeCast Match Simulation...');
  console.log('Ensure both the server (:3001) and client (:5173) are running!\n');

  for (let i = 0; i < matchScript.length; i++) {
    const step = matchScript[i];
    await new Promise(r => setTimeout(r, step.delay));
    await sendEvent(step);
  }

  console.log('\n🏆 Match Simulation completed!');
}

run();
