# -*- coding: utf-8 -*-
"""
Demo — Subsistema Research (SPEC-017)
======================================
Fluxo completo: busca multiplataforma → download de PDFs → PDF→Markdown →
fichamentos + resenhas críticas ABNT/APA → referências consolidadas,
tudo em uma pasta única de produção científica, via orquestrador marceloclaro.

Uso:
    python3 examples/demo_research.py "tema de pesquisa"
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.basicConfig(level=logging.INFO,
                    format="%(levelname)s %(name)s: %(message)s")

from marceloclaro.orchestrator import MarceloClaroOrchestrator


def main():
    tema = (sys.argv[1] if len(sys.argv) > 1
            else "metacognition in multi-agent LLM systems")

    print("=" * 70)
    print("DEMO RESEARCH — Busca e Extração Acadêmica (SPEC-017)")
    print(f"Tema: {tema}")
    print("=" * 70)

    orch = MarceloClaroOrchestrator(auto_load_agents=True)

    # 1) Busca rápida federada (sem download) — ranking por aderência
    print("\n[1] Busca federada (arXiv + OpenAlex + GitHub)...")
    hits = orch.research_search(tema, platforms=["arxiv", "openalex", "github"],
                                limit_per_platform=3)
    for h in hits[:5]:
        tipo = h["extra"].get("type", "paper")
        print(f"  - [{tipo}] {h['title'][:70]} ({h['year']}) — {h['source']}")

    # 2) Pipeline completo em pasta única
    print("\n[2] Pipeline completo (download + PDF→MD + fichamentos + resenhas)...")
    manifest = orch.research(tema, max_papers=3,
                             platforms=["arxiv", "openalex", "github"])
    print(json.dumps(manifest["resumo"], indent=2, ensure_ascii=False))
    print(f"\nPasta única: {manifest['folder']}")

    # 3) Estrutura gerada
    print("\n[3] Artefatos da subpasta pesquisa/:")
    pesquisa = Path(manifest["folder"]) / "pesquisa"
    for p in sorted(pesquisa.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(pesquisa)}")

    # 4) Metacognição registrada
    print("\n[4] Última reflexão metacognitiva do orquestrador:")
    ctx = orch.perceive("pesquisa")
    if ctx["recent_context"]:
        print(f"  {ctx['recent_context'][-1]}")

    print("\nDemo concluída com sucesso.")


if __name__ == "__main__":
    main()
