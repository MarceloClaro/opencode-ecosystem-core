# -*- coding: utf-8 -*-
"""R832 — schemas_validator (infra_dados).
Keywords: schemas, schema, validator, schema/, schema.json. Categoria: schemas_validator."""
from __future__ import annotations
def validate(data=None, required=None) -> dict:
    data = data or {}; required = required or []
    missing = [k for k in required if k not in data]
    return {"valid": not missing, "valid_str": str(not missing).lower(), "missing": missing, "schemas": True, "validator": "schemas_validator"}
