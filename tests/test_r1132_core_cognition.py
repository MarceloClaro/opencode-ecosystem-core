# -*- coding: utf-8 -*-
"""Testes da camada de cognição (SPEC-935-R1132)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from core_cognition import (
    claims_ledger,
    cognitive_function_map,
    contestability,
    epistemic_risk,
    n_of_1,
    stop_rules,
)
from core_cognition.claims_ledger import Claim
from core_cognition.doctor_checks import run_cognition_checks

ROOT = Path(__file__).resolve().parents[1]
HEX = "a" * 64


def _claim(**overrides):
    payload = {
        "claim_id": "CLAIM-001",
        "text": "O Core reduz o custo de retomada.",
        "status": "tested",
        "falsifier": "Tempo de retomada não diminui.",
        "evidence": [],
        "source_sha256": "",
        "external_validation": None,
        "history": [],
    }
    payload.update(overrides)
    return payload


def _external():
    return {
        "independent": True,
        "verifier": "Revisor independente",
        "artifact_sha256": HEX,
    }


def test_cognitive_function_map_covers_required_functions():
    functions = cognitive_function_map.load_map()
    names = {function.function for function in functions}
    assert cognitive_function_map.REQUIRED_FUNCTIONS <= names
    assert len(functions) >= 12


def test_cognitive_function_map_rejects_duplicate():
    data = [asdict(function) for function in cognitive_function_map.load_map()[:2]]
    data[1]["function"] = data[0]["function"]
    with pytest.raises(ValueError):
        cognitive_function_map.validate_map(data)


def test_cognitive_function_map_audit_passes_on_repo():
    report = cognitive_function_map.audit(ROOT)
    assert report["status"] == "pass"
    assert report["missing_modules"] == []
    assert report["missing_limits"] == []


def test_epistemic_risk_overclaim():
    findings = epistemic_risk.audit_claim(
        {
            "text": "O Core previne Alzheimer.",
            "confidence": 0.9,
            "evidence": [],
            "falsifier": "Ensaio clínico não mostra prevenção.",
            "status": "verified",
        }
    )
    assert any(
        finding.code == epistemic_risk.OVERCLAIM and finding.severity == "critical"
        for finding in findings
    )


def test_epistemic_risk_false_objectivity():
    findings = epistemic_risk.audit_claim(
        {
            "text": "O agente é confiável.",
            "confidence": 0.9,
            "evidence": [],
            "falsifier": "O agente erra em tarefa simples.",
            "status": "inference",
        },
        trust_score=0.9,
    )
    assert any(finding.code == epistemic_risk.FALSE_OBJECTIVITY for finding in findings)


def test_epistemic_risk_automation_bias():
    findings = epistemic_risk.audit_session(
        {
            "agent_output_accepted": True,
            "independent_judgment": False,
            "external_validation": False,
        }
    )
    assert any(finding.code == epistemic_risk.AUTOMATION_BIAS for finding in findings)


def test_epistemic_risk_deskilling():
    findings = epistemic_risk.audit_session(
        {"manual_verifications": 0, "sessions_without_manual": 5}
    )
    assert any(finding.code == epistemic_risk.DESKILLING for finding in findings)


def test_epistemic_risk_maintenance_overload():
    findings = epistemic_risk.audit_session(
        {"maintenance_minutes": 120, "productive_minutes": 60}
    )
    assert any(finding.code == epistemic_risk.MAINTENANCE_OVERLOAD for finding in findings)


def test_epistemic_risk_evidence_hash():
    findings = epistemic_risk.audit_claim(
        {
            "text": "Evidência sem hash.",
            "confidence": 0.5,
            "evidence": [{"source_sha256": "bad", "literal_verified": False}],
            "falsifier": "A fonte não confirma.",
            "status": "inference",
        }
    )
    assert any(finding.code == epistemic_risk.EVIDENCE_WITHOUT_HASH for finding in findings)


def test_audit_repository_passes_on_repo():
    report = epistemic_risk.audit_repository(ROOT)
    assert report["status"] == "pass"
    assert report["counts"]["specs"] > 0
    assert report["counts"]["tests"] > 0
    assert report["counts"]["cycles"] > 0


def test_stop_rules_session_budget():
    decision = stop_rules.StopRules().evaluate({"session_minutes": 130})
    assert decision.action == "stop"
    assert decision.rule == "session_budget"


def test_stop_rules_consecutive_failures():
    decision = stop_rules.StopRules().evaluate({"consecutive_failures": 3})
    assert decision.action == "ask"
    assert decision.rule == "consecutive_failures"


def test_stop_rules_maintenance_ratio():
    decision = stop_rules.StopRules().evaluate(
        {"maintenance_minutes": 120, "productive_minutes": 60}
    )
    assert decision.action == "ask"
    assert decision.rule == "maintenance_ratio"


def test_stop_rules_quiet_hours():
    decision = stop_rules.StopRules().evaluate({"local_hour": 23})
    assert decision.action == "defer"
    assert decision.rule == "quiet_hours"


def test_stop_rules_user_stop():
    decision = stop_rules.StopRules().evaluate({"user_requested_stop": True})
    assert decision.action == "stop"
    assert decision.rule == "user_requested_stop"


def test_humane_default_has_four_paths():
    default = stop_rules.humane_default("session_budget")
    assert {"explanation", "alternative", "human_contact", "exit", "rule"} <= set(default)


def test_claims_ledger_valid_observation():
    claim = claims_ledger.validate_claim(_claim(status="observation"))
    assert claim.status == "observation"
    assert claim.claim_id == "CLAIM-001"


def test_claims_ledger_rejects_invalid_status():
    with pytest.raises(ValueError):
        claims_ledger.validate_claim(_claim(status="verified"))


def test_claims_ledger_promotion_requires_external_validation():
    claim = claims_ledger.validate_claim(_claim(status="tested"))
    with pytest.raises(ValueError):
        claims_ledger.promote(claim, {"independent": False, "verifier": "x", "artifact_sha256": HEX})
    promoted = claims_ledger.promote(claim, _external())
    assert promoted.status == "externally_validated"
    assert promoted.external_validation == _external()


def test_claims_ledger_detects_invalid_overclaim(tmp_path):
    path = tmp_path / "claims.jsonl"
    path.write_text(
        json.dumps(_claim(status="externally_validated", external_validation=None)) + "\n",
        encoding="utf-8",
    )
    report = claims_ledger.audit_ledger(path)
    assert report["status"] == "fail"
    assert report["invalid"]


def test_claims_overclaims_direct():
    claim = Claim(
        claim_id="CLAIM-X",
        text="x",
        status="externally_validated",
        falsifier="y",
        external_validation=None,
    )
    assert claims_ledger.overclaims([claim]) == [claim]


def test_contestability_report_passes_on_repo():
    report = contestability.audit(ROOT)
    assert report.score == 1.0
    assert report.gaps == []


def test_contestability_report_flags_missing_exit(tmp_path):
    (tmp_path / "README.md").write_text("export e distribuição", encoding="utf-8")
    (tmp_path / "MANUAL.md").write_text("export e backup", encoding="utf-8")
    (tmp_path / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (tmp_path / "CORRIGENDUM.md").write_text("correção pública", encoding="utf-8")
    (tmp_path / "mci").mkdir()
    (tmp_path / "mci" / "metacognitive_gate.py").write_text("", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    for index in range(5):
        (tmp_path / "docs" / f"doc-{index}.md").write_text("doc", encoding="utf-8")

    report = contestability.audit(tmp_path)
    assert report.score < 1.0
    assert "exit" in report.gaps


def test_n_of_1_template_valid():
    protocol = n_of_1.validate_protocol(n_of_1.template())
    assert protocol.duration_weeks == 12
    assert len(protocol.outcomes) >= 5


def test_n_of_1_rejects_missing_preregistration():
    data = n_of_1.template()
    data["pre_registration"] = False
    with pytest.raises(ValueError):
        n_of_1.validate_protocol(data)


def test_n_of_1_rejects_missing_ethics():
    data = n_of_1.template()
    data["ethics"]["consent"] = False
    with pytest.raises(ValueError):
        n_of_1.validate_protocol(data)


def test_n_of_1_summarize():
    rows = [
        {"phase": "A", "outcome": "time_to_resume", "value": 10},
        {"phase": "A", "outcome": "time_to_resume", "value": 20},
        {"phase": "B", "outcome": "time_to_resume", "value": 5},
        {"phase": "B", "outcome": "time_to_resume", "value": 15},
    ]
    summary = n_of_1.summarize(rows)
    assert summary["descriptive_only"] is True
    assert summary["outcomes"]["time_to_resume"]["mean_A"] == 15.0
    assert summary["outcomes"]["time_to_resume"]["mean_B"] == 10.0
    assert summary["outcomes"]["time_to_resume"]["delta_B_minus_A"] == -5.0


def test_doctor_checks_return_three_checks():
    checks = run_cognition_checks(ROOT)
    assert len(checks) == 3
    assert {check.name for check in checks} == {
        "cognitive_function_map",
        "epistemic_risk",
        "contestability",
    }
    assert all(check.status in {"pass", "warn", "fail"} for check in checks)
