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
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

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
        "  /colab-mcp list     # tools via protocolo (open_colab_browser_connection, materialize_*)\n"
        "  /colab-mcp materialize --model-file M --json NB  # grava .ipynb local\n"
        "  /colab-mcp doctor   # saúde (pass/warn, nunca fail)\n"
        "\n"
        "Nota: open_colab_browser_connection exige aba do navegador do operador;\n"
        "materialize grava .ipynb local via protocolo (provado em R651)."
    )


def _server_cmd_resolved(server_cmd: Optional[List[str]] = None) -> List[str]:
    """Comando do servidor: argumento, `COLAB_MCP_CMD` (separado por \\x1f) ou padrão uvx."""
    if server_cmd:
        return list(server_cmd)
    env = os.environ.get("COLAB_MCP_CMD")
    if env:
        return env.split("\x1f")
    return list(mcp_config(prefer_uvx=True)["command"])  # type: ignore[arg-type]


def _run_colab_stdio(
    op: str,
    tool: str = "",
    arguments: Optional[Dict[str, Any]] = None,
    server_cmd: Optional[List[str]] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Handshake MCP real via stdio contra o colab-mcp (adendo R651).

    `op` = "list" (tools/list) ou "call". Importa `mcp`/`anyio` sob demanda;
    nunca lança exceção.
    """
    try:
        import anyio  # noqa: F401
        from mcp import ClientSession, StdioServerParameters  # noqa: F401
        from mcp.client.stdio import stdio_client  # noqa: F401
    except ImportError:
        return {"ok": False, "error": "pacote `mcp` ausente (pip install mcp)."}
    command = _server_cmd_resolved(server_cmd)

    async def _run() -> Dict[str, Any]:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(command=command[0], args=command[1:])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                if op == "list":
                    tools = await session.list_tools()
                    return {"ok": True, "tools": [
                        {"name": t.name, "description": (t.description or "")[:200]}
                        for t in (tools.tools or [])
                    ]}
                result = await session.call_tool(tool, arguments or {})
                return {"ok": True, "texts": [
                    (c.text if hasattr(c, "text") else str(c))
                    for c in (result.content or [])
                ]}

    try:
        import anyio

        async def _bounded() -> Dict[str, Any]:
            with anyio.fail_after(timeout):
                return await _run()

        return anyio.run(_bounded)
    except Exception as exc:  # noqa: BLE001 - erro vira payload
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def list_tools_via_server(
    server_cmd: Optional[List[str]] = None, timeout: int = 120,
) -> Dict[str, Any]:
    """Lista tools do colab-mcp via protocolo (adendo R651)."""
    return _run_colab_stdio("list", server_cmd=server_cmd, timeout=timeout)


def materialize_qcaf(
    notebook_json: str,
    filename: str = "qcaf_experiment.ipynb",
    output_dir: str = ".",
    overwrite: bool = False,
    server_cmd: Optional[List[str]] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Materializa notebook QCAF como .ipynb via `materialize_qcaf_colab_notebook`.

    Nunca lança; devolve `{"ok", "result" (QCAFNotebookMaterializeResult)}.
    """
    if not isinstance(notebook_json, str) or len(notebook_json.strip()) < 2:
        return {"ok": False, "error": "notebook_json deve ser string JSON não vazia."}
    raw = _run_colab_stdio(
        "call", "materialize_qcaf_colab_notebook",
        {"request": {"notebook_json": notebook_json, "filename": filename,
                     "output_dir": output_dir, "overwrite": overwrite}},
        server_cmd=server_cmd, timeout=timeout,
    )
    if not raw.get("ok"):
        return {"ok": False, "error": str(raw.get("error"))}
    try:
        texts = raw.get("texts") or []
        return {"ok": True, "result": json.loads(texts[0]) if texts else {}}
    except (json.JSONDecodeError, IndexError, TypeError) as exc:
        return {"ok": False, "error": f"resposta não-JSON: {exc}"}


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
            "Uso: python3 -m integrations.colab_mcp <status|config|list|materialize|doctor|install> [args...]\n"
            "  config [--no-uvx]   # imprime o snippet JSON stdio\n"
            "  list                # tools via protocolo MCP\n"
            "  materialize --json NBJSON --file NOME [--dir DIR] [--overwrite]"
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
    if command == "list":
        print(json.dumps(list_tools_via_server(), ensure_ascii=False, indent=2))
        return 0
    if command == "materialize":
        nbjson, fname, dname, over = "", "qcaf_experiment.ipynb", ".", False
        idx = 0
        while idx < len(rest):
            if rest[idx] == "--json" and idx + 1 < len(rest):
                nbjson = rest[idx + 1]; idx += 2; continue
            if rest[idx] == "--file" and idx + 1 < len(rest):
                fname = rest[idx + 1]; idx += 2; continue
            if rest[idx] == "--dir" and idx + 1 < len(rest):
                dname = rest[idx + 1]; idx += 2; continue
            if rest[idx] == "--overwrite":
                over = True; idx += 1; continue
            idx += 1
        if not nbjson.strip():
            print("Uso: materialize --json NBJSON --file NOME [--dir DIR] [--overwrite]")
            return 2
        out = materialize_qcaf(nbjson, fname, dname, over)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 1
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
