# -*- coding: utf-8 -*-
from typing import Dict, Any

def calculate_scores(question: str, uncertainty_profile: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, float]:
    overrides = context.get("scoring_overrides", {}).get(question, {})
    
    words = question.lower().split()
    q_len = len(question)
    
    # URS: Uncertainty Reduction Score
    base_urs = 0.5
    if "equivalência" in question.lower() or "incerteza" in question.lower():
        base_urs += 0.2
    if "diferença" in question.lower():
        base_urs += 0.1
    urs = min(1.0, max(0.0, overrides.get("URS", base_urs)))
    
    # SVS: Structural Value Score
    base_svs = 0.4
    if "medir" in question.lower() or "preservar" in question.lower() or "h1" in question.lower():
        base_svs += 0.3
    svs = min(1.0, max(0.0, overrides.get("SVS", base_svs)))
    
    # DRI: Dispersion Risk Index
    base_dri = 0.2
    if len(words) > 12:
        base_dri += 0.2
    dri = max(0.0, overrides.get("DRI", base_dri))
    
    # CCI: Cognitive Cost Index
    base_cci = 0.15
    if q_len > 70:
        base_cci += 0.15
    cci = max(0.0, overrides.get("CCI", base_cci))
    
    # Formula: CS = URS + SVS - DRI - CCI
    cs = urs + svs - dri - cci
    
    return {
        "URS": round(urs, 3),
        "SVS": round(svs, 3),
        "DRI": round(dri, 3),
        "CCI": round(cci, 3),
        "CS": round(cs, 3)
    }
