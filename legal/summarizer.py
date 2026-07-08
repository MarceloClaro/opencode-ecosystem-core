# -*- coding: utf-8 -*-
"""
LegalDocumentSummarizer — Sumarizador de Documentos Jurídicos (SPEC-923)
=========================================================================
Inspirado no agente Sumarizador de Documentos do AUXJURIS.

Produz resumos estruturados de documentos legais com:
  - Compressão por relevância (preserva pontos essenciais)
  - Extração de entidades jurídicas (leis, artigos, precedentes)
  - Análise de estrutura (partes, objeto, fundamentos, conclusão)
  - Integração opcional com PrecedentAnalyzer
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class LegalEntities:
    """Entidades jurídicas extraídas de um documento."""
    leis: List[str] = field(default_factory=list)
    artigos: List[str] = field(default_factory=list)
    tribunais: List[str] = field(default_factory=list)
    precedentes_citados: List[str] = field(default_factory=list)
    partes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "leis": self.leis,
            "artigos": self.artigos,
            "tribunais": self.tribunais,
            "precedentes_citados": self.precedentes_citados,
            "partes": self.partes,
        }


@dataclass
class SummaryResult:
    """Resultado da sumarização."""
    titulo: str
    resumo: str
    entidades: LegalEntities
    compression_ratio: float  # 0.0 a 1.0 (1.0 = máxima compressão)
    topicos: List[str] = field(default_factory=list)
    fundamentos: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "titulo": self.titulo,
            "resumo": self.resumo,
            "entidades": self.entidades.to_dict(),
            "compression_ratio": self.compression_ratio,
            "topicos": self.topicos,
            "fundamentos": self.fundamentos,
        }


# ── Padrões para extração de entidades jurídicas ────────────────────────

_PATTERN_LEI = re.compile(r'Lei\s+(?:n[º°]?\s*)?(\d+[./]\d+)', re.IGNORECASE)
_PATTERN_ARTIGO = re.compile(r'art[.]?\s*(?:[º°]\s*)?(\d+[A-Za-zº°-]*)', re.IGNORECASE)
_PATTERN_TRIBUNAL = re.compile(r'(STF|STJ|TST|TSE|STM|TRF[1-5]|TJ[A-Z]{2})', re.IGNORECASE)
_PATTERN_CPC = re.compile(r'CPC[/\s]*(\d+)', re.IGNORECASE)
_PATTERN_CF = re.compile(r'CF[/\s]*(?:/88)?', re.IGNORECASE)
_PATTERN_CC = re.compile(r'CC[/\s]*(\d+)', re.IGNORECASE)
_PATTERN_PRECEDENTE = re.compile(
    r'(?:REsp|RE|HC|ADI|ADC|ADPF|MS|AI|RMS)\s+(\d+[./]\d+)',
    re.IGNORECASE
)


class LegalDocumentSummarizer:
    """Sumarizador de documentos jurídicos.

    Aplica análise estrutural a textos legais, extraindo entidades,
    tópicos e produzindo resumo condensado.
    """

    def __init__(self, max_summary_ratio: float = 0.3):
        """
        Args:
            max_summary_ratio: Proporção máxima do resumo em relação ao
                               original (0.0-1.0). Ex: 0.3 = 30%.
        """
        self.max_summary_ratio = max_summary_ratio

    def _extract_entities(self, text: str) -> LegalEntities:
        """Extrai entidades jurídicas do texto."""
        leis = list(set(m.strip() for m in _PATTERN_LEI.findall(text) if m))
        artigos_raw = list(set(m.strip() for m in _PATTERN_ARTIGO.findall(text) if m))
        tribunais = list(set(m.upper() for m in _PATTERN_TRIBUNAL.findall(text) if m))
        precedentes = list(set(m.strip() for m in _PATTERN_PRECEDENTE.findall(text) if m))

        # Limpeza de artigos
        artigos = []
        for a in artigos_raw:
            a = a.rstrip(',').strip()
            if a:
                artigos.append(a)

        # Detectar partes (simplificado: busca por "Autor", "Réu", "Recorrente")
        partes = []
        for termo in ["Autor", "Réu", "Recorrente", "Recorrido", "Apelante",
                      "Apelado", "Impetrante", "Impetrado"]:
            if re.search(rf'\b{termo}\b', text, re.IGNORECASE):
                # Extrai o nome após o termo (até próximo ponto ou quebra)
                match = re.search(
                    rf'{termo}[:\s]+([^;.\n]{{3,80}})', text, re.IGNORECASE
                )
                if match:
                    partes.append(match.group(1).strip())

        return LegalEntities(
            leis=leis,
            artigos=artigos,
            tribunais=tribunais,
            precedentes_citados=precedentes,
            partes=partes,
        )

    def _identify_topics(self, text: str) -> List[str]:
        """Identifica tópicos principais do documento.

        Usa heurística: busca por frases no início de parágrafos
        que indicam estrutura jurídica.
        """
        topicos = []
        markers = [
            (r'(?:I|II|III|IV|V|VI|VII|VIII|IX|X)\s*[-–—]\s*([^\n.]{3,60})', 1),
            (r'(?:DO|DA|DOS|DAS)\s+([A-ZÀ-Ú][A-ZÀ-Ú\s]{3,40})', 1),
            (r'(?:Objeto|Preliminar|Mérito|Fundamentação|Dispositivo|Conclusão)\s*[:\n]', 0),
        ]

        for pattern, group_idx in markers:
            for match in re.finditer(pattern, text):
                topicos.append(match.group(group_idx).strip() if group_idx else match.group(0).rstrip(':').strip())
                if len(topicos) >= 8:
                    break
            if len(topicos) >= 8:
                break

        return topicos

    def _extract_fundamentos(self, text: str) -> List[str]:
        """Extrai fundamentos jurídicos do texto."""
        fundamentos = []
        # Busca por frases que indicam fundamentação
        patterns = [
            r'(?:com base no|nos termos do|conforme|segundo|de acordo com)\s+([^;\n]{10,160})',
            r'(?:violação|afronta|contrariedade)\s+(?:ao|aos?)\s+([^;\n]{10,120})',
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                fundamentos.append(match.group(0).strip())
                if len(fundamentos) >= 5:
                    break
            if len(fundamentos) >= 5:
                break
        return fundamentos

    def summarize(self, text: str, titulo: Optional[str] = None) -> SummaryResult:
        """Produz resumo estruturado de um documento jurídico.

        Args:
            text: Texto completo do documento.
            titulo: Título opcional do documento.

        Returns:
            SummaryResult com resumo, entidades e metadados.
        """
        if not text.strip():
            return SummaryResult(
                titulo=titulo or "Documento vazio",
                resumo="Documento sem conteúdo.",
                entidades=LegalEntities(),
                compression_ratio=0.0,
            )

        # 1. Extrair entidades
        entities = self._extract_entities(text)

        # 2. Identificar tópicos
        topicos = self._identify_topics(text)

        # 3. Extrair fundamentos
        fundamentos = self._extract_fundamentos(text)

        # 4. Produzir resumo
        sentences = re.split(r'(?<=[.!?])\s+', text)
        total_chars = len(text)

        # Estratégia de compressão: preservar primeira e última sentenças,
        # mais sentenças com entidades jurídicas
        max_summary_chars = int(total_chars * self.max_summary_ratio)
        max_summary_chars = max(max_summary_chars, 200)  # mínimo 200 chars

        # Sentenças âncora: primeira sentença (contexto) + últimas (conclusão)
        anchor_indices = {0}
        if len(sentences) > 2:
            anchor_indices.add(len(sentences) - 1)
        if len(sentences) > 4:
            anchor_indices.add(len(sentences) - 2)

        # Sentenças com entidades
        for i, sent in enumerate(sentences):
            if i in anchor_indices:
                continue
            # Verificar se contém entidades relevantes
            if (_PATTERN_LEI.search(sent) or _PATTERN_ARTIGO.search(sent) or
                    _PATTERN_TRIBUNAL.search(sent) or _PATTERN_PRECEDENTE.search(sent)):
                anchor_indices.add(i)

        # Construir resumo
        selected_sentences = []
        current_len = 0
        for i, sent in enumerate(sentences):
            if i in anchor_indices and current_len < max_summary_chars:
                selected_sentences.append(sent)
                current_len += len(sent)

        resumo = " ".join(selected_sentences)
        if len(resumo) > max_summary_chars:
            resumo = resumo[:max_summary_chars] + "..."

        # Ratio de compressão
        compression_ratio = round(1.0 - (len(resumo) / max(total_chars, 1)), 4)

        return SummaryResult(
            titulo=titulo or "Documento Jurídico",
            resumo=resumo,
            entidades=entities,
            compression_ratio=compression_ratio,
            topicos=topicos,
            fundamentos=fundamentos,
        )

    def summarize_with_precedents(
        self, text: str, precedentes_dict: Optional[Dict[str, Any]] = None,
        titulo: Optional[str] = None,
    ) -> SummaryResult:
        """Sumariza e enriquece com análise de precedentes.

        Args:
            text: Texto do documento.
            precedentes_dict: Dict {id_precedente: Precedent} para enriquecer.
            titulo: Título opcional.

        Returns:
            SummaryResult enriquecido.
        """
        result = self.summarize(text, titulo)

        if precedentes_dict:
            # Adicionar referência a precedentes relevantes
            for prec_id, precedent in precedentes_dict.items():
                if prec_id in text or (hasattr(precedent, 'tese') and
                                        precedent.tese in text):
                    result.fundamentos.append(
                        f"Precedente relacionado: {precedent.tese} ({prec_id})"
                    )

        return result
