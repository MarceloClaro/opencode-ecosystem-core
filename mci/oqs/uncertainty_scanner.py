# -*- coding: utf-8 -*-
from typing import Dict, Any

def scan_uncertainty(normalized_problem: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    profile = context.get("uncertainty_profile", {})
    conceptual_gaps = profile.get("conceptual_gaps", 0)
    undefined_terms = profile.get("undefined_terms", 0)
    conflicting_assumptions = profile.get("conflicting_assumptions", 0)

    text = normalized_problem.get("clean_text", "").lower()
    if not profile:
        if "se " in text or "talvez" in text or "hipótese" in text:
            conceptual_gaps += 1
        if "como " in text or "definir" in text or "termo" in text:
            undefined_terms += 1
        if "ou " in text or "versus" in text or "concorrentes" in text or "conflito" in text:
            conflicting_assumptions += 1

    total_uncertainties = conceptual_gaps + undefined_terms + conflicting_assumptions
    return {
        "conceptual_gaps": conceptual_gaps,
        "undefined_terms": undefined_terms,
        "conflicting_assumptions": conflicting_assumptions,
        "total_uncertainty": max(1, total_uncertainties)
    }
