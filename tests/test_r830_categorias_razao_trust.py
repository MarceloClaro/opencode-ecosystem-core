"""R830 RED: 12 ausências nome a nome (6 razão + 6 trust) + fix do scanner.

Estado esperado inicial: RED. GREEN após facades + fix.
Sem rede, sem inferência, sem escrita externa (exceto leitura do corpus).
"""
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent

TRUST_FILES = [
    "trust/staking_mechanism.py",
    "trust/slashing_mechanism.py",
    "trust/fee_market.py",
    "trust/behavioral_gate.py",
    "trust/outcome_tracker.py",
    "trust/stake_pool.py",
]
REASON_FILES = [
    "reasoning/z3_solver.py",
    "reasoning/critical_reasoner.py",
    "reasoning/quantum_reasoning.py",
    "reasoning/bayesian_inference.py",
    "reasoning/dialectical_engine.py",
    "reasoning/reasoning_engines.py",
]


def _corpus():
    from scanners.pipeline import DiagnosticPipeline
    p = DiagnosticPipeline(domain="ecosystem")
    return p._build_ecosystem_corpus("")


def test_scanner_compila_ecosystem_keywords():
    from scanners.noological_scanner import NoologicalScanner
    s = NoologicalScanner(domain="ecosystem")
    class O:
        def get_all_text(self):
            return "z3 staking sdd tdd"
    s.scan(O(), research_domain="ecosystem")
    assert s._compiled_ecosystem, "RED: _compile_dimension_patterns nunca chamado; ECOSYSTEM_KEYWORDS inerte"


def test_inventario_autodescoberta_contem_literais_trust():
    corp = _corpus().lower()
    for rel in TRUST_FILES:
        lit = pathlib.Path(rel).stem
        assert lit in corp, f"RED: literal {lit} ausente do corpus (arquivo {rel} não descoberto)"


def test_inventario_autodescoberta_contem_literais_reason():
    corp = _corpus().lower()
    for rel in REASON_FILES:
        lit = pathlib.Path(rel).stem
        assert lit in corp, f"RED: literal {lit} ausente do corpus (arquivo {rel} não descoberto)"


def test_staking_mechanism_funcional():
    from trust.staking_mechanism import deposit, slots_usados
    deposit("alice", 10.0, "t1")
    assert slots_usados("alice") == 1


def test_slashing_mechanism_funcional():
    from trust.slashing_mechanism import slash
    out = slash(locked=100.0, amount=20.0, reason="falha")
    assert out["slashed"] == 20.0 and out["remaining"] == 80.0


def test_fee_market_funcional():
    from trust.fee_market import quote
    q = quote("t1", priority="high", congestion=1.0)
    assert q["total_fee"] > q["base_fee"]


def test_behavioral_gate_funcional():
    from trust.behavioral_gate import allow
    assert allow("a", trust=0.9, threshold=0.5)["allowed"] is True
    assert allow("a", trust=0.1, threshold=0.5)["allowed"] is False


def test_outcome_tracker_funcional():
    from trust.outcome_tracker import OutcomeTracker
    t = OutcomeTracker()
    t.record(True)
    t.record(False)
    assert 0.0 <= t.score() <= 1.0 and t.stats()["total"] == 2


def test_stake_pool_funcional():
    from trust.stake_pool import StakePool
    p = StakePool()
    p.lock("bob", 30.0)
    assert p.total_locked() == 30.0


def test_z3_solver_fallback_explicito():
    import pytest
    pytest.importorskip('z3')
    from reasoning.z3_solver import check
    out = check("x > 1", {"x": 2})
    assert out["engine"] == "z3_solver" and out["status"] == "sat"
    assert out["available"] is True
    assert check("x > 1", {"x": 0})["status"] == "unsat"
    assert check("__import__('os').system('x')")["status"] == "fallback"


def test_critical_reasoner_funcional():
    from reasoning.critical_reasoner import critique
    out = critique("tese: X funciona")
    assert "veredito" in out and out["veredito"] in ("sustentada", "contestada")


def test_quantum_reasoning_fallback():
    from reasoning.quantum_reasoning import run_experiment
    out = run_experiment("bell")
    assert out["engine"] == "quantum_reasoning" and "status" in out


def test_bayesian_inference_funcional():
    from reasoning.bayesian_inference import update_beta_binomial
    out = update_beta_binomial(a0=1, b0=1, sucessos=7, tentativas=10)
    assert 0.0 < out["posterior_mean"] < 1.0 and out["prior"] == [1, 1]


def test_dialectical_engine_funcional():
    from reasoning.dialectical_engine import run
    out = run("tese inicial")
    assert "synthesis" in out and "trail" in out


def test_reasoning_engines_compositor():
    import pytest
    pytest.importorskip('sympy')
    from reasoning.reasoning_engines import route
    out = route("2+2")
    assert out["engine"] == "sympy" and out["result"] == "4"
    assert out["available"] is True and out["trust"] is None
    assert route("2+3")["result"] == "5"


def test_spec_r830_existe():
    text = (REPO / "specs" / "SPEC-935-R830-categorias-razao-trust.md").read_text(encoding="utf-8")
    assert "SPEC-935-R830" in text and "z3prover/z3" in text and "vouch-protocol/vouch" in text
