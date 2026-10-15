"""R891: aceite científico ligado ao primário, CLI, MCP e memória reais."""
import asyncio
import importlib
import json

import pytest


@pytest.fixture
def primary(tmp_path, monkeypatch):
    memory_module = importlib.import_module("mci.metabus")
    monkeypatch.setattr(memory_module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(memory_module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    memory = memory_module.MetacognitiveMemory()
    memory.confidence_ledger["marceloclaro"] = 0.37
    monkeypatch.setattr(memory_module.metabus, "memory", memory)
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    return MarceloClaroOrchestrator(auto_load_agents=False), memory


def accepted():
    return {"status": "locally_verified", "success": True,
            "local_computational_acceptance": True, "human_submission_acceptance": False,
            "external_validation": False, "confidence_promoted": False,
            "package_manifest_sha256": "a" * 64, "report_sha256": "b" * 64,
            "verified_artifacts": [], "replay": {"matched": True, "process_executed": True}}


def test_primary_records_verification_without_changing_confidence(primary, monkeypatch):
    core, memory = primary
    assert hasattr(core, "scientific_verify_package"), "Falta operação científica canônica"
    release = importlib.import_module("research.scientific_release")
    calls = []
    def verify(**config):
        calls.append(config)
        return accepted()
    monkeypatch.setattr(release, "verify_scientific_package", verify)
    before = dict(memory.confidence_ledger)
    result = core.scientific_verify_package(package_dir="package", timeout_seconds=30)
    assert calls == [{"package_dir": "package", "timeout_seconds": 30}]
    assert result["local_computational_acceptance"] is True
    assert result["human_submission_acceptance"] is False
    assert result["metacognition"]["persisted"] is True
    assert memory.confidence_ledger == before
    observation = memory.episodic[-1]["observation"]
    assert observation["report_sha256"] == "b" * 64
    assert observation["externally_validated"] is False


def test_verification_does_not_claim_success_after_memory_failure(primary, monkeypatch):
    core, memory = primary
    assert hasattr(core, "scientific_verify_package")
    release = importlib.import_module("research.scientific_release")
    monkeypatch.setattr(release, "verify_scientific_package", lambda **_: accepted())
    def failed_record(*args, **kwargs):
        raise RuntimeError("fixture persistence failure")
    monkeypatch.setattr(core, "_record_knowledge_outcome", failed_record)
    result = core.scientific_verify_package(package_dir="package")
    assert result["status"] == "blocked"
    assert result["success"] is False
    assert result["local_computational_acceptance"] is False
    assert result["metacognition"]["persisted"] is False
    assert memory.confidence_ledger["marceloclaro"] == 0.37


def test_new_scientific_run_requires_the_same_package_check(primary, monkeypatch, tmp_path):
    core, _ = primary
    assert hasattr(core, "scientific_verify_package")
    from research.provenance_pipeline import ScientificProvenancePipeline
    monkeypatch.setattr(ScientificProvenancePipeline, "run", lambda *a, **kw: {
        "status": "completed", "experiment_executed": True, "artifacts": {}})
    # O estágio que só declara completed não possui pacote verificável.
    result = core.scientific_reproducible_run(question="Fixture de contrato", dataset_csv="x.csv",
        dataset_provenance={}, method="descriptive", variables={"value": "x"},
        output_dir=str(tmp_path / "missing"))
    assert result["status"] == "blocked"
    assert result["release_check"]["local_computational_acceptance"] is False


class PrimarySpy:
    def __init__(self, report):
        self.report, self.calls = report, []

    def scientific_verify_package(self, **config):
        self.calls.append(config)
        return self.report


def test_cli_and_mcp_use_the_same_primary_operation(tmp_path, monkeypatch, capsys):
    from marceloclaro.science_cli import run_science_cli
    from integrations import ecosystem_mcp
    config = {"package_dir": str(tmp_path), "timeout_seconds": 30}
    path = tmp_path / "check.json"
    path.write_text(json.dumps(config))
    spy = PrimarySpy(accepted())
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: spy)
    assert run_science_cli(["verificar", "--config", str(path)], orchestrator=spy) == 0
    assert json.loads(capsys.readouterr().out)["local_computational_acceptance"] is True
    assert hasattr(ecosystem_mcp, "ecosystem_scientific_verify")
    result = asyncio.run(ecosystem_mcp.ecosystem_scientific_verify(config))
    assert result["human_submission_acceptance"] is False
    assert spy.calls == [config, config]


@pytest.mark.parametrize("report", [
    {"status": "blocked", "success": False, "local_computational_acceptance": False},
    {"status": "locally_verified", "success": True, "local_computational_acceptance": False},
    {"status": "locally_verified", "success": "true", "local_computational_acceptance": True},
    {"status": "completed", "success": True, "local_computational_acceptance": True},
    {},
])
def test_cli_rejects_incomplete_or_truthy_verification_receipt(tmp_path, capsys, report):
    from marceloclaro.science_cli import run_science_cli
    path = tmp_path / "check.json"
    path.write_text(json.dumps({"package_dir": str(tmp_path)}))
    assert run_science_cli(["verificar", "--config", str(path)], orchestrator=PrimarySpy(report)) == 1
    capsys.readouterr()


@pytest.mark.parametrize("config", [{}, {"package_dir": "x", "execute": True},
                                     {"package_dir": "x", "timeout_seconds": True}])
def test_mcp_validates_before_primary_construction(monkeypatch, config):
    from integrations import ecosystem_mcp
    assert hasattr(ecosystem_mcp, "ecosystem_scientific_verify")
    monkeypatch.setattr(ecosystem_mcp, "get_library_orchestrator", lambda: pytest.fail("Validação tardia"))
    with pytest.raises(ValueError):
        asyncio.run(ecosystem_mcp.ecosystem_scientific_verify(config))
