# -*- coding: utf-8 -*-
from typing import List, Dict, Any

def get_recommendations(tensions: List[str]) -> List[str]:
    recs = []
    for tension in tensions:
        if "discriminação" in tension.lower() or "viés" in tension.lower():
            recs.append("Aplicar auditoria demográfica e balanceamento do conjunto de treinamento.")
        if "supervisão" in tension.lower():
            recs.append("Integrar um gate de validação human-in-the-loop (HITL) para aprovação manual.")
        if "alto" in tension.lower():
            recs.append("Mitigar riscos éticos restringindo o escopo a ambientes de teste controlados.")
    if not recs and tensions:
        recs.append("Realizar revisão ética manual detalhada.")
    return recs
