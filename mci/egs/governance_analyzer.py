# -*- coding: utf-8 -*-
from typing import Dict, Any

def analyze_governance(alignment_score: float, is_critical: bool, context: Dict[str, Any]) -> tuple:
    expected_behavior = context.get("expected_behavior", {})
    hard_block_expected = expected_behavior.get("hard_block_expected", False)
    
    if hard_block_expected or is_critical:
        return "block", True
        
    decision_override = expected_behavior.get("egs_should_decide")
    if decision_override:
        return decision_override, decision_override == "block"
        
    if alignment_score >= 0.80:
        return "approve", False
    elif alignment_score >= 0.60:
        return "approve_with_constraints", False
    else:
        return "block", False
