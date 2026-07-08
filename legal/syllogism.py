# -*- coding: utf-8 -*-
"""
LegalSyllogism — Subsunção Legal (Silogismo Jurídico Brasileiro)
=================================================================
O raciocínio jurídico fundamental: subsunção do fato à norma.

Estrutura:
  Premissa Maior (norma): "Se F, então deve-ser C"
  Premissa Menor (fato): "Ocorreu F"
  Conclusão: "Logo, deve-ser C"

Suporte a:
  - Hierarquia normativa (CF > Lei Complementar > Lei Ordinária > Decreto)
  - Antinomias (conflito entre normas de mesmo nível)
  - Conflito de competência (União, Estado, Município)
  - Ponderação entre princípios colidentes
  - Controle de constitucionalidade (norma inaplicável se inconstitucional)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


class NormHierarchy(Enum):
    """Hierarquia normativa do ordenamento jurídico brasileiro (Kelsen adaptado)."""
    CONSTITUICAO_FEDERAL = 7
    EMENDA_CONSTITUCIONAL = 7
    TRATADO_DIREITOS_HUMANOS_EC3 = 6
    LEI_COMPLEMENTAR = 5
    LEI_ORDINARIA = 4
    MEDIDA_PROVISORIA = 4
    LEI_DELEGADA = 4
    DECRETO_LEGISLATIVO = 4
    DECRETO_REGULAMENTAR = 3
    PORTARIA = 2
    INSTRUCAO_NORMATIVA = 2
    ATO_ADMINISTRATIVO = 1


class Competence(Enum):
    """Competência federativa (CF arts. 21-24)."""
    UNIAO = auto()
    ESTADO = auto()
    MUNICIPIO = auto()
    DISTRITO_FEDERAL = auto()
    CONCORRENTE = auto()
    COMUM = auto()
    PRIVATIVA_UNIAO = auto()
    RESIDUAL = auto()


class NormType(Enum):
    """Tipo de norma jurídica."""
    REGRA = auto()        # "se F, então C" — aplicação por subsunção
    PRINCIPIO = auto()    # mandamento de otimização — aplicação por ponderação
    CONCEITO_INDETERMINADO = auto()


@dataclass
class LegalNorm:
    """Representação de uma norma jurídica."""
    id: str
    texto: str
    hierarquia: NormHierarchy
    tipo: NormType = NormType.REGRA
    competencia: Optional[Competence] = None
    fundamento_constitucional: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "texto": self.texto,
            "hierarquia": self.hierarquia.name,
            "tipo": self.tipo.name,
            "competencia": self.competencia.name if self.competencia else None,
            "fundamento_constitucional": self.fundamento_constitucional,
        }


@dataclass
class LegalFact:
    """Representação de um fato jurídico relevante."""
    descricao: str
    competencia: Optional[Competence] = None

    def to_dict(self) -> Dict:
        return {
            "descricao": self.descricao,
            "competencia": self.competencia.name if self.competencia else None,
        }


@dataclass
class SubsumpionResult:
    """Resultado da subsunção."""
    conclusao: str
    aplicavel: bool
    norma_aplicada: Optional[LegalNorm] = None
    fundamentacao: List[str] = field(default_factory=list)
    antinomia_detectada: bool = False
    inconstitucionalidade: bool = False
    conflito_competencia: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "conclusao": self.conclusao,
            "aplicavel": self.aplicavel,
            "norma_aplicada": self.norma_aplicada.to_dict() if self.norma_aplicada else None,
            "fundamentacao": self.fundamentacao,
            "antinomia_detectada": self.antinomia_detectada,
            "inconstitucionalidade": self.inconstitucionalidade,
            "conflito_competencia": self.conflito_competencia,
        }


class LegalSyllogism:
    """Motor de subsunção legal (silogismo jurídico brasileiro).

    Aplica a estrutura clássica: premissa maior (norma) + premissa menor (fato) → conclusão.
    Inclui controle de hierarquia, antinomias e competência federativa.
    """

    def __init__(self):
        self.norm_registry: Dict[str, LegalNorm] = {}

    def register_norm(self, norm: LegalNorm) -> None:
        """Registra uma norma no repositório."""
        self.norm_registry[norm.id] = norm

    def register_norms(self, norms: List[LegalNorm]) -> None:
        """Registra múltiplas normas."""
        for n in norms:
            self.register_norm(n)

    def _check_hierarchy(self, normas: List[LegalNorm]) -> LegalNorm:
        """Retorna a norma hierarquicamente superior (critério hierárquico)."""
        return max(normas, key=lambda n: n.hierarquia.value)

    def _check_competence(self, norma: LegalNorm, fato: LegalFact) -> Optional[str]:
        """Verifica conflito de competência federativa."""
        if norma.competencia and fato.competencia:
            if norma.competencia == Competence.PRIVATIVA_UNIAO:
                if fato.competencia in (Competence.ESTADO, Competence.MUNICIPIO):
                    return "incompetencia_estado_municipio_materia_federal"
            if norma.competencia == Competence.UNIAO and fato.competencia == Competence.ESTADO:
                return "conflito_uniao_estado"
            if norma.competencia == Competence.ESTADO and fato.competencia == Competence.UNIAO:
                return "conflito_estado_uniao"
            if norma.competencia == Competence.CONCORRENTE:
                return None  # competência concorrente não gera conflito
        return None

    def _detect_antinomy(self, normas: List[LegalNorm]) -> Tuple[bool, Optional[str]]:
        """Detecta antinomia (conflito entre normas do mesmo nível hierárquico)."""
        if len(normas) < 2:
            return False, None
        niveis = [n.hierarquia for n in normas]
        # Se todas são do mesmo nível, há antinomia (critério cronológico ou especialidade)
        if len(set(niveis)) == 1:
            if normas[0].tipo == NormType.REGRA and normas[1].tipo == NormType.REGRA:
                return True, f"Antinomia entre normas de mesmo nível hierárquico: {normas[0].id} vs {normas[1].id}"
        return False, None

    def _check_constitutionality(self, norma: LegalNorm) -> bool:
        """Verificação simplificada de constitucionalidade.

        Retorna False se a norma infraconstitucional conflitar com a CF.
        Regra: norma de hierarquia < CF não pode conflitar com princípio constitucional.
        """
        if norma.hierarquia.value >= NormHierarchy.CONSTITUICAO_FEDERAL.value:
            return True
        # Busca se há norma constitucional que conflita
        for n in self.norm_registry.values():
            if n.hierarquia == NormHierarchy.CONSTITUICAO_FEDERAL:
                if n.tipo == NormType.PRINCIPIO and norma.fundamento_constitucional:
                    if n.id != norma.fundamento_constitucional:
                        # Verificação simplificada: norma não está fundada no princípio constitucional correto
                        return False
        return True

    def subsume(self, fato: LegalFact, normas_candidatas: Optional[List[str]] = None) -> SubsumpionResult:
        """Aplica a subsunção: fato + norma(s) → conclusão.

        Args:
            fato: O fato jurídico a ser subsumido.
            normas_candidatas: Lista de IDs de normas a considerar (None = todas).

        Returns:
            SubsumpionResult com a conclusão e fundamentação.
        """
        # Selecionar normas candidatas
        if normas_candidatas:
            normas = [self.norm_registry[nid] for nid in normas_candidatas if nid in self.norm_registry]
        else:
            normas = list(self.norm_registry.values())

        if not normas:
            return SubsumpionResult(
                conclusao="Inaplicável — nenhuma norma encontrada",
                aplicavel=False,
                fundamentacao=["Ausência de norma jurídica aplicável ao caso."]
            )

        fundamentos: List[str] = []

        # 1. Verificar antinomia
        antinomia, antinomia_msg = self._detect_antinomy(normas)
        if antinomia:
            # Tentar resolver por hierarquia primeiro
            if len(normas) > 1:
                norma_primaria = self._check_hierarchy(normas)
                fundamentos.append(f"Antinomia detectada: {antinomia_msg}")
                fundamentos.append(f"Resolvida pelo critério hierárquico: prevalece {norma_primaria.id}")
                normas = [norma_primaria]
            else:
                return SubsumpionResult(
                    conclusao="Inaplicável — antinomia insolúvel",
                    aplicavel=False,
                    antinomia_detectada=True,
                    fundamentacao=[antinomia_msg],
                )

        # 2. Verificar hierarquia (se múltiplas normas de níveis diferentes)
        if len(normas) > 1:
            norma_primaria = self._check_hierarchy(normas)
            fundamentos.append(
                f"Critério hierárquico: {norma_primaria.id} ({norma_primaria.hierarquia.name}) "
                f"prevalece sobre as demais"
            )
            normas = [norma_primaria]

        norma = normas[0]

        # 3. Verificar constitucionalidade
        if not self._check_constitutionality(norma):
            return SubsumpionResult(
                conclusao=f"Inaplicável — norma inconstitucional: {norma.id}",
                aplicavel=False,
                inconstitucionalidade=True,
                norma_aplicada=norma,
                fundamentacao=[f"A norma {norma.id} conflita com princípio constitucional e é inconstitucional."],
            )

        # 4. Verificar competência
        conflito = self._check_competence(norma, fato)
        if conflito:
            return SubsumpionResult(
                conclusao=f"Inaplicável — conflito de competência: {conflito}",
                aplicavel=False,
                norma_aplicada=norma,
                conflito_competencia=conflito,
                fundamentacao=[f"O fato ocorre em competência diversa da norma {norma.id}."],
            )

        # 5. Aplicar subsunção
        if norma.tipo == NormType.REGRA:
            conclusao = f"Aplicável — {norma.id}: {norma.texto}"
            fundamentos.append(f"Premissa Maior: {norma.texto} ({norma.id})")
            fundamentos.append(f"Premissa Menor: {fato.descricao}")
            fundamentos.append(f"Conclusão: subsume-se o fato à norma")
        elif norma.tipo == NormType.PRINCIPIO:
            conclusao = f"Aplicável em ponderação — {norma.id}: {norma.texto}"
            fundamentos.append(f"Princípio aplicável: {norma.texto} ({norma.id})")
            fundamentos.append(f"Fato relevante: {fato.descricao}")
            fundamentos.append("Exige ponderação com outros princípios colidentes")
        else:
            conclusao = f"Aplicável com interpretação — {norma.id}: {norma.texto}"
            fundamentos.append(f"Norma de conceito indeterminado: {norma.id}")
            fundamentos.append("Exige concretização pelo aplicador")

        return SubsumpionResult(
            conclusao=conclusao,
            aplicavel=True,
            norma_aplicada=norma,
            fundamentacao=fundamentos,
            antinomia_detectada=antinomia,
        )
