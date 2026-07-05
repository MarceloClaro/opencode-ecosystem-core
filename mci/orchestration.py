# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Any
import jsonschema

from .hypothesis_engine import generate_hypothesis
from .experiment_designer import design_experiment
from .statistical_validator import validate_statistics
from .adversarial_reviewer import run_adversarial_review
from .confidence_calibrator import calibrate_confidence
from .scientific_reporter import build_report

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "schemas",
    "scientific_claim.schema.json"
)

class ScientificRunResult:
    def __init__(self, claim: Dict[str, Any], report_tex: str):
        self.claim = claim
        self.report_tex = report_tex

def run_scientific_cycle(question: str, context: Dict[str, Any] = None) -> ScientificRunResult:
    if context is None:
        context = {}
        
    claim = generate_hypothesis(question=question, context=context)
    claim = design_experiment(claim=claim, context=context)
    claim = validate_statistics(claim=claim, context=context)
    claim = run_adversarial_review(claim=claim, context=context)
    claim = calibrate_confidence(claim=claim, context=context)
    report_tex = build_report(claim=claim, context=context)
    
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        jsonschema.validate(instance=claim, schema=schema)
        
    return ScientificRunResult(claim=claim, report_tex=report_tex)
