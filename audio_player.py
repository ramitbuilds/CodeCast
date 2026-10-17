"""
CodeCast Native Audio Player
Handles ElevenLabs TTS generation and PyQt6 Multimedia playback with Windows TTS fallback.
"""

import os
import sys
import json
import tempfile
import urllib.request
import threading
from PyQt6.QtCore import QUrl, QObject, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class AudioPlayer(QObject):
    speech_started = pyqtSignal()
    speech_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        self.is_playing = False
        self.is_muted = False
        self.queue = []

        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.player.stop()
        return self.is_muted

    def speak(self, text):
        if self.is_muted or not text:
            return
        threading.Thread(target=self._process_speech, args=(text,), daemon=True).start()

    def _process_speech(self, text):
        api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb").strip()

        if api_key:
            try:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": api_key
                }
                data = json.dumps({
                    "text": text,
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.45,
                        "similarity_boost": 0.85
                    }
                }).encode("utf-8")

                req = urllib.request.Request(url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    audio_bytes = resp.read()
                    temp_file = os.path.join(tempfile.gettempdir(), f"codecast_{os.getpid()}.mp3")
                    with open(temp_file, "wb") as f:
                        f.write(audio_bytes)
                    self._play_file(temp_file)
                    return
            except Exception as e:
                pass

        # Windows speech fallback
        self._fallback_windows_speech(text)

    def _play_file(self, file_path):
        if self.is_muted:
            return
        self.speech_started.emit()
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()

    def _fallback_windows_speech(self, text):
        if self.is_muted:
            return
        try:
            self.speech_started.emit()
            clean_text = text.replace('"', '').replace("'", "")
            cmd = f'powershell -WindowStyle Hidden -NoProfile -Command "(New-Object -ComObject SAPI.SpVoice).Speak(\'{clean_text}\')"'
            os.system(cmd)
        finally:
            self.speech_finished.emit()

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.speech_finished.emit()
