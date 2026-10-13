"""R818: entradas externas são validadas antes de qualquer operação simbólica."""

import pytest
import sympy

from reasoning.engines import MultiReasoningEngine, SymPyEngine


UNSAFE = [
    "__import__('os')", "open('arquivo')", "x.__class__", "x[0]",
    "(lambda: 0)()", "[x for x in (1,2)]", "{x: 1}", "import os",
    "eval(1)", "foo(x)", "sin(x, evaluate=False)", "sin(*x)",
    "sin(**x)", "_private", "__builtins__", "True", "'texto'",
    "x if True else y", "(x := 1)", "x == 2", "1 # comentário",
    "[1,2]", "(1,2)", "1e999", "9**9**9", "x**1000000",
    "texto administrativo 2 + 3", "resolver um conflito", "",
    "x+" * 300 + "x",
]


@pytest.mark.parametrize("expression", UNSAFE)
def test_unsafe_input_never_reaches_text_sympify(monkeypatch, expression):
    calls = []
    original = sympy.sympify

    def guarded(value, *args, **kwargs):
        if isinstance(value, str):
            calls.append(value)
            raise AssertionError("fronteira bloqueada antes de executar qualquer texto")
        return original(value, *args, **kwargs)

    monkeypatch.setattr(sympy, "sympify", guarded)
    result = SymPyEngine().reason("consulta de teste", expression=expression)
    assert calls == []
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion


@pytest.mark.parametrize("expression,expected", [
    ("2 + 3*4", "14"), ("-2 + +3", "1"), ("1/3 + 1/6", "1/2"),
    ("sin(x)**2 + cos(x)**2", "1"), ("sqrt(16)", "4"),
    ("diff(x**3, x)", "3*x**2"), ("diff(x**3, x, 2)", "6*x"),
    ("integrate(x, x)", "x**2/2"), ("integrate(x, (x, 0, 1))", "1/2"),
    ("solve(x**2 - 4, x)", "[-2, 2]"), ("2*x = 8", "[4]"),
    ("x**2 = 4", "[-2, 2]"), ("exp(0) + log(1)", "1"),
])
def test_allowed_math_preserves_real_symbolic_result(monkeypatch, expression, expected):
    calls = []
    original = sympy.sympify

    def guarded(value, *args, **kwargs):
        if isinstance(value, str):
            calls.append(value)
            raise AssertionError("nenhum texto externo deve ser reparsado")
        return original(value, *args, **kwargs)

    monkeypatch.setattr(sympy, "sympify", guarded)
    result = SymPyEngine().reason("cálculo", expression=expression)
    assert result.confidence == 0.95
    assert result.conclusion.endswith(expected)
    assert calls == []


@pytest.mark.parametrize("expression", ["garbage12 + 3", "text 2", "x + 2", "sin(2)", "2*x=8", "True", "[1,2]", "1e999"])
def test_numeric_fallback_rejects_input_without_sanitizing(expression):
    engine = SymPyEngine()
    engine.available = False
    result = engine.reason("fallback", expression=expression)
    assert result.confidence == 0.0
    assert result.available is False
    assert "recusada" in result.conclusion


@pytest.mark.parametrize("expression,expected", [("2+3*4", "14.0"), ("-2 + +3", "1.0"), ("5 % 2", "1.0")])
def test_numeric_fallback_keeps_arithmetic(expression, expected):
    engine = SymPyEngine()
    engine.available = False
    result = engine.reason("fallback", expression=expression)
    assert result.confidence == 0.6
    assert result.conclusion.endswith(expected)


@pytest.mark.parametrize("expression", [False, 2, [], {}])
def test_non_string_expression_is_refused(expression):
    result = SymPyEngine().reason("cálculo", expression=expression)
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion


@pytest.mark.parametrize("query", ["resolver um conflito", "integralidade dos dados", "simplificar o procedimento", "x.__class__", "2 and 3"])
def test_non_math_prose_does_not_route_to_symbolic_engine(query):
    assert MultiReasoningEngine._route(query) != "sympy"


@pytest.mark.parametrize("query", ["2+2", "diff(x**2, x)", "integrate(x, x)", "resolver equação x=2"])
def test_math_routes_to_symbolic_engine(query):
    assert MultiReasoningEngine._route(query) == "sympy"


def test_auto_route_with_explicit_expression_uses_math_not_query_text():
    result = MultiReasoningEngine().reason("resolver", expression="2*x = 8")
    assert result.engine == "sympy"
    assert result.conclusion.endswith("[4]")


def test_descriptive_math_query_is_not_silently_parsed():
    result = SymPyEngine().reason("resolver equação x=2")
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion


@pytest.mark.parametrize("expression", [
    "2**(1000000 + 1)", "2**(999999 * 999999)", "2**1e9",
    "x**(200 + 100)", "(1000 * 1000)**256",
    "2**sqrt(1000000000000)", "2**(x-x+1000000)",
])
def test_computed_power_budgets_rejected_before_sympy(monkeypatch, expression):
    import reasoning.engines as engines
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError("nenhuma expressão expansiva pode alcançar o construtor")

    monkeypatch.setattr(engines, "_build_sympy_math", forbidden)
    result = SymPyEngine().reason("limite sintático", expression=expression)
    assert result.confidence == 0.0
    assert calls == []


@pytest.mark.parametrize("expression,expected", [("x**(2+1)", "x**3"), ("4**0.5", "2.00000000000000")])
def test_small_computed_and_fractional_powers_preserved(expression, expected):
    result = SymPyEngine().reason("potência limitada", expression=expression)
    assert result.confidence == 0.95
    assert result.conclusion.endswith(expected)


@pytest.mark.parametrize("expression", [
    "sin(x) + foo(x)", "integrate(x, x) = foo(x)",
    "sin(x) + x.__class__", "integrate(x, (x, 0, foo(x)))",
    "diff(x**3, x, 1000000)", "sin(x, y)", "integrate(x, (1, 0, 1))",
    "x+" * 130 + "x", "-" * 34 + "1", "9" * 80,
    "a" * 65 + " + 1", "1+" * 2100 + "1", "𝐱 + 1",
])
def test_entire_expression_validated_before_any_sympy_construction(monkeypatch, expression):
    import reasoning.engines as engines
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError("nenhuma construção antes de validar toda a entrada")

    monkeypatch.setattr(engines, "_build_sympy_math", forbidden)
    result = SymPyEngine().reason("guarda integral", expression=expression)
    assert result.confidence == 0.0
    assert calls == []


@pytest.mark.parametrize("expression", [
    "0/0", "1/0", "1/(2-2)", "(1/0)**0", "0*(1/0)",
    "log(0)", "tan(pi/2)", "1/0 = 1/0", "solve(1/0, x)",
    "integrate(1/0, x)", "diff(1/0, x)",
])
def test_undefined_intermediate_or_final_result_is_refused(expression):
    result = SymPyEngine().reason("operação indefinida", expression=expression)
    assert result.available is True
    assert result.confidence == 0.0
    assert "recusada" in result.conclusion


@pytest.mark.parametrize("expression,expected", [
    ("sqrt(-1)", "I"), ("log(-1)", "I*pi"),
    ("1/x", "1/x"), ("log(x)", "log(x)"),
])
def test_finite_complex_or_unknown_symbolic_domain_is_preserved(expression, expected):
    result = SymPyEngine().reason("expressão simbólica válida", expression=expression)
    assert result.confidence == 0.95
    assert result.conclusion.endswith(expected)
