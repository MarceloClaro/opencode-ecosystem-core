#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Scoring Qualis A1 — Theme-Agnostic & Format-Aware Manuscript Scorer
========================================================================
Supports: Markdown (*.md) and LaTeX (*.tex) files.
Dynamic Theme Adaptation: Adapts scoring rubrics for general sciences, materials science, game theory, etc.
Integrates with MCPs and local ecosystem validations.
"""

import json
import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

RUBRIC = {
    "rigor_academico": {"peso": 10, "desc": "Rigor academico e profundidade teorica"},
    "densidade_citacoes": {"peso": 10, "desc": "Densidade de citacoes (>=55 referencias com DOI)"},
    "abnt_compliance": {"peso": 10, "desc": "Conformidade ABNT/Vancouver/APA e indexadores"},
    "originalidade": {"peso": 10, "desc": "Originalidade e relevancia da contribuicao"},
    "metodologia": {"peso": 10, "desc": "Metodologia reprodutivel e delineamento estatistico"},
    "analise_estatistica": {"peso": 10, "desc": "Analise estatistica rigorosa e validada"},
    "coerencia": {"peso": 10, "desc": "Coerencia argumentativa (intro↔conclusao)"},
    "qualidade_visual": {"peso": 10, "desc": "Qualidade de graficos, tabelas e figuras"},
    "internacionalizacao": {"peso": 10, "desc": "Abstract em ingles + conformidade internacional"},
    "autocontencao": {"peso": 10, "desc": "Tamanho e densidade textual de conformidade"},
}

DOMAIN_KEYWORDS = {
    "materials_science": [
        "pelbd", "rgo", "nanocompos", "grafen", "rotomoldagem", "tração", "flexão", "impacto",
        "tga", "dsc", "xrd", "sem", "mve", "polietileno", "polímero", "argila", "ensaio"
    ],
    "game_theory": [
        "pareto", "nash", "shapley", "minimax", "equilíbrio", "otimização", "teoria dos jogos",
        "jogador", "estratégia", "dilema", "coalizão", "zero-sum", "tit-for-tat", "bargaining"
    ],
    "economics": [
        "sobre-educacao", "overeducation", "armadilha da renda", "bonus demografico", "renda media",
        "pib", "desemprego", "mercado de trabalho", "salário", "capital humano"
    ],
    "machine_learning": [
        "machine learning", "deep learning", "algoritmo", "rede neural", "treinamento", "acurácia",
        "dataset", "cnn", "hiperparâmetro", "validação cruzada", "grad-cam", "overfitting"
    ]
}

def detect_project_format(manuscript_dir: Path) -> Tuple[str, List[Path]]:
    """Detects whether the project is LaTeX-based or Markdown-based."""
    tex_files = sorted(manuscript_dir.glob("*.tex"))
    tex_files = [f for f in tex_files if not f.name.startswith("artigo_disruptivo") and f.name != "template.tex"]
    
    if tex_files:
        return "latex", tex_files
    
    md_files = sorted(manuscript_dir.glob("*.md"))
    md_files = [f for f in md_files if f.name != "SKILL.md" and f.name != "README.md"]
    return "markdown", md_files

def detect_theme_profile(text: str) -> str:
    """Detects theme profile based on keyword match density."""
    text_lower = text.lower()
    scores = {}
    for theme, keywords in DOMAIN_KEYWORDS.items():
        score = sum(text_lower.count(k) for k in keywords)
        scores[theme] = score
    max_theme = max(scores, key=scores.get)
    if scores[max_theme] > 3:
        return max_theme
    return "general_science"

def score_manuscript(manuscript_dir: str) -> Dict[str, Any]:
    """Score a manuscript dynamically adjusting to its format and domain."""
    dir_path = Path(manuscript_dir)
    fmt, files = detect_project_format(dir_path)
    
    contents = []
    for f in files:
        try:
            contents.append(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
    text = "\n".join(contents)
    theme = detect_theme_profile(text)
    
    results = {}
    
    # 1. Rigor Acadêmico (citations + footnotes + bibliographic databases)
    if fmt == "latex":
        citations = len(re.findall(r"\\cite[a-z]*\{[^}]+\}", text))
        footnotes = len(re.findall(r"\\footnote\{", text))
        bibitems = len(re.findall(r"\\bibitem\b", text))
        ref_count = citations + footnotes + bibitems
    else:
        ref_count = text.count("[^") + text.count("doi.org") + text.count("Disponivel em:")
        
    results["rigor_academico"] = min(10, max(5, ref_count // 10))
    
    # 2. Densidade de Citações (DOIs)
    dois_raw = re.findall(r"10\.\d{4,}/[^\s\]>},]+", text)
    dois_url = re.findall(r"doi\.org/10\.[^\s\]>},]+", text)
    doi_count = len(set(dois_raw + [d.replace("doi.org/", "") for d in dois_url]))
    
    results["densidade_citacoes"] = 10 if doi_count >= 55 else min(9, doi_count // 6)
    
    # 3. ABNT / Citation Compliance
    abnt_score = 5
    if fmt == "latex":
        if "\\bibliographystyle" in text or "\\bibliography" in text or "\\printbibliography" in text:
            abnt_score += 3
        if "et al." in text:
            abnt_score += 1
        if "\\cite" in text:
            abnt_score += 1
    else:
        if "ABNT" in text: abnt_score += 1
        if "NBR 6023" in text or "NBR 10520" in text: abnt_score += 2
        if "et al." in text: abnt_score += 1
        if text.count("p.") > 5: abnt_score += 1
    results["abnt_compliance"] = min(10, abnt_score)
    
    # 4. Originalidade (state of the art, unique domain vocabulary)
    originality = 5
    text_lower = text.lower()
    if "contribuicao" in text_lower or "contribuição" in text_lower: originality += 1
    if "inedit" in text_lower or "inédit" in text_lower: originality += 1
    if "lacuna" in text_lower or "gap" in text_lower: originality += 1
    if "estado da arte" in text_lower or "state of the art" in text_lower: originality += 1
    
    theme_keys = DOMAIN_KEYWORDS.get(theme, [])
    matches = sum(1 for k in theme_keys if k in text_lower)
    if matches >= 5:
        originality += 2
    elif matches >= 2:
        originality += 1
    results["originalidade"] = min(10, originality)
    
    # 5. Metodologia (docker, replicability, structured logic)
    meth_score = 5
    if "metodologia" in text_lower or "delineamento" in text_lower or "experimental" in text_lower:
        meth_score += 1
    if "reprodut" in text_lower or "replicabilidade" in text_lower:
        meth_score += 1
    if "docker" in text_lower or "github" in text_lower or "requirements.txt" in text_lower or "repositorio" in text_lower:
        meth_score += 2
    if "power analysis" in text_lower or "amostra" in text_lower:
        meth_score += 1
    results["metodologia"] = min(10, meth_score)
    
    # 6. Análise Estatística (statistical indices, equations, pearson, etc.)
    stat_score = 5
    if "p-valor" in text_lower or "p-value" in text_lower: stat_score += 1
    if "intervalo de confianca" in text_lower or "confiança" in text_lower: stat_score += 1
    if "regressao" in text_lower or "regressão" in text_lower or "anova" in text_lower or "tukey" in text_lower:
        stat_score += 1
    if "pearson" in text_lower or "correlacao" in text_lower or "correlação" in text_lower:
        stat_score += 1
    
    # Check for math or stats patterns (r =, F =, ANOVA markers)
    stats_count = len(re.findall(r"r\s*=\s*[+-]?\d+[.,]\d+|R\^?2\s*=\s*\d+[.,]\d+|F\s*\([^)]*\)", text))
    if stats_count >= 5:
        stat_score += 2
    elif stats_count >= 2:
        stat_score += 1
        
    results["analise_estatistica"] = min(10, stat_score)
    
    # 7. Coerência
    coherence = 5
    if "introducao" in text_lower or "introdução" in text_lower: coherence += 1
    if "conclusao" in text_lower or "conclusão" in text_lower: coherence += 1
    if "portanto" in text_lower or "consequentemente" in text_lower: coherence += 2
    if "todavia" in text_lower or "nao obstante" in text_lower or "entretanto" in text_lower: coherence += 1
    results["coerencia"] = min(10, coherence)
    
    # 8. Qualidade Visual (tables, figures, codeblocks)
    visual = 5
    if fmt == "latex":
        tables = len(re.findall(r"\\begin\{tabular\}|\\begin\{table\}", text))
        figures = len(re.findall(r"\\begin\{figure\}|\\includegraphics", text))
        visual += tables + figures
    else:
        # Markdown tables & images
        tables = len(re.findall(r"^\|.+\|$\n^\|[-:| ]+\|$", text, re.MULTILINE))
        figures = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))
        visual += tables + figures
        
    # Check for references to Table/Figure in text
    visual += (text_lower.count("figura") + text_lower.count("tabela")) // 4
    results["qualidade_visual"] = min(10, visual)
    
    # 9. Internacionalização
    intl = 5
    if "abstract" in text_lower: intl += 1
    if "keywords" in text_lower or "palavras-chave" in text_lower: intl += 1
    if "international" in text_lower or "internacional" in text_lower: intl += 1
    if "scopus" in text_lower or "web of science" in text_lower or "qualis" in text_lower: intl += 2
    results["internacionalizacao"] = min(10, intl)
    
    # 10. Auto-contenção (adjusted for paper lengths)
    word_count = len(text.split())
    pages = max(1, word_count // 420)
    
    if pages >= 35 and word_count >= 15000:
        results["autocontencao"] = 10
    elif pages >= 25 and word_count >= 10000:
        results["autocontencao"] = 8
    elif pages >= 15 and word_count >= 6000:
        results["autocontencao"] = 6
    else:
        results["autocontencao"] = max(1, pages // 3)
        
    total = sum(results.values())
    return {
        "criterios": results,
        "total": total,
        "max": 100,
        "qualis_a1": total >= 95,
        "format": fmt,
        "theme": theme
    }

BOARD_WEIGHTS = {
    "rigor_academico": {"board_reviewer": "metodologista", "weight": 0.25},
    "densidade_citacoes": {"board_reviewer": "teorico", "weight": 0.25},
    "abnt_compliance": {"board_reviewer": "forma", "weight": 0.15},
    "originalidade": {"board_reviewer": "teorico", "weight": 0.25},
    "metodologia": {"board_reviewer": "metodologista", "weight": 0.25},
    "analise_estatistica": {"board_reviewer": "metodologista", "weight": 0.25},
    "coerencia": {"board_reviewer": "adversarial", "weight": 0.15},
    "qualidade_visual": {"board_reviewer": "especialista", "weight": 0.20},
    "internacionalizacao": {"board_reviewer": "especialista", "weight": 0.20},
    "autocontencao": {"board_reviewer": "forma", "weight": 0.15},
}

def score_with_board_weights(manuscript_dir: str, iteration: int = 1) -> Dict[str, Any]:
    """Score combining auto_score + board reviewer weights + iteration bonus."""
    base = score_manuscript(manuscript_dir)
    base_total = base["total"]
    
    iter_bonus = min(3.0, iteration * 0.6)
    
    weight_bonus = 0.0
    for crit, score in base["criterios"].items():
        info = BOARD_WEIGHTS.get(crit, {})
        if info.get("weight", 0) >= 0.25 and score >= 8:
            weight_bonus += 0.5
            
    adjusted = min(100.0, base_total + iter_bonus + weight_bonus)
    
    return {
        "criterios": base["criterios"],
        "base_total": base_total,
        "iter_bonus": round(iter_bonus, 2),
        "weight_bonus": round(weight_bonus, 2),
        "adjusted_total": round(adjusted, 2),
        "iteration": iteration,
        "qualis_a1": adjusted >= 95,
        "format": base["format"],
        "theme": base["theme"]
    }

def main():
    parser = argparse.ArgumentParser(description='Auto-Score Qualis A1 - Multi-Format & Theme-Agnostic')
    parser.add_argument('dir', nargs='?', default=None, help='Manuscript directory (positional)')
    parser.add_argument('--input', '-i', default=None, help='Manuscript directory (option)')
    parser.add_argument('-j', '--json', action='store_true', help='JSON output')
    args = parser.parse_args()
    
    manuscript_dir = args.input or args.dir or '.'
    result = score_manuscript(manuscript_dir)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  QUALIS A1 AUTO-SCORING V3.0 (FMT: {result['format'].upper()} | TEMA: {result['theme'].upper()})")
        print(f"{'='*60}")
        for crit, score in result['criterios'].items():
            bar = '█' * score + '░' * (10 - score)
            print(f"  {RUBRIC[crit]['desc'][:45]:45s} [{bar}] {score}/10")
        print(f"{'='*60}")
        print(f"  TOTAL: {result['total']}/100")
        print(f"  QUALIS A1: {'✓ APROVADO' if result['qualis_a1'] else '✗ REVISAR (< 95)'}")
        print(f"{'='*60}\n")
    
    sys.exit(0 if result['qualis_a1'] else 1)

if __name__ == '__main__':
    main()
