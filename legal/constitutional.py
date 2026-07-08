# -*- coding: utf-8 -*-
"""
ConstitutionalInterpretation — Métodos de Interpretação Constitucional
======================================================================
Implementa os métodos hermenêuticos clássicos aplicados à Constituição
Federal de 1988, conforme a doutrina brasileira.

Métodos:
  1. Gramatical / Textual — sentido literal das palavras
  2. Histórico — contexto de criação da norma
  3. Sistemático — unidade do ordenamento
  4. Teleológico — finalidade da norma
  5. Argumentum a contrario — exclusão por ausência de previsão
  6. Argumentum a simili — analogia para casos similares
  7. Proporcionalidade — ponderação de bens jurídicos

Referências:
  - CANOTILHO, J.J. Gomes. Direito Constitucional e Teoria da Constituição (2003)
  - STRECK, Lenio. Hermenêutica Jurídica e(m) Crise (2011)
  - MENDES, Gilmar Ferreira. Curso de Direito Constitucional (2020)
  - STF, ADI 4.815 (biografias não autorizadas)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional


class InterpretationMethod(Enum):
    """Métodos de interpretação constitucional."""
    GRAMATICAL = "gramatical"
    HISTORICO = "historico"
    SISTEMATICO = "sistematico"
    TELEOLOGICO = "teleologico"
    A_CONTRARIO = "a_contrario"
    A_SIMILI = "a_simili"
    PROPORCIONALIDADE = "proporcionalidade"


@dataclass
class ConstitutionalNorm:
    """Representação de uma norma constitucional."""
    artigo: str
    capitulo: str
    texto: str
    principios_relacionados: List[str] = field(default_factory=list)
    contexto_historico: Optional[str] = None
    finalidade: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "artigo": self.artigo,
            "capitulo": self.capitulo,
            "texto": self.texto,
            "principios_relacionados": self.principios_relacionados,
            "contexto_historico": self.contexto_historico,
            "finalidade": self.finalidade,
        }


@dataclass
class InterpretationResult:
    """Resultado da interpretação constitucional."""
    metodo: InterpretationMethod
    interpretacao: str
    fundamentacao: List[str] = field(default_factory=list)
    confianca: float = 0.5

    def to_dict(self) -> Dict:
        return {
            "metodo": self.metodo.value,
            "interpretacao": self.interpretacao,
            "fundamentacao": self.fundamentacao,
            "confianca": self.confianca,
        }


class ConstitutionalInterpretation:
    """Motor de interpretação constitucional.

    Aplica múltiplos métodos hermenêuticos à normas da CF/88,
    retornando interpretações fundamentadas para cada método.
    """

    def __init__(self):
        self.norms: Dict[str, ConstitutionalNorm] = {}

    def register_norm(self, norm: ConstitutionalNorm) -> None:
        """Registra uma norma constitucional."""
        self.norms[norm.artigo] = norm

    def register_norms(self, normas: List[ConstitutionalNorm]) -> None:
        """Registra múltiplas normas."""
        for n in normas:
            self.register_norm(n)

    def interpret(self, artigo: str,
                  metodo: InterpretationMethod,
                  contexto_aplicacao: Optional[str] = None) -> InterpretationResult:
        """Aplica um método de interpretação a uma norma constitucional.

        Args:
            artigo: Artigo da CF/88 a interpretar.
            metodo: Método de interpretação a aplicar.
            contexto_aplicacao: Contexto específico de aplicação (opcional).

        Returns:
            InterpretationResult com o resultado da interpretação.
        """
        norm = self.norms.get(artigo)
        if not norm:
            return InterpretationResult(
                metodo=metodo,
                interpretacao=f"Norma não encontrada: artigo {artigo}",
                fundamentacao=[f"O artigo {artigo} não está registrado no repositório."],
                confianca=0.0,
            )

        if metodo == InterpretationMethod.GRAMATICAL:
            return self._interpret_grammatical(norm, contexto_aplicacao)
        elif metodo == InterpretationMethod.HISTORICO:
            return self._interpret_historical(norm, contexto_aplicacao)
        elif metodo == InterpretationMethod.SISTEMATICO:
            return self._interpret_systematic(norm, contexto_aplicacao)
        elif metodo == InterpretationMethod.TELEOLOGICO:
            return self._interpret_teleological(norm, contexto_aplicacao)
        elif metodo == InterpretationMethod.A_CONTRARIO:
            return self._interpret_a_contrario(norm, contexto_aplicacao)
        elif metodo == InterpretationMethod.A_SIMILI:
            return self._interpret_a_simili(norm, contexto_aplicacao)
        elif metodo == InterpretationMethod.PROPORCIONALIDADE:
            return self._interpret_proportionality(norm, contexto_aplicacao)
        else:
            return InterpretationResult(
                metodo=metodo,
                interpretacao="Método de interpretação não implementado",
                fundamentacao=[f"Método {metodo.value} não está implementado."],
                confianca=0.0,
            )

    def _interpret_grammatical(self, norm: ConstitutionalNorm,
                               contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação gramatical/textual: sentido literal do texto."""
        fundamentos = [
            f"Método: Gramatical (textual)",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
        ]
        if contexto:
            fundamentos.append(f"Contexto de aplicação: {contexto}")

        # Análise textual simples
        palavras = norm.texto.split()
        fundamentos.append(
            f"Interpretação literal: o texto do art. {norm.artigo} "
            f"estabelece {' '.join(palavras[:10])}{'...' if len(palavras) > 10 else ''}"
        )
        fundamentos.append("A interpretação gramatical é o ponto de partida da hermenêutica constitucional.")

        interpretacao = f"Pela interpretação gramatical, o art. {norm.artigo} dispõe que {norm.texto.lower().rstrip('.')}."

        return InterpretationResult(
            metodo=InterpretationMethod.GRAMATICAL,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.8,
        )

    def _interpret_historical(self, norm: ConstitutionalNorm,
                              contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação histórica: contexto de criação da norma."""
        fundamentos = [
            f"Método: Histórico",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
        ]
        if norm.contexto_historico:
            fundamentos.append(f"Contexto histórico: {norm.contexto_historico}")
        else:
            fundamentos.append("Contexto histórico não disponível no repositório.")
        if contexto:
            fundamentos.append(f"Contexto atual de aplicação: {contexto}")

        interpretacao = (
            f"A interpretação histórica do art. {norm.artigo} revela "
            f"a intenção do constituinte originário/derivado ao positivá-lo."
        )
        if norm.contexto_historico:
            interpretacao += f" O contexto de criação indica: {norm.contexto_historico}"

        return InterpretationResult(
            metodo=InterpretationMethod.HISTORICO,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.6,
        )

    def _interpret_systematic(self, norm: ConstitutionalNorm,
                              contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação sistemática: unidade do ordenamento."""
        fundamentos = [
            f"Método: Sistemático",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
            f"Princípios relacionados: {', '.join(norm.principios_relacionados) if norm.principios_relacionados else 'não especificados'}",
        ]
        if contexto:
            fundamentos.append(f"Contexto de aplicação: {contexto}")

        fundamentos.append(
            "A interpretação sistemática considera que o ordenamento jurídico "
            "é uma unidade coerente e que a norma deve ser interpretada em "
            "conjunto com os demais dispositivos constitucionais."
        )

        interpretacao = (
            f"Pela interpretação sistemática, o art. {norm.artigo} deve ser "
            f"lido em conjunto com os princípios fundamentais da CF/88 "
            f"(arts. 1º a 4º) e com os demais dispositivos do {norm.capitulo}."
        )

        return InterpretationResult(
            metodo=InterpretationMethod.SISTEMATICO,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.7,
        )

    def _interpret_teleological(self, norm: ConstitutionalNorm,
                                contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação teleológica: finalidade da norma."""
        fundamentos = [
            f"Método: Teleológico (finalístico)",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
        ]
        if norm.finalidade:
            fundamentos.append(f"Finalidade: {norm.finalidade}")
        else:
            fundamentos.append("Finalidade não especificada no repositório.")
        if contexto:
            fundamentos.append(f"Contexto de aplicação: {contexto}")

        fundamentos.append(
            "A interpretação teleológica busca a finalidade social da norma "
            "e os valores que ela protege (ratio legis)."
        )

        interpretacao = (
            f"A finalidade do art. {norm.artigo} é "
            f"{norm.finalidade if norm.finalidade else 'proteger o bem jurídico nele enunciado'}, "
            f"devendo o intérprete buscar a máxima efetividade da norma constitucional."
        )

        return InterpretationResult(
            metodo=InterpretationMethod.TELEOLOGICO,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.7,
        )

    def _interpret_a_contrario(self, norm: ConstitutionalNorm,
                               contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação a contrario: exclusão por ausência de previsão."""
        fundamentos = [
            f"Método: Argumentum a contrario",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
        ]
        if contexto:
            fundamentos.append(f"Contexto de aplicação: {contexto}")

        fundamentos.append(
            "Pelo argumento a contrario, se a Constituição previu expressamente "
            "determinada situação, exclui-se a aplicação a situações não previstas. "
            "Onde o legislador expressamente distinguiu, não cabe ao intérprete igualar."
        )

        interpretacao = (
            f"Pelo argumento a contrario, o art. {norm.artigo} aplica-se "
            f"exclusivamente às situações nele expressamente previstas, "
            f"não podendo ser estendido a casos não contemplados pelo texto constitucional."
        )

        return InterpretationResult(
            metodo=InterpretationMethod.A_CONTRARIO,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.6,
        )

    def _interpret_a_simili(self, norm: ConstitutionalNorm,
                            contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação a simili (analogia): aplicação a casos similares."""
        fundamentos = [
            f"Método: Argumentum a simili (analogia)",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
        ]
        if contexto:
            fundamentos.append(f"Contexto de aplicação: {contexto}")

        fundamentos.append(
            "Pelo argumento a simili, onde há a mesma razão jurídica, "
            "aplica-se a mesma norma. A analogia é admitida no direito constitucional "
            "quando há identidade substancial entre a situação prevista e a não prevista."
        )

        interpretacao = (
            f"Pelo argumento a simili, o art. {norm.artigo} pode ser aplicado "
            f"analogicamente a situações que apresentem identidade de razão jurídica "
            f"(ubi eadem ratio, ibi eadem dispositio)."
        )

        return InterpretationResult(
            metodo=InterpretationMethod.A_SIMILI,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.5,
        )

    def _interpret_proportionality(self, norm: ConstitutionalNorm,
                                   contexto: Optional[str] = None) -> InterpretationResult:
        """Interpretação pela proporcionalidade: ponderação de bens."""
        fundamentos = [
            f"Método: Proporcionalidade",
            f"Artigo {norm.artigo} ({norm.capitulo}):",
            f"Texto: \"{norm.texto}\"",
        ]
        if contexto:
            fundamentos.append(f"Contexto de aplicação: {contexto}")

        fundamentos.append(
            "A proporcionalidade impõe a aplicação dos subtestes de "
            "adequação, necessidade e proporcionalidade em sentido estrito "
            "para resolver colisões entre princípios constitucionais."
        )

        interpretacao = (
            f"Aplica-se o princípio da proporcionalidade ao art. {norm.artigo} "
            f"para ponderá-lo com outros princípios constitucionais colidentes, "
            f"avaliando adequação, necessidade e proporcionalidade estrita da medida."
        )

        return InterpretationResult(
            metodo=InterpretationMethod.PROPORCIONALIDADE,
            interpretacao=interpretacao,
            fundamentacao=fundamentos,
            confianca=0.6,
        )

    def multi_interpret(self, artigo: str,
                        metodos: Optional[List[InterpretationMethod]] = None,
                        contexto_aplicacao: Optional[str] = None) -> List[InterpretationResult]:
        """Aplica múltiplos métodos de interpretação e retorna todos os resultados.

        Args:
            artigo: Artigo da CF/88 a interpretar.
            metodos: Lista de métodos. Se None, aplica todos.
            contexto_aplicacao: Contexto específico (opcional).

        Returns:
            Lista de InterpretationResult, um para cada método.
        """
        if metodos is None:
            metodos = list(InterpretationMethod)

        resultados = []
        for metodo in metodos:
            resultado = self.interpret(artigo, metodo, contexto_aplicacao)
            resultados.append(resultado)
        return resultados

    def generate_opinion(self, artigo: str,
                         contexto_aplicacao: Optional[str] = None) -> Dict:
        """Gera um parecer interpretativo completo usando todos os métodos.

        Retorna um dicionário com interpretações por método e uma síntese final.
        """
        resultados = self.multi_interpret(artigo, contexto_aplicacao=contexto_aplicacao)

        # Síntese: seleciona a interpretação de maior confiança
        melhor_resultado = max(resultados, key=lambda r: r.confianca)

        return {
            "artigo": artigo,
            "contexto": contexto_aplicacao,
            "interpretacoes": {r.metodo.value: r.interpretacao for r in resultados},
            "fundamentacoes": {r.metodo.value: r.fundamentacao for r in resultados},
            "sintese": melhor_resultado.interpretacao,
            "metodo_prevalente": melhor_resultado.metodo.value,
            "confianca": melhor_resultado.confianca,
        }
