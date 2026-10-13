# -*- coding: utf-8 -*-
"""Fachada SMT R830/R838 sobre a gramática restrita canônica R821.

Símbolos livres são inteiros. Atribuições explícitas substituem símbolos por
literais numéricos finitos. SAT/UNSAT não são produzidos por um fallback.
"""
from __future__ import annotations
import math
import re


def _try_z3(expr: str, variables: dict):
    """Traduz a expressão integral; nunca transforma consulta ignorada em SAT."""
    try:
        if not isinstance(variables, dict) or len(variables) > 64:
            raise ValueError('atribuições inválidas ou acima do limite')
        import z3
        from reasoning.engines import _safe_build_z3_constraint
        env = {}
        for name, value in variables.items():
            if not isinstance(name, str) or re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}', name) is None:
                raise ValueError('nome de variável inválido')
            if type(value) not in (int, float):
                raise ValueError('atribuição exige número finito')
            if type(value) is int and value.bit_length() > 256:
                raise ValueError('inteiro acima do limite')
            if type(value) is float and not math.isfinite(value):
                raise ValueError('atribuição não finita')
            env[name] = z3.IntVal(value) if type(value) is int else z3.RealVal(str(value))
        formula = _safe_build_z3_constraint(expr, env)
        solver = z3.Solver()
        solver.set(timeout=5000, rlimit=100000)
        solver.add(formula)
        verdict = str(solver.check())
        return {'smt': verdict, 'ok': verdict in ('sat', 'unsat'), 'encoded': str(formula)}
    except Exception as exc:
        # Erros de entrada/backend opcional não concluem parte da fórmula.
        return {'smt': 'unknown', 'ok': False, 'error': str(exc)[:200]}


def check(expr: str, variables: dict | None = None) -> dict:
    result = _try_z3(expr, {} if variables is None else variables)
    return {
        'engine': 'z3_solver', 'status': result['smt'] if result['ok'] else 'fallback',
        'available': result['ok'], 'smt': result['smt'],
        'expr': expr[:4096] if isinstance(expr, str) else None,
        'encoded': result.get('encoded'), 'reason': result.get('error'),
        'verification': 'local_smt_execution' if result['ok'] else 'not_evaluated',
        'variable_domain': 'integer_free_symbols_explicit_numeric_substitution',
        'calibrated': False,
    }
