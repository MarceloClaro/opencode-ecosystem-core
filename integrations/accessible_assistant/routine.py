"""R1063 — gravador de rotina acessível: eventos de janela + voz, sem pixels/áudio bruto."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from . import dialog, memory, voice, windows_uia


class RoutineRecorder:
    def __init__(self, interval_seconds: int = 10, memory_store: memory.ActivityMemory | None = None,
                 config: dict | None = None):
        self.interval = max(5, min(int(interval_seconds), 60))
        self.memory = memory_store or memory.ActivityMemory(ttl_hours=24)
        self.config = config or windows_uia.load_config()

    def capture_window(self) -> dict:
        try:
            focused = windows_uia.focused(self.config)
            window = focused["data"]["window"]
            data = windows_uia.read(window, self.config)
            names = [item.get("name", "") for item in data.get("data", []) if item.get("name")][:8]
            entry = self.memory.append("activity", "", window=window,
                                        focused=focused["data"].get("name", ""),
                                        elements=names)
            return {"ok": True, "window": window, "elements": len(names), "entry": entry}
        except windows_uia.UIAError as exc:
            return {"ok": False, "code": exc.code, "message": exc.message}

    def capture_voice(self, seconds: int = 5) -> dict:
        try:
            path = voice.record(seconds)
            if not voice.has_speech(path):
                return {"ok": True, "speech": False}
            text = voice.transcribe(path)
            if not text:
                return {"ok": True, "speech": False}
            self.memory.append("voice", text)
            return {"ok": True, "speech": True, "text": text,
                    "command": dialog.parse_command(text)}
        except voice.VoiceError as exc:
            return {"ok": False, "code": exc.code, "message": exc.message}

    def step(self, voice_seconds: int = 5) -> dict:
        window = self.capture_window()
        speech = self.capture_voice(voice_seconds)
        return {"window": window, "voice": speech,
                "at": datetime.now(timezone.utc).isoformat()}

    def run(self, hours: float = 24.0, voice_seconds: int = 5) -> dict:
        deadline = time.monotonic() + max(0.1, min(float(hours), 72.0)) * 3600
        steps = 0
        while time.monotonic() < deadline:
            result = self.step(voice_seconds)
            steps += 1
            if steps % 100 == 0:
                self.memory.prune()
            command = (result.get("voice") or {}).get("command") or {}
            if command.get("intent") == "stop":
                return {"ok": True, "stopped": True, "steps": steps,
                        "reason": "voice_stop"}
            time.sleep(self.interval)
        self.memory.prune()
        return {"ok": True, "stopped": False, "steps": steps,
                "hours": round(min(float(hours), 72.0), 2)}
