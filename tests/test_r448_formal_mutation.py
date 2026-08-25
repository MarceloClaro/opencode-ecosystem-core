"""Sonda mínima de mutação para os invariantes formais da SPEC-935-R448."""

from integrations.deepmind.formal_verifier import FormalProofVerifier
from integrations.deepmind.formal_safety_predicates import solver_result_proves_implication


def test_countermodel_is_rejected_by_the_mutation_gate() -> None:
    """A mutação que aceita ``p -> q`` sem ``q`` deve ser eliminada."""
    verified, _ = FormalProofVerifier().verify_logical_implication(["p"], "q")
    assert verified is False


def test_countermodel_predicate_distinguishes_unsat_from_sat() -> None:
    """A decisão de promoção só é verdadeira para o marcador ``unsat`` exato."""
    unsat_marker = object()
    sat_marker = object()

    assert solver_result_proves_implication(unsat_marker, unsat_marker) is True
    assert solver_result_proves_implication(sat_marker, unsat_marker) is False


def test_malformed_identity_is_rejected_by_the_mutation_gate() -> None:
    """Fallback sem SymPy não pode aceitar equações estruturalmente inválidas."""
    verifier = FormalProofVerifier()
    verifier.has_sympy = False

    verified, _ = verifier.verify_algebraic_identity("", "x")
    assert verified is False


def test_unrelated_step_does_not_establish_claim_in_mutation_gate() -> None:
    """Uma identidade independente não prova uma alegação proposicional."""
    result = FormalProofVerifier().verify_proof_steps(
        "p",
        [{"statement": "x = x", "justification": "Identidade reflexiva"}],
    )

    assert result.is_valid is False
