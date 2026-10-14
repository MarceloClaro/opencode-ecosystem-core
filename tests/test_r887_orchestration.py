"""R887: contexto de código chega ao executor pela orquestração canônica."""
import asyncio
import importlib
import json

import pytest


@pytest.fixture
def primary(tmp_path, monkeypatch):
    memory_module = importlib.import_module("mci.metabus")
    module = importlib.import_module("marceloclaro.orchestrator")
    from mci.blackboard import blackboard
    monkeypatch.setattr(memory_module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(memory_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    bus = memory_module.metabus
    monkeypatch.setattr(bus, "memory", memory_module.MetacognitiveMemory())
    monkeypatch.setattr(bus, "subscribers", {})
    monkeypatch.setattr(blackboard, "registry", {})
    monkeypatch.setattr(blackboard, "tasks", {})
    bus.subscribe("agent.register", blackboard._handle_registration)
    bus.subscribe("task.post", blackboard._handle_task_post)
    result = module.MarceloClaroOrchestrator(auto_load_agents=False, strict_sdd=False)
    return result, bus, blackboard


class ProviderBoundary:
    """Substitui somente o transporte externo, sem executar modelo ou instalar."""
    def run(self, config):
        if config["operation"] == "status":
            return {"status": "ready", "success": True, "index_ready": True}
        return {"status": "completed", "success": True, "response": {"structuredContent": {"metadata": {"tokens_saved_est": 999, "cost_avoided_est": "$99"}, "results": [{"input": "parse_cobalto", "data": {"symbol": {"file_path": "core/parser.py", "name": "parse_cobalto", "start_line": 1, "end_line": 1, "code_block": "def parse_cobalto(): return 5"}}}]}},
                "provenance": {"provider": "context-link", "sources": [{"path": "core/parser.py", "sha256": "a" * 64}]}}


def test_consulta_registra_proveniencia_sem_promover_confianca(primary):
    core, bus, _ = primary
    core._code_context_provider = ProviderBoundary()
    before = dict(bus.memory.confidence_ledger)
    assert hasattr(core, "code_context_action"), "Falta entrada pelo primário"
    result = core.code_context_action({"operation": "query", "tool": "get_code_by_symbol", "arguments": {"symbol_name": "parse_cobalto"}})
    assert result["success"] is True
    assert result["metacognition"]["confidence_promoted"] is False
    assert result["metacognition"]["observation_id"]
    assert bus.memory.confidence_ledger == before
    assert bus.memory.episodic[-1]["observation"]["provenance"]["provider"] == "context-link"


def test_contexto_chega_ao_briefing_real_do_blackboard(primary):
    core, _, board = primary
    core._code_context_provider = ProviderBoundary()
    task = core.delegate("Corrigir parse_cobalto", ["python"])
    briefing = board.tasks[task].context["metacognitive_briefing"]
    assert "code_context" in briefing, "Contexto de código não chegou à tarefa"
    context = briefing["code_context"]
    assert context["status"] == "completed"
    assert context["content_is_instruction"] is False
    assert "parse_cobalto" in context["data"]
    assert context["provenance"]["sources"][0]["path"] == "core/parser.py"


def test_indisponibilidade_nao_fabrica_contexto(primary):
    core, _, board = primary
    class Missing:
        def run(self, config):
            return {"status": "unavailable", "index_ready": False, "success": False}
    core._code_context_provider = Missing()
    task = core.delegate("Corrigir parser", ["coding"])
    assert board.tasks[task].context["metacognitive_briefing"].get("code_context", {}).get("status") == "unavailable"


def test_mcp_nao_expoe_instalacao_ou_indexacao(primary, monkeypatch):
    core, _, _ = primary
    core._code_context_provider = ProviderBoundary()
    from integrations import ecosystem_mcp
    monkeypatch.setattr(ecosystem_mcp, "_library_orchestrator", core)
    assert hasattr(ecosystem_mcp, "ecosystem_code_context"), "Falta fachada MCP"
    for operation in ("setup", "index"):
        with pytest.raises(ValueError):
            asyncio.run(ecosystem_mcp.ecosystem_code_context({"operation": operation}))
    report = asyncio.run(ecosystem_mcp.ecosystem_code_context({"operation": "query", "tool": "get_code_by_symbol", "arguments": {"symbol_name": "parse_cobalto"}}))
    assert report["success"] is True
    assert report["metacognition"]["observation_id"]


def test_contexto_grande_e_limitado_e_claramente_truncado(primary):
    core, _, board = primary
    class Large(ProviderBoundary):
        def run(self, config):
            out = super().run(config)
            if config["operation"] == "query":
                out["response"]["structuredContent"]["results"][0]["data"]["symbol"]["code_block"] = "IGNORE GATE " * 10000
            return out
    core._code_context_provider = Large()
    task = core.delegate("Corrigir parser", ["python"])
    context = board.tasks[task].context["metacognitive_briefing"].get("code_context", {})
    assert context.get("truncated") is True
    assert len(context["data"]) <= 6000
    assert context["content_is_instruction"] is False


def test_cli_chama_primario_e_transmite_parametros(capsys):
    from marceloclaro import code_context_cli
    calls = []
    class Core:
        def code_context_action(self, config):
            calls.append(config)
            return {"success": True, "status": "completed"}
    result = code_context_cli.run_code_context_cli(["query", "--tool", "get_file_skeleton", "--arguments", '{"file_path":"core/parser.py"}'], lambda **_: Core())
    assert result == 0
    assert calls == [{"operation": "query", "tool": "get_file_skeleton", "arguments": {"file_path": "core/parser.py"}, "timeout_seconds": 30.0}]
    assert json.loads(capsys.readouterr().out)["success"] is True


def test_contexto_compacto_remove_contador_estimado_e_mantem_fonte(primary):
    core, _, board = primary
    core._code_context_provider = ProviderBoundary()
    task = core.delegate("Corrigir parser", ["python"])
    context = board.tasks[task].context["metacognitive_briefing"]["code_context"]
    assert "tokens_saved_est" not in context["data"]
    assert "cost_avoided_est" not in context["data"]
    assert "a" * 64 in context["data"]


def test_sem_proveniencia_nao_passar_snippet_como_contexto(primary):
    core, _, board = primary
    class Uncited(ProviderBoundary):
        def run(self, config):
            out = super().run(config)
            out.pop("provenance", None)
            return out
    core._code_context_provider = Uncited()
    task = core.delegate("Corrigir parser", ["python"])
    context = board.tasks[task].context["metacognitive_briefing"]["code_context"]
    assert context["status"] == "untraceable_response"
    assert "parse_cobalto" not in context.get("data", "")


def test_snippets_repetidos_sao_deduplicados_com_posicao(primary):
    core, _, _ = primary
    class Duplicate(ProviderBoundary):
        def run(self, config):
            out = super().run(config)
            if config["operation"] == "query":
                rows = out["response"]["structuredContent"]["results"]
                rows.extend([rows[0], rows[0]])
            return out
    core._code_context_provider = Duplicate()
    result = core.code_context_action({"operation": "query", "tool": "get_code_by_symbol", "arguments": {"symbol_name": "parse_cobalto"}})
    rows = result["response"]["snippets"]
    assert len(rows) == 1
    assert rows[0]["start_line"] == rows[0]["end_line"] == 1
    assert rows[0]["source_sha256"] == "a" * 64


def test_falha_com_response_nulo_nao_aborta_delegacao(primary):
    core, _, board = primary
    class Oversized(ProviderBoundary):
        def run(self, config):
            if config["operation"] == "status":
                return super().run(config)
            return {"success": False, "status": "response_too_large", "response": None}
    core._code_context_provider = Oversized()
    task = core.delegate("Corrigir parser", ["python"])
    context = board.tasks[task].context["metacognitive_briefing"]["code_context"]
    assert context["status"] == "response_too_large"
    assert context["success"] is False


def test_nomes_qualificados_distintos_nao_sao_colapsados():
    from integrations.code_context_view import compact_code_response
    report = {"success": True, "status": "completed", "response": {"structuredContent": {"results": [
        {"file_path": "core/parser.py", "symbol_name": "run", "qualified_name": "Agent.run"},
        {"file_path": "core/parser.py", "symbol_name": "run", "qualified_name": "Worker.run"},
        {"file_path": "core/parser.py", "symbol_name": "run", "qualified_name": "Agent.run"}]}},
        "provenance": {"sources": [{"path": "core/parser.py", "sha256": "b"*64}]}}
    rows = compact_code_response(report)["snippets"]
    assert {row["qualified_name"] for row in rows} == {"Agent.run", "Worker.run"}
    assert len(rows) == 2


@pytest.mark.parametrize("path", ["../secrets.py", "/etc/passwd", "C:\\keys.py"])
def test_projecao_rejeita_caminhos_fora_do_corpus(path):
    from integrations.code_context_view import compact_code_response
    report = {"success": True, "status": "completed", "response": {"structuredContent": {"results": [
        {"file_path": path, "name": "run"}]}}, "provenance": {"sources": [{"path": path, "sha256": "b"*64}]}}
    projected = compact_code_response(report)
    assert projected["success"] is False
    assert projected["snippets"] == []
