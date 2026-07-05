# -*- coding: utf-8 -*-
from typing import Dict, Any

def calibrate_confidence(claim: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    base = 0.5
    
    p_value = claim.get("p_value")
    if p_value is not None:
        if p_value < 0.01:
            base += 0.25
        elif p_value < 0.05:
            base += 0.15
        else:
            base -= 0.15
            
    if claim.get("confidence_interval") is not None:
        base += 0.10
        
    findings = claim.get("adversarial_findings", [])
    if findings:
        base -= min(0.25, 0.05 * len(findings))
        
    claim["calibrated_confidence"] = max(0.0, min(1.0, round(base, 3)))
    
    reproducibility = context.get("reproducibility_score", 0.85)
    claim["reproducibility_score"] = float(reproducibility)
    
    return claim
