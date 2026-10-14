"""SPEC-935-R888: execução de benchmark, gabarito e prova são distintos."""
from dataclasses import asdict
from types import SimpleNamespace

import pytest

from integrations.deepmind.imo_real_solver import RealIMOSolver
from integrations.deepmind.imobench_harness import (
    GradingHeadDeepMind,
    IMOBenchmarkHarness,
    IMOProblem,
)


@pytest.fixture
def harness():
    value = IMOBenchmarkHarness()
    value.sample_dataset = [IMOProblem("fixture-r888", "Determine a quantidade.", "3", "arithmetic")]
    return value


def test_no_solver_is_not_an_executed_benchmark(harness):
    report = harness.run_benchmark(limit=1)
    assert report.get("status") == "not_executed"
    assert report["accuracy"] is None
    assert report["average_grade_0_to_7"] is None
    assert report["results"] == []
    assert report.get("executed_problems") == 0


def test_callback_only_receives_public_problem(harness):
    seen = []
    def solver(problem):
        fields = asdict(problem)
        assert "short_answer" not in fields
        assert "solution" not in fields
        assert not hasattr(problem, "short_answer")
        assert problem.problem_id == "fixture-r888"
        assert problem.problem_text == "Determine a quantidade."
        assert problem.category == "arithmetic"
        seen.append(problem)
        return {"answer": "3", "reasoning": "Contagem independente."}
    report = harness.run_benchmark(solver_fn=solver, limit=1)
    assert len(seen) == 1
    assert report["accuracy"] == 1.0
    assert report["results"][0]["predicted_answer"] == "3"
    assert report["results"][0]["formal_verified"] is False


def test_answer_13_does_not_match_expected_3(harness):
    report = harness.run_benchmark(solver_fn=lambda _: "13", limit=1)
    row = report["results"][0]
    assert row["is_correct"] is False
    assert row["predicted_answer"] == "13"
    assert report["accuracy"] == 0.0


def test_reasoning_text_and_grading_cannot_supply_the_answer(harness):
    report = harness.run_benchmark(solver_fn=lambda _: {
        "answer": "13", "reasoning": "lema = 3; demonstração formal; certo",
        "formal_verified": True, "grade_score_0_to_7": 7}, limit=1)
    row = report["results"][0]
    assert row["is_correct"] is False
    assert row["formal_verified"] is False
    assert row.get("formal_verification_status") == "not_performed"
    assert report.get("calibrated") is False


def test_correct_answer_with_text_markers_is_not_a_formal_proof(harness):
    report = harness.run_benchmark(solver_fn=lambda _: {
        "answer": "3", "reasoning": "Pelo lema de indução, x = 3."}, limit=1)
    row = report["results"][0]
    assert row["is_correct"] is True
    assert row["formal_verified"] is False
    assert row.get("grading_kind") == "textual_heuristic_uncalibrated"


def test_prose_with_embedded_answer_is_not_full_answer(harness):
    report = harness.run_benchmark(solver_fn=lambda _: "A resposta talvez seja 3 ou 13.", limit=1)
    assert report["results"][0]["is_correct"] is False


@pytest.mark.parametrize("answer,expected,correct", [
    ("  $ (7, 3) $  ", "(7,3)", True),
    ("x + 1", "x+1", True),
    ("X", "x", False),
    ("1 3", "13", False),
    ("3²", "32", False),
    ("{3}", "(3)", False),
])
def test_normalization_preserves_mathematical_distinctions(harness, answer, expected, correct):
    harness.sample_dataset[0].short_answer = expected
    row = harness.run_benchmark(solver_fn=lambda _: answer, limit=1)["results"][0]
    assert row["is_correct"] is correct


def test_callback_error_is_reported_without_fabricating_accuracy(harness):
    def failed(_):
        raise RuntimeError("solver fixture indisponível")
    report = harness.run_benchmark(solver_fn=failed, limit=1)
    assert report.get("status") == "execution_failed"
    assert report["accuracy"] is None
    assert report["results"][0]["is_correct"] is None
    assert report["results"][0]["formal_verified"] is False
    assert report.get("failed_problems") == 1


def test_empty_answer_is_not_counted_as_correct(harness):
    report = harness.run_benchmark(solver_fn=lambda _: {"answer": "", "reasoning": "3"}, limit=1)
    assert report["results"][0]["is_correct"] is not True
    assert report["accuracy"] is None


def test_grading_does_not_call_textual_features_a_proof(harness):
    score, feedback = GradingHeadDeepMind().grade(harness.sample_dataset[0], "indução e lema = 13")
    assert score < 7
    assert "heurístic" in feedback.lower()
    assert "100% correta" not in feedback


@pytest.mark.parametrize("limit", [True, 0, -1, 1.5])
def test_invalid_limit_is_rejected(harness, limit):
    with pytest.raises(ValueError):
        harness.run_benchmark(solver_fn=lambda _: "3", limit=limit)


def test_deterministic_submission_derives_values_without_answer_field():
    solver = RealIMOSolver()
    problem = SimpleNamespace(problem_id="imo-bench-algebra-001", problem_text="enunciado", category="algebra")
    submission = solver.submit(problem)
    assert submission["answer"] == "3"
    assert "Metodo:" in submission["reasoning"]


def test_deterministic_submission_carries_partial_candidate_status():
    solver = RealIMOSolver()
    problem = SimpleNamespace(problem_id="imo-bench-algebra-004", problem_text="enunciado", category="algebra")
    submission = solver.submit(problem)
    assert submission["answer"] == "2^{u-2}"
    assert submission["answer_status"] == "candidate"


def test_primary_method_uses_the_same_no_solver_contract():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    report = MarceloClaroOrchestrator(auto_load_agents=False).imobench_evaluate(limit=1)
    assert report.get("status") == "not_executed"
    assert report["accuracy"] is None


def test_deep_think_natural_claim_remains_pending():
    from integrations.deepmind.deep_think_engine import OpenCodeDeepThink
    report = OpenCodeDeepThink().think("Demonstrar convergência de qualquer sistema complexo.", compute_budget=1)
    assert report["best_trajectory"]["is_valid"] is False
    assert report.get("proof_status") == "unproven"
    assert report["confidence_score"] is None
    assert report.get("calibrated") is False
    assert "Demonstração Formal Concluída" not in report["final_solution"]


def test_deep_think_real_identity_is_independent_of_heuristic_grade():
    from integrations.deepmind.deep_think_engine import OpenCodeDeepThink
    claim = "(x + 1)**2 = x**2 + 2*x + 1"
    report = OpenCodeDeepThink().think(claim, compute_budget=1)
    assert report["best_trajectory"]["is_valid"] is True
    assert report["best_grade_0_to_7"] < 5
    receipt = report.get("verification", {})
    assert receipt.get("claim") == claim
    assert receipt.get("backend") == "sympy"
    assert receipt.get("execution_performed") is True
    assert receipt.get("verified") is True
    assert report["confidence_score"] is None
    assert report.get("externally_validated") is False


@pytest.mark.parametrize("claim,backend_available", [("x = x + 1", True), ("x = x", False)])
def test_deep_think_rechecks_candidate_and_does_not_promote_fallback(claim, backend_available):
    from integrations.deepmind.deep_think_engine import OpenCodeDeepThink
    from integrations.deepmind.formal_verifier import FormalProofVerifier
    class ClaimedProof:
        def search_proof(self, value):
            return {"theorem": value, "premises": [], "is_proven": True, "proof_status": "proven",
                    "proof_steps": ["prova declarada"], "tactics_applied": ["string"],
                    "confidence_score": 1.0}
    verifier = FormalProofVerifier()
    verifier.has_sympy = backend_available
    report = OpenCodeDeepThink(verifier=verifier, alphaproof=ClaimedProof()).think(claim, compute_budget=1)
    assert report["best_trajectory"]["is_valid"] is False
    assert report.get("verification", {}).get("verified") is False
    assert report["confidence_score"] is None


def test_deep_think_rejects_a_proof_for_a_different_claim():
    from integrations.deepmind.deep_think_engine import OpenCodeDeepThink
    class WrongClaim:
        def search_proof(self, value):
            return {"theorem": "x=x", "premises": [], "is_proven": True,
                    "proof_status": "proven", "proof_steps": ["x=x"], "tactics_applied": []}
    report = OpenCodeDeepThink(alphaproof=WrongClaim()).think("x=x+1", compute_budget=1)
    assert report["best_trajectory"]["is_valid"] is False
    assert report["verification"]["verified"] is False


@pytest.fixture
def isolated_memory(monkeypatch, tmp_path):
    from importlib import import_module
    module = import_module("mci.metabus")
    monkeypatch.setattr(module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    memory = module.MetacognitiveMemory()
    memory.confidence_ledger["marceloclaro"] = 0.5
    monkeypatch.setattr(module.metabus, "memory", memory)
    return memory


def test_primary_deep_think_does_not_update_confidence_from_its_own_report(isolated_memory):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    before = dict(isolated_memory.confidence_ledger)
    report = MarceloClaroOrchestrator(auto_load_agents=False).deep_think("x=x+1", compute_budget=1)
    assert report["proof_status"] == "unproven"
    assert dict(isolated_memory.confidence_ledger) == before


def test_primary_alphaproof_does_not_update_confidence_from_its_own_report(isolated_memory):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    before = dict(isolated_memory.confidence_ledger)
    report = MarceloClaroOrchestrator(auto_load_agents=False).alphaproof_search("x=x+1")
    assert report["is_proven"] is False
    assert dict(isolated_memory.confidence_ledger) == before


def test_grading_does_not_consult_the_answer_key(harness):
    public = harness.sample_dataset[0].solver_input()
    grader = GradingHeadDeepMind()
    assert grader.grade(public, "lema com igualdade = 13") == grader.grade(harness.sample_dataset[0], "lema com igualdade = 13")


def test_solver_cannot_mutate_its_public_problem(harness):
    from dataclasses import FrozenInstanceError
    def solver(problem):
        with pytest.raises(FrozenInstanceError):
            problem.problem_text = "alteração"
        return "3"
    report = harness.run_benchmark(solver_fn=solver, limit=1)
    assert report["accuracy"] == 1.0
    assert harness.sample_dataset[0].problem_text == "Determine a quantidade."


def test_missing_answer_cannot_be_supplied_by_reasoning(harness):
    report = harness.run_benchmark(solver_fn=lambda _: {"reasoning": "resposta 3"}, limit=1)
    assert report["results"][0]["is_correct"] is None
    assert report["accuracy"] is None
