#!/usr/bin/env python3
"""
RuleBasedRouter — Roteador Determinístico de Tarefas
=====================================================
Substituto do AttentionRouter (LLM) para classificação e roteamento
de tarefas no ecossistema OpenCode.

Usa DecisionTreeClassifier do sklearn + regras explícitas para decidir
qual agente ou pipeline deve receber uma tarefa, sem chamar LLM.

Uso:
    router = RuleBasedRouter()
    agent = router.route("preciso buscar uma biblioteca python")
    # → "pypi-searcher"
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier

# Banco de regras: padrão textual → agente alvo
# (ordem importa: primeiro match vence para regras)
TEXT_RULES: List[Tuple[str, str, float]] = [
    # Tarefas de código
    (r"(implement|refactor|refatorar|criar fun)[a-zçãõéê]*", "coder", 0.95),
    (r"(debug|bug|erro|crash|falha|exception)", "debugger", 0.95),
    (r"(test|pytest|tdd|teste unit)", "test-engineer", 0.95),
    (r"(revis[ãa]o|revisar|code review|quality|pr review)", "reviewer", 0.95),

    # Busca de bibliotecas
    (r"(biblioteca|lib|pypi|pacote python|pip install)", "pypi-searcher", 0.95),
    (r"(sci[- ]?hub|paper|artigo acad|download pdf)", "pypi-searcher", 0.90),

    # Pesquisa acadêmica
    (r"(pesquis[ai]|artigo cient|academic|qualis|doi|publica[çc][ãa]o)", "researcher", 0.90),
    (r"(m aswos|pipeline acad|latex|abnt)", "ws-academic-pipeline", 0.90),

    # Documentação
    (r"(documenta[çc][ãa]o|doc|wiki|readme|manual)", "docs-writer", 0.90),
    (r"(arquitetura|architectur|design system|ddd|bounded context)", "architect", 0.90),

    # Análise de código
    (r"(analis[ae] c[óo]dig|mapping|codebase|explorar|locat)", "codebase-analyzer", 0.90),
    (r"(seguran[çc]a|vulnerabilidad|auditoria)", "security-auditor", 0.90),

    # DevOps
    (r"(deploy|ci/cd|docker|kubernetes|infra|container|compose)", "devops-specialist", 0.90),

    # Dados
    (r"(dado|dataset|sql|banco|etl|pipeline dado)", "cloud-data-pipelines-specialist", 0.85),

    # Orquestração
    (r"(orquestra[çc][ãa]o|multi.*agente|pipeline|workflow)", "stage-orchestrator", 0.85),
    (r"(evolu[çc][ãa]o|evolutivo|autoevolve|discover)", "autoevolve", 0.85),

    # Acadêmico / Escrita
    (r"(escrev|reda[çc][ãa]o|artigo|monografia|tese|disserta[çc][ãa]o)", "academic_writer", 0.85),
    (r"(livro|cap[tí]tulo|manuscrito|manuscript)", "nano-orchestrator", 0.85),

    # Jurídico
    (r"(jur[dí]dic|lei|norma|advocaci|peti[çc][ãa]o|contrato)", "auxjuris_legal_assistant", 0.90),
    (r"(datajud|jurisprud)", "reversa", 0.85),

    # Medical
    (r"(m[eé]dic[ao]|cardiolog|neurolog|cl[í]nic[ao]|sintoma|paciente)", "medico-virtual-supremo", 0.90),

    # Apresentação
    (r"(apresenta[çc][ãa]o|slide|mira|deck|visual)", "mira-builder", 0.85),
    (r"(imagem|image|figura|gr[áa]fic|chart|infogr)", "mira-chart", 0.85),

    # Geral
    (r"(ajuda|help|manual|comand|como usar)", "context-manager", 0.80),
    (r"(diagn[óo]stic[oai]|doctor|sa[úu]de do ecossistema|health.check)", "auditor", 0.90),
]

# Banco de treino para o DecisionTree (além das regras)
TRAIN_DATA: List[Tuple[str, str]] = [
    # (texto, agente)
    ("implementar função de busca", "coder"),
    ("refatorar módulo de pagamento", "coder"),
    ("criar endpoint REST", "coder"),
    ("testar unidade de cálculo", "test-engineer"),
    ("rodar pytest no módulo x", "test-engineer"),
    ("revisar código do PR", "reviewer"),
    ("code review do módulo y", "reviewer"),
    ("buscar biblioteca para PDF", "pypi-searcher"),
    ("encontrar pacote para HTTP async", "pypi-searcher"),
    ("qual a melhor lib para scraping", "pypi-searcher"),
    ("scihub para baixar paper", "pypi-searcher"),
    ("pesquisar artigo sobre machine learning", "researcher"),
    ("fazer pesquisa acadêmica", "researcher"),
    ("escrever artigo Qualis A1", "academic_writer"),
    ("documentar API", "docs-writer"),
    ("criar documentação técnica", "docs-writer"),
    ("analisar arquitetura", "architect"),
    ("projetar bounded context", "architect"),
    ("mapear codebase", "codebase-analyzer"),
    ("explorar estrutura do projeto", "codebase-analyzer"),
    ("auditar segurança", "security-auditor"),
    ("configurar deploy", "devops-specialist"),
    ("subir container docker", "devops-specialist"),
    ("criar pipeline de dados", "cloud-data-pipelines-specialist"),
    ("orquestrar multi-agente", "stage-orchestrator"),
    ("disparar evolução", "autoevolve"),
    ("escrever livro técnico", "nano-orchestrator"),
    ("criar apresentação", "mira-builder"),
    ("fazer slide deck", "mira-builder"),
    ("gerar gráfico", "mira-chart"),
    ("analisar contrato", "auxjuris_legal_assistant"),
    ("petição jurídica", "auxjuris_legal_assistant"),
    ("diagnóstico ecossistema", "auditor"),
    ("status do sistema", "auditor"),
    ("ajuda com comando", "context-manager"),
    ("deploy em produção", "devops-specialist"),
    ("subir container", "devops-specialist"),
    ("revisar PR", "reviewer"),
    ("revisão de código", "reviewer"),
    ("diagnóstico ecossistema", "auditor"),
    ("diagnosticar problema", "auditor"),
    ("médico cardiologista", "medico-virtual-supremo"),
    ("neurodivergente diagnóstico", "medico-virtual-supremo"),
    ("sintoma cardíaco", "medico-virtual-supremo"),
]


class RuleBasedRouter:
    """
    Roteador determinístico que combina:
    1. Regras textuais (regex) — alta precisão
    2. DecisionTreeClassifier (sklearn) — fallback para casos não cobertos
    3. Agente padrão — fallback final
    """

    def __init__(self, model_path: Optional[str] = None):
        self.text_rules = TEXT_RULES
        self._train()
        self.stats = {
            "total_routes": 0,
            "rule_matches": 0,
            "tree_matches": 0,
            "fallback": 0,
            "avg_ms": 0.0,
        }

    def _train(self):
        """Treina DecisionTreeClassifier com dados de exemplo."""
        texts = [t for t, _ in TRAIN_DATA]
        labels = [l for _, l in TRAIN_DATA]

        # Mapear labels para índices
        self._label_to_idx: Dict[str, int] = {}
        self._idx_to_label: Dict[int, str] = {}
        for label in sorted(set(labels)):
            if label not in self._label_to_idx:
                idx = len(self._label_to_idx)
                self._label_to_idx[label] = idx
                self._idx_to_label[idx] = label

        y = np.array([self._label_to_idx[l] for l in labels])

        # TF-IDF vectorizer
        self._vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            analyzer="word",
            lowercase=True,
        )
        X = self._vectorizer.fit_transform(texts)

        # DecisionTree com profundidade limitada (evita overfitting)
        self._clf = DecisionTreeClassifier(
            max_depth=10,
            min_samples_leaf=2,
            random_state=42,
        )
        self._clf.fit(X, y)

    def route(self, task_description: str) -> Dict[str, Any]:
        """
        Roteia uma descrição de tarefa para o melhor agente.

        Args:
            task_description: descrição textual da tarefa

        Returns:
            Dict com agent, method, confidence, elapsed_ms
        """
        start = time.time()
        self.stats["total_routes"] += 1
        text_lower = task_description.lower()

        # 1. Tentar regras textuais primeiro (mais precisas)
        for pattern, agent, confidence in self.text_rules:
            if re.search(pattern, text_lower):
                elapsed = (time.time() - start) * 1000
                self._update_avg(elapsed)
                self.stats["rule_matches"] += 1
                return {
                    "agent": agent,
                    "method": "rule_match",
                    "confidence": confidence,
                    "pattern": pattern,
                    "elapsed_ms": round(elapsed, 2),
                }

        # 2. Fallback: DecisionTree
        try:
            X = self._vectorizer.transform([text_lower])
            pred = self._clf.predict(X)[0]
            probas = self._clf.predict_proba(X)[0]
            confidence = float(max(probas))
            agent = self._idx_to_label[pred]

            elapsed = (time.time() - start) * 1000
            self._update_avg(elapsed)
            self.stats["tree_matches"] += 1

            return {
                "agent": agent,
                "method": "decision_tree",
                "confidence": round(confidence, 4),
                "elapsed_ms": round(elapsed, 2),
            }
        except Exception:
            pass

        # 3. Fallback final: agente geral
        elapsed = (time.time() - start) * 1000
        self._update_avg(elapsed)
        self.stats["fallback"] += 1
        return {
            "agent": "general",
            "method": "fallback",
            "confidence": 0.5,
            "elapsed_ms": round(elapsed, 2),
        }

    def _update_avg(self, elapsed_ms: float):
        n = self.stats["total_routes"]
        self.stats["avg_ms"] = (
            (self.stats["avg_ms"] * (n - 1) + elapsed_ms) / n
        )

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas do roteador."""
        return {**self.stats, "agents": len(self._label_to_idx)}


# Singleton
_default_router: Optional[RuleBasedRouter] = None


def get_router() -> RuleBasedRouter:
    global _default_router
    if _default_router is None:
        _default_router = RuleBasedRouter()
    return _default_router


# ─── Teste ───────────────────────────────────────────────────

if __name__ == "__main__":
    router = RuleBasedRouter()
    test_tasks = [
        "preciso de uma biblioteca python para baixar papers do scihub",
        "implementar uma função de validação de CPF",
        "revisar o código do módulo de pagamento",
        "pesquisar artigos sobre machine learning em educação",
        "fazer deploy do container docker",
        "criar apresentação de slides para a banca",
        "qual o melhor pacote para PDF em Python?",
        "orquestrar pipeline multi-agente com validação",
        "documentar a API REST do módulo de usuários",
        "diagnosticar saúde do ecossistema",
    ]

    print("=== RuleBasedRouter ===")
    print(f"Regras: {len(router.text_rules)} | Treino: {len(TRAIN_DATA)} amostras | Agentes: {len(router._label_to_idx)}\n")

    for task in test_tasks:
        result = router.route(task)
        print(f"  Tarefa: \"{task[:50]:50s}\"")
        print(f"    → {result['agent']:30s} ({result['method']}, conf={result['confidence']}, {result['elapsed_ms']}ms)")
        print()

    print(f"Stats: {router.get_stats()}")
