# 🏏 CodeCast
> **Your AI codes. We commentate.**  
> A 100% desktop-native Windows **Dynamic Notch / Island overlay** that turns your AI coding session into a live, high-voltage cricket match with an overly dramatic sports commentator narrating everything Claude Code does.

---

## 🖥️ 100% Native Windows Dynamic Notch (Zero Web / Browser!)
CodeCast is built using **PyQt6**, inspired by open-source Windows Dynamic Island projects:
* [rajsriv/dynamic-island-for-windows](https://github.com/rajsriv/dynamic-island-for-windows)
* [imnakul/venu---Dynamic-Notch-for-Windows](https://github.com/imnakul/venu---Dynamic-Notch-for-Windows)
* [khanhas/Notch](https://github.com/khanhas/Notch)
* [Smart-notch](https://github.com/Avenger11764/Smart-notch)

```
        ┌────────────────────────────────────────────────────────┐
        │  [======]  Stealth Idle Notch (Hidden at Top Bezel)    │
        └────────────────────────────────────────────────────────┘
                                 │ (Hover / Claude Action)
                                 ▼
        ┌────────────────────────────────────────────────────────┐
        │   Air Gap (14px) • Floating Island (Continuous Curves)  │
        │   Claude XI  •  48/1 (2.4 ov)  •  "TOUCHED THE CSS!"   │
        └────────────────────────────────────────────────────────┘
```

---

## ⚡ The Pipeline
```
[ Claude Code in Terminal ]
            │
            ▼ (Lifecycle Hook HTTP POST)
[ CodeCast Embedded Event Server (:3001) ]
            │
    ┌───────┴───────────────┐
    ▼                       ▼
[ Commentary Engine ]   [ Audio Voice Player ]
 (Gemini / Fallback)     (ElevenLabs + SAPI)
    │                       │
    └───────┬───────────────┘
            ▼ (PyQt Signal Dispatch)
[ Native Windows Dynamic Island ]
   • Resting state: Compact live cricket scoreboard pill
   • Action state: Smoothly expands with sports flashes & voice
   • Drawer state: Match center, stats & replay simulator
```

---

## 🏏 Cricket Commentary Reactions

| Terminal Event | Cricket Moment | Commentator Reaction |
|---|---|---|
| **Task Initialized** | Coin Toss & Match Start | *"The pitch is ready. The code is not. Claude strides out to the middle!"* |
| **File Edited** | Attacking Boundary Shot | *"He's touched the CSS! An absolute daredevil move through extra cover!"* |
| **Tool / Test Failed** | ⚡ Wicket Falls | *"AND HE'S GONE! Bowled him neck and crop straight into the stack trace!"* |
| **Tests Passed** | 🏏 Massive Six | *"IT'S GREEN! That has cleared the stadium roof! Nobody knows how, but it's green!"* |
| **Permission Request** | 📺 3rd Umpire Review | *"Upstairs we go! The human operator has been summoned to the screen!"* |
| **Repeated Edits** | Stubborn Defense | *"Fourth attempt at the exact same file! Incredible dogged resistance!"* |
| **Task Completed** | 🏆 Historic Century | *"HE'S DONE IT! What a magnificent finish! Whether it works in production is another matter!"* |

---

## 🚀 Quickstart

### 1. Requirements
Ensure PyQt6 is installed:
```bash
pip install PyQt6
```

### 2. Launch CodeCast
```bash
python main.py
```
*(Or double-click `run.bat`)*

A sleek obsidian Dynamic Notch is nestled at the top bezel. Hover over it or trigger an event to see it float down with an air gap and smooth continuous capsule curves.

---

## 🎮 Replay Simulator (Instant Demo for Pitch)

Want to rehearse or pitch to judges without running Claude Code?
* Click **`[Scorecard ▾]`** on your desktop island to drop down the Match Center.
* In the **Demo Simulator** panel, click any cricket event (`Attacking Shot`, `Wicket Falls`, `3rd Umpire`, `Huge Six!`, `Century Win`).
* Watch the island expand, play commentator audio, and update stats!

Or run the automated 6-ball match simulator in another terminal:
```bash
python simulate.py
```

---

## 🔌 Connected with Claude Code (Already Configured!)

CodeCast is now **fully wired up** into both your global `~/.claude/settings.json` and local `.claude/settings.json`! Every tool call streams directly from Claude Code into the Notch via stdin.

### Configured Lifecycle Hooks:
* **`UserPromptSubmit`** → Fires when you enter a prompt. Notch announces match beginning / new batsman.
* **`PostToolUse`** → Automatically streams every tool execution (`Edit`, `Write`, `Bash`, `Glob`, `Grep`) with live parameters and file paths.
* **`Notification`** → Triggers a **3rd Umpire Review** when Claude requests permission or attention.
* **`Stop`** → Celebrates **Historic Finish / Century** when Claude completes the task.

Whenever you run `claude` in any terminal, every tool execution will automatically broadcast to your desktop Dynamic Island with humorous live cricket commentary and speech!

Or send manual events from any script:
```bash
curl -X POST http://localhost:3001/api/event \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"FileEdit","file_path":"src/index.py"}'
```

---

## 🛠️ Architecture & Tech Stack
* **Desktop Shell:** Pure PyQt6 (`FramelessWindowHint`, `WindowStaysOnTopHint`, `WA_TranslucentBackground`)
* **Event Intake:** Embedded Python HTTP server daemon on port 3001
* **Commentary:** Gemini 2.5 Flash / OpenAI + Curated Cricket Matrix ([HRD.md](file:///c:/Projects/Hackathon/Teens%20Delhi%202/docs/HRD.md))
* **Voice:** ElevenLabs TTS API (`eleven_turbo_v2_5`) + Windows SAPI speech fallback

---

## 👥 Hackathon Submission
Built for **Teens Delhi Hackathon 2026** by the CodeCast Team.  
License: Apache-2.0
