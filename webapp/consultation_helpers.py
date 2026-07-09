# -*- coding: utf-8 -*-
"""
Helpers de Consulta e Producao para a interface web.

Oferece funcoes de busca, navegacao e visualizacao dos artefatos
produzidos pelo ecossistema: ciclos evolutivos, evidencias,
producoes cientificas, etc.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# =========================================================================
# Evolution Registry
# =========================================================================

def load_evolution_cycles(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Carrega ciclos de evolution/cycles.json."""
    path = ROOT / "evolution" / "cycles.json"
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    cycles = data.get("cycles", [])
    if limit:
        cycles = cycles[-limit:]
    return cycles

def get_evolution_stats(cycles: List[Dict]) -> Dict[str, Any]:
    """Calcula estatisticas dos ciclos de evolucao."""
    if not cycles:
        return {"count": 0, "avg_score": 0, "max_score": 0, "min_score": 0}
    scores = [c.get("score", 0) for c in cycles if c.get("score")]
    lessons = sum(len(c.get("lessons", [])) for c in cycles)
    return {
        "count": len(cycles),
        "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "total_lessons": lessons,
        "first_cycle": cycles[0].get("round_id", "N/A"),
        "last_cycle": cycles[-1].get("round_id", "N/A"),
    }

def search_cycles(query: str, cycles: List[Dict]) -> List[Dict]:
    """Busca ciclos por palavra-chave no objetivo ou licoes."""
    q = query.lower()
    results = []
    for c in cycles:
        obj = c.get("objective", "").lower()
        lessons = " ".join(c.get("lessons", [])).lower()
        changes = " ".join(c.get("changes", [])).lower()
        if q in obj or q in lessons or q in changes:
            results.append(c)
    return results

# =========================================================================
# Producao Cientifica (past research outputs)
# =========================================================================

def list_producoes(limit: int = 20) -> List[Dict[str, Any]]:
    """Lista pastas de producao cientifica."""
    base = ROOT / "producao_cientifica"
    if not base.exists():
        return []
    folders = sorted(base.iterdir(), key=os.path.getmtime, reverse=True)[:limit]
    producoes = []
    for f in folders:
        if f.is_dir():
            manifest_path = f / "pesquisa" / "RESEARCH_MANIFEST.json"
            manifest = {}
            if manifest_path.exists():
                with open(manifest_path) as mf:
                    manifest = json.load(mf)
            producoes.append({
                "folder": f.name,
                "path": str(f),
                "created": datetime.fromtimestamp(os.path.getmtime(f)).isoformat(),
                "manifest": manifest,
                "has_pdfs": len(list(f.rglob("*.pdf"))) > 0,
                "has_md": len(list(f.rglob("*.md"))) > 0,
            })
    return producoes

# =========================================================================
# Evidence browsing
# =========================================================================

def get_evidence_graph_summary() -> Dict[str, Any]:
    """Retorna sumario do grafo de evidencias (se existir)."""
    try:
        from agentic_science_v2.evidence_graph import EvidenceGraph
        g = EvidenceGraph()
        return {
            "entity_count": len(g.entities),
            "relation_count": len(g.relations),
            "evidence_count": len(g.evidences),
            "entity_types": list(g.ENTITY_TYPES),
            "relation_types": list(g.RELATION_TYPES),
        }
    except Exception as e:
        return {"error": str(e), "entity_count": 0, "relation_count": 0, "evidence_count": 0}

# =========================================================================
# Academic Search (wrapper for existing research tools)
# =========================================================================

def search_academic(topic: str, platforms: List[str] = None,
                    limit: int = 5) -> List[Dict[str, Any]]:
    """Busca literatura academica usando o orquestrador."""
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    orch = MarceloClaroOrchestrator()
    if platforms is None:
        platforms = ["arxiv"]
    try:
        results = orch.research_search(topic, platforms=platforms,
                                        limit_per_platform=limit)
        return results if isinstance(results, list) else []
    except Exception:
        return []

# =========================================================================
# Specs (SDD)
# =========================================================================

def list_specs() -> List[Dict[str, str]]:
    """Lista todas as specs disponiveis em specs/."""
    specs_dir = ROOT / "specs"
    if not specs_dir.exists():
        return []
    specs = []
    for f in sorted(specs_dir.glob("SPEC-*.md")):
        with open(f) as fh:
            first_line = fh.readline().strip("# \n")
        specs.append({
            "filename": f.name,
            "title": first_line,
            "path": str(f),
            "size": f.stat().st_size,
        })
    return specs

# =========================================================================
# MCP Tools status
# =========================================================================

def get_mcp_tools_list() -> List[Dict[str, str]]:
    """Retorna lista de ferramentas MCP disponiveis."""
    return [
        {"tool": "su_generate", "cycle": "R94", "description": "Gera pares de conceitos interdisciplinares"},
        {"tool": "su_evaluate", "cycle": "R94", "description": "Avalia tese interdisciplinar"},
        {"tool": "su_enrich", "cycle": "R89/R94", "description": "Enriquece tese com busca web"},
        {"tool": "su_visual_abstract", "cycle": "R90/R94", "description": "Gera abstract visual SVG"},
        {"tool": "su_peer_review", "cycle": "R91/R94", "description": "Revisao cega multi-LLM"},
        {"tool": "su_submission", "cycle": "R92/R94", "description": "Pacote de submissao Qualis A1"},
        {"tool": "su_novelty", "cycle": "R93/R94", "description": "Analise de novidade classica"},
        {"tool": "su_novelty_v2", "cycle": "R98/R99a", "description": "Analise V2 c/ contribution points"},
        {"tool": "su_dashboard", "cycle": "R94", "description": "Dashboard HTML interativo"},
        {"tool": "su_agentic_science", "cycle": "R101", "description": "Ciclo EvoSci completo"},
        {"tool": "su_deep_research", "cycle": "R102", "description": "Pesquisa profunda multi-fontes"},
        {"tool": "su_peer_review_v2", "cycle": "R103", "description": "Revisao agentiva c/ auditagem"},
        {"tool": "su_manuscript_revision", "cycle": "R104d", "description": "Revisao de manuscrito c/ diff"},
        {"tool": "su_paper_composer", "cycle": "R105", "description": "Composicao de paper ABNT/APA/IEEE"},
    ]

# =========================================================================
# Quality Report
# =========================================================================

def get_quality_summary() -> Dict[str, Any]:
    """Retorna sumario do ultimo relatorio de qualidade."""
    report_path = ROOT / "quality_report.json"
    if not report_path.exists():
        # Gera um relatorio rapido
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "quality_report.py"), "--quick", "--json"],
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout.strip()
            json_start = output.find("{")
            if json_start >= 0:
                return json.loads(output[json_start:])
        except Exception:
            pass
        return {"quality_score": {"overall_score": "N/A"}, "overall_status": "N/A"}
    with open(report_path) as f:
        return json.load(f)


# =========================================================================
# Dashboard HTML (embed)
# =========================================================================

def get_dashboard_html() -> str:
    """Retorna o HTML do dashboard interativo (se existir)."""
    dash_path = ROOT / "academic" / "dashboard" / "index.html"
    if dash_path.exists():
        with open(dash_path) as f:
            return f.read()
    return "<p>Dashboard ainda nao gerado. Execute o pipeline primeiro.</p>"


__all__ = [
    "load_evolution_cycles", "get_evolution_stats", "search_cycles",
    "list_producoes", "get_evidence_graph_summary",
    "search_academic", "list_specs", "get_mcp_tools_list",
    "get_quality_summary", "get_dashboard_html",
]
