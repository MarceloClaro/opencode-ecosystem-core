# -*- coding: utf-8 -*-
import os
import json
import uuid
from typing import Dict, Any, Callable
import jsonschema

from .policy import evaluate_routing_policy
from .fallback import execute_with_fallback
from .telemetry import compute_telemetry

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "schemas",
    "vector_execution_decision.schema.json"
)

def run_vsee_router(executor_fn: Callable, context: Dict[str, Any] = None) -> Dict[str, Any]:
    if context is None:
        context = {}
        
    req_id = f"req-{uuid.uuid4().hex[:8]}"
    
    policy_res = evaluate_routing_policy(context)
    chosen_path = policy_res["chosen_path"]
    
    actual_path, fallback_triggered, execution_result = execute_with_fallback(
        chosen_path, executor_fn, context
    )
    
    telemetry_data = compute_telemetry(actual_path, context)
    
    if fallback_triggered:
        telemetry_data = compute_telemetry("original", context)
        
    result = {
        "request_id": req_id,
        "chosen_path": actual_path,
        "policy_reason": policy_res["policy_reason"],
        "risk_level": policy_res["risk_level"],
        "expected_gain": float(policy_res["expected_gain"]),
        "fallback_triggered": fallback_triggered,
        "telemetry": telemetry_data,
        "result_data": execution_result,
        "version": "1.0.0"
    }
    
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        val_data = {k: v for k, v in result.items() if k != "result_data"}
        jsonschema.validate(instance=val_data, schema=schema)
        
    return result
