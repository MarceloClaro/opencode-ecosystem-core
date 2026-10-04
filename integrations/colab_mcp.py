# -*- coding: utf-8 -*-
"""
Servidor MCP do Google Colab (SPEC-935-R645) — ponte orquestrável.

Repositório: MarceloClaro/colab-mcp (fork de googlecolab/colab-mcp, Apache-2.0):
servidor MCP para codificação assistida interativa dentro do notebook —
complemento do fluxo terminal do `google-colab-cli`.

Este módulo NÃO executa o protocolo MCP; ele expõe presença/versão/config
stdio pronta para `opencode.json` + healthcheck tolerante (padrão M7).
A execução do servidor é EXTERNA; resultados nunca são "verificados" sem
validação do Core (anti-overclaim R110).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

_BIN_NAME = "colab-mcp"
_UVX_BIN = "uvx"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"

MCP_INSTALL_UVX = "uvx colab-mcp --help"
MCP_INSTALL_PIP = "pip install colab-mcp"


def _find_binary() -> Optional[str]:
    """Caminho do binário `colab-mcp` (None se ausente; sem cache persistente)."""
    return shutil.which(_BIN_NAME)


def _uvx_available() -> bool:
    """True se `uvx` estiver no PATH (fallback sem instalação global)."""
    return shutil.which(_UVX_BIN) is not None


def mcp_available() -> bool:
    """True se o servidor for executável (binário local ou via uvx)."""
    return _find_binary() is not None or _uvx_available()


def mcp_version(timeout: int = 15) -> Optional[str]:
    """Versão semântica via `colab-mcp --version` (None se ausente/falha).

    Não tenta rede: se só houver `uvx` (sem binário local), retorna None para
    evitar download implícito durante o doctor.
    """
    binary = _find_binary()
    if binary is None:
        return None
    for flag in ("--version", "version"):
        try:
            proc = subprocess.run(
                [binary, flag], capture_output=True, text=True,
                timeout=timeout, check=False,
            )
            combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
            match = re.search(_SEMVER_RE, combined)
            if match:
                return match.group(1)
        except (OSError, subprocess.TimeoutExpired):
            return None
    return None


def mcp_config(prefer_uvx: bool = True) -> Dict[str, object]:
    """Entrada stdio pronta para a seção `mcp` do `opencode.json`.

    Prefere `uvx colab-mcp` (sem instalação global) quando solicitado e
    disponível; caso contrário usa o binário local.
    """
    binary = _find_binary()
    if prefer_uvx and _uvx_available():
        command: List[str] = [_UVX_BIN, _BIN_NAME]
    elif binary is not None:
        command = [binary]
    elif _uvx_available():
        command = [_UVX_BIN, _BIN_NAME]
    else:
        command = [_BIN_NAME]
    return {
        "type": "local",
        "command": command,
        "enabled": True,
        "timeout": 660000,
    }


def doctor_check() -> Dict[str, str]:
    """DoctorCheck no formato do Core (name/status/detail; nunca fail)."""
    version = mcp_version()
    if version is not None:
        return {
            "name": "colab-mcp",
            "status": "pass",
            "detail": f"Colab MCP Server executável (versão {version}). "
            "Ponte orquestrável via integrations.colab_mcp (SPEC-935-R645).",
        }
    if _find_binary() is not None:
        return {
            "name": "colab-mcp",
            "status": "pass",
            "detail": "Colab MCP Server instalado (versão não detectada). "
            "Ponte orquestrável via integrations.colab_mcp (SPEC-935-R645).",
        }
    if _uvx_available():
        return {
            "name": "colab-mcp",
            "status": "pass",
            "detail": "Colab MCP Server executável via uvx (sem instalação global). "
            "Ponte orquestrável via integrations.colab_mcp (SPEC-935-R645).",
        }
    return {
        "name": "colab-mcp",
        "status": "warn",
        "detail": "Colab MCP Server ausente (SPEC-935-R645). "
        f"Use sem instalar: {MCP_INSTALL_UVX}  (ou {MCP_INSTALL_PIP}).",
    }


def install_instructions() -> str:
    """Instrução oficial de uso do Colab MCP Server."""
    return (
        "Colab MCP Server (googlecolab/colab-mcp, Apache-2.0) — codificação\n"
        "assistida interativa dentro do notebook (complemento do CLI de terminal):\n"
        f"  {MCP_INSTALL_UVX}\n"
        f"  # alternativa com instalação: {MCP_INSTALL_PIP}\n"
        "\n"
        "Registro no opencode.json (gerado por mcp_config()):\n"
        '  "colab-mcp": {"type": "local", "command": ["uvx", "colab-mcp"], "enabled": true}\n'
        "\n"
        "Uso no Core:\n"
        "  /colab-mcp status   # presença (binário ou uvx) + versão\n"
        "  /colab-mcp config   # snippet JSON stdio\n"
        "  /colab-mcp doctor   # saúde (pass/warn, nunca fail)\n"
        "\n"
        "Nota: o servidor opera no contexto do notebook Colab autenticado;\n"
        "credenciais e kernels pertencem ao operador (não ao Core)."
    )


def _format_status() -> str:
    binary = _find_binary()
    return json.dumps(
        {
            "especificacao": "SPEC-935-R645",
            "disponivel": mcp_available(),
            "binario": binary,
            "via_uvx": _uvx_available(),
            "versao": mcp_version(),
            "licenca": "Apache-2.0",
            "origem": "https://github.com/googlecolab/colab-mcp",
            "fork": "https://github.com/MarceloClaro/colab-mcp",
        },
        ensure_ascii=False,
        indent=2,
    )


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.colab_mcp <status|config|doctor|install> [args...]\n"
            "  config [--no-uvx]   # imprime o snippet JSON stdio"
        )
        return 0
    command, *rest = argv
    if command == "status":
        print(_format_status())
        return 0
    if command == "config":
        prefer_uvx = "--no-uvx" not in rest
        print(json.dumps({"colab-mcp": mcp_config(prefer_uvx=prefer_uvx)},
                         ensure_ascii=False, indent=2))
        return 0
    if command == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1
    if command == "install":
        print(install_instructions())
        return 0
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
