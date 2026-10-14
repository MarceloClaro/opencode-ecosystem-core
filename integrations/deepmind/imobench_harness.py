"""SPEC-935-R442 / R888: benchmark local sem gabarito na entrada do solver.

Acerto textual, sinais heurísticos e evidência formal têm contratos distintos.
A amostra interna não constitui execução do IMO Bench completo nem calibração.
"""
from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any, ClassVar

from integrations.deepmind.formal_verifier import FormalProofVerifier

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IMOSolverInput:
    """Visão pública; não é um sandbox para callbacks Python não confiáveis."""
    problem_id: str
    problem_text: str
    category: str
    subcategory: str = ""
    source: str = ""
    difficulty: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IMOProblem:
    """Problema privado do avaliador, incluindo o gabarito reservado."""
    problem_id: str
    problem_text: str
    short_answer: str
    category: str
    subcategory: str = ""
    source: str = ""
    difficulty: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def solver_input(self) -> IMOSolverInput:
        return IMOSolverInput(self.problem_id, self.problem_text, self.category,
                              self.subcategory, self.source, self.difficulty)


@dataclass
class IMOEvalResult:
    problem_id: str
    is_correct: bool | None
    predicted_answer: str
    expected_answer: str
    grade_score_0_to_7: int | None
    grade_feedback: str
    justification: str = ""
    formal_verified: bool = False
    formal_verification_status: str = "not_performed"
    grading_kind: str = "textual_heuristic_uncalibrated"
    answer_match_method: str = "full_normalized_exact"
    answer_status: str = "submitted"
    status: str = "evaluated"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalized_answer(value: str) -> str:
    """Normaliza apresentação, não equivalência algébrica ou semântica.

    Preserva caixa, conjuntos versus tuplas, dígitos separados e expoentes.
    Não aplica NFKC, que transformaria indevidamente '3²' em '32'.
    """
    text = value.strip()
    for left, right in (("$$", "$$"), ("$", "$"), (r"\(", r"\)")):
        if text.startswith(left) and text.endswith(right) and len(text) >= len(left) + len(right):
            text = text[len(left):-len(right)].strip()
            break
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\s*([,;(){}=+*/^])\s*", r"\1", text)


class GradingHeadDeepMind:
    """Heurística de traços textuais; não calibrada com IMO-GradingBench.

    O nome público é mantido por compatibilidade. A escala legada é 0–7;
    este avaliador usa somente 0–4 e não atribui completude ou prova.
    O argumento verifier é preservado, mas nenhum verificador é invocado.
    """
    RUBRIC_LEVELS: ClassVar[dict[int, str]] = {
        0: "Heurística textual: resposta vazia; nenhuma avaliação de prova.",
        1: "Heurística textual: texto curto; correção e prova não avaliadas.",
        2: "Heurística textual: texto extenso; correção e prova não avaliadas.",
        3: "Heurística textual: marca algébrica ou de lema; correção e prova não avaliadas.",
        4: "Heurística textual: marcas algébricas e de lema; correção e prova não avaliadas.",
    }

    def grade(self, problem: IMOProblem | IMOSolverInput, solution_text: str,
              verifier: FormalProofVerifier | None = None) -> tuple[int, str]:
        if not isinstance(solution_text, str):
            raise TypeError("A justificativa da heurística deve ser textual.")
        text = solution_text.strip()
        has_algebra = "=" in text
        has_lemma = bool(re.search(r"\b(indução|inducao|induction|lema|lemas|lemma|lemmas)\b", text.casefold()))
        score = (0 if not text else 4 if has_algebra and has_lemma else 3
                 if has_algebra or has_lemma else 2 if len(text) > 50 else 1)
        return score, self.RUBRIC_LEVELS[score]


class IMOBenchmarkHarness:
    """Avalia respostas explícitas sobre uma amostra interna identificada."""

    def __init__(self, verifier: FormalProofVerifier | None = None) -> None:
        self.verifier = verifier or FormalProofVerifier()
        self.grading_head = GradingHeadDeepMind()
        self.sample_dataset: list[IMOProblem] = self._load_canonical_sample()

    def _load_canonical_sample(self) -> list[IMOProblem]:
        """Amostra interna adaptada/derivada; não carrega o dataset upstream."""
        return [
            IMOProblem(
                problem_id="imo-bench-algebra-001",
                problem_text="For a given positive integer N, Henry writes the quotient of ab divided by N+1 on the board for each integer pair (a,b) where 1 <= a,b <= N. Find all N such that the sum is (N^3 - N^2 + 2)/4.",
                short_answer="3",
                category="Algebra",
                subcategory="Operation",
                source="IMO Shortlist 2021",
            ),
            IMOProblem(
                problem_id="imo-bench-algebra-004",
                problem_text="Let u >= 2 be a given positive integer. Find the smallest real number C such that for all real numbers t, (t^(2^u) + 1)/2 <= (C(t-1)^2 + t)^(2^(u-1)).",
                short_answer="2^{u-2}",
                category="Algebra",
                subcategory="Inequality",
                source="IMO Shortlist 2021",
            ),
            IMOProblem(
                problem_id="imo-bench-number-theory-001",
                problem_text="Find all pairs of primes (p, q) such that p^3 - q^5 = (p + q)^2.",
                short_answer="(7, 3)",
                category="Number Theory",
                subcategory="Diophantine",
                source="IMO Shortlist 2022",
            ),
            IMOProblem(
                problem_id="imo-bench-combinatorics-001",
                problem_text="Let n be a positive integer. Find the number of permutations of (1, 2, ..., n) having exactly one local maximum.",
                short_answer="2^{n-1}",
                category="Combinatorics",
                subcategory="Permutations",
                source="IMO Shortlist 2020",
            ),
            # ── R503: contra-prova (novos problemas estilo-IMO, respostas
            #    verificáveis por enumeração determinística) ─────────────────
            IMOProblem(
                problem_id="imo-bench-algebra-002",
                problem_text="Find the smallest integer n > 1 such that 2^n > n^2.",
                short_answer="5",
                category="Algebra",
                subcategory="Inequality",
                source="IMO-style (R503, derivado)",
            ),
            IMOProblem(
                problem_id="imo-bench-number-theory-002",
                problem_text="Find all primes p <= 20 such that p^2 divides 2^p + 1.",
                short_answer="{3}",
                category="Number Theory",
                subcategory="Modular",
                source="IMO-style (R503, derivado)",
            ),
            IMOProblem(
                problem_id="imo-bench-number-theory-003",
                problem_text="Find the largest exponent e such that 3^e divides 2023! (the factorial of 2023).",
                short_answer="1006",
                category="Number Theory",
                subcategory="Legendre",
                source="IMO-style (R503, derivado)",
            ),
            IMOProblem(
                problem_id="imo-bench-combinatorics-002",
                problem_text="Let n = 5. Find the number of permutations of (1, 2, 3, 4, 5) having exactly two local maxima (a local maximum is larger than all existing neighbors; endpoints count).",
                short_answer="88",
                category="Combinatorics",
                subcategory="Permutations",
                source="IMO-style (R503, derivado)",
            ),
            IMOProblem(
                problem_id="imo-bench-geometry-001",
                problem_text="Find the number of diagonals in a convex polygon with 2023 sides.",
                short_answer="2043230",
                category="Geometry",
                subcategory="Polygon",
                source="IMO-style (R503, derivado)",
            ),
        ]

    def run_benchmark(self, solver_fn: Callable[[IMOSolverInput], str | dict] | None = None,
                      limit: int = 4) -> dict[str, Any]:
        """O callback recebe somente o problema público, sem gabarito.

        Retorno: resposta curta inteira em string ou {answer, reasoning}.
        Prosa sem campo answer não é interpretada como resposta escondida.
        O relatório final contém gabaritos para auditoria; não deve voltar ao
        solver como entrada de uma avaliação supostamente independente.
        """
        if type(limit) is not int or limit <= 0:
            raise ValueError("limit deve ser inteiro positivo.")
        if solver_fn is not None and not callable(solver_fn):
            raise ValueError("solver_fn deve ser um callback explícito.")
        problems = self.sample_dataset[:limit]
        report = {
            "status": "not_executed", "total_problems": len(problems),
            "executed_problems": 0, "evaluated_problems": 0, "failed_problems": 0,
            "correct_problems": None, "accuracy": None, "average_grade_0_to_7": None,
            "results": [], "dataset_scope": "internal_sample_with_derived_problems",
            "verification": "not_executed", "calibrated": False,
            "confidence_promoted": False, "externally_validated": False,
            "limitations": [
                "Acerto compara a resposta curta inteira após normalização de apresentação; não decide equivalência algébrica.",
                "A nota é heurística textual não calibrada; nenhuma prova formal é executada por este harness.",
                "A amostra interna não é o dataset upstream completo; exposição prévia do solver não foi medida.",
                "Callbacks Python são confiáveis para execução local; a visão pública não é um isolamento de processo.",
            ],
        }
        if solver_fn is None or not problems:
            return report
        results: list[IMOEvalResult] = []
        # Conservar os gabaritos fora dos objetos transmitidos ao callback.
        prepared = [(problem.problem_id, problem.short_answer, problem.solver_input()) for problem in problems]
        for problem_id, expected, public in prepared:
            try:
                submission = solver_fn(public)
                if isinstance(submission, str):
                    answer, reasoning, answer_status = submission, "", "submitted"
                elif type(submission) is dict:
                    answer = submission.get("answer")
                    reasoning = submission.get("reasoning", "")
                    answer_status = submission.get("answer_status", "submitted")
                    if answer_status not in {"submitted", "computed", "candidate"}:
                        raise ValueError("answer_status deve ser submitted, computed ou candidate.")
                else:
                    raise ValueError("O solver deve retornar resposta textual ou objeto com answer.")
                if not isinstance(answer, str) or not _normalized_answer(answer):
                    raise ValueError("A resposta curta deve conter texto explícito não vazio.")
                if not isinstance(reasoning, str):
                    raise TypeError("reasoning deve ser textual.")
                score, feedback = self.grading_head.grade(public, reasoning or answer)
                results.append(IMOEvalResult(
                    problem_id=problem_id,
                    is_correct=bool(_normalized_answer(expected)) and _normalized_answer(answer) == _normalized_answer(expected),
                    predicted_answer=answer, expected_answer=expected,
                    grade_score_0_to_7=score, grade_feedback=feedback,
                    justification=reasoning, answer_status=answer_status))
            except Exception as error:
                logger.exception("Falha explícita no callback/contrato do problema %s", problem_id)
                results.append(IMOEvalResult(
                    problem_id=problem_id, is_correct=None, predicted_answer="", expected_answer=expected,
                    grade_score_0_to_7=None, grade_feedback="Resposta não avaliada por falha de execução/contrato.",
                    status="failed", error=type(error).__name__ + ": " + str(error)[:400]))
        evaluated = [row for row in results if row.status == "evaluated"]
        failed = len(results) - len(evaluated)
        correct = sum(row.is_correct is True for row in evaluated)
        report.update(
            status="completed" if not failed else "partial" if evaluated else "execution_failed",
            executed_problems=len(results), evaluated_problems=len(evaluated), failed_problems=failed,
            correct_problems=correct, results=[row.to_dict() for row in results],
            verification="local_solver_execution",
        )
        if not failed:
            report["accuracy"] = round(correct / len(results), 4)
            report["average_grade_0_to_7"] = round(sum(row.grade_score_0_to_7 for row in evaluated) / len(evaluated), 2)
        return report
