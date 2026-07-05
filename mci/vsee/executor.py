# -*- coding: utf-8 -*-
from typing import Dict, Any, Callable

def execute_path(path: str, executor_fn: Callable, context: Dict[str, Any]) -> Any:
    if path == "vector":
        if context.get("simulate_vector_exception", False):
            raise RuntimeError("Erro ao executar atalho vetorial")
        return {
            "result_type": "vector",
            "data": "Resultado vetorial comprimido",
            "fidelity": context.get("expected_fidelity", 0.95)
        }
    else:
        if executor_fn:
            return executor_fn(context)
        return {
            "result_type": "original",
            "data": "Resultado da execução original de raciocínio pesado"
        }
