# -*- coding: utf-8 -*-
"""EvidenceGuard — autoridade epistemológica (SPEC-935-R504).

Estados: OBSERVED, INFERRED, UNVERIFIED, BLOCKED.
Somente evidência direta rastreável pode promover um claim a OBSERVED.
Fontes aprendidas (policy, memória, confiança de skill) NUNCA têm essa
autoridade — replicam as invariantes do ReversaFeynman:

    TEACHBACK_GREEN != OBSERVED
    HUMAN-VALIDATED != OBSERVED
    policy confidence != OBSERVED
    reward != OBSERVED
    Hermes memory != OBSERVED
    Hermes skill confidence != OBSERVED
"""

from __future__ import annotations

from typing import Any, Dict, List

OBSERVED = "OBSERVED"
INFERRED = "INFERRED"
UNVERIFIED = "UNVERIFIED"
BLOCKED = "BLOCKED"
EPISTEMIC_STATES = {OBSERVED, INFERRED, UNVERIFIED, BLOCKED}

# Tipos de evidência direta reconhecidos (baseline ReversaFeynman)
DIRECT_EVIDENCE_KINDS = {
    "code", "contract", "test", "execution", "log", "dataset", "artifact",
}

# Fontes que NUNCA podem produzir OBSERVED (autoridade não epistêmica)
NON_EPISTEMIC_KINDS = {
    "learned-policy", "memory", "skill-confidence", "user-model",
    "session-summary", "reward", "policy-confidence",
}


class EvidenceGuard:
    """Guarda que decide se uma proposta de evidência pode promover um claim."""

    def apply_evidence_proposal(
        self,
        claim: Dict[str, Any],
        proposal: Dict[str, Any],
    ) -> Dict[str, Any]:
        source = proposal.get("source", {})
        kind = source.get("kind", "")
        direct = bool(source.get("direct", False))
        proposed = proposal.get("proposed", claim.get("epistemic_state", INFERRED))

        if proposed == OBSERVED:
            if not direct:
                raise ValueError(
                    f"fonte não-diretiva ({kind}) não pode promover claim a {OBSERVED}"
                )
            if kind in NON_EPISTEMIC_KINDS:
                raise ValueError(
                    f"fonte {kind} jamais produz {OBSERVED} (firewall epistemológico)"
                )
            if kind not in DIRECT_EVIDENCE_KINDS:
                raise ValueError(
                    f"tipo de evidência {kind!r} não reconhecido como direto"
                )
            ref = source.get("ref", "")
            if not ref:
                raise ValueError("evidência direta exige ref rastreável")

        claim = dict(claim)
        claim["epistemic_state"] = proposed
        claim["source"] = {
            "kind": kind,
            "direct": direct,
            "ref": source.get("ref"),
            "approved_by": "evidence_guard",
        }
        return claim

    def can_observe(self, source: Dict[str, Any]) -> bool:
        kind = source.get("kind", "")
        return (
            bool(source.get("direct"))
            and kind in DIRECT_EVIDENCE_KINDS
            and kind not in NON_EPISTEMIC_KINDS
            and bool(source.get("ref"))
        )