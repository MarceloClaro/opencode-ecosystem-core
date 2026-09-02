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
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


PROVIDER_ID = "runai"
RUNAI_BIN = os.environ.get("RUNAI_BIN", "runai")
NPM_PACKAGE_URL = "https://registry.npmjs.org/@canirun%2Frunai"

# Catálogo mínimo curado para o ecossistema. Não é espelho da canirun.ai.
MODEL_ALIASES: Dict[str, str] = {
    # aliases internos/ecossistema -> ids runai conhecidos
    "qwen-3-4B-it": "qwen3.5-4b",
    "qwen3.5-4b": "qwen3.5-4b",
    "gemma-4-E2B-it": "gemma4-e2b-it",
    "gemma4-e2b-it": "gemma4-e2b-it",
    "phi-4-mini-reasoning": "phi-4-mini-reasoning",
}

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
    cwd: Optional[str] = None

    def is_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def resolve_model_id(self, model_id: str) -> str:
        return MODEL_ALIASES.get(model_id, model_id)

    def installer_diagnosis(self) -> Dict[str, Any]:
        """Diagnóstico upstream do pacote documentado pelo instalador.

        Não instala nada. Apenas verifica se o endpoint npm documentado existe.
        Isso permite diferenciar “runai ausente localmente” de “instalador aponta
        para pacote inexistente/indisponível”.
        """
        try:
            with urllib.request.urlopen(NPM_PACKAGE_URL, timeout=10) as resp:
                return {
                    "ok": resp.status == 200,
                    "status_code": resp.status,
                    "package_url": NPM_PACKAGE_URL,
                    "detail": "Pacote npm documentado respondeu com sucesso.",
                }
        except urllib.error.HTTPError as exc:
            return {
                "ok": False,
                "status_code": exc.code,
                "package_url": NPM_PACKAGE_URL,
                "detail": f"Pacote npm documentado indisponível (HTTP {exc.code}).",
            }
        except Exception as exc:  # pragma: no cover - rede/ambiente
            return {
                "ok": False,
                "status_code": None,
                "package_url": NPM_PACKAGE_URL,
                "detail": f"Não foi possível validar o pacote npm documentado: {exc}",
            }

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
                cwd=self.cwd,
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

    def help(self) -> Dict[str, Any]:
        # muitos CLIs retornam 0 em --help; caso contrário ainda devolvemos stdout/stderr.
        return self._run_cli(["--help"], timeout=30.0)

    def version(self) -> Dict[str, Any]:
        # Não assumimos uma flag única. Tentamos --version e fallback version.
        result = self._run_cli(["--version"], timeout=30.0)
        if result.get("ok"):
            result["parsed_version"] = self._extract_version(result.get("stdout", "") or result.get("stderr", ""))
            return result
        alt = self._run_cli(["version"], timeout=30.0)
        alt["parsed_version"] = self._extract_version(alt.get("stdout", "") or alt.get("stderr", ""))
        return alt

    @staticmethod
    def _extract_version(text: str) -> str:
        match = re.search(r"\b(\d+\.\d+(?:\.\d+)?)\b", text or "")
        return match.group(1) if match else ""

    def pull(self, model_id: str) -> Dict[str, Any]:
        return self._run_cli(["pull", self.resolve_model_id(model_id)], timeout=self.timeout)

    def run(self, model_id: str) -> Dict[str, Any]:
        """Lança `runai run <model_id>` em subprocesso best-effort.

        Não assume protocolo HTTP nem parsing de saída estruturada. Apenas lança
        o processo e retorna PID/comando, ou erro imediato.
        """
        resolved = self.resolve_model_id(model_id)
        if not self.is_available():
            return self._run_cli(["run", resolved], timeout=5.0)
        try:
            proc = subprocess.Popen(  # noqa: S603 - args controlados pelo código
                [self.binary, "run", resolved],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.cwd,
            )
            return {
                "ok": True,
                "pid": proc.pid,
                "command": [self.binary, "run", resolved],
                "provider": PROVIDER_ID,
                "model": resolved,
                "requested_model": model_id,
                "launched": True,
            }
        except Exception as exc:
            return {
                "ok": False,
                "exit_code": 1,
                "stderr": str(exc),
                "command": [self.binary, "run", resolved],
                "launched": False,
            }

    def list_models(self) -> List[Dict[str, Any]]:
        return [dict({"id": model_id}, **meta) for model_id, meta in MODELS.items()]

    def model_info(self, model_id: str) -> Dict[str, Any]:
        resolved = self.resolve_model_id(model_id)
        meta = MODELS.get(resolved)
        if meta is None:
            return {
                "id": resolved,
                "requested_model": model_id,
                "known": False,
                "provider": PROVIDER_ID,
                "note": "Modelo fora do catálogo curado local; o runai pode suportá-lo mesmo assim.",
            }
        return dict({"id": resolved, "requested_model": model_id, "known": True}, **meta)

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
            "aliases": dict(MODEL_ALIASES),
            "doctor_ok": bool(result.get("ok")),
            "doctor_exit_code": result.get("exit_code"),
            "installer": self.installer_diagnosis() if not available else {"ok": True, "detail": "Binário local encontrado; diagnóstico upstream opcional."},
        }

    def provider_info(self) -> Dict[str, Any]:
        return {
            "provider_id": PROVIDER_ID,
            "binary": self.binary,
            "available": self.is_available(),
            "catalog_models": len(MODELS),
            "model_aliases": dict(MODEL_ALIASES),
            "scope": "provisionamento/launcher CLI local (não HTTP provider)",
            "supported_commands": ["doctor", "pull", "run", "--help", "--version|version"],
            "installer_package_url": NPM_PACKAGE_URL,
        }


runai_provisioner = RunAIProvisioner()
