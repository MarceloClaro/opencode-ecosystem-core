# -*- coding: utf-8 -*-
import uuid
from typing import Dict, Any

def generate_hypothesis(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    clean_q = question.strip()
    if clean_q.endswith("?"):
        clean_q = clean_q[:-1]
        
    h1 = f"H1: {clean_q} produz um efeito estatisticamente significativo e positivo."
    h0 = f"H0: {clean_q} não possui efeito estatisticamente significativo (efeito nulo)."
    
    return {
        "claim_id": f"clm-{uuid.uuid4().hex[:8]}",
        "hypothesis": h1,
        "null_hypothesis": h0,
        "experimental_design": {
            "type": "randomized_control_trial",
            "sample_strategy": "stratified_random_sampling",
            "stop_criteria": "minimum_sample_size_reached_and_power_0.8"
        },
        "dataset_refs": context.get("dataset_refs", ["dataset_default_v1"]),
        "metrics": context.get("metrics", ["F1-score", "Latency", "Accuracy"]),
        "statistical_tests": context.get("statistical_tests", ["paired_t_test"]),
        "effect_size": None,
        "confidence_interval": None,
        "p_value": None,
        "bayes_factor": None,
        "limitations": [
            "Os dados experimentais estão sujeitos a ruído de rede e hardware.",
            "A inferência causal assume a ausência de confounders não medidos."
        ],
        "reproducibility_score": 0.0,
        "calibrated_confidence": 0.0,
        "adversarial_findings": [],
        "final_verdict": "inconclusive"
    }
