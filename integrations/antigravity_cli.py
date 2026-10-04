# -*- coding: utf-8 -*-
"""
Runner direto Antigravity CLI (SPEC-935-R651) — executor externo orquestrável.

Complementa (NÃO substitui) a integração profunda existente:
`integrations/antigravity/bridge.py` + MCP + executor `antigravity`.
Upstream: google-antigravity/antigravity-cli (oficial).

Forma canônica (cf. bridge.py::delegate): `agy --agent A --print PROMPT
--output-format F`. Sintaxe errada abre TUI interativa; `returncode == 0`
com stdout `CLI error:/Error:` é falha silenciosa — inspecionada aqui.
Execução EXTERNA; resultados nunca "verificados" sem validação (R110).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

_BIN_NAME = "agy"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"
_BIN_CACHE: Optional[str] = None

AGY_INSTALL = "curl -fsSL https://antigravity.google/cli/install.sh | bash"
_SILENT_FAILURE_PREFIXES = ("CLI error:", "Error:")


def _find_binary() -> Optional[str]:
    """Caminho do binário `agy` (None se ausente)."""
    global _BIN_CACHE
    if _BIN_CACHE is None:
        _BIN_CACHE = shutil.which(_BIN_NAME)
    return _BIN_CACHE


def agy_available() -> bool:
    """True se o binário `agy` estiver no PATH."""
    return _find_binary() is not None


def agy_version(timeout: int = 15) -> Optional[str]:
    """Versão semântica via `agy --version` (None se ausente/falha)."""
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


def agy_run(
    prompt: str,
    agent: str = "default",
    output_format: str = "text",
    extra_args: Optional[List[str]] = None,
    timeout: int = 300,
) -> Dict[str, object]:
    """Executa `agy --agent A --print PROMPT --output-format F` (nunca lança).

    Inspeciona falha silenciosa (stdout com prefixo de erro + rc 0).
    `extra_args`: ex. ["--model", "X", "--effort", "high"]. stdin = DEVNULL
    (nunca herdar TTY — evita TUI interativa).
    """
    binary = _find_binary()
    if binary is None:
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": "Antigravity CLI não instalado. Execute /agy install.",
                "timeout": False, "version": None, "comando": None}
    if not prompt.strip():
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": "prompt vazio", "timeout": False,
                "version": agy_version(), "comando": None}
    cmd: List[str] = [binary, "--agent", agent, "--print", prompt,
                      "--output-format", output_format]
    if extra_args:
        cmd += list(extra_args)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL,
                              timeout=timeout, check=False)
        stdout = proc.stdout or ""
        silent = stdout.lstrip().startswith(_SILENT_FAILURE_PREFIXES)
        returncode = int(proc.returncode)
        return {"ok": returncode == 0 and not silent,
                "returncode": returncode, "stdout": stdout,
                "stderr": (proc.stderr or ""),
                "timeout": False, "version": agy_version(),
                "comando": " ".join(cmd[:5]) + " ..."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": f"agy excedeu o limite de {timeout}s.",
                "timeout": True, "version": agy_version(), "comando": None}
    except OSError as exc:
        return {"ok": False, "returncode": None, "stdout": "",
                "stderr": f"Falha ao invocar agy: {exc}",
                "timeout": False, "version": None, "comando": None}


def doctor_check() -> Dict[str, str]:
    """DoctorCheck (pass/warn, nunca fail)."""
    version = agy_version()
    if version is not None:
        return {"name": "agy", "status": "pass",
                "detail": f"Antigravity CLI instalado (versão {version}). "
                "Runner direto via integrations.antigravity_cli (SPEC-935-R651)."}
    if agy_available():
        return {"name": "agy", "status": "pass",
                "detail": "Antigravity CLI instalado (versão não detectada). SPEC-935-R651."}
    return {"name": "agy", "status": "warn",
            "detail": f"Antigravity CLI ausente (SPEC-935-R651). Instale com: {AGY_INSTALL}."}


def install_instructions() -> str:
    """Instalação oficial + relação com o bridge existente."""
    return (
        "Antigravity CLI (google-antigravity/antigravity-cli, oficial):\n"
        f"  {AGY_INSTALL}\n"
        "\n"
        "Uso no Core — duas vias complementares:\n"
        "  /agy run '<prompt>' [--agent A] [--format text|json]  (runner direto, SPEC-935-R651)\n"
        "  ecosystem_run com executor antigravity  (orquestrado com revisão, SPEC-935-R621)\n"
        "\n"
        "Forma canônica: agy --agent <agent> --print '<prompt>' --output-format text\n"
        "Nunca herdar TTY (abre TUI); falhas silenciosas (rc 0 + 'CLI error:') são detectadas."
    )


def _format_status() -> str:
    return json.dumps(
        {"especificacao": "SPEC-935-R651", "disponivel": agy_available(),
         "versao": agy_version(), "binario": "agy",
         "licenca": "a confirmar no upstream",
         "origem": "https://github.com/google-antigravity/antigravity-cli",
         "ponte_profunda": "integrations/antigravity/bridge.py + MCP"},
        ensure_ascii=False, indent=2,
    )


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.antigravity_cli <status|run|doctor|install> [args...]\n"
            "  run '<prompt>' [--agent A] [--format text|json|stream-json] [--timeout SEG] [--model M] [--effort E]"
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
        prompt_parts, agent, fmt, timeout, extra = [], "default", "text", 300, []
        idx = 0
        while idx < len(rest):
            tok = rest[idx]
            if tok == "--agent" and idx + 1 < len(rest):
                agent = rest[idx + 1]; idx += 2; continue
            if tok == "--format" and idx + 1 < len(rest):
                fmt = rest[idx + 1]; idx += 2; continue
            if tok == "--timeout" and idx + 1 < len(rest):
                try: timeout = int(rest[idx + 1])
                except ValueError: timeout = 300
                idx += 2; continue
            if tok in ("--model", "--effort", "--sandbox") and idx + 1 < len(rest):
                extra += [tok, rest[idx + 1]]; idx += 2; continue
            prompt_parts.append(tok); idx += 1
        prompt = " ".join(prompt_parts).strip()
        if not prompt:
            print("Uso: python3 -m integrations.antigravity_cli run '<prompt>' [--agent A]")
            return 2
        result = agy_run(prompt, agent=agent, output_format=fmt,
                         extra_args=extra or None, timeout=timeout)
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
