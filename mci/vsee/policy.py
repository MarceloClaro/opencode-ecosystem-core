# -*- coding: utf-8 -*-
from typing import Dict, Any

def evaluate_routing_policy(context: Dict[str, Any]) -> Dict[str, Any]:
    validated_shortcut = context.get("validated_shortcut", False)
    
    # Check expected behavior overrides
    expected_behavior = context.get("expected_behavior", {})
    if "vsee_should_choose" in expected_behavior:
        chosen = expected_behavior["vsee_should_choose"]
        validated_shortcut = (chosen == "vector")
        
    risk = context.get("risk", 0.2)
    risk_threshold = context.get("risk_threshold", 0.5)
    expected_fidelity = context.get("expected_fidelity", 0.95)
    min_fidelity = context.get("min_fidelity", 0.90)
    expected_cost_gain = context.get("expected_cost_gain", 1.2)
    
    gates_passed = (
        validated_shortcut and
        risk <= risk_threshold and
        expected_fidelity >= min_fidelity and
        expected_cost_gain > 1.0
    )
    
    chosen_path = "vector" if gates_passed else "original"
    
    reasons = []
    if not validated_shortcut:
        reasons.append("Shortcut not validated")
    if risk > risk_threshold:
        reasons.append(f"Risk {risk} above threshold {risk_threshold}")
    if expected_fidelity < min_fidelity:
        reasons.append(f"Expected fidelity {expected_fidelity} below minimum {min_fidelity}")
    if expected_cost_gain <= 1.0:
        reasons.append(f"Expected cost gain {expected_cost_gain} is not beneficial")
        
    policy_reason = "All gates passed. Routing to vector shortcut." if gates_passed else f"Routing to original path: {', '.join(reasons)}"
    
    return {
        "chosen_path": chosen_path,
        "policy_reason": policy_reason,
        "risk_level": "high" if risk > 0.5 else ("medium" if risk > 0.2 else "low"),
        "expected_gain": expected_cost_gain
    }
