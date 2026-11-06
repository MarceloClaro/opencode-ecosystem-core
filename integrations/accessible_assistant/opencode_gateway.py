"""R1063 — gateway de voz para o OpenCode via CLI, sem teclado na TUI."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from integrations.desktop_operator import runtime

from . import windows_uia

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATE = Path("~/.local/state/opencode-accessible-assistant").expanduser()
MAX_PROMPT = 4000


class GatewayError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _binary() -> str:
    return os.environ.get("OPENCODE_BIN") or shutil.which("opencode") or ""


def _session_path(state_dir: Path) -> Path:
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "opencode_session.txt"


def ask(prompt: str, *, agent: str = "plan", state_dir: str | Path | None = None,
        new_session: bool = False, timeout: int = 180) -> dict:
    if not isinstance(prompt, str) or not prompt.strip():
        raise GatewayError("PROMPT_REQUIRED", "pergunta vazia")
    if len(prompt.encode("utf-8")) > MAX_PROMPT:
        raise GatewayError("PROMPT_TOO_LARGE", "pergunta acima de 4000 bytes")
    if not isinstance(agent, str) or not agent or len(agent) > 80:
        raise GatewayError("AGENT_INVALID", "agente inválido")
    allowed_agents = windows_uia.load_config().get("opencode_agents", ["plan"])
    if agent not in allowed_agents:
        raise GatewayError("AGENT_NOT_ALLOWED", "agente fora da allowlist")
    binary = _binary()
    if not binary:
        raise GatewayError("OPENCODE_NOT_FOUND", "CLI opencode não encontrada")
    state = Path(state_dir or DEFAULT_STATE).expanduser()
    session_file = _session_path(state)
    session = None if new_session else (session_file.read_text().strip() if session_file.is_file() else "")
    argv = [binary, "run", "--format", "json", "--agent", agent]
    if session:
        argv += ["--session", session]
    argv.append(prompt.strip())
    try:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                                timeout=max(30, min(int(timeout), 600)), shell=False, check=False)
    except subprocess.TimeoutExpired as exc:
        raise GatewayError("TIMEOUT", "OpenCode excedeu o tempo") from exc
    except OSError as exc:
        raise GatewayError("EXEC_FAILED", "falha ao executar OpenCode") from exc
    texts = []
    session_id = session or ""
    for line in (result.stdout or "").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("sessionID"):
            session_id = event["sessionID"]
        part = event.get("part") or {}
        if event.get("type") == "text" and part.get("type") == "text" and part.get("text"):
            texts.append(part["text"])
    if result.returncode != 0 and not texts:
        raise GatewayError("OPENCODE_FAILED", (result.stderr or result.stdout or "falha")[-1000:])
    if session_id:
        session_file.write_text(str(session_id))
    answer = runtime.redact_payload("\n".join(texts).strip())
    return {"ok": True, "text": answer, "sessionID": session_id or None,
            "agent": agent, "events": len(texts), "external_validation": False}
