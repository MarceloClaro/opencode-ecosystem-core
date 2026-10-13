# -*- coding: utf-8 -*-
"""Contrato declarativo de entrada, sem aprovação de entrega ou testes.

O gate de execução pertence ao primário, SpecVerifier e TDDRunner. `approved`
é alias de `input_valid`; não consulta o registro nem executa a especificação.
"""
from __future__ import annotations
def check(spec_id: str = "", tests_green: bool = False, **_) -> dict:
    ok = isinstance(spec_id, str) and spec_id.startswith("SPEC-935-R") and tests_green is True
    return {
        "approved": ok, "input_valid": ok, "gate": "sdd_gate", "spec": spec_id,
        "runtime_gate": False, "execution_verified": False,
        "verification": "input_contract_only",
        "reason": "forma da entrada aceita; entrega não verificada" if ok else "entrada inválida",
    }
