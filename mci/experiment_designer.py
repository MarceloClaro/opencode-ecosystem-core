# -*- coding: utf-8 -*-
from typing import Dict, Any

def design_experiment(claim: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    design_override = context.get("experimental_design", {})
    if design_override:
        claim["experimental_design"].update(design_override)
    return claim
