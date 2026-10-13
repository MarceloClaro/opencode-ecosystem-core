"""Contratos semânticos e adversariais; existência não comprova função."""
import ast
from pathlib import Path

import pytest


@pytest.mark.parametrize('expr', ["__import__('os').system('x')", '(2).__class__',
                                "x[0] > 1", 'x > 1 and unknown(x)', '2+3'])
def test_smt_recusa_formula_integralmente(expr):
    from reasoning.z3_solver import check
    result = check(expr, {})
    assert result['status'] == 'fallback'
    assert result['available'] is False


def test_smt_respeita_atribuicoes_e_contradicao():
    pytest.importorskip('z3')
    from reasoning.z3_solver import check
    assert check('x > 1', {'x': 2})['status'] == 'sat'
    assert check('x > 1', {'x': 0})['status'] == 'unsat'
    assert check('x > 1 and x < 0', {})['status'] == 'unsat'
    assert check('x == 0.5', {'x': .5})['status'] == 'sat'


@pytest.mark.parametrize('variables', [{'x': float('nan')}, {'x': True}, {'x': object()}, {'__private': 1}])
def test_atribuicoes_invalidas_nao_produzem_veredito(variables):
    from reasoning.z3_solver import check
    assert check('x > 1', variables)['status'] == 'fallback'


def test_route_reflete_soma_integral_e_nao_fabrica_confianca():
    pytest.importorskip('sympy')
    from reasoning.reasoning_engines import route
    result = route('2+3')
    assert result['engine'] == 'sympy' and result['result'] == '5'
    assert result['available'] is True
    assert result['trust'] is None and result['justified_trust'] is None
    assert route('integrate(sin(x), x)')['result'] == '-cos(x)'
    unparsed = route('integrar sin(x)')
    assert unparsed['available'] is False and unparsed.get('result') is None


def test_texto_externo_nao_chega_a_sympify(monkeypatch):
    import sympy
    from reasoning.reasoning_engines import route
    calls = []
    monkeypatch.setattr(sympy, 'sympify', lambda *a, **k: calls.append(a) or (_ for _ in ()).throw(AssertionError('parser externo')))
    result = route("__import__('os').system('x')+1")
    assert not calls
    assert result['available'] is False and result.get('result') is None


def test_fonte_reasoning_proibe_execucao_dinamica_e_reparsing():
    root = Path(__file__).resolve().parents[1] / 'reasoning'
    prohibited = []
    for path in root.glob('*.py'):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ''
                if name in {'eval', 'exec', 'sympify', 'parse_expr'}:
                    prohibited.append((path.name, node.lineno, name))
    assert prohibited == []
