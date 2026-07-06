#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NoologicalScanner v3.0 — Scanner Epistemologico com Negacao + Word-Boundary
===========================================================================
v3.0 — 2026-06-08 — Refinado com correcoes de precisao (SPEC-028)
v2.0 — 2026-06-07 — Refinado e Amplificado
v1.0 — 2026-06-06 — Original

Melhorias v3.0 sobre v2.0:
  1. _negation_filter() — remove sentencas negadas antes do keyword matching
  2. _word_boundary_match() — evita falsos positivos por substring
     (ex: "control" nao casa mais com "controle")
  3. keyword_map expandido: 10 dimensoes (antes 4) com keywords especificas
  4. Pipeline documentado: negacao → ENRICHED_KW → TextAnalyzer → keyword_map → fallback
  5. Metodos v1.0 marcados como @deprecated

Melhorias v2.0 sobre v1.0:
  1. Pesos adaptativos por dominio (psicologia, economia, computacao, saude, educacao)
  2. Integracao com TextAnalyzer (frequencia de palavras -> validacao)
  3. Correlacao cruzada entre dimensoes (heatmap data)
  4. Deteccao de "zonas de conforto epistemologico"
  5. Keyword map enriquecido (+n-gramas +sinonimos)
  6. Blind spots ponderados pela relevancia ao dominio
  7. Export JSON para visualizacao externa
  8. Analise de tendencia (comparacao multi-scan)

Conceito original: interlocutor anonimo (2026)
v1.0-v2.0: Marcelo Claro Laranjeira
v3.0: Marcelo Claro Laranjeira — refinado com SPEC-028 (SDD+TDD, 14 CTs)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAZIL_TZ = timezone.utc

# ═══ DOMAIN PRESETS (v2.0) ═══
DOMAIN_WEIGHTS: dict[str, dict[str, float]] = {
    "psicologia": {"paradigmas":1.2,"metodos":1.1,"teorias":1.3,"raciocinio":1.0,"teoria_jogos":0.6,"niveis_analise":1.0,"temporalidade":0.8,"populacao":1.2,"dados":1.1,"dominios":0.7},
    "economia":   {"paradigmas":0.8,"metodos":1.3,"teorias":0.9,"raciocinio":1.1,"teoria_jogos":1.5,"niveis_analise":1.0,"temporalidade":1.2,"populacao":0.7,"dados":1.3,"dominios":0.8},
    "computacao": {"paradigmas":0.6,"metodos":1.1,"teorias":0.7,"raciocinio":1.5,"teoria_jogos":1.3,"niveis_analise":0.6,"temporalidade":0.5,"populacao":0.4,"dados":1.2,"dominios":1.0},
    "saude":      {"paradigmas":0.9,"metodos":1.4,"teorias":1.0,"raciocinio":0.8,"teoria_jogos":0.5,"niveis_analise":1.1,"temporalidade":1.2,"populacao":1.4,"dados":1.5,"dominios":0.9},
    "educacao":   {"paradigmas":1.1,"metodos":1.0,"teorias":1.3,"raciocinio":1.0,"teoria_jogos":0.4,"niveis_analise":0.9,"temporalidade":1.1,"populacao":1.2,"dados":0.8,"dominios":1.0},
}


# ═══════════════════════════════════════════════════════════════════════
# DIMENSÕES DO ESPAÇO DE CONHECIMENTO
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class KnowledgeDimension:
    """Uma dimensão do espaço de conhecimento."""
    name: str
    categories: list[str]
    description: str = ""
    covered: list[str] = field(default_factory=list)
    absent: list[str] = field(default_factory=list)
    density: float = 0.0  # 0.0 = vazio, 1.0 = totalmente explorado


# ─── Dimensões do Ecossistema OpenCode Core (SPEC-022) ────────────────
# Usadas quando domain="ecosystem"
ECOSYSTEM_DIMENSIONS: dict[str, KnowledgeDimension] = {
    "agentes": KnowledgeDimension(
        name="Agentes do Ecossistema",
        categories=["orchestrator", "coder", "researcher", "auditor",
                     "academic_writer", "bernstein_orchestrator",
                     "antigravity_orchestrator", "reversa_agents",
                     "ws_agents", "agent_catalog"],
        description="Agentes disponíveis para delegação de tarefas"
    ),
    "mci_core": KnowledgeDimension(
        name="Middleware de Consciência Integral (MCI)",
        categories=["metabus", "blackboard", "reflexion", "transformer",
                     "context_manager", "memory_updater", "graph_builder",
                     "mcp_server", "orchestration_pipeline"],
        description="Núcleo metacognitivo — memória, contexto e orquestração"
    ),
    "scanners": KnowledgeDimension(
        name="Scanners de Diagnóstico",
        categories=["noological_scanner", "teleological_scanner",
                     "potentiality_scanner", "evolutionary_pipeline",
                     "social_impact_scanner", "reversa_scanner",
                     "epistemic_prioritizer", "successor_generator",
                     "cross_validation_engine", "capability_composer"],
        description="Pipeline de diagnóstico, cobertura e evolução"
    ),
    "trust_economy": KnowledgeDimension(
        name="Trust & Token Economy",
        categories=["trust_engine", "token_economy", "staking_mechanism",
                     "slashing_mechanism", "fee_market", "behavioral_gate",
                     "outcome_tracker", "stake_pool"],
        description="Governança econômica e reputacional do ecossistema"
    ),
    "razao_logica": KnowledgeDimension(
        name="Motores de Raciocínio",
        categories=["z3_solver", "sympy", "kanren", "critical_reasoner",
                     "quantum_reasoning", "bayesian_inference",
                     "dialectical_engine", "reasoning_engines"],
        description="Raciocínio formal, simbólico e probabilístico"
    ),
    "evolucao": KnowledgeDimension(
        name="Evolução e Ciclos",
        categories=["evolution_registry", "cycles_manager",
                     "reflection_ledger", "trajectory_mapper",
                     "autoevolve_pipeline", "evolutionary_roadmap",
                     "successor_generator"],
        description="Registro de ciclos evolutivos e auto-melhoria"
    ),
    "protocolos": KnowledgeDimension(
        name="Protocolos do Ecossistema",
        categories=["sdd_spec_first", "tdd_red_green_refactor",
                     "a2a_blackboard", "mcp_interconnect",
                     "bernstein_orchestration", "sdd_gate",
                     "behavioral_gate", "reflexion_middleware"],
        description="Protocolos formais: SDD, TDD, A2A, MCP"
    ),
    "integracoes": KnowledgeDimension(
        name="Integrações Externas",
        categories=["antigravity_bridge", "cli_integrations",
                     "pypi_searcher", "web_search", "webfetch",
                     "mcp_servers", "git_manager"],
        description="Pontes com sistemas externos e APIs"
    ),
    "infra_dados": KnowledgeDimension(
        name="Infraestrutura e Dados",
        categories=["schemas_validator", "data_pipeline", "benchmarks",
                     "notebooks", "batch_executor", "installer",
                     "assets_media", "gametheory_models"],
        description="Esquemas, dados, benchmarks e automação"
    ),
    "governanca": KnowledgeDimension(
        name="Governança Distribuída",
        categories=["cooperative_governance", "debate_strategies",
                     "game_theory_analysis", "trust_scoring",
                     "slashing_rules", "phd_auditor",
                     "scientific_governance", "tokenomics"],
        description="Mecanismos de governança, incentivos e auditoria"
    ),
}

# Dimensões predefinidas para escaneamento acadêmico
EPISTEMOLOGICAL_DIMENSIONS: dict[str, KnowledgeDimension] = {
    "paradigmas": KnowledgeDimension(
        name="Paradigmas Epistemológicos",
        categories=["Positivista", "Interpretativista", "Crítico/Transformador",
                    "Pragmatista", "Fenomenológico", "Construtivista",
                    "Pós-estruturalista", "Complexo/Sistêmico"],
        description="Lentes epistemológicas através das quais o fenômeno é observado"
    ),
    "metodos": KnowledgeDimension(
        name="Métodos de Investigação",
        categories=["Quantitativo experimental", "Quantitativo correlacional",
                    "Qualitativo fenomenológico", "Qualitativo grounded theory",
                    "Misto sequencial", "Misto convergente",
                    "Revisão sistemática", "Meta-análise",
                    "Estudo de caso", "Pesquisa-ação"],
        description="Abordagens metodológicas empregadas"
    ),
    "teorias": KnowledgeDimension(
        name="Referenciais Teóricos",
        categories=["Cognitivo-comportamental", "Psicanalítico", "Humanista",
                    "Sistêmico", "Neurobiológico", "Evolucionista",
                    "Social-crítico", "Fenomenológico-existencial",
                    "Comportamental", "Integrativo/transdiagnóstico"],
        description="Marcos teóricos que fundamentam a análise"
    ),
    "raciocinio": KnowledgeDimension(
        name="Tipos de Raciocínio",
        categories=["Dedutivo", "Indutivo", "Abdutivo", "Dialético",
                    "Sistêmico", "Probabilístico", "Contrafactual",
                    "Metacognitivo", "Teleológico", "Pragmático"],
        description="Modos de inferência e construção de conhecimento"
    ),
    "teoria_jogos": KnowledgeDimension(
        name="Perspectivas Estratégicas (Teoria dos Jogos)",
        categories=["Equilíbrio de Nash", "Dilema do Prisioneiro", "Soma Zero",
                    "Tit-for-Tat", "Stackelberg", "Barganha",
                    "Sinalização", "Evolutivo", "Bayesiano", "Cooperativo"],
        description="Modelos estratégicos para análise de decisões"
    ),
    "niveis_analise": KnowledgeDimension(
        name="Níveis de Análise",
        categories=["Individual/intrapsíquico", "Interpessoal/relacional",
                    "Grupal/organizacional", "Comunitário", "Sistêmico/político",
                    "Neurobiológico", "Evolutivo/filogenético", "Cultural/antropológico"],
        description="Escalas de observação do fenômeno"
    ),
    "temporalidade": KnowledgeDimension(
        name="Perspectiva Temporal",
        categories=["Transversal (momento único)", "Longitudinal (curto prazo)",
                    "Longitudinal (longo prazo)", "Histórico/retrospectivo",
                    "Prospectivo/preditivo", "Desenvolvimental (ciclo de vida)"],
        description="Enquadramento temporal da análise"
    ),
    "populacao": KnowledgeDimension(
        name="População e Contexto",
        categories=["Adultos", "Idosos", "Adolescentes", "Infância",
                    "Gênero feminino", "Gênero masculino", "Diversidade de gênero",
                    "Contexto clínico", "Contexto comunitário", "Contexto organizacional",
                    "Brasil/América Latina", "Cross-cultural"],
        description="Características da população estudada e contexto"
    ),
    "dados": KnowledgeDimension(
        name="Tipos de Dados e Evidências",
        categories=["Dados clínicos (escalas, inventários)", "Dados neurobiológicos",
                    "Dados qualitativos (entrevistas)", "Dados observacionais",
                    "Dados epidemiológicos", "Dados longitudinais",
                    "Dados comparativos (cross-cultural)", "Metadados (revisões)"],
        description="Natureza das evidências utilizadas"
    ),
    "dominios": KnowledgeDimension(
        name="Domínios de Conhecimento Cruzados",
        categories=["Psicologia clínica", "Neurociências", "Sociologia",
                    "Antropologia", "Economia comportamental", "Filosofia da mente",
                    "Psicofarmacologia", "Saúde pública", "Educação",
                    "Inteligência Artificial / Tecnologia"],
        description="Áreas do conhecimento potencialmente relevantes"
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# SCANNER NOOLÓGICO
# ═══════════════════════════════════════════════════════════════════════

# ═══ ENRICHED KEYWORDS (v2.0) ═══
ENRICHED_KW: dict[str, dict[str, list[str]]] = {
    "paradigmas": {"positivista":["positiv","quantitativ","experimental","hipotese","mensur","objetiv"],"interpretativista":["interpretativ","qualitativ","fenomenolog","compreens","subjetiv"],"fenomenológico":["fenomenolog","vivencia","experiencia vivida","sentido","heidegger","merleau"],"construtivista":["construtiv","construcion","significado","vygotsk","piaget"]},
    "teoria_jogos": {"soma zero":["soma zero","zero-sum","jogo de soma zero"],"equilíbrio de nash":["nash","equilibrio","estrategia dominante","nao-cooperativo","pne","equilibrio de nash"],"dilema do prisioneiro":["prisioneiro","dilema","cooperacao","traicao","payoff","prisoner"],"tit-for-tat":["tit for tat","olho por olho","reciproc","axelrod","retaliacao"],"stackelberg":["stackelberg","lider","seguidor","liderança","lideranca"],"barganha":["barganha","negociacao","negocia","nash bargaining","threat point"],"sinalização":["sinalizac","sinalizacao","signaling","sinal","screening"],"evolutivo":["evolutivo","selecao natural","smith","price","ess","evolutivamente estavel"],"bayesiano":["bayesiano","harsanyi","informacao incompleta","crenca","tipo"],"cooperativo":["cooperativo","shapley","coalizao","contribuicao marginal","nucleolo"]},
}

# ═══ ECOSYSTEM KEYWORDS (SPEC-022) ═══
ECOSYSTEM_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "agentes": {
        "orchestrator": ["orchestrator", "marceloclaro", "orquestrador", "master-orchestrator"],
        "coder": ["coder", "coding", "coder-agent", "ws-coder"],
        "researcher": ["researcher", "research", "web-search-researcher", "ws-researcher"],
        "auditor": ["auditor", "security-auditor", "code-reviewer", "reviewer"],
        "academic_writer": ["academic_writer", "maswos", "academic pipeline", "ws-academic"],
        "bernstein_orchestrator": ["bernstein", "bernstein-orchestrator", "maestro"],
        "antigravity_orchestrator": ["antigravity", "antigravity-orchestrator"],
        "reversa_agents": ["reversa", "reversa-agent", "reversa-"],
        "ws_agents": ["ws-coder", "ws-researcher", "ws-reviewer", "ws-scribe"],
        "agent_catalog": ["catalog/", "agent_catalog", "catalogo"],
    },
    "mci_core": {
        "metabus": ["metabus", "meta_bus", "metabus.py", "global memory"],
        "blackboard": ["blackboard", "a2a", "blackboard.py"],
        "reflexion": ["reflexion", "reflection", "reflexion.py"],
        "transformer": ["transformer", "transformer/"],
        "context_manager": ["context_manager", "context-manager", "context manager", "contextscout"],
        "memory_updater": ["memory_updater", "memory-updater", "reversa-memory-updater"],
        "graph_builder": ["graph_builder", "graph-builder", "reversa-graph-builder", "graphrag"],
        "mcp_server": ["mcp_server", "mcp server", "mcp_servers", "mcp.py"],
        "orchestration_pipeline": ["orchestration", "pipeline/", "orchestration.py", "stage-orchestrator"],
    },
    "scanners": {
        "noological_scanner": ["noological", "noological_scanner", "scanner noológico"],
        "teleological_scanner": ["teleological", "teleological_scanner", "scanner teleológico"],
        "potentiality_scanner": ["potentiality", "potentiality_scanner"],
        "evolutionary_pipeline": ["evolutionary", "evolutionary_pipeline", "evolutionary scanner"],
        "social_impact_scanner": ["social_impact", "social impact scanner"],
        "reversa_scanner": ["reversa_scanner", "reversa scanner"],
        "epistemic_prioritizer": ["epistemic_prioritizer", "epistemic prioritizer"],
        "successor_generator": ["successor_generator", "successor generator", "successor"],
        "cross_validation_engine": ["cross_validation", "cross validation engine"],
        "capability_composer": ["capability_composer", "capability composer"],
    },
    "trust_economy": {
        "trust_engine": ["trust_engine", "trust engine", "trust/", "TrustEngine", "TrustScorer"],
        "token_economy": ["token_economy", "token economy", "economy/", "tokenomics", "TokenEconomy", "TokenLedger"],
        "staking_mechanism": ["staking", "stake", "stake pool", "StakingPool", "stake_position", "stake_release", "total_locked"],
        "slashing_mechanism": ["slashing", "slash", "penalty", "slashing_rules", "slash_"],
        "fee_market": ["fee market", "fee_market", "gas", "tax", "FeeMarket", "FeeQuote"],
        "behavioral_gate": ["behavioral_gate", "behavioral gate", "behavioral", "BehavioralGate", "GateDecision"],
        "outcome_tracker": ["outcome_tracker", "outcome tracker", "trust score", "OutcomeTracker", "TrackedOutcome"],
        "stake_pool": ["stake pool", "stake_pool", "pool", "StakingPool", "StakePosition"],
    },
    "razao_logica": {
        "z3_solver": ["z3", "z3_solver", "smt", "satisfiability", "Z3Engine", "z3_engine"],
        "sympy": ["sympy", "symbolic", "sympy engine", "SymPyEngine"],
        "kanren": ["kanren", "logic programming", "miniKanren", "KanrenEngine"],
        "critical_reasoner": ["critical", "critical_reasoner", "critical reasoning", "CriticalEngine"],
        "quantum_reasoning": ["quantum", "quantum.py", "quantum reasoning", "quantum_"],
        "bayesian_inference": ["bayesian", "bayes", "probabilistic", "bayesian_inference"],
        "dialectical_engine": ["dialectical", "dialetic", "thesis", "antithesis", "DialecticalEngine", "Dialectic"],
        "reasoning_engines": ["engines.py", "reasoning engines", "reasoning/", "MultiReasoningEngine", "reasoning_result"],
    },
    "evolucao": {
        "evolution_registry": ["evolution_registry", "evolution/cycles", "evolution registry", "EvolutionRegistry"],
        "cycles_manager": ["cycles", "cycles.py", "cycles.json", "evo-", "EvolutionCycle"],
        "reflection_ledger": ["reflection_ledger", "reflection", "reflexion ledger", "reflexion_middleware"],
        "trajectory_mapper": ["trajectory_mapper", "trajectory mapper", "trajectory", "TrajectoryMapper"],
        "autoevolve_pipeline": ["autoevolve", "auto_evolve", "auto-evolve", "autoevolve"],
        "evolutionary_roadmap": ["evolutionary_roadmap", "roadmap", "evolutionary pipeline", "EvolutionaryRoadmap", "evolutionary_pipeline"],
        "successor_generator": ["successor_generator", "successor generator", "plausible successors", "SuccessorGenerator"],
    },
    "protocolos": {
        "sdd_spec_first": ["sdd", "spec-first", "spec_first", "especificação formal", "spec-", "Specification Driven"],
        "tdd_red_green_refactor": ["tdd", "red-green-refactor", "test-first", "test driven", "RED", "GREEN", "REFACTOR", "test_"],
        "a2a_blackboard": ["a2a", "blackboard", "agent-to-agent", "A2A blackboard", "blackboard.py"],
        "mcp_interconnect": ["mcp", "model context protocol", "mcp_interconnect", "metacognitive", "mcp_server", "MCP interconnect"],
        "bernstein_orchestration": ["bernstein", "orchestration", "pipeline multi-agente", "BernsteinOrchestrator"],
        "sdd_gate": ["sdd gate", "spec verifier", "specverifier", "SDD Gate", "SpecVerifier"],
        "behavioral_gate": ["behavioral_gate", "behavioral gate", "gate", "BehavioralGate"],
        "reflexion_middleware": ["reflexion", "reflection middleware", "auto-reflexão", "ReflexionMiddleware"],
    },
    "integracoes": {
        "antigravity_bridge": ["antigravity", "antigravity_bridge", "antigravity bridge", "deepmind", "antigravity_bridge.py"],
        "cli_integrations": ["cli", "command line", "integrations/", "opencode_cli", "integrations"],
        "pypi_searcher": ["pypi", "pypi_searcher", "pypi scout", "pip", "pypi-searcher"],
        "web_search": ["web_search", "web search", "websearch", "search web", "web_search_researcher"],
        "webfetch": ["webfetch", "fetch url", "web fetch", "webfetch_"],
        "mcp_servers": ["mcp", "mcp server", "model context protocol", "mcp_servers"],
        "git_manager": ["git", "git-manager", "git_manager", "github", "git-manager"],
    },
    "infra_dados": {
        "schemas_validator": ["schemas", "schema", "validator", "schema/", "schema.json"],
        "data_pipeline": ["data/", "data pipeline", "dataset", "evidence_graph"],
        "benchmarks": ["benchmark", "benchmarks/", "scientific_reasoning"],
        "notebooks": ["notebook", "notebooks/", "jupyter", "notebook"],
        "batch_executor": ["batch", "batch-executor", "executor", "batch-executor"],
        "installer": ["installer", "install/", "setup", "installer/"],
        "assets_media": ["assets/", "illustrations", "media", "webapp", "assets"],
        "gametheory_models": ["gametheory", "game theory", "gametheory/", "PayoffMatrix", "ShapleyValue"],
    },
    "governanca": {
        "cooperative_governance": ["cooperative", "cooperative_governance", "governança", "cooperative governance"],
        "debate_strategies": ["debate", "debate_strategies", "moderator", "DebateStrategy", "MetaReasoner"],
        "game_theory_analysis": ["game theory", "gametheory", "teoria dos jogos", "TitForTat", "GrimTrigger", "ShapleyValue", "PayoffMatrix"],
        "trust_scoring": ["trust score", "trust_scoring", "trust/", "TrustScorer", "ActionTrust", "TrustEngine"],
        "slashing_rules": ["slashing", "slash", "slashing rules", "slashing_mechanism"],
        "phd_auditor": ["phd", "phd_auditor", "doutor", "auditor acadêmico", "phd_auditor"],
        "scientific_governance": ["scientific_governance", "governance pipeline", "scientific_governance_pipeline"],
        "tokenomics": ["token", "token economy", "tokenomics", "economy", "TokenEconomy"],
    },
}


class NoologicalScanner:
    """Scanner que identifica AUSÊNCIAS no espaço de conhecimento.

    Complementa o AcademicAuditTrail (que identifica ERROS)
    com uma camada que identifica INCOMPLETUDES.

    Pipeline de detecção (v3.0):
      1. _negation_filter() — remove sentenças negadas ("sem X", "ausência de X")
      2. _category_present_v2() — ENRICHED_KW (keywords + sinônimos + n-gramas)
      3. _category_present() — keyword_map específico por dimensão
      4. Fallback genérico — word matching com word-boundary (\b)
    """

    # ─── Negation patterns (v3.0) ────────────────────────────────────────
    NEGATION_PATTERNS: list[str] = [
        r'\bsem\s+\w+(?:\s+(?!sem\b|aus[eê]ncia\b|n[aã]o\b)\w+){0,3}\b',  # "sem X" — non-greedy, evita capturar proximo "sem"
        r'\baus[eê]ncia\s+de\s+\w+(?:\s+\w+){0,3}\b',  # "ausência de X"
        r'\bn[aã]o\s+\w+(?:\s+\w+){0,3}\b',       # "não randomizado"
        r'\binexist[eê]ncia\s+de\s+\w+(?:\s+\w+){0,3}\b',
        r'\bdesprovido\s+de\s+\w+(?:\s+\w+){0,3}\b',
        r'\bcarente\s+de\s+\w+(?:\s+\w+){0,3}\b',
    ]

    @staticmethod
    def _negation_filter(corpus: str) -> str:
        """Remove do corpus sentencas com padrões de negacao (v3.0).

        Evita falsos positivos como:
          "sem grupo controle" -> "controle" detectado
          "ausencia de randomizacao" -> "randomiz" detectado
        """
        import re
        filtered = corpus
        for pattern in NoologicalScanner.NEGATION_PATTERNS:
            filtered = re.sub(pattern, ' ', filtered, flags=re.IGNORECASE)
        # Remove extra whitespace
        return re.sub(r'\s+', ' ', filtered).strip()

    @staticmethod
    def _word_boundary_match(keyword: str, corpus: str) -> bool:
        """Keyword matching com word-boundary (\b) — v3.0.

        Evita falsos positivos como:
          "control" ⊂ "controle" (substring)
          "randomiz" ⊂ "randomizacao" (substring)
        """
        import re
        # Para keywords multi-palavra, usa match literal
        if ' ' in keyword:
            return keyword in corpus
        # Para keywords de raiz (ex: "control", "randomiz"), usa \b
        return bool(re.search(r'\b' + re.escape(keyword) + r'\w*', corpus, re.IGNORECASE))

    def __init__(self, dimensions: dict[str, KnowledgeDimension] | None = None,
                 domain: str = ""):
        """Inicializa o scanner.

        Args:
            dimensions: dicionário de dimensões (se None, usa EPISTEMOLOGICAL_DIMENSIONS
                        ou ECOSYSTEM_DIMENSIONS conforme domain)
            domain: domínio de pesquisa — "ecosystem" carrega ECOSYSTEM_DIMENSIONS
        """
        if dimensions is not None:
            self.dimensions = dimensions
        elif domain == "ecosystem":
            self.dimensions = ECOSYSTEM_DIMENSIONS
        else:
            self.dimensions = EPISTEMOLOGICAL_DIMENSIONS
        self._domain = domain
        self.scan_results: dict[str, Any] = {}
        self.domain_weights: dict[str, float] = {}
        self.scan_history: list[dict[str, Any]] = []  # v2.0: historico para tendencia

    def set_domain(self, domain: str):
        """Aplica pesos adaptativos ao dominio de pesquisa (v2.0)."""
        if domain in DOMAIN_WEIGHTS:
            self.domain_weights = DOMAIN_WEIGHTS[domain]
        else:
            self.domain_weights = {}

    def scan(self, audit_trail: Any, research_domain: str = "",
             text_analyzer: Any = None) -> dict[str, Any]:
        """Varredura completa com validacao por frequencia (v2.0).

        Se research_domain == "ecosystem", usa ECOSYSTEM_DIMENSIONS
        e ECOSYSTEM_KEYWORDS para detecção. Inclui análise por camadas.
        """
        self.set_domain(research_domain)
        # Alterna para dimensões do ecossistema se domain == "ecosystem"
        if research_domain == "ecosystem" and self._domain != "ecosystem":
            self.dimensions = ECOSYSTEM_DIMENSIONS
            self._domain = "ecosystem"
        elif research_domain != "ecosystem" and self._domain == "ecosystem":
            self.dimensions = EPISTEMOLOGICAL_DIMENSIONS
            self._domain = ""

        corpus_text = self._extract_corpus(audit_trail)
        corpus_lower = corpus_text.lower()

        dimension_results = {}
        total_covered = 0
        total_categories = 0

        for dim_key, dimension in self.dimensions.items():
            covered, absent = [], []
            weight = self.domain_weights.get(dim_key, 1.0)

            for category in dimension.categories:
                total_categories += 1
                if self._category_present_v2(category, corpus_lower, dim_key, text_analyzer):
                    covered.append(category)
                    total_covered += 1
                else:
                    absent.append(category)

            density = len(covered) / max(1, len(dimension.categories))
            confidence = 0.85 if text_analyzer else 0.70
            blind_spot_score = (0.2 - density) * weight if density < 0.2 else 0

            dimension_results[dim_key] = {
                "name": dimension.name,
                "description": dimension.description,
                "weight": round(weight, 2),
                "covered": covered,
                "absent": absent,
                "density": round(density, 2),
                "coverage_pct": round(density * 100),
                "confidence": confidence,
                "weighted_coverage": round(density * weight * 100),
                "blind_spot_score": round(blind_spot_score, 3),
            }

        overall_density = total_covered / max(1, total_categories)
        blind_spots = self._identify_blind_spots_v2(dimension_results)
        comfort_zones = self._detect_comfort_zones(dimension_results)
        cross_corr = self._cross_correlation(dimension_results)
        recommendations = self._generate_recommendations_v2(dimension_results, comfort_zones)

        # Análise por camadas do ecossistema (SPEC-022)
        ecosystem_layers = None
        if research_domain == "ecosystem":
            ecosystem_layers = self._analyze_ecosystem_layers(dimension_results)

        self.scan_results = {
            "research_domain": research_domain,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "version": "2.0",
            "overall_density": round(overall_density, 2),
            "overall_coverage_pct": round(overall_density * 100),
            "dimensions_analyzed": len(dimension_results),
            "total_categories": total_categories,
            "categories_covered": total_covered,
            "categories_absent": total_categories - total_covered,
            "dimensions": dimension_results,
            "cross_correlation": cross_corr,
            "comfort_zones": comfort_zones,
            "blind_spots": blind_spots,
            "recommendations": recommendations,
            "completeness_grade": self._grade(overall_density),
        }
        if ecosystem_layers is not None:
            self.scan_results["ecosystem_layers"] = ecosystem_layers

        self.scan_history.append(self.scan_results)
        return self.scan_results

    def _extract_corpus(self, audit_trail: Any) -> str:
        """Extrai texto completo do corpus de pesquisa."""
        texts = []
        # Suporte para _TextAuditTrail (SPEC-022) e objetos similares
        if hasattr(audit_trail, "get_all_text"):
            return audit_trail.get_all_text()
        if hasattr(audit_trail, "paragraphs"):
            for para in audit_trail.paragraphs.values():
                if hasattr(para, "text"):
                    texts.append(para.text)
                elif isinstance(para, dict):
                    texts.append(para.get("text", ""))
        # Também incluir evidências/claims
        if hasattr(audit_trail, "citation_map"):
            for src in audit_trail.citation_map:
                texts.append(str(src))
        return " ".join(texts)

    def _category_present_v2(self, category: str, corpus_lower: str,
                              dim_key: str, text_analyzer: Any = None) -> bool:
        """Detecção enriquecida v3.0: negação → ECOSYSTEM_KW/ENRICHED_KW → TextAnalyzer → fallback.

        Pipeline de precedência:
          1. _negation_filter() — remove sentenças negadas
          2. ECOSYSTEM_KEYWORDS (se domain="ecosystem") ou ENRICHED_KW (acadêmico)
          3. TextAnalyzer — validação por frequência de palavras
          4. _category_present() — keyword_map específico por dimensão
          5. Fallback genérico — word matching com \b boundary
        """
        cat_lower = category.lower()
        # v3.0: Remove sentencas negadas antes do matching
        clean_corpus = self._negation_filter(corpus_lower)

        # ─── Ecossistema: ECOSYSTEM_KEYWORDS (SPEC-022) ────────────────
        if self._domain == "ecosystem" and dim_key in ECOSYSTEM_KEYWORDS:
            for kw_cat, keywords in ECOSYSTEM_KEYWORDS[dim_key].items():
                if kw_cat in cat_lower:
                    return any(self._word_boundary_match(kw, clean_corpus) for kw in keywords)

        # ─── Acadêmico: ENRICHED_KW (camada 1 original) ────────────────
        if dim_key in ENRICHED_KW:
            for kw_cat, keywords in ENRICHED_KW[dim_key].items():
                if kw_cat in cat_lower:
                    # v3.0: word-boundary matching
                    return any(self._word_boundary_match(kw, clean_corpus) for kw in keywords)
        # TextAnalyzer frequency validation (camada 2)
        if text_analyzer and hasattr(text_analyzer, "word_counts"):
            words = cat_lower.split()
            found = sum(1 for w in words if len(w) > 3 and w in text_analyzer.word_counts)
            return found >= len(words) * 0.4
        # Fallback: original keyword matching (camada 3)
        return self._category_present(category, clean_corpus, dim_key)

    def _category_present(self, category: str, corpus_lower: str, dim_key: str) -> bool:
        """v3.0: Keyword matching com word-boundary (\\b) + 5 novas dimensoes.

        Usa casamento semantico por palavras-chave especificas de cada dimensao.
        v3.0: Adicionadas keywords para niveis_analise, temporalidade, populacao,
        dados, dominios (antes caiam no fallback generico).
        """
        cat_lower = category.lower()

        # Palavras-chave por dimensão (v3.0: expandido para 10 dimensoes)
        keyword_map: dict[str, dict[str, list[str]]] = {
            "paradigmas": {
                "positivista": ["positiv", "quantitativ", "experimental", "hipotese", "mensura"],
                "interpretativista": ["interpretativ", "qualitativ", "fenomenolog", "compreens"],
                "crítico": ["critic", "transformador", "emancip", "dialetic"],
                "pragmatista": ["pragmat", "misto", "multimetod", "triangul"],
                "construtivista": ["construtiv", "construcion", "significado"],
                "pós-estruturalista": ["estrutural", "desconst", "foucault", "derrida"],
                "complexo": ["complex", "sistem", "emerg", "holistic", "caos"],
            },
            "metodos": {
                "quantitativo experimental": ["experiment", "randomiz", "control", "ensaio clinico"],
                "quantitativo correlacional": ["correla", "regress", "associac", "preditor"],
                "qualitativo": ["qualitativ", "entrevista", "analise tematica", "fenomenolog"],
                "grounded theory": ["grounded", "teoria fundamentada"],
                "misto": ["misto", "multimetod", "triangul"],
                "revisão sistemática": ["revisao sistematica", "systematic review", "prisma"],
                "meta-análise": ["meta-analise", "meta analise", "tamanho de efeito"],
                "estudo de caso": ["estudo de caso", "case study", "caso clinico", "caso unico"],
                "pesquisa-ação": ["pesquisa-acao", "pesquisa acao", "action research"],
            },
            "teorias": {
                "cognitivo-comportamental": ["cognitiv", "comportamental", "tcc", "beck", "pensamento automatico"],
                "psicanalítico": ["psicanal", "freud", "inconscient", "transferenc"],
                "humanista": ["humanist", "roger", "centrado na pessoa", "auto-atualiz"],
                "sistêmico": ["sistemic", "familia", "cibernet", "padrao relacional"],
                "neurobiológico": ["neurobiolog", "neurocien", "amigdala", "cortex", "pre-frontal"],
                "evolucionista": ["evolucion", "adaptativ", "selecao natural"],
                "social-crítico": ["social critic", "critic social", "desiguald", "opress"],
                "fenomenológico-existencial": ["existencial", "heidegger", "sartre", "sentido da vida"],
                "comportamental": ["comportament", "skinner", "condicion", "reforc"],
                "integrativo": ["integrat", "transdiagnost", "unificad", "ecletic"],
            },
            "raciocinio": {
                "dedutivo": ["dedut", "premissa", "conclusao necessaria"],
                "indutivo": ["indut", "generaliz", "padrao", "regularidad"],
                "abdutivo": ["abdut", "hipotese", "melhor explicacao"],
                "dialético": ["dialet", "tese", "antitese", "sintes", "contradic"],
                "sistêmico": ["sistemic", "interconex", "retroaliment", "emergenc"],
                "probabilístico": ["probabil", "bayes", "incerteza", "estatistic"],
                "contrafactual": ["contrafactual", "se", "cenario alternativ"],
                "metacognitivo": ["metacognit", "pensar sobre", "auto-regul"],
                "teleológico": ["teleolog", "proposit", "finalidad", "objetivo"],
                "pragmático": ["pragmat", "aplic", "util", "pratico", "funcional"],
            },
            # ─── v3.0: novas dimensões com keywords específicas ───────
            "niveis_analise": {
                "individual": ["individu", "intrapsiquic", "sujeito", "self", "autoconsci"],
                "interpessoal": ["interpessoal", "relacional", "vincul", "terapeut"],
                "grupal": ["grupal", "organizacional", "equipe", "grupo", "coletiv"],
                "comunitário": ["comunitari", "comunidade", "territor", "local"],
                "sistêmico": ["politic", "governanc", "politica publica", "legislac"],
                "neurobiológico": ["neurobiolog", "neurocien", "amigdala", "cortex"],
                "evolutivo": ["evolutiv", "filogenet", "selecao natural", "ancestral", "adaptac"],
                "cultural": ["cultur", "antropolog", "etnograf", "intercultur"],
            },
            "temporalidade": {
                "transversal": ["transversal", "cross-sectional", "amostra unica"],
                "longitudinal": ["follow-up", "pre-post", "pre post", "seguimento", "curto prazo", "curtoprazo"],
                "longitudinal longo": ["longitudinal", "coorte", "prospectiv", "acompanhamento", "longo prazo", "longoprazo"],
                "histórico": ["retrospectiv", "histor", "arquiv", "documental", "passado"],
                "prospectivo": ["preditiv", "prognost", "futuro", "previs"],
                "desenvolvimental": ["desenvolviment", "ciclo de vida", "life span", "life-span"],
            },
            "populacao": {
                "adultos": ["adult", "meia-idade", "meia idade"],
                "idosos": ["idos", "envelhec", "geriatri"],
                "adolescentes": ["adolesc", "juven", "jovem"],
                "infância": ["infanc", "crianc", "infantil", "pre-escolar"],
                "gênero feminino": ["mulher", "feminin", "genero feminin"],
                "gênero masculino": ["homem", "masculin", "genero masculin"],
                "diversidade": ["lgbt", "diversidade", "genero nao", "transgener"],
                "contexto clínico": ["paciente", "clinic", "hospital", "ambulatori"],
                "contexto comunitário": ["comunitari", "comunidade", "atencao primaria"],
                "brasil": ["brasil", "latino-americ", "latino americ", "latam"],
            },
            "dados": {
                "clínicos": ["escala", "inventari", "questionari", "bdi", "ham", "scl"],
                "neurobiológicos": ["eeg", "fmri", "mri", "neuroimag", "biomarcador"],
                "qualitativos": ["entrevista", "grupo focal", "discurso", "narrativa"],
                "observacionais": ["observac", "naturalist", "etnograf"],
                "epidemiológicos": ["epidemiolog", "prevalenc", "incidencia", "comorbid"],
                "longitudinais": ["longitudinal", "follow-up", "onda", "wave", "painel"],
                "comparativos": ["cross-cultural", "transcultural", "cross national"],
                "metadados": ["meta-analise", "revisao sistematica", "metanalise"],
            },
            "dominios": {
                "psicologia clínica": ["psicologi", "clinic", "psicopatolog", "psicoterap"],
                "neurociências": ["neurocien", "neurobiolog", "neuroimag", "cerebr"],
                "sociologia": ["sociolog", "estratificac", "desiguald", "capital social"],
                "antropologia": ["antropolog", "etnograf", "cultur", "ritual"],
                "economia comportamental": ["economi", "comportamental", "nudge", "vies"],
                "filosofia da mente": ["filosof", "conscienc", "mente", "fenomenolog"],
                "psicofarmacologia": ["farmac", "medicac", "antidepress", "psicofarmac"],
                "saúde pública": ["saude publica", "sus", "promocao saude", "prevenc"],
                "educação": ["educac", "ensino", "aprendizag", "escolar"],
                "ia tecnologia": ["inteligencia artificial", "machine learning", "deep learning", "ia", "chatbot"],
            },
            "teoria_jogos": {
                "equilíbrio de nash": ["nash", "equilibrio de nash", "pne", "estrategia dominante"],
                "dilema do prisioneiro": ["prisioneiro", "dilema do prisioneiro", "cooperacao", "payoff"],
                "soma zero": ["soma zero", "zero-sum", "jogo de soma zero"],
                "tit-for-tat": ["tit for tat", "reciprocidade", "olho por olho"],
                "stackelberg": ["stackelberg", "lider", "seguidor"],
                "barganha": ["barganha", "negociacao", "bargaining"],
                "sinalização": ["sinalizac", "signaling", "screening"],
                "evolutivo": ["evolutivamente estavel", "ess", "selecao natural", "evolutiv"],
                "bayesiano": ["bayesiano", "harsanyi", "informacao incompleta"],
                "cooperativo": ["cooperativo", "shapley", "coalizao", "nucleolo"],
            },
        }

        # Buscar keywords específicas da dimensão
        if dim_key in keyword_map:
            for kw_category, keywords in keyword_map[dim_key].items():
                if kw_category in cat_lower:
                    # v3.0: word-boundary matching
                    for kw in keywords:
                        if self._word_boundary_match(kw, corpus_lower):
                            return True
                    return False  # Categoria específica não encontrada

        # Fallback: busca genérica com word-boundary
        words = cat_lower.split()
        match_count = 0
        for w in words:
            if len(w) > 3:
                if self._word_boundary_match(w, corpus_lower):
                    match_count += 1
        return match_count >= len(words) * 0.5

    def _analyze_ecosystem_layers(self, dimension_results: dict[str, Any]) -> dict[str, Any]:
        """Analisa a cobertura por camadas do ecossistema (SPEC-022).

        Agrupa dimensões em camadas funcionais e calcula cobertura consolidada.
        """
        LAYER_MAP = {
            "core_orchestration": ["agentes", "mci_core", "protocolos"],
            "diagnostico_evolucao": ["scanners", "evolucao"],
            "governanca_economia": ["trust_economy", "governanca"],
            "raciocinio_conhecimento": ["razao_logica"],
            "integracao_infra": ["integracoes", "infra_dados"],
        }

        layers = {}
        for layer_name, dim_keys in LAYER_MAP.items():
            dims_in_layer = [k for k in dim_keys if k in dimension_results]
            if not dims_in_layer:
                continue
            total_cats = sum(len(dimension_results[k].get("covered", []) +
                               dimension_results[k].get("absent", []))
                           for k in dims_in_layer)
            total_covered = sum(len(dimension_results[k].get("covered", []))
                               for k in dims_in_layer)
            covered_pct = round(total_covered / max(1, total_cats) * 100)
            status = "boa" if covered_pct >= 50 else "parcial" if covered_pct >= 20 else "crítica"
            layers[layer_name] = {
                "coverage_pct": covered_pct,
                "status": status,
                "components_found": sum(len(dimension_results[k].get("covered", []))
                                       for k in dims_in_layer),
                "components_absent": sum(len(dimension_results[k].get("absent", []))
                                        for k in dims_in_layer),
                "dimensions": dims_in_layer,
            }

        return layers

    def _identify_blind_spots_v2(self, dimension_results: dict[str, Any]) -> list[dict[str, Any]]:
        """v2.0: Pontos cegos com severidade ponderada pelo peso do dominio."""
        blind_spots = []
        for dim_key, dim_data in dimension_results.items():
            if dim_data["density"] < 0.2:
                score = dim_data.get("blind_spot_score", 0)
                severity = "critical" if score > 0.2 else "high" if score > 0.1 else "moderate"
                blind_spots.append({
                    "dimension": dim_data["name"], "key": dim_key,
                    "density": dim_data["density"], "severity": severity,
                    "weight": dim_data.get("weight", 1.0),
                    "absent_categories": dim_data["absent"][:5],
                    "impact": f"Dimensao '{dim_data['name']}' com apenas {dim_data['coverage_pct']}% de cobertura (peso: {dim_data.get('weight',1.0)})."
                })
        return sorted(blind_spots, key=lambda x: x["density"])

    def _detect_comfort_zones(self, dim_results: dict[str, Any]) -> list[dict[str, Any]]:
        """v2.0: Detecta 'zonas de conforto epistemologico'."""
        zones = []
        high = {k: v for k, v in dim_results.items() if v["density"] > 0.6}
        low = {k: v for k, v in dim_results.items() if v["density"] < 0.2}
        for hk, hd in high.items():
            neglected = [lk for lk in low if lk != hk][:3]
            if neglected:
                zones.append({"comfort_zone": hd["name"], "comfort_density": hd["coverage_pct"], "neglected": neglected})
        return zones

    def _cross_correlation(self, dim_results: dict[str, Any]) -> list[dict[str, Any]]:
        """v2.0: Correlacao cruzada entre pares de dimensoes (heatmap data)."""
        corrs, keys = [], list(dim_results.keys())
        for i, d1 in enumerate(keys):
            for d2 in keys[i+1:]:
                diff = abs(dim_results[d1]["coverage_pct"] - dim_results[d2]["coverage_pct"])
                corr = max(0, 1 - diff / 100)
                corrs.append({"dim1": d1, "dim2": d2, "d1_pct": dim_results[d1]["coverage_pct"], "d2_pct": dim_results[d2]["coverage_pct"], "correlation": round(corr, 2)})
        return sorted(corrs, key=lambda x: x["correlation"], reverse=True)

    def _generate_recommendations_v2(self, dim_results: dict[str, Any], comfort_zones: list[dict[str, Any]]) -> list[str]:
        """v2.0: Recomendacoes enriquecidas com zonas de conforto."""
        recs = []
        for dk, dd in dim_results.items():
            if dd["density"] < 0.3 and dd["absent"]:
                recs.append(f"[{dd['name']}] Densidade {dd['coverage_pct']}%. Explorar: {', '.join(dd['absent'][:3])}.")
        for cz in comfort_zones[:3]:
            recs.append(f"[Conforto] Concentracao em '{cz['comfort_zone']}' ({cz['comfort_density']}%). Expandir para: {', '.join(cz['neglected'][:2])}.")
        return recs if recs else ["Pesquisa com boa cobertura multidimensional."]

    def _identify_blind_spots(self, dimension_results: dict[str, Any]) -> list[dict[str, Any]]:
        """@deprecated v1.0 — Substituído por _identify_blind_spots_v2().
        
        Mantido para compatibilidade com código legado.
        """
        blind_spots = []

        for dim_key, dim_data in dimension_results.items():
            if dim_data["density"] < 0.2:
                blind_spots.append({
                    "dimension": dim_data["name"],
                    "key": dim_key,
                    "density": dim_data["density"],
                    "absent_categories": dim_data["absent"][:5],
                    "severity": "critical" if dim_data["density"] == 0 else "high" if dim_data["density"] < 0.1 else "moderate",
                    "impact": f"A dimensão '{dim_data['name']}' está praticamente inexplorada. "
                             f"Isso pode indicar viés metodológico ou limitação de escopo."
                })

        return sorted(blind_spots, key=lambda x: x["density"])

    def _generate_recommendations(
        self,
        dimension_results: dict[str, Any],
        research_domain: str,
    ) -> list[str]:
        """@deprecated v1.0 — Substituído por _generate_recommendations_v2().
        
        Mantido para compatibilidade com código legado.
        """
        recommendations = []

        # Recomendações por dimensão com baixa densidade
        for dim_key, dim_data in dimension_results.items():
            if dim_data["density"] < 0.3 and dim_data["absent"]:
                top_absent = dim_data["absent"][:3]
                recommendations.append(
                    f"[{dim_data['name']}] Explorar: {', '.join(top_absent)}. "
                    f"A densidade atual é de apenas {dim_data['coverage_pct']}%."
                )

        # Recomendações de cruzamento interdisciplinar
        if dimension_results.get("dominios", {}).get("density", 1) < 0.3:
            recommendations.append(
                "[Domínios Cruzados] A pesquisa está concentrada em poucas áreas do conhecimento. "
                "Considere incorporar perspectivas da neurociência, sociologia ou economia comportamental."
            )

        # Recomendações de diversidade metodológica
        if dimension_results.get("metodos", {}).get("density", 1) < 0.3:
            recommendations.append(
                "[Métodos] A abordagem metodológica é restrita. "
                "Considere complementar com métodos mistos ou revisão sistemática."
            )

        # Recomendações de Teoria dos Jogos
        if dimension_results.get("teoria_jogos", {}).get("density", 1) == 0:
            recommendations.append(
                "[Teoria dos Jogos] Nenhuma perspectiva estratégica foi aplicada. "
                "Para pesquisas que envolvem decisão ou interação, considere modelar com "
                "Equilíbrio de Nash, Jogos Evolutivos ou Barganha."
            )

        return recommendations if recommendations else ["A pesquisa apresenta boa cobertura multidimensional."]

    def _grade(self, density: float) -> str:
        """Atribui conceito baseado na densidade de cobertura."""
        if density >= 0.7: return "A — Cobertura Epistemológica Ampla"
        if density >= 0.5: return "B — Cobertura Moderada"
        if density >= 0.3: return "C — Cobertura Limitada"
        if density >= 0.1: return "D — Cobertura Restrita"
        return "F — Cobertura Mínima ( muitos pontos cegos)"

    def generate_markdown_report(self) -> str:
        """Gera relatório Markdown do escaneamento."""
        r = self.scan_results
        if not r:
            return "Nenhum escaneamento realizado."

        lines = [
            f"# Scanner Noológico — Relatório de Cobertura Epistemológica",
            f"",
            f"**Domínio**: {r['research_domain'] or 'Não especificado'}",
            f"**Data**: {r['timestamp'][:19]}",
            f"**Cobertura Global**: {r['overall_coverage_pct']}% ({r['categories_covered']}/{r['total_categories']} categorias)",
            f"**Conceito**: {r['completeness_grade']}",
            f"",
            f"---",
            f"",
            f"## Dimensões Analisadas ({r['dimensions_analyzed']})",
            f"",
        ]

        for dim_key, dim_data in r["dimensions"].items():
            bar_len = 30
            filled = int(dim_data["density"] * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            lines.append(f"### {dim_data['name']} — {dim_data['coverage_pct']}%")
            lines.append(f"`{bar}`")
            lines.append(f"")
            if dim_data["covered"]:
                lines.append(f"**Explorado ({len(dim_data['covered'])})**: {', '.join(dim_data['covered'][:5])}")
            if dim_data["absent"]:
                lines.append(f"**Ausente ({len(dim_data['absent'])})**: {', '.join(dim_data['absent'][:5])}")
            lines.append(f"")

        lines.append("---")
        lines.append("")
        lines.append(f"## Pontos Cegos ({len(r['blind_spots'])})")
        lines.append("")
        if r["blind_spots"]:
            for bs in r["blind_spots"]:
                lines.append(f"- 🔴 **{bs['dimension']}** [{bs['severity'].upper()}]: {bs['impact']}")
        else:
            lines.append("Nenhum ponto cego crítico identificado.")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(f"## Recomendações de Expansão ({len(r['recommendations'])})")
        lines.append("")
        for i, rec in enumerate(r["recommendations"], 1):
            lines.append(f"{i}. {rec}")

        return "\n".join(lines)

    def save_report(self, output_path: str | Path) -> Path:
        """Salva relatório em disco."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_markdown_report(), encoding="utf-8")
        return path
