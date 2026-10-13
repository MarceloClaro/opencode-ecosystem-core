"""SPEC-935-R844: instalação verificada do Hopper demo e prova real de análise.

A instalação foi a ação `install_hopper` planejada pelo próprio REA; o `pkexec`
falhou sem sessão gráfica (code=authorization_or_package_manager_failed), então a
remediação oficial ("install the planned Hopper package ... then rerun rea setup")
foi aplicada com o pacote oficial verificado por bytes e SHA-1. Nada é promovido:
`externally_validated=false`, `confidence_promoted=false`.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from integrations import rea_layers

ROOT = Path(__file__).resolve().parents[1]
R844 = ROOT / "outputs" / "core-r844"


def _receipt():
    return json.loads((R844 / "install-receipt.json").read_text())


def test_install_receipt_matches_planned_action_integrity():
    r = _receipt()
    assert r["action"] == "install_hopper"
    assert r["artifact"]["bytes"] == 35755772
    assert r["artifact"]["sha1"] == "e4f79dff602648a8ff4a88b773875b6bfac0dc65"
    assert r["artifact"]["integrity_verified"] is True
    assert r["launcher"] == "/opt/hopper/bin/Hopper"
    assert r["flags"] == {"externally_validated": False, "confidence_promoted": False}


def test_install_receipt_records_pkexec_failure_and_remediation():
    r = _receipt()
    assert "authorization_or_package_manager_failed" in r["reason_pkexec"]
    assert "install the planned Hopper package" in r["remediation_applied"]


def test_live_evidence_proves_real_hopper_analysis():
    e = json.loads((R844 / "live-evidence.json").read_text())
    assert e["provider"]["id"] == "hopper"
    assert e["evidence_id"].startswith("ev_")
    assert e["function"]["name"] == "soma"
    assert e["function"]["signature"] == "int soma(int arg0, int arg1)"
    assert "return rax" in e["pseudocode"]
    assert any("endbr64" in line for line in e["assembly"])
    assert e["callers"] == ["main"]
    assert e["authority"] == "shipped-artifact" and e["confidence"] == "observed"
    assert e["flags"] == {"externally_validated": False, "confidence_promoted": False}


def test_live_evidence_hashes_are_recorded():
    e = json.loads((R844 / "live-evidence.json").read_text())
    assert len(e["response_sha256"]) == 64
    assert e["limitations"]  # limitações declaradas pelo engine, não omitidas


@pytest.mark.skipif(not (rea_layers.engine_environment().get("HOPPER_LAUNCHER_PATH")
                         or shutil.which("Hopper")
                         or Path("/opt/hopper/bin/Hopper").exists()),
                    reason="Hopper ausente no host")
def test_host_hopper_layer_ready_after_install():
    assert rea_layers.probe_layer("native_hopper")["ready"] is True
