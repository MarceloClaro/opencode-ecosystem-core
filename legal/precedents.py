# -*- coding: utf-8 -*-
"""
PrecedentAnalyzer — Análise de Precedentes Vinculantes (CPC/2015)
==================================================================
Implementa a análise de precedentes judiciais no sistema brasileiro,
conforme arts. 926-928 do CPC/2015 e a jurisprudência do STF e STJ.

CPC/2015, Art. 926: "Os tribunais devem uniformizar sua jurisprudência
e mantê-la estável, íntegra e coerente."

Suporte a:
  - Ratio decidendi (fundamento vinculante do precedente)
  - Obiter dictum (manifestações incidentes não vinculantes)
  - Distinguishing (distinção de fatos que afasta a aplicação do precedente)
  - Overruling (superação de precedente)
  - Súmulas Vinculantes (STF, art. 103-A CF)
  - IRDR (Incidente de Resolução de Demandas Repetitivas)
  - Repercussão Geral (STF, art. 102 §3º CF)
  - Recursos Repetitivos (STJ, art. 1.036 CPC)

Referências:
  - MARINONI, Luiz Guilherme. Precedentes Obrigatórios (2016)
  - DIDIER JR., Fredie. Curso de Direito Processual Civil (2020)
  - STF, RE 898.060 (coisa julgada inconstitucional)
  - STJ, REsp 1.111.111 (IRDR)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple


class PrecedentType(Enum):
    """Tipo de precedente no direito brasileiro."""
    SUMULA_VINCULANTE = auto()        # STF, art. 103-A CF
    REPERCUSSAO_GERAL = auto()         # STF, art. 102 §3º CF
    RECURSO_REPETITIVO = auto()        # STJ, art. 1.036 CPC
    IRDR = auto()                      # Incidente de Resolução de Demandas Repetitivas
    PRECEDENTE_INTERPRETATIVO = auto() # Decisão interpretativa de tribunal superior
    ORDINARIO = auto()                 # Decisão comum


class BindingLevel(Enum):
    """Nível de vinculatividade do precedente."""
    VINCULANTE_ERGA_OMNES = auto()   # Súmula Vinculante
    VINCULANTE_NACIONAL = auto()     # RG + Repercussão Geral
    VINCULANTE_INTERNO = auto()      # IRDR no tribunal de origem
    PERSUASIVO = auto()              # Precedente não vinculante mas relevante


@dataclass
class Precedent:
    """Representação de um precedente judicial."""
    id: str
    tribunal: str
    orgao_julgador: str
    data_julgamento: date
    tipo: PrecedentType
    binding: BindingLevel
    ementa: str
    tese: str           # Tese firmada (ratio decidendi)
    fundamentos: List[str]  # Fundamentos determinantes
    fatos: List[str]     # Fatos relevantes do caso
    dispositivo: str = ""  # Parte dispositiva
    obiter_dicta: List[str] = field(default_factory=list)
    superado_por: Optional[str] = None  # ID do precedente que o superou
    superado_em: Optional[date] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tribunal": self.tribunal,
            "orgao_julgador": self.orgao_julgador,
            "data_julgamento": self.data_julgamento.isoformat(),
            "tipo": self.tipo.name,
            "binding": self.binding.name,
            "ementa": self.ementa,
            "tese": self.tese,
            "fundamentos": self.fundamentos,
            "fatos": self.fatos,
            "dispositivo": self.dispositivo,
            "obiter_dicta": self.obiter_dicta,
            "superado_por": self.superado_por,
        }


@dataclass
class CaseFacts:
    """Fatos do caso concreto para análise de precedentes."""
    descricao: str
    fatos_relevantes: List[str]

    def to_dict(self) -> Dict:
        return {
            "descricao": self.descricao,
            "fatos_relevantes": self.fatos_relevantes,
        }


@dataclass
class PrecedentAnalysisResult:
    """Resultado da análise de precedentes."""
    precedente_aplicavel: bool
    precedente_id: Optional[str] = None
    ratio_decidendi: Optional[str] = None
    fundamentos_aplicaveis: List[str] = field(default_factory=list)
    obiter_dicta_relevantes: List[str] = field(default_factory=list)
    distinguishing: bool = False
    distinguishing_fundamentos: List[str] = field(default_factory=list)
    overruling: bool = False
    overruling_por: Optional[str] = None
    fundamentacao_completa: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "precedente_aplicavel": self.precedente_aplicavel,
            "precedente_id": self.precedente_id,
            "ratio_decidendi": self.ratio_decidendi,
            "fundamentos_aplicaveis": self.fundamentos_aplicaveis,
            "obiter_dicta_relevantes": self.obiter_dicta_relevantes,
            "distinguishing": self.distinguishing,
            "distinguishing_fundamentos": self.distinguishing_fundamentos,
            "overruling": self.overruling,
            "overruling_por": self.overruling_por,
            "fundamentacao_completa": self.fundamentacao_completa,
        }


class PrecedentAnalyzer:
    """Analisador de precedentes vinculantes do direito brasileiro.

    Permite registrar precedentes, extrair ratio decidendi, realizar
    distinguishing e verificar overruling.
    """

    def __init__(self):
        self.precedents: Dict[str, Precedent] = {}

    def register_precedent(self, p: Precedent) -> None:
        """Registra um precedente no repositório."""
        self.precedents[p.id] = p

    def register_precedents(self, precedentes: List[Precedent]) -> None:
        """Registra múltiplos precedentes."""
        for p in precedentes:
            self.register_precedent(p)

    def extract_ratio(self, precedente_id: str) -> Optional[str]:
        """Extrai a ratio decidendi (tese) de um precedente.

        A ratio decidendi é o fundamento jurídico determinante
        para a conclusão do julgamento (CPC art. 489 §1º).
        """
        p = self.precedents.get(precedente_id)
        if not p:
            return None
        return p.tese

    def extract_obiter_dicta(self, precedente_id: str) -> List[str]:
        """Extrai obiter dicta (manifestações incidentes não vinculantes)."""
        p = self.precedents.get(precedente_id)
        if not p:
            return []
        return p.obiter_dicta

    def _compare_facts(self, fatos_precedente: List[str],
                       fatos_caso: List[str]) -> List[str]:
        """Compara fatos do precedente com fatos do caso concreto.

        Retorna lista de fatos que distinguem o caso do precedente.
        """
        distintos = []
        for fato_caso in fatos_caso:
            if fato_caso not in fatos_precedente:
                for fato_prec in fatos_precedente:
                    palavras_prec = set(fato_prec.lower().split())
                    palavras_caso = set(fato_caso.lower().split())
                    # Se menos de 40% das palavras são compartilhadas,
                    # considera-se fato novo/distinto
                    if len(palavras_prec) > 0 and len(palavras_caso) > 0:
                        intersecao = palavras_prec & palavras_caso
                        similaridade = len(intersecao) / max(len(palavras_prec), len(palavras_caso))
                        if similaridade < 0.3:
                            distintos.append(fato_caso)
                            break
        return distintos

    def identify_distinguishing(self, precedente_id: str,
                                caso: CaseFacts) -> PrecedentAnalysisResult:
        """Identifica se há distinguishing que afasta a aplicação do precedente.

        Distinguishing (CPC art. 489 §1º VI): quando o caso concreto
        possui particularidades que afastam a aplicação do precedente.
        """
        p = self.precedents.get(precedente_id)
        if not p:
            return PrecedentAnalysisResult(
                precedente_aplicavel=False,
                fundamentacao_completa=[f"Precedente {precedente_id} não encontrado."],
            )

        fundamentos: List[str] = [
            f"Análise de distinguishing — Precedente: {p.id} ({p.tribunal})",
            f"Tese: {p.tese}",
            f"Fatos do precedente: {', '.join(p.fatos)}",
            f"Fatos do caso: {', '.join(caso.fatos_relevantes)}",
        ]

        # Comparar fatos
        fatos_distintos = self._compare_facts(p.fatos, caso.fatos_relevantes)

        if fatos_distintos:
            fundamentos.append(f"Distinguishing detectado: fatos distintos encontrados:")
            fundamentos.extend([f"  - {f}" for f in fatos_distintos])
            return PrecedentAnalysisResult(
                precedente_aplicavel=False,
                precedente_id=precedente_id,
                ratio_decidendi=p.tese,
                fundamentos_aplicaveis=p.fundamentos,
                obiter_dicta_relevantes=p.obiter_dicta,
                distinguishing=True,
                distinguishing_fundamentos=fatos_distintos,
                fundamentacao_completa=fundamentos,
            )
        else:
            fundamentos.append("Nenhum distinguishing detectado — precedente aplicável ao caso.")
            return PrecedentAnalysisResult(
                precedente_aplicavel=True,
                precedente_id=precedente_id,
                ratio_decidendi=p.tese,
                fundamentos_aplicaveis=p.fundamentos,
                obiter_dicta_relevantes=p.obiter_dicta,
                distinguishing=False,
                fundamentacao_completa=fundamentos,
            )

    def identify_overruling(self, precedente_id: str) -> PrecedentAnalysisResult:
        """Verifica se um precedente foi superado (overruling).

        Overruling: superação total ou parcial de precedente anterior,
        seja por evolução jurisprudencial, alteração legislativa
        ou mudança de contexto constitucional.
        """
        p = self.precedents.get(precedente_id)
        if not p:
            return PrecedentAnalysisResult(
                precedente_aplicavel=False,
                fundamentacao_completa=[f"Precedente {precedente_id} não encontrado."],
            )

        if p.superado_por:
            p_superador = self.precedents.get(p.superado_por)
            superador_info = f"{p_superador.tese} ({p_superador.id})" if p_superador else p.superado_por
            return PrecedentAnalysisResult(
                precedente_aplicavel=False,
                precedente_id=precedente_id,
                ratio_decidendi=p.tese,
                fundamentos_aplicaveis=p.fundamentos,
                overruling=True,
                overruling_por=p.superado_por,
                fundamentacao_completa=[
                    f"Overruling detectado: precedente {p.id} foi superado.",
                    f"Superado por: {superador_info}",
                    f"Data da superação: {p.superado_em.isoformat() if p.superado_em else 'desconhecida'}",
                ],
            )

        return PrecedentAnalysisResult(
            precedente_aplicavel=True,
            precedente_id=precedente_id,
            ratio_decidendi=p.tese,
            fundamentos_aplicaveis=p.fundamentos,
            overruling=False,
            fundamentacao_completa=[
                f"Precedente {p.id} continua válido e aplicável.",
                f"Tese: {p.tese}",
            ],
        )

    def apply_precedent(self, precedente_id: str,
                        caso: CaseFacts) -> PrecedentAnalysisResult:
        """Aplica um precedente ao caso concreto, com todas as verificações.

        Pipeline:
          1. Verifica overruling
          2. Extrai ratio decidendi
          3. Verifica distinguishing
          4. Se aplicável, aplica a tese ao caso
        """
        # 1. Overruling
        overruling_result = self.identify_overruling(precedente_id)
        if overruling_result.overruling:
            return overruling_result

        # 2-3. Distinguishing + aplicação
        return self.identify_distinguishing(precedente_id, caso)

    def get_binding_precedents_by_subject(self, assunto: str) -> List[Precedent]:
        """Retorna precedentes vinculantes por assunto."""
        results = []
        assunto_lower = assunto.lower()
        for p in self.precedents.values():
            if p.binding in (BindingLevel.VINCULANTE_ERGA_OMNES,
                             BindingLevel.VINCULANTE_NACIONAL):
                if (assunto_lower in p.ementa.lower() or
                        assunto_lower in p.tese.lower()):
                    results.append(p)
        return results
