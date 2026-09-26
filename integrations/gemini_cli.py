# -*- coding: utf-8 -*-
"""
Integração da CLI Gemini (SPEC-935-R600) — executor externo orquestrável.

Pacote oficial: @google/gemini-cli  (repositório google-gemini/gemini-cli)
Entry point:   gemini

Modo headless/scripts (fonte: README oficial):
    gemini -p "<prompt>" [--output-format json|stream-json] [-m MODELO]

Autenticação:
    export GEMINI_API_KEY="..."            # aistudio.google.com/apikey (free tier)
    # ou Vertex AI:
    export GOOGLE_API_KEY="..."
    export GOOGLE_GENAI_USE_VERTEXAI=true

A execução é EXTERNA ao Core: o orquestrador marceloclaro permanece dono do
ciclo SDD/TDD; resultados do Gemini nunca são declarados "verificados" sem
validação (anti-overclaim R110).
"""

import json
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

_BIN_NAME = "gemini"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"
_BIN_CACHE: Optional[str] = None
_AVAILABLE_CACHE: Optional[bool] = None


def _find_binary() -> Optional[str]:
    """Caminho do binário `gemini`, com cache por sessão (None se ausente)."""
    global _BIN_CACHE
    if _BIN_CACHE is None:
        _BIN_CACHE = shutil.which(_BIN_NAME)
    return _BIN_CACHE


def gemini_available() -> bool:
    """True se o binário `gemini` estiver no PATH."""
    global _AVAILABLE_CACHE
    if _AVAILABLE_CACHE is None:
        _AVAILABLE_CACHE = _find_binary() is not None
    return _AVAILABLE_CACHE


def gemini_version() -> Optional[str]:
    """Versão semântica instalada via `gemini --version` (None se ausente).

    Extrai apenas a versão (ex.: "Gemini CLI v3.5.2 (build 2026)" → "3.5.2").
    """
    binary = _find_binary()
    if binary is None:
        return None
    try:
        proc = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=10, check=False
        )
        match = re.search(_SEMVER_RE, (proc.stdout or "").strip())
        return match.group(1) if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def gemini_run(
    prompt: str,
    model: Optional[str] = None,
    output_format: Optional[str] = None,
    timeout: int = 300,
) -> Dict[str, object]:
    """Executa o Gemini em modo headless (`-p`) e retorna dict estruturado.

    Nunca lança exceção. `comando` usa lista (sem shell) para auditabilidade.
    """
    binary = _find_binary()
    if binary is None:
        return {
            "ok": False,
            "stdout": "",
            "stderr": "Gemini CLI não instalado. Execute /gemini install.",
            "returncode": None,
            "comando": [],
            "timeout": timeout,
        }
    comando: List[str] = [binary, "-p", prompt]
    if model:
        comando += ["-m", model]
    if output_format:
        comando += ["--output-format", output_format]
    try:
        proc = subprocess.run(
            comando, capture_output=True, text=True, timeout=timeout, check=False
        )
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "returncode": proc.returncode,
            "comando": comando,
            "timeout": timeout,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(exc),
            "returncode": None,
            "comando": comando,
            "timeout": timeout,
        }


def doctor_check() -> Dict[str, str]:
    """Checagem de saúde da integração Gemini (pass/warn — nunca fail)."""
    if not gemini_available():
        return {
            "name": "gemini-cli",
            "status": "warn",
            "detail": "Gemini CLI não instalado (comando /gemini install).",
        }
    versao = gemini_version()
    sufixo = f" (versão {versao})" if versao else ""
    return {
        "name": "gemini-cli",
        "status": "pass",
        "detail": f"Gemini CLI instalado{sufixo}.",
    }


def install_instructions() -> str:
    """Instruções de instalação e autenticação da CLI Gemini."""
    return (
        "Instalação (requer Node.js 18+):\n"
        "  npm install -g @google/gemini-cli\n"
        "  # ou sem instalar:  npx @google/gemini-cli\n"
        "  # ou Homebrew:      brew install gemini-cli\n"
        "\n"
        "Autenticação (obter key em https://aistudio.google.com/apikey):\n"
        "  export GEMINI_API_KEY=\"sua_chave\"\n"
        "  # opção Vertex AI:\n"
        "  #   export GOOGLE_API_KEY=\"sua_chave\"\n"
        "  #   export GOOGLE_GENAI_USE_VERTEXAI=true\n"
        "\n"
        "Uso headless no Core:\n"
        "  /gemini run '<tarefa>' [--model gemini-2.5-flash] [--output-format json]\n"
        "  gemini -p 'pergunta' --output-format json\n"
    )


def _format_status() -> str:
    binario = _find_binary() or "(não instalado)"
    versao = gemini_version() or "-"
    return json.dumps(
        {"name": "gemini-cli", "available": gemini_available(), "binary": binario, "version": versao},
        ensure_ascii=False,
        indent=2,
    )


def _parse_run_argv(tokens: List[str]) -> Dict[str, object]:
    """Interpreta flags de run: -m/--model, --output-format, --timeout."""
    parsed: Dict[str, object] = {"prompt_parts": []}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        matched = False
        for flag, key in (("-m", "model"), ("--model", "model"),
                          ("--output-format", "output_format"),
                          ("--timeout", "timeout")):
            if token == flag and index + 1 < len(tokens):
                parsed[key] = tokens[index + 1]
                index += 2
                matched = True
                break
            if token.startswith(flag + "="):
                parsed[key] = token.split("=", 1)[1]
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
            "Uso: python3 -m integrations.gemini_cli <status|run|doctor|install> [args...]\n"
            "  run '<tarefa>' [--model|-m MODELO] [--output-format json|stream-json]\n"
            "                  [--timeout SEG]\n"
            "  ex.: /gemini run 'explique o arquivo' -m gemini-2.5-flash --output-format json"
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
            print("Uso: python3 -m integrations.gemini_cli run '<prompt>' [--model MODELO]")
            return 2
        timeout = int(parsed.get("timeout", 300) or 300)  # type: ignore[arg-type]
        resultado = gemini_run(
            prompt,
            model=str(parsed["model"]) if parsed.get("model") else None,
            output_format=str(parsed["output_format"]) if parsed.get("output_format") else None,
            timeout=timeout,
        )
        print(resultado.get("stdout") or resultado.get("stderr") or "")
        return 0 if resultado.get("ok") else 1
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())