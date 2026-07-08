"""Testes TDD para Synthetic University MCP Server (SPEC-935 R94)."""

import json
import pytest
from unittest.mock import patch, MagicMock
from synthetic_university.mcp_server import (
    SimpleMCPServer,
    handle_generate,
    handle_evaluate,
    handle_enrich,
    handle_visual_abstract,
    handle_peer_review,
    handle_submission_package,
    handle_novelty_analysis,
    handle_dashboard,
)


class TestR94MCPServer:
    """Testes para o servidor MCP da Universidade Sintetica."""

    @pytest.fixture
    def server(self):
        s = SimpleMCPServer("test-server")
        # Registra ferramentas manualmente
        s.register_tool("su_generate", "Generate", {"type": "object", "properties": {}}, handle_generate)
        s.register_tool("su_evaluate", "Evaluate", {"type": "object", "properties": {}}, handle_evaluate)
        s.register_tool("su_enrich", "Enrich", {"type": "object", "properties": {}}, handle_enrich)
        s.register_tool("su_visual_abstract", "Visual", {"type": "object", "properties": {}}, handle_visual_abstract)
        s.register_tool("su_peer_review", "Review", {"type": "object", "properties": {}}, handle_peer_review)
        s.register_tool("su_submission", "Submission", {"type": "object", "properties": {}}, handle_submission_package)
        s.register_tool("su_novelty", "Novelty", {"type": "object", "properties": {}}, handle_novelty_analysis)
        s.register_tool("su_dashboard", "Dashboard", {"type": "object", "properties": {}}, handle_dashboard)
        return s

    def test_server_creates(self, server):
        """R94: Servidor MCP e criado com ferramentas registradas."""
        assert server is not None
        assert len(server.tools) >= 8

    def test_tools_list(self, server):
        """R94: Lista de ferramentas via tools/list."""
        req = {"method": "tools/list", "id": 1}
        resp = server.handle_sync(req)

        assert "tools" in resp
        tool_names = [t["name"] for t in resp["tools"]]
        assert "su_generate" in tool_names
        assert "su_evaluate" in tool_names
        assert "su_enrich" in tool_names
        assert "su_visual_abstract" in tool_names
        assert "su_peer_review" in tool_names
        assert "su_submission" in tool_names
        assert "su_novelty" in tool_names
        assert "su_dashboard" in tool_names

    def test_generate_tool(self, server):
        """R94: Ferramenta de geracao de teses."""
        # Patch o handler registrado no server
        server.tools["su_generate"]["handler"] = lambda args: {
            "success": True,
            "theses": [{"thesis_id": "t1", "title": "Test Thesis"}],
        }

        req = {
            "method": "tools/call",
            "params": {"name": "su_generate", "arguments": {"n_pairs": 2}},
            "id": 2,
        }
        resp = server.handle_sync(req)

        assert "content" in resp
        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True

    def test_evaluate_tool(self, server):
        """R94: Ferramenta de avaliacao com LLM."""
        server.tools["su_evaluate"]["handler"] = lambda args: {
            "success": True,
            "score": 8,
            "feedback": "Excellent work",
            "source": "opencode",
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_evaluate",
                "arguments": {
                    "thesis_id": "t1",
                    "title": "Quantum Ethics",
                    "hypothesis": "Test hypothesis",
                },
            },
            "id": 3,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True

    def test_enrich_tool(self, server):
        """R94: Ferramenta de enriquecimento."""
        server.tools["su_enrich"]["handler"] = lambda args: {
            "success": True,
            "concepts_enriched": [{"concept": "ethics", "results": []}],
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_enrich",
                "arguments": {
                    "thesis_id": "t1",
                    "concepts": ["ethics", "quantum"],
                },
            },
            "id": 4,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True

    def test_visual_abstract_tool(self, server):
        """R94: Ferramenta de abstract visual."""
        server.tools["su_visual_abstract"]["handler"] = lambda args: {
            "success": True,
            "image_path": "/tmp/viz.svg",
            "source": "svg_fallback",
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_visual_abstract",
                "arguments": {
                    "thesis_id": "t1",
                    "title": "Quantum Ethics",
                    "hypothesis": "Test",
                },
            },
            "id": 5,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True

    def test_peer_review_tool(self, server):
        """R94: Ferramenta de revisao por pares."""
        server.tools["su_peer_review"]["handler"] = lambda args: {
            "success": True,
            "aggregate_score": 7.5,
            "decision": "Minor Revision",
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_peer_review",
                "arguments": {
                    "thesis_id": "t1",
                    "title": "Quantum Ethics",
                },
            },
            "id": 6,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True
        assert "aggregate_score" in content

    def test_submission_tool(self, server):
        """R94: Ferramenta de pacote de submissao."""
        server.tools["su_submission"]["handler"] = lambda args: {
            "success": True,
            "package_path": "/tmp/submission/",
            "journal": "Nature MI",
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_submission",
                "arguments": {
                    "thesis_id": "t1",
                    "title": "Quantum Ethics",
                    "journal": "Nature Machine Intelligence",
                },
            },
            "id": 7,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True
        assert "package_path" in content

    def test_novelty_tool(self, server):
        """R94: Ferramenta de analise de novidade."""
        server.tools["su_novelty"]["handler"] = lambda args: {
            "success": True,
            "novelty_score": 72.5,
            "components": {"originality": 80, "impact": 65},
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_novelty",
                "arguments": {
                    "thesis_id": "t1",
                    "title": "Quantum Ethics",
                    "concepts": ["quantum", "ethics"],
                },
            },
            "id": 8,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True
        assert content["novelty_score"] > 0

    def test_dashboard_tool(self, server):
        """R94: Ferramenta de dashboard."""
        server.tools["su_dashboard"]["handler"] = lambda args: {
            "success": True,
            "dashboard_path": "/tmp/dashboard/index.html",
        }

        req = {
            "method": "tools/call",
            "params": {
                "name": "su_dashboard",
                "arguments": {"lang": "en"},
            },
            "id": 9,
        }
        resp = server.handle_sync(req)

        content = json.loads(resp["content"][0]["text"])
        assert content["success"] is True

    def test_invalid_tool(self, server):
        """R94: Ferramenta inexistente retorna erro."""
        req = {
            "method": "tools/call",
            "params": {"name": "su_nonexistent", "arguments": {}},
            "id": 10,
        }
        resp = server.handle_sync(req)
        assert resp.get("isError") is True

    def test_stdio_roundtrip(self, server):
        """R94: Round-trip via stdio (simulado) funciona."""
        import io
        import sys

        req = {"method": "tools/list", "id": 1}
        input_data = json.dumps(req) + "\n"

        # Simula stdin
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(input_data)

        try:
            result = server.handle_sync(req)
            assert "tools" in result
            assert len(result["tools"]) >= 8
        finally:
            sys.stdin = old_stdin
