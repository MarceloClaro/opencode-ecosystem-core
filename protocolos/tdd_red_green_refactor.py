# -*- coding: utf-8 -*-
"""Contrato de declarações TDD do chamador; não executa nem verifica fases.

Texto em `red_hash` e a flag `green` não provam testes executados. `approved`
é alias de `input_valid`; evidência de runtime pertence ao TDDRunner canônico.
"""
from __future__ import annotations
def check(red_hash: str = "", green: bool = False, **_) -> dict:
    ok = isinstance(red_hash, str) and len(red_hash.strip()) > 0 and green is True
    return {
        "approved": ok, "input_valid": ok,
        "declared_red_hash": red_hash, "declared_green": green,
        "runtime_gate": False, "execution_verified": False,
        "verification": "input_contract_only",
        "reason": "declarações recebidas; fases não executadas" if ok else "declarações inválidas",
    }
