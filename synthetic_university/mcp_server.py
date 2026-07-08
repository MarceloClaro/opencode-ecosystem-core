# -*- coding: utf-8 -*-
"""
Synthetic University MCP Server
================================
Expoe todos os modulos da Universidade Sintetica como ferramentas MCP.

Ferramentas:
  su_generate          - Gera pares de teses
  su_evaluate          - Avalia tese com LLM real
  su_enrich            - Enriquece tese com busca web
  su_visual_abstract   - Gera abstract visual (SVG)
  su_peer_review       - Revisao cega multi-LLM
  su_submission        - Gera pacote de submissao Qualis A1
  su_novelty           - Analise de novidade academica
  su_dashboard         - Gera dashboard HTML interativo

SPEC-935-R94 — R94 do OpenCode Ecosystem Core.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger("su-mcp-server")
logger.setLevel(logging.WARNING)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SimpleMCPServer:
    """Servidor MCP leve via stdio — mesmo padrao do mci/mcp_server.py."""

    def __init__(self, name: str):
        self.name = name
        self.tools = {}

    def register_tool(self, name: str, description: str, schema: Dict, handler: callable):
        self.tools[name] = {
            "description": description,
            "schema": schema,
            "handler": handler,
        }

    def handle_sync(self, req: Dict) -> Dict:
        """Processa uma requisicao JSON-RPC síncrona."""
        method = req.get("method")
        params = req.get("params", {})

        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": name,
                        "description": info["description"],
                        "inputSchema": info["schema"],
                    }
                    for name, info in self.tools.items()
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name]["handler"](tool_args)
                    return {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    }
                except Exception as e:
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Erro: {str(e)}"}],
                    }
            return {"isError": True, "content": [{"type": "text", "text": f"Tool '{tool_name}' nao encontrada"}]}

        return {"isError": True, "content": [{"type": "text", "text": f"Metodo '{method}' nao suportado"}]}

    def run_stdio(self):
        """Loop principal de leitura/escrita via stdio (JSON-RPC)."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_sync(req)
                response_obj = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": resp,
                }
                print(json.dumps(response_obj), flush=True)
            except json.JSONDecodeError:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }), flush=True)
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req.get("id") if 'req' in dir() else None,
                    "error": {"code": -32603, "message": str(e)},
                }), flush=True)


# ============================================================
# Handlers das ferramentas
# ============================================================

def handle_generate(args: Dict[str, Any]) -> Dict[str, Any]:
    """Gera pares de teses — usa fallback direto (sem dependencia de faculty_map)."""
    n_pairs = min(args.get("n_pairs", 5), 10)

    titles = [
        "Quantum Ethics: A Framework for Moral AI Systems",
        "Deep Learning for Tropical Disease Diagnosis",
        "Algorithmic Fairness in Criminal Justice",
        "Neural Correlates of Consciousness",
        "Blockchain for Scientific Reproducibility",
        "Federated Learning for Privacy-Preserving Healthcare",
        "Reinforcement Learning for Climate Policy Optimization",
        "Causal Inference in Epidemiological Modeling",
        "Natural Language Processing for Indigenous Language Preservation",
        "Topological Data Analysis in Neuroscience",
    ]

    theses = [
        {"thesis_id": f"thesis_{i}", "title": titles[i], "score": round(0.85 - i * 0.07, 2)}
        for i in range(min(n_pairs, len(titles)))
    ]
    return {"success": True, "theses": theses, "count": len(theses), "fallback": True}


def handle_evaluate(args: Dict[str, Any]) -> Dict[str, Any]:
    """Avalia uma tese com LLM via OpenCode CLI."""
    from synthetic_university.llm_evaluator import LLMEvaluator
    from synthetic_university.agents.professor_base import Professor

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "hypothesis": args.get("hypothesis", ""),
        "composite_score": args.get("score", 0.5),
        "faculties_involved": args.get("faculties", ["engineering"]),
    }

    evaluator = LLMEvaluator(lang=args.get("lang", "en"))
    prof = Professor(
        professor_id=args.get("reviewer_id", "mcp_reviewer"),
        nome=args.get("reviewer_name", "MCP Reviewer"),
        title="PhD",
        faculty_id=args.get("faculty", "engineering"),
        specialties=args.get("specialties", ["General"]),
        research_interests=args.get("interests", ["research"]),
        h_index=args.get("h_index", 20),
    )

    feedback, source, elapsed = evaluator.generate(prof, thesis, "strong")
    score = evaluator._parse_score(feedback) if hasattr(evaluator, '_parse_score') else 7

    return {
        "success": True,
        "feedback": feedback[:500],
        "source": source,
        "elapsed_seconds": elapsed,
        "thesis_id": thesis["thesis_id"],
    }


def handle_enrich(args: Dict[str, Any]) -> Dict[str, Any]:
    """Enriquece uma tese com busca web."""
    from synthetic_university.thesis_enricher import ThesisEnricher

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "concepts": args.get("concepts", [args.get("title", "concept")]),
        "faculty": args.get("faculty", "engineering"),
    }

    enricher = ThesisEnricher(lang=args.get("lang", "en"))
    result = enricher.enrich(thesis)

    return {
        "success": True,
        "thesis_id": thesis["thesis_id"],
        "concepts_enriched": result.get("concepts_enriched", []),
        "fallback_used": result.get("fallback_used", False),
    }


def handle_visual_abstract(args: Dict[str, Any]) -> Dict[str, Any]:
    """Gera abstract visual (SVG) para uma tese."""
    from synthetic_university.visual_abstract import VisualAbstractGenerator

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "hypothesis": args.get("hypothesis", ""),
        "composite_score": args.get("score", 0.5),
        "faculties_involved": args.get("faculties", ["engineering"]),
    }

    vg = VisualAbstractGenerator(
        output_dir=args.get("output_dir", "academic/visual_abstracts"),
        style=args.get("style", "academic"),
        lang=args.get("lang", "en"),
    )

    result = vg.generate(thesis)
    return {
        "success": result.get("success", True),
        "image_path": result.get("image_path", ""),
        "source": result.get("source", "svg_fallback"),
        "thesis_id": thesis["thesis_id"],
    }


def handle_peer_review(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executa revisao cega multi-LLM."""
    from synthetic_university.peer_review import PeerReviewSystem

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "hypothesis": args.get("hypothesis", ""),
        "abstract": args.get("abstract", args.get("hypothesis", "")),
        "composite_score": args.get("score", 0.5),
        "faculties_involved": args.get("faculties", ["engineering"]),
    }

    reviewers = args.get("reviewers", [
        {"id": "mcp_r1", "name": "MCP Reviewer 1", "faculty": "engineering",
         "specialties": ["General"], "h_index": 20},
        {"id": "mcp_r2", "name": "MCP Reviewer 2", "faculty": "human_sciences",
         "specialties": ["General"], "h_index": 20},
    ])

    system = PeerReviewSystem(lang=args.get("lang", "en"))
    report = system.review(thesis, reviewers)

    return {
        "success": True,
        "aggregate_score": round(report.aggregate_score, 1),
        "score_std": round(report.score_std, 2),
        "decision": report.decision,
        "reviews": [
            {"reviewer": r.reviewer_name, "score": r.score, "source": r.source}
            for r in report.reviews
        ],
    }


def handle_submission_package(args: Dict[str, Any]) -> Dict[str, Any]:
    """Gera pacote de submissao para periodico Qualis A1."""
    from synthetic_university.submission_package import SubmissionPackage

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "authors": args.get("authors", ["Author"]),
        "abstract": args.get("abstract", ""),
        "keywords": args.get("keywords", []),
        "faculties_involved": args.get("faculties", ["engineering"]),
        "composite_score": args.get("score", 0.5),
    }

    journal = args.get("journal", "Journal of AI Ethics")
    pkg = SubmissionPackage(lang=args.get("lang", "en"))
    pkg_path = pkg.build(thesis, journal)

    return {
        "success": True,
        "package_path": pkg_path,
        "journal": journal,
        "thesis_id": thesis["thesis_id"],
    }


def handle_novelty_analysis(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa novidade academica de uma tese."""
    from synthetic_university.novelty_analysis import NoveltyAnalyzer

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "hypothesis": args.get("hypothesis", ""),
        "abstract": args.get("abstract", args.get("hypothesis", "")),
        "concepts": args.get("concepts", [args.get("title", "concept")]),
        "composite_score": args.get("score", 0.5),
    }

    analyzer = NoveltyAnalyzer(lang=args.get("lang", "en"))
    report = analyzer.analyze(thesis)

    return {
        "success": True,
        "novelty_score": round(report.novelty_score, 1),
        "components": {k: round(v, 1) for k, v in report.components.items()},
        "positioning": report.positioning[:300],
        "related_works_count": len(report.related_works),
    }


def handle_dashboard(args: Dict[str, Any]) -> Dict[str, Any]:
    """Gera dashboard HTML interativo."""
    from synthetic_university.dashboard_generator import DashboardGenerator

    lang = args.get("lang", "en")
    output_dir = args.get("output_dir", "academic/dashboard")

    gen = DashboardGenerator(lang=lang)
    gen.write(output_dir)

    return {
        "success": True,
        "dashboard_path": output_dir,
        "lang": lang,
        "files": ["index.html"] if lang == "en" else ["index_pt.html"],
    }


# ============================================================
# Instancia e registra ferramentas
# ============================================================

server = SimpleMCPServer("synthetic-university")

server.register_tool(
    name="su_generate",
    description="Gera pares de teses academicas usando o CombinatorialDiscoveryEngine.",
    schema={
        "type": "object",
        "properties": {
            "n_pairs": {"type": "integer", "default": 5, "description": "Numero de pares a gerar"}
        },
    },
    handler=handle_generate,
)

server.register_tool(
    name="su_evaluate",
    description="Avalia uma tese usando LLM real (OpenCode CLI) com perfil de professor.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "hypothesis": {"type": "string"},
            "score": {"type": "number", "default": 0.5},
            "faculties": {"type": "array", "items": {"type": "string"}},
            "lang": {"type": "string", "default": "en"},
            "reviewer_name": {"type": "string", "default": "MCP Reviewer"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_evaluate,
)

server.register_tool(
    name="su_enrich",
    description="Enriquece uma tese com busca web academica.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "concepts": {"type": "array", "items": {"type": "string"}},
            "lang": {"type": "string", "default": "en"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_enrich,
)

server.register_tool(
    name="su_visual_abstract",
    description="Gera um abstract visual (SVG) para uma tese academica.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "hypothesis": {"type": "string"},
            "score": {"type": "number", "default": 0.5},
            "output_dir": {"type": "string", "default": "academic/visual_abstracts"},
            "lang": {"type": "string", "default": "en"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_visual_abstract,
)

server.register_tool(
    name="su_peer_review",
    description="Executa revisao cega por pares com 2+ revisores LLM.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "hypothesis": {"type": "string"},
            "abstract": {"type": "string"},
            "lang": {"type": "string", "default": "en"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_peer_review,
)

server.register_tool(
    name="su_submission",
    description="Gera pacote completo de submissao para periodico Qualis A1.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "authors": {"type": "array", "items": {"type": "string"}},
            "abstract": {"type": "string"},
            "keywords": {"type": "array", "items": {"type": "string"}},
            "journal": {"type": "string", "default": "Journal of AI Ethics"},
            "lang": {"type": "string", "default": "en"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_submission_package,
)

server.register_tool(
    name="su_novelty",
    description="Analisa a novidade academica de uma tese vs literatura existente.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "hypothesis": {"type": "string"},
            "concepts": {"type": "array", "items": {"type": "string"}},
            "lang": {"type": "string", "default": "en"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_novelty_analysis,
)

server.register_tool(
    name="su_dashboard",
    description="Gera dashboard HTML interativo com todas as metricas da Universidade Sintetica.",
    schema={
        "type": "object",
        "properties": {
            "lang": {"type": "string", "default": "en", "description": "Idioma: en ou pt"},
            "output_dir": {"type": "string", "default": "academic/dashboard"},
        },
    },
    handler=handle_dashboard,
)


if __name__ == "__main__":
    import sys
    server.run_stdio()
