# -*- coding: utf-8 -*-
"""
Academic API Gateway — R96
===========================
Gateway REST (FastAPI) que expõe os módulos da Universidade Sintética
como endpoints HTTP.

Uso:
    # Instalar dependências
    pip install fastapi uvicorn

    # Executar
    uvicorn synthetic_university.api_gateway:app --reload

    # Ou via Python
    python -m synthetic_university.api_gateway

Endpoints:
    GET  /health                → status do servidor
    GET  /tools                 → lista de ferramentas disponíveis
    POST /tools/generate        → gera teses
    POST /tools/evaluate        → avalia tese
    POST /tools/enrich          → enriquece tese
    POST /tools/visual-abstract → gera abstract visual
    POST /tools/peer-review     → executa revisão por pares
    POST /tools/submission      → gera pacote de submissão
    POST /tools/novelty         → analisa novidade (classica)
    POST /tools/novelty-v2      → [NOVO] analise V2 com contribution points
    POST /tools/dashboard       → gera dashboard

SPEC-935-R96.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ============================================================
# Import condicional do FastAPI
# ============================================================

try:
    from fastapi import FastAPI, HTTPException, Request
    from pydantic import BaseModel

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


# ============================================================
# Handlers (reutilizados do MCP server)
# ============================================================

def _import_handlers():
    """Importa handlers do MCP server sob demanda."""
    from synthetic_university.mcp_server import (
        handle_generate,
        handle_evaluate,
        handle_enrich,
        handle_visual_abstract,
        handle_peer_review,
        handle_submission_package,
        handle_novelty_analysis,
        handle_novelty_v2,
        handle_dashboard,
    )
    return {
        "generate": handle_generate,
        "evaluate": handle_evaluate,
        "enrich": handle_enrich,
        "visual-abstract": handle_visual_abstract,
        "peer-review": handle_peer_review,
        "submission": handle_submission_package,
        "novelty": handle_novelty_analysis,
        "novelty-v2": handle_novelty_v2,
        "dashboard": handle_dashboard,
    }


TOOL_DESCRIPTIONS = {
    "generate": "Gera pares de teses academicas",
    "evaluate": "Avalia uma tese usando LLM real",
    "enrich": "Enriquece uma tese com busca web",
    "visual-abstract": "Gera um abstract visual (SVG) para uma tese",
    "peer-review": "Executa revisao cega por pares multi-LLM",
    "submission": "Gera pacote de submissao para periodico Qualis A1",
    "novelty": "Analisa a novidade academica de uma tese",
    "novelty-v2": "[V2] Analise OpenNovelty-style com contribution points, taxonomia e discrepancia",
    "dashboard": "Gera dashboard HTML interativo",
}


# ============================================================
# Criação da aplicação (condicional)
# ============================================================

if HAS_FASTAPI:

    app = FastAPI(
        title="Synthetic University API Gateway",
        description="REST API para os módulos da Universidade Sintética",
        version="1.0.0",
    )

    # --- Models Pydantic ---

    class GenerateRequest(BaseModel):
        n_pairs: int = 5

    class EvaluateRequest(BaseModel):
        thesis_id: str
        title: str
        hypothesis: str = ""
        score: float = 0.5
        faculties: list = ["engineering"]
        lang: str = "en"
        reviewer_name: str = "API Reviewer"

    class EnrichRequest(BaseModel):
        thesis_id: str
        title: str
        concepts: list = []
        lang: str = "en"

    class VisualAbstractRequest(BaseModel):
        thesis_id: str
        title: str
        hypothesis: str = ""
        score: float = 0.5
        output_dir: str = "academic/visual_abstracts"
        lang: str = "en"

    class PeerReviewRequest(BaseModel):
        thesis_id: str
        title: str
        hypothesis: str = ""
        abstract: str = ""
        lang: str = "en"

    class SubmissionRequest(BaseModel):
        thesis_id: str
        title: str
        authors: list = ["Author"]
        abstract: str = ""
        keywords: list = []
        journal: str = "Journal of AI Ethics"
        lang: str = "en"

    class NoveltyRequest(BaseModel):
        thesis_id: str
        title: str
        hypothesis: str = ""
        concepts: list = []
        lang: str = "en"

    class NoveltyV2Request(BaseModel):
        thesis_id: str
        title: str
        hypothesis: str = ""
        abstract: str = ""
        methodology: str = ""
        concepts: list = []
        lang: str = "en"

    class DashboardRequest(BaseModel):
        lang: str = "en"
        output_dir: str = "academic/dashboard"

    # --- Endpoints ---

    @app.get("/health")
    async def health():
        """Health check."""
        return {"status": "ok", "version": "1.0.0"}

    @app.get("/tools")
    async def list_tools():
        """Lista ferramentas disponíveis."""
        tools = [
            {"name": name, "description": desc}
            for name, desc in TOOL_DESCRIPTIONS.items()
        ]
        return {"tools": tools}

    def _call_handler(handler, args: Dict[str, Any]) -> Dict[str, Any]:
        """Chama um handler e retorna resultado ou erro."""
        try:
            return handler(args)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tools/generate")
    async def generate(req: GenerateRequest):
        return _call_handler(
            _import_handlers()["generate"], {"n_pairs": req.n_pairs}
        )

    @app.post("/tools/evaluate")
    async def evaluate(req: EvaluateRequest):
        return _call_handler(
            _import_handlers()["evaluate"], req.model_dump()
        )

    @app.post("/tools/enrich")
    async def enrich(req: EnrichRequest):
        return _call_handler(
            _import_handlers()["enrich"], req.model_dump()
        )

    @app.post("/tools/visual-abstract")
    async def visual_abstract(req: VisualAbstractRequest):
        return _call_handler(
            _import_handlers()["visual-abstract"], req.model_dump()
        )

    @app.post("/tools/peer-review")
    async def peer_review(req: PeerReviewRequest):
        return _call_handler(
            _import_handlers()["peer-review"], req.model_dump()
        )

    @app.post("/tools/submission")
    async def submission(req: SubmissionRequest):
        return _call_handler(
            _import_handlers()["submission"], req.model_dump()
        )

    @app.post("/tools/novelty")
    async def novelty(req: NoveltyRequest):
        return _call_handler(
            _import_handlers()["novelty"], req.model_dump()
        )

    @app.post("/tools/novelty-v2")
    async def novelty_v2(req: NoveltyV2Request):
        return _call_handler(
            _import_handlers()["novelty-v2"], req.model_dump()
        )

    @app.post("/tools/dashboard")
    async def dashboard(req: DashboardRequest):
        return _call_handler(
            _import_handlers()["dashboard"], req.model_dump()
        )

else:
    # Placeholder quando FastAPI não está instalado
    app = None  # type: ignore

    def create_app_stub():
        """Retorna um dicionário descritivo quando FastAPI não está disponível."""
        return {
            "error": "FastAPI nao instalado. Execute: pip install fastapi uvicorn",
            "tools": list(TOOL_DESCRIPTIONS.keys()),
        }


# ============================================================
# CLI para execução direta
# ============================================================

def main():
    """Executa o servidor via uvicorn (se disponível)."""
    if not HAS_FASTAPI:
        print("Erro: FastAPI nao instalado. Execute: pip install fastapi uvicorn")
        sys.exit(1)

    try:
        import uvicorn
    except ImportError:
        print("Erro: uvicorn nao instalado. Execute: pip install uvicorn")
        sys.exit(1)

    port = int(os.environ.get("SU_API_PORT", "8000"))
    host = os.environ.get("SU_API_HOST", "127.0.0.1")
    print(f"Iniciando Synthetic University API Gateway em http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
