# -*- coding: utf-8 -*-
from typing import List, Dict, Any

def run_stress_test(output_to_check: str, context: Dict[str, Any]) -> Dict[str, Any]:
    risk_profile = context.get("risk_profile", {})
    ethical_risk = risk_profile.get("ethical_risk", "low")
    
    tensions = []
    
    expected_behavior = context.get("expected_behavior", {})
    if ethical_risk == "high" or expected_behavior.get("hard_block_expected", False):
        tensions.append("Risco ético alto detectado no perfil do problema.")
        
    text = output_to_check.lower()
    if "discriminação" in text or "discriminatório" in text or "viés" in text:
        tensions.append("Possível viés discriminatório detectado no texto de saída.")
    if "sem supervisão" in text or "autônomo sem controle" in text:
        tensions.append("Ausência de supervisão humana em domínio crítico.")
        
    return {
        "tensions": tensions,
        "is_critical": len(tensions) > 0 and (ethical_risk == "high" or expected_behavior.get("hard_block_expected", False))
    }
