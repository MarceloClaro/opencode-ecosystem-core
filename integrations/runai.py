# -*- coding: utf-8 -*-
"""
RunAI Provisioner — Ponte opcional para provisionamento local via canirun.ai
============================================================================

Escopo honesto: o `runai` é tratado aqui como um provisionador/launcher de
modelos locais via CLI (`doctor`, `pull`, `run`), NÃO como um provider HTTP de
completude. O objetivo é reduzir fricção de onboarding e seleção manual de
quantização GGUF/llama.cpp por hardware.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


PROVIDER_ID = "runai"
RUNAI_BIN = os.environ.get("RUNAI_BIN", "runai")

# Catálogo mínimo curado para o ecossistema. Não é espelho da canirun.ai.
MODELS: Dict[str, Dict[str, Any]] = {
    "qwen3.5-4b": {
        "name": "Qwen 3.5 4B",
        "provider": PROVIDER_ID,
        "family": "qwen",
        "strengths": ["coding", "local", "lightweight"],
        "tier": "standard",
        "free": True,
    },
    "gemma4-e2b-it": {
        "name": "Gemma 4 E2B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "local", "standard"],
        "tier": "standard",
        "free": True,
    },
    "phi-4-mini-reasoning": {
        "name": "Phi-4 Mini Reasoning",
        "provider": PROVIDER_ID,
        "family": "microsoft",
        "strengths": ["reasoning", "math", "local", "lightweight"],
        "tier": "fast",
        "free": True,
    },
}


@dataclass
class RunAIProvisioner:
    """Bridge seguro para a CLI `runai`."""

    binary: str = RUNAI_BIN
    timeout: float = 300.0

    def is_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def _run_cli(self, args: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "ok": False,
                "exit_code": 127,
                "stdout": "",
                "stderr": (
                    "CLI 'runai' não encontrada no PATH. Instale com: "
                    "curl -fsSL https://canirun.ai/runai/install.sh | bash"
                ),
                "command": [self.binary] + list(args),
            }
        try:
            completed = subprocess.run(
                [self.binary] + list(args),
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                check=False,
            )
            return {
                "ok": completed.returncode == 0,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "command": [self.binary] + list(args),
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "exit_code": 124,
                "stdout": exc.stdout or "",
                "stderr": (exc.stderr or "") + "\nTimeout ao executar runai.",
                "command": [self.binary] + list(args),
            }
        except Exception as exc:  # pragma: no cover - defesa final
            return {
                "ok": False,
                "exit_code": 1,
                "stdout": "",
                "stderr": str(exc),
                "command": [self.binary] + list(args),
            }

    def doctor(self) -> Dict[str, Any]:
        return self._run_cli(["doctor"], timeout=60.0)

    def pull(self, model_id: str) -> Dict[str, Any]:
        return self._run_cli(["pull", model_id], timeout=self.timeout)

    def run(self, model_id: str) -> Dict[str, Any]:
        """Lança `runai run <model_id>` em subprocesso best-effort.

        Não assume protocolo HTTP nem parsing de saída estruturada. Apenas lança
        o processo e retorna PID/comando, ou erro imediato.
        """
        if not self.is_available():
            return self._run_cli(["run", model_id], timeout=5.0)
        try:
            proc = subprocess.Popen(  # noqa: S603 - args controlados pelo código
                [self.binary, "run", model_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return {
                "ok": True,
                "pid": proc.pid,
                "command": [self.binary, "run", model_id],
                "provider": PROVIDER_ID,
                "model": model_id,
                "launched": True,
            }
        except Exception as exc:
            return {
                "ok": False,
                "exit_code": 1,
                "stderr": str(exc),
                "command": [self.binary, "run", model_id],
                "launched": False,
            }

    def list_models(self) -> List[Dict[str, Any]]:
        return [dict({"id": model_id}, **meta) for model_id, meta in MODELS.items()]

    def model_info(self, model_id: str) -> Dict[str, Any]:
        meta = MODELS.get(model_id)
        if meta is None:
            return {
                "id": model_id,
                "known": False,
                "provider": PROVIDER_ID,
                "note": "Modelo fora do catálogo curado local; o runai pode suportá-lo mesmo assim.",
            }
        return dict({"id": model_id, "known": True}, **meta)

    def health_check(self) -> Dict[str, Any]:
        available = self.is_available()
        result = self.doctor() if available else {
            "ok": False,
            "exit_code": 127,
            "stdout": "",
            "stderr": "runai ausente",
            "command": [self.binary, "doctor"],
        }
        return {
            "provider": PROVIDER_ID,
            "available": available,
            "binary": self.binary,
            "catalog_models": list(MODELS.keys()),
            "doctor_ok": bool(result.get("ok")),
            "doctor_exit_code": result.get("exit_code"),
        }

    def provider_info(self) -> Dict[str, Any]:
        return {
            "provider_id": PROVIDER_ID,
            "binary": self.binary,
            "available": self.is_available(),
            "catalog_models": len(MODELS),
            "scope": "provisionamento/launcher CLI local (não HTTP provider)",
            "supported_commands": ["doctor", "pull", "run"],
        }


runai_provisioner = RunAIProvisioner()
