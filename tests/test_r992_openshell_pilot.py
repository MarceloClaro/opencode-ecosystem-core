"""R992: preflight/evidência do piloto OpenShell — hermético, sem Podman/CLI."""
import importlib
import json

import pytest


def pilot():
    assert importlib.util.find_spec("integrations.openshell_pilot"), "Módulo R992 ausente"
    return importlib.import_module("integrations.openshell_pilot")


def test_preflight_never_claims_isolation(monkeypatch):
    monkeypatch.setattr(pilot().shutil, "which", lambda name: None)
    result = pilot().preflight()
    assert result["openshell_cli"] is None
    assert result["sandbox_executed"] is False and result["isolation_verified"] is False
    assert result["isolation_scope"] == "none_observed"
    assert result["external_validation"] is False and result["confidence_promoted"] is False


def test_test_plan_has_positive_and_negative_controls_for_all_targets():
    plan = pilot().isolation_test_plan()
    targets = {item["target"] for item in plan}
    assert {"egress", "filesystem", "credentials", "telemetry", "lifecycle"}.issubset(targets)
    for item in plan:
        assert item["positive"] and item["negative"]
        assert item["observed"] is None  # nada executado no plano


def test_record_evidence_is_fail_closed_and_hash_aware(tmp_path):
    artifact = tmp_path / "log.txt"
    artifact.write_text("observação sintética", encoding="utf-8")
    receipt = pilot().record_evidence(
        phase="egress", observations=[{"id": "egress_ip", "observed": "denied_blocked"}],
        artifacts={"log": str(artifact)})
    assert receipt["sandbox_executed"] is True
    assert receipt["isolation_verified"] is False
    assert receipt["external_validation"] is False and receipt["confidence_promoted"] is False
    assert len(receipt["artifact_hashes"]["log"]) == 64


def test_record_evidence_rejects_malformed_observations():
    with pytest.raises(ValueError):
        pilot().record_evidence(phase="x", observations=[])
    with pytest.raises(ValueError):
        pilot().record_evidence(phase="x", observations=[{"id": "only-id"}])


def test_cli_preflight_available_without_fallback(monkeypatch, capsys):
    from marceloclaro import scientific_lab as cli
    assert "openshell" in cli.HELP
    monkeypatch.setattr(cli, "dispatch", lambda *a: pytest.fail("Fallback externo"))
    assert cli.main(["openshell", "preflight"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["isolation_verified"] is False
