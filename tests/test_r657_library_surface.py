"""Contratos do orquestrador e CLI para livros e gate de dados."""
import json
import sqlite3

from marceloclaro.orchestrator import MarceloClaroOrchestrator


class Library:
    def status(self):
        return {"status": "ready", "book_count": 2}

    def index(self):
        return {"status": "indexed", "book_count": 2}

    def query(self, query, top_k=5):
        return {"query": query, "top_k": top_k, "abstained": True, "evidence": []}

    def read_page(self, book_id, page):
        return {"book_id": book_id, "page": page}


def orchestrator():
    # O teste exercita os encaminhamentos sem inicializar agentes/executores.
    orch = MarceloClaroOrchestrator.__new__(MarceloClaroOrchestrator)
    orch._book_library = Library()
    return orch


def test_opencode_command_routes_library_via_primary_orchestrator():
    from integrations.opencode_cli import build_config

    command = build_config()["command"]["biblioteca"]
    assert command["agent"] == "marceloclaro"
    assert "ecosystem_library_search" in command["template"]
    assert "$ARGUMENTS" in command["template"]
    assert "página" in command["template"]


def test_orchestrator_centralizes_library_operations():
    orch = orchestrator()
    assert orch.library_status()["book_count"] == 2
    assert orch.library_index()["status"] == "indexed"
    assert orch.library_query("MCP", 2)["top_k"] == 2
    assert orch.library_page("a" * 64, 55)["page"] == 55


def test_library_cli_preserves_query_and_explicit_limit(capsys):
    from marceloclaro.library_cli import run_library_cli

    assert run_library_cli(["buscar", "split por grupo", "--top-k", "2"], orchestrator()) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["query"] == "split por grupo"
    assert result["top_k"] == 2


def test_library_cli_status_and_index(capsys):
    from marceloclaro.library_cli import run_library_cli

    assert run_library_cli(["status"], orchestrator()) == 0
    assert json.loads(capsys.readouterr().out)["book_count"] == 2
    assert run_library_cli(["indexar"], orchestrator()) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "indexed"


def test_cli_reports_invalid_input_without_traceback(capsys):
    from marceloclaro.library_cli import run_library_cli, run_finetuning_cli

    assert run_library_cli(["buscar", "MCP", "--top-k", "0"], orchestrator()) == 2
    assert "Traceback" not in capsys.readouterr().out
    assert run_finetuning_cli(["validar", "/missing/dataset.json"], orchestrator()) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_library_cli_database_failure_is_actionable(capsys):
    from marceloclaro.library_cli import run_library_cli

    class Broken:
        def library_index(self):
            raise sqlite3.OperationalError("database is locked; execute indexar novamente")

    assert run_library_cli(["indexar"], Broken()) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "error"
    assert "database is locked" in result["error"]


def test_finetuning_cli_never_prints_dataset_records(tmp_path, capsys):
    from marceloclaro.library_cli import run_finetuning_cli

    class Gate:
        def finetuning_prepare_data(self, records, seed=42):
            return {"status": "accepted", "manifest": {"seed": seed},
                    "splits": {"train": records}, "diagnostics": []}

    data = tmp_path / "records.json"
    data.write_text(json.dumps([{"input": "CONTEUDO PRIVADO", "output": "RESPOSTA PRIVADA"}]))
    assert run_finetuning_cli(["validar", str(data)], Gate()) == 0
    output = capsys.readouterr().out
    assert "PRIVAD" not in output
    assert "splits" not in json.loads(output)


def test_finetuning_cli_failed_gate_has_nonzero_exit(tmp_path, capsys):
    from marceloclaro.library_cli import run_finetuning_cli

    class Gate:
        def finetuning_evaluate(self, baseline, candidate, min_improvement=0.0):
            return {"status": "blocked", "passed": False, "reason": "hashes divergentes"}

    comparison = tmp_path / "comparison.json"
    comparison.write_text(json.dumps({"baseline": {}, "candidate": {}}))
    assert run_finetuning_cli(["avaliar", str(comparison)], Gate()) == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False
