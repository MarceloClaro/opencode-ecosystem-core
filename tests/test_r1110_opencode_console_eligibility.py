"""R1110 — testes do diagnóstico de elegibilidade MCP do Console."""

from __future__ import annotations

import json
import sqlite3
import time

import pytest

from scripts import opencode_console_eligibility as elig


def _make_db(tmp_path, rows):
    db = tmp_path / "opencode.db"
    con = sqlite3.connect(db)
    con.execute(
        "create table credential ("
        "id text, integration_id text, label text, value text, "
        "connector_id text, method_id text, active integer, "
        "time_created integer, time_updated integer)"
    )
    for idx, (integration, value, active, updated) in enumerate(rows):
        con.execute(
            "insert into credential values (?,?,?,?,?,?,?,?,?)",
            (f"cred_{idx}", integration, "test", json.dumps(value), None, None,
             active, updated, updated),
        )
    con.commit()
    con.close()
    return db


def _credential(token: str, expires_ms: int) -> dict:
    return {"type": "oauth", "access": token, "expires": expires_ms}


def test_read_credential_token_returns_latest_active(tmp_path):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("old-token", now_ms + 3_600_000), 1, 1),
        ("opencode", _credential("new-token", now_ms + 3_600_000), 1, 2),
        ("opencode", _credential("inactive-token", now_ms + 3_600_000), 0, 3),
    ])

    assert elig.read_credential_token(db, "opencode") == "new-token"


def test_read_credential_token_rejects_expired(tmp_path):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("expired", now_ms - 1), 1, 1),
    ])

    with pytest.raises(elig.CredentialError, match="expired"):
        elig.read_credential_token(db, "opencode")


def test_sanitize_redacts_tokens_emails_and_ids():
    text = "Bearer st_abc123456789 user@example.com acc_01ABC wrk_01DEF"

    cleaned = elig._sanitize(text)

    assert "st_abc123456789" not in cleaned
    assert "user@example.com" not in cleaned
    assert "acc_01ABC" not in cleaned
    assert "wrk_01DEF" not in cleaned


def test_summarize_extracts_only_safe_fields():
    result = {
        "http_status": 200,
        "payload": {
            "eligible": True,
            "caller": {
                "email": "user@example.com",
                "role": "owner",
                "workspace": {"id": "wrk_01DEF", "name": "Default"},
                "permissions": ["a", "b", "c"],
            },
        },
    }

    summary = elig.summarize(result)

    assert summary == {
        "eligible": True,
        "http_status": 200,
        "role": "owner",
        "workspace": "Default",
        "permissions": 3,
        "error": None,
    }
    assert "user@example.com" not in json.dumps(summary)
    assert "wrk_01DEF" not in json.dumps(summary)


def test_collect_compares_member_and_mcp_without_leaking(tmp_path, monkeypatch):
    now_ms = int(time.time() * 1000)
    db = _make_db(tmp_path, [
        ("opencode", _credential("member-token", now_ms + 3_600_000), 1, 1),
        ("mcp_eec8489fdfd1e19a", _credential("mcp-token", now_ms + 3_600_000), 1, 2),
    ])

    def fake_fetch(token, url=elig.ELIGIBILITY_URL):
        if token == "member-token":
            return {
                "http_status": 200,
                "payload": {
                    "eligible": True,
                    "caller": {
                        "email": "user@example.com",
                        "role": "owner",
                        "workspace": {"id": "wrk_01DEF", "name": "Default"},
                        "permissions": ["a", "b"],
                    },
                },
            }
        return {"http_status": 200, "payload": {"eligible": False}}

    monkeypatch.setattr(elig, "fetch_eligibility", fake_fetch)

    result = elig.collect(db)
    assert result["member"]["eligible"] is True
    assert result["member"]["role"] == "owner"
    assert result["mcp_oauth"]["eligible"] is False

    rendered = json.dumps(result) + elig._format(result["member"])
    assert "member-token" not in rendered
    assert "mcp-token" not in rendered
    assert "user@example.com" not in rendered
    assert "wrk_01DEF" not in rendered
