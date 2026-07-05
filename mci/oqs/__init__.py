# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Any
import jsonschema

from .intake import normalize_problem
from .uncertainty_scanner import scan_uncertainty
from .candidate_generator import generate_candidates
from .scoring import calculate_scores
from .selector import select_optimal_question

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "schemas",
    "optimal_question.schema.json"
)

def run_oqs_scanner(problem_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    if context is None:
        context = {}
        
    normalized = normalize_problem(problem_text)
    prob_id = normalized["problem_id"]
    
    unc_profile = scan_uncertainty(normalized, context)
    candidates = generate_candidates(problem_text, context)
    
    scored_candidates = []
    for q in candidates:
        scores = calculate_scores(q, unc_profile, context)
        scored_candidates.append((q, scores))
        
    selection_result = select_optimal_question(scored_candidates)
    
    scores = selection_result["scores"]
    pass_gate = (
        scores["URS"] >= 0.40 and
        scores["SVS"] >= 0.40 and
        scores["DRI"] <= 0.50
    )
    
    result = {
        "problem_id": prob_id,
        "candidates": candidates,
        "selected_question": selection_result["selected_question"],
        "scores": scores,
        "selection_rationale": selection_result["selection_rationale"],
        "discarded_with_reason": selection_result["discarded_with_reason"],
        "pass": pass_gate,
        "version": "1.0.0"
    }
    
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        val_data = {k: v for k, v in result.items() if k != "pass"}
        jsonschema.validate(instance=val_data, schema=schema)
        
    return result
