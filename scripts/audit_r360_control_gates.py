#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica e persiste os gates internos de controle da SPEC-935-R360.

O arquivo resultante audita SpecVerifier, BehavioralGate e a economia de falhas.
Esses mecanismos validam processo interno; não avaliam competência cultural.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from economy.token_economy import SLASH_RATE, TokenEconomy  # noqa: E402
from sdd.spec_engine import spec_registry, spec_verifier  # noqa: E402
from trust import create_trust_engine  # noqa: E402


BASE = ROOT / "validacao_externa" / "cultural_episteme"
REVIEWS_PATH = BASE / "molambudos_r360_reviews.json"
CONTROL_PATH = BASE / "molambudos_r360_control_gates.json"


def _register_criteria() -> None:
    spec = spec_registry.get("SPEC-935-R360")
    if spec is None:
        raise RuntimeError("SPEC-935-R360 não registrada")
    if spec.criteria:
        return
    spec.add_criterion("Doze pareceres runtime", lambda out: len(out.get("reviews", [])) == 12)
    spec.add_criterion(
        "Contratos runtime revalidados",
        lambda out: all(
            review.get("agent_runtime", {}).get("contract_valid") is True
            for review in out.get("reviews", [])
        ),
    )
    spec.add_criterion(
        "Release permanece bloqueado",
        lambda out: all(
            review.get("gate", {}).get("release_gate") == "blocked"
            for review in out.get("reviews", [])
        ),
    )
    spec.add_criterion(
        "Nenhuma edição automática",
        lambda out: out.get("manuscript_edits_applied") is False
        and not out.get("aggregate", {}).get("automatic_changes"),
    )
    spec.add_criterion(
        "Sem validação externa alegada",
        lambda out: out.get("external_validation") is False,
    )
    spec.add_criterion(
        "Deltas permanecem propostos",
        lambda out: bool(out.get("aggregate", {}).get("proposed_terminology_deltas"))
        and all(
            delta.get("approval_state") == "proposed"
            for delta in out["aggregate"]["proposed_terminology_deltas"]
        ),
    )


def _audit_economy() -> dict:
    economy = TokenEconomy()
    failures = [
        ("marceloclaro", "r360-generator-import-path", 1.0),
        ("marceloclaro", "r360-generator-concern-arity", 1.0),
        ("cultural-episteme-agent", "ses_041c58ee0ffe1rdzZRje394SWa-invalid-delta", 1.0),
        ("cultural-episteme-agent", "ses_041c58d74ffeRVhN4opcWtY3bh-invalid-delta", 1.0),
    ]
    successes = [
        ("cultural-episteme-agent", "ses_041c58ee0ffe1rdzZRje394SWa-corrected", 1.0),
        ("cultural-episteme-agent", "ses_041c58d74ffeRVhN4opcWtY3bh-corrected", 1.0),
        ("marceloclaro", "SPEC-935-R360-final-gates", 2.0),
    ]
    failed_outcomes = []
    successful_outcomes = []
    for agent_id, task_id, stake in failures:
        position = economy.commit(agent_id, task_id, stake)
        if position is None:
            raise RuntimeError(f"stake não criado para falha {task_id}")
        failed_outcomes.append(economy.resolve(task_id, success=False))
    for agent_id, task_id, stake in successes:
        position = economy.commit(agent_id, task_id, stake)
        if position is None:
            raise RuntimeError(f"stake não criado para sucesso {task_id}")
        successful_outcomes.append(economy.resolve(task_id, success=True))
    return {
        "slash_rate": SLASH_RATE,
        "failures": failed_outcomes,
        "successes": successful_outcomes,
        "report": economy.report(),
        "balances": {
            "marceloclaro": economy.balance("marceloclaro"),
            "cultural-episteme-agent": economy.balance("cultural-episteme-agent"),
        },
        "audit_trail": economy.ledger.audit_trail(),
    }


def main() -> None:
    artifact = json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))
    _register_criteria()
    sdd_gate = spec_verifier.verify("SPEC-935-R360", artifact)
    if not sdd_gate["verified"]:
        raise RuntimeError(f"SpecVerifier reprovou: {sdd_gate}")

    trust = create_trust_engine()
    behavioral = trust.execute("r360_finalize_internal_dossier", required_trust=0.4)
    if not behavioral.allowed:
        raise RuntimeError(f"BehavioralGate bloqueou: {behavioral.reason}")
    trust_outcome = trust.learn(
        "r360_finalize_internal_dossier",
        success=True,
        delta=0.1,
        context="12 envelopes válidos, 36 testes de regressão e release cultural bloqueado",
    )

    control = {
        "spec_id": "SPEC-935-R360",
        "generated_at": "2026-08-01",
        "external_validation": False,
        "sdd_gate": sdd_gate,
        "behavioral_gate": asdict(behavioral),
        "trust_outcome": asdict(trust_outcome),
        "trust_status": trust.status,
        "token_economy": _audit_economy(),
        "release_gate": "blocked",
        "human_review_required": True,
        "safe_claim": "Os gates internos de processo passaram após slashing das falhas recuperáveis; isso não valida equivalência cultural, história ou qualidade literária.",
    }
    CONTROL_PATH.write_text(
        json.dumps(control, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("R360 control gates: SDD 6/6; BehavioralGate allowed; 4 stakes slashed.")


if __name__ == "__main__":
    main()
