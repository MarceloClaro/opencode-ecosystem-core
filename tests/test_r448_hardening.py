"""Contratos RED iniciais da SPEC-935-R448."""

from pathlib import Path
import typing

from integrations.deepmind.aletheia_scaffold import AletheiaHypothesisEngine
from integrations.deepmind.alphaproof_engine import OpenCodeAlphaProof
from integrations.deepmind.formal_verifier import FormalProofVerifier
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from sdd.spec_engine import SpecRegistry


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_counterexample_is_not_accepted_as_a_proof():
    """`p` não implica `q`; um modelo Z3 não pode resultar em sucesso."""
    verified, detail = FormalProofVerifier().verify_logical_implication(["p"], "q")

    assert verified is False
    assert detail


def test_malformed_equations_never_verify_without_sympy():
    """Operandos vazios ou expressões inválidas não podem usar o fallback sintático."""
    verifier = FormalProofVerifier()
    verifier.has_sympy = False

    for lhs, rhs in [("", ""), ("", "x"), ("x", ""), ("x +", "x +"), ("=", "=")]:
        verified, _ = verifier.verify_algebraic_identity(lhs, rhs)
        assert verified is False

    result = verifier.verify_proof_steps(
        "=",
        [{"statement": "=", "justification": "Equação sem operandos"}],
    )

    assert result.is_valid is False
    assert result.verified_steps[0].is_valid is False


def test_alphaproof_rejects_malformed_goal_without_symbolic_engines():
    """Uma meta `=` não pode ser promovida pelo fallback de AlphaProof."""
    verifier = FormalProofVerifier()
    verifier.has_sympy = False
    verifier.has_z3 = False

    result = OpenCodeAlphaProof(verifier=verifier).search_proof("=", premises=["="])

    assert result["is_proven"] is False
    assert result["proof_status"] == "unproven"


def test_alphaproof_respects_zero_max_depth_for_direct_identities():
    """Uma derivação de um passo não cabe em profundidade máxima zero."""
    result = OpenCodeAlphaProof().search_proof("x = x", max_depth=0)

    assert result["is_proven"] is False
    assert result["proof_status"] == "unproven"
    assert result["confidence_score"] == 0.0


def test_formal_runtime_dependencies_are_explicitly_pinned():
    """Os motores carregados em runtime devem constar no manifesto com pin exato."""
    requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert any(line.startswith("sympy==") for line in requirements.splitlines())
    assert any(line.startswith("z3-solver==") for line in requirements.splitlines())


def test_unrelated_verified_step_does_not_prove_the_claim():
    """Uma identidade válida não demonstra uma alegação sem ligação formal."""
    result = FormalProofVerifier().verify_proof_steps(
        "p",
        [{"statement": "x = x", "justification": "Identidade reflexiva"}],
    )

    assert result.is_valid is False
    assert any("alegação" in error.lower() for error in result.errors)


def test_alphaproof_fallback_is_explicitly_unproven():
    """Exaurir a busca não pode promover o fallback a uma demonstração."""
    result = OpenCodeAlphaProof().search_proof(
        "q",
        premises=["p"],
        max_expanded_nodes=0,
    )

    assert result["is_proven"] is False
    assert result["proof_status"] == "unproven"
    assert "não demonstrada" in result["verification_message"].lower()


def test_alphaproof_closes_an_explicitly_verified_entailment():
    """O caminho positivo exige uma implicação proposicional verificável."""
    result = OpenCodeAlphaProof().search_proof(
        "q",
        premises=["p -> q", "p"],
    )

    assert result["is_proven"] is True
    assert result["proof_status"] == "proven"
    assert result["tactics_applied"] == ["LogicalEntailment"]


def test_aletheia_generated_lemmas_start_unverified():
    """Lemas de scaffold permanecem pendentes até uma verificação real."""
    decomposition = AletheiaHypothesisEngine().decompose(
        "Toda instância de p implica q.",
        domain="logic",
    )

    assert decomposition.lemmas
    assert all(lemma.verified is False for lemma in decomposition.lemmas)
    assert decomposition.verification_result["is_valid"] is False


def test_orchestrator_public_annotations_are_resolvable():
    """Anotações públicas que usam ``Callable``/``Tuple`` resolvem em runtime."""
    for method_name in (
        "amplify_free_model_response",
        "imobench_evaluate",
        "formal_verify_identity",
    ):
        hints = typing.get_type_hints(getattr(MarceloClaroOrchestrator, method_name))
        assert hints

    formal_hints = typing.get_type_hints(MarceloClaroOrchestrator.formal_verify_identity)
    assert typing.get_origin(formal_hints["return"]) is tuple
    assert typing.get_args(formal_hints["return"]) == (bool, str)


def test_installers_do_not_persist_unrestricted_privilege_or_pipe_to_shell():
    """Instalação deve falhar fechada, sem bootstrap remoto não verificável."""
    provision = (REPO_ROOT / "installer/windows/provision.sh").read_text(encoding="utf-8")
    shared = (REPO_ROOT / "installer/common/install_clis.sh").read_text(encoding="utf-8")

    assert "NOPASSWD:ALL" not in provision
    assert "curl -fsSL https://opencode.ai/install | bash" not in shared
    assert "curl -fsSL https://antigravity.google/cli/install.sh | bash" not in shared
    assert "curl -fsSL https://ollama.com/install.sh | sh" not in shared


def test_formal_specs_load_markdown_acceptance_criteria_as_contracts():
    """Critérios no corpo da SPEC-R448 precisam chegar ao SpecVerifier."""
    spec = SpecRegistry().get("SPEC-935-R448")

    assert spec is not None
    assert spec.test_file == "tests"
    assert {criterion.criterion_id for criterion in spec.criteria}
