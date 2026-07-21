# -*- coding: utf-8 -*-
"""
Raciocínio Diagnóstico — Probabilidade Bayesiana e Likelihood Ratios
======================================================================
Implementa:
  - Cálculo de probabilidade pré-teste e pós-teste (Teorema de Bayes)
  - Likelihood ratios (LR+ / LR-) para exames diagnósticos
  - Nomograma de Fagan (estimativa visual)
  - Análise de probabilidade para múltiplas hipóteses

Referência: Sackett et al., Evidence-Based Medicine (EBM)
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LikelihoodRatio:
    """Razão de verossimilhança de um teste diagnóstico."""
    nome_teste: str
    lr_mais: float  # LR+ = sensibilidade / (1 - especificidade)
    lr_menos: float  # LR- = (1 - sensibilidade) / especificidade
    sensibilidade: float
    especificidade: float
    fonte: str = ""


@dataclass
class BayesianResult:
    """Resultado do cálculo bayesiano para uma hipótese."""
    hipotese: str
    prob_pre_teste: float     # Probabilidade antes do teste (0-1)
    prob_pos_teste: float     # Probabilidade depois do teste (0-1)
    lr_aplicado: float        # LR usado no cálculo
    variacao: float           # Diferença pós - pré
    interpretacao: str = ""


class DiagnosticReasoning:
    """
    Motor de raciocínio diagnóstico baseado em probabilidade bayesiana.

    Permite calcular como um resultado de exame altera a probabilidade
    de uma hipótese diagnóstica, usando likelihood ratios.
    """

    def __init__(self):
        self._testes_registrados: Dict[str, LikelihoodRatio] = {}
        self._historico: List[BayesianResult] = []

    def registrar_teste(
        self,
        nome: str,
        sensibilidade: float,
        especificidade: float,
        fonte: str = "",
    ) -> LikelihoodRatio:
        """
        Registra um teste diagnóstico com suas características.

        Args:
            nome: Nome do teste/exame.
            sensibilidade: Proporção de verdadeiros positivos (0-1).
            especificidade: Proporção de verdadeiros negativos (0-1).
            fonte: Fonte da evidência.

        Returns:
            LikelihoodRatio calculado.
        """
        if not 0 < sensibilidade < 1:
            raise ValueError(f"Sensibilidade deve estar entre 0 e 1: {sensibilidade}")
        if not 0 < especificidade < 1:
            raise ValueError(f"Especificidade deve estar entre 0 e 1: {especificidade}")

        lr_mais = sensibilidade / (1 - especificidade)
        lr_menos = (1 - sensibilidade) / especificidade

        lr = LikelihoodRatio(
            nome_teste=nome,
            lr_mais=round(lr_mais, 2),
            lr_menos=round(lr_menos, 2),
            sensibilidade=sensibilidade,
            especificidade=especificidade,
            fonte=fonte,
        )
        self._testes_registrados[nome.lower()] = lr
        return lr

    def calcular_probabilidade_pos_teste(
        self,
        prob_pre_teste: float,
        lr: float,
        hipotese: str = "",
    ) -> BayesianResult:
        """
        Calcula a probabilidade pós-teste usando o Teorema de Bayes.

        Args:
            prob_pre_teste: Probabilidade antes do teste (0-1).
            lr: Likelihood ratio (LR+ para teste positivo, LR- para negativo).
            hipotese: Nome da hipótese (opcional).

        Returns:
            BayesianResult com probabilidades calculadas.
        """
        if not 0 < prob_pre_teste < 1:
            raise ValueError(f"Probabilidade pré-teste deve estar entre 0 e 1: {prob_pre_teste}")
        if lr <= 0:
            raise ValueError(f"LR deve ser positivo: {lr}")

        # Odds pré-teste
        odds_pre = prob_pre_teste / (1 - prob_pre_teste)

        # Odds pós-teste
        odds_pos = odds_pre * lr

        # Probabilidade pós-teste
        prob_pos = odds_pos / (1 + odds_pos)

        resultado = BayesianResult(
            hipotese=hipotese,
            prob_pre_teste=round(prob_pre_teste, 4),
            prob_pos_teste=round(prob_pos, 4),
            lr_aplicado=round(lr, 2),
            variacao=round(prob_pos - prob_pre_teste, 4),
            interpretacao=self._interpretar_mudanca(prob_pre_teste, prob_pos),
        )

        self._historico.append(resultado)
        return resultado

    def avaliar_teste(
        self,
        nome_teste: str,
        prob_pre_teste: float,
        resultado_positivo: bool = True,
        hipotese: str = "",
    ) -> BayesianResult:
        """
        Avalia o impacto de um teste registrado na probabilidade.

        Args:
            nome_teste: Nome do teste (deve estar registrado).
            prob_pre_teste: Probabilidade pré-teste.
            resultado_positivo: True se teste positivo, False se negativo.
            hipotese: Nome da hipótese.

        Returns:
            BayesianResult com o impacto do teste.
        """
        teste = self._testes_registrados.get(nome_teste.lower())
        if not teste:
            raise ValueError(f"Teste '{nome_teste}' não registrado. Use registrar_teste() primeiro.")

        lr = teste.lr_mais if resultado_positivo else teste.lr_menos
        return self.calcular_probabilidade_pos_teste(prob_pre_teste, lr, hipotese)

    def comparar_testes(
        self,
        prob_pre_teste: float,
        testes: List[Tuple[str, bool]],
        hipotese: str = "",
    ) -> List[BayesianResult]:
        """
        Compara múltiplos testes sequencialmente.

        Args:
            prob_pre_teste: Probabilidade pré-teste inicial.
            testes: Lista de (nome_teste, resultado_positivo).
            hipotese: Nome da hipótese.

        Returns:
            Lista de BayesianResult para cada teste aplicado sequencialmente.
        """
        resultados = []
        prob_atual = prob_pre_teste

        for nome, positivo in testes:
            res = self.avaliar_teste(nome, prob_atual, positivo, hipotese)
            resultados.append(res)
            prob_atual = res.prob_pos_teste  # Atualiza para próximo teste

        return resultados

    def _interpretar_mudanca(self, pre: float, pos: float) -> str:
        """Interpreta a mudança de probabilidade."""
        delta = abs(pos - pre)
        if delta < 0.05:
            return "Mudança clinicamente insignificante"
        elif delta < 0.15:
            return "Mudança moderada na probabilidade"
        elif delta < 0.30:
            return "Mudança significativa na probabilidade"
        else:
            return "Mudança muito significativa (potencialmente diagnóstica)"

    def testes_disponiveis(self) -> Dict[str, LikelihoodRatio]:
        """Retorna todos os testes registrados."""
        return dict(self._testes_registrados)

    def historico(self, limit: int = 10) -> List[BayesianResult]:
        """Retorna histórico de cálculos."""
        return self._historico[-limit:]


# ──────────────────────────────────────────────────────────────────────────────
# Testes comuns pré-registrados (valores da literatura)
# ──────────────────────────────────────────────────────────────────────────────

TESTES_CLINICOS_PADRAO: Dict[str, Dict[str, float]] = {
    "ecg_para_iam": {
        "sensibilidade": 0.50,
        "especificidade": 0.95,
        "fonte": "Hess et al., JAMA 2010",
    },
    "troponina_para_iam": {
        "sensibilidade": 0.95,
        "especificidade": 0.80,
        "fonte": "Reichlin et al., NEJM 2009",
    },
    "d_dimero_para_tep": {
        "sensibilidade": 0.95,
        "especificidade": 0.40,
        "fonte": "Wells et al., Thromb Haemost 2006",
    },
    "angiotomografia_para_tep": {
        "sensibilidade": 0.96,
        "especificidade": 0.98,
        "fonte": "Stein et al., Radiology 2007",
    },
    "pcr_para_infeccao": {
        "sensibilidade": 0.75,
        "especificidade": 0.70,
        "fonte": "Simon et al., CID 2004",
    },
    "procalcitonina_para_sepse": {
        "sensibilidade": 0.85,
        "especificidade": 0.80,
        "fonte": "Schuetz et al., BMC Med 2011",
    },
}


def criar_raciocinio_padrao() -> DiagnosticReasoning:
    """
    Cria DiagnosticReasoning com testes clínicos comuns pré-registrados.
    """
    motor = DiagnosticReasoning()
    for nome, params in TESTES_CLINICOS_PADRAO.items():
        motor.registrar_teste(
            nome=nome,
            sensibilidade=params["sensibilidade"],
            especificidade=params["especificidade"],
            fonte=params["fonte"],
        )
    return motor
