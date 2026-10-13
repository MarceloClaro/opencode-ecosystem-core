# -*- coding: utf-8 -*-
"""Fachada R830/R838: entrada real, gramática canônica e limites declarados."""
from __future__ import annotations
import ast


def route(query: str) -> dict:
    base = {'derivation_trail': ['parse', 'validate'], 'trust': None,
            'justified_trust': None, 'calibrated': False,
            'reasoning_engines': True}
    if not isinstance(query, str) or not query.strip() or len(query) > 4096:
        return {**base, 'engine': 'fallback', 'available': False, 'reason': 'entrada inválida ou acima do limite'}
    # AST só classifica; a gramática inteira é validada pelo backend canônico.
    try:
        tree = ast.parse(query.strip(), mode='eval')
    except (SyntaxError, ValueError, RecursionError):
        return {**base, 'engine': 'fallback', 'available': False, 'reason': 'forneça expressão matemática explícita'}
    if any(isinstance(node, (ast.Compare, ast.BoolOp)) for node in ast.walk(tree)):
        from reasoning.z3_solver import check
        return {**base, **check(query), 'derivation_trail': base['derivation_trail'] + ['z3_solver']}
    from reasoning.engines import SymPyEngine
    result = SymPyEngine().reason(query)
    successful = result.available and result.confidence > 0
    prefix, separator, answer = result.conclusion.partition(': ')
    return {**base, 'engine': 'sympy' if successful else 'fallback',
            'available': bool(successful), 'result': answer if successful and separator else None,
            'reason': None if successful else result.conclusion,
            'derivation_trail': base['derivation_trail'] + result.steps,
            'verification': 'local_symbolic_execution' if successful else 'not_evaluated'}
