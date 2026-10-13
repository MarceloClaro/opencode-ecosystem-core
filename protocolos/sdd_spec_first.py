# -*- coding: utf-8 -*-
"""Contrato declarativo de identificação; não comprova especificação prévia.

Não consulta registro, artefato, ordem temporal ou execução. `approved` é alias
de `input_valid`. O gate real pertence ao primário e ao SpecVerifier.
"""
from __future__ import annotations
def check(spec_id: str = "", **_) -> dict:
    ok = isinstance(spec_id, str) and spec_id.startswith("SPEC-935-R")
    return {
        "approved": ok, "input_valid": ok, "spec": spec_id,
        "runtime_gate": False, "execution_verified": False,
        "verification": "input_contract_only",
        "reason": "forma do identificador aceita; especificação não verificada" if ok else "identificador ausente ou inválido",
    }
