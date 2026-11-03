# -*- coding: utf-8 -*-
"""SPEC-935-R1014 — prova de protocolo e ativação MCP com recibo.

Testes offline: usam um servidor MCP falso local; nenhum pacote é baixado.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from integrations.federation_sync import runtime
from integrations.federation_sync.probe import probe

FAKE_SERVER = '''\
import json, sys
for line in sys.stdin:
    try:
        message = json.loads(line)
    except ValueError:
        continue
    method = message.get("method")
    if method == "initialize":
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "fake", "version": "0.0.1"}}}), flush=True)
    elif method == "tools/list":
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": {
            "tools": [{"name": "ping"}, {"name": "echo"}]}}), flush=True)
    elif method == "tools/call":
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": {
            "content": [{"type": "text", "text": "pong"}]}}), flush=True)
'''


@pytest.fixture()
def fake_server(tmp_path: Path) -> Path:
    path = tmp_path / "fake_mcp.py"
    path.write_text(FAKE_SERVER, encoding="utf-8")
    return path


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "federation").mkdir(parents=True)
    (root / "opencode.json").write_text(json.dumps({"mcp": {}}), encoding="utf-8")
    return root


# ── probe ───────────────────────────────────────────────────────────────────
def test_probe_handshake_and_tools(fake_server: Path):
    result = probe([sys.executable, str(fake_server)], timeout=20)
    assert result["ok"] is True
    assert result["protocol_version"] == "2024-11-05"
    assert result["server"]["name"] == "fake"
    assert result["tools"] == ["ping", "echo"]
    assert result["tools_count"] == 2


def test_probe_fails_when_process_exits(tmp_path: Path):
    script = tmp_path / "boom.py"
    script.write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
    result = probe([sys.executable, str(script)], timeout=10)
    assert result["ok"] is False
    assert "initialize" in result["error"]


def test_probe_ignores_non_json_banner(tmp_path: Path):
    script = tmp_path / "banner.py"
    script.write_text(
        "print('Successfully initialized Chroma client', flush=True)\n" + FAKE_SERVER,
        encoding="utf-8",
    )
    result = probe([sys.executable, str(script)], timeout=20)
    assert result["ok"] is True
    assert result["tools_count"] == 2


# ── registro de servidores ──────────────────────────────────────────────────
def test_all_eight_specs_are_declared(repo: Path):
    specs = runtime.server_specs(repo)
    assert set(specs) == {
        "chroma", "context7", "executeautomation-playwright", "mcp-everything",
        "mcp-memory", "mcp-time", "playwright", "qdrant",
    }
    for spec in specs.values():
        assert spec.version
        assert spec.license
        assert spec.command[0].startswith(str(repo))


# ── ativação ────────────────────────────────────────────────────────────────
def _touch_binary(repo: Path, name: str) -> None:
    spec = runtime.server_specs(repo)[name]
    path = Path(spec.command[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


def _ready(repo: Path, name: str) -> dict:
    """Instalação e recibos novos coerentes; os testes negativos os alteram."""

    _touch_binary(repo, name)
    spec = runtime.server_specs(repo)[name]
    if spec.ecosystem == "node":
        manifest = repo / runtime.INSTALL_ROOT / "node/node_modules" / spec.package / "package.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"name": spec.package, "version": spec.version}), encoding="utf-8")
    else:
        venv = "py-time" if name == "mcp-time" else f"py-{name}"
        manifest = (repo / runtime.INSTALL_ROOT / venv / "lib/python3.12/site-packages"
                    / f"{spec.package.replace('-', '_')}-{spec.version}.dist-info/METADATA")
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(f"Name: {spec.package}\nVersion: {spec.version}\n", encoding="utf-8")
    identity = runtime.installation_identity(repo, spec)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tool, args = runtime.SMOKE_CALLS[name]
    probe_receipt = {"schema": runtime.PROBE_SCHEMA, "name": name, "ok": True,
                     "checked_at": timestamp, "identity": identity,
                     "tools_count": 1, "tools": [tool], "protocol_version": "2024-11-05"}
    smoke_receipt = {"schema": runtime.SMOKE_SCHEMA, "name": name, "ok": True,
                     "checked_at": timestamp, "identity": identity,
                     "tool": tool, "arguments": args, "result_is_error": False}
    directory = repo / "federation/probes"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.json").write_text(json.dumps(probe_receipt), encoding="utf-8")
    (directory / f"{name}.smoke.json").write_text(json.dumps(smoke_receipt), encoding="utf-8")
    return probe_receipt


def test_activate_requires_probe_ok(repo: Path):
    _touch_binary(repo, "mcp-time")
    result = runtime.activate(repo, names=["mcp-time"], probes={})
    assert result["activated"] == []
    assert "mcp-time" in result["blocked"]
    stored = json.loads((repo / "federation" / "activated.json").read_text())
    assert stored["servers"] == {}


def test_activate_writes_entry_and_provenance(repo: Path):
    _ready(repo, "mcp-time")
    result = runtime.activate(repo, names=["mcp-time"])
    assert result["activated"] == ["mcp-time"]
    document = json.loads((repo / "federation" / "activated.json").read_text())
    entry = document["servers"]["mcp-time"]
    assert entry["enabled"] is True
    assert entry["command"][0].endswith("mcp-server-time")
    assert document["provenance"]["mcp-time"]["version"] == "2026.10.28"
    assert len(document["digest"]) == 64


def test_activate_blocks_missing_binary(repo: Path):
    probes = {"mcp-time": {"ok": True, "tools_count": 2}}
    result = runtime.activate(repo, names=["mcp-time"], probes=probes)
    assert result["activated"] == []
    assert "binário ausente" in result["blocked"]["mcp-time"]


def test_deactivate_removes_entry(repo: Path):
    _ready(repo, "mcp-time")
    runtime.activate(repo, names=["mcp-time"])
    result = runtime.deactivate(repo, names=["mcp-time"])
    assert result["removed"] == ["mcp-time"]
    assert runtime.activated_servers(repo) == {}


# ── doctor ──────────────────────────────────────────────────────────────────
def test_doctor_flags_missing_binary(repo: Path):
    _ready(repo, "mcp-time")
    runtime.activate(repo, names=["mcp-time"])
    Path(runtime.server_specs(repo)["mcp-time"].command[0]).unlink()
    result = runtime.doctor(repo)
    assert result["status"] == "degraded"
    assert any(issue["code"] == "installation_invalid" for issue in result["issues"])


def test_doctor_ok_with_binary_and_probe(repo: Path):
    _ready(repo, "mcp-time")
    runtime.activate(repo, names=["mcp-time"])
    result = runtime.doctor(repo)
    assert result["status"] == "ok"
    assert result["activated"] == 1


# ── smoke ───────────────────────────────────────────────────────────────────
def test_smoke_calls_declared_tool(repo: Path, fake_server: Path, monkeypatch):
    _ready(repo, "mcp-time")
    spec = runtime.server_specs(repo)["mcp-time"]
    binary = Path(spec.command[0])
    binary.write_text(f"#!{sys.executable}\n" + fake_server.read_text(encoding="utf-8"))
    binary.chmod(0o755)
    monkeypatch.setitem(runtime.SMOKE_CALLS, "mcp-time", ("ping", {}))
    receipts = runtime.smoke(repo, names=["mcp-time"])
    assert receipts["mcp-time"]["ok"] is True
    assert receipts["mcp-time"]["tool"] == "ping"
    assert "pong" in receipts["mcp-time"]["result_excerpt"]
    assert (repo / "federation" / "probes" / "mcp-time.smoke.json").is_file()


def test_real_fake_protocol_writes_bound_probe_and_smoke(repo: Path, fake_server: Path, monkeypatch):
    _ready(repo, "mcp-time")
    binary = Path(runtime.server_specs(repo)["mcp-time"].command[0])
    binary.write_text(f"#!{sys.executable}\n" + fake_server.read_text(encoding="utf-8"))
    binary.chmod(0o755)
    monkeypatch.setitem(runtime.SMOKE_CALLS, "mcp-time", ("ping", {}))
    probe_receipt = runtime.probe_all(repo, names=["mcp-time"])["mcp-time"]
    smoke_receipt = runtime.smoke(repo, names=["mcp-time"])["mcp-time"]
    assert probe_receipt["identity"]["binary_sha256"] == smoke_receipt["identity"]["binary_sha256"]
    assert smoke_receipt["result_is_error"] is False
    assert runtime.activate(repo, names=["mcp-time"])["activated"] == ["mcp-time"]


def test_smoke_does_not_write_browser_artifacts_into_checkout(repo: Path, fake_server: Path, monkeypatch):
    _ready(repo, "mcp-time")
    binary = Path(runtime.server_specs(repo)["mcp-time"].command[0])
    # Imita servidor que grava arquivo no cwd durante tools/call.
    source = fake_server.read_text(encoding="utf-8").replace(
        '    elif method == "tools/call":\n',
        '    elif method == "tools/call":\n'
        '        from pathlib import Path\n'
        '        Path(".playwright-mcp").mkdir(exist_ok=True)\n'
        '        Path(".playwright-mcp/smoke.yml").write_text("gerado")\n',
    )
    binary.write_text(f"#!{sys.executable}\n" + source, encoding="utf-8")
    binary.chmod(0o755)
    monkeypatch.setitem(runtime.SMOKE_CALLS, "mcp-time", ("ping", {}))
    assert runtime.smoke(repo, names=["mcp-time"])["mcp-time"]["ok"]
    assert not (repo / ".playwright-mcp").exists()
