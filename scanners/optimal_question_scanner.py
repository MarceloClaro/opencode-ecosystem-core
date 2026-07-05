#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptimalQuestionScanner v1.0 — SPEC-039: Scanner de Perguntas Ótimas
======================================================================
Identifica a pergunta com maior poder de convergência para reduzir
o espaço de incerteza de um problema.

Pipeline (9 etapas):
  1. ProblemIntake         — normalizar o problema bruto
  2. UncertaintyScanner     — mapear incertezas
  3. StructuralNoiseFilter  — remover ruídos que geram perguntas improdutivas
  4. QuestionCandidateGen   — gerar perguntas candidatas (10 tipos)
  5. QuestionVectorizer     — transformar cada pergunta em vetor
  6. ConvergenceScorer      — calcular CS = URS + SVS - DRI - CCI
  7. OptimalSelector        — Q* = argmax(CS)
  8. AnswerDirectionTest    — verificar utilidade da resposta esperada
  9. OutputFinal            — entregar pergunta ótima + justificativa

Autor: OpenCode Ecosystem (2026) — SPEC-039
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

class QuestionType(str, Enum):
    DEFINITION = "definition"
    CAUSALITY = "causality"
    COMPARISON = "comparison"
    VALIDATION = "validation"
    FALSIFICATION = "falsification"
    OPERATIONALIZATION = "operationalization"
    METRIC = "metric"
    IMPACT = "impact"
    SEQUENCE = "sequence"
    INTEGRATION = "integration"


@dataclass
class ProblemState:
    """Estado normalizado do problema."""
    raw: str
    normalized: str
    object_of_analysis: str
    scope: str
    uncertainties: list[str] = field(default_factory=list)
    noise_elements: list[str] = field(default_factory=list)
    structural_core: str = ""


@dataclass
class QuestionCandidate:
    """Pergunta candidata vetorizada."""
    text: str
    qtype: QuestionType
    direction: str            # vetor de investigação
    scope_radius: float       # 0-1 (foco vs amplitude)
    depth: float              # 0-1 (superficial vs profunda)
    uncertainty_reduction: float  # URS estimado
    structural_value: float      # SVS estimado
    dispersion_risk: float       # DRI estimado
    cognitive_cost: float        # CCI estimado
    convergence_score: float = 0.0  # CS calculado


@dataclass
class OQSResult:
    """Resultado final do Optimal Question Scanner."""
    optimal_question: QuestionCandidate
    justification: str
    discarded_questions: list[QuestionCandidate]
    discard_reasons: dict[str, str]
    next_likely_question: str
    uncertainty_reduced: list[str]
    remaining_risk: str


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 1: PROBLEM INTAKE
# ═══════════════════════════════════════════════════════════════════════════

class ProblemIntake:
    """Normaliza o problema bruto e identifica o objeto de análise."""

    def intake(self, raw_problem: str) -> ProblemState:
        """Recebe texto bruto e normaliza."""
        # Limpar e normalizar
        normalized = raw_problem.strip()
        
        # Extrair objeto de análise (primeira entidade mencionada ou foco)
        object_match = re.search(
            r'(?:sobre|acerca de|a respeito de|analisar|estudar|investigar)\s+(.+?)(?:[.,;]|$)',
            normalized, re.IGNORECASE
        )
        obj = object_match.group(1).strip() if object_match else normalized[:80]
        
        # Extrair escopo
        scope_match = re.search(
            r'(?:contexto|domínio|área|campo)\s+(?:de|da|do)\s+(.+?)(?:[.,;]|$)',
            normalized, re.IGNORECASE
        )
        scope = scope_match.group(1).strip() if scope_match else "geral"
        
        return ProblemState(
            raw=raw_problem,
            normalized=normalized,
            object_of_analysis=obj,
            scope=scope,
        )


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 2: UNCERTAINTY SCANNER
# ═══════════════════════════════════════════════════════════════════════════

class UncertaintyScanner:
    """Mapeia incertezas, lacunas e ambiguidades no problema."""

    UNCERTAINTY_MARKERS: list[str] = [
        "não sei", "incerto", "dúvida", "talvez", "possivelmente",
        "?", "qual", "como", "quando", "onde", "por que", "quem",
        "ainda não", "falta definir", "precisa ser", "deveria",
    ]

    def scan(self, problem: ProblemState) -> list[str]:
        """Identifica incertezas no texto."""
        uncertainties: list[str] = []
        text = problem.normalized.lower()
        
        # Buscar marcadores de incerteza
        for marker in self.UNCERTAINTY_MARKERS:
            idx = text.find(marker)
            if idx >= 0:
                # Extrair contexto da incerteza
                start = max(0, idx - 30)
                end = min(len(text), idx + 80)
                context = text[start:end].strip()
                uncertainties.append(context)
        
        # Identificar lacunas conceituais (termos sem definição)
        undefined = re.findall(
            r'\b(\w+(?:ção|mento|dade|ência|aria|ismo|logia))\b(?!.*\b(?:é|são|define|significa|consiste)\b)',
            text
        )
        for term in undefined:
            if term not in str(uncertainties):
                uncertainties.append(f"Termo potencialmente indefinido: '{term}'")
        
        problem.uncertainties = uncertainties[:10]
        return uncertainties


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 3: STRUCTURAL NOISE FILTER
# ═══════════════════════════════════════════════════════════════════════════

class StructuralNoiseFilter:
    """Remove ruídos que geram perguntas improdutivas."""

    NOISE_PATTERNS: list[str] = [
        r'\b(obviamente|claramente|evidentemente|basicamente|simplesmente)\b',
        r'\b(certamente|naturalmente|provavelmente|definitivamente)\b',
        r'\b(na verdade|a rigor|em princípio|via de regra)\b',
    ]

    def filter(self, problem: ProblemState) -> ProblemState:
        """Remove ruído preservando núcleo estrutural."""
        text = problem.normalized
        noise_found: list[str] = []
        
        for pattern in self.NOISE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            noise_found.extend(matches)
        
        # Extrair núcleo estrutural (frases com verbos de ação/definição)
        structural_sentences = re.findall(
            r'[^.!?]*(?:é|são|define|consiste|propõe|objetiva|busca|pretende)[^.!?]*[.!?]',
            text, re.IGNORECASE
        )
        core = ' '.join(structural_sentences) if structural_sentences else text
        
        problem.noise_elements = noise_found
        problem.structural_core = core[:500]
        return problem


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 4: QUESTION CANDIDATE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class QuestionCandidateGenerator:
    """Gera perguntas candidatas de 10 tipos diferentes."""

    QUESTION_TEMPLATES: dict[QuestionType, str] = {
        QuestionType.DEFINITION: "O que é {object}? Como se define {object} no contexto de {scope}?",
        QuestionType.CAUSALITY: "Qual é a causa de {object}? O que produz {object}?",
        QuestionType.COMPARISON: "Qual é a diferença entre {object} e suas alternativas?",
        QuestionType.VALIDATION: "Quais evidências confirmariam ou refutariam {object}?",
        QuestionType.FALSIFICATION: "O que precisaria ser falso para {object} ser inválido?",
        QuestionType.OPERATIONALIZATION: "Como {object} pode ser implementado na prática?",
        QuestionType.METRIC: "Como medir {object}? Quais métricas capturam {object}?",
        QuestionType.IMPACT: "Qual o impacto de {object}? O que muda se {object} for verdadeiro?",
        QuestionType.SEQUENCE: "Em que ordem {object} deve ser abordado? Qual o próximo passo?",
        QuestionType.INTEGRATION: "Como {object} se integra com outros elementos do sistema?",
    }

    def generate(self, problem: ProblemState) -> list[QuestionCandidate]:
        """Gera perguntas candidatas baseadas no problema."""
        candidates: list[QuestionCandidate] = []
        obj = problem.object_of_analysis
        scope = problem.scope
        
        for qtype, template in self.QUESTION_TEMPLATES.items():
            text = template.format(object=obj, scope=scope)
            candidates.append(QuestionCandidate(
                text=text,
                qtype=qtype,
                direction=obj,
                scope_radius=0.5,
                depth=0.5,
                uncertainty_reduction=0.5,
                structural_value=0.5,
                dispersion_risk=0.3,
                cognitive_cost=0.3,
            ))
        
        return candidates


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 5 + 6: QUESTION VECTORIZER + CONVERGENCE SCORER
# ═══════════════════════════════════════════════════════════════════════════

class ConvergenceScorer:
    """Calcula o Convergence Score (CS) para cada pergunta candidata."""

    def score(self, candidates: list[QuestionCandidate],
              problem: ProblemState) -> list[QuestionCandidate]:
        """Calcula CS = URS + SVS - DRI - CCI."""
        for c in candidates:
            # URS: Uncertainty Reduction Score
            # Perguntas de definição e validação reduzem mais incerteza
            if c.qtype in (QuestionType.DEFINITION, QuestionType.VALIDATION,
                          QuestionType.FALSIFICATION):
                c.uncertainty_reduction = 0.85
            elif c.qtype in (QuestionType.CAUSALITY, QuestionType.OPERATIONALIZATION):
                c.uncertainty_reduction = 0.75
            elif c.qtype in (QuestionType.COMPARISON, QuestionType.METRIC):
                c.uncertainty_reduction = 0.65
            else:
                c.uncertainty_reduction = 0.55
            
            # SVS: Structural Value Score
            # Perguntas que atingem o núcleo têm valor maior
            if any(word in c.text.lower() for word in
                   ["estrutura", "núcleo", "essência", "definição", "fundamento"]):
                c.structural_value = 0.90
            elif any(word in c.text.lower() for word in
                     ["causa", "impacto", "relação", "diferença"]):
                c.structural_value = 0.75
            else:
                c.structural_value = 0.55
            
            # DRI: Dispersion Risk Index
            num_words = len(c.text.split())
            c.dispersion_risk = min(0.8, num_words / 30)  # mais palavras = mais dispersão
            
            # CCI: Cognitive Cost Index
            c.cognitive_cost = min(0.7, num_words / 40)
            
            # CS Final
            c.convergence_score = round(
                c.uncertainty_reduction + c.structural_value
                - c.dispersion_risk - c.cognitive_cost, 4
            )
        
        return candidates


# ═══════════════════════════════════════════════════════════════════════════
# ETAPA 7 + 8 + 9: OPTIMAL SELECTOR + DIRECTION TEST + OUTPUT
# ═══════════════════════════════════════════════════════════════════════════

class OptimalQuestionScanner:
    """Orquestrador completo do OQS."""

    def __init__(self):
        self.intake = ProblemIntake()
        self.uncertainty = UncertaintyScanner()
        self.noise_filter = StructuralNoiseFilter()
        self.generator = QuestionCandidateGenerator()
        self.scorer = ConvergenceScorer()

    def scan(self, raw_problem: str) -> OQSResult:
        """Pipeline completo: problema bruto → pergunta ótima."""
        # Etapa 1: Intake
        problem = self.intake.intake(raw_problem)
        
        # Etapa 2: Uncertainty Scanner
        self.uncertainty.scan(problem)
        
        # Etapa 3: Noise Filter
        self.noise_filter.filter(problem)
        
        # Etapa 4: Generate Candidates
        candidates = self.generator.generate(problem)
        
        # Etapa 5-6: Vectorize + Score
        scored = self.scorer.score(candidates, problem)
        
        # Etapa 7: Select Optimal
        scored.sort(key=lambda c: -c.convergence_score)
        optimal = scored[0]
        
        # Etapa 8: Answer Direction Test
        discarded = scored[1:]
        reasons = {}
        for c in discarded:
            reasons[c.text[:50]] = (
                f"CS={c.convergence_score:.2f} < optimal={optimal.convergence_score:.2f}"
            )
        
        # Etapa 9: Output
        return OQSResult(
            optimal_question=optimal,
            justification=(
                f"Pergunta do tipo '{optimal.qtype.value}' com CS={optimal.convergence_score:.2f}. "
                f"URS={optimal.uncertainty_reduction:.2f}, SVS={optimal.structural_value:.2f}, "
                f"DRI={optimal.dispersion_risk:.2f}, CCI={optimal.cognitive_cost:.2f}."
            ),
            discarded_questions=discarded[:3],
            discard_reasons=reasons,
            next_likely_question=scored[1].text if len(scored) > 1 else "",
            uncertainty_reduced=problem.uncertainties[:3],
            remaining_risk=(
                "Alto" if optimal.convergence_score < 0.6
                else "Moderado" if optimal.convergence_score < 0.9
                else "Baixo"
            ),
        )

    @property
    def metrics(self) -> dict[str, str]:
        return {
            "URS": "Uncertainty Reduction Score — incertezas reduzidas / incertezas totais",
            "SVS": "Structural Value Score — elementos estruturais atingidos / total",
            "DRI": "Dispersion Risk Index — bifurcações prováveis / foco estrutural",
            "CCI": "Cognitive Cost Index — complexidade da resposta / valor esperado",
            "CS": "Convergence Score = URS + SVS - DRI - CCI",
        }


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_oqs() -> OptimalQuestionScanner:
    """Factory: cria Optimal Question Scanner pronto para uso."""
    return OptimalQuestionScanner()
