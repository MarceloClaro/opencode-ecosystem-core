# -*- coding: utf-8 -*-
"""
Demo end-to-end do OpenCode Ecosystem Core
==========================================
Fluxo completo: carga de agentes → percepção metacognitiva → delegação via
Blackboard → voluntariado → conclusão → reflexão → memória atualizada.

Execução:
    python3 examples/demo_pipeline.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marceloclaro.orchestrator import MarceloClaroOrchestrator


def main():
    print("=" * 60)
    print("DEMO — OpenCode Ecosystem Core / Orquestrador marceloclaro")
    print("=" * 60)

    # 1. Inicializa o orquestrador (carrega os 5 agentes de agents/*.md)
    orchestrator = MarceloClaroOrchestrator()
    print(f"\n[1] Agentes registrados: {len(orchestrator.list_agents())}")
    for card in orchestrator.list_agents():
        print(f"    - {card['name']} ({card['agent_id']}): {card['capabilities']} "
              f"| confiança={card['confidence_score']:.2f}")

    # 2. Percepção metacognitiva pré-delegação
    awareness = orchestrator.perceive()
    print(f"\n[2] Percepção metacognitiva: {len(awareness['recent_context'])} eventos recentes, "
          f"{len(awareness['lessons'])} lições aprendidas")

    # 3. Delegação de tarefas via Blackboard
    t1 = orchestrator.delegate(
        "Levantar literatura sobre protocolos A2A e blackboard multi-agente",
        required_capabilities=["search"],
    )
    t2 = orchestrator.delegate(
        "Implementar módulo de parsing YAML sem dependências externas",
        required_capabilities=["python"],
    )
    print(f"\n[3] Tarefas delegadas: {t1}, {t2}")

    # 4. Simula execução e conclusão pelos agentes escolhidos
    status = orchestrator.status()
    assignments = {tid: s for tid, s in status["tasks"].items()}
    print(f"\n[4] Estado das tarefas após CFP/voluntariado: {assignments}")

    orchestrator.report_completion(t1, "researcher", "3 papers encontrados e sintetizados", success=True)
    orchestrator.report_completion(t2, "coder", "Módulo implementado com 100% de cobertura", success=True)

    # 5. Estado final: reflexões geradas e confiança atualizada
    final = orchestrator.status()
    print("\n[5] Estado final do ecossistema:")
    print(json.dumps(final, indent=2, ensure_ascii=False))

    print("\nDemo concluída: a metacognição circulou por todos os agentes via MCI.")


if __name__ == "__main__":
    main()
