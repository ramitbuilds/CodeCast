#!/usr/bin/env python3
"""
CodeCast — Minimalist Floating Dynamic Notch for Windows
Pure Minimalist Monochrome Cricket Commentary Overlay for Claude Code.

- Pure Stealth Idle: Pitch black 120x6px notch nestled against screen top bezel.
- Clean Hover: Floats down with 14px air gap, showing crisp white "Claude Code".
- Ultra-Clean Commentary Island: Expands smoothly into a floating capsule showing
  ONLY the punchy cricket commentary quote in pure white text.
- No Distractions: Zero scores, zero fake stats, zero colored badges, zero raw commands.
- Continuous Smooth Pill Curves: Mathematical capsule (radius = h / 2) with soft drop shadow.
"""

import sys
import os
import time
import socket

# Single-instance enforcement:
try:
    _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _lock_socket.bind(("127.0.0.1", 3002))
    _lock_socket.listen(1)
except OSError:
    print("[CodeCast] Another instance of CodeCast is already running. Exiting.")
    sys.exit(0)

from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, 
    QParallelAnimationGroup, pyqtProperty, pyqtSignal, QObject
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QPainterPath, QFont, QCursor
)
from PyQt6.QtWidgets import QApplication, QWidget

from commentary_engine import generate_commentary
from audio_player import AudioPlayer
from server_thread import start_event_server

def is_claude_process_running():
    """Fast, zero-overhead Windows process scan via kernel32 snapshot (< 1ms)."""
    try:
        import ctypes, ctypes.wintypes
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ('dwSize', ctypes.wintypes.DWORD),
                ('cntUsage', ctypes.wintypes.DWORD),
                ('th32ProcessID', ctypes.wintypes.DWORD),
                ('th32DefaultHeapID', ctypes.c_size_t),
                ('th32ModuleID', ctypes.wintypes.DWORD),
                ('cntThreads', ctypes.wintypes.DWORD),
                ('th32ParentProcessID', ctypes.wintypes.DWORD),
                ('pcPriClassBase', ctypes.c_long),
                ('dwFlags', ctypes.wintypes.DWORD),
                ('szExeFile', ctypes.c_char * 260)
            ]
        kernel32 = ctypes.windll.kernel32
        h = kernel32.CreateToolhelp32Snapshot(2, 0)
        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        running = False
        if kernel32.Process32First(h, ctypes.byref(pe)):
            while True:
                name = pe.szExeFile.decode('utf-8', 'ignore').lower()
                if 'claude' in name:
                    running = True
                    break
                if not kernel32.Process32Next(h, ctypes.byref(pe)):
                    break
        kernel32.CloseHandle(h)
        return running
    except Exception:
        return False

class EventBridge(QObject):
    event_signal = pyqtSignal(dict)

class FloatingDynamicNotch(QWidget):
    def __init__(self):
        super().__init__()

        # Frameless, Always on Top, Tool Window with Translucent Canvas
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setMouseTracking(True)

        # State Dimensions (Width, Height, Floating Air Gap Y Offset)
        # IDLE: Stealth notch flush at top bezel
        self.IDLE_W, self.IDLE_H, self.IDLE_Y = 120, 6, 0
        # PEEK: Clean floating pill on hover
        self.PEEK_W, self.PEEK_H, self.PEEK_Y = 200, 36, 14
        # ALERT: Sleek continuous capsule for commentary quotes
        self.ALERT_W, self.ALERT_H, self.ALERT_Y = 560, 48, 14

        self._island_w = float(self.IDLE_W)
        self._island_h = float(self.IDLE_H)
        self._island_y = float(self.IDLE_Y)

        self.current_state = "idle"  # idle | peek | alert

        # Telemetry State
        self.claude_online = is_claude_process_running()
        self.last_hook_time = 0.0
        self.commentary = ""

        # Voice Narration
        self.audio = AudioPlayer()

        # Spring Animations
        self.w_anim = QPropertyAnimation(self, b"island_w")
        self.h_anim = QPropertyAnimation(self, b"island_h")
        self.y_anim = QPropertyAnimation(self, b"island_y")
        
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(self.w_anim)
        self.anim_group.addAnimation(self.h_anim)
        self.anim_group.addAnimation(self.y_anim)
        self.anim_group.finished.connect(self._on_animation_finished)

        # Auto-shrink Timer (retract back to stealth notch after commentary)
        self.autohide_timer = QTimer(self)
        self.autohide_timer.setSingleShot(True)
        self.autohide_timer.timeout.connect(self.shrink_to_idle)

        # Geometry Setup
        self.screen_geo = QApplication.primaryScreen().geometry()
        self.set_window_bounds_for(self.IDLE_W, self.IDLE_H, self.IDLE_Y)

        # Proximity Hover Polling (every 35ms)
        self.proximity_timer = QTimer(self)
        self.proximity_timer.setInterval(35)
        self.proximity_timer.timeout.connect(self.check_proximity)
        self.proximity_timer.start()

        # Debounce timer when cursor moves away
        self.leave_debounce_timer = QTimer(self)
        self.leave_debounce_timer.setSingleShot(True)
        self.leave_debounce_timer.setInterval(320)
        self.leave_debounce_timer.timeout.connect(self._do_retract)

        # Background Claude Process Poller (every 800ms)
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(800)
        self.status_timer.timeout.connect(self.check_claude_status)
        self.status_timer.start()

        # Start Background Event Intake Server on Port 3001
        self.bridge = EventBridge()
        self.bridge.event_signal.connect(self.on_event_received)
        start_event_server(self.bridge.event_signal.emit, port=3001)

    @pyqtProperty(float)
    def island_w(self):
        return self._island_w

    @island_w.setter
    def island_w(self, val):
        self._island_w = val
        self.update()

    @pyqtProperty(float)
    def island_h(self):
        return self._island_h

    @island_h.setter
    def island_h(self, val):
        self._island_h = val
        self.update()

    @pyqtProperty(float)
    def island_y(self):
        return self._island_y

    @island_y.setter
    def island_y(self, val):
        self._island_y = val
        self.update()

    def set_window_bounds_for(self, w, h, y):
        win_w = int(w + 40)
        win_h = int(y + h + 30)
        win_x = (self.screen_geo.width() - win_w) // 2
        self.setGeometry(win_x, 0, win_w, win_h)

    def _on_animation_finished(self):
        if self.current_state == "idle":
            self.set_window_bounds_for(self.IDLE_W, self.IDLE_H, self.IDLE_Y)

    def check_claude_status(self):
        running = is_claude_process_running()
        if time.time() - self.last_hook_time < 8:
            running = True

        if running != self.claude_online:
            self.claude_online = running
            if self.claude_online:
                self.show()
                self.shrink_to_idle()
            else:
                self.hide()

    def animate_to(self, target_w, target_h, target_y, new_state, easing=QEasingCurve.Type.OutBack, duration=420):
        self.current_state = new_state
        self.anim_group.stop()

        max_w = max(self._island_w, float(target_w))
        max_h = max(self._island_h, float(target_h))
        max_y = max(self._island_y, float(target_y))
        self.set_window_bounds_for(max_w, max_h, max_y)

        for anim in [self.w_anim, self.h_anim, self.y_anim]:
            anim.setDuration(duration)
            anim.setEasingCurve(easing)

        self.w_anim.setEndValue(float(target_w))
        self.h_anim.setEndValue(float(target_h))
        self.y_anim.setEndValue(float(target_y))
        self.anim_group.start()

    def check_proximity(self):
        # Don't interrupt active commentary alert
        if self.current_state == "alert":
            return

        cursor = QCursor.pos()
        cx = self.screen_geo.width() // 2
        dx = abs(cursor.x() - cx)
        dy = cursor.y()

        if self.current_state == "idle":
            if dx <= 110 and dy <= 32:
                self.leave_debounce_timer.stop()
                self.animate_to(self.PEEK_W, self.PEEK_H, self.PEEK_Y, "peek", QEasingCurve.Type.OutBack, 380)

        elif self.current_state == "peek":
            if dx <= 140 and dy <= 65:
                self.leave_debounce_timer.stop()
            else:
                if not self.leave_debounce_timer.isActive():
                    self.leave_debounce_timer.start()

    def _do_retract(self):
        if self.current_state == "peek":
            self.shrink_to_idle()

    def get_pill_rect(self):
        pill_x = (self.width() - self._island_w) / 2.0
        pill_y = float(self._island_y)
        return QRectF(pill_x, pill_y, float(self._island_w), float(self._island_h))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Clicking dismisses alert or shrinks
            self.shrink_to_idle()

    def on_event_received(self, data):
        self.claude_online = True
        self.last_hook_time = time.time()
        if not self.isVisible():
            self.show()

        # Only expand and narrate on actual tool executions
        if data.get("is_major_action"):
            self.commentary = data.get("commentary", "")

            # 1. Narrate commentary voice
            if self.commentary:
                self.audio.speak(self.commentary)

            # 2. Fluid floating drop-down expansion showing ONLY the commentary line
            self.animate_to(self.ALERT_W, self.ALERT_H, self.ALERT_Y, "alert", QEasingCurve.Type.OutBack, 460)

            # 3. Auto-retract back to stealth notch after 7 seconds
            self.autohide_timer.start(7000)

    def shrink_to_idle(self):
        self.autohide_timer.stop()
        self.leave_debounce_timer.stop()
        self.animate_to(self.IDLE_W, self.IDLE_H, self.IDLE_Y, "idle", QEasingCurve.Type.OutCubic, 360)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        pill_rect = self.get_pill_rect()
        w = pill_rect.width()
        h = pill_rect.height()

        # Mathematical continuous capsule curvature: radius = h / 2.0
        if self.current_state == "idle":
            radius = min(h / 2.0, 3.0)
        else:
            radius = h / 2.0  # Perfect continuous pill

        pill_path = QPainterPath()
        pill_path.addRoundedRect(pill_rect, radius, radius)

        # Subtle Ambient Drop Shadow (when detached from bezel)
        if self._island_y > 4:
            for i in range(3):
                shadow_offset = (i + 1) * 1.5
                shadow_rect = pill_rect.adjusted(-i * 1.0, shadow_offset, i * 1.0, shadow_offset + i * 1.0)
                shadow_path = QPainterPath()
                shadow_path.addRoundedRect(shadow_rect, radius + i, radius + i)
                p.strokePath(shadow_path, QPen(QColor(0, 0, 0, 20 - i * 6), 1.5))

        # Core Obsidian Body (Pure Deep Matte Black)
        p.fillPath(pill_path, QColor(8, 8, 8, 252))

        # Subtle Specular Rim (Frosted White Highlight, No Color)
        if self.current_state != "idle":
            p.strokePath(pill_path, QPen(QColor(255, 255, 255, 26), 1.0))

        # Render State Content
        if self.current_state == "idle":
            pass
        elif self.current_state == "peek":
            self.draw_peek(p, pill_rect)
        elif self.current_state == "alert":
            self.draw_alert(p, pill_rect)

    def draw_peek(self, p, r):
        # Clean, pure white, no scores, no extra text
        p.setPen(QColor(245, 245, 245))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, "Claude Code")

    def draw_alert(self, p, r):
        # ONLY display the clean taunt without double quotes
        if self.commentary:
            p.setPen(QColor(255, 255, 255))
            p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
            text_rect = r.adjusted(24, 0, -24, 0)
            clean_text = self.commentary.replace('"', '').replace('“', '').replace('”', '').strip()
            p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, clean_text)

def main():
    app = QApplication(sys.argv)
    notch = FloatingDynamicNotch()
    if notch.claude_online:
        notch.show()
    else:
        notch.hide()
        print("[CodeCast] Daemon active. Notch is hidden and will appear when 'claude' is launched.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
