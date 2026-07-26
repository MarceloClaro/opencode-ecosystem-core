#!/usr/bin/env python3
"""
LLM Reduction — Fachada Unificada de Redução de Dependência de LLM
====================================================================
Integra os 5 componentes de substituição de LLM em uma única interface
para o orquestrador MarceloClaro.

Componentes:
1. Whoosh3Engine — busca full-text local (substitui busca semântica LLM)
2. RuleBasedRouter — roteamento determinístico (substitui AttentionRouter)
3. LocalClassifier — classificação de texto local (substitui Ollama/OpenAI)
4. GameTheoryLocal — teoria dos jogos local (substitui debate_strategies)
5. Jinja2Engine — geração de documentos (substitui LLM para textos/reports)

Uso:
    from skills.tooling.llm_reduction import get_reduction_layer
    layer = get_reduction_layer()
    agent = layer.route("preciso buscar biblioteca python")
    results = layer.search("trust engine")
    report = layer.render_template("fichamento.md.j2", data)
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from skills.tooling.whoosh3_engine import Whoosh3Engine
from skills.tooling.rule_based_router import RuleBasedRouter
from skills.tooling.local_classifier import LocalClassifier
from skills.tooling.game_theory_local import GameTheoryLocal
from skills.tooling.jinja2_templates import Jinja2Engine
from skills.tooling.data_knowledge_hub import DataKnowledgeHub


class LLMReductionLayer:
    """
    Camada de redução de LLM: unifica os 6 substitutos em uma fachada.

    Cada chamada a esta camada evita uma chamada de LLM.
    """

    def __init__(self):
        self.whoosh = Whoosh3Engine("opencode_memoria")
        self.router = RuleBasedRouter()
        self.classifier = LocalClassifier()
        self.gametheory = GameTheoryLocal()
        self.jinja2 = Jinja2Engine()
        self.data_hub = DataKnowledgeHub()
        self._initialized = False
        self.stats = {
            "total_llm_calls_saved": 0,
            "search_calls": 0,
            "route_calls": 0,
            "classify_calls": 0,
            "gametheory_calls": 0,
            "template_calls": 0,
            "data_queries": 0,
        }

    # ─── Indexação (Whoosh3) ─────────────────────────────────

    def index_document(self, doc: Dict[str, Any]) -> bool:
        """Indexa um documento para busca local (evita LLM)."""
        return self.whoosh.index(doc)

    def index_batch(self, docs: List[Dict[str, Any]]) -> int:
        """Indexa lote de documentos."""
        return self.whoosh.index_batch(docs)

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca full-text local (0 LLM calls).
        Substitui busca semântica via LLM.
        """
        self.stats["search_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.whoosh.search(query, limit=limit)

    # ─── Roteamento (RuleBasedRouter) ─────────────────────────

    def route(self, task_description: str) -> Dict[str, Any]:
        """
        Roteia tarefa para agente (0 LLM calls).
        Substitui AttentionRouter + blackboard A2A via LLM.
        """
        self.stats["route_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.router.route(task_description)

    def route_batch(
        self, tasks: List[str]
    ) -> List[Dict[str, Any]]:
        """Roteia múltiplas tarefas."""
        results = [self.route(t) for t in tasks]
        return results

    # ─── Classificação (LocalClassifier) ──────────────────────

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifica texto localmente (0 LLM calls).
        Substitui classificação via Ollama/OpenAI.
        """
        self.stats["classify_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.classifier.predict(text)

    def classify_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        return [self.classify(t) for t in texts]

    # ─── Game Theory (GameTheoryLocal) ────────────────────────

    def nash_equilibrium(
        self, A: List[List[float]], B: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """Equilíbrio de Nash (0 LLM calls). Substitui debate_strategies."""
        self.stats["gametheory_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.gametheory.nash_equilibrium(A, B)

    def shapley_value(
        self, coalitions: Dict[str, float], players: List[str]
    ) -> Dict[str, Any]:
        """Valor de Shapley (0 LLM calls)."""
        self.stats["gametheory_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.gametheory.shapley_value(coalitions, players)

    def pareto_frontier(
        self, payoffs: List[tuple]
    ) -> Dict[str, Any]:
        """Fronteira de Pareto (0 LLM calls)."""
        self.stats["gametheory_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.gametheory.pareto_frontier(payoffs)

    # ─── Jinja2 Templates (Jinja2Engine) ──────────────────────

    def render_template(
        self, template_name: str, data: Dict[str, Any]
    ) -> str:
        """
        Renderiza template Jinja2 (0 LLM calls).
        Substitui geração de documentos/relatórios via LLM.
        """
        self.stats["template_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.jinja2.render(template_name, data)

    def render_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """
        Renderiza string de template Jinja2 (0 LLM calls).
        Substitui f-strings/LLM para texto dinâmico.
        """
        self.stats["template_calls"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.jinja2.render_string(template_string, data)

    def list_templates(self) -> List[str]:
        """Lista templates disponíveis."""
        return self.jinja2.list_templates()

    # ─── Data/Knowledge Hub (DataKnowledgeHub) ─────────────────

    def search_data(
        self, query: str, domain: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Busca dados em qualquer domínio (0 LLM calls).
        Substitui pesquisa manual via navegador/LLM para dados estruturados.
        """
        self.stats["data_queries"] += 1
        self.stats["total_llm_calls_saved"] += 1
        return self.data_hub.search(query, domain=domain, **kwargs)

    def search_finance(self, query: str, **kwargs) -> Dict[str, Any]:
        """Atalho para busca financeira."""
        return self.search_data(query, domain="financeiro", **kwargs)

    def search_knowledge(self, query: str, **kwargs) -> Dict[str, Any]:
        """Atalho para busca de conhecimento."""
        return self.search_data(query, domain="conhecimento", **kwargs)

    def search_dataset(self, query: str, **kwargs) -> Dict[str, Any]:
        """Atalho para busca de datasets."""
        return self.search_data(query, domain="dataset", **kwargs)

    def search_official(self, query: str, **kwargs) -> Dict[str, Any]:
        """Atalho para busca de dados oficiais."""
        return self.search_data(query, domain="oficial", **kwargs)

    # ─── Status ──────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "whoosh_stats": self.whoosh.stats(),
            "router_stats": self.router.get_stats(),
            "classifier_stats": self.classifier.get_stats(),
            "gametheory_stats": self.gametheory.stats,
            "jinja2_stats": self.jinja2.get_stats(),
            "data_hub_stats": self.data_hub.get_stats(),
        }

    def get_report(self) -> str:
        """Relatório legível do impacto."""
        s = self.stats
        return (
            f"LLM Reduction Layer\n"
            f"{'='*50}\n"
            f"Total de chamadas LLM evitadas: {s['total_llm_calls_saved']}\n"
            f"  - Buscas (Whoosh3): {s['search_calls']}\n"
            f"  - Roteamentos (RuleBasedRouter): {s['route_calls']}\n"
            f"  - Classificações (LocalClassifier): {s['classify_calls']}\n"
            f"  - Teoria dos Jogos (GameTheoryLocal): {s['gametheory_calls']}\n"
            f"  - Templates (Jinja2Engine): {s['template_calls']}\n"
            f"  - Data/Knowledge (DataKnowledgeHub): {s['data_queries']}\n"
        )


# Singleton
_layer: Optional[LLMReductionLayer] = None


def get_reduction_layer() -> LLMReductionLayer:
    global _layer
    if _layer is None:
        _layer = LLMReductionLayer()
    return _layer


# ─── Teste Integrado ─────────────────────────────────────────

if __name__ == "__main__":
    layer = get_reduction_layer()

    print("=== LLM Reduction Layer - Teste Integrado ===")
    print()

    # 1. Indexar documentos
    docs = [
        {"id": "1", "title": "Spec Trust Engine",
         "content": "Cognitive guardrails and goal drift prevention",
         "tags": ["trust"], "source": "specs"},
        {"id": "2", "title": "Spec Token Economy",
         "content": "Staking slashing and fee market",
         "tags": ["economy"], "source": "specs"},
    ]
    n = layer.index_batch(docs)
    print(f"1. Indexados {n} documentos (0 LLM)")

    # 2. Buscar
    results = layer.search("trust guardrails")
    print(f"2. Busca 'trust guardrails': {len(results)} resultados (0 LLM)")

    # 3. Roteamento
    tasks = [
        "preciso baixar um paper do scihub",
        "implementar função de validação",
        "revisar o código do módulo",
    ]
    print(f"\n3. Roteamento de {len(tasks)} tarefas (0 LLM):")
    for task in tasks:
        r = layer.route(task)
        print(f'   "{task[:40]:40s}" → {r["agent"]:20s} ({r["method"]})')

    # 4. Classificação
    texts = [
        "qual a melhor biblioteca para PDF em Python?",
        "fazer deploy em produção",
    ]
    print(f"\n4. Classificação de {len(texts)} textos (0 LLM):")
    for t in texts:
        r = layer.classify(t)
        print(f'   "{t[:40]:40s}" → {r["label"]:20s} ({r["method"]})')

    # 5. Game Theory
    print("\n5. Game Theory (0 LLM):")
    A = [[-1, -3], [0, -2]]
    B = [[-1, 0], [-3, -2]]
    nash_r = layer.nash_equilibrium(A, B)
    print(f'   Nash equilibria: {nash_r.get("num_equilibria", 0)}')

    print(f"\n{layer.get_report()}")
