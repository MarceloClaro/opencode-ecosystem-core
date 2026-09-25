# -*- coding: utf-8 -*-
"""SkillGovernance — Skill Mutation Gate (SPEC-935-R505).

Toda proposta de skill nasce:
    mode = shadow; requires_review = True; requires_tests = True;
    evidence_authority = False
Elegibilidadidade exige: reviewApproved AND testsPassing AND feynmanApproved
AND no drift. Mesmo elegível: executable = False; file_mutation = False.
A mutação real pertence ao workflow normal do repositório.
"""
from __future__ import annotations

from hermes_bridge.contracts import SkillProposal


class SkillGovernance:
    def propose(self, proposal: SkillProposal) -> SkillProposal:
        proposal.mode = "shadow"
        proposal.requires_review = True
        proposal.requires_tests = True
        proposal.evidence_authority = False
        proposal.executable = False
        proposal.file_mutation_performed = False
        return proposal

    def check_eligibility(self, proposal: SkillProposal, review_approved: bool,
                          tests_passing: bool, feynman_approved: bool,
                          no_drift: bool) -> bool:
        eligible = bool(
            review_approved and tests_passing and feynman_approved and no_drift
        )
        # A elegibilidade NUNCA executa mutação automaticamente.
        if eligible:
            proposal.executable = False
            proposal.file_mutation_performed = False
        return eligible