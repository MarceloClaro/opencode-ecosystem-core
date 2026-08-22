# -*- coding: utf-8 -*-
"""
ReversaBridge — ponte metacognitiva e de gaps (SPEC-935-R437)
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

from reversa_universal.engine import ReversaUniversalEngine, reversa_engine


def _slug(path: str) -> str:
    s = Path(path).name or "root"
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    s = re.sub(r"[-\s]+", "-", s)
    return s[:50] or "target"


class ReversaBridge:
    """Ponte que conecta engine a MetaBus, pesquisa, manuscrito e scanners."""

    def __init__(self, engine: Optional[ReversaUniversalEngine] = None, metabus: Any = None):
        self.engine = engine or reversa_engine
        if metabus is not None:
            self.metabus = metabus
        else:
            try:
                from mci.metabus import metabus as _mb

                self.metabus = _mb
            except Exception:
                self.metabus = None
        self._last_analysis: Optional[Dict[str, Any]] = None

    def analyze_and_reflect(self, path: str | Path, output_root: Optional[str | Path] = None) -> Dict[str, Any]:
        result = self.engine.analyze(path, output_root=output_root)
        self._last_analysis = result
        if self.metabus is not None:
            try:
                slug = _slug(str(path))
                gaps = result.get("gaps", {}).get("metrics", {}).get("total_gaps", 0)
                self.metabus.memory.add_reflection(
                    agent_id="reversa_bridge",
                    task_context=f"reversa universal: {path}",
                    reflection=f"Reversa universal analisou {path}: {len(result.get('modules',[]))} módulos, {gaps} gaps.",
                    score=min(1.0, 0.6 + gaps * 0.05) if isinstance(gaps, int) else 0.6,
                )
                self.metabus.memory.upsert_semantic_topic(
                    f"reversa_universal.{slug}",
                    lesson=f"Análise Reversa de {path}: {len(result.get('modules',[]))} módulos, {gaps} gaps. Frameworks: {', '.join(result.get('inventory',{}).get('frameworks',[])[:2])}",
                    metadata={"target": str(path), "modules": len(result.get("modules",[])), "gaps": gaps},
                )
                self.metabus.publish_subsystem_event(
                    "reversa_universal",
                    "bridge.analysis_reflected",
                    {"target": str(path), "modules": len(result.get("modules",[])), "gaps": gaps},
                    source_agent="reversa_bridge",
                )
            except Exception:
                pass
        return result

    def enhance_gaps(self, diagnostic_report: Dict[str, Any], analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Injeta gaps Reversa no report de diagnóstico."""
        if not isinstance(diagnostic_report, dict):
            return diagnostic_report
        analysis = analysis or self._last_analysis
        if not analysis:
            return diagnostic_report
        gaps_data = analysis.get("gaps", {})
        gaps = gaps_data.get("gaps", [])
        if not gaps:
            return diagnostic_report
        # Garante estruturas
        evo = diagnostic_report.setdefault("evolutionary", {})
        evo.setdefault("total_gaps", 0)
        # Injeta reversa_gaps
        reversa_gaps = [
            {"dimension": f"reversa:{g['type']}", "severity": g.get("severity","medium"), "description": g["description"]}
            for g in gaps
        ]
        evo["reversa_gaps"] = reversa_gaps
        evo["total_gaps"] = int(evo.get("total_gaps", 0)) + len(reversa_gaps)
        # Seção reversa dedicada
        diagnostic_report["reversa"] = {
            "score": max(0.0, min(10.0, 5.0 + len(gaps) * 0.8)),
            "findings": [g["description"] for g in gaps],
            "recommendations": analysis.get("recommendations", [])[:5],
            "correlations": gaps_data.get("correlations", []),
            "solutions": gaps_data.get("solutions", []),
            "innovations": gaps_data.get("innovations", []),
        }
        # Recomendações evolutivas: prioriza gaps críticos
        if gaps:
            evo["recommendation"] = f"Reversa detectou {len(gaps)} gaps estruturais ({', '.join(g['type'] for g in gaps[:3])}) — priorizar soluções: {'; '.join(gaps_data.get('solutions',[])[:1])}"
        return diagnostic_report

    def status(self) -> Dict[str, Any]:
        last = self._last_analysis
        return {
            "engine_available": self.engine is not None,
            "last_target": last.get("target") if isinstance(last, dict) else None,
            "last_modules": len(last.get("modules", [])) if isinstance(last, dict) else 0,
            "last_gaps": last.get("gaps", {}).get("metrics", {}).get("total_gaps", 0) if isinstance(last, dict) else 0,
            "metacognitive_topics": len(getattr(self.metabus.memory, "semantic", {})) if self.metabus and hasattr(self.metabus, "memory") else 0,
        }


reversa_bridge = ReversaBridge()
