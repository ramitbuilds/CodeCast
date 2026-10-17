#!/usr/bin/env python3
"""
CodeCast — Minimalist Floating Dynamic Notch for Windows
Inspired by Apple Dynamic Island, venu, and rajsriv.

Key Enhancements:
- Proximity-based Near Hover: Smoothly triggers when approaching near the top center,
  without needing to touch the exact 6px strip.
- 100% Glitch-Free Architecture: Window geometry is resized once per state transition,
  never on animation frames, preventing DWM flicker loops and synthetic mouseleave events.
- Debounce Hysteresis: 350ms leave buffer ensures rock-solid stability when hovering.
- Floating Air Gap: Floats with a 14px air gap below the top bezel on hover & events.
- Pure Minimalist Stealth Idle: Pitch black (#080808), 130x6px, zero text/borders at screen top.
- Continuous Smooth Pill Curves: Mathematical capsule (radius = h / 2) with soft drop shadow.
"""

import sys
import os
import time
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

MOCK_EVENTS = [
    {
        "type": "FILE_EDITED",
        "badge": "ATTACKING SHOT",
        "context": "src/auth/jwt.py",
        "runs": 4,
        "wickets": 0,
        "commentary": "He's touched the CSS! An absolute daredevil move through extra cover!"
    },
    {
        "type": "TOOL_FAILED",
        "badge": "WICKET FALLS",
        "context": "pytest: 1 failed",
        "runs": 0,
        "wickets": 1,
        "commentary": "AND HE'S GONE! Bowled him neck and crop straight into the stack trace!"
    },
    {
        "type": "PERMISSION_REQUIRED",
        "badge": "3RD UMPIRE",
        "context": "Write permissions",
        "runs": 1,
        "wickets": 0,
        "commentary": "Third umpire review! The human operator has been summoned to the screen!"
    },
    {
        "type": "TESTS_PASSED",
        "badge": "HUGE SIX!",
        "context": "All tests green",
        "runs": 6,
        "wickets": 0,
        "commentary": "IT'S GREEN! That has cleared the stadium roof! Nobody knows how, but it's green!"
    },
    {
        "type": "TASK_COMPLETED",
        "badge": "CENTURY FINISH",
        "context": "Session complete",
        "runs": 10,
        "wickets": 0,
        "commentary": "HE'S DONE IT! What a magnificent finish! Whether it works in production is another matter!"
    }
]

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
        # IDLE: Stealth notch flush at top bezel, no text, pure black
        self.IDLE_W, self.IDLE_H, self.IDLE_Y = 130, 6, 0
        # PEEK: Floating capsule with clean 14px air gap below bezel
        self.PEEK_W, self.PEEK_H, self.PEEK_Y = 290, 38, 14
        # ALERT: Fluid floating pill for commentary events
        self.ALERT_W, self.ALERT_H, self.ALERT_Y = 570, 98, 16
        # DRAWER: Expanded match center scorecard drawer
        self.DRAWER_W, self.DRAWER_H, self.DRAWER_Y = 620, 245, 16

        self._island_w = float(self.IDLE_W)
        self._island_h = float(self.IDLE_H)
        self._island_y = float(self.IDLE_Y)

        self.current_state = "idle"  # idle | peek | alert | drawer

        # Match Stats
        self.runs = 0
        self.wickets = 0
        self.balls = 0
        self.commentary = ""
        self.badge = ""
        self.context_info = ""

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

        # Auto-shrink Timer (retract to stealth notch after commentary)
        self.autohide_timer = QTimer(self)
        self.autohide_timer.setSingleShot(True)
        self.autohide_timer.timeout.connect(self.shrink_to_idle)

        # Geometry Setup
        self.screen_geo = QApplication.primaryScreen().geometry()
        self.set_window_bounds_for(self.IDLE_W, self.IDLE_H, self.IDLE_Y)

        # Proximity Hover Polling (every 35ms)
        # Checks if cursor is NEAR the notch instead of requiring pixel-perfect hover
        self.proximity_timer = QTimer(self)
        self.proximity_timer.setInterval(35)
        self.proximity_timer.timeout.connect(self.check_proximity)
        self.proximity_timer.start()

        # Debounce timer when cursor moves away (prevents flicker)
        self.leave_debounce_timer = QTimer(self)
        self.leave_debounce_timer.setSingleShot(True)
        self.leave_debounce_timer.setInterval(320)
        self.leave_debounce_timer.timeout.connect(self._do_retract)

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
        """
        Calculates window bounds anchored at top center screen.
        Called once before animation expands to avoid DWM flicker.
        """
        win_w = int(w + 40)
        win_h = int(y + h + 30)
        win_x = (self.screen_geo.width() - win_w) // 2
        self.setGeometry(win_x, 0, win_w, win_h)

    def _on_animation_finished(self):
        # When fully shrunk back to idle, resize window to stealth notch
        if self.current_state == "idle":
            self.set_window_bounds_for(self.IDLE_W, self.IDLE_H, self.IDLE_Y)

    def animate_to(self, target_w, target_h, target_y, new_state, easing=QEasingCurve.Type.OutBack, duration=420):
        prev_state = self.current_state
        self.current_state = new_state
        self.anim_group.stop()

        # If expanding, enlarge the transparent window surface immediately
        # so the pill can animate smoothly without clipping or resizing jitter
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
        """
        Proximity detector: checks if cursor is NEAR the notch.
        Completely eliminates edge-boundary glitching.
        """
        # During alert state, let commentary timer handle retreat unless user clicks
        if self.current_state == "alert":
            return

        cursor = QCursor.pos()
        cx = self.screen_geo.width() // 2
        dx = abs(cursor.x() - cx)
        dy = cursor.y()

        if self.current_state == "idle":
            # "Near" zone for idle: within 120px horizontally of center, and within 32px of screen top
            if dx <= 120 and dy <= 32:
                self.leave_debounce_timer.stop()
                self.animate_to(self.PEEK_W, self.PEEK_H, self.PEEK_Y, "peek", QEasingCurve.Type.OutBack, 380)

        elif self.current_state == "peek":
            # Keep peek open if cursor is near floating pill (within 180px horizontally, 75px vertically)
            if dx <= 180 and dy <= 75:
                self.leave_debounce_timer.stop()
            else:
                if not self.leave_debounce_timer.isActive():
                    self.leave_debounce_timer.start()

        elif self.current_state == "drawer":
            # Keep drawer open if cursor is anywhere near drawer (within 340px horizontally, 280px vertically)
            if dx <= 340 and dy <= 280:
                self.leave_debounce_timer.stop()
            else:
                if not self.leave_debounce_timer.isActive():
                    self.leave_debounce_timer.start()

    def _do_retract(self):
        if self.current_state in ["peek", "drawer"]:
            self.shrink_to_idle()

    def get_pill_rect(self):
        pill_x = (self.width() - self._island_w) / 2.0
        pill_y = float(self._island_y)
        return QRectF(pill_x, pill_y, float(self._island_w), float(self._island_h))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pill_rect = self.get_pill_rect()
            pos = event.position() if hasattr(event, 'position') else event.pos()
            
            if not pill_rect.contains(pos):
                return

            if self.current_state in ["idle", "peek"]:
                self.open_drawer()
            elif self.current_state == "alert":
                self.shrink_to_idle()
            elif self.current_state == "drawer":
                rel_x = pos.x() - pill_rect.left()
                rel_y = pos.y() - pill_rect.top()
                
                # Check clicks inside demo simulator row: y in [120, 160]
                if 120 <= rel_y <= 160:
                    bx = 24
                    for item in MOCK_EVENTS:
                        if bx <= rel_x <= bx + 108:
                            self.on_event_received(item)
                            return
                        bx += 116
                # Quit button in drawer
                elif rel_y > pill_rect.height() - 32 and rel_x > pill_rect.width() - 80:
                    QApplication.quit()

    def on_event_received(self, data):
        self.runs += data.get("runs", 0)
        self.wickets += data.get("wickets", 0)
        self.balls += 1
        self.badge = data.get("badge", "ACTION")
        self.context_info = data.get("context", "")
        self.commentary = data.get("commentary", "")

        # 1. Narrate witty cricket commentary via TTS
        self.audio.speak(self.commentary)

        # 2. Fluid drop-down spring expansion with floating gap
        self.animate_to(self.ALERT_W, self.ALERT_H, self.ALERT_Y, "alert", QEasingCurve.Type.OutBack, 460)

        # 3. Auto-retract back to stealth notch after 6.5s
        self.autohide_timer.start(6500)

    def shrink_to_idle(self):
        self.autohide_timer.stop()
        self.leave_debounce_timer.stop()
        self.animate_to(self.IDLE_W, self.IDLE_H, self.IDLE_Y, "idle", QEasingCurve.Type.OutCubic, 360)

    def open_drawer(self):
        self.autohide_timer.stop()
        self.leave_debounce_timer.stop()
        self.animate_to(self.DRAWER_W, self.DRAWER_H, self.DRAWER_Y, "drawer", QEasingCurve.Type.OutBack, 440)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        pill_rect = self.get_pill_rect()
        w = pill_rect.width()
        h = pill_rect.height()

        # Continuous Smooth Curvature:
        # Idle: small rounded cap at bezel
        # Peek: radius = h / 2 (continuous capsule/pill)
        # Alert: radius = 28px
        # Drawer: radius = 26px
        if self.current_state == "idle":
            radius = min(h / 2.0, 3.5)
        elif self.current_state == "peek":
            radius = h / 2.0
        else:
            radius = min(h / 2.0, 28.0)

        pill_path = QPainterPath()
        pill_path.addRoundedRect(pill_rect, radius, radius)

        # Ambient Floating Drop Shadow (when detached from bezel)
        if self._island_y > 4:
            for i in range(4):
                shadow_offset = (i + 1) * 1.5
                shadow_rect = pill_rect.adjusted(-i * 1.0, shadow_offset, i * 1.0, shadow_offset + i * 1.2)
                shadow_path = QPainterPath()
                shadow_path.addRoundedRect(shadow_rect, radius + i, radius + i)
                p.strokePath(shadow_path, QPen(QColor(0, 0, 0, 22 - i * 5), 1.6))

        # Core Obsidian Body (Pure Matte Deep Black)
        p.fillPath(pill_path, QColor(8, 8, 8, 252))

        # Frosted Specular Highlight Rim (Ultra-subtle, non-distracting)
        if self.current_state != "idle":
            p.strokePath(pill_path, QPen(QColor(255, 255, 255, 28), 1.0))

        # Render Content based on state
        if self.current_state == "idle":
            # Completely clean: NO text, NO icons, NO borders
            pass
        elif self.current_state == "peek":
            self.draw_peek(p, pill_rect)
        elif self.current_state == "alert":
            self.draw_alert(p, pill_rect)
        elif self.current_state == "drawer":
            self.draw_drawer(p, pill_rect)

    def draw_peek(self, p, r):
        # Crisp, clean typography on hover
        p.setPen(QColor(245, 245, 245))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        overs = f"{self.balls // 6}.{self.balls % 6}"
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, f"Claude XI  •  {self.runs}/{self.wickets}  ({overs} ov)")

    def draw_alert(self, p, r):
        # Frosted Badge Capsule
        bx = r.left() + 22
        by = r.top() + 14
        bw, bh = 118, 22
        badge_rect = QRectF(bx, by, bw, bh)

        p.setBrush(QColor(255, 255, 255, 24))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(badge_rect, 11, 11)

        p.setPen(QColor(255, 255, 255, 235))
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, self.badge)

        # Context Info (soft muted text)
        if self.context_info:
            p.setPen(QColor(160, 160, 160))
            p.setFont(QFont("Consolas", 8))
            p.drawText(int(bx + bw + 14), int(by + 15), self.context_info[:38])

        # Bold Crisp White Commentary Quote
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        q_rect = QRectF(r.left() + 22, r.top() + 44, r.width() - 44, 46)
        p.drawText(q_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, f'"{self.commentary}"')

    def draw_drawer(self, p, r):
        top = r.top()
        left = r.left()
        w = r.width()
        h = r.height()

        # Match Center Header
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.drawText(int(left + 24), int(top + 30), "CodeCast Match Center")

        overs = f"{self.balls // 6}.{self.balls % 6}"
        p.setPen(QColor(210, 210, 210))
        p.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        p.drawText(int(left + w - 120), int(top + 30), f"{self.runs}/{self.wickets} ({overs}ov)")

        # 3 Minimalist Stat Boxes
        cw = (w - 64) / 3.0
        stats = [
            ("RUNS", str(self.runs)),
            ("WICKETS", str(self.wickets)),
            ("OVERS", overs)
        ]
        for i, (title, val) in enumerate(stats):
            cx = left + 24 + i * (cw + 8)
            box_rect = QRectF(cx, top + 46, cw, 44)
            p.setBrush(QColor(255, 255, 255, 12))
            p.setPen(QColor(255, 255, 255, 18))
            p.drawRoundedRect(box_rect, 10, 10)

            p.setPen(QColor(140, 140, 140))
            p.setFont(QFont("Segoe UI", 7))
            p.drawText(QRectF(cx, top + 51, cw, 14), Qt.AlignmentFlag.AlignCenter, title)

            p.setPen(QColor(255, 255, 255))
            p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            p.drawText(QRectF(cx, top + 66, cw, 20), Qt.AlignmentFlag.AlignCenter, val)

        # Simulator Row
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(int(left + 24), int(top + 110), "Demo Simulator (Click to Trigger):")

        labels = ["Attack Shot", "Wicket", "3rd Umpire", "Huge Six", "Century"]
        bx = left + 24
        for i, item in enumerate(MOCK_EVENTS):
            rect = QRectF(bx, top + 122, 108, 30)
            p.setBrush(QColor(255, 255, 255, 15))
            p.setPen(QColor(255, 255, 255, 28))
            p.drawRoundedRect(rect, 8, 8)

            p.setPen(QColor(240, 240, 240))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, labels[i])
            bx += 116

        # Latest Commentary Line
        p.setPen(QColor(130, 130, 130))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(int(left + 24), int(top + 178), "Latest Commentary:")

        p.setPen(QColor(240, 240, 240))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        q_rect = QRectF(left + 24, top + 194, w - 100, 36)
        p.drawText(q_rect, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, f'"{self.commentary or "Awaiting delivery..."}"')

        # Quit Button
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(int(left + w - 65), int(top + h - 16), "[Quit ✕]")

def main():
    app = QApplication(sys.argv)
    notch = FloatingDynamicNotch()
    notch.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
