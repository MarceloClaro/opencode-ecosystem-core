"""
OpenCode Deep Think Engine — SPEC-935-R443
===========================================
Motor de raciocínio profundo com alocação dinâmica de Test-Time Compute
inspirado no Gemini Deep Think do Google DeepMind.

Explora trajetórias locais de resolução, executa auto-crítica
e poda de ramos inconsistentes, selecionando a derivação de maior rigor.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

from integrations.deepmind.alphaproof_engine import OpenCodeAlphaProof
from integrations.deepmind.formal_verifier import FormalProofVerifier
from integrations.deepmind.imobench_harness import GradingHeadDeepMind, IMOProblem


@dataclass
class ReasoningTrajectory:
    """Trajetória individual de raciocínio profundo."""
    trajectory_id: int
    approach_name: str
    thinking_trace: str
    candidate_answer: str
    grade_score_0_to_7: int
    is_valid: bool
    verified_steps: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    verification: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trajectory_id": self.trajectory_id,
            "approach_name": self.approach_name,
            "thinking_trace": self.thinking_trace,
            "candidate_answer": self.candidate_answer,
            "grade_score_0_to_7": self.grade_score_0_to_7,
            "is_valid": self.is_valid,
            "verified_steps": self.verified_steps,
            "latency_ms": round(self.latency_ms, 2),
            "verification": self.verification,
        }


class OpenCodeDeepThink:
    """Motor de raciocínio com busca e alocação de computação em tempo de teste."""

    def __init__(
        self,
        verifier: FormalProofVerifier | None = None,
        alphaproof: OpenCodeAlphaProof | None = None,
    ) -> None:
        self.verifier = verifier or FormalProofVerifier()
        self.alphaproof = alphaproof or OpenCodeAlphaProof(verifier=self.verifier)
        self.grading_head = GradingHeadDeepMind()

    def _verify_candidate(self, claim: str, candidate: dict) -> dict:
        """Reexecuta a identidade original; nenhum sinal textual fecha o gate."""
        receipt = {"claim": claim, "claim_sha256": hashlib.sha256(claim.encode()).hexdigest(),
                   "backend": None, "execution_performed": False, "verified": False,
                   "method": "restricted_symbolic_identity", "calibrated": False,
                   "externally_validated": False,
                   "limitation": "Somente identidades algébricas com SymPy disponível são aceitas neste consumidor."}
        if (candidate.get("is_proven") is not True or candidate.get("proof_status") != "proven"
                or candidate.get("theorem") != claim):
            receipt["message"] = "O candidato não demonstrou a mesma alegação de entrada."
        elif self.verifier.has_sympy is not True:
            receipt["message"] = "Backend simbólico indisponível; fallback textual não é promovido."
        else:
            equation = FormalProofVerifier._split_algebraic_equation(claim)
            if equation is None:
                receipt["message"] = "A alegação está fora do fragmento de identidade algébrica."
            else:
                receipt.update(backend="sympy", execution_performed=True)
                try:
                    confirmed, message = self.verifier.verify_algebraic_identity(*equation)
                    receipt.update(verified=confirmed is True, message=message)
                except (ArithmeticError, RuntimeError, TypeError, ValueError) as error:
                    receipt["message"] = "Verificação falhou: " + type(error).__name__
        receipt["receipt_sha256"] = hashlib.sha256(json.dumps(
            receipt, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        return receipt

    def think(
        self,
        problem_statement: str,
        domain: str = "general",
        compute_budget: int = 3,
        target_confidence: float = 0.95,
    ) -> dict[str, Any]:
        """Busca local com verificação vinculada à entrada, sem probabilidade calibrada.

        As tentativas são sequenciais sobre o mesmo prover; seus nomes não
        demonstram diversidade independente de raciocínio. target_confidence
        é preservado na assinatura, mas não constitui limiar de aceitação.
        """
        start_time = time.time()
        trajectories: list[ReasoningTrajectory] = []
        approaches = [
            "Decomposição Estrutural & Lemas",
            "Análise de Invariantes & Casos de Borda",
            "Equivalência Algébrica & Redução Simbólica",
            "Redução ao Absurdo & Falsificação Popperiana",
            "Síntese Direta e Verificação",
        ]
        active_approaches = approaches[:max(1, min(len(approaches), compute_budget))]
        for idx, name in enumerate(active_approaches, start=1):
            started = time.time()
            candidate = self.alphaproof.search_proof(problem_statement)
            verification = self._verify_candidate(problem_statement, candidate)
            confirmed = verification["verified"] is True
            steps = [problem_statement] if confirmed else []
            trace = (f"=== [Tentativa local {idx}: {name}] ===\n"
                     f"Alegação examinada: {problem_statement}\n"
                     f"Resultado do verificador: {verification['message']}\n"
                     "A ausência de prova não demonstra falsidade nem ausência de contraexemplos.")
            answer = (f"Identidade algébrica confirmada no fragmento local: {problem_statement}"
                      if confirmed else f"Alegação pendente de demonstração: {problem_statement}")
            public = IMOProblem(problem_id=f"deepthink-task-{idx}", problem_text=problem_statement,
                                short_answer="", category=domain).solver_input()
            grade, _ = self.grading_head.grade(public, "\n".join(steps) if steps else answer)
            trajectories.append(ReasoningTrajectory(
                trajectory_id=idx, approach_name=name, thinking_trace=trace,
                candidate_answer=answer, grade_score_0_to_7=grade, is_valid=confirmed,
                verified_steps=steps, latency_ms=(time.time() - started) * 1000,
                verification=verification))
        # A validade vem do verificador; a heurística apenas desempata tentativas.
        best = max(trajectories, key=lambda item: (item.is_valid, item.grade_score_0_to_7, -item.latency_ms))
        trace = "\n\n".join(item.thinking_trace for item in trajectories)
        status = "proven" if best.is_valid else "unproven"
        heading = "Identidade confirmada no escopo local" if best.is_valid else "Demonstração pendente"
        final_answer = (f"<think>\n{trace}\n\n[Deep Think Decision]: Tentativa {best.trajectory_id}; "
                        f"heurística textual {best.grade_score_0_to_7}/7, não calibrada.\n</think>\n\n"
                        f"**{heading}:**\n{best.candidate_answer}")
        return {
            "problem": problem_statement, "domain": domain, "compute_budget": compute_budget,
            "total_trajectories_evaluated": len(trajectories), "best_trajectory": best.to_dict(),
            "final_solution": final_answer, "best_grade_0_to_7": best.grade_score_0_to_7,
            "proof_status": status, "verification": best.verification,
            "confidence_score": None, "calibrated": False, "confidence_promoted": False,
            "target_confidence_applied": False, "externally_validated": False,
            "total_duration_ms": round((time.time() - start_time) * 1000, 2),
            "trajectories": [item.to_dict() for item in trajectories],
            "limitations": ["As tentativas locais usam o mesmo prover, sem comprovar diversidade independente.",
                            "A confirmação simbólica limita-se à identidade recebida, sem validar enunciados naturais ou equivalência geral.",
                            "O recibo é local; não representa prova independente do software, calibração ou avaliação externa."],
        }
