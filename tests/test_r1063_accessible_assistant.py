"""R1063: assistente acessível; testa ponte, memória e comandos sem voz real."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.accessible_assistant import dialog, memory, voice, windows_uia


def test_window_allowlist_and_denylist():
    config = windows_uia.load_config()
    assert windows_uia.window_allowed(config, "push_repo.ps1 - Bloco de notas")
    assert not windows_uia.window_allowed(config, "OC | Implement skill")
    assert not windows_uia.window_allowed(config, "Banco do Brasil")


def test_unallowed_window_is_denied_before_powershell(monkeypatch):
    monkeypatch.setattr(windows_uia, "_powershell", lambda command, config, **kwargs: {
        "ok": True, "data": [{"name": "OC | Implement skill"}]})
    with pytest.raises(windows_uia.UIAError) as exc:
        windows_uia.snapshot("OC | Implement skill")
    assert exc.value.code == "WINDOW_NOT_ALLOWED"


def test_click_requires_confirmation(monkeypatch):
    monkeypatch.setattr(windows_uia, "_resolve_window", lambda config, window: window)
    with pytest.raises(windows_uia.UIAError) as exc:
        windows_uia.invoke("Bloco de notas", "Salvar", confirmed=False)
    assert exc.value.code == "CONFIRMATION_REQUIRED"


def test_uia_output_is_redacted(monkeypatch):
    class Result:
        returncode = 0
        stderr = ""
        stdout = json.dumps({
            "ok": True,
            "command": "read",
            "data": [{"name": "sk-1234567890abcdefghij", "type": "ControlType.Text"}],
        })

    monkeypatch.setattr(windows_uia, "_resolve_window", lambda config, window: window)
    monkeypatch.setattr(windows_uia.subprocess, "run", lambda *a, **k: Result())
    result = windows_uia.read("Bloco de notas")
    assert "sk-1234567890abcdefghij" not in json.dumps(result)
    assert "REDACTED" in json.dumps(result)


def test_memory_is_encrypted_and_ttl_prunes(tmp_path):
    state = tmp_path / "state"
    mem = memory.ActivityMemory(state, ttl_hours=24, now=1000)
    mem.append("voice", "segredo pessoal", window="Bloco de notas")
    raw = (state / "activity.jsonl").read_text()
    assert "segredo pessoal" not in raw
    assert mem.summary()["entries"] == 1
    later = memory.ActivityMemory(state, ttl_hours=24, now=1000 + 25 * 3600)
    assert later.prune() == 0
    assert later.summary()["entries"] == 0


def test_memory_forget(tmp_path):
    state = tmp_path / "state"
    mem = memory.ActivityMemory(state, now=1000)
    mem.append("voice", "olá")
    assert mem.forget()["forgotten"] is True
    assert not (state / "activity.jsonl").exists()


def test_voice_record_command_uses_microphone():
    argv = voice.record_command(Path("/tmp/x.wav"), 5)
    assert argv[0] == "parecord"
    assert any("RDPSource" in arg for arg in argv)
    assert "/tmp/x.wav" in argv


def test_voice_rejects_empty_text():
    with pytest.raises(voice.VoiceError):
        voice.speak("   ")


def test_parse_voice_commands():
    assert dialog.parse_command("Core, o que está na tela?")["intent"] == "read"
    assert dialog.parse_command("Core, clicar em Salvar") == {"intent": "click", "target": "Salvar"}
    assert dialog.parse_command("Core, escrever bom dia") == {"intent": "write", "text": "bom dia"}
    assert dialog.parse_command("Core, parar")["intent"] == "stop"
    assert dialog.parse_command("qualquer conversa")["intent"] == "ambient"


def test_confirmation_words():
    assert dialog.is_confirmation("sim, pode")
    assert dialog.is_confirmation("confirmo")
    assert dialog.is_denial("não, cancelar")


def test_has_speech_on_silence(tmp_path):
    import wave
    import numpy as np
    path = tmp_path / "silence.wav"
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(16000)
        stream.writeframes(np.zeros(16000, dtype=np.int16).tobytes())
    assert voice.has_speech(path) is False
