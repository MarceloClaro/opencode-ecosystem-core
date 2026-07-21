# -*- coding: utf-8 -*-
"""
Motor de Raciocínio Baseado em Evidências (EBM)
=================================================
Implementa os frameworks:
  - GRADE: Classificação da qualidade da evidência e força da recomendação
  - PICO: Estruturação de perguntas clínicas
  - SOAP: Organização subjetivo/objetivo/avaliação/plano

Referências: GRADE Working Group, Centre for Evidence-Based Medicine (Oxford)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class NivelEvidencia(Enum):
    """Graus de evidência científica (GRADE adaptado)."""
    ALTA = "alta"
    MODERADA = "moderada"
    BAIXA = "baixa"
    MUITO_BAIXA = "muito_baixa"


class ForcaRecomendacao(Enum):
    """Força da recomendação (GRADE)."""
    FORTE_FAVORAVEL = "forte_favoravel"
    FRACA_FAVORAVEL = "fraca_favoravel"
    FRACA_CONTRA = "fraca_contra"
    FORTE_CONTRA = "forte_contra"
    INCONCLUSIVA = "inconclusiva"


class TipoEstudo(Enum):
    """Tipo de estudo para classificação de evidência."""
    REVISAO_SISTEMATICA = "revisao_sistematica"
    META_ANALISE = "meta_analise"
    ENSAIO_CLINICO_RANDOMIZADO = "ensaio_clinico_randomizado"
    COORTE = "coorte"
    CASO_CONTROLE = "caso_controle"
    SERIE_DE_CASOS = "serie_de_casos"
    RELATO_DE_CASO = "relato_de_caso"
    OPINIAO_ESPECIALISTA = "opiniao_especialista"
    DIRETRIZ = "diretriz"
    REVISAO_NARRATIVA = "revisao_narrativa"


@dataclass
class PICOQuery:
    """
    Pergunta clínica estruturada no formato PICO.

    P: Population/Paciente
    I: Intervention/Intervenção
    C: Comparison/Comparação
    O: Outcome/Desfecho
    """
    population: str
    intervention: str
    comparison: Optional[str] = None
    outcome: str = ""
    contexto: str = ""

    def formatar(self) -> str:
        """Formata a pergunta PICO como string."""
        partes = [
            f"P: {self.population}",
            f"I: {self.intervention}",
        ]
        if self.comparison:
            partes.append(f"C: {self.comparison}")
        partes.append(f"O: {self.outcome}")
        return " | ".join(partes)


@dataclass
class GradeClassification:
    """Classificação GRADE de uma evidência."""
    nivel: NivelEvidencia
    forca: ForcaRecomendacao
    justificativa: str
    tipo_estudo: Optional[TipoEstudo] = None
    populacao: str = ""
    data_referencia: str = ""
    limitacoes: List[str] = field(default_factory=list)


@dataclass
class SOAPNote:
    """
    Nota clínica estruturada no formato SOAP.

    S: Subjetivo (queixa do paciente)
    O: Objetivo (dados objetivos, exames)
    A: Assessment (avaliação, hipóteses)
    P: Plan (plano)
    """
    subjetivo: str = ""
    objetivo: str = ""
    assessment: str = ""
    plano: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Motor de Raciocínio Baseado em Evidências
# ──────────────────────────────────────────────────────────────────────────────


class EvidenceBasedReasoning:
    """
    Motor de raciocínio baseado em evidências.

    Fornece:
    - Classificação GRADE de evidências
    - Estruturação PICO de perguntas clínicas
    - Organização SOAP de notas clínicas
    - Hierarquia de evidência por tipo de estudo
    """

    # Hierarquia padrão de evidência (Oxford CEBM)
    HIERARQUIA_EVIDENCIA = {
        TipoEstudo.REVISAO_SISTEMATICA: 1,
        TipoEstudo.META_ANALISE: 1,
        TipoEstudo.ENSAIO_CLINICO_RANDOMIZADO: 2,
        TipoEstudo.COORTE: 3,
        TipoEstudo.CASO_CONTROLE: 4,
        TipoEstudo.SERIE_DE_CASOS: 5,
        TipoEstudo.RELATO_DE_CASO: 6,
        TipoEstudo.OPINIAO_ESPECIALISTA: 7,
        TipoEstudo.REVISAO_NARRATIVA: 7,
        TipoEstudo.DIRETRIZ: 1,  # Diretriz baseada em RS/MA
    }

    def __init__(self):
        self._classificacoes: List[GradeClassification] = []

    def classificar_evidencia(
        self,
        tipo_estudo: TipoEstudo,
        populacao: str = "",
        consistencia: bool = True,
        aplicabilidade_direta: bool = True,
        risco_viés: str = "baixo",
    ) -> GradeClassification:
        """
        Classifica uma evidência usando GRADE.

        Args:
            tipo_estudo: Tipo de estudo.
            populacao: População estudada.
            consistencia: Se os resultados são consistentes entre estudos.
            aplicabilidade_direta: Se a evidência é diretamente aplicável.
            risco_viés: 'baixo', 'moderado', 'alto'.

        Returns:
            GradeClassification com nível e força.
        """
        nivel = self._calcular_nivel(tipo_estudo, risco_viés, consistencia)
        forca = self._calcular_forca(nivel, aplicabilidade_direta, tipo_estudo)

        limitacoes = []
        if risco_viés == "alto":
            limitacoes.append("Alto risco de viés")
        if not consistencia:
            limitacoes.append("Resultados inconsistentes entre estudos")
        if not aplicabilidade_direta:
            limitacoes.append("Evidência indireta (população/desfecho diferente)")

        classificacao = GradeClassification(
            nivel=nivel,
            forca=forca,
            justificativa=self._gerar_justificativa(nivel, forca, tipo_estudo),
            tipo_estudo=tipo_estudo,
            populacao=populacao,
            data_referencia=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
            limitacoes=limitacoes,
        )

        self._classificacoes.append(classificacao)
        return classificacao

    def _calcular_nivel(
        self,
        tipo: TipoEstudo,
        risco_viés: str,
        consistencia: bool,
    ) -> NivelEvidencia:
        """Calcula o nível de evidência com base no tipo de estudo."""
        nivel_base = self.HIERARQUIA_EVIDENCIA.get(tipo, 7)

        # Penalidades
        if risco_viés == "alto":
            nivel_base += 2
        elif risco_viés == "moderado":
            nivel_base += 1
        if not consistencia:
            nivel_base += 1

        # Mapear número para enum
        if nivel_base <= 2:
            return NivelEvidencia.ALTA
        elif nivel_base <= 4:
            return NivelEvidencia.MODERADA
        elif nivel_base <= 6:
            return NivelEvidencia.BAIXA
        else:
            return NivelEvidencia.MUITO_BAIXA

    def _calcular_forca(
        self,
        nivel: NivelEvidencia,
        aplicabilidade_direta: bool,
        tipo: TipoEstudo,
    ) -> ForcaRecomendacao:
        """Calcula a força da recomendação."""
        if nivel == NivelEvidencia.ALTA and aplicabilidade_direta:
            return ForcaRecomendacao.FORTE_FAVORAVEL
        elif nivel in (NivelEvidencia.ALTA, NivelEvidencia.MODERADA):
            if aplicabilidade_direta:
                return ForcaRecomendacao.FRACA_FAVORAVEL
            return ForcaRecomendacao.INCONCLUSIVA
        elif nivel == NivelEvidencia.BAIXA:
            return ForcaRecomendacao.FRACA_FAVORAVEL
        else:
            return ForcaRecomendacao.INCONCLUSIVA

    def _gerar_justificativa(
        self,
        nivel: NivelEvidencia,
        forca: ForcaRecomendacao,
        tipo: TipoEstudo,
    ) -> str:
        """Gera justificativa textual para a classificação."""
        template = (
            f"Evidência de nível **{nivel.value}** baseada em "
            f"{tipo.value.replace('_', ' ')}. "
            f"Recomendação **{forca.value.replace('_', ' ')}**."
        )
        return template

    def criar_pico(
        self,
        population: str,
        intervention: str,
        outcome: str,
        comparison: Optional[str] = None,
        contexto: str = "",
    ) -> PICOQuery:
        """Cria uma pergunta clínica estruturada PICO."""
        return PICOQuery(
            population=population,
            intervention=intervention,
            outcome=outcome,
            comparison=comparison,
            contexto=contexto,
        )

    def criar_soap(
        self,
        subjetivo: str = "",
        objetivo: str = "",
        assessment: str = "",
        plano: str = "",
    ) -> SOAPNote:
        """Cria uma nota clínica SOAP."""
        return SOAPNote(
            subjetivo=subjetivo,
            objetivo=objetivo,
            assessment=assessment,
            plano=plano,
        )

    def aplicar_pico_ao_caso(
        self, pico: PICOQuery, caso: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aplica uma pergunta PICO a um caso clínico.

        Retorna resposta estruturada com evidência aplicável.
        """
        return {
            "pergunta_pico": pico.formatar(),
            "caso_aplicavel": pico.population.lower() in str(caso).lower(),
            "relevancia": self._calcular_relevancia(pico, caso),
            "classificacao_necessaria": "Aplicar GRADE para responder",
        }

    def _calcular_relevancia(self, pico: PICOQuery, caso: Dict[str, Any]) -> str:
        """Calcula quão relevante a pergunta PICO é para o caso."""
        caso_str = str(caso).lower()
        score = 0
        if pico.population.lower() in caso_str:
            score += 1
        if pico.intervention.lower() in caso_str:
            score += 1
        if pico.outcome.lower() in caso_str:
            score += 1
        if score >= 2:
            return "alta"
        elif score >= 1:
            return "moderada"
        return "baixa"

    def resumo_classificacoes(self) -> List[Dict[str, Any]]:
        """Resumo das classificações realizadas."""
        return [
            {
                "nivel": c.nivel.value,
                "forca": c.forca.value,
                "justificativa": c.justificativa,
                "tipo_estudo": c.tipo_estudo.value if c.tipo_estudo else None,
                "populacao": c.populacao,
            }
            for c in self._classificacoes
        ]
