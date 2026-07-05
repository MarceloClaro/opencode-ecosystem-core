# -*- coding: utf-8 -*-
"""
Diagnostic Pipeline — Pipeline unificado dos 5 Scanners
=======================================================
Orquestra em sequência os scanners portados do OpenCode_Ecosystem:

1. NoologicalScanner        — cobertura epistemológica (dimensões do conhecimento)
2. TeleologicalReverseScanner — lacunas entre metas e capacidades
3. EvolutionaryPipeline     — roadmap evolutivo (rotas de melhoria)
4. PotentialityScanner      — potenciais latentes de componentes
5. SocialImpactScanner      — SROI, ToC, SDG, B-Impact

Entrada mínima: um "audit_trail" (qualquer objeto com texto, ou dict/list) e
metas opcionais. Saída: DiagnosticReport consolidado (dict serializável).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from scanners.noological_scanner import NoologicalScanner
from scanners.teleological_scanner import TeleologicalReverseScanner, TeleologicalGoal
from scanners.evolutionary_pipeline import EvolutionaryRoadmap  # noqa: F401 (reexport)
from scanners.potentiality_scanner import PotentialityScanner
from scanners.social_impact_scanner import SocialImpactScanner
from scanners.reversa_scanner import ReversaScanner
from scanners.epistemic_prioritizer import EpistemicPrioritizer
from scanners.successor_generator import SuccessorGenerator


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
    """Pipeline de diagnóstico unificado do ecossistema."""

    def __init__(self):
        self.noological = NoologicalScanner()
        self.teleological = TeleologicalReverseScanner()
        self.potentiality = PotentialityScanner()
        self.social = SocialImpactScanner()
        self.reversa = ReversaScanner()
        self.prioritizer = EpistemicPrioritizer()
        self.successor_gen = SuccessorGenerator()

    def run(self, corpus: str, domain: str = "",
            goals: Optional[List[Dict[str, Any]]] = None,
            include_social: bool = False,
            social_params: Optional[Dict[str, Any]] = None,
            deep: bool = False) -> Dict[str, Any]:
        """Executa o pipeline completo de diagnóstico.

        Args:
            corpus: texto a diagnosticar (manuscrito, log de sessão, plano)
            domain: domínio de pesquisa (ex.: "machine_learning")
            goals: lista de metas [{"name":..., "description":..., "weight":...}]
            include_social: se True, roda o SocialImpactScanner
            social_params: parâmetros para analyze_research_paper
            deep: se True, roda também o roadmap evolutivo completo
                (Trajetórias M1–M5 + Composição Unitária + Sequenciamento),
                a Priorização Epistemológica (erro→ausência→oportunidade)
                e o Gerador de Sucessores Plausíveis
        """
        started = time.time()
        trail = _TextAuditTrail(corpus)
        report: Dict[str, Any] = {"domain": domain, "started_at": started}

        # 1. Scanner Noológico
        try:
            noo = self.noological.scan(trail, research_domain=domain)
            report["noological"] = {
                "coverage": noo.get("overall_coverage", noo.get("coverage", 0)),
                "gaps": noo.get("gaps", [])[:10],
                "summary": {k: v for k, v in noo.items()
                            if isinstance(v, (int, float, str))},
            }
        except Exception as exc:  # scanner não deve derrubar o pipeline
            report["noological"] = {"error": str(exc)}
            noo = {}

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
                for i, g in enumerate(goals or [])
            ]
            if goal_objs:
                self.teleological.set_goals(goal_objs)
                self.teleological.infer_requirements()
                gaps = self.teleological.compare_with_scan(noo or {})
                score = self.teleological.teleological_score
                report["teleological"] = {
                    "score": score() if callable(score) else score,
                    "gaps": [
                        {"dimension": getattr(g, "dimension", ""),
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
                    area_conhecimento=params.get("area_conhecimento", domain),
                )
                report["social_impact"] = {
                    "sroi_ratio": getattr(getattr(sr, "sroi", None), "ratio", None),
                    "summary": str(sr)[:800],
                }
            except Exception as exc:
                report["social_impact"] = {"error": str(exc)}

        # 5. Síntese evolutiva simplificada: prioriza lacunas encontradas
        gaps_total = (
            len(report.get("noological", {}).get("gaps", []))
            + len(report.get("teleological", {}).get("gaps", []))
        )
        report["evolutionary"] = {
            "total_gaps": gaps_total,
            "recommendation": (
                "Ecossistema saudável — evoluir por otimização incremental."
                if gaps_total <= 3 else
                "Priorizar fechamento de lacunas críticas antes de novas features."
            ),
        }

        # 5.5 Modo profundo: roadmap evolutivo completo + priorização +
        #     sucessores (Anexos 3–8 — SPEC-020)
        if deep:
            self._run_deep(report, trail, goal_objs if goals else [], noo, domain)

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
        return report

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


# Singleton
diagnostic_pipeline = DiagnosticPipeline()
