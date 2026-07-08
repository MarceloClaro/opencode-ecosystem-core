# -*- coding: utf-8 -*-
"""
Pacote legal — Módulo de Raciocínio Jurídico Brasileiro (SPEC-921/922/923/927)
=================================================================================
Implementa os principais métodos de argumentação e decisão jurídica
do sistema jurídico brasileiro.

Componentes:
  - LegalSyllogism: subsunção legal (silogismo: norma + fato → conclusão)
  - PrincipleBalancing: ponderação de princípios (Alexy, fórmula do peso)
  - PrecedentAnalyzer: análise de precedentes vinculantes (CPC/2015)
  - ConstitutionalInterpretation: métodos de interpretação constitucional
  - LegalArgumentScorer: scoring de argumentos jurídicos
  - DatajudClient: cliente para API pública Datajud do CNJ (SPEC-922)
  - LegalDatajudIntegration: ponte Datajud → motores de raciocínio
  - LegalAgentCard: 4 agentes jurídicos A2A (SPEC-923/AUXJURIS)
  - LegalKnowledgeBase: base de conhecimento com RAG por keywords
  - LegalDocumentSummarizer: sumarizador de documentos jurídicos
  - Specializations: perfis e agentes especialistas por ramo do direito
"""

from legal.syllogism import (
    LegalSyllogism,
    LegalNorm,
    LegalFact,
    SubsumpionResult,
    NormHierarchy,
    NormType,
    Competence,
)
from legal.balancing import (
    PrincipleBalancing,
    Principle,
    BalancingResult,
)
from legal.precedents import (
    PrecedentAnalyzer,
    Precedent,
    CaseFacts,
    PrecedentAnalysisResult,
    PrecedentType,
    BindingLevel,
)
from legal.constitutional import (
    ConstitutionalInterpretation,
    ConstitutionalNorm,
    InterpretationResult,
    InterpretationMethod,
)
from legal.argumentation import (
    LegalArgumentScorer,
    LegalArgument,
    ArgumentScoreResult,
    ScoreDetail,
)
from legal.datajud_client import (
    DatajudClient,
    DatajudProcess,
    TRIBUNAIS,
)
from legal.integration import (
    LegalDatajudIntegration,
    process_to_precedent,
    process_to_legal_fact,
    process_to_legal_argument,
)
from legal.agents import (
    LegalAgentCard,
    LEGAL_AGENTS,
    get_legal_agent,
    resolve_legal_agent,
    get_all_legal_agent_cards,
    register_legal_agents,
)
from legal.knowledge_base import (
    LegalKnowledgeBase,
    LegalDocument,
    DEFAULT_LEGAL_DOCUMENTS,
)
from legal.summarizer import (
    LegalDocumentSummarizer,
    SummaryResult,
    LegalEntities,
)
from legal.specializations import (
    LegalDomainProfile,
    LEGAL_DOMAIN_PROFILES,
    list_legal_domains,
    get_legal_domain_profile,
    route_legal_domain,
    assess_domain_coverage,
    build_domain_specialist_agent,
    route_specialist_agent,
)
from legal.benchmarks import (
    LegalBenchmarkCase,
    LEGAL_BENCHMARK_CASES,
    benchmark_router,
    evaluate_domain_answer,
    classify_domain_expertise_tier,
    run_domain_benchmark_suite,
)

__all__ = [
    # Syllogism
    "LegalSyllogism", "LegalNorm", "LegalFact", "SubsumpionResult",
    "NormHierarchy", "NormType", "Competence",
    # Balancing
    "PrincipleBalancing", "Principle", "BalancingResult",
    # Precedents
    "PrecedentAnalyzer", "Precedent", "CaseFacts", "PrecedentAnalysisResult",
    "PrecedentType", "BindingLevel",
    # Constitutional
    "ConstitutionalInterpretation", "ConstitutionalNorm", "InterpretationResult",
    "InterpretationMethod",
    # Argumentation
    "LegalArgumentScorer", "LegalArgument", "ArgumentScoreResult", "ScoreDetail",
    # Datajud
    "DatajudClient", "DatajudProcess", "TRIBUNAIS",
    # Integration
    "LegalDatajudIntegration",
    "process_to_precedent", "process_to_legal_fact", "process_to_legal_argument",
    # Agents
    "LegalAgentCard", "LEGAL_AGENTS",
    "get_legal_agent", "resolve_legal_agent", "get_all_legal_agent_cards",
    "register_legal_agents",
    # Knowledge Base
    "LegalKnowledgeBase", "LegalDocument", "DEFAULT_LEGAL_DOCUMENTS",
    # Summarizer
    "LegalDocumentSummarizer", "SummaryResult", "LegalEntities",
    # Domain specialization
    "LegalDomainProfile", "LEGAL_DOMAIN_PROFILES", "list_legal_domains",
    "get_legal_domain_profile", "route_legal_domain", "assess_domain_coverage",
    "build_domain_specialist_agent", "route_specialist_agent",
    # Benchmarks
    "LegalBenchmarkCase", "LEGAL_BENCHMARK_CASES", "benchmark_router",
    "evaluate_domain_answer", "classify_domain_expertise_tier",
    "run_domain_benchmark_suite",
]

__version__ = "1.0.0"
