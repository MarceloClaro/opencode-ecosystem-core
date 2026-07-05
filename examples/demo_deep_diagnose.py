# -*- coding: utf-8 -*-
"""Demo — Diagnóstico Profundo (SPEC-020).

Executa o DiagnosticPipeline em modo deep, exercitando:
- Roadmap Evolutivo completo (M1–M5 + Composição Unitária + Sequenciamento)
- Priorização Epistemológica (erro → ausência → oportunidade)
- Gerador de Sucessores Plausíveis (DNA estrutural → capacidades emergentes)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scanners.pipeline import DiagnosticPipeline  # noqa: E402


def main() -> None:
    p = DiagnosticPipeline()
    corpus = (
        "Este manuscrito investiga metacognição em sistemas multiagentes com "
        "arquitetura transformer, atenção multi-cabeça, memória hierárquica, "
        "teoria dos jogos e economia de tokens. Faltam análises estatísticas "
        "e validação empírica com dados reais. TODO: adicionar experimentos."
    )
    goals = [
        {"name": "publicar_qualis",
         "description": "Publicar artigo Qualis A1 sobre metacognição multiagente",
         "weight": 2.0, "goal_type": "strategic"},
        {"name": "validar",
         "description": "Validar empiricamente o roteamento por atenção",
         "weight": 1.5, "goal_type": "evaluative"},
    ]
    r = p.run(corpus, domain="multiagent_systems", goals=goals, deep=True)

    print("chaves do relatório:", sorted(r.keys()))

    rm = r.get("roadmap", {})
    print("\n== ROADMAP EVOLUTIVO ==")
    if "error" in rm:
        print("  ERRO:", rm["error"])
    else:
        print(f"  cobertura noológica : {rm.get('noological_coverage')}")
        print(f"  score teleológico   : {rm.get('teleological_score')}")
        print(f"  gaps totais         : {rm.get('total_gaps')} "
              f"(quick_wins={rm.get('quick_wins')}, "
              f"foundations={rm.get('foundations')}, "
              f"frontiers={rm.get('frontiers')})")
        print(f"  custo de construção : {rm.get('total_construction_cost')}")
        print(f"  sequência lógica    : {rm.get('logical_sequence', [])[:6]}")

    eo = r.get("epistemic_opportunities", {})
    print("\n== PRIORIZAÇÃO EPISTEMOLÓGICA ==")
    print(f"  oportunidades: {eo.get('total')} "
          f"(breakthroughs={eo.get('breakthroughs')})")
    for o in (eo.get("top") or [])[:5]:
        print(f"  - {o['dimension']:<28} {o['tier']:<13} "
              f"score={o['opportunity_score']:.3f}")

    su = r.get("successors", {})
    print("\n== SUCESSORES PLAUSÍVEIS ==")
    print(f"  hipóteses: {su.get('total')} (imediatos={su.get('immediate')})")
    for s in (su.get("top") or [])[:5]:
        print(f"  - {s['name']:<45} {s['tier']:<18} "
              f"score={s['successor_score']:.3f}")

    assert "roadmap" in r and "error" not in r.get("roadmap", {}), \
        "roadmap falhou"
    assert eo.get("total", 0) > 0, "priorização vazia"
    assert su.get("total", 0) > 0, "sucessores vazios"
    print("\nDemo deep diagnose: OK")


if __name__ == "__main__":
    main()
