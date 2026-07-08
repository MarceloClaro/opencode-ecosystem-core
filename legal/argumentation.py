# -*- coding: utf-8 -*-
"""
LegalArgumentScorer — Scoring de Argumentação Jurídica
========================================================
Avalia a qualidade de argumentos jurídicos com base em critérios
objetivos do direito brasileiro.

Critérios de avaliação:
  1. Validade Legal — o argumento possui fundamento normativo?
  2. Suporte Jurisprudencial — o argumento é consistente com precedentes?
  3. Suporte Doutrinário — o argumento é corroborado pela doutrina?
  4. Consistência Interna — o argumento é logicamente coerente?
  5. Persuasão Retórica — o argumento é bem estruturado?

Referências:
  - PERELMAN, Chaïm. Tratado da Argumentação (1958)
  - ATIENZA, Manuel. As Razões do Direito (2006)
  - FERRAZ JR., Tercio Sampaio. Introdução ao Estudo do Direito (2003)
  - STF, ADC 43 (separação de poderes)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LegalArgument:
    """Representação de um argumento jurídico."""
    id: str
    autor: str
    tese: str                     # A conclusão defendida
    fundamento_normativo: str      # Base legal (artigo, lei, CF)
    fundamento_jurisprudencial: Optional[str] = None
    fundamento_doutrinario: Optional[str] = None
    premissas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "autor": self.autor,
            "tese": self.tese,
            "fundamento_normativo": self.fundamento_normativo,
            "fundamento_jurisprudencial": self.fundamento_jurisprudencial,
            "fundamento_doutrinario": self.fundamento_doutrinario,
            "premissas": self.premissas,
        }


@dataclass
class ScoreDetail:
    """Detalhamento de um critério de score."""
    criterio: str
    score: float            # 0 a 1
    justificativa: str
    peso: float = 1.0       # Peso na composição final

    def to_dict(self) -> Dict:
        return {
            "criterio": self.criterio,
            "score": self.score,
            "justificativa": self.justificativa,
            "peso": self.peso,
        }


@dataclass
class ArgumentScoreResult:
    """Resultado completo do scoring de argumento jurídico."""
    argumento_id: str
    score_total: float        # 0 a 1
    scores: List[ScoreDetail] = field(default_factory=list)
    recomendacao: str = ""    # "Forte", "Moderado", "Fraco", "Inconsistente"
    fundamentacao: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "argumento_id": self.argumento_id,
            "score_total": self.score_total,
            "scores": [s.to_dict() for s in self.scores],
            "recomendacao": self.recomendacao,
            "fundamentacao": self.fundamentacao,
        }


class LegalArgumentScorer:
    """Avaliador de argumentos jurídicos.

    Pondera múltiplos critérios para produzir um score objetivo
    da qualidade e robustez de um argumento jurídico.
    """

    # Pesos-padrão para cada critério (validade legal tem maior peso)
    DEFAULT_WEIGHTS = {
        "validade_legal": 3.0,
        "suporte_jurisprudencial": 2.0,
        "suporte_doutrinario": 1.5,
        "consistencia_interna": 2.0,
        "persuasao_retorica": 1.0,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)

    def _score_validity(self, arg: LegalArgument) -> ScoreDetail:
        """Avalia a validade legal: o argumento possui fundamento normativo correto?

        Critérios:
          - Se há fundamento normativo específico (ex.: CF art. 5º, Lei X art. Y) → score alto
          - Se há apenas menção genérica a "legislação" → score médio
          - Se não há fundamento normativo → score baixo
        """
        fundamento = arg.fundamento_normativo.lower()

        if not fundamento or fundamento in ("", "n/a", "nenhum"):
            score = 0.0
            justificativa = "Ausência de fundamento normativo."
        elif any(palavra in fundamento for palavra in [
            "art.", "artigo", "cf", "constituição", "lei", "cpc",
            "código", "decreto-lei", "lindb", "parágrafo", "inciso",
        ]):
            score = 1.0
            justificativa = f"Fundamento normativo específico: {arg.fundamento_normativo}"
        else:
            score = 0.5
            justificativa = f"Fundamento normativo genérico: {arg.fundamento_normativo}"

        return ScoreDetail(
            criterio="validade_legal",
            score=score,
            justificativa=justificativa,
            peso=self.weights.get("validade_legal", 3.0),
        )

    def _score_jurisprudential(self, arg: LegalArgument) -> ScoreDetail:
        """Avalia suporte jurisprudencial."""
        fj = (arg.fundamento_jurisprudencial or "").lower()

        if not fj or fj in ("", "n/a", "nenhum"):
            score = 0.0
            justificativa = "Sem suporte jurisprudencial."
        elif any(palavra in fj for palavra in [
            "stf", "stj", "tst", "tse", "súmula", "repercussão geral",
            "recurso repetitivo", "irdr", "precedente", "vinculante",
        ]):
            if "súmula" in fj and "vinculante" in fj:
                score = 1.0
                justificativa = f"Suporte jurisprudencial vinculante: {arg.fundamento_jurisprudencial}"
            elif any(palavra in fj for palavra in ["stf", "stj"]):
                score = 0.9
                justificativa = f"Suporte de tribunal superior: {arg.fundamento_jurisprudencial}"
            else:
                score = 0.7
                justificativa = f"Suporte jurisprudencial relevante: {arg.fundamento_jurisprudencial}"
        else:
            score = 0.4
            justificativa = f"Suporte jurisprudencial genérico: {arg.fundamento_jurisprudencial}"

        return ScoreDetail(
            criterio="suporte_jurisprudencial",
            score=score,
            justificativa=justificativa,
            peso=self.weights.get("suporte_jurisprudencial", 2.0),
        )

    def _score_doctrinal(self, arg: LegalArgument) -> ScoreDetail:
        """Avalia suporte doutrinário."""
        fd = (arg.fundamento_doutrinario or "").lower()

        if not fd or fd in ("", "n/a", "nenhum"):
            score = 0.0
            justificativa = "Sem suporte doutrinário."
        elif any(nome in fd for nome in [
            "alexy", "á vila", "humberto", "canotilho", "streck",
            "lenio", "marinoni", "didier", "ferraz", "sampaio",
            "perelman", "atienza", "mendes", "gilmar",
        ]):
            score = 1.0
            justificativa = f"Suporte doutrinário de autoridade reconhecida: {arg.fundamento_doutrinario}"
        else:
            score = 0.5
            justificativa = f"Suporte doutrinário: {arg.fundamento_doutrinario}"

        return ScoreDetail(
            criterio="suporte_doutrinario",
            score=score,
            justificativa=justificativa,
            peso=self.weights.get("suporte_doutrinario", 1.5),
        )

    def _score_consistency(self, arg: LegalArgument) -> ScoreDetail:
        """Avalia consistência interna do argumento.

        Verifica se as premissas sustentam a tese e se há contradições.
        """
        if not arg.premissas:
            score = 0.3
            justificativa = "Argumento sem premissas explícitas — consistência não verificável."
        else:
            # Verifica coerência básica: número de premissas e relação com a tese
            n_premissas = len(arg.premissas)
            palavras_tese = set(arg.tese.lower().split())

            # Checa se as premissas se relacionam com a tese
            conexoes = 0
            for prem in arg.premissas:
                palavras_prem = set(prem.lower().split())
                intersecao = palavras_tese & palavras_prem
                if len(intersecao) >= 2:
                    conexoes += 1

            if n_premissas >= 3 and conexoes >= 2:
                score = 1.0
                justificativa = f"Argumento com {n_premissas} premissas consistentes com a tese."
            elif n_premissas >= 1 and conexoes >= 1:
                score = 0.6
                justificativa = f"Argumento com {n_premissas} premissa(s) e {conexoes} conexão(ões) com a tese."
            else:
                score = 0.3
                justificativa = "Premissas inconsistentes ou não conectadas à tese."

        return ScoreDetail(
            criterio="consistencia_interna",
            score=score,
            justificativa=justificativa,
            peso=self.weights.get("consistencia_interna", 2.0),
        )

    def _score_persuasion(self, arg: LegalArgument) -> ScoreDetail:
        """Avalia persuasão retórica (estruturação do argumento).

        Critérios: clareza da tese, presença de fundamentação normativa,
        completude (tese + norma + premissas).
        """
        score = 0.0
        fatores_positivos = []

        if len(arg.tese) > 10:
            score += 0.3
            fatores_positivos.append("Tese claramente enunciada")

        if arg.fundamento_normativo and arg.fundamento_normativo not in ("", "n/a"):
            score += 0.3
            fatores_positivos.append("Fundamento normativo presente")

        if arg.premissas:
            score += 0.2
            fatores_positivos.append(f"{len(arg.premissas)} premissa(s) explicitada(s)")

        if arg.fundamento_jurisprudencial:
            score += 0.1
            fatores_positivos.append("Jurisprudência citada")

        if arg.fundamento_doutrinario:
            score += 0.1
            fatores_positivos.append("Doutrina citada")

        justificativa = "; ".join(fatores_positivos) if fatores_positivos else "Argumento pouco estruturado."

        return ScoreDetail(
            criterio="persuasao_retorica",
            score=min(score, 1.0),
            justificativa=justificativa,
            peso=self.weights.get("persuasao_retorica", 1.0),
        )

    def score(self, argumento: LegalArgument) -> ArgumentScoreResult:
        """Avalia um argumento jurídico e retorna score detalhado.

        Args:
            argumento: O argumento jurídico a ser avaliado.

        Returns:
            ArgumentScoreResult com score 0-1 e detalhamento.
        """
        scores = [
            self._score_validity(argumento),
            self._score_jurisprudential(argumento),
            self._score_doctrinal(argumento),
            self._score_consistency(argumento),
            self._score_persuasion(argumento),
        ]

        # Score ponderado
        peso_total = sum(s.peso for s in scores)
        score_ponderado = sum(s.score * s.peso for s in scores) / peso_total if peso_total > 0 else 0.0

        # Recomendação
        if score_ponderado >= 0.8:
            recomendacao = "Forte"
            fundamentacao_extra = "Argumento juridicamente robusto com fundamentação sólida em norma, jurisprudência e doutrina."
        elif score_ponderado >= 0.6:
            recomendacao = "Moderado"
            fundamentacao_extra = "Argumento razoável mas que pode ser fortalecido com mais fundamentação."
        elif score_ponderado >= 0.4:
            recomendacao = "Fraco"
            fundamentacao_extra = "Argumento insuficientemente fundamentado — necessário reforçar base normativa e/ou jurisprudencial."
        else:
            recomendacao = "Inconsistente"
            fundamentacao_extra = "Argumento sem fundamentação jurídica mínima."

        fundamentos = [
            f"Score total: {score_ponderado:.4f}",
            f"Recomendação: {recomendacao}",
            fundamentacao_extra,
        ]
        for s in scores:
            fundamentos.append(f"  {s.criterio}: {s.score:.2f} (peso {s.peso}) — {s.justificativa}")

        return ArgumentScoreResult(
            argumento_id=argumento.id,
            score_total=round(score_ponderado, 4),
            scores=scores,
            recomendacao=recomendacao,
            fundamentacao=fundamentos,
        )
