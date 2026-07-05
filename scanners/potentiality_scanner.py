#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotentialityScanner v1.0 — Scanner de Potenciais Latentes (Módulo 1)
======================================================================
Extrai o DNA estrutural do ecossistema mapeando os componentes e
skills ativos para suas capacidades fundamentais. Identifica o núcleo central,
redundâncias críticas e lacunas epistemológicas emergentes.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set

class PotentialityScanner:
    """Scanner de Potenciais Latentes do OpenCode Ecosystem."""

    # Mapeamento estático das capacidades dos componentes core do ecossistema
    CORE_COMPONENT_MAP = {
        "noological_scanner": ["gap_detection", "epistemological_analysis", "vocabulary_boundary"],
        "teleological_scanner": ["prescriptive_inference", "normative_analysis", "teleological_mapping"],
        "cross_validation_engine": ["cross_validation", "consistency_checking", "validation_matrix"],
        "polymathic_convergence": ["polymathic_reasoning", "interdisciplinary_synthesis"],
        "trajectory_mapper": ["trajectory_mapping", "evolutionary_path_planning"],
        "autoevolve": ["self_evolution", "pipeline_optimization", "metacognitive_feedback"],
        "mcp_ecosystem": ["dependency_mapping", "context_offloading", "mcp_connection"],
        "antigravity_bridge": ["parallel_orchestration", "external_agent_delegation", "image_generation", "browser_automation"],
        "master_orchestrator": ["central_coordination", "task_delegation", "session_management"],
        "stage_orchestrator": ["pipeline_execution", "stage_sequencing"],
        "trust_engine": ["cognitive_guardrails", "goal_drift_prevention", "realtime_interception"],
        "social_impact_scanner": ["social_impact_assessment", "sroi_analysis", "theory_of_change",
                                   "b_impact_assessment", "sdg_tracking", "iris_plus_indicators",
                                   "iso_26000_compliance", "social_value_measurement"],
        "cooperative_governance": ["governance_enforcement", "conflict_resolution"],
        "dialectical_engine": ["thesis_antithesis_synthesis", "contradiction_analysis"],
        "epistemological_potential": ["potential_estimation", "opportunity_ranking"],
        "structural_compression_engine": ["structural_compression", "token_optimization"],
        "structural_noise_scanner": ["noise_filtering", "information_density"],
        # ── Research Skills Implementation Framework (SPEC-081, R35/R36) ──
        "game_theory_skill": ["game_theory_modeling", "equilibrium_analysis", "pareto_optimality", "payoff_analysis"],
        "temporal_population_skill": ["temporal_modeling", "longitudinal_analysis", "population_generalization", "sampling_design", "time_series_analysis"],
        "theoretical_empirical_skill": ["paradigm_analysis", "empirical_validation", "theoretical_framework", "reliability_analysis", "effect_size_analysis"],
        "logical_multiscale_skill": ["reasoning_engine", "logical_inference", "multi_scale_analysis", "argumentation_validation", "hierarchical_modeling"],
        # ── Cross-Paradigm Reasoning Engine (SPEC-082, R38) ──
        "cross_paradigm_reasoning_skill": ["cross_paradigm_reasoning", "reasoning_orchestration",
                                            "autonomous_self_repair", "paradigm_bridge",
                                            "cross_paradigm_synthesis", "system_self_diagnostic"],
    }

    # Heurísticas de mapeamento de palavras-chave para skills dinâmicas
    KEYWORD_TO_CAPABILITY = {
        "test": "tdd_validation",
        "tdd": "tdd_validation",
        "mock": "tdd_validation",
        "git": "version_control",
        "worktree": "version_control",
        "branch": "version_control",
        "agent": "agent_orchestration",
        "subagent": "agent_orchestration",
        "swarm": "agent_orchestration",
        "paper": "academic_synthesis",
        "article": "academic_synthesis",
        "qualis": "academic_synthesis",
        "academic": "academic_synthesis",
        "quantum": "quantum_computing",
        "qubit": "quantum_computing",
        "contract": "legal_processing",
        "law": "legal_processing",
        "juridico": "legal_processing",
        "data": "data_management",
        "db": "data_management",
        "sqlite": "data_management",
        "mcp": "mcp_connection",
        "server": "mcp_connection",
        "token": "token_optimization",
        "cost": "token_optimization",
        "sroi": "social_impact_assessment",
        "iso_26000": "social_impact_assessment",
        "theory_of_change": "social_impact_assessment",
        "impact": "social_impact_assessment",
        "social": "social_impact_assessment",
        "sdg": "sdg_tracking",
        "ods": "sdg_tracking",
        "sustentabilidade": "sdg_tracking",
        "b_corp": "b_impact_assessment",
        "iris": "iris_plus_indicators",
        "giin": "iris_plus_indicators",
        "deadweight": "social_value_measurement",
        "attribution": "social_value_measurement",
        "displacement": "social_value_measurement",
        # ── Dimensão: paradigmas ──
        "paradigma": "paradigm_analysis",
        "epistemologia": "paradigm_analysis",
        "fenomenologico": "paradigm_analysis",
        "positivista": "paradigm_analysis",
        "construtivista": "paradigm_analysis",
        "pragmatista": "paradigm_analysis",
        "pos-estruturalista": "paradigm_analysis",
        # ── Dimensão: metodos ──
        "metodologia": "methodology_design",
        "metodo": "methodology_design",
        "qualitativ": "methodology_design",
        "quantitativ": "methodology_design",
        "misto": "methodology_design",
        "revisao": "methodology_design",
        "meta-analise": "methodology_design",
        "grounded": "methodology_design",
        "estudo-de-caso": "methodology_design",
        "pesquisa-acao": "methodology_design",
        "empirico": "empirical_validation",
        "empirica": "empirical_validation",
        "validacao": "empirical_validation",
        # ── Dimensão: dominios ──
        "dominio": "interdisciplinary_synthesis",
        "psicologia": "interdisciplinary_synthesis",
        "clinica": "interdisciplinary_synthesis",
        "neurociencias": "interdisciplinary_synthesis",
        "sociologia": "interdisciplinary_synthesis",
        "antropologia": "interdisciplinary_synthesis",
        "educacao": "interdisciplinary_synthesis",
        "filosofia": "interdisciplinary_synthesis",
        "cross-domain": "cross_domain_mapping",
        "interdisciplinar": "cross_domain_mapping",
        # ── Dimensão: raciocinio ──
        "raciocinio": "reasoning_engine",
        "logica": "reasoning_engine",
        "inferencia": "reasoning_engine",
        "deducao": "reasoning_engine",
        "inducao": "reasoning_engine",
        "abducao": "reasoning_engine",
        "logical": "logical_inference",
        "argumentacao": "logical_inference",
        # ── Dimensão: dados ──
        "dados": "data_collection",
        "coleta": "data_collection",
        "entrevista": "data_collection",
        "observacao": "data_collection",
        "neurobiologico": "data_collection",
        "estatistica": "statistical_analysis",
        "analise": "statistical_analysis",
        "quantitativo": "statistical_analysis",
        # ── Dimensão: teorias ──
        "teoria": "theoretical_integration",
        "framework": "theoretical_integration",
        "referencial": "theoretical_integration",
        "sintese": "literature_synthesis",
        "revisao-sistematica": "literature_synthesis",
        # ── Dimensão: paradigmas (theoretical_framework) ──
        "epistemico": "theoretical_framework",
        "conceitual": "theoretical_framework",
        "marco_teorico": "theoretical_framework",
        "fundamentacao": "theoretical_framework",
        "ontologico": "theoretical_framework",
        # ── Dimensão: niveis_analise ──
        "nivel": "multi_scale_analysis",
        "escala": "multi_scale_analysis",
        "intra": "hierarchical_modeling",
        "inter": "hierarchical_modeling",
        "multi": "hierarchical_modeling",
        # ── Dimensão: temporalidade ──
        "temporal": "temporal_modeling",
        "longitudinal": "temporal_modeling",
        "transversal": "temporal_modeling",
        "historico": "temporal_modeling",
        "prospectivo": "longitudinal_analysis",
        "desenvolvimental": "longitudinal_analysis",
        # ── Dimensão: populacao ──
        "populacao": "population_generalization",
        "amostra": "population_generalization",
        "adultos": "population_generalization",
        "idosos": "population_generalization",
        "adolescentes": "population_generalization",
        "contexto": "sampling_design",
        "clinico": "sampling_design",
        "comunitar": "sampling_design",
        "cross-cultural": "sampling_design",
        # ── Dimensão: teoria_jogos ──
        "jogo": "game_theory_modeling",
        "nash": "equilibrium_analysis",
        "equilibrio": "equilibrium_analysis",
        "estrategia": "game_theory_modeling",
        "cooperativo": "game_theory_modeling",
        "dilema": "game_theory_modeling",
        "stackelberg": "equilibrium_analysis",
        "barganha": "game_theory_modeling",
        "pareto": "equilibrium_analysis",
        "payoff": "game_theory_modeling",
        "tit-for-tat": "game_theory_modeling",
        "replicator": "game_theory_modeling",
        "gale-shapley": "game_theory_modeling",
        # ── Novas keywords para skills de pesquisa (R35/R36) ──
        "time-series": "temporal_modeling",
        "moving-average": "temporal_modeling",
        "cronbach": "empirical_validation",
        "cohen": "statistical_analysis",
        "multiscale": "multi_scale_analysis",
        "multiescala": "multi_scale_analysis",
        "modus-ponens": "logical_inference",
        "modus-tollens": "logical_inference",
        "deductivo": "logical_inference",
        "falacia": "logical_inference",
        "etnografia": "methodology_design",
        "etnometodologia": "paradigm_analysis",
        "gwas": "statistical_analysis",
        "biobanco": "data_collection",
        "genomica": "interdisciplinary_synthesis",
        "serie-temporal": "temporal_modeling",
        "poder-estatistico": "statistical_analysis",
        "tamanho-efeito": "statistical_analysis",
        "mixed-model": "methodology_design",
        "inferencia-causal": "reasoning_engine",
        # ── SPEC-082: Cross-Paradigm Reasoning (R38) ──
        "cross-paradigm": "cross_paradigm_reasoning",
        "cross_paradigm": "cross_paradigm_reasoning",
        "multi-paradigm": "cross_paradigm_reasoning",
        "orchestrat": "reasoning_orchestration",
        "self-repair": "autonomous_self_repair",
        "self_repair": "autonomous_self_repair",
        "auto-repair": "autonomous_self_repair",
        "paradigm-bridge": "paradigm_bridge",
        "paradigm_bridge": "paradigm_bridge",
        "synthesis": "cross_paradigm_synthesis",
        "sintese": "cross_paradigm_synthesis",
        "diagnostic": "system_self_diagnostic",
        "self-diagnostic": "system_self_diagnostic",
    }

    # Lista de capacidades latentes que representam o roadmap futuro do ecossistema
    TARGET_EVOLVING_CAPABILITIES = [
        "autonomous_self_repair",
        "distributed_consensus",
        "proactive_alignment",
        "cross_paradigm_reasoning",
        "dynamic_dependency_injection",
        "predictive_teleology",
        "social_impact_automation",
        "esg_continuous_monitoring",
        "impact_weighted_accounting",
    ]

    def __init__(self, workspace_path: str | Path = None):
        if workspace_path is None:
            self.workspace = Path(__file__).parent.parent.parent.parent.resolve()
        else:
            self.workspace = Path(workspace_path)
            
        self.registry_path = self.workspace / "nexus" / "skills_registry.json"
        self.capability_map: Dict[str, List[str]] = {}

    def extract_dna(self) -> Dict[str, Any]:
        """Extrai o DNA de capacidades estruturais do ecossistema."""
        # 1. Carregar mapeamento do núcleo (core)
        self.capability_map = {k: list(v) for k, v in self.CORE_COMPONENT_MAP.items()}

        # 2. Carregar skills dinâmicas do skills_registry.json
        skills = []
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    skills = data.get("skills", [])
            except Exception as e:
                print(f"[PotentialityScanner] Erro ao ler registro de skills: {e}")

        # 3. Mapear skills dinâmicas via heurística
        for skill in skills:
            skill_name = skill.get("name", "")
            skill_path = skill.get("path", "")
            
            # Combinar texto de busca
            search_text = (skill_name + " " + skill_path).lower()
            
            # Encontrar capacidades correspondentes
            caps = []
            for kw, cap in self.KEYWORD_TO_CAPABILITY.items():
                if kw in search_text:
                    caps.append(cap)
            
            if caps:
                # Se a skill já existir no mapa, apenas estende as capacidades
                if skill_name in self.capability_map:
                    self.capability_map[skill_name] = list(set(self.capability_map[skill_name] + caps))
                else:
                    self.capability_map[skill_name] = list(set(caps))

        # 4. Calcular frequência das capacidades
        cap_frequency: Dict[str, int] = {}
        for caps in self.capability_map.values():
            for cap in caps:
                cap_frequency[cap] = cap_frequency.get(cap, 0) + 1

        # 5. Identificar Capacidades Centrais (Core)
        # Qualquer capacidade que apareça em 2 ou mais componentes é considerada central
        core_capabilities = {cap for cap, freq in cap_frequency.items() if freq >= 2}

        # 6. Identificar Capacidades Redundantes
        # Qualquer capacidade com 3 ou mais componentes implementando
        redundant_capabilities = {cap for cap, freq in cap_frequency.items() if freq >= 3}

        # 7. Identificar Capacidades Ausentes
        # Qualquer capacidade do roadmap alvo que não esteja presente em nenhuma skill ativa
        all_extracted_caps = set(cap_frequency.keys())
        missing_capabilities = {
            cap for cap in self.TARGET_EVOLVING_CAPABILITIES
            if cap not in all_extracted_caps
        }

        return {
            "capability_map": self.capability_map,
            "core_capabilities": sorted(list(core_capabilities)),
            "redundant_capabilities": sorted(list(redundant_capabilities)),
            "missing_capabilities": sorted(list(missing_capabilities)),
            "frequencies": cap_frequency
        }

    def scan(self) -> Dict[str, Any]:
        """Executa a varredura completa de potenciais latentes (DNA Extractor)."""
        return self.extract_dna()

    def save_report(self, report_data: Dict[str, Any], output_path: str | Path) -> None:
        """Gera e salva um relatório formatado em markdown."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Relatório de DNA Estrutural (Potentiality Scanner)",
            "",
            "## 🧬 1. Resumo do DNA de Capacidades",
            f"- **Componentes/Skills mapeados:** {len(report_data['capability_map'])}",
            f"- **Capacidades distintas identificadas:** {len(report_data['frequencies'])}",
            f"- **Capacidades centrais (Core):** {len(report_data['core_capabilities'])}",
            f"- **Capacidades redundantes (Sobreposição):** {len(report_data['redundant_capabilities'])}",
            f"- **Capacidades ausentes (Lacunas evolutivas):** {len(report_data['missing_capabilities'])}",
            "",
            "## 🔑 2. Capacidades Centrais (Core)",
            "Estas capacidades formam o núcleo de inteligência do ecossistema e são amplamente utilizadas:",
        ]

        for cap in report_data["core_capabilities"]:
            freq = report_data["frequencies"].get(cap, 0)
            lines.append(f"- `{cap}` (Presente em {freq} componentes)")

        lines.extend([
            "",
            "## ⚠️ 3. Capacidades Redundantes (Potencial de Convergência)",
            "Múltiplos componentes implementam estas capacidades. Há oportunidade de refatorar ou convergência de código:",
        ])

        for cap in report_data["redundant_capabilities"]:
            components = [k for k, v in report_data["capability_map"].items() if cap in v]
            lines.append(f"- `{cap}` (Implementado por: {', '.join(components)})")

        lines.extend([
            "",
            "## 🔍 4. Capacidades Ausentes (Lacunas do Roadmap Evolutivo)",
            "Estas capacidades pertencem ao roadmap planejado para o ecossistema mas não foram detectadas em nenhum componente:",
        ])

        for cap in report_data["missing_capabilities"]:
            lines.append(f"- `{cap}` 🔴 (Sem implementação ativa)")

        lines.extend([
            "",
            "## 🗺️ 5. Mapa Detalhado de Capacidades",
            "| ID do Componente | Capacidades Mapeadas |",
            "|------------------|----------------------|",
        ])

        for comp, caps in sorted(report_data["capability_map"].items()):
            lines.append(f"| `{comp}` | {', '.join(f'`{c}`' for c in caps)} |")

        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"[PotentialityScanner] Relatório salvo em: {out}")
