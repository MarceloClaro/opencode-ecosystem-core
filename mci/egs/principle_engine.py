# -*- coding: utf-8 -*-
from typing import List, Dict, Any

def get_principles(context: Dict[str, Any]) -> List[str]:
    return context.get("principles", [
        "dignidade humana",
        "autonomia",
        "transparência",
        "justiça",
        "não maleficência",
        "supervisão humana"
    ])
