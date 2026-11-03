"""R1015 — contraprovas offline: recibos, perfil seletivo e saúde fail-closed."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import pytest

from integrations.federation_sync import runtime
from integrations.federation_sync.probe import call_tool
from integrations.federation_sync.model import sha256_text


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "federation" / "probes").mkdir(parents=True)
    return tmp_path


def _install(root: Path, name: str) -> tuple[runtime.ServerSpec, Path, Path]:
    spec = runtime.server_specs(root)[name]
    binary = Path(spec.command[0])
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    binary.chmod(0o755)
    if spec.ecosystem == "node":
        manifest = root / runtime.INSTALL_ROOT / "node/node_modules" / spec.package / "package.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"name": spec.package, "version": spec.version}), encoding="utf-8")
    else:
        venv = "py-time" if name == "mcp-time" else f"py-{name}"
        manifest = (root / runtime.INSTALL_ROOT / venv / "lib/python3.12/site-packages"
                    / f"{spec.package.replace('-', '_')}-{spec.version}.dist-info/METADATA")
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(f"Metadata-Version: 2.3\nName: {spec.package}\nVersion: {spec.version}\n", encoding="utf-8")
    return spec, binary, manifest


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipts(root: Path, name: str, *, timestamp: str | None = None):
    spec, binary, manifest = _install(root, name)
    identity = {
        "command": list(spec.command), "env": dict(spec.env),
        "package": spec.package, "installed_version": spec.version,
        "binary_path": str(binary.resolve()), "binary_sha256": _hash(binary),
        "manifest_sha256": _hash(manifest),
    }
    now = timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tool, arguments = runtime.SMOKE_CALLS[name]
    probe = {"schema": "federation-mcp-probe/v2", "name": name, "ok": True,
             "checked_at": now, "identity": identity, "protocol_version": "2024-11-05",
             "tools_count": 1, "tools": [tool]}
    smoke = {"schema": "federation-mcp-smoke/v2", "name": name, "ok": True,
             "checked_at": now, "identity": deepcopy(identity), "tool": tool,
             "arguments": deepcopy(arguments), "result_excerpt": "ok", "result_is_error": False}
    _save(root, name, probe, smoke)
    return probe, smoke, binary, manifest


def _save(root: Path, name: str, probe: dict, smoke: dict) -> None:
    directory = root / "federation" / "probes"
    (directory / f"{name}.json").write_text(json.dumps(probe), encoding="utf-8")
    (directory / f"{name}.smoke.json").write_text(json.dumps(smoke), encoding="utf-8")


def _codes(result: dict) -> set[str]:
    return {issue["code"] for issue in result["issues"]}


def test_valid_receipts_activate_and_doctor(root: Path):
    _receipts(root, "mcp-time")
    result = runtime.activate(root, names=["mcp-time"])
    assert result["activated"] == ["mcp-time"]
    assert runtime.doctor(root)["status"] == "ok"
    assert runtime.activated_servers(root)["mcp-time"]["command"] == list(runtime.server_specs(root)["mcp-time"].command)


@pytest.mark.parametrize("tamper", ["legacy", "name", "command", "version", "manifest", "binary", "env"])
def test_activation_rejects_unbound_or_mismatched_probe(root: Path, tamper: str):
    probe, smoke, binary, manifest = _receipts(root, "mcp-time")
    if tamper == "legacy":
        del probe["identity"]
    elif tamper == "name":
        probe["name"] = "another"
    elif tamper == "command":
        probe["identity"]["command"].append("--unsafe")
    elif tamper == "version":
        manifest.write_text(manifest.read_text().replace("2026.10.28", "0.0.1"))
    elif tamper == "manifest":
        manifest.write_text(manifest.read_text() + "Changed: yes\n")
    elif tamper == "binary":
        binary.write_text("#!/bin/sh\nexit 9\n")
    elif tamper == "env":
        probe["identity"]["env"]["INJECTED"] = "1"
    _save(root, "mcp-time", probe, smoke)
    result = runtime.activate(root, names=["mcp-time"])
    assert "mcp-time" in result["blocked"]
    assert "mcp-time" not in runtime.activated_servers(root)


@pytest.mark.parametrize("timestamp", ["", "invalid", "2000-01-01T00:00:00Z", "3000-01-01T00:00:00Z"])
def test_activation_rejects_missing_old_future_or_bad_time(root: Path, timestamp: str):
    probe, smoke, _, _ = _receipts(root, "mcp-time")
    probe["checked_at"] = timestamp
    _save(root, "mcp-time", probe, smoke)
    assert "mcp-time" in runtime.activate(root, names=["mcp-time"])["blocked"]


def test_historical_v1_receipts_cannot_be_reused(root: Path):
    probe, smoke, _, _ = _receipts(root, "mcp-time")
    probe["schema"] = "federation-mcp-probe/v1"
    smoke["schema"] = "federation-mcp-smoke/v1"
    _save(root, "mcp-time", probe, smoke)
    assert "mcp-time" in runtime.activate(root, names=["mcp-time"])["blocked"]


def test_smoke_missing_or_failed_rejects_and_doctor_degrades(root: Path):
    probe, smoke, _, _ = _receipts(root, "mcp-time")
    runtime.activate(root, names=["mcp-time"])
    for bad in (None, {**smoke, "ok": False}, {**smoke, "identity": {**smoke["identity"], "binary_sha256": "0" * 64}},
                {**smoke, "tool": "unrelated"}, {**smoke, "checked_at": "2000-01-01T00:00:00Z"},
                {**smoke, "result_is_error": True}):
        _save(root, "mcp-time", probe, smoke)
        runtime.activate(root, names=["mcp-time"])
        if bad is None:
            (root / "federation/probes/mcp-time.smoke.json").unlink(missing_ok=True)
        else:
            _save(root, "mcp-time", probe, bad)
        assert runtime.doctor(root)["status"] == "degraded"
        assert runtime.activated_servers(root) == {}
        assert "mcp-time" in runtime.activate(root, names=["mcp-time"])["blocked"]


def test_doctor_rejects_identity_changed_after_activation(root: Path):
    _, _, binary, _ = _receipts(root, "mcp-time")
    runtime.activate(root, names=["mcp-time"])
    binary.write_text("alterado")
    assert runtime.doctor(root)["status"] == "degraded"
    assert runtime.activated_servers(root) == {}


def test_activated_json_tampering_is_not_imported_into_config(root: Path):
    _receipts(root, "mcp-time")
    runtime.activate(root, names=["mcp-time"])
    path = root / "federation/activated.json"
    document = json.loads(path.read_text())
    document["servers"]["mcp-time"]["command"] = ["/tmp/unsafe"]
    document["digest"] = sha256_text(json.dumps({"servers": document["servers"],
                                                "provenance": document["provenance"]}, sort_keys=True))
    path.write_text(json.dumps(document))
    assert runtime.activated_servers(root) == {}
    assert runtime.doctor(root)["status"] == "degraded"


def test_provenance_tampering_is_detected_by_document_digest(root: Path):
    _receipts(root, "mcp-time")
    runtime.activate(root, names=["mcp-time"])
    path = root / "federation/activated.json"
    document = json.loads(path.read_text())
    document["provenance"]["mcp-time"]["version"] = "adulterada"
    path.write_text(json.dumps(document))
    assert runtime.doctor(root)["status"] == "degraded"
    assert runtime.activated_servers(root) == {}


def test_v1_activation_document_is_migrated_without_reusing_old_receipts(root: Path):
    _receipts(root, "mcp-time")
    runtime.activate(root, names=["mcp-time"])
    path = root / "federation/activated.json"
    document = json.loads(path.read_text())
    document["schema"] = "federation-activated-mcp/v1"
    document["digest"] = sha256_text(json.dumps(document["servers"], sort_keys=True))
    path.write_text(json.dumps(document))
    assert runtime.doctor(root)["status"] == "degraded"
    assert runtime.activated_servers(root) == {}
    runtime.activate(root, names=["mcp-time"])
    assert json.loads(path.read_text())["schema"] == runtime.ACTIVATED_SCHEMA
    assert runtime.doctor(root)["status"] == "ok"


def test_partial_activation_preserves_other_servers_and_profile(root: Path):
    _receipts(root, "mcp-time")
    _receipts(root, "mcp-memory")
    assert runtime.activate(root, names=["mcp-time"])["activated"] == ["mcp-time"]
    result = runtime.activate(root, names=["mcp-memory", "chroma"])
    assert set(result["activated"]) == {"mcp-time", "mcp-memory"}
    assert "chroma" in result["blocked"]
    assert set(runtime.activated_servers(root)) == {"mcp-time", "mcp-memory"}
    runtime.deactivate(root, names=["mcp-time"])
    assert set(runtime.activated_servers(root)) == {"mcp-memory"}
    assert "mcp-everything" not in runtime.DEFAULT_SERVERS
    assert "executeautomation-playwright" not in runtime.DEFAULT_SERVERS


@pytest.mark.parametrize("name", ["mcp-everything", "executeautomation-playwright"])
def test_optional_server_can_be_reenabled_explicitly(root: Path, name: str):
    _receipts(root, name)
    assert name not in runtime.activate(root)["activated"]
    assert name in runtime.activate(root, names=[name])["activated"]
    assert name in runtime.server_specs(root)


def test_default_activation_does_not_erase_explicit_optional_choice(root: Path):
    _receipts(root, "mcp-everything")
    runtime.activate(root, names=["mcp-everything"])
    # Sem --ids, tenta só seis padrões; preserva opção explicitamente ativa.
    runtime.activate(root)
    assert "mcp-everything" in runtime.activated_servers(root)


def test_qdrant_http_environment_is_passed_to_active_config(root: Path):
    _receipts(root, "qdrant")
    assert "qdrant" in runtime.activate(root, names=["qdrant"])["activated"]
    entry = runtime.activated_servers(root)["qdrant"]
    assert entry["environment"]["QDRANT_URL"] == "http://127.0.0.1:6333"
    assert "QDRANT_LOCAL_PATH" not in entry["environment"]


def test_expired_smoke_and_probe_reject_in_doctor(root: Path):
    probe, smoke, _, _ = _receipts(root, "mcp-time")
    runtime.activate(root, names=["mcp-time"])
    probe["checked_at"] = "2000-01-01T00:00:00Z"
    _save(root, "mcp-time", probe, smoke)
    assert "probe_invalid" in _codes(runtime.doctor(root))
    assert runtime.activated_servers(root) == {}


def test_doctor_reports_stale_host_config_without_receipts(root: Path):
    (root / "opencode.json").write_text(json.dumps({"mcp": {"mcp-everything": {"type": "local"}}}))
    result = runtime.doctor(root)
    assert result["status"] == "degraded"
    assert "config_stale_or_unverified" in _codes(result)


def test_symlink_outside_installation_is_rejected(root: Path, tmp_path: Path):
    probe, smoke, binary, _ = _receipts(root, "mcp-time")
    binary.unlink()
    outside = tmp_path.parent / "foreign-mcp-binary"
    outside.write_text("#!/bin/sh\nexit 0\n")
    binary.symlink_to(outside)
    _save(root, "mcp-time", probe, smoke)
    assert "mcp-time" in runtime.activate(root, names=["mcp-time"])["blocked"]


def test_tool_level_error_is_not_reported_as_success(tmp_path: Path):
    script = tmp_path / "error_server.py"
    script.write_text('''import json, sys
for line in sys.stdin:
 m = json.loads(line)
 if m.get("method") == "initialize":
  print(json.dumps({"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05"}}),flush=True)
 if m.get("method") == "tools/call":
  print(json.dumps({"jsonrpc":"2.0","id":2,"result":{"isError":True,"content":[{"type":"text","text":"falhou"}]}}),flush=True)
''')
    result = call_tool([sys.executable, str(script)], "ping", {}, timeout=5)
    assert not result["ok"]
    assert "falhou" in result["error"]
