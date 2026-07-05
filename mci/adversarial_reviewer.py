# -*- coding: utf-8 -*-
from typing import Dict, Any

def run_adversarial_review(claim: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    findings = []
    
    if not claim.get("dataset_refs"):
        findings.append("Ausência de referência explícita de dataset.")
    if claim.get("p_value") is None:
        findings.append("Sem p-valor: evidência insuficiente para decisão forte.")
    if claim.get("confidence_interval") is None:
        findings.append("Intervalo de confiança ausente.")
    if claim.get("effect_size") is not None and abs(claim["effect_size"]) < 0.2:
        findings.append("Tamanho de efeito fraco detectado.")
        
    claim["adversarial_findings"] = findings
    
    if findings and claim["final_verdict"] == "supported":
        if len(findings) >= 2 or claim.get("p_value", 0.0) > 0.04:
            claim["final_verdict"] = "inconclusive"
            
    return claim
