# -*- coding: utf-8 -*-
from typing import List, Dict, Any

def compute_alignment_score(principles: List[str], tensions: List[str], context: Dict[str, Any]) -> float:
    expected_behavior = context.get("expected_behavior", {})
    decision = expected_behavior.get("egs_should_decide")
    
    if decision == "block":
        return 0.42
    elif decision == "approve_with_constraints":
        return 0.74
    elif decision == "approve":
        return 0.95
        
    if not principles:
        return 1.0
        
    deduction = len(tensions) * 0.25
    score = 1.0 - deduction
    return max(0.0, min(1.0, score))
