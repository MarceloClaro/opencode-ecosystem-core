#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StructuralCompressionEngine v1.0 — SCE (R495)

Proposta do usuário: comprimir textos gigantes preservando a estrutura
cognitiva essencial — não é um resumidor ("o que o texto diz em poucas
palavras?"), é um compressor estrutural ("qual é a menor versão que ainda
preserva sua estrutura cognitiva?"). Aplicação operacional do SNS (R494).

    T = P1 + P2 + ... + Pn     (fragmentação respeitando frases)
    SNS(Pi) = Vi               (vetorização estrutural por parte)
    T' = ΣV                    (reconstrução global)
    Δ = Estrutura(T) − Estrutura(T')   (teste delta)

Métricas:
    CR  (Compression Ratio)          = tokens originais / tokens finais
    CPS (Cognitive Preservation)     = estruturas preservadas / totais
    FLI (Functional Loss Index)      = 1 − CPS
    DG  (Density Gain)               = CPS × CR

Níveis: CPS ≥ 0.90 seguro | 0.70–0.90 moderado | < 0.70 destrutivo.
Só aprova a compressão se o final ainda permitir reconstruir o raciocínio.
Hermético, stdlib, anti-overclaim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from scanners.noise_scanner import StructuralNoiseScanner

# ─── Limiares (mesmas faixas do SNS R494) ───────────────────────────────
CPS_SEGURO = 0.90
CPS_MODERADO = 0.70

SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"\S+")


@dataclass
class SCEReport:
    """Relatório de compressão estrutural."""
    compressed_text: str
    cr: float
    cps: float
    fli: float
    dg: float
    level: str
    tokens_original: int
    tokens_final: int
    tokens_saved: int
    n_elements_original: int
    n_elements_final: int
    parts_processed: int
    functions_preserved: list[str]
    removed: list[str]
    params: dict[str, Any] = field(default_factory=dict)


class StructuralCompressionEngine:
    """Comprime texto gigante com preservação estrutural auditável."""

    def __init__(self, chunk_chars: int = 1200):
        self.chunk_chars = max(80, chunk_chars)
        self.sns = StructuralNoiseScanner()

    # ── Etapa 1 — Fragmentação ──────────────────────────────────────────
    def fragment(self, text: str, chunk_chars: int | None = None) -> list[str]:
        """Divide respeitando fronteiras de frases (`.!?`), máx. chunk_chars.

        Sem cortar frases no meio: agrega frases até estourar o limite e
        então quebra na última fronteira; se uma única frase exceder o
        limite, corta por palavras (fallback).
        """
        max_chars = chunk_chars or self.chunk_chars
        if not text.strip():
            return []
        sentences = [s.strip() for s in SENTENCE_END_RE.split(text) if s.strip()]
        parts: list[str] = []
        current = ""
        for sent in sentences:
            if len(current) + len(sent) + 1 <= max_chars:
                current = (current + " " + sent).strip()
            else:
                if current:
                    parts.append(current)
                # frase única maior que o limite: fallback palavra a palavra
                if len(sent) > max_chars:
                    words = sent.split()
                    buf = ""
                    for w in words:
                        if len(buf) + len(w) + 1 <= max_chars:
                            buf = (buf + " " + w).strip()
                        else:
                            parts.append(buf)
                            buf = w
                    if buf:
                        parts.append(buf)
                else:
                    current = sent
        if current:
            parts.append(current)
        return parts

    # ── Etapa 2 — Vetorização (SNS por parte) ───────────────────────────
    def _vectorize(self, parts: list[str]) -> tuple[list[str], list[str], int, int, int, int]:
        preserved: list[str] = []
        removed: list[str] = []
        n_original = 0
        n_final = 0
        functions_total = 0
        functions_preserved = 0
        for part in parts:
            elements = [s.strip() for s in re.split(r"(?<=[.!?])\s+", part)
                        if s.strip()] or [part]
            rep = self.sns.scan_text(elements)
            n_original += len(elements)
            preserved.extend(rep.preserved)
            removed.extend(rep.removed)
            n_final += len(rep.preserved)
            functions_total += rep.functions_total
            functions_preserved += rep.functions_preserved
        return (preserved, removed, n_original, n_final,
                functions_total, functions_preserved)

    # ── Pipeline completo ───────────────────────────────────────────────
    def compress(self, text: str,
                 chunk_chars: int | None = None) -> SCEReport:
        if not text.strip():
            return SCEReport(
                compressed_text="", cr=1.0, cps=1.0, fli=0.0, dg=1.0,
                level="seguro", tokens_original=0, tokens_final=0,
                tokens_saved=0, n_elements_original=0, n_elements_final=0,
                parts_processed=0, functions_preserved=[], removed=[],
            )
        parts = self.fragment(text, chunk_chars=chunk_chars)
        (preserved, removed, n_orig, n_final,
         funcs_total, funcs_preserved) = self._vectorize(parts)
        compressed = " ".join(preserved).strip()
        tokens_orig = len(TOKEN_RE.findall(text))
        tokens_final = len(TOKEN_RE.findall(compressed))
        # CPS mede FUNÇÕES (estrutura cognitiva), não elementos: remover uma
        # repetição não perde função (FLI = funções perdidas / funções totais)
        cps = (funcs_preserved / funcs_total) if funcs_total else 1.0
        cr = (tokens_orig / tokens_final) if tokens_final else 1.0
        fli = 1.0 - cps
        dg = cps * cr
        level = ("seguro" if cps >= CPS_SEGURO
                 else "moderado" if cps >= CPS_MODERADO
                 else "destrutivo")
        return SCEReport(
            compressed_text=compressed,
            cr=round(cr, 4),
            cps=round(cps, 4),
            fli=round(fli, 4),
            dg=round(dg, 4),
            level=level,
            tokens_original=tokens_orig,
            tokens_final=tokens_final,
            tokens_saved=max(0, tokens_orig - tokens_final),
            n_elements_original=n_orig,
            n_elements_final=n_final,
            parts_processed=len(parts),
            functions_preserved=preserved,
            removed=removed,
            params={"chunk_chars": chunk_chars or self.chunk_chars,
                    "parts": len(parts)},
        )