"""SPEC-935-R852: JEB Community Edition instalada e provider `jeb` fechado.

O provider `jeb` deixa de ser "pendente por licença comercial": a JEB CE é
gratuita, o download oficial não exige conta, e o MCP nativo (`jeb-mcp-server`
1.3.0) reproduz exatamente a versão verificada pelo REA 6.4.0 (JEB 5.48.0).
A EULA foi aceita pelo licenciado (operador); a chave de máquina não é gravada.
Nada é promovido: `externally_validated=false`, `confidence_promoted=false`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations import rea_layers

ROOT = Path(__file__).resolve().parents[1]
R852 = ROOT / "outputs" / "core-r852"

# Nenhuma licença de máquina deve ser copiada para este teste ou para recibos.


def _receipt():
    return json.loads((R852 / "install-receipt.json").read_text())


def _evidence():
    return json.loads((R852 / "live-evidence.json").read_text())


# --- recibo de instalação -----------------------------------------------------

def test_receipt_artifact_integrity_and_origin():
    r = _receipt()
    assert r["action"] == "install_jeb_ce"
    a = r["artifact"]
    assert a["version"] == "5.48.0.202610071539"
    assert a["build_type"] == "jeb-ce"
    assert a["bytes"] == 697549250
    assert a["sha256"] == "709e7fe8e88bb0e9e2bc03b028f8b9fc78cec0289d04abe54fc26cda6369e175"
    assert a["integrity_verified"] is True
    assert a["download_requires_account"] is False
    assert a["install_path"].endswith("jeb-ce-5.48.0")


def test_receipt_mcp_matches_verified_server_pair():
    r = _receipt()
    m = r["mcp"]
    assert m["server"] == "jeb-mcp-server"
    assert m["server_version"] == "1.3.0"
    assert m["endpoint"] == "http://127.0.0.1:8425/mcp"
    assert m["rei_env"] == "REA_JEB_MCP_URL"
    assert m["protocol_version"] == "2024-11-05"


def test_receipt_never_records_the_machine_license_key():
    r = _receipt()
    assert r["activation"]["license_key_recorded_in_receipt"] is False
    forbidden = {"license_key", "activation_key", "registration_key"}
    def check(value):
        if isinstance(value, dict):
            assert forbidden.isdisjoint({str(key).lower() for key in value})
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(r)


def test_receipt_flags_not_promoted():
    assert _receipt()["flags"] == {"externally_validated": False, "confidence_promoted": False}


# --- evidência real de análise ------------------------------------------------

def test_live_evidence_provider_and_subject():
    e = _evidence()
    assert e["provider"]["id"] == "jeb"
    assert e["provider"]["version"] == "5.48.0.202610071539"
    assert e["provider"]["endpoint"] == "http://127.0.0.1:8425/mcp"
    assert e["subject"]["sha256"] == "bc50349dc46a1225e40307d2a3b54ec65775478f3358510ca4df507c0935cabd"
    assert e["subject"]["format"] == "elf"


def test_live_evidence_units_and_decompilation():
    e = _evidence()
    obs = {o["operation"]: o for o in e["observations"] if o["operation"] != "decompile_jeb_item"}
    decompiles = [o for o in e["observations"] if o["operation"] == "decompile_jeb_item"]
    assert all(o["evidence_id"].startswith("ev_") for o in e["observations"])
    units = obs["list_jeb_units"]["units"]
    assert {"soma/soma", "soma/soma/x86_64-image"} <= {u["unit_path"] for u in units}
    texts = {d["parameters"]["item_address"]: d["text"] for d in decompiles}
    assert "param1 + param0" in texts["soma"]
    assert "soma(2, 3)" in texts["main"]
    assert obs["inspect_jeb_client"]["raw_result"]["gui_client"] is False


def test_live_evidence_declares_engine_limits_and_headless_gap():
    e = _evidence()
    assert e["engine_limitations"]
    joined = " ".join(e["engine_limitations"]) + " " + e["engine_start"]["note"]
    assert "open_project" in joined  # recusa preservada, não silenciada
    assert e["flags"] == {"externally_validated": False, "confidence_promoted": False}


# --- gate fail-closed do Core -------------------------------------------------

def test_jeb_gate_requires_explicit_local_configuration(monkeypatch):
    monkeypatch.setattr(rea_layers, "_DISCOVERED", {})
    monkeypatch.delenv("REA_JEB_MCP_URL", raising=False)
    assert rea_layers.probe_layer("jeb")["ready"] is False
    monkeypatch.setenv("REA_JEB_MCP_URL", "http://10.0.0.9:8425/mcp")  # remoto: rejeitado
    assert rea_layers.probe_layer("jeb")["ready"] is False
    monkeypatch.setenv("REA_JEB_MCP_URL", "http://127.0.0.1:8425/mcp")
    layer = rea_layers.probe_layer("jeb")
    assert layer["ready"] is True and layer["env"][0]["ok"] is True


def test_jeb_uses_only_documented_variable():
    layer = rea_layers.layer("jeb")
    assert [e["name"] for e in layer["env"]] == ["REA_JEB_MCP_URL"]
    assert "REA_JEB_MCP_URL" in rea_layers.REQUIREMENTS["jeb"]


def test_r843_frozen_receipt_still_records_commercial_transition():
    # histórico (R843): jeb pendente; hoje (R852) fechado — o artefato R843 é congelado.
    r843 = json.loads((ROOT / "outputs" / "core-r843" / "config-gates.json").read_text())
    assert "jeb" in r843["pending"]
