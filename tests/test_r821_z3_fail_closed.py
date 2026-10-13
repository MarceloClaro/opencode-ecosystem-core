"""R821: recusa integral do problema sem consultar um solver parcial."""

import pytest

z3 = pytest.importorskip("z3")

from reasoning.engines import Z3Engine


@pytest.fixture
def traced_solver(monkeypatch):
    original = z3.Solver
    events = []

    class Trace:
        def __init__(self):
            self.real = original()
            self.forced_verdict = None
            self.settings = {}

        def set(self, **settings):
            self.settings.update(settings)
            return self.real.set(**settings)

        def add(self, expression):
            return self.real.add(expression)

        def check(self):
            events.append("check")
            return self.forced_verdict if self.forced_verdict is not None else self.real.check()

        def model(self):
            events.append("model")
            return self.real.model()

    trace = Trace()
    monkeypatch.setattr(z3, "Solver", lambda: trace)
    return trace, events


@pytest.mark.parametrize("constraints", [
    ["x[0] == 2"], ["x.__class__", "x +"], ["1"], [""],
    ["x == 2", "x[0] == 2"], ["x[0] == 2", "x == 2"],
    ["x == 2", "x +", "x > 0"], ["x == 2", "1"],
])
def test_invalid_or_mixed_constraints_refused_before_solver_check(traced_solver, constraints):
    _, events = traced_solver
    result = Z3Engine().reason("verificar restrições fornecidas", constraints=constraints)
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert "SATISFATÍVEL" not in result.conclusion
    assert result.available is True
    assert events == []


@pytest.mark.parametrize("constraints", ["x == 2", {"x": 2}, [2], [None]])
def test_invalid_constraint_collection_refused_before_check(traced_solver, constraints):
    _, events = traced_solver
    result = Z3Engine().reason("tipos inválidos", constraints=constraints)
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert events == []


def test_valid_sat_keeps_real_model(traced_solver):
    _, events = traced_solver
    result = Z3Engine().reason("x positivo", constraints=["x == 2", "x > 0"])
    assert result.confidence == 0.95
    assert "SATISFATÍVEL" in result.conclusion
    assert "'x': '2'" in result.conclusion
    assert events == ["check", "model"]


def test_valid_unsat_keeps_real_verdict(traced_solver):
    _, events = traced_solver
    result = Z3Engine().reason("contradição", constraints=["x == 2", "x == 3"])
    assert result.confidence == 0.9
    assert "unsat" in result.conclusion
    assert events == ["check"]


@pytest.mark.parametrize("verdict", [z3.unknown, "unexpected"])
def test_unknown_or_unexpected_verdict_is_inconclusive_without_model(traced_solver, verdict):
    trace, events = traced_solver
    trace.forced_verdict = verdict
    result = Z3Engine().reason("retorno simulado", constraints=["x == 2"])
    assert result.confidence == 0.0
    assert "inconclusivo" in result.conclusion
    assert "SATISFATÍVEL" not in result.conclusion
    assert events == ["check"]


def test_solver_exception_returns_zero_confidence_without_model(traced_solver, monkeypatch):
    trace, events = traced_solver

    def fail():
        events.append("check")
        raise RuntimeError("backend indisponível durante operação")

    monkeypatch.setattr(trace, "check", fail)
    result = Z3Engine().reason("erro simulado", constraints=["x == 2"])
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert events == ["check"]


@pytest.mark.parametrize("constraints", [None, [], ()])
def test_absent_constraints_do_not_answer_prose_query(traced_solver, constraints):
    _, events = traced_solver
    result = Z3Engine().reason("prove que o tratamento é eficaz", constraints=constraints)
    assert result.confidence == 0.0
    assert "tautologia vazia" in result.conclusion
    assert "não avaliada" in result.conclusion
    assert "SATISFATÍVEL" not in result.conclusion
    assert events == []


def test_solver_has_finite_timeout(traced_solver):
    trace, _ = traced_solver
    Z3Engine().reason("x positivo", constraints=["x > 0"])
    assert 0 < trace.settings["timeout"] <= 60000


@pytest.mark.parametrize("constraints", [
    ["not (x == 2)", "x == 2"], ["x == 2 and not (x != 2)", "x == 3"],
    ["x == 1.5"],
])
def test_not_and_fractional_constants_preserve_unsat(traced_solver, constraints):
    _, events = traced_solver
    result = Z3Engine().reason("contradição formal", constraints=constraints)
    assert result.confidence == 0.9
    assert "unsat" in result.conclusion
    assert events == ["check"]


def test_legitimate_small_power_still_sat(traced_solver):
    result = Z3Engine().reason("potência finita", constraints=["x == 2", "x**2 == 4"])
    assert result.confidence == 0.95
    assert "SATISFATÍVEL" in result.conclusion


@pytest.mark.parametrize("expression", [
    "x.__class__ == 2", "x[0] == 2", "f(x) == 2", "[x for x in y] == 2",
    "x == 1e999", "x == " + str(1 << 300),
    "x == 2**1000000", "x == 2**(1000 * 1000)",
    "x == 2**(x - x + 1000000)", "x == (2**200)**200",
    "x == " + "+".join(["1"] * 100),
    "x == " + "-" * 40 + "1", "x == " + " " * 4096 + "1",
    "x == 2 and f(x) == 2", "explique o raciocínio lógico",
])
def test_invalid_ast_and_budgets_rejected_before_z3_construction(monkeypatch, expression):
    from reasoning.engines import _safe_build_z3_constraint

    calls = []

    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("construtor não pode preceder validação integral")

    for name in ("Int", "IntVal", "RealVal", "BoolVal", "And", "Or", "Not"):
        monkeypatch.setattr(z3, name, forbidden)
    with pytest.raises(ValueError):
        _safe_build_z3_constraint(expression, {})
    assert calls == []


def test_constraint_set_size_has_finite_budget_before_check(traced_solver):
    _, events = traced_solver
    result = Z3Engine().reason("coleção excessiva", constraints=["x > 0"] * 65)
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert events == []


def test_missing_backend_remains_superficial_fallback():
    engine = Z3Engine()
    engine.available = False
    result = engine.reason("análise superficial", constraints=["A", "not A"])
    assert result.available is False
    assert result.confidence == 0.6
    assert "Possível contradição" in result.conclusion
    assert "SATISFATÍVEL" not in result.conclusion


@pytest.mark.parametrize("constraints,expected", [
    (["1/2 == 0"], "unsat"),
    (["x == 0", "x == 1/2"], "unsat"),
    (["1/2 == 0.5"], "sat"),
    (["-1/2 == -0.5"], "sat"),
    (["-1/2 == -1"], "unsat"),
    (["x == 1/y", "y == 2"], "unsat"),
    (["x == 1/y", "y == -1"], "sat"),
])
def test_division_has_real_fraction_semantics(traced_solver, constraints, expected):
    _, events = traced_solver
    result = Z3Engine().reason("divisão real usual", constraints=constraints)
    if expected == "sat":
        assert result.confidence == 0.95
        assert "SATISFATÍVEL" in result.conclusion
        assert events == ["check", "model"]
    else:
        assert result.confidence == 0.9
        assert "unsat" in result.conclusion
        assert events == ["check"]


@pytest.mark.parametrize("constraint", [
    "x == 1/0", "x == 0/0", "x == 1/(2-2)",
    "not (x == 1/0)", "x == 0 or 1/0 == 2", "1/(x-x) == 1",
])
def test_known_zero_divisor_refused_before_check(traced_solver, constraint):
    _, events = traced_solver
    result = Z3Engine().reason("operação indefinida", constraints=[constraint])
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert "zero" in result.conclusion
    assert events == []


@pytest.mark.parametrize("constraint", [
    "x == 1/y", "not (x == 1/y)",
    "(x == 1/y) or (x == 0)", "x == 0 or 1/y == 2",
    "not ((x == 1/y) and (x == 0))", "x == 1/(1/y)",
])
def test_symbolic_division_domain_cannot_hide_inside_not_or_or(traced_solver, constraint):
    _, events = traced_solver
    result = Z3Engine().reason("domínio da fórmula inteira", constraints=[constraint, "y == 0"])
    assert result.confidence == 0.9
    assert "unsat" in result.conclusion
    assert events == ["check"]


def test_nonzero_symbolic_divisor_keeps_real_model(traced_solver):
    _, events = traced_solver
    result = Z3Engine().reason("divisão definida", constraints=["x == 1/y", "x == 1"])
    assert result.confidence == 0.95
    assert "'x': '1'" in result.conclusion
    assert "'y': '1'" in result.conclusion
    assert events == ["check", "model"]


@pytest.mark.parametrize("constraint", [
    "x == 0**-1", "not (x == 0**-1)",
    "x == 0 or 0**-1 == 2", "x == (2-2)**-1",
])
def test_known_zero_base_negative_power_refused_before_check(traced_solver, constraint):
    _, events = traced_solver
    result = Z3Engine().reason("potência indefinida", constraints=[constraint])
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert "zero" in result.conclusion
    assert events == []


@pytest.mark.parametrize("constraints", [
    ["x == y**-1", "y == 0"],
    ["not (x == y**-1)", "y == 0"],
    ["(x == y**-1) or x == 0", "y == 0"],
    ["x == y**z", "y == 0", "z == -1"],
    ["x == 0**z", "z == -1"],
])
def test_negative_power_domain_cannot_admit_zero_base(traced_solver, constraints):
    _, events = traced_solver
    result = Z3Engine().reason("domínio da potência inteira", constraints=constraints)
    assert result.confidence == 0.9
    assert "unsat" in result.conclusion
    assert events == ["check"]


@pytest.mark.parametrize("constraints,expected", [
    (["0**0 == 1"], "sat"), (["0**0 == 0"], "unsat"),
    (["0**z == 1", "z == 0"], "sat"),
    (["0**z == 0", "z == 0"], "unsat"),
    (["y**z == 1", "y == 0", "z == 0"], "sat"),
    (["x == y**z", "x == 0", "y == 0", "z == 0"], "unsat"),
    (["(-2)**-1 == -0.5"], "sat"),
])
def test_zero_exponent_and_defined_negative_power_preserve_semantics(traced_solver, constraints, expected):
    _, events = traced_solver
    result = Z3Engine().reason("potência definida", constraints=constraints)
    if expected == "sat":
        assert result.confidence == 0.95
        assert "SATISFATÍVEL" in result.conclusion
        assert events == ["check", "model"]
    else:
        assert result.confidence == 0.9
        assert "unsat" in result.conclusion
        assert events == ["check"]


@pytest.mark.parametrize("constraint", [
    "x == 1%0", "x == 1%y", "not (1%y == 2)",
    "x == 0 or 1%y == 2", "-5%2 == 1",
])
def test_modulo_remains_outside_z3_grammar(traced_solver, constraint):
    _, events = traced_solver
    result = Z3Engine().reason("gramática preservada", constraints=[constraint])
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion
    assert events == []
