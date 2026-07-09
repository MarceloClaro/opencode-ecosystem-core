#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Score Qualis A1 v2.0 — Refatorado com DI
================================================
Avaliacao automatizada de manuscritos contra rubrica Qualis A1.
Injecao de Dependencia via state_manager (opcional, fallback = Container).
"""

from __future__ import annotations
import json
import os
import sys
import re as _re
import argparse
from pathlib import Path
from typing import Optional

try:
    from core.interfaces import IStateManager, IEventBus
except ImportError:
    import sys as _sys
    _recon = Path(__file__).resolve().parent.parent / "reconstruction"
    if _recon.exists():
        _sys.path.insert(0, str(_recon))
    from core_interfaces import IStateManager, IEventBus

try:
    from core.container import Container
except ImportError:
    class Container:
        _instance = None
        @classmethod
        def instance(cls):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
        def __init__(self):
            self._services = {}
        def register(self, name, instance):
            self._services[name] = instance
        def resolve(self, name):
            return self._services.get(name)

RUBRIC = {
    "rigor_academico": {"peso": 10, "desc": "Rigor academico e profundidade teorica"},
    "densidade_citacoes": {"peso": 10, "desc": "Densidade de citacoes (>=55 referencias com DOI)"},
    "abnt_compliance": {"peso": 10, "desc": "Conformidade ABNT NBR 6023/6028"},
    "originalidade": {"peso": 10, "desc": "Originalidade e relevancia da contribuicao"},
    "metodologia": {"peso": 10, "desc": "Metodologia reprodutivel e documentada"},
    "analise_estatistica": {"peso": 10, "desc": "Analise estatistica rigorosa e validada"},
    "coerencia": {"peso": 10, "desc": "Coerencia argumentativa (intro <-> conclusao)"},
    "qualidade_visual": {"peso": 10, "desc": "Qualidade de graficos, tabelas e figuras"},
    "internacionalizacao": {"peso": 10, "desc": "Abstract em ingles + conformidade internacional"},
    "autocontencao": {"peso": 10, "desc": "Auto-containment (>=110 paginas, >=48k palavras)"},
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


def score_manuscript(manuscript_dir: str, state_manager: Optional[IStateManager] = None) -> dict:
    """Score a manuscript against Qualis A1 rubric com DI."""
    sm = state_manager or Container.instance().resolve("state_manager")
    results = {}
    total = 0

    ref_count = 0
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        ref_count += content.count("[^")
        ref_count += content.count("doi.org")
        ref_count += content.count("Disponivel em:")
    refs_dir = Path(manuscript_dir) / "referencias"
    if refs_dir.exists():
        for f in refs_dir.glob("*.md"):
            content = open(f, encoding='utf-8', errors='ignore').read()
            ref_count += content.count("DOI:") + content.count("doi:")
    results["rigor_academico"] = min(10, max(5, ref_count // 10))

    doi_count = 0
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        doi_count += content.count("10.") + content.count("doi.org")
    results["densidade_citacoes"] = 10 if doi_count >= 55 else min(9, doi_count // 6)

    abnt_score = 5
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        if "ABNT" in content: abnt_score += 1
        if "NBR 6023" in content or "NBR 6028" in content: abnt_score += 1
        if "SOBRENOME" in content: abnt_score += 1
        if "et al." in content: abnt_score += 1
        if content.count("p.") > 5: abnt_score += 1
    results["abnt_compliance"] = min(10, abnt_score)

    originality = 5
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        if "contribuicao" in content.lower() or "contribuição" in content.lower(): originality += 1
        if "inedito" in content.lower() or "inédito" in content.lower(): originality += 1
        if "lacuna" in content.lower(): originality += 1
        if "estado da arte" in content.lower(): originality += 1
        if "gap" in content.lower(): originality += 1
    results["originalidade"] = min(10, originality)

    meth_score = 5
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        if "metodologia" in content.lower(): meth_score += 1
        if "reprodut" in content.lower(): meth_score += 1
        if "docker" in content.lower() or "requirements.txt" in content.lower(): meth_score += 2
        if "codebook" in content.lower(): meth_score += 1
    results["metodologia"] = min(10, meth_score)

    stat_score = 5
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        if "p-valor" in content.lower() or "p-value" in content.lower(): stat_score += 1
        if "intervalo de confianca" in content.lower(): stat_score += 1
        if "regressao" in content.lower() or "correlacao" in content.lower(): stat_score += 1
        if "pearson" in content.lower(): stat_score += 1
        if "r =" in content or "r=" in content: stat_score += 1
        if "cross-nacional" in content.lower() or "transversal" in content.lower(): stat_score += 1
    results["analise_estatistica"] = min(10, stat_score)

    coherence = 5
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        if "introducao" in content.lower() or "introdução" in content.lower(): coherence += 1
        if "conclusao" in content.lower() or "conclusão" in content.lower(): coherence += 1
        if "portanto" in content.lower(): coherence += 1
        if "logo" in content.lower(): coherence += 1
        if "consequentemente" in content.lower(): coherence += 1
    results["coerencia"] = min(10, coherence)

    visual = 5
    for img in Path(manuscript_dir).rglob("*"):
        if img.suffix in ('.png', '.jpg', '.svg', '.pdf', '.eps'):
            visual += 1
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        visual += content.count("![]") + content.lower().count("figura") + content.lower().count("tabela")
        visual += len(_re.findall(r"^\|.+\|$\n^\|[-:| ]+\|$", content, _re.MULTILINE))
    results["qualidade_visual"] = min(10, visual)

    intl = 5
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        if "abstract" in content.lower(): intl += 1
        if "keywords" in content.lower(): intl += 1
        if "international" in content.lower(): intl += 1
        if "scopus" in content.lower() or "web of science" in content.lower(): intl += 1
        if "nature" in content.lower() or "science" in content.lower(): intl += 1
    results["internacionalizacao"] = min(10, intl)

    pages = 0
    word_count = 0
    for md_file in Path(manuscript_dir).rglob("*.md"):
        content = open(md_file, encoding='utf-8', errors='ignore').read()
        word_count += len(content.split())
        pages += max(1, len(content.split()) // 420)

    if pages >= 35 and word_count >= 15000:
        results["autocontencao"] = 10
    elif pages >= 25 and word_count >= 10000:
        results["autocontencao"] = 8
    elif pages >= 15 and word_count >= 6000:
        results["autocontencao"] = 6
    else:
        results["autocontencao"] = max(1, pages // 5)

    total = sum(results.values())
    return {"criterios": results, "total": total, "max": 100, "qualis_a1": total >= 95}


def score_with_board_weights(manuscript_dir: str, iteration: int = 1,
                             state_manager: Optional[IStateManager] = None) -> dict:
    """Score combinando auto_score + board reviewer weights + iteration bonus."""
    sm = state_manager or Container.instance().resolve("state_manager")
    base = score_manuscript(manuscript_dir, sm)
    base_total = base["total"]
    iter_bonus = min(3, iteration * 0.6)
    weight_bonus = 0
    for crit, score in base["criterios"].items():
        info = BOARD_WEIGHTS.get(crit, {})
        if info.get("weight", 0) >= 0.25 and score >= 8:
            weight_bonus += 0.5
    adjusted = min(100, base_total + iter_bonus + weight_bonus)
    return {
        "criterios": base["criterios"],
        "base_total": base_total,
        "iter_bonus": round(iter_bonus, 2),
        "weight_bonus": round(weight_bonus, 2),
        "adjusted_total": round(adjusted, 2),
        "iteration": iteration,
        "qualis_a1": adjusted >= 95,
    }


def main():
    parser = argparse.ArgumentParser(description='Auto-Score Qualis A1 v2.0 - Refatorado DI')
    parser.add_argument('dir', nargs='?', default=None, help='Manuscript directory (positional)')
    parser.add_argument('--input', '-i', default=None, help='Manuscript directory (option)')
    parser.add_argument('-j', '--json', action='store_true', help='JSON output')
    parser.add_argument('--iteration', type=int, default=1, help='Iteration number')
    parser.add_argument('--board-weights', action='store_true', help='Usar board weights')
    args = parser.parse_args()

    manuscript_dir = args.input or args.dir or '.'
    if args.board_weights:
        result = score_with_board_weights(manuscript_dir, args.iteration)
    else:
        result = score_manuscript(manuscript_dir)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  QUALIS A1 AUTO-SCORING v2.0")
        print(f"{'='*60}")
        for crit, score in result['criterios'].items():
            desc = RUBRIC.get(crit, {}).get('desc', crit)[:45]
            bar = '█' * score + '░' * (10 - score)
            print(f"  {desc:45s} [{bar}] {score}/10")
        print(f"{'='*60}")
        print(f"  TOTAL: {result.get('adjusted_total', result['total'])}/100")
        total = result.get('adjusted_total', result['total'])
        print(f"  QUALIS A1: {'✓ APROVADO' if total >= 95 else '✗ < 95'}")
        print(f"{'='*60}\n")

    sys.exit(0 if (result.get('adjusted_total', result['total']) >= 95) else 1)


if __name__ == '__main__':
    main()
