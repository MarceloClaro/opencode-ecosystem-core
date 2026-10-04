# -*- coding: utf-8 -*-
"""
Integração Kaggle CLI (SPEC-935-R650) — executor externo orquestrável.

Upstream: Kaggle/kaggle-cli (`kaggle`: competitions, datasets, kernels,
models, files, forums, benchmarks, config, auth, quota).
Auth do operador em ~/.kaggle/kaggle.json (600). Quota/GPU consomem a conta.

Passthrough genérico (20+ subcomandos). Execução EXTERNA; resultados nunca
são "verificados" sem validação do Core (anti-overclaim R110).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

_BIN_NAME = "kaggle"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"
_BIN_CACHE: Optional[str] = None

KAGGLE_INSTALL = "pip install kaggle"
KAGGLE_CRED_PATH = os.path.expanduser("~/.kaggle/kaggle.json")


def _find_binary() -> Optional[str]:
    """Caminho do binário `kaggle` (sem cache persistente entre interpretações)."""
    global _BIN_CACHE
    if _BIN_CACHE is None:
        _BIN_CACHE = shutil.which(_BIN_NAME)
    return _BIN_CACHE


def kaggle_available() -> bool:
    """True se o binário `kaggle` estiver no PATH."""
    return _find_binary() is not None


def kaggle_version(timeout: int = 15) -> Optional[str]:
    """Versão via `kaggle --version` (ex.: 'Kaggle CLI 2.2.4' → '2.2.4')."""
    binary = _find_binary()
    if binary is None:
        return None
    try:
        proc = subprocess.run(
            [binary, "--version"], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        match = re.search(_SEMVER_RE, combined)
        return match.group(1) if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def auth_check() -> Dict[str, object]:
    """Credencial presente? Só filesystem (SEM rede — doctor não sonda API)."""
    path = KAGGLE_CRED_PATH
    present = os.path.isfile(path)
    return {"present": present, "path": path,
            "hint": "obtenha em kaggle.com → Settings → Account → API" if not present else ""}


def kaggle_run_args(args: List[str], timeout: int = 300) -> Dict[str, object]:
    """Executa `kaggle <args>` (lista, sem shell) — nunca lança exceção."""
    binary = _find_binary()
    if binary is None:
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": "Kaggle CLI não instalado. Execute /kaggle install.",
                "timeout": False, "version": None, "comando": None}
    cmd: List[str] = [binary] + list(args)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, check=False)
        returncode = int(proc.returncode)
        return {"ok": returncode == 0, "returncode": returncode,
                "stdout": (proc.stdout or ""), "stderr": (proc.stderr or ""),
                "timeout": False, "version": kaggle_version(),
                "comando": " ".join(cmd)}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": f"kaggle {' '.join(args)} excedeu {timeout}s.",
                "timeout": True, "version": kaggle_version(),
                "comando": " ".join(cmd)}
    except OSError as exc:
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": f"Falha ao invocar kaggle: {exc}",
                "timeout": False, "version": None, "comando": " ".join(cmd)}


def doctor_check() -> Dict[str, str]:
    """DoctorCheck (pass/warn, nunca fail)."""
    version = kaggle_version()
    auth = auth_check()
    if version is not None:
        detail = f"Kaggle CLI instalado (versão {version}). SPEC-935-R650."
        if not auth["present"]:
            detail += " Sem credencial (~/.kaggle/kaggle.json) — chamadas à API falharão por auth."
        return {"name": "kaggle", "status": "pass", "detail": detail}
    if kaggle_available():
        return {"name": "kaggle", "status": "pass",
                "detail": "Kaggle CLI instalado (versão não detectada). SPEC-935-R650."}
    return {"name": "kaggle", "status": "warn",
            "detail": f"Kaggle CLI ausente (SPEC-935-R650). Instale com: {KAGGLE_INSTALL}."}


def install_instructions() -> str:
    """Instalação + autenticação oficiais."""
    return (
        "Kaggle CLI (Kaggle/kaggle-cli):\n"
        f"  {KAGGLE_INSTALL}\n"
        "\n"
        "Autenticação (conta do operador):\n"
        "  1. kaggle.com → Settings → Account → Create New API Token\n"
        "  2. salve como ~/.kaggle/kaggle.json com chmod 600\n"
        "  3. verifique: kaggle competitions list --page-size 2\n"
        "\n"
        "Uso no Core (passthrough):\n"
        "  /kaggle run competitions list --page-size 2\n"
        "  /kaggle run datasets download -d owner/dataset --unzip\n"
        "  /kaggle run quota   # cota semanal de GPU/TPU\n"
        "\n"
        "Aviso: downloads, kernels e quota consomem a conta Kaggle."
    )


def _format_status() -> str:
    return json.dumps(
        {"especificacao": "SPEC-935-R650",
         "disponivel": kaggle_available(), "versao": kaggle_version(),
         "auth": auth_check(), "binario": "kaggle",
         "licenca": "verificar no repo (Kaggle/kaggle-cli)",
         "origem": "https://github.com/Kaggle/kaggle-cli"},
        ensure_ascii=False, indent=2,
    )


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.kaggle_cli <status|run|auth|doctor|install> [args...]\n"
            "  run [--timeout SEG] <args do kaggle...>\n"
            "    ex.: run competitions list --page-size 2"
        )
        return 0
    command, *rest = argv
    if command == "status":
        print(_format_status())
        return 0
    if command == "auth":
        print(json.dumps(auth_check(), ensure_ascii=False, indent=2))
        return 0
    if command == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1
    if command == "install":
        print(install_instructions())
        return 0
    if command == "run":
        timeout = 300
        passthrough = []
        idx = 0
        while idx < len(rest):
            if rest[idx] == "--timeout" and idx + 1 < len(rest):
                try:
                    timeout = int(rest[idx + 1])
                except ValueError:
                    timeout = 300
                idx += 2
                continue
            passthrough.append(rest[idx])
            idx += 1
        if not passthrough:
            print("Uso: python3 -m integrations.kaggle_cli run [--timeout SEG] <args...>")
            return 2
        result = kaggle_run_args(passthrough, timeout=timeout)
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
