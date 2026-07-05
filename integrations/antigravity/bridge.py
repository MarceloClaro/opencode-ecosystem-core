# -*- coding: utf-8 -*-
"""
Antigravity Bridge — Integração com o Antigravity CLI (SPEC-046)
================================================================
Porte Python do antigravity-bridge.ts do OpenCode_Ecosystem original.
Permite ao orquestrador marceloclaro delegar tarefas a agentes externos
via Antigravity CLI (Google), com detecção automática de disponibilidade
e fila de handoff em arquivos quando o CLI não está instalado.

Fluxo:
    bridge = AntigravityBridge()
    if bridge.available:
        result = bridge.delegate("gerar imagem do diagrama", agent="image")
    else:
        bridge.enqueue_handoff(task)   # fila .antigravity/queue/*.json
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from typing import Any, Dict, List, Optional

QUEUE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".antigravity", "queue",
)

# Capacidades expostas pelo Antigravity CLI (SPEC-046)
ANTIGRAVITY_CAPABILITIES = [
    "parallel_orchestration",
    "external_agent_delegation",
    "image_generation",
    "browser_automation",
]


class AntigravityBridge:
    """Ponte entre o orquestrador marceloclaro e o Antigravity CLI."""

    def __init__(self, cli_command: str = "antigravity"):
        self.cli_command = cli_command
        self.available = shutil.which(cli_command) is not None

    def delegate(self, prompt: str, agent: str = "default",
                 timeout: int = 300) -> Dict[str, Any]:
        """Delega uma tarefa ao Antigravity CLI (modo síncrono)."""
        if not self.available:
            handoff = self.enqueue_handoff({"prompt": prompt, "agent": agent})
            return {
                "status": "queued",
                "reason": "Antigravity CLI não instalado — handoff enfileirado",
                "handoff_file": handoff,
            }
        try:
            proc = subprocess.run(
                [self.cli_command, "run", "--agent", agent, "--prompt", prompt],
                capture_output=True, text=True, timeout=timeout,
            )
            return {
                "status": "completed" if proc.returncode == 0 else "failed",
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-1000:],
                "returncode": proc.returncode,
            }
        except (subprocess.TimeoutExpired, OSError) as exc:
            return {"status": "error", "error": str(exc)}

    def enqueue_handoff(self, task: Dict[str, Any]) -> str:
        """Enfileira handoff em arquivo JSON para consumo posterior pelo CLI."""
        os.makedirs(QUEUE_DIR, exist_ok=True)
        handoff = {
            "id": f"ag-{uuid.uuid4().hex[:8]}",
            "created_at": time.time(),
            "source": "marceloclaro-orchestrator",
            "capabilities_requested": ANTIGRAVITY_CAPABILITIES,
            "task": task,
        }
        path = os.path.join(QUEUE_DIR, f"{handoff['id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(handoff, f, ensure_ascii=False, indent=2)
        return path

    def pending_handoffs(self) -> List[Dict[str, Any]]:
        if not os.path.isdir(QUEUE_DIR):
            return []
        items = []
        for name in sorted(os.listdir(QUEUE_DIR)):
            if name.endswith(".json"):
                try:
                    with open(os.path.join(QUEUE_DIR, name), "r", encoding="utf-8") as f:
                        items.append(json.load(f))
                except (OSError, json.JSONDecodeError):
                    continue
        return items

    def status(self) -> Dict[str, Any]:
        return {
            "cli_available": self.available,
            "cli_command": self.cli_command,
            "capabilities": ANTIGRAVITY_CAPABILITIES,
            "pending_handoffs": len(self.pending_handoffs()),
        }


# Singleton
antigravity_bridge = AntigravityBridge()
