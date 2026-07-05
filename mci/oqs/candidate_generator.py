# -*- coding: utf-8 -*-
from typing import List, Dict, Any

def generate_candidates(problem_text: str, context: Dict[str, Any]) -> List[str]:
    candidates = context.get("candidates", [])
    if candidates:
        return candidates
    
    clean_text = problem_text.strip()
    if clean_text.endswith("?"):
        clean_text = clean_text[:-1]
        
    return [
        f"Qual é a diferença entre resumir e preservar a estrutura em: {clean_text}?",
        f"A hipótese H1 reduz o espaço de incerteza em: {clean_text}?",
        f"Existe equivalência estrutural ou contraexemplo para: {clean_text}?",
        f"Como medir e validar quantitativamente: {clean_text}?"
    ]
