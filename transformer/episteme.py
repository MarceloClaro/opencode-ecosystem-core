# -*- coding: utf-8 -*-
"""Camada Epistêmica de Roteamento — SPEC-935-R363.

Associa agentes/skills e tarefas a regimes epistemológicos por léxico
determinístico de sinais (sem LLM, sem rede, sem estado). A afinidade
entre regimes é um peso brando no roteamento do SkillHandbook.

Limite epistêmico: heurística lexical. Não determina competência real
nem a natureza "verdadeira" do conhecimento exigido; quando os sinais
são insuficientes a inferência retorna None e o roteamento permanece
idêntico ao comportamento sem episteme (fail-open).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# Taxonomia — 6 regimes epistemológicos
# ═══════════════════════════════════════════════════════════════════════

EPISTEMES: Dict[str, Dict[str, object]] = {
    "empirico_analitico": {
        "nome": "Empírico-analítico",
        "descricao": (
            "Conhecimento validado por observação, medição, experimento "
            "e inferência estatística sobre dados."
        ),
        "sinais": [
            "statistics", "statistical", "estatistica", "estatistico",
            "inference", "inferencia", "hypothesis", "hipotese", "hipoteses",
            "dados", "dataset", "datasets", "benchmark", "benchmarks",
            "experiment", "experimento", "experimentos", "empirical",
            "empirico", "regression", "regressao", "sample", "amostra",
            "amostragem", "anova", "measurement", "medicao", "correlacao",
            "correlation", "quantitativo", "quantitative",
        ],
    },
    "formal_dedutivo": {
        "nome": "Formal-dedutivo",
        "descricao": (
            "Conhecimento derivado por dedução a partir de axiomas: "
            "matemática, lógica, provas e modelagem formal."
        ),
        "sinais": [
            "mathematics", "matematica", "math", "formal", "modelagem",
            "modeling", "proof", "proofs", "prova", "provas", "teorema",
            "theorem", "logica", "logic", "dedutivo", "deduction",
            "algebra", "axioma", "axiom", "quantica", "quantum",
            "otimizacao", "optimization", "algoritmo", "algorithm",
        ],
    },
    "hermeneutico_interpretativo": {
        "nome": "Hermenêutico-interpretativo",
        "descricao": (
            "Conhecimento construído por interpretação de textos, "
            "culturas, línguas e contextos históricos."
        ),
        "sinais": [
            "translation", "traducao", "culture", "cultura", "cultural",
            "literary", "literaria", "literario", "literatura",
            "literature", "voice", "voz", "interpretacao",
            "interpretation", "hermeneutica", "linguistica", "linguistics",
            "narrativa", "narrative", "discurso", "discourse", "semiotica",
            "episteme", "epistemes", "proofreading", "idiomatic",
        ],
    },
    "critico_reflexivo": {
        "nome": "Crítico-reflexivo",
        "descricao": (
            "Conhecimento produzido por crítica, reflexão sobre vieses, "
            "ética e revisão por pares."
        ),
        "sinais": [
            "peer", "review", "reviewer", "ethics", "etica", "etico",
            "bias", "vies", "vieses", "blind", "critica", "critical",
            "critico", "reflexao", "reflexivo", "integridade", "integrity",
            "auditoria", "audit", "transparencia", "transparency",
            "openscience", "retraction",
        ],
    },
    "pragmatico_tecnico": {
        "nome": "Pragmático-técnico",
        "descricao": (
            "Conhecimento orientado a fazer funcionar: engenharia, "
            "tooling, integração e operação de sistemas."
        ),
        "sinais": [
            "tooling", "devops", "integration", "integracao", "cli",
            "engineering", "engenharia", "deploy", "deployment",
            "infraestrutura", "infrastructure", "automacao", "automation",
            "operacao", "operations", "pipeline", "instalador",
            "installer", "docker", "api", "sdk", "orchestration",
            "orquestracao", "reprodutibilidade", "reproducibility",
        ],
    },
    "regulatorio_normativo": {
        "nome": "Regulatório-normativo",
        "descricao": (
            "Conhecimento ancorado em normas, padrões e conformidade: "
            "formatação, legislação e regulação."
        ),
        "sinais": [
            "abnt", "apa", "vancouver", "norma", "normas", "norm",
            "conformidade", "compliance", "regulacao", "regulation",
            "legislacao", "legislation", "lgpd", "gdpr", "formatacao",
            "formatting", "bibliografica", "bibliografico", "citacao",
            "citacoes", "citations", "referencias", "references",
            "qualis", "iso",
        ],
    },
}

# Matriz de afinidade entre regimes (simétrica; diagonal implícita = 1.0).
# Chave canônica: tupla ordenada alfabeticamente.
_AFFINITY_PAIRS: Dict[Tuple[str, str], float] = {
    ("empirico_analitico", "formal_dedutivo"): 0.7,
    ("empirico_analitico", "pragmatico_tecnico"): 0.6,
    ("critico_reflexivo", "empirico_analitico"): 0.5,
    ("empirico_analitico", "hermeneutico_interpretativo"): 0.35,
    ("empirico_analitico", "regulatorio_normativo"): 0.4,
    ("formal_dedutivo", "pragmatico_tecnico"): 0.6,
    ("formal_dedutivo", "hermeneutico_interpretativo"): 0.3,
    ("critico_reflexivo", "formal_dedutivo"): 0.45,
    ("formal_dedutivo", "regulatorio_normativo"): 0.5,
    ("critico_reflexivo", "hermeneutico_interpretativo"): 0.7,
    ("hermeneutico_interpretativo", "pragmatico_tecnico"): 0.3,
    ("hermeneutico_interpretativo", "regulatorio_normativo"): 0.4,
    ("critico_reflexivo", "regulatorio_normativo"): 0.65,
    ("critico_reflexivo", "pragmatico_tecnico"): 0.4,
    ("pragmatico_tecnico", "regulatorio_normativo"): 0.55,
}

AFFINITY: Dict[Tuple[str, str], float] = {
    tuple(sorted(k)): v for k, v in _AFFINITY_PAIRS.items()
}

# Mínimo de ocorrências de sinais para inferir um regime (nunca chutar).
MIN_SINAIS = 2

_NEUTRAL_AFFINITY = 0.5

# Índice invertido sinal → regime (sinais são disjuntos entre regimes)
_SIGNAL_INDEX: Dict[str, str] = {}
for _regime, _spec in EPISTEMES.items():
    for _sinal in _spec["sinais"]:
        _SIGNAL_INDEX[_sinal] = _regime


@dataclass
class EpistemeProfile:
    """Resultado de uma inferência epistêmica."""

    episteme: str
    secundaria: Optional[str] = None
    confianca: float = 0.0
    sinais: List[str] = field(default_factory=list)


def _normalize(text: str) -> str:
    """Minúsculas e sem acentos (NFD, remove marcas combinantes)."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", _normalize(text))


def infer_episteme_from_text(text: Optional[str]) -> Optional[EpistemeProfile]:
    """Infere o regime epistemológico dominante de um texto.

    Retorna None quando os sinais são insuficientes (< MIN_SINAIS
    ocorrências para o regime dominante) — nunca chuta.
    """
    if not text:
        return None

    counts: Dict[str, int] = {}
    matched: Dict[str, List[str]] = {}
    for token in _tokenize(text):
        regime = _SIGNAL_INDEX.get(token)
        if regime:
            counts[regime] = counts.get(regime, 0) + 1
            matched.setdefault(regime, [])
            if token not in matched[regime]:
                matched[regime].append(token)

    if not counts:
        return None

    # Ordena por contagem desc; empate resolvido pela ordem de EPISTEMES
    regime_order = list(EPISTEMES.keys())
    ranked = sorted(
        counts.items(),
        key=lambda item: (-item[1], regime_order.index(item[0])),
    )
    dominante, dom_count = ranked[0]
    if dom_count < MIN_SINAIS:
        return None

    secundaria = None
    if len(ranked) > 1 and ranked[1][1] >= MIN_SINAIS:
        secundaria = ranked[1][0]

    return EpistemeProfile(
        episteme=dominante,
        secundaria=secundaria,
        confianca=min(1.0, dom_count / 4.0),
        sinais=matched[dominante],
    )


def infer_agent_episteme(
    category: str = "",
    agent_type: str = "",
    tags: Optional[List[str]] = None,
    name: str = "",
    description: str = "",
) -> Optional[EpistemeProfile]:
    """Infere a episteme de um agente a partir de metadados já existentes."""
    parts = [category or "", agent_type or "", name or "", description or ""]
    if tags:
        parts.extend(str(t) for t in tags)
    return infer_episteme_from_text(" ".join(parts))


def infer_task_episteme(task_description: str) -> Optional[EpistemeProfile]:
    """Infere a episteme exigida por uma tarefa."""
    return infer_episteme_from_text(task_description)


def episteme_affinity(a: str, b: str) -> float:
    """Afinidade entre dois regimes em [0,1]; desconhecidos → 0.5 neutro."""
    if a not in EPISTEMES or b not in EPISTEMES:
        return _NEUTRAL_AFFINITY
    if a == b:
        return 1.0
    return AFFINITY.get(tuple(sorted((a, b))), _NEUTRAL_AFFINITY)
