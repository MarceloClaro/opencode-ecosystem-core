# -*- coding: utf-8 -*-
from typing import Dict, Any

def compute_telemetry(path: str, context: Dict[str, Any]) -> Dict[str, float]:
    if path == "vector":
        eg = context.get("eg", 1.25)
        trr = context.get("trr", 0.35)
        ri = context.get("ri", 1.4)
        efs = context.get("efs", 0.95)
    else:
        eg = 1.0
        trr = 0.0
        ri = 1.0
        efs = 1.0
        
    return {
        "EG": round(eg, 3),
        "TRR": round(trr, 3),
        "RI": round(ri, 3),
        "EFS": round(efs, 3)
    }
