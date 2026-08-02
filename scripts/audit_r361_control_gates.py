#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica gates internos à matriz cultural R361, sem validar tradução/história."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from economy.token_economy import SLASH_RATE, TokenEconomy  # noqa: E402
from sdd.spec_engine import spec_registry, spec_verifier  # noqa: E402
from trust import create_trust_engine  # noqa: E402


BASE = ROOT / "validacao_externa" / "cultural_episteme"
MATRIX_PATH = BASE / "molambudos_r361_decision_matrix.json"
SOURCES_PATH = BASE / "molambudos_r361_sources.json"
DRIFT_PATH = BASE / "molambudos_r361_provenance_drift.json"
CONTROL_PATH = BASE / "molambudos_r361_control_gates.json"


def _register_criteria() -> None:
    spec = spec_registry.get("SPEC-935-R361")
    if spec is None:
        raise RuntimeError("SPEC-935-R361 não registrada")
    if spec.criteria:
        return
    spec.add_criterion(
        "Cinco conceitos e dez decisões",
        lambda out: len(out.get("concepts", [])) == 5
        and len(out.get("decisions", [])) == 10,
    )
    spec.add_criterion(
        "Decisões humanas condicionais",
        lambda out: all(
            item.get("status") == "pending_human"
            and item.get("conditional_preference", {}).get("status") == "conditional"
            for item in out.get("decisions", [])
        ),
    )
    spec.add_criterion(
        "Registros substantivos e grupos independentes explicitados",
        lambda out: out.get("source_evidence_summary", {}).get("records_coverage_passed") is True
        and all(
            len(groups) >= 2
            for groups in out["source_evidence_summary"]["substantive_independent_groups_by_concept"].values()
        ),
    )
    spec.add_criterion(
        "Ausência de equivalência-alvo mantém gate fechado",
        lambda out: out.get("source_evidence_summary", {}).get("target_equivalence_count") == 0
        and out["source_evidence_summary"].get("target_equivalence_gate_passed") is False
        and out["source_evidence_summary"].get("release_allowed") is False,
    )
    spec.add_criterion(
        "Dez bloqueios históricos e éticos sem alteração automática",
        lambda out: len(out.get("historical_blockers", [])) == 10
        and all(
            item.get("status") == "blocked_author_decision"
            and item.get("automatic_change_applied") is False
            for item in out.get("historical_blockers", [])
        ),
    )
    spec.add_criterion(
        "Somente três correções mecânicas",
        lambda out: len(out.get("mechanical_changes", [])) == 3
        and all(item.get("risk_level") == "low" for item in out["mechanical_changes"])
        and all(item.get("changed") is False for item in out.get("protected_cultural_terms", [])),
    )
    spec.add_criterion(
        "Deriva R360 explicitamente encadeada",
        lambda out: out.get("drift_payload", {}).get("predecessor_spec_id") == "SPEC-935-R360"
        and out["drift_payload"].get("predecessor_artifact_mutated") is False
        and len(out["drift_payload"].get("records", [])) == 3,
    )
    spec.add_criterion(
        "Verificação operacional completa",
        lambda out: out.get("verification", {}).get("quote_normalizer_pending") == 0
        and out["verification"].get("routes", {}).get("valid") == 540
        and all(
            build.get("passed") is True
            for build in out["verification"].get("builds", {}).values()
        )
        and out["verification"].get("regression", {}).get("failed") == 0,
    )
    spec.add_criterion(
        "Release e claims permanecem bloqueados",
        lambda out: out.get("external_validation") is False
        and out.get("human_review_required") is True
        and out.get("release_gate") == "blocked"
        and out.get("quality_verdict_allowed") is False,
    )


def _audit_economy() -> dict:
    economy = TokenEconomy()
    failures = [
        ("antigravity-bridge", "r361-antigravity-pending-batch", 1.0),
        ("marceloclaro", "r361-ufpr-doi-http-429", 0.5),
        ("marceloclaro", "r361-puc-presumed-url-http-404", 0.5),
        ("marceloclaro", "r361-r360-provenance-regression", 1.0),
        ("marceloclaro", "r361-premature-internal-gate-overclaim", 1.0),
        ("marceloclaro", "r361-incomplete-ethical-blocker-inventory", 1.0),
        ("marceloclaro", "r361-lancet-http-403", 0.5),
    ]
    successes = [
        ("literary-research-scholar-phd", "ses_0419bf052ffesbTFEHQ0bQeD7S", 1.5),
        ("honest-critic-agent", "ses_0416f48e3ffekBtIj4mhAI8Zxa", 1.5),
        ("literary-ethics-trauma-phd", "ses_0416f4865ffeVhI7tPdMPiefO4", 1.5),
        ("marceloclaro", "SPEC-935-R361-final-gates", 2.0),
    ]
    failed_outcomes = []
    successful_outcomes = []
    for agent_id, task_id, stake in failures:
        if economy.commit(agent_id, task_id, stake) is None:
            raise RuntimeError(f"stake não criado para falha {task_id}")
        failed_outcomes.append(economy.resolve(task_id, success=False))
    for agent_id, task_id, stake in successes:
        if economy.commit(agent_id, task_id, stake) is None:
            raise RuntimeError(f"stake não criado para sucesso {task_id}")
        successful_outcomes.append(economy.resolve(task_id, success=True))
    return {
        "slash_rate": SLASH_RATE,
        "failures": failed_outcomes,
        "successes": successful_outcomes,
        "report": economy.report(),
        "balances": {
            agent: economy.balance(agent)
            for agent in (
                "antigravity-bridge",
                "marceloclaro",
                "literary-research-scholar-phd",
                "honest-critic-agent",
                "literary-ethics-trauma-phd",
            )
        },
        "audit_trail": economy.ledger.audit_trail(),
    }


def main() -> None:
    artifact = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    artifact["sources_payload"] = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    artifact["drift_payload"] = json.loads(DRIFT_PATH.read_text(encoding="utf-8"))
    _register_criteria()
    sdd_gate = spec_verifier.verify("SPEC-935-R361", artifact)
    if not sdd_gate["verified"]:
        raise RuntimeError(f"SpecVerifier reprovou: {sdd_gate}")

    trust = create_trust_engine()
    sdd_gate.update(
        {
            "verifier": "SpecVerifier",
            "verification_scope": "internal_spec_conformance",
            "status_scope": "sdd_tdd",
            "external_validation_conferred": False,
            "release_conferred": False,
        }
    )

    behavioral = trust.execute("r361_finalize_cultural_decision_matrix", required_trust=0.4)
    if not behavioral.allowed:
        raise RuntimeError(f"BehavioralGate bloqueou: {behavioral.reason}")
    trust_outcome = trust.learn(
        "r361_finalize_cultural_decision_matrix",
        success=True,
        delta=0.1,
        context="fontes lidas, bloqueios explícitos, cinco builds, 540 rotas e release bloqueado",
    )

    behavioral_payload = asdict(behavioral)
    behavioral_payload["opens_release"] = False
    control = {
        "spec_id": "SPEC-935-R361",
        "generated_at": "2026-08-01",
        "external_validation": False,
        "human_review_required": True,
        "release_gate": "blocked",
        "quality_verdict_allowed": False,
        "spec_lifecycle_status": sdd_gate["status"],
        "communicable_status": "internal_spec_checks_passed",
        "sdd_gate": sdd_gate,
        "source_evidence_gate": artifact["source_evidence_summary"],
        "adversarial_review_gate": {
            "anti_overclaim": {
                "task_id": "ses_0416f48e3ffekBtIj4mhAI8Zxa",
                "initial_status": "FAIL_WITH_BLOCKERS",
                "final_status": "PASS_INTERNAL_PROCESS",
                "scope": "processo interno; não qualidade nem validação externa",
            },
            "ethics": {
                "task_id": "ses_0416f4865ffeVhI7tPdMPiefO4",
                "final_status": "PASS_AS_BLOCKING_DOSSIER",
                "scope": "suficiente para bloquear; não autoriza mudança ou publicação",
            },
            "release_allowed": False,
        },
        "behavioral_gate": behavioral_payload,
        "trust_outcome": asdict(trust_outcome),
        "trust_status": trust.status,
        "token_economy": _audit_economy(),
        "safe_claim": "Checagens processuais internas passaram, mas não conferem validação externa, qualidade ou equivalência-alvo. Dez bloqueios e dez decisões humanas mantêm o release bloqueado.",
    }
    CONTROL_PATH.write_text(
        json.dumps(control, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("R361 control gates: SDD 9/9 interno; BehavioralGate sem release; 7 stakes slashed.")


if __name__ == "__main__":
    main()
