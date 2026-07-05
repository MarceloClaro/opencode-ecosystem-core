# -*- coding: utf-8 -*-
from typing import Dict, Any, Callable
from .executor import execute_path

def execute_with_fallback(path: str, executor_fn: Callable, context: Dict[str, Any]) -> tuple:
    fallback_triggered = False
    result = None
    
    if path == "vector":
        try:
            result = execute_path("vector", executor_fn, context)
            
            min_fidelity = context.get("min_fidelity", 0.90)
            actual_fidelity = result.get("fidelity", 1.0)
            if actual_fidelity < min_fidelity:
                fallback_triggered = True
                
        except Exception as exc:
            fallback_triggered = True
            
        if fallback_triggered:
            result = execute_path("original", executor_fn, context)
            path = "original"
    else:
        result = execute_path("original", executor_fn, context)
        
    return path, fallback_triggered, result
