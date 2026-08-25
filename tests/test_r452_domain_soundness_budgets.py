"""Contratos RED da SPEC-935-R452 para domínio e orçamento global."""

from __future__ import annotations

import pytest

from integrations.deepmind import formal_verifier as formal_verifier_module
from integrations.deepmind.formal_verifier import FormalProofVerifier

def test_symbolic_denominators_are_rejected_before_universal_identity_check() -> None:
    verifier = FormalProofVerifier()

    for lhs, rhs in (
        ("x / x", "1"),
        ("x**-1", "1"),
        ("(x + 1)**-1", "1"),
        ("x**0", "1"),
        ("0**0", "1"),
    ):
        accepted, message = verifier.verify_algebraic_identity(lhs, rhs)
        assert accepted is False
        assert "recusada" in message

    rational_coefficient, _ = verifier.verify_algebraic_identity(
        "(x + 1) / 2", "x / 2 + 1 / 2"
    )
    assert rational_coefficient is True

    literal_inverse, _ = verifier.verify_algebraic_identity("2**-1", "1 / 2")
    assert literal_inverse is True


def test_raw_algebraic_input_rejects_unicode_normalization_and_comments() -> None:
    verifier = FormalProofVerifier()

    for lhs, rhs in (("K", "K"), ("x # comentário", "x")):
        accepted, message = verifier.verify_algebraic_identity(lhs, rhs)
        assert accepted is False
        assert "recusada" in message


def test_logical_implication_rejects_excessive_aggregate_input_before_z3(monkeypatch) -> None:
    verifier = FormalProofVerifier()

    def unexpected_solver() -> None:
        pytest.fail("entrada acima do orçamento não pode alcançar o solver")

    monkeypatch.setattr(formal_verifier_module.z3, "Solver", unexpected_solver)

    accepted, message = verifier.verify_logical_implication(["p"] * 65, "p")
    assert accepted is False
    assert "limite" in message.lower()

    accepted, message = verifier.verify_logical_implication(["p" * 5000, "q" * 5000], "r")
    assert accepted is False
    assert "tamanho agregado" in message.lower()

    many_atoms = " OR ".join(f"p{number}" for number in range(65))
    accepted, message = verifier.verify_logical_implication([many_atoms], "p0")
    assert accepted is False
    assert "átomos" in message.lower()


def test_logical_implication_sets_a_runtime_z3_timeout(monkeypatch) -> None:
    verifier = FormalProofVerifier()
    recorded_timeouts: list[int] = []

    class FakeSolver:
        def set(self, **kwargs) -> None:
            recorded_timeouts.append(kwargs["timeout"])

        def add(self, *_args) -> None:
            return None

        def check(self):
            return fake_z3.unsat

    class FakeZ3:
        unsat = object()
        sat = object()

        @staticmethod
        def Bool(name):
            return ("bool", name)

        @staticmethod
        def Not(expression):
            return ("not", expression)

        @staticmethod
        def Solver():
            return FakeSolver()

    fake_z3 = FakeZ3()
    monkeypatch.setattr(formal_verifier_module, "z3", fake_z3)
    verifier.has_z3 = True

    accepted, _ = verifier.verify_logical_implication(["p"], "p")
    assert accepted is True
    assert recorded_timeouts == [verifier._Z3_SOLVER_TIMEOUT_MS]


def test_logical_implication_uses_a_snapshot_after_preflight(monkeypatch) -> None:
    verifier = FormalProofVerifier()
    premises = ["p"]
    original_well_formed = verifier._is_well_formed_propositional_formula
    mutated = False

    def mutate_after_preflight(formula):
        nonlocal mutated
        is_well_formed = original_well_formed(formula)
        if not mutated:
            premises.append("NOT p")
            mutated = True
        return is_well_formed

    monkeypatch.setattr(verifier, "_is_well_formed_propositional_formula", mutate_after_preflight)

    accepted, _ = verifier.verify_logical_implication(premises, "q")
    assert accepted is False


def test_proof_steps_reject_excessive_batch_before_full_processing() -> None:
    verifier = FormalProofVerifier()
    excessive_steps = [{"statement": "x = x", "justification": "reflexividade"}] * 65

    result = verifier.verify_proof_steps("x = x", excessive_steps)
    assert result.is_valid is False
    assert result.verified_steps == []
    assert any("limite" in error.lower() for error in result.errors)


def test_proof_step_snapshot_rejects_subclasses_and_oversized_text() -> None:
    verifier = FormalProofVerifier()

    class OversizedText(str):
        pass

    subclass_result = verifier.verify_proof_steps(
        "x = x",
        [
            {
                "statement": "x = x",
                "justification": OversizedText(
                    "j" * (verifier._MAX_PROOF_AGGREGATE_TEXT_LENGTH + 1)
                ),
            }
        ],
    )
    assert subclass_result.is_valid is False
    assert subclass_result.verified_steps == []

    oversized_result = verifier.verify_proof_steps(
        "x = x",
        [
            {
                "statement": "x = x",
                "justification": "j" * (verifier._MAX_PROOF_AGGREGATE_TEXT_LENGTH + 1),
            }
        ],
    )
    assert oversized_result.is_valid is False
    assert oversized_result.verified_steps == []
    assert any("tamanho agregado" in error.lower() for error in oversized_result.errors)


def test_proof_claim_is_parsed_before_matching_a_verified_step() -> None:
    result = FormalProofVerifier().verify_proof_steps(
        "x 1 = x1",
        [{"statement": "x1 = x1", "justification": "identidade"}],
    )

    assert result.is_valid is False
    assert result.verified_steps == []
