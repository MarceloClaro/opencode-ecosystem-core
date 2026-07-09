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
   su_novelty           - Analise de novidade academica (classica)
   su_novelty_v2        - [NOVO] Analise V2 com contribution points e taxonomia
   su_dashboard         - Gera dashboard HTML interativo
   su_agentic_science   - [R101] Ciclo completo de descoberta cientifica autonomia
   su_deep_research     - [R102] Pesquisa profunda multi-fontes com Evidence Graph
   su_peer_review_v2    - [R103] Revisao por pares agentiva com auditagem em grafo

SPEC-935-R94 — R94 do OpenCode Ecosystem Core.
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("su-mcp-server")
logger.setLevel(logging.WARNING)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SimpleMCPServer:
    """Servidor MCP leve via stdio — mesmo padrao do mci/mcp_server.py.

    Attributes:
        name: Nome do servidor.
        tools: Dict de ferramentas registradas.
        security: Dict opcional com componentes de seguranca (R100).
    """

    def __init__(self, name: str, security: Optional[Dict[str, Any]] = None):
        self.name = name
        self.tools = {}
        self.security = security or {}

    def register_tool(self, name: str, description: str, schema: Dict, handler: callable):
        # Aplica MCPGuard se disponivel
        guard = self.security.get("guard")
        if guard:
            handler = guard.wrap(name, handler, schema)

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
            caller = params.get("caller", "unknown")
            start = time.time()

            # Security checks (R100)
            limiter = self.security.get("limiter")
            vetter = self.security.get("vetter")
            audit = self.security.get("audit")

            # Rate limiting
            if limiter and not limiter.allow(caller):
                audit and audit.log(tool_name, tool_args,
                                    {"error": "rate_limit_exceeded"}, 0, caller)
                return {
                    "isError": True,
                    "content": [{"type": "text",
                                "text": f"Rate limit exceeded for caller '{caller}'"}],
                }

            # Tool vetting
            if vetter:
                vetter_result = vetter.scan_args(tool_args)
                if vetter_result["suspicious"]:
                    audit and audit.log(tool_name, tool_args,
                                        {"error": "suspicious_input",
                                         "flags": vetter_result["flags"]},
                                        time.time() - start, caller)
                    return {
                        "isError": True,
                        "content": [{"type": "text",
                                    "text": f"Input rejected: suspicious patterns detected "
                                            f"({', '.join(vetter_result['flags'])})"}],
                    }

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name]["handler"](tool_args)
                    audit and audit.log(tool_name, tool_args, result,
                                        time.time() - start, caller)
                    return {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    }
                except Exception as e:
                    audit and audit.log(tool_name, tool_args,
                                        {"error": str(e)}, time.time() - start, caller)
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


def handle_novelty_v2(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa novidade academica V2 — pipeline OpenNovelty-style com contribution points, taxonomia e discrepancia."""
    from synthetic_university.novelty_v2 import NoveltyAnalyzerV2

    thesis = {
        "thesis_id": args.get("thesis_id", "unknown"),
        "title": args.get("title", "Untitled"),
        "hypothesis": args.get("hypothesis", ""),
        "abstract": args.get("abstract", args.get("hypothesis", "")),
        "methodology": args.get("methodology", ""),
        "concepts": args.get("concepts", [args.get("title", "concept")]),
        "composite_score": args.get("score", 0.5),
    }

    analyzer = NoveltyAnalyzerV2(lang=args.get("lang", "en"))
    report = analyzer.analyze(thesis)

    return {
        "success": True,
        "global_novelty_score": round(report.global_novelty_score, 1),
        "per_point_scores": {
            pid: {"type": ns.point_type, "score": round(ns.novelty_score, 1),
                  "evidence": ns.evidence[:200], "gap": ns.gap_identified[:200]}
            for pid, ns in report.per_point_scores.items() if pid != "_global"
        },
        "n_points": len(report.per_point_scores) - 1,
        "taxonomy_areas": [c.name for c in report.taxonomy_tree.children],
        "top_related": [w.get("title", "") for w in report.top_related_works[:3]],
        "discrepancy": report.discrepancy_analysis[:300],
        "positioning": report.positioning_statement[:300],
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

# Security components (R100)
from synthetic_university.mcp_security import MCPGuard, AuditLogger, ToolVetter, RateLimiter

_security = {
    "guard": MCPGuard(),
    "audit": AuditLogger(),
    "vetter": ToolVetter(),
    "limiter": RateLimiter(max_calls=30, window_seconds=60),
}

server = SimpleMCPServer("synthetic-university", security=_security)

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
    name="su_novelty_v2",
    description="[V2] Analisa novidade academica com pipeline OpenNovelty-style: extracao de contribution points, taxonomia hierarquica e analise de discrepancia.",
    schema={
        "type": "object",
        "properties": {
            "thesis_id": {"type": "string"},
            "title": {"type": "string"},
            "hypothesis": {"type": "string"},
            "abstract": {"type": "string"},
            "methodology": {"type": "string"},
            "concepts": {"type": "array", "items": {"type": "string"}},
            "lang": {"type": "string", "default": "en"},
        },
        "required": ["thesis_id", "title"],
    },
    handler=handle_novelty_v2,
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


# ============================================================
# R101 — Agentic Science V2
# ============================================================

def handle_agentic_science(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executa ciclo de descoberta cientifica autonomia."""
    from agentic_science_v2.orchestrator import run_agentic_science_v2
    return run_agentic_science_v2(
        seed_domain=args.get("seed_domain"),
        max_rounds=args.get("max_rounds", 3),
    )

server.register_tool(
    name="su_agentic_science",
    description=(
        "[R101] Ciclo completo de descoberta cientifica autonomia "
        "com multiagentes bio-inspirados (Mentor, Researcher, Reviewer). "
        "Gera ideias, avalia, evolui e destila memorias."
    ),
    schema={
        "type": "object",
        "properties": {
            "seed_domain": {
                "type": "string",
                "description": "Dominio cientifico inicial (ex: Quantum ML)",
                "default": "",
            },
            "max_rounds": {
                "type": "integer",
                "description": "Numero maximo de ciclos evolutivos",
                "default": 3,
            },
        },
    },
    handler=handle_agentic_science,
)

# ============================================================
# R102 — Deep Research Agent
# ============================================================

def handle_deep_research(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executa pesquisa profunda multi-fontes."""
    from agentic_science_v2.deep_research import run_deep_research
    return run_deep_research(
        question=args.get("question", ""),
        max_rounds=args.get("max_rounds", 2),
        max_depth=args.get("max_depth", 3),
    )

server.register_tool(
    name="su_deep_research",
    description=(
        "[R102] Pesquisa profunda multi-fontes com orquestracao BF/DF, "
        "Evidence Graph incremental e sintese de relatorio. "
        "Baseado no DeepEvidence (Nature Machine Intelligence 2026)."
    ),
    schema={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Pergunta de pesquisa",
            },
            "max_rounds": {
                "type": "integer",
                "description": "Rodadas maximas de pesquisa",
                "default": 2,
            },
            "max_depth": {
                "type": "integer",
                "description": "Profundidade maxima de investigacao",
                "default": 3,
            },
        },
        "required": ["question"],
    },
    handler=handle_deep_research,
)

# ============================================================
# R103 — Agentic Peer Review
# ============================================================

def handle_peer_review_v2(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executa revisao por pares agentiva com auditagem."""
    from agentic_science_v2.review_agent import run_peer_review
    return run_peer_review(
        paper_title=args.get("title", "Untitled"),
        paper_abstract=args.get("abstract", ""),
        paper_sections=args.get("sections", [
            "Introduction", "Methodology", "Experiments",
            "Results", "Discussion",
        ]),
        citations=args.get("citations", []),
    )

server.register_tool(
    name="su_peer_review_v2",
    description=(
        "[R103] Revisao por pares agentiva com auditagem baseada em grafo. "
        "8 rubricas multi-dimensionais, ledger claim-evidence-risk, "
        "4 revisores especialistas, export gate com traceability. "
        "Baseado em REVIEWGROUNDER (ACL 2026) e DeepReviewer 2.0 (arXiv 2026)."
    ),
    schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Titulo do paper",
            },
            "abstract": {
                "type": "string",
                "description": "Resumo do paper",
            },
            "sections": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de secoes do paper",
            },
            "citations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista de citacoes",
            },
        },
    },
    handler=handle_peer_review_v2,
)


# ============================================================
# R104 — Agentic Manuscript Revision
# ============================================================

def handle_manuscript_revision(args: Dict[str, Any]) -> Dict[str, Any]:
    """Executa revisao agentiva de manuscrito pos-peer-review."""
    from agentic_science_v2.revision_agent import create_revision
    review_package = args.get("review_package", {})
    manuscript = args.get("manuscript", "")
    return create_revision(review_package, manuscript)

server.register_tool(
    name="su_manuscript_revision",
    description=(
        "[R104] Revisao agentiva de manuscritos academicos pos-peer-review. "
        "Toma ReviewPackage do R103 e gera revision proposals, "
        "diff controlado, rebuttal letter ponto-a-ponto. "
        "Baseado em ReViewGraph e DeepReviewer 2.0."
    ),
    schema={
        "type": "object",
        "properties": {
            "review_package": {
                "type": "object",
                "description": "ReviewPackage do R103 contendo claims, risks, evidence",
            },
            "manuscript": {
                "type": "string",
                "description": "Texto completo do manuscrito",
            },
        },
        "required": ["review_package", "manuscript"],
    },
    handler=handle_manuscript_revision,
)


# ============================================================
# R105 — Agentic Paper Composer
# ============================================================

def handle_paper_composer(args: Dict[str, Any]) -> Dict[str, Any]:
    """Compoe manuscrito academico completo a partir de R101-R104 outputs."""
    from agentic_science_v2.paper_composer import compose_paper
    return compose_paper(
        title=args.get("title", "Untitled"),
        discoveries=args.get("discoveries", []),
        evidence_graph=args.get("evidence_graph", {}),
        review=args.get("review", {}),
        revisions=args.get("revisions", []),
        venue=args.get("venue", "apa"),
        keywords=args.get("keywords", []),
        references=args.get("references", []),
    )

server.register_tool(
    name="su_paper_composer",
    description=(
        "[R105] Composicao agentiva de manuscritos academicos. "
        "Integra outputs de R101 (descoberta), R102 (evidencias), "
        "R103 (revisao) e R104 (revisao de manuscrito) para gerar "
        "artigo completo em formatos ABNT, APA ou IEEE. "
        "Inclui StructurePlanner, SectionWriter, CitationFormatter, "
        "CrossConsistencyVerifier. Baseado em PaperAgent (arXiv 2026)."
    ),
    schema={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Titulo do artigo",
            },
            "discoveries": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Lista de descobertas do R101 Agentic Science",
            },
            "evidence_graph": {
                "type": "object",
                "description": "Evidence Graph do R102 Deep Research",
            },
            "review": {
                "type": "object",
                "description": "ReviewPackage do R103 Peer Review",
            },
            "revisions": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Revisions do R104 Manuscript Revision",
            },
            "venue": {
                "type": "string",
                "enum": ["apa", "abnt", "ieee"],
                "default": "apa",
                "description": "Formato do venue (APA, ABNT, IEEE)",
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Palavras-chave",
            },
            "references": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Referencias bibliograficas",
            },
        },
        "required": ["title"],
    },
    handler=handle_paper_composer,
)


if __name__ == "__main__":
    import sys
    server.run_stdio()
