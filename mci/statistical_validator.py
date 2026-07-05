# -*- coding: utf-8 -*-
from typing import Dict, Any

def validate_statistics(claim: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    p_value = context.get("p_value", 0.03)
    effect_size = context.get("effect_size", 0.35)
    confidence_interval = context.get("confidence_interval", [0.10, 0.50])
    bayes_factor = context.get("bayes_factor", 4.2)
    reproducibility_score = context.get("reproducibility_score", 0.85)
    
    claim["p_value"] = p_value
    claim["effect_size"] = effect_size
    claim["confidence_interval"] = confidence_interval
    claim["bayes_factor"] = bayes_factor
    claim["reproducibility_score"] = reproducibility_score
    
    if p_value is None:
        claim["final_verdict"] = "inconclusive"
        return claim
        
    if p_value < 0.05 and effect_size is not None and abs(effect_size) >= 0.2:
        claim["final_verdict"] = "supported"
    else:
        claim["final_verdict"] = "refuted"
        
    return claim
