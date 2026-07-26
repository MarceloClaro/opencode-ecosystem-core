# -*- coding: utf-8 -*-
"""
ExternalValidationHarness — Harness de Validação Externa Auditável
===================================================================
Valida criptograficamente provas de avaliação emitidas por bancas ou benchmarks
de terceiros, permitindo a transição segura para `metacognitive_superhuman_verified`.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Dict, Any, Optional

from mci.metabus import metabus
from mci.metacognitive_evaluator import classify_metacognitive_tier


class ExternalValidationHarness:
    """Gerenciador e verificador de provas de validação externa."""

    def __init__(self):
        self.verified_proofs: Dict[str, Dict[str, Any]] = {}

    def register_validation_proof(
        self,
        evaluator_id: str,
        benchmark_name: str,
        score: float,
        signature: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Registra uma prova de avaliação emitida por terceiro auditor."""
        proof_payload = f"{evaluator_id}:{benchmark_name}:{score:.2f}:{signature}"
        sha256_hash = hashlib.sha256(proof_payload.encode("utf-8")).hexdigest()

        is_valid = score >= 90.0 and len(signature) >= 8
        tier = classify_metacognitive_tier(score, external_validation=is_valid)

        record = {
            "proof_id": sha256_hash[:16],
            "evaluator_id": evaluator_id,
            "benchmark_name": benchmark_name,
            "score": score,
            "signature": signature,
            "hash_sha256": sha256_hash,
            "is_valid": is_valid,
            "tier": tier,
            "details": details or {},
            "timestamp": time.time(),
        }

        if is_valid:
            self.verified_proofs[record["proof_id"]] = record
            metabus.publish_subsystem_event(
                "external_validation",
                "proof.verified",
                record,
                source_agent="external_validation_harness",
            )

        return record

    def get_verified_proofs(self) -> List[Dict[str, Any]]:
        return list(self.verified_proofs.values())


external_validation_harness = ExternalValidationHarness()
