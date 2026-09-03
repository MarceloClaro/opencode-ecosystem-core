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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


PROVIDER_ID = "runai"
RUNAI_BIN = os.environ.get("RUNAI_BIN", "runai")
NPM_PACKAGE_URL = "https://registry.npmjs.org/@canirun%2Frunai"
SOURCE_REPOSITORY_URL = "https://github.com/midudev/canirun.ai"

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
    source_dir: str = field(default_factory=lambda: os.environ.get("RUNAI_SOURCE_DIR", ""))
    bun_binary: str = field(default_factory=lambda: os.environ.get("RUNAI_BUN_BIN", "bun"))
    pnpm_binary: str = field(default_factory=lambda: os.environ.get("RUNAI_PNPM_BIN", "pnpm"))

    def _resolve_command(self, preferred: str, fallback_name: str, candidates: Optional[List[str]] = None) -> str:
        candidates = candidates or []
        if preferred:
            expanded = os.path.expanduser(preferred)
            if os.path.isabs(expanded) and os.path.exists(expanded):
                return expanded
            found = shutil.which(preferred)
            if found:
                return found
        found = shutil.which(fallback_name)
        if found:
            return found
        for candidate in candidates:
            expanded = os.path.expanduser(candidate)
            if os.path.exists(expanded):
                return expanded
        return ""

    def bun_path(self) -> str:
        return self._resolve_command(
            self.bun_binary,
            "bun",
            ["~/.bun/bin/bun"],
        )

    def pnpm_path(self) -> str:
        return self._resolve_command(
            self.pnpm_binary,
            "pnpm",
            ["~/.local/share/pnpm/bin/pnpm", "~/Library/pnpm/pnpm"],
        )

    def is_binary_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def source_root(self) -> str:
        root = os.path.expanduser(self.source_dir or "").strip()
        if not root:
            return ""
        root = os.path.abspath(root)
        if os.path.isfile(os.path.join(root, "packages", "runai", "package.json")):
            return root
        return ""

    def has_source_checkout(self) -> bool:
        return bool(self.source_root())

    def source_dependencies_installed(self) -> bool:
        root = self.source_root()
        if not root:
            return False
        return os.path.isdir(os.path.join(root, "node_modules"))

    def source_build_ready(self) -> bool:
        root = self.source_root()
        if not root:
            return False
        return (
            os.path.isdir(os.path.join(root, "packages", "compatibility", "dist"))
            and os.path.isdir(os.path.join(root, "packages", "models", "dist"))
        )

    def is_source_available(self) -> bool:
        return bool(
            self.has_source_checkout()
            and self.bun_path()
            and self.pnpm_path()
            and self.source_dependencies_installed()
        )

    def runtime_mode(self) -> str:
        if self.is_binary_available():
            return "binary"
        if self.is_source_available():
            return "source"
        return "unavailable"

    def is_available(self) -> bool:
        return self.runtime_mode() != "unavailable"

    def resolve_model_id(self, model_id: str) -> str:
        return MODEL_ALIASES.get(model_id, model_id)

    def source_diagnosis(self) -> Dict[str, Any]:
        root = self.source_root()
        return {
            "detected": bool(root),
            "source_dir": root,
            "bun_path": self.bun_path(),
            "pnpm_path": self.pnpm_path(),
            "dependencies_installed": self.source_dependencies_installed(),
            "build_ready": self.source_build_ready(),
            "ready": self.is_source_available(),
            "repository": SOURCE_REPOSITORY_URL,
        }

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
                "repository": SOURCE_REPOSITORY_URL,
                "detail": "Pacote npm documentado respondeu com sucesso.",
            }
        except urllib.error.HTTPError as exc:
            return {
                "ok": False,
                "status_code": exc.code,
                "package_url": NPM_PACKAGE_URL,
                "repository": SOURCE_REPOSITORY_URL,
                "detail": f"Pacote npm documentado indisponível (HTTP {exc.code}).",
            }
        except Exception as exc:  # pragma: no cover - rede/ambiente
            return {
                "ok": False,
                "status_code": None,
                "package_url": NPM_PACKAGE_URL,
                "repository": SOURCE_REPOSITORY_URL,
                "detail": f"Não foi possível validar o pacote npm documentado: {exc}",
            }

    def _source_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        path_parts = []
        bun_path = self.bun_path()
        pnpm_path = self.pnpm_path()
        if bun_path:
            path_parts.append(os.path.dirname(bun_path))
        if pnpm_path:
            path_parts.append(os.path.dirname(pnpm_path))
        current = env.get("PATH", "")
        env["PATH"] = ":".join([p for p in path_parts if p] + ([current] if current else []))
        env.setdefault("RUNAI_TELEMETRY_DISABLED", "1")
        return env

    def _ensure_source_ready(self) -> Dict[str, Any]:
        if not self.has_source_checkout():
            return {
                "ok": False,
                "detail": "RUNAI_SOURCE_DIR não aponta para um checkout válido do repositório canirun.ai.",
            }
        if not self.bun_path() or not self.pnpm_path():
            return {
                "ok": False,
                "detail": "Modo source requer Bun e pnpm disponíveis no ambiente.",
            }
        if not self.source_dependencies_installed():
            return {
                "ok": False,
                "detail": "Checkout detectado, mas dependências não instaladas. Rode 'pnpm install' na raiz do checkout.",
            }
        if self.source_build_ready():
            return {"ok": True, "detail": "Workspace runai pronto."}
        try:
            build = subprocess.run(
                [self.pnpm_path(), "packages:build"],
                capture_output=True,
                text=True,
                timeout=max(self.timeout, 600.0),
                check=False,
                cwd=self.source_root(),
                env=self._source_env(),
            )
            if build.returncode == 0 and self.source_build_ready():
                return {"ok": True, "detail": "Workspace runai preparado via packages:build."}
            return {
                "ok": False,
                "detail": "Falha ao preparar o workspace runai via packages:build.",
                "stdout": build.stdout,
                "stderr": build.stderr,
                "exit_code": build.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "detail": "Timeout ao preparar o workspace runai via packages:build.",
            }

    def _run_source_cli(self, args: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        prepared = self._ensure_source_ready()
        if not prepared.get("ok"):
            return {
                "ok": False,
                "exit_code": 2,
                "stdout": prepared.get("stdout", ""),
                "stderr": prepared.get("detail", "") + (
                    ("\n" + prepared.get("stderr", "")) if prepared.get("stderr") else ""
                ),
                "command": [self.pnpm_path() or self.pnpm_binary, "--filter", "@canirun/runai", "run", "dev", "--"] + list(args),
                "mode": "source",
            }
        command = [self.pnpm_path(), "--filter", "@canirun/runai", "run", "dev", "--"] + list(args)
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                check=False,
                cwd=self.source_root(),
                env=self._source_env(),
            )
            return {
                "ok": completed.returncode == 0,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "command": command,
                "mode": "source",
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "exit_code": 124,
                "stdout": exc.stdout or "",
                "stderr": (exc.stderr or "") + "\nTimeout ao executar runai (source mode).",
                "command": command,
                "mode": "source",
            }

    def _run_cli(self, args: List[str], timeout: Optional[float] = None) -> Dict[str, Any]:
        if self.runtime_mode() == "source":
            return self._run_source_cli(args, timeout=timeout)
        if not self.is_binary_available():
            return {
                "ok": False,
                "exit_code": 127,
                "stdout": "",
                "stderr": (
                    "CLI 'runai' não encontrada no PATH. Instale com: "
                    "curl -fsSL https://canirun.ai/runai/install.sh | bash. "
                    "Se o npm estiver inconsistente, use o checkout-fonte em "
                    "RUNAI_SOURCE_DIR (repo canirun.ai)."
                ),
                "command": [self.binary] + list(args),
                "mode": "unavailable",
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
                "mode": "binary",
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "exit_code": 124,
                "stdout": exc.stdout or "",
                "stderr": (exc.stderr or "") + "\nTimeout ao executar runai.",
                "command": [self.binary] + list(args),
                "mode": "binary",
            }
        except Exception as exc:  # pragma: no cover - defesa final
            return {
                "ok": False,
                "exit_code": 1,
                "stdout": "",
                "stderr": str(exc),
                "command": [self.binary] + list(args),
                "mode": "binary",
            }

    def doctor(self, json_mode: bool = False) -> Dict[str, Any]:
        args = ["doctor"]
        if json_mode:
            args.append("--json")
        return self._run_cli(args, timeout=60.0)

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

    def browse(self, query: str = "", limit: Optional[int] = None, json_mode: bool = True) -> Dict[str, Any]:
        args = ["browse"]
        if query:
            args.append(query)
        if limit is not None:
            args.extend(["--limit", str(limit)])
        if json_mode:
            args.append("--json")
        return self._run_cli(args, timeout=90.0)

    def recommend(self, top: Optional[int] = None, json_mode: bool = True) -> Dict[str, Any]:
        args = ["recommend"]
        if top is not None:
            args.extend(["--top", str(top)])
        if json_mode:
            args.append("--json")
        return self._run_cli(args, timeout=90.0)

    def list_installed(self, json_mode: bool = True) -> Dict[str, Any]:
        args = ["list"]
        if json_mode:
            args.append("--json")
        return self._run_cli(args, timeout=60.0)

    def show(self, model_id: str, json_mode: bool = True) -> Dict[str, Any]:
        args = ["show", self.resolve_model_id(model_id)]
        if json_mode:
            args.append("--json")
        return self._run_cli(args, timeout=60.0)

    def run(self, model_id: str) -> Dict[str, Any]:
        """Lança `runai run <model_id>` em subprocesso best-effort.

        Não assume protocolo HTTP nem parsing de saída estruturada. Apenas lança
        o processo e retorna PID/comando, ou erro imediato.
        """
        resolved = self.resolve_model_id(model_id)
        if self.runtime_mode() == "source":
            prepared = self._ensure_source_ready()
            if not prepared.get("ok"):
                return {
                    "ok": False,
                    "exit_code": 2,
                    "stderr": prepared.get("detail", ""),
                    "command": [self.pnpm_path() or self.pnpm_binary, "--filter", "@canirun/runai", "run", "dev", "--", "run", resolved],
                    "launched": False,
                    "mode": "source",
                }
            command = [self.pnpm_path(), "--filter", "@canirun/runai", "run", "dev", "--", "run", resolved]
            try:
                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=self.source_root(),
                    env=self._source_env(),
                )
                return {
                    "ok": True,
                    "pid": proc.pid,
                    "command": command,
                    "provider": PROVIDER_ID,
                    "model": resolved,
                    "requested_model": model_id,
                    "launched": True,
                    "mode": "source",
                }
            except Exception as exc:
                return {
                    "ok": False,
                    "exit_code": 1,
                    "stderr": str(exc),
                    "command": command,
                    "launched": False,
                    "mode": "source",
                }
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
                "mode": "binary",
            }
        except Exception as exc:
            return {
                "ok": False,
                "exit_code": 1,
                "stderr": str(exc),
                "command": [self.binary, "run", resolved],
                "launched": False,
                "mode": "binary",
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
            "mode": self.runtime_mode(),
            "binary": self.binary,
            "catalog_models": list(MODELS.keys()),
            "aliases": dict(MODEL_ALIASES),
            "doctor_ok": bool(result.get("ok")),
            "doctor_exit_code": result.get("exit_code"),
            "installer": self.installer_diagnosis() if not self.is_binary_available() else {"ok": True, "detail": "Binário local encontrado; diagnóstico upstream opcional."},
            "source": self.source_diagnosis(),
        }

    def provider_info(self) -> Dict[str, Any]:
        return {
            "provider_id": PROVIDER_ID,
            "binary": self.binary,
            "available": self.is_available(),
            "mode": self.runtime_mode(),
            "catalog_models": len(MODELS),
            "model_aliases": dict(MODEL_ALIASES),
            "scope": "provisionamento/launcher CLI local (não HTTP provider)",
            "supported_commands": [
                "doctor[--json]", "pull", "run", "browse", "recommend",
                "list", "show", "--help", "--version|version"
            ],
            "installer_package_url": NPM_PACKAGE_URL,
            "source_repository_url": SOURCE_REPOSITORY_URL,
            "source": self.source_diagnosis(),
        }


runai_provisioner = RunAIProvisioner()
