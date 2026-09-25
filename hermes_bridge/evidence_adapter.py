# -*- coding: utf-8 -*-
"""EvidenceAdapter — ExecutionResult → EvidenceGuard (SPEC-935-R505).

Execução bem-sucedida NÃO basta para produzir OBSERVED:
    ExecutionResult
        -> direct_evidence[]
        -> kind reconhecido + ref rastreável
        -> claim_id explícito
        -> Evidence Proposal
        -> EvidenceGuard (R504)
        -> OBSERVED somente se aceito
Sem claim_id mapeado, a proposta nunca é OBSERVED.
"""
from __future__ import annotations

from hermes_bridge.contracts import ExecutionResult


class EvidenceAdapter:
    def to_evidence_proposal(self, result: ExecutionResult) -> dict:
        evidence = result.direct_evidence or []
        source = None
        for ev in evidence:
            if ev.get("kind") and ev.get("ref"):
                source = {"kind": ev["kind"], "direct": True, "ref": ev["ref"]}
                break
        if source is None:
            source = {"kind": "execution", "direct": False, "ref": None}
        proposed = "OBSERVED" if (result.claim_id and source["direct"]) else "INFERRED"
        return {
            "claim_id": result.claim_id,
            "proposed": proposed,
            "source": source,
            "success": result.success,
        }