# -*- coding: utf-8 -*-
import os
import json
import uuid
from typing import Dict, Any
import jsonschema

from mci.metabus import metabus
from .principle_engine import get_principles
from .stress_test import run_stress_test
from .alignment import compute_alignment_score
from .governance_analyzer import analyze_governance
from .explainability import get_recommendations

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "schemas",
    "ethical_assessment.schema.json"
)

def run_egs_scanner(output_to_check: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    if context is None:
        context = {}
        
    assessment_id = f"ast-{uuid.uuid4().hex[:8]}"
    
    principles = get_principles(context)
    stress_res = run_stress_test(output_to_check, context)
    tensions = stress_res["tensions"]
    is_critical = stress_res["is_critical"]
    
    align_score = compute_alignment_score(principles, tensions, context)
    decision, hard_block = analyze_governance(align_score, is_critical, context)
    recs = get_recommendations(tensions)
    
    risk_buckets = {}
    for i, tension in enumerate(tensions):
        risk_buckets[f"tension_{i+1}"] = "high" if is_critical else "medium"
        
    result = {
        "assessment_id": assessment_id,
        "principles_checked": principles,
        "tensions": tensions,
        "alignment_score": align_score,
        "risk_buckets": risk_buckets,
        "recommendations": recs,
        "decision": decision,
        "hard_block": hard_block,
        "pass": decision != "block",
        "version": "1.0.0"
    }
    
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        val_data = {k: v for k, v in result.items() if k not in ["pass", "hard_block"]}
        jsonschema.validate(instance=val_data, schema=schema)

    metabus.publish_subsystem_event(
        "egs",
        "assessed",
        {
            "assessment_id": assessment_id,
            "decision": decision,
            "hard_block": hard_block,
            "alignment_score": align_score,
            "marker": context.get("marker"),
        },
        source_agent="egs",
    )
    metabus.memory.upsert_semantic_topic(
        "egs.governance",
        lesson=f"EGS avaliou output com decisão={decision} e hard_block={hard_block}.",
        metadata={"last_assessment_id": assessment_id, "last_alignment_score": align_score},
    )
    metabus.memory.update_topic_confidence("egs", align_score)
        
    return result
