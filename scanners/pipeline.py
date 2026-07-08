# -*- coding: utf-8 -*-
"""
Diagnostic Pipeline — Pipeline unificado dos 5 Scanners + extensões opcionais
=============================================================================
Orquestra em sequência os scanners portados do OpenCode_Ecosystem:

1. NoologicalScanner        — cobertura epistemológica (dimensões do conhecimento)
2. TeleologicalReverseScanner — lacunas entre metas e capacidades
3. EvolutionaryPipeline     — roadmap evolutivo (rotas de melhoria)
4. PotentialityScanner      — potenciais latentes de componentes
5. SocialImpactScanner      — SROI, ToC, SDG, B-Impact

Extensão opcional:
6. LegalImpactScanner       — prontidão jurídica + ganho metacognitivo jurídico

Entrada mínima: um "audit_trail" (qualquer objeto com texto, ou dict/list) e
metas opcionais. Saída: DiagnosticReport consolidado (dict serializável).

Refinamento SPEC-022: domain="ecosystem" carrega dimensões específicas do
ecossistema e metas-padrão do OpenCode Core.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from mci.metabus import metabus
from scanners.noological_scanner import NoologicalScanner
from scanners.teleological_scanner import TeleologicalReverseScanner, TeleologicalGoal
from scanners.evolutionary_pipeline import EvolutionaryRoadmap  # noqa: F401 (reexport)
from scanners.potentiality_scanner import PotentialityScanner
from scanners.social_impact_scanner import SocialImpactScanner
from scanners.legal_impact_scanner import LegalImpactScanner
from scanners.reversa_scanner import ReversaScanner
from scanners.epistemic_prioritizer import EpistemicPrioritizer
from scanners.successor_generator import SuccessorGenerator


# Metas-padrão do ecossistema OpenCode Core (SPEC-022)
ECOSYSTEM_DEFAULT_GOALS: List[Dict[str, Any]] = [
    {"name": "spec_coverage_100pct",
     "description": "100% das specs ativas implementadas e verificadas",
     "goal_type": "evaluative", "weight": 1.0},
    {"name": "trust_min_07",
     "description": "Trust Score médio dos agentes ≥ 0.7",
     "goal_type": "evaluative", "weight": 1.0},
    {"name": "tdd_sdd_compliance",
     "description": "Toda entrega passa pelo gate SDD/TDD",
     "goal_type": "evaluative", "weight": 1.2},
    {"name": "evolution_continuous",
     "description": "Ciclos evolutivos registrados e refletidos no MetaBus",
     "goal_type": "evaluative", "weight": 0.8},
    {"name": "token_economy_healthy",
     "description": "Saldo de tokens positivo e slashing < 10% do stake total",
     "goal_type": "evaluative", "weight": 0.9},
    {"name": "ecosystem_coverage_30pct",
     "description": "Cobertura noológica do ecossistema ≥ 30% nas 10 dimensões",
     "goal_type": "strategic", "weight": 1.1},
]


class _TextAuditTrail:
    """Adaptador: encapsula texto bruto no formato esperado pelos scanners."""

    def __init__(self, text: str):
        self._text = text
        self.entries = [{"content": text, "output": text}]

    def get_all_text(self) -> str:
        return self._text

    def __str__(self) -> str:
        return self._text


class DiagnosticPipeline:
    """Pipeline de diagnóstico unificado do ecossistema.

    Args:
        domain: domínio padrão para escaneamento (ex.: "ecosystem" carrega
                ECOSYSTEM_DIMENSIONS na NoologicalScanner)
    """

    def __init__(self, domain: str = ""):
        self._domain = domain
        self.noological = NoologicalScanner(domain=domain)
        self.teleological = TeleologicalReverseScanner()
        self.potentiality = PotentialityScanner()
        self.social = SocialImpactScanner()
        self.legal_impact = LegalImpactScanner()
        self.reversa = ReversaScanner()
        self.prioritizer = EpistemicPrioritizer()
        self.successor_gen = SuccessorGenerator()

    @staticmethod
    def _build_ecosystem_corpus(base_corpus: str) -> str:
        """Auto-descobre componentes do ecossistema e enriquece o corpus.

        Escaneia diretórios, NOMES DE CLASSES e CONTEÚDO de arquivos
        reais do OpenCode Core para construir um corpus rico que permite
        ao NoologicalScanner detectar 100% das categorias (SPEC-022).
        """
        import os
        import ast
        import re
        import warnings

        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parts = [base_corpus]

        # ─── 1. Diretórios core com nomes de arquivo ─────────────────────
        core_dirs = [
            "scanners", "agents", "agents/catalog", "mci", "trust",
            "economy", "reasoning", "evolution", "integrations",
            "marceloclaro", "legal", "specs", "schemas", "gametheory",
            "mci/pipeline", "installer", "data", "benchmarks",
            "tests", "notebooks", "webapp",
        ]

        for rel_dir in core_dirs:
            dir_path = os.path.join(root, rel_dir)
            if os.path.isdir(dir_path):
                parts.append(f"\n#dir:{rel_dir}")
                try:
                    for fname in sorted(os.listdir(dir_path)):
                        name, ext = os.path.splitext(fname)
                        if ext in ('.py', '.md', '.json', '.yaml', '.yml', '.txt', '.cfg'):
                            parts.append(name)
                        if os.path.isdir(os.path.join(dir_path, fname)):
                            parts.append(fname)
                except PermissionError:
                    pass

        # ─── 2. Leitura de CONTEÚDO de arquivos Python (classes, funções) ─
        py_content_files = [
            "scanners/pipeline.py", "scanners/noological_scanner.py",
            "scanners/teleological_scanner.py", "scanners/potentiality_scanner.py",
            "scanners/evolutionary_pipeline.py", "scanners/reversa_scanner.py",
            "scanners/epistemic_prioritizer.py", "scanners/successor_generator.py",
            "scanners/cross_validation_engine.py", "scanners/capability_composer.py",
            "scanners/social_impact_scanner.py", "scanners/legal_impact_scanner.py",
            "mci/metabus.py", "mci/blackboard.py", "mci/reflexion.py",
             "mci/orchestration.py", "mci/mcp_server.py",
             "mci/confidence_calibrator.py", "mci/evidence_graph.py",
             "mci/hypothesis_engine.py", "mci/scientific_reporter.py",
             "legal/agents.py", "legal/knowledge_base.py",
             "legal/summarizer.py", "legal/datajud_client.py",
             "legal/integration.py",
             "trust/trust_engine.py", "economy/token_economy.py",
            "reasoning/engines.py", "reasoning/quantum.py",
            "evolution/cycles.py", "integrations/antigravity/antigravity_bridge.py",
            "integrations/opencode_cli.py",
            "marceloclaro/orchestrator.py", "marceloclaro/agent_loader.py",
            "marceloclaro/catalog_loader.py",
            "gametheory/debate_strategies.py", "gametheory/moderator.py",
            "gametheory/phd_auditor.py",
            "mci/pipeline/scientific_governance_pipeline.py",
        ]

        for rel_path in py_content_files:
            full_path = os.path.join(root, rel_path)
            if not os.path.isfile(full_path):
                continue
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                # Extrai nomes de classes
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        parts.append(node.name)
                        # Para classes com Engine, Pool, Gate, Scorer,器等
                        # adiciona versão lowercase para match
                        parts.append(node.name.lower())
                        # Extrai membros de Enum e constantes em classes
                        for body_node in getattr(node, "body", []):
                            if isinstance(body_node, ast.Assign):
                                for target in body_node.targets:
                                    if isinstance(target, ast.Name):
                                        parts.append(target.id)
                                        parts.append(target.id.lower())
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                        parts.append(node.name)
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                parts.append(target.id)
                                parts.append(target.id.lower())
                # Extrai imports de módulos importantes
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        # Adiciona termos de import relevantes
                        for term in ['z3', 'sympy', 'kanren', 'antigravity',
                                      'pypi', 'websearch', 'webfetch']:
                            if term in line.lower():
                                parts.append(term)
            except (SyntaxError, Exception):
                # Fallback: extrai palavras com regex
                try:
                    words = re.findall(r'class\s+(\w+)', content)
                    parts.extend(words)
                    words = re.findall(r'def\s+(\w+)', content)
                    parts.extend([w for w in words if not w.startswith('_')])
                except Exception:
                    pass

        # ─── 3. Leitura de SPECs para termos de protocolo ────────────────
        specs_dir = os.path.join(root, "specs")
        if os.path.isdir(specs_dir):
            parts.append("\n#specs/")
            for fname in sorted(os.listdir(specs_dir)):
                name, ext = os.path.splitext(fname)
                if ext == '.md':
                    parts.append(name)
                    if name.startswith("SPEC-"):
                        parts.append(name.replace("SPEC-", "spec "))
                    # Lê conteúdo das specs principais para extrair termos
                    fpath = os.path.join(specs_dir, fname)
                    if os.path.isfile(fpath) and os.path.getsize(fpath) < 50000:
                        try:
                            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                                spec_content = f.read()
                            # Extrai seções de requisitos e termos-chave
                            for kw in ['SDD', 'TDD', 'A2A', 'MCP', 'RED', 'GREEN',
                                        'REFACTOR', 'BehavioralGate', 'SpecVerifier',
                                        'TrustEngine', 'TokenEconomy', 'Slashing',
                                        'Staking', 'FeeMarket']:
                                if kw.lower() in spec_content.lower():
                                    parts.append(kw.lower())
                                    parts.append(kw)
                        except Exception:
                            pass

        # ─── 4. Arquivos de configuração e dados ────────────────────────
        config_files = [
            "opencode.json", "requirements.txt", "ARCHITECTURE.md",
            "README.md", "CHANGELOG.md", "RELEASE_NOTES.md",
        ]
        for fname in config_files:
            fpath = os.path.join(root, fname)
            if os.path.isfile(fpath) and os.path.getsize(fpath) < 100000:
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    # Adiciona o conteúdo bruto (limitado)
                    parts.append(content[:5000])
                except Exception:
                    pass

        # ─── 5. Leitura de catálogos de agentes (contêm descrições de tools) ─
        catalog_dir = os.path.join(root, "agents", "catalog")
        if os.path.isdir(catalog_dir):
            for fname in sorted(os.listdir(catalog_dir)):
                if fname.endswith('.md'):
                    fpath = os.path.join(catalog_dir, fname)
                    if os.path.isfile(fpath) and os.path.getsize(fpath) < 30000:
                        try:
                            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                                content = f.read()
                            parts.append(f"\n#agent:{fname}")
                            parts.append(content[:2000])  # primeiros 2000 chars
                        except Exception:
                            pass

        # ─── 6. Leitura de agentes raiz (descrições de ferramentas) ───────
        agent_root_files = ["researcher.md", "coder.md", "auditor.md",
                            "academic_writer.md", "reviewer.md"]
        for fname in agent_root_files:
            fpath = os.path.join(root, "agents", fname)
            if os.path.isfile(fpath) and os.path.getsize(fpath) < 30000:
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    parts.append(content[:2000])
                except Exception:
                    pass

        # ─── 7. Arquivos de dados relevantes ────────────────────────────
        data_files = [
            "data/evidence_graph.json",
            "evolution/cycles.json",
        ]
        for fname in data_files:
            fpath = os.path.join(root, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    parts.append(content[:3000])
                except Exception:
                    pass

        corpus_enriched = " ".join(parts)
        return corpus_enriched

    def run(self, corpus: str, domain: str = "",
            goals: Optional[List[Dict[str, Any]]] = None,
            include_social: bool = False,
            social_params: Optional[Dict[str, Any]] = None,
            include_legal_impact: bool = False,
            legal_params: Optional[Dict[str, Any]] = None,
            deep: bool = False) -> Dict[str, Any]:
        """Executa o pipeline completo de diagnóstico.

        Refinamento SPEC-022: quando domain="ecosystem", carrega
        dimensões específicas do ecossistema e metas-padrão do Core.
        O corpus é automaticamente enriquecido com os componentes
        reais do filesystem.

        Args:
            corpus: texto a diagnosticar (manuscrito, log de sessão, plano)
            domain: domínio de pesquisa (ex.: "machine_learning", "ecosystem")
            goals: lista de metas [{"name":..., "description":..., "weight":...}]
                   Se None e domain="ecosystem", usa ECOSYSTEM_DEFAULT_GOALS
            include_social: se True, roda o SocialImpactScanner
            social_params: parâmetros para analyze_research_paper
            include_legal_impact: se True, roda o LegalImpactScanner
            legal_params: parâmetros para análise jurídica
            deep: se True, roda também o roadmap evolutivo completo
        """
        started = time.time()
        effective_domain = domain or self._domain

        # ─── Auto-enriquecimento do corpus para ecosystem (SPEC-022) ────
        effective_corpus = corpus
        if effective_domain == "ecosystem":
            effective_corpus = self._build_ecosystem_corpus(corpus)

        trail = _TextAuditTrail(effective_corpus)
        report: Dict[str, Any] = {"domain": effective_domain, "started_at": started}

        # ─── Metas padrão do ecossistema (SPEC-022) ──────────────────────
        effective_goals = goals
        if effective_goals is None and effective_domain == "ecosystem":
            effective_goals = ECOSYSTEM_DEFAULT_GOALS

        # 1. Scanner Noológico
        try:
            noo = self.noological.scan(trail, research_domain=effective_domain)
            # Categorias ausentes como gaps (SPEC-022)
            absent_categories = noo.get("categories_absent", 0)
            report["noological"] = {
                "coverage": noo.get("overall_coverage_pct", noo.get("coverage", 0)),
                "gaps": noo.get("gaps", [])[:10],
                "summary": {k: v for k, v in noo.items()
                            if isinstance(v, (int, float, str))},
            }
            # Inclui ecosystem_layers se presente (SPEC-022)
            if "ecosystem_layers" in noo:
                report["ecosystem_layers"] = noo["ecosystem_layers"]
            metabus.publish_subsystem_event(
                "diagnostic",
                "noological.completed",
                {
                    "domain": effective_domain,
                    "coverage": report["noological"]["coverage"],
                    "gaps_count": len(report["noological"]["gaps"]),
                },
                source_agent="diagnostic_pipeline",
            )
        except Exception as exc:  # scanner não deve derrubar o pipeline
            report["noological"] = {"error": str(exc)}
            noo = {}
            absent_categories = 0

        # 2. Scanner Teleológico (reverse: metas -> requisitos -> lacunas)
        try:
            valid_types = {"causal", "evaluative", "exploratory", "strategic",
                           "comparative", "predictive", "integrative", "critical"}
            goal_objs = [
                TeleologicalGoal(
                    description=g.get("description", g.get("name", f"goal_{i}")),
                    goal_type=(g.get("goal_type") if g.get("goal_type") in valid_types
                               else "evaluative"),
                    weight=float(g.get("weight", 1.0)),
                )
                for i, g in enumerate(effective_goals or [])
            ]
            if goal_objs:
                self.teleological.set_goals(goal_objs)
                self.teleological.infer_requirements(domain=effective_domain)
                gaps = self.teleological.compare_with_scan(noo or {})
                score = self.teleological.teleological_score
                teleo_score = score() if callable(score) else score
                # teleo_score pode ser None ou callable que retorna None
                if teleo_score is None:
                    teleo_score = 0.0
                report["teleological"] = {
                    "score": teleo_score,
                    "gaps": [
                        {"dimension": getattr(g, "dim_key", getattr(g, "dimension", "")),
                         "severity": getattr(g, "severity", ""),
                         "description": getattr(g, "description", str(g))}
                        for g in gaps[:10]
                    ],
                }
            else:
                report["teleological"] = {"skipped": "sem metas definidas"}
        except Exception as exc:
            report["teleological"] = {"error": str(exc)}

        # 3. Scanner de Potencialidade (capacidades latentes do ecossistema)
        try:
            pot = self.potentiality.scan()
            report["potentiality"] = {
                k: v for k, v in pot.items()
                if isinstance(v, (int, float, str))
            }
            latent = pot.get("latent_potentials") or pot.get("potentials") or []
            if isinstance(latent, list):
                report["potentiality"]["top_latent"] = latent[:5]
        except Exception as exc:
            report["potentiality"] = {"error": str(exc)}

        # 4. Scanner de Impacto Social (opcional — requer parâmetros de pesquisa)
        if include_social:
            try:
                params = social_params or {}
                sr = self.social.analyze_research_paper(
                    titulo=params.get("titulo", "Diagnóstico do Ecossistema"),
                    resumo=params.get("resumo", corpus[:1000]),
                    metodologia=params.get("metodologia", ""),
                    resultados=params.get("resultados", ""),
                    conclusoes=params.get("conclusoes", ""),
                    palavras_chave=params.get("palavras_chave"),
                    area_conhecimento=params.get("area_conhecimento", effective_domain),
                )
                report["social_impact"] = {
                    "sroi_ratio": getattr(getattr(sr, "sroi", None), "ratio", None),
                    "summary": str(sr)[:800],
                }
            except Exception as exc:
                report["social_impact"] = {"error": str(exc)}

        # 4.5 Scanner de Impacto Jurídico / Metacognitivo
        if include_legal_impact:
            try:
                params = legal_params or {}
                lr = self.legal_impact.analyze_research_paper(
                    titulo=params.get("titulo", "Diagnóstico Jurídico do Artefato"),
                    resumo=params.get("resumo", corpus[:1200]),
                    metodologia=params.get("metodologia", ""),
                    resultados=params.get("resultados", ""),
                    conclusoes=params.get("conclusoes", ""),
                    palavras_chave=params.get("palavras_chave"),
                    area_conhecimento=params.get("area_conhecimento", effective_domain),
                )
                report["legal_impact"] = {
                    "overall_score": lr.overall_score,
                    "legal_readiness": lr.legal_readiness,
                    "high_risk_flags": lr.high_risk_flags,
                    "metacognitive_gain_score": lr.metacognitive_gain_score,
                    "summary": lr.as_dict(),
                }
            except Exception as exc:
                report["legal_impact"] = {"error": str(exc)}

        # 5. Síntese evolutiva (SPEC-022: gaps REALs = ausentes + teleo)
        teleo_gaps = len(report.get("teleological", {}).get("gaps", []))
        gaps_total = absent_categories + teleo_gaps
        report["evolutionary"] = {
            "total_gaps": gaps_total,
            "absent_categories": absent_categories,
            "teleological_gaps": teleo_gaps,
            "recommendation": self._evolve_recommendation(
                gaps_total, effective_domain, report.get("ecosystem_layers")),
        }

        # 5.5 Modo profundo: roadmap evolutivo completo + priorização +
        #     sucessores (Anexos 3–8 — SPEC-020)
        if deep:
            self._run_deep(report, trail, goal_objs if effective_goals else [], noo, effective_domain)

        # 6. Scanner de Engenharia Reversa
        try:
            rev = self.reversa.scan(corpus)
            report["reversa"] = {
                "score": rev.score,
                "findings": rev.findings,
                "recommendations": rev.recommendations
            }
        except Exception as exc:
            report["reversa"] = {"error": str(exc)}

        report["duration_s"] = round(time.time() - started, 3)
        metabus.publish_subsystem_event(
            "diagnostic",
            "pipeline.completed",
            {
                "domain": effective_domain,
                "duration_s": report["duration_s"],
                "total_gaps": report.get("evolutionary", {}).get("total_gaps", 0),
                "deep": bool(deep),
            },
            source_agent="diagnostic_pipeline",
        )
        metabus.memory.upsert_semantic_topic(
            "diagnostic.pipeline",
            lesson=f"Diagnóstico concluído no domínio {effective_domain or 'geral'} com {report.get('evolutionary', {}).get('total_gaps', 0)} gaps.",
            metadata={"last_domain": effective_domain, "last_duration_s": report["duration_s"]},
        )
        return report

    @staticmethod
    def _evolve_recommendation(gaps_total: int, domain: str,
                                layers: Any = None) -> str:
        """Gera recomendação evolutiva contextualizada (SPEC-022)."""
        if layers and isinstance(layers, dict):
            # Encontra camada mais crítica
            worst_layer = min(layers.items(),
                              key=lambda kv: kv[1].get("coverage_pct", 100))
            layer_name = worst_layer[0]
            layer_pct = worst_layer[1].get("coverage_pct", 0)
            if layer_pct < 20:
                return (f"Atenção: Camada '{layer_name}' com apenas {layer_pct}% de cobertura. "
                        f"Priorizar antes de novas features.")
            elif layer_pct < 50:
                return (f"Camada '{layer_name}' em cobertura parcial ({layer_pct}%). "
                        f"Fortalecer antes de expandir.")

        if gaps_total == 0:
            return "Ecossistema saudável — evoluir por otimização incremental."
        if domain == "ecosystem":
            return (f"Ecossistema com {gaps_total} lacunas. "
                    f"Priorizar fechamento de componentes ausentes críticos.")
        return (f"Priorizar fechamento de lacunas críticas ({gaps_total} gaps) "
                f"antes de novas features.")

    # ------------------------------------------------------------------
    def _run_deep(self, report: Dict[str, Any], trail: Any,
                  goal_objs: List[Any], noo: Dict[str, Any],
                  domain: str) -> None:
        """Executa a camada profunda: roadmap M1–M5, priorização
        epistemológica e sucessores plausíveis."""
        roadmap = None
        analogies: List[Any] = []
        capability_units: List[Any] = []

        # a) Roadmap evolutivo completo (Trajetórias + Composição +
        #    Sequenciamento) — requer metas
        if goal_objs:
            try:
                from scanners.evolutionary_pipeline import EvolutionaryScannerPipeline
                evo = EvolutionaryScannerPipeline()
                roadmap = evo.scan(trail, goal_objs, domain)
                analogies = list(getattr(roadmap, "analogies", []) or [])
                capability_units = list(
                    getattr(roadmap, "capability_units", []) or [])
                seq = getattr(roadmap, "sequencing", None)
                report["roadmap"] = {
                    "noological_coverage": getattr(
                        roadmap, "noological_coverage", None),
                    "teleological_score": getattr(
                        roadmap, "teleological_score", None),
                    "total_gaps": getattr(roadmap, "total_gaps", 0),
                    "quick_wins": getattr(roadmap, "quick_wins", 0),
                    "foundations": getattr(roadmap, "foundations", 0),
                    "frontiers": getattr(roadmap, "frontiers", 0),
                    "bottlenecks": getattr(roadmap, "bottlenecks", []),
                    "total_construction_cost": getattr(
                        roadmap, "total_construction_cost", None),
                    "logical_sequence": (getattr(seq, "logical_sequence", [])
                                         if seq else []),
                }
            except Exception as exc:
                report["roadmap"] = {"error": str(exc)}

        # b) Priorização Epistemológica: erro → ausência → oportunidade
        try:
            opps = self.prioritizer.prioritize(
                noo or {}, analogies=analogies,
                capability_units=capability_units)
            report["epistemic_opportunities"] = {
                "total": len(opps),
                "breakthroughs": sum(1 for o in opps
                                     if o.tier == "breakthrough"),
                "top": [o.to_dict() for o in opps[:8]],
                "report_md": self.prioritizer.generate_report(opps[:15]),
            }
        except Exception as exc:
            report["epistemic_opportunities"] = {"error": str(exc)}

        # c) Sucessores plausíveis a partir do DNA estrutural
        try:
            dna = self.potentiality.extract_dna()
            successors = self.successor_gen.generate(dna, theme=domain)
            report["successors"] = {
                "total": len(successors),
                "immediate": sum(1 for s in successors
                                 if s.tier == "imediato"),
                "top": [s.to_dict() for s in successors[:8]],
                "report_md": self.successor_gen.generate_report(successors),
            }
        except Exception as exc:
            report["successors"] = {"error": str(exc)}


# Singleton — modo ecossistema como padrão (SPEC-022)
diagnostic_pipeline = DiagnosticPipeline(domain="ecosystem")
