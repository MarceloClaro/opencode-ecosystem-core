"""Contratos RED da SPEC-935-R451 para recursos e exatidão formais."""

from __future__ import annotations

import pytest

from integrations.deepmind.formal_verifier import (
    FormalProofVerifier,
    _RestrictedAlgebraicSyntaxError,
)


def test_power_growth_is_rejected_before_sympy_construction() -> None:
    verifier = FormalProofVerifier()

    with pytest.raises(_RestrictedAlgebraicSyntaxError):
        verifier._parse_restricted_algebraic_ast("(((2**64)**64)**64)")

    accepted, _ = verifier.verify_algebraic_identity(
        "(a + b)**2", "a**2 + 2*a*b + b**2"
    )
    assert accepted is True


def test_float_literals_are_not_silently_rounded_into_formal_identities() -> None:
    verifier = FormalProofVerifier()

    accepted, message = verifier.verify_algebraic_identity(
        "9007199254740992.0", "9007199254740993.0"
    )
    assert accepted is False
    assert "recusada" in message

    rational_identity, _ = verifier.verify_algebraic_identity("1 / 10 + 1 / 10", "1 / 5")
    assert rational_identity is True


def test_counterexample_search_enumerates_all_declared_variables_within_budget() -> None:
    verifier = FormalProofVerifier()

    counterexamples = verifier.search_counterexamples("x < y", ["x", "y"], range(-1, 2))
    assert {"x": 0, "y": 0, "result": False} in counterexamples
    assert verifier.search_counterexamples("x < y", ["x"], range(-1, 2)) == []


def test_propositional_parser_rejects_input_before_recursive_depth_is_exhausted() -> None:
    verifier = FormalProofVerifier()
    excessive_negation = "not " * 300 + "p"

    assert verifier._tokenize_propositional_formula(excessive_negation) is None
    verified, message = verifier.verify_logical_implication([excessive_negation], "p")
    assert verified is False
    assert "fora do fragmento" in message
