# -*- coding: utf-8 -*-
"""
Testes TDD para R96 — Academic API Gateway (SPEC-935-R96).

Ciclo: RED → GREEN → REFACTOR.
Usa TestClient do Starlette diretamente (sem runtime FastAPI completo).
"""

import json
from unittest.mock import patch, MagicMock

import pytest

try:
    from starlette.testclient import TestClient
    HAS_STARLETTE = True
except ImportError:
    HAS_STARLETTE = False


# ============================================================
# Mock handlers (evitam chamadas reais a LLM / rede)
# ============================================================

def _mock_handler_factory(return_value: dict):
    """Factory que retorna um handler mockado."""
    def handler(args):
        return return_value
    return handler


MOCK_HANDLERS = {
    "generate": _mock_handler_factory({
        "success": True, "theses": [{"thesis_id": "t1", "title": "Mock"}], "count": 1
    }),
    "evaluate": _mock_handler_factory({
        "success": True, "feedback": "Mock feedback", "source": "mock", "elapsed_seconds": 0.1
    }),
    "enrich": _mock_handler_factory({
        "success": True, "concepts_enriched": [{"concept": "mock", "results": []}]
    }),
    "visual-abstract": _mock_handler_factory({
        "success": True, "image_path": "/tmp/mock.svg", "source": "mock"
    }),
    "peer-review": _mock_handler_factory({
        "success": True, "aggregate_score": 7.0, "decision": "Minor Revision"
    }),
    "submission": _mock_handler_factory({
        "success": True, "package_path": "/tmp/mock/", "journal": "Mock"
    }),
    "novelty": _mock_handler_factory({
        "success": True, "novelty_score": 72.5, "components": {}
    }),
    "dashboard": _mock_handler_factory({
        "success": True, "dashboard_path": "/tmp/mock", "files": ["index.html"]
    }),
}


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def client():
    """TestClient para a aplicação FastAPI com handlers mockados."""
    import synthetic_university.api_gateway as gateway
    # Aplicar patch global nos handlers para evitar chamadas reais
    patcher = patch.object(gateway, "_import_handlers", return_value=MOCK_HANDLERS)
    patcher.start()
    app = gateway.app
    yield TestClient(app)
    patcher.stop()


# ============================================================
# Testes
# ============================================================

@pytest.mark.skipif(not HAS_STARLETTE, reason="Starlette/TestClient não instalado")
class TestR96ApiGateway:
    """Suíte TDD para Academic API Gateway."""

    # --- CA1: Estrutura ---

    def test_ca1_module_loads(self):
        """CA1: Módulo deve carregar sem erro (import condicional)."""
        from synthetic_university import api_gateway
        assert hasattr(api_gateway, "app")

    # --- CA2: Endpoints básicos ---

    def test_ca2_health(self, client):
        """CA2: GET /health deve retornar status ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_ca2_tools(self, client):
        """CA2: GET /tools deve listar ferramentas."""
        resp = client.get("/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert "tools" in data
        assert len(data["tools"]) >= 8
        names = [t["name"] for t in data["tools"]]
        assert "generate" in names

    # --- CA3: Endpoints de ferramentas ---

    def test_ca3_generate(self, client):
        """CA3: POST /tools/generate deve gerar teses."""
        resp = client.post("/tools/generate", json={"n_pairs": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "theses" in data

    def test_ca3_evaluate(self, client):
        """CA3: POST /tools/evaluate deve avaliar tese."""
        resp = client.post("/tools/evaluate", json={
            "thesis_id": "t1", "title": "Quantum Ethics",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert "feedback" in data

    def test_ca3_enrich(self, client):
        """CA3: POST /tools/enrich deve enriquecer tese."""
        resp = client.post("/tools/enrich", json={
            "thesis_id": "t1", "title": "Quantum Ethics", "concepts": ["ethics"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True

    def test_ca3_peer_review(self, client):
        """CA3: POST /tools/peer-review deve iniciar revisão."""
        resp = client.post("/tools/peer-review", json={
            "thesis_id": "t1", "title": "Quantum Ethics",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True

    def test_ca3_submission(self, client):
        """CA3: POST /tools/submission deve gerar pacote."""
        resp = client.post("/tools/submission", json={
            "thesis_id": "t1", "title": "Quantum Ethics",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True

    def test_ca3_novelty(self, client):
        """CA3: POST /tools/novelty deve analisar novidade."""
        resp = client.post("/tools/novelty", json={
            "thesis_id": "t1", "title": "Quantum Ethics", "concepts": ["quantum"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True

    def test_ca3_dashboard(self, client):
        """CA3: POST /tools/dashboard deve gerar dashboard."""
        resp = client.post("/tools/dashboard", json={"lang": "en"})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True

    # --- CA5: Tratamento de erros ---

    def test_ca5_404(self, client):
        """CA5: Endpoint inexistente retorna 404."""
        resp = client.get("/nonexistent")
        assert resp.status_code == 404

    def test_ca5_invalid_json(self, client):
        """CA5: JSON inválido retorna 422."""
        resp = client.post(
            "/tools/generate",
            data="not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422
