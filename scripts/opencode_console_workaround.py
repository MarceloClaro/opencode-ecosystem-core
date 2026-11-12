#!/usr/bin/env python3
"""Workaround temporário para o opencode_console (HTTP 403).

Causa conhecida: o token emitido pelo OAuth do MCP não é reconhecido pelo
workspace, embora o token de membro da integração `opencode` seja. O endpoint
aceita o token de membro. Este script aplica um override em runtime no serviço
OpenCode, usando o token de membro no header Authorization, sem gravar o token
em opencode.json nem duplicar a credencial no banco.

Limites:
- o override vive na memória do serviço; reiniciou o serviço, rode de novo;
- o token de membro expira e pode ser rotacionado; se expirar, rode /connect
  para renovar a integração e execute este script novamente;
- não corrige o bug upstream (anomalyco/opencode#59806); é uma ponte local.

Uso:
    python3 scripts/opencode_console_workaround.py
    python3 scripts/opencode_console_workaround.py --check
    python3 scripts/opencode_console_workaround.py --project /caminho
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

INTEGRATION = "mcp_eec8489fdfd1e19a"
MEMBER_INTEGRATION = "opencode"
SERVER = "opencode_console"
MCP_URL = "https://opencode.ai/console/mcp"


def default_binary() -> str:
    service = Path.home() / ".local/state/opencode/service.json"
    try:
        data = json.loads(service.read_text())
        pid = int(data["pid"])
        exe = os.readlink(f"/proc/{pid}/exe")
        if Path(exe).exists():
            return exe
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        pass
    known = Path.home() / ".local/share/wsl-cli-tools/opencode-2.2.7/opencode"
    if known.exists():
        return str(known)
    found = shutil.which("opencode")
    if not found:
        raise SystemExit("binário opencode não encontrado")
    return found


def member_token() -> str:
    db = Path.home() / ".local/share/opencode/opencode.db"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        row = con.execute(
            "select value from credential where integration_id=? and active=1 "
            "order by time_updated desc limit 1",
            (MEMBER_INTEGRATION,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        raise SystemExit("credencial de membro ausente; rode /connect no OpenCode")
    data = json.loads(row[0])
    access = data.get("access")
    expires = data.get("expires")
    if not access:
        raise SystemExit("credencial de membro sem access token; rode /connect")
    if isinstance(expires, (int, float)) and expires / 1000 <= time.time():
        raise SystemExit("token de membro expirado; rode /connect para renovar")
    return access


def location_path(project: Path) -> str:
    return (
        f"/api/experimental/mcp/{SERVER}"
        f"?location%5Bdirectory%5D={quote(str(project), safe='')}"
    )


def list_path(project: Path) -> str:
    return f"/api/mcp?location%5Bdirectory%5D={quote(str(project), safe='')}"


def run_api(binary: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [binary, "api", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def status_of(binary: str, project: Path, token: str) -> dict:
    result = run_api(binary, "get", list_path(project))
    if result.returncode != 0:
        raise SystemExit(
            "falha ao consultar /api/mcp: "
            + (result.stderr or result.stdout).replace(token, "<redacted>")[:500]
        )
    payload = json.loads(result.stdout)
    for item in payload.get("data", []):
        if item.get("name") == SERVER:
            return item.get("status", {})
    return {"status": "missing"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="diretório do location OpenCode (default: raiz do repositório)",
    )
    parser.add_argument("--binary", default=None, help="binário opencode 2.2.x")
    parser.add_argument("--check", action="store_true", help="apenas verificar o estado")
    args = parser.parse_args()

    project = args.project.resolve()
    binary = args.binary or default_binary()
    token = member_token()

    if args.check:
        status = status_of(binary, project, token)
        print(json.dumps({"server": SERVER, "project": str(project), "status": status}))
        return 0 if status.get("status") == "connected" else 1

    body = json.dumps(
        {
            "config": {
                "type": "remote",
                "url": MCP_URL,
                "oauth": False,
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    )
    result = run_api(binary, "put", location_path(project), "--data", body)
    if result.returncode != 0:
        message = (result.stderr or result.stdout).replace(token, "<redacted>")
        print(f"falha ao aplicar override: {message[:600]}", file=sys.stderr)
        return 1

    status = status_of(binary, project, token)
    print(
        json.dumps(
            {
                "server": SERVER,
                "project": str(project),
                "status": status,
                "note": "override em runtime; reaplique após reiniciar o serviço",
            },
            ensure_ascii=False,
        )
    )
    return 0 if status.get("status") == "connected" else 1


if __name__ == "__main__":
    raise SystemExit(main())
