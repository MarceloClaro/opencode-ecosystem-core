"""Gate explícito para o teste de execução real GJQ (R1106).

Nada aqui executa job. O teste de fumaça só roda quando o operador define
GJQ_REAL_EXECUTION=1 e GJQ_API_KEY no ambiente. Hardware é recusado.
"""
from __future__ import annotations

import os

from integrations.gjq_backend_registry import is_hardware_name


def real_execution_enabled() -> bool:
    flag = os.environ.get("GJQ_REAL_EXECUTION", "").strip().lower()
    key = os.environ.get("GJQ_API_KEY", "").strip()
    return flag in {"1", "true", "yes", "on"} and bool(key)


def real_backend() -> str:
    backend = os.environ.get("GJQ_REAL_EXECUTION_BACKEND", "FAS-CPU").strip() or "FAS-CPU"
    if is_hardware_name(backend):
        raise ValueError(
            "o teste de fumaça real só aceita simulador; "
            f"backend recusado: {backend!r}"
        )
    return backend
