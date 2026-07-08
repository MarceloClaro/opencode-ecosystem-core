# -*- coding: utf-8 -*-
"""
PrincipleBalancing — Ponderação de Princípios (Alexy / Direito Brasileiro)
===========================================================================
Implementa a Fórmula do Peso de Robert Alexy (Teoria dos Direitos Fundamentais)
e o teste de proporcionalidade em três subtestes (adequação, necessidade,
proporcionalidade em sentido estrito), amplamente adotados pelo STF.

Referências:
  - ALEXY, Robert. Teoria dos Direitos Fundamentais (2008)
  - ÁVILA, Humberto. Teoria dos Princípios (2003)
  - STF, ADI 3.510 (células-tronco), ADPF 132 (união homoafetiva),
    RE 898.060 (coisa julgada inconstitucional)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Constantes da Fórmula do Peso de Alexy
# W = (I · G · S) / (I_j · G_j · S_j)
# I = intensidade da intervenção
# G = peso abstrato do princípio
# S = segurança das premissas empíricas

INTENSITY_LEVELS = {
    "leve": 2**0,       # 1
    "moderada": 2**1,   # 2
    "grave": 2**2,      # 4
}


@dataclass
class Principle:
    """Representação de um princípio jurídico (mandamento de otimização)."""
    id: str
    nome: str
    descricao: str
    peso_abstrato: float = 1.0  # G na fórmula de Alexy
    fundamento_constitucional: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "peso_abstrato": self.peso_abstrato,
            "fundamento_constitucional": self.fundamento_constitucional,
        }


@dataclass
class BalancingResult:
    """Resultado da ponderação entre dois princípios."""
    principio_prevalente: str
    formula_weight: float
    grau_precedencia: str  # "condicionado" | "definitivo" | "empate"
    fundamentacao: List[str] = field(default_factory=list)
    proporcao_adequada: bool = False
    proporcao_necessaria: bool = False
    proporcao_estrita: bool = False

    def to_dict(self) -> Dict:
        return {
            "principio_prevalente": self.principio_prevalente,
            "formula_weight": self.formula_weight,
            "grau_precedencia": self.grau_precedencia,
            "fundamentacao": self.fundamentacao,
            "proporcao_adequada": self.proporcao_adequada,
            "proporcao_necessaria": self.proporcao_necessaria,
            "proporcao_estrita": self.proporcao_estrita,
        }


class PrincipleBalancing:
    """Motor de ponderação de princípios (Alexy).

    Aplica a Fórmula do Peso e o teste de proporcionalidade tripartite
    para resolver colisões entre princípios constitucionais.
    """

    def __init__(self):
        self.principles: Dict[str, Principle] = {}

    def register_principle(self, p: Principle) -> None:
        """Registra um princípio no repositório."""
        self.principles[p.id] = p

    def register_principles(self, principios: List[Principle]) -> None:
        """Registra múltiplos princípios."""
        for p in principios:
            self.register_principle(p)

    def _weight_formula(self, i: float, g: float, s: float,
                        i_j: float, g_j: float, s_j: float) -> float:
        """Fórmula do peso de Alexy.

        W = (I · G · S) / (I_j · G_j · S_j)

        Onde:
          I  = intensidade da intervenção no princípio P
          G  = peso abstrato do princípio P
          S  = segurança das premissas empíricas de P
          I_j = intensidade da intervenção no princípio colidente P_j
          G_j = peso abstrato de P_j
          S_j = segurança das premissas empíricas de P_j
        """
        denominador = i_j * g_j * s_j
        if denominador == 0:
            return float('inf')
        return (i * g * s) / denominador

    def balance(self, principle_a_id: str, principle_b_id: str,
                intensidade_a: str, intensidade_b: str,
                seguranca_a: float = 1.0, seguranca_b: float = 1.0) -> BalancingResult:
        """Realiza a ponderação entre dois princípios colidentes.

        Args:
            principle_a_id: ID do primeiro princípio.
            principle_b_id: ID do segundo princípio.
            intensidade_a: Intensidade da intervenção em A ('leve', 'moderada', 'grave').
            intensidade_b: Intensidade da intervenção em B ('leve', 'moderada', 'grave').
            seguranca_a: Segurança das premissas empíricas de A (0-1, default 1.0).
            seguranca_b: Segurança das premissas empíricas de B (0-1, default 1.0).

        Returns:
            BalancingResult com o resultado da ponderação.
        """
        pa = self.principles.get(principle_a_id)
        pb = self.principles.get(principle_b_id)

        if not pa or not pb:
            raise ValueError(f"Princípio não encontrado: {principle_a_id if not pa else principle_b_id}")

        i_a = INTENSITY_LEVELS.get(intensidade_a, 1)
        i_b = INTENSITY_LEVELS.get(intensidade_b, 1)

        # W = (I · G · S) / (I_j · G_j · S_j)
        weight = self._weight_formula(i_a, pa.peso_abstrato, seguranca_a,
                                      i_b, pb.peso_abstrato, seguranca_b)

        fundamentos: List[str] = [
            f"Ponderação entre {pa.nome} (P1) e {pb.nome} (P2)",
            f"I1 (intensidade intervenção em {pa.nome}) = {intensidade_a} ({i_a})",
            f"I2 (intensidade intervenção em {pb.nome}) = {intensidade_b} ({i_b})",
            f"G1 (peso abstrato {pa.nome}) = {pa.peso_abstrato}",
            f"G2 (peso abstrato {pb.nome}) = {pb.peso_abstrato}",
            f"S1 (segurança premissas {pa.nome}) = {seguranca_a}",
            f"S2 (segurança premissas {pb.nome}) = {seguranca_b}",
            f"W = ({i_a}·{pa.peso_abstrato}·{seguranca_a}) / ({i_b}·{pb.peso_abstrato}·{seguranca_b}) = {weight:.4f}",
        ]

        # Determinar precedência
        if weight > 1.5:
            prevalente = pa.nome
            grau = "condicionado"
            fundamentos.append(f"P1 ({pa.nome}) prevalece condicionalmente: W = {weight:.4f} > 1,5")
        elif weight < 0.67:
            prevalente = pb.nome
            grau = "condicionado"
            fundamentos.append(f"P2 ({pb.nome}) prevalece condicionalmente: W = {weight:.4f} < 0,67")
        elif weight == float('inf'):
            prevalente = pa.nome
            grau = "definitivo"
            fundamentos.append(f"P1 ({pa.nome}) prevalece definitivamente: intervenção zero em P2")
        else:
            prevalente = "empate"
            grau = "empate"
            fundamentos.append(f"Empate na ponderação: W = {weight:.4f} (0,67 ≤ W ≤ 1,5)")

        return BalancingResult(
            principio_prevalente=prevalente,
            formula_weight=weight,
            grau_precedencia=grau,
            fundamentacao=fundamentos,
        )

    def proportionality(self, principle_a_id: str, principle_b_id: str,
                        medida: str, fim: str,
                        intensidade_a: str, intensidade_b: str,
                        alternativa_menos_onerosa: Optional[str] = None,
                        seguranca_a: float = 1.0, seguranca_b: float = 1.0) -> BalancingResult:
        """Teste de proporcionalidade completo (3 subtestes).

        Subtestes:
          1. Adequação: a medida é adequada para atingir o fim?
          2. Necessidade: há alternativa menos onerosa?
          3. Proporcionalidade em sentido estrito: benefício > custo?

        Args:
            principle_a_id: Princípio que justifica a medida.
            principle_b_id: Princípio restringido pela medida.
            medida: Descrição da medida analisada.
            fim: Fim perseguido pela medida.
            intensidade_a: Intensidade da promoção de A.
            intensidade_b: Intensidade da restrição a B.
            alternativa_menos_onerosa: Se existe alternativa que restrinja menos.
            seguranca_a: Segurança empírica da eficácia da medida.
            seguranca_b: Segurança empírica da restrição.

        Returns:
            BalancingResult com o resultado dos 3 subtestes.
        """
        pa = self.principles.get(principle_a_id)
        pb = self.principles.get(principle_b_id)

        if not pa or not pb:
            raise ValueError(f"Princípio não encontrado")

        fundamentos: List[str] = [
            f"Teste de Proporcionalidade — Medida: {medida}",
            f"Fim: {fim}",
            f"Princípio fundamentador: {pa.nome}",
            f"Princípio restringido: {pb.nome}",
        ]

        # 1. Adequação
        adequada = seguranca_a > 0.3 and intensidade_a in ("leve", "moderada", "grave")
        fundamentos.append(
            f"1. Adequação: medida {'é' if adequada else 'NÃO é'} adequada "
            f"(segurança empírica = {seguranca_a:.2f})"
        )

        # 2. Necessidade
        necessaria = alternativa_menos_onerosa is None
        fundamentos.append(
            f"2. Necessidade: {'NÃO há' if necessaria else 'HÁ'} alternativa menos onerosa"
            + (f" ({alternativa_menos_onerosa})" if not necessaria else "")
        )

        # 3. Proporcionalidade estrita
        balance = self.balance(principle_a_id, principle_b_id,
                               intensidade_a, intensidade_b,
                               seguranca_a, seguranca_b)
        estrita = balance.formula_weight >= 1.0
        fundamentos.append(
            f"3. Proporcionalidade estrita: W = {balance.formula_weight:.4f} — "
            f"{'proporcional' if estrita else 'desproporcional'}"
        )

        return BalancingResult(
            principio_prevalente=balance.principio_prevalente,
            formula_weight=balance.formula_weight,
            grau_precedencia=balance.grau_precedencia,
            fundamentacao=fundamentos,
            proporcao_adequada=adequada,
            proporcao_necessaria=necessaria,
            proporcao_estrita=estrita,
        )
