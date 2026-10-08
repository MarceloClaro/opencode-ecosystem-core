"""R677: solicitação vazia não é confundida com índice pronto."""
from __future__ import annotations

import asyncio
import json

import pytest

from rag.book_library import LocalBookLibrary


@pytest.mark.parametrize("query", ["", " ", "\t\r\n", "\u00a0\u2003"])
def test_empty_query_abstains_before_any_index_or_source_access(tmp_path, monkeypatch, query):
    library = LocalBookLibrary(tmp_path / "missing-books", tmp_path / "missing.sqlite3")
    monkeypatch.setattr(library, "_snapshot", lambda: pytest.fail("Inventário/PDF acessado"))
    result = library.query(query)
    assert result["status"] == "invalid_request"
    assert result["reason_code"] == "empty_query"
    assert result["abstained"] is True
    assert result["evidence"] == [] and result["evidence_count"] == 0
    assert result["retrieval_executed"] is False
    assert result["model_inference_executed"] is False
    assert result["training_executed"] is False
    assert "index_status" not in result
    assert not library.index_path.exists() and not library.source_dir.exists()
    assert result["reason"]


def test_orchestrator_exposes_same_empty_request_gate_without_an_executor(tmp_path, monkeypatch):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    orch = MarceloClaroOrchestrator.__new__(MarceloClaroOrchestrator)
    orch._book_library = LocalBookLibrary(tmp_path / "books", tmp_path / "index.sqlite3")
    monkeypatch.setattr(orch._book_library, "_snapshot", lambda: pytest.fail("Recuperação acionada"))
    result = orch.library_query("")
    assert result["status"] == "invalid_request" and result["abstained"]
    assert not getattr(orch, "agents", None)


def test_term_limit_is_rejected_before_source_access(tmp_path, monkeypatch):
    library = LocalBookLibrary(tmp_path / "books", tmp_path / "index.sqlite3")
    monkeypatch.setattr(library, "_snapshot", lambda: pytest.fail("Fontes acessadas antes da validação"))
    with pytest.raises(ValueError, match="32"):
        library.query(" ".join(f"term{index}" for index in range(33)))


def test_valid_query_without_support_preserves_actual_index_state(tmp_path, monkeypatch):
    library = LocalBookLibrary(tmp_path / "books", tmp_path / "index.sqlite3")
    calls = []

    def snapshot():
        calls.append("read")
        return {"status": "ready", "books": 2}, set()

    monkeypatch.setattr(library, "_snapshot", snapshot)
    result = library.query("neutrinos inexistentes")
    assert calls == ["read"]
    assert result["status"] == "ready" and result["abstained"]
    assert result["index_status"]["books"] == 2
    assert result.get("reason_code") != "empty_query"
    assert result["evidence_count"] == 0 and result["evidence"] == []


@pytest.mark.parametrize("task,topic", [("", ""), (" ", "MCP"), ("Revisar", "\t")])
def test_current_mcp_prompt_rejects_empty_input_before_orchestrator_construction(monkeypatch, task, topic):
    from integrations import ecosystem_mcp as surface

    monkeypatch.setattr(surface, "get_library_orchestrator", lambda: pytest.fail("Orquestrador construído"))
    monkeypatch.setattr(surface, "get_coordinator", lambda: pytest.fail("Executor construído"))
    with pytest.raises(Exception, match="task|topic"):
        asyncio.run(surface.mcp.get_prompt("ecosystem_book_review", {"task": task, "topic": topic}))


@pytest.mark.parametrize("query", ["", " \t"])
def test_current_mcp_search_rejects_empty_query_before_construction(monkeypatch, query):
    from integrations import ecosystem_mcp as surface

    monkeypatch.setattr(surface, "get_library_orchestrator", lambda: pytest.fail("Orquestrador construído"))
    with pytest.raises(Exception, match="query"):
        asyncio.run(surface.mcp.call_tool("ecosystem_library_search", {"query": query}))


@pytest.mark.parametrize("query", ["", " \t"])
def test_cli_rejects_empty_query_without_constructing_orchestrator(monkeypatch, capsys, query):
    from marceloclaro import library_cli

    monkeypatch.setattr(library_cli, "_orchestrator", lambda _: pytest.fail("Orquestrador construído"))
    assert library_cli.run_library_cli(["buscar", query]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "error"
    assert "evidence" not in output and "Traceback" not in output["error"]
