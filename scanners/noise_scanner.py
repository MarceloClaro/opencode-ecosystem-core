#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StructuralNoiseScanner v1.0 — Structural Noise Scanner / SNS (R494)

Proposta do usuário: nem tudo que aparece no fenômeno é estruturalmente
relevante — exemplos redundantes, metáforas, variações superficiais e ruído
contextual. O objetivo é REMOVER RUÍDO SEM ELIMINAR FUNÇÃO RELEVANTE.

    C = E + S + R               (corpus = exemplos + estruturas + ruído)
    C' = S + E*                 (modelo reduzido: estruturas + exemplos mínimos)
    Reconstrução(C') ≈ Estrutura(C)

Componentes (proposta do usuário):
    1. ElementClassifier      — exemplo | estrutura | ruído | redundância
                                | vetor-explicativo
    2. FunctionPreservation   — função continua representada após remoção?
    3. StructuralCompression  — manifestações equivalentes → estrutura comum
    4. ReconstructionTest     — o modelo reduzido ainda explica o original?
    5. RelevanceProtection    — regras de remoção (função noutro elemento /
                                retirada não altera reconstrução / repetição)

Métricas:
    SPS (Structural Preservation Score) = funções preservadas / totais
        ≥ 0.90 → compressão segura | 0.70–0.90 → moderada | < 0.70 → destrutiva
    NRR (Noise Reduction Rate) = removidos como ruído / totais
    FLI (Functional Loss Index) = funções perdidas / totais (menor é melhor)

Redução de dimensionalidade conceitual, stdlib, anti-overclaim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ─── Limiares documentados (SPEC-935-R494) ──────────────────────────────
SIMILARITY_REDUNDANCY = 0.75   # > = duplicata funcional
SIMILARITY_CLUSTER = 0.60      # ≥ = manifestações equivalentes
SPS_SEGURO = 0.90
SPS_MODERADO = 0.70

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "com", "sem", "por",
    "para", "que", "e", "ou", "se", "é", "não", "nao", "mais", "menos",
    "muito", "pouco", "ao", "aos", "este", "esta", "isto", "isso", "ele",
    "ela", "eles", "elas", "todo", "toda", "todos", "todas", "como",
    "são", "sao", "ser", "ter", "há", "ha", "the", "and", "of", "to",
    "in", "for", "with", "is", "are", "was", "were", "on", "at", "by",
    "an", "be", "it", "its", "this", "that", "these", "those",
}

EXAMPLE_MARKERS = (
    "ex:", "ex.", "exemplo", "por exemplo", "e.g.", "como por exemplo",
    "p.ex", "tais como", "como no caso",
)

PROPER_NAME_RE = re.compile(r"\b[A-ZÀ-Ú][a-zà-ú]+\b")

TOKEN_RE = re.compile(r"[a-zà-ú0-9]+")


def _tokens(text: str) -> set[str]:
    """Vocabulário funcional: palavras de conteúdo, minúsculas, ≥3 chars."""
    out: set[str] = set()
    for word in TOKEN_RE.findall(text.lower()):
        if len(word) >= 3 and word not in STOPWORDS:
            out.add(word)
    return out


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


@dataclass
class ClassifiedElement:
    element: str
    category: str          # exemplo|estrutura|ruido|redundancia|vetor-explicativo
    tokens: set[str]       # vocabulário funcional
    function: str          # função declarada (tokens ordenados)


@dataclass
class NoiseScanReport:
    """Relatório estruturado de compressão do SNS."""
    classified: list[dict[str, Any]]
    clusters: list[dict[str, Any]]
    preserved: list[str]            # elementos mantidos no modelo reduzido
    removed: list[str]              # elementos removidos (com justificativa)
    removals: dict[str, str]        # elemento → razão da remoção
    sps: float
    nrr: float
    fli: float
    level: str                      # seguro | moderado | destrutivo
    reconstruction: float           # score de reconstrução (0-1)
    functions_total: int
    functions_preserved: int
    params: dict[str, Any] = field(default_factory=dict)


class StructuralNoiseScanner:
    """Compressão estrutural com preservação de função relevante."""

    def __init__(self, force_remove_all_noise: bool = False):
        self.force_remove_all_noise = force_remove_all_noise  # teste CA4

    # ── 1. Element Classifier ───────────────────────────────────────────
    def classify(self, elements: list[str]) -> list[ClassifiedElement]:
        classified: list[ClassifiedElement] = []
        for el in elements:
            tokens = _tokens(el)
            if not tokens:
                category = "ruido"
            else:
                category = "estrutura"
                # redundância: alta similaridade com elemento anterior
                for prev in classified:
                    if _jaccard(prev.tokens, tokens) > SIMILARITY_REDUNDANCY:
                        category = "redundancia"
                        break
                if category == "estrutura":
                    low = el.lower()
                    if any(m in low for m in EXAMPLE_MARKERS) or (
                            PROPER_NAME_RE.search(el) and len(tokens) <= 6):
                        category = "exemplo"
                    elif any(w in low for w in
                             ("significa", "consiste", " é ", "é ",
                              "é definido", "define-se")):
                        category = "vetor-explicativo"
            function = " ".join(sorted(tokens))
            classified.append(ClassifiedElement(
                element=el, category=category, tokens=tokens,
                function=function))
        return classified

    # ── 2+4. Função preservada / teste de reconstrução ──────────────────
    @staticmethod
    def _function_map(classified: list[ClassifiedElement]) -> dict[str, int]:
        funcs: dict[str, int] = {}
        for c in classified:
            if c.function:
                funcs[c.function] = funcs.get(c.function, 0) + 1
        return funcs

    def _preserved_count(self, kept: list[ClassifiedElement],
                         all_funcs: dict[str, int]) -> int:
        kept_funcs = {c.function for c in kept if c.function}
        return sum(1 for f in all_funcs if f in kept_funcs)

    # ── 5. Relevance Protection Layer ───────────────────────────────────
    def _removable(self, el: ClassifiedElement, others: list[ClassifiedElement],
                   funcs: dict[str, int]) -> tuple[bool, str]:
        """Regras do usuário: só remove se (1) função representada em outro;
        (2) retirada não altera reconstrução; (3) repetição sem função nova.
        """
        if not el.function:
            return True, "sem vocabulário funcional (ruído)"
        # (3) repetição sem função nova
        if funcs.get(el.function, 0) > 1:
            return True, "repetição sem função nova (função já representada)"
        # (1) função representada em outro elemento
        for o in others:
            if o is not el and o.function == el.function:
                return True, "função idêntica já representada em outro elemento"
        # (2) retirada não altera reconstrução: tokens cobertos por outros
        covered = set()
        for o in others:
            if o is not el:
                covered |= o.tokens
        if el.tokens and el.tokens <= covered:
            return True, "função integralmente coberta por outros elementos"
        # caso contrário, o elemento deve ser preservado (proteção)
        return False, "elemento único — função não representada em outro"

    # ── 3. Structural Compression Engine ────────────────────────────────
    def compress(self, classified: list[ClassifiedElement]) -> list[dict]:
        clusters: list[dict] = []
        for i, c in enumerate(classified):
            placed = False
            for cl in clusters:
                common = c.tokens & set(cl["common_tokens"])
                union = c.tokens | set(cl["common_tokens"])
                sim = len(common) / len(union) if union else 0.0
                if sim >= SIMILARITY_CLUSTER:
                    cl["members"].append(c.element)
                    cl["common_tokens"] = sorted(common or union)
                    placed = True
                    break
            if not placed:
                clusters.append({"members": [c.element],
                                 "common_tokens": sorted(c.tokens)})
        return clusters

    # ── pipeline ────────────────────────────────────────────────────────
    def scan_text(self, elements: list[str]) -> NoiseScanReport:
        if not elements:
            return NoiseScanReport(
                classified=[], clusters=[], preserved=[], removed=[],
                removals={}, sps=0.0, nrr=0.0, fli=0.0, level="seguro",
                reconstruction=0.0, functions_total=0, functions_preserved=0,
            )
        classified = self.classify(elements)
        funcs = self._function_map(classified)
        kept: list[ClassifiedElement] = []
        removed: list[str] = []
        removals: dict[str, str] = {}
        for c in classified:
            if c.category == "ruido" and not self.force_remove_all_noise:
                removed.append(c.element)
                removals[c.element] = "ruído sem vocabulário funcional"
                continue
            ok, why = self._removable(c, classified, funcs)
            if ok and (c.category in ("redundancia", "ruido")
                       or self.force_remove_all_noise):
                removed.append(c.element)
                removals[c.element] = why
            else:
                kept.append(c)
        clusters = self.compress(kept)
        total = max(1, len(funcs))
        preserved = self._preserved_count(kept, funcs)
        fli = (total - preserved) / total
        sps = preserved / total
        level = ("seguro" if sps >= SPS_SEGURO
                 else "moderado" if sps >= SPS_MODERADO
                 else "destrutivo")
        nrr = len(removed) / max(1, len(elements))
        reconstruction = 1.0 - fli
        return NoiseScanReport(
            classified=[
                {"element": c.element, "category": c.category,
                 "function": c.function, "tokens": sorted(c.tokens)}
                for c in classified
            ],
            clusters=clusters,
            preserved=[c.element for c in kept],
            removed=removed,
            removals=removals,
            sps=round(sps, 4),
            nrr=round(nrr, 4),
            fli=round(fli, 4),
            level=level,
            reconstruction=round(reconstruction, 4),
            functions_total=total,
            functions_preserved=preserved,
            params={"n_elements": len(elements),
                    "n_kept": len(kept),
                    "n_clusters": len(clusters)},
        )