# -*- coding: utf-8 -*-
"""
Goose CLI Integration — agente de IA nativo open source (AAIF/Linux Foundation)
================================================================================
Integra a CLI `goose` (https://github.com/aaif-goose/goose, Apache-2.0) ao
OpenCode Ecosystem Core como executor externo orquestrável (padrão M7, mesma
família do bernstein-orchestrator e do opencode-go-agent): invocação por
subprocess, healthcheck tolerante — Goose é opcional, ausência vira ``warn``
no doctor, nunca ``fail`` (SPEC-935-R598).

Goose é um agente generalista em Rust (desktop + CLI + API) com suporte a 15+
providers (Anthropic, OpenAI, Google, Ollama, OpenRouter, Azure, Bedrock — com
assinaturas existentes via ACP) e 70+ extensões via Model Context Protocol (MCP).

Uso:
    python3 -m integrations.goose_cli status          # disponibilidade + versão
    python3 -m integrations.goose_cli run '<prompt>'  # execução headless (mode auto)
    python3 -m integrations.goose_cli doctor          # DoctorCheck (formato do doctor do Core)
    python3 -m integrations.goose_cli install         # instrução oficial de instalação
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

GOOSE_INSTALL_CMD = (
    "curl -fsSL "
    "https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh"
    " | bash"
)

# Base dos comandos headless (estáveis na CLI 2025-2026; confira com
# `goose run --help` após instalar para flags adicionais do seu provider).
_RUN_HEADLESS_FLAGS = ("run", "--text")


def goose_available() -> bool:
    """True se o binário `goose` estiver no PATH."""
    return shutil.which("goose") is not None


_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"


def goose_version() -> Optional[str]:
    """Versão semântica instalada via `goose --version` (None se ausente).

    Lê a primeira linha da saída e extrai apenas o número de versão
    (ex.: ``"goose 1.1.0 (stable)"`` → ``"1.1.0"``).
    """
    if not goose_available():
        return None
    try:
        proc = subprocess.run(
            ["goose", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        match = re.search(_SEMVER_RE, (proc.stdout or "").strip())
        return match.group(1) if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def goose_run(
    prompt: str,
    cwd: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 300,
    extra_flags: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Executa o Goose em modo headless (`goose run --text`).

    Retorna sempre um dicionário estável ``{ok, returncode, stdout, stderr,
    timeout, version, comando}`` — nunca lança exceção para o chamador.

    ``provider``/``model`` são injetados com as flags ``--provider`` e
    ``--model`` quando informados (consulte a doc do provider instalado;
    providers padrão são resolvidos pela config local do Goose).
    """
    if not goose_available():
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "goose não está instalado. Instale com: " + GOOSE_INSTALL_CMD,
            "timeout": False,
            "version": None,
            "comando": None,
        }

    cmd: List[str] = ["goose", *_RUN_HEADLESS_FLAGS]
    if provider:
        cmd += ["--provider", provider]
    if model:
        cmd += ["--model", model]
    if extra_flags:
        cmd += list(extra_flags)
    cmd.append(prompt)

    timeout_flag = False
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
        returncode = int(proc.returncode)
        return {
            "ok": returncode == 0,
            "returncode": returncode,
            "stdout": (proc.stdout or ""),
            "stderr": (proc.stderr or ""),
            "timeout": False,
            "version": goose_version(),
            "comando": " ".join(cmd),
        }
    except subprocess.TimeoutExpired:
        timeout_flag = True
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"goose run excedeu o limite de {timeout}s.",
            "timeout": True,
            "version": goose_version(),
            "comando": " ".join(cmd),
        }
    except OSError as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Falha ao invocar goose: {exc}",
            "timeout": False,
            "version": goose_version(),
            "comando": " ".join(cmd),
        }


def doctor_check() -> Dict[str, str]:
    """DoctorCheck no formato do doctor do Core (name/status/detail)."""
    version = goose_version()
    if version is not None:
        return {
            "name": "goose",
            "status": "pass",
            "detail": f"Goose CLI instalado (versão {version}). "
            "Executor externo orquestrável via integrations.goose_cli (SPEC-935-R598).",
        }
    return {
        "name": "goose",
        "status": "warn",
        "detail": "Goose CLI ausente (específica do SPEC-935-R598). Anterior a "
        f"integrar, instale com: {GOOSE_INSTALL_CMD}",
    }


def install_instructions() -> str:
    """Instrução oficial de instalação do Goose CLI."""
    return (
        "Instalação oficial do Goose CLI (stable):\n"
        f"  {GOOSE_INSTALL_CMD}\n"
        "Alternativas: https://goose-docs.ai/docs/getting-started/installation\n"
        "Provider padrão: o Goose pede a chave do provider na primeira execução;\n"
        "  ou use --provider/--model no goose_run (Anthropic, OpenAI, Google,\n"
        "  Ollama, OpenRouter, Azure, Bedrock e outros — 15+ providers)."
    )


def _format_status() -> str:
    available = goose_available()
    version = goose_version()
    versao_json = "null" if version is None else json.dumps(version)
    lines = [
        "{",
        f'  "especificacao": "SPEC-935-R598",',
        f'  "disponivel": {str(available).lower()},',
        f'  "versao": {versao_json},',
        f'  "providers": "15+ (Anthropic, OpenAI, Google, Ollama, OpenRouter, Azure, Bedrock, ...)",',
        f'  "mcp_extensoes": "70+ via Model Context Protocol",',
        f'  "licenca": "Apache-2.0",',
        f'  "origem": "https://github.com/aaif-goose/goose",',
        "}",
    ]
    return "\n".join(lines)


def _parse_run_argv(tokens: List[str]) -> Dict[str, object]:
    """Interpreta flags de run: --provider/--model/--timeout (valor ou =valor)."""
    parsed: Dict[str, object] = {"prompt_parts": []}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        matched = False
        for flag in ("--provider", "--model", "--timeout"):
            if token == flag and index + 1 < len(tokens):
                parsed[flag[2:]] = tokens[index + 1]
                index += 2
                matched = True
                break
            if token.startswith(flag + "="):
                parsed[flag[2:]] = token.split("=", 1)[1]
                index += 1
                matched = True
                break
        if not matched:
            parsed["prompt_parts"].append(token)  # type: ignore[attr-defined]
            index += 1
    return parsed


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.goose_cli <status|run|doctor|install> [args...]\n"
            "  run '<tarefa>' [--provider PROV] [--model MODELO] [--timeout SEG] [--flag-extra ...]\n"
            "  ex.: /goose run 'revise este texto' --provider ollama --model qwen3:8b --timeout 120"
        )
        return 0
    command, *rest = argv
    if command == "status":
        print(_format_status())
        return 0
    if command == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1
    if command == "install":
        print(install_instructions())
        return 0
    if command == "run":
        parsed = _parse_run_argv(rest)
        prompt = " ".join(str(piece) for piece in parsed["prompt_parts"]).strip()
        if not prompt:
            print("Uso: python3 -m integrations.goose_cli run '<prompt>' [--provider PROV] [--model M]")
            return 2
        timeout = int(parsed.get("timeout", 300) or 300)  # type: ignore[arg-type]
        result = goose_run(
            prompt,
            provider=str(parsed.get("provider")) if parsed.get("provider") else None,
            model=str(parsed.get("model")) if parsed.get("model") else None,
            timeout=timeout,
        )
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())