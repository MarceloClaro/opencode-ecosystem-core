"""R1063: assistente acessível; testa ponte, memória e comandos sem voz real."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.accessible_assistant import dialog, memory, opencode_gateway, voice, windows_uia


def test_window_allowlist_and_denylist():
    config = windows_uia.load_config()
    assert windows_uia.window_allowed(config, "push_repo.ps1 - Bloco de notas")
    assert not windows_uia.window_allowed(config, "OC | Implement skill")
    assert windows_uia.window_readable(config, "OC | Implement skill")
    assert not windows_uia.window_allowed(config, "Banco do Brasil")


def test_unallowed_window_is_denied_before_powershell(monkeypatch):
    monkeypatch.setattr(windows_uia, "_powershell", lambda command, config, **kwargs: {
        "ok": True, "data": [{"name": "Banco do Brasil"}]})
    with pytest.raises(windows_uia.UIAError) as exc:
        windows_uia.snapshot("Banco do Brasil")
    assert exc.value.code == "WINDOW_NOT_ALLOWED"


def test_click_requires_confirmation(monkeypatch):
    monkeypatch.setattr(windows_uia, "_resolve_window", lambda config, window, write=True: window)
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

    monkeypatch.setattr(windows_uia, "_resolve_window", lambda config, window, write=True: window)
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


def test_terminal_is_read_only_not_writable(monkeypatch):
    config = windows_uia.load_config()
    assert windows_uia.window_readable(config, "OC | Implement skill")
    assert not windows_uia.window_allowed(config, "OC | Implement skill")
    assert windows_uia.window_allowed(config, "Bloco de notas")


def test_parse_ask_command():
    command = dialog.parse_command("Core, perguntar como está o sistema")
    assert command == {"intent": "ask", "text": "como está o sistema"}


def test_opencode_gateway_parses_jsonl_and_disallows_auto(monkeypatch, tmp_path):
    class Result:
        returncode = 0
        stderr = ""
        stdout = "\n".join([
            json.dumps({"type": "step_start", "sessionID": "ses_teste"}),
            json.dumps({"type": "text", "sessionID": "ses_teste",
                        "part": {"type": "text", "text": "resposta sk-1234567890abcdefghij"}}),
        ])

    calls = []
    monkeypatch.setenv("OPENCODE_BIN", "/bin/echo")
    monkeypatch.setattr(opencode_gateway.subprocess, "run",
                        lambda argv, **kwargs: (calls.append(argv), Result())[1])
    result = opencode_gateway.ask("qual é?", state_dir=tmp_path)
    assert result["text"] == "resposta [REDACTED_API_KEY]"
    assert result["sessionID"] == "ses_teste"
    assert "--auto" not in calls[0]
    assert calls[0][calls[0].index("--agent") + 1] == "plan"


def test_opencode_gateway_rejects_unlisted_agent(tmp_path):
    with pytest.raises(opencode_gateway.GatewayError) as exc:
        opencode_gateway.ask("oi", agent="build", state_dir=tmp_path)
    assert exc.value.code == "AGENT_NOT_ALLOWED"


def test_opencode_gateway_rejects_empty(tmp_path):
    with pytest.raises(opencode_gateway.GatewayError):
        opencode_gateway.ask("  ", state_dir=tmp_path)
