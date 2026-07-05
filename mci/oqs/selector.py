# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Tuple

def select_optimal_question(scored_candidates: List[Tuple[str, Dict[str, float]]]) -> Dict[str, Any]:
    if not scored_candidates:
        raise ValueError("Sem candidatos para seleção.")
        
    # Sort by CS desc, then question text asc (deterministic tie-breaker)
    sorted_candidates = sorted(scored_candidates, key=lambda item: (-item[1]["CS"], item[0]))
    
    selected_question, selected_scores = sorted_candidates[0]
    
    discarded = []
    for q, s in sorted_candidates[1:]:
        discarded.append({
            "question": q,
            "reason": f"Score de convergência inferior (CS: {s['CS']} vs {selected_scores['CS']})"
        })
        
    return {
        "selected_question": selected_question,
        "scores": selected_scores,
        "selection_rationale": f"Selecionado porque possui o maior score de convergência ({selected_scores['CS']}) entre os candidatos.",
        "discarded_with_reason": discarded
    }
