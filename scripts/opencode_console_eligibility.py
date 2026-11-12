#!/usr/bin/env python3
"""Diagnóstico upstream do `opencode_console` (SPEC-935-R1110).

Compara a elegibilidade MCP do token de membro da integração `opencode` com a
do token OAuth emitido para o MCP. Não imprime tokens, e-mail, IDs de conta ou
de workspace: apenas `eligible`, status HTTP, papel, nome do workspace e
contagem de permissões.

Uso:
    python3 scripts/opencode_console_eligibility.py
    python3 scripts/opencode_console_eligibility.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_DB = Path.home() / ".local/share/opencode/opencode.db"
ELIGIBILITY_URL = "https://opencode.ai/console/api/mcp/eligibility"
MEMBER_INTEGRATION = "opencode"
MCP_INTEGRATION = "mcp_eec8489fdfd1e19a"
TOKEN_MARGIN_SECONDS = 60

SECRET_RE = re.compile(r"(st_|oc_sk_|sk_)[A-Za-z0-9_\-]+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
ID_RE = re.compile(r"\b(?:acc|wrk|user|org|conn|ses|mcp)_[A-Za-z0-9]+\b")


class CredentialError(RuntimeError):
    """Credencial ausente, inválida ou expirada."""


def _sanitize(value: str) -> str:
    value = SECRET_RE.sub("<redacted>", value)
    value = EMAIL_RE.sub("<email>", value)
    return ID_RE.sub("<id>", value)


def read_credential_token(
    db_path: Path | str,
    integration: str,
    now: float | None = None,
) -> str:
    """Lê a credencial ativa mais recente de uma integração."""
    data = _read_credential(db_path, integration, now)
    access = data.get("access")
    if not isinstance(access, str) or not access.strip():
        raise CredentialError(f"credential {integration} has no access token")
    return access


def read_credential_metadata(db_path: Path | str, integration: str) -> dict:
    """Lê apenas os metadados não secretos de uma credencial ativa."""
    data = _read_credential(db_path, integration, None)
    metadata = data.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _read_credential(
    db_path: Path | str,
    integration: str,
    now: float | None = None,
) -> dict:
    db_path = Path(db_path)
    if not db_path.exists():
        raise CredentialError("OpenCode database not found; run /connect in OpenCode")
    current = time.time() if now is None else now
    con = None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
        con.execute("pragma busy_timeout=5000")
        row = con.execute(
            "select value from credential where integration_id=? and active=1 "
            "order by time_updated desc limit 1",
            (integration,),
        ).fetchone()
    except sqlite3.Error as exc:
        raise CredentialError(f"cannot read OpenCode credentials: {exc}") from exc
    finally:
        if con is not None:
            con.close()
    if not row:
        raise CredentialError(f"credential {integration} missing; run /connect")
    try:
        data = json.loads(row[0])
    except (TypeError, json.JSONDecodeError) as exc:
        raise CredentialError(f"credential {integration} is not valid JSON") from exc
    if not isinstance(data, dict):
        raise CredentialError(f"credential {integration} has an unexpected shape")
    expires = data.get("expires")
    if isinstance(expires, (int, float)) and expires / 1000.0 <= current + TOKEN_MARGIN_SECONDS:
        raise CredentialError(f"credential {integration} expired or expiring; run /connect")
    return data


def fetch_eligibility(
    token: str,
    url: str = ELIGIBILITY_URL,
    org_id: str | None = None,
) -> dict:
    request = urllib.request.Request(url, method="GET")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", "opencode-console-eligibility/1.0")
    if org_id:
        request.add_header("x-org-id", org_id)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(8192).decode("utf-8", "replace")
            payload = json.loads(body) if body else {}
            return {"http_status": response.status, "payload": payload}
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", "replace")
        return {
            "http_status": exc.code,
            "payload": {},
            "error": _sanitize(body)[:300],
        }
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "http_status": None,
            "payload": {},
            "error": _sanitize(f"upstream unavailable: {exc}")[:300],
        }


def summarize(result: dict) -> dict:
    payload = result.get("payload") or {}
    caller = payload.get("caller") or {}
    workspace = caller.get("workspace") or {}
    return {
        "eligible": payload.get("eligible"),
        "http_status": result.get("http_status"),
        "role": caller.get("role"),
        "workspace": workspace.get("name"),
        "permissions": len(caller.get("permissions") or []),
        "error": result.get("error"),
    }


def collect(db_path: Path | str = DEFAULT_DB) -> dict[str, dict]:
    out: dict[str, dict] = {}
    try:
        member_token = read_credential_token(db_path, MEMBER_INTEGRATION)
        out["member"] = summarize(fetch_eligibility(member_token))
    except CredentialError as exc:
        out["member"] = {
            "eligible": None,
            "http_status": None,
            "error": str(exc),
        }

    try:
        mcp_token = read_credential_token(db_path, MCP_INTEGRATION)
        out["mcp_oauth"] = summarize(fetch_eligibility(mcp_token))
        try:
            org_id = read_credential_metadata(db_path, MEMBER_INTEGRATION).get("orgID")
        except CredentialError:
            org_id = None
        if isinstance(org_id, str) and org_id:
            out["mcp_oauth_with_org"] = summarize(
                fetch_eligibility(mcp_token, org_id=org_id)
            )
    except CredentialError as exc:
        out["mcp_oauth"] = {
            "eligible": None,
            "http_status": None,
            "error": str(exc),
        }
    return out


def _format(summary: dict) -> str:
    eligible = summary.get("eligible")
    status = summary.get("http_status")
    role = summary.get("role")
    workspace = summary.get("workspace")
    permissions = summary.get("permissions")
    error = summary.get("error")
    parts = [
        f"eligible={eligible}",
        f"status={status}",
        f"role={role}",
        f"workspace={workspace}",
        f"permissions={permissions}",
    ]
    if error:
        parts.append(f"error={error}")
    return " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--json", action="store_true", help="saída JSON")
    args = parser.parse_args(argv)

    result = collect(args.db)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for label in ("member", "mcp_oauth", "mcp_oauth_with_org"):
            if label in result:
                print(f"{label:18} {_format(result[label])}")
    return 0 if result.get("member", {}).get("eligible") is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
