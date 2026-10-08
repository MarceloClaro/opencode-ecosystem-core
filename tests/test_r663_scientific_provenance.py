"""R663: fixtures artificiais verificam contratos, sem alegar coleta externa."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from research.provenance_pipeline import ScientificProvenancePipeline
from research.statistical_methods import execute_analysis
from skills.tooling.data_knowledge_hub.datasets import DatasetDataSource


@pytest.fixture
def inputs(tmp_path):
    dataset = tmp_path / "observations.csv"
    dataset.write_text("x,y,group\n1,2,a\n2,5,a\n3,4,a\n4,8,b\n5,7,b\n6,12,b\n", encoding="utf-8")
    refs = tmp_path / "references.json"
    refs.write_text(json.dumps({
        "status": "online", "evidence_kind": "retrieved_http_metadata",
        "records": [{"title": "Fixture bibliografica para contrato",
                     "url": "https://example.org/paper", "abstract": "Numeric association x y",
                     "source": "fixture", "year": 2024}],
    }), encoding="utf-8")
    return {
        "question": "Qual é a associação entre x e y?",
        "dataset_csv": str(dataset),
        "dataset_provenance": {"source_url": "https://example.org/dataset",
                               "title": "Fixture CSV", "evidence_kind": "real_observations"},
        "method": "pearson", "variables": {"x": "x", "y": "y"},
        "reference_sources": [{"path": str(refs), "source_url": "https://example.org/metadata"}],
        "output_dir": str(tmp_path / "run"),
    }


def test_pipeline_executes_and_reproduces_in_another_process(inputs):
    report = ScientificProvenancePipeline().run(**inputs)
    assert report["status"] == "completed"
    assert report["analysis"]["n"] == 6
    assert report["reproduction"]["process_executed"] is True
    assert report["reproduction"]["matched"] is True
    assert report["computational_review"]["human_peer_review"] is False
    assert report["external_validation"] is False
    assert report["provenance"]["dataset"]["source_authenticity"] == "user_declared"
    assert report["provenance"]["references"][0]["source_mode"] == "provided_snapshot"
    assert report["rag"]["retrieval_executed"] is True
    assert report["rag"]["scientific_claim_support"] is False
    for artifact in report["artifacts"].values():
        assert Path(artifact["path"]).is_file()
        assert hashlib.sha256(Path(artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
    manuscript = Path(report["artifacts"]["article"]["path"]).read_text()
    assert "revisão computacional" in manuscript.lower()
    assert "não estabelece causalidade" in manuscript.lower()
    assert "Fixture bibliografica" in manuscript


def test_analysis_agrees_with_independent_scipy_reference(inputs):
    from scipy.stats import pearsonr
    result = execute_analysis(inputs["dataset_csv"], "pearson", {"x": "x", "y": "y"})
    expected = pearsonr([1, 2, 3, 4, 5, 6], [2, 5, 4, 8, 7, 12])
    assert result["estimate"] == pytest.approx(expected.statistic)
    assert result["p_value"] == pytest.approx(expected.pvalue)
    assert result["permutation"]["replicates"] == 999


def test_descriptive_analysis_does_not_invent_pvalue(inputs):
    result = execute_analysis(inputs["dataset_csv"], "descriptive", {"value": "y"})
    assert result["p_value"] is None
    assert result["null_hypothesis"] is None
    assert result["descriptive"]["y"]["mean"] == pytest.approx(38 / 6)


def test_existing_output_is_preserved(inputs):
    output = Path(inputs["output_dir"])
    output.mkdir()
    sentinel = output / "original.txt"
    sentinel.write_text("preserve")
    report = ScientificProvenancePipeline().run(**inputs)
    assert report["status"] == "blocked"
    assert sentinel.read_text() == "preserve"
    assert list(output.iterdir()) == [sentinel]


def test_reference_hash_is_checked(inputs):
    inputs["reference_sources"][0]["sha256"] = "0" * 64
    report = ScientificProvenancePipeline().run(**inputs)
    assert report["status"] == "blocked"
    assert report["reason"] == "snapshot_hash_mismatch"


def test_dataset_source_transformation_and_limitations_are_preserved(inputs):
    metadata = {"license": "CC BY fixture", "archive_sha256": "a" * 64,
                "member_sha256": "b" * 64, "dataset_doi": "10.example/dataset",
                "transformation": "CSV labels retained; no synthetic rows introduced.",
                "limitations": ["Fixture groups cannot establish causality."]}
    inputs["dataset_provenance"].update(metadata)
    report = ScientificProvenancePipeline().run(**inputs)
    assert report["status"] == "completed"
    for key, value in metadata.items():
        assert report["provenance"]["dataset"][key] == value
    text = Path(report["artifacts"]["article"]["path"]).read_text()
    assert metadata["transformation"] in text
    assert metadata["limitations"][0] in text


@pytest.mark.parametrize("value", [float("nan"), {"nested": [[[[[[[[["too deep"]]]]]]]]]}, "x" * 8193])
def test_invalid_provenance_metadata_is_blocked(inputs, value):
    inputs["dataset_provenance"]["extra"] = value
    report = ScientificProvenancePipeline().run(**inputs)
    assert report["status"] == "blocked"
    assert not Path(inputs["output_dir"]).exists()


def test_reproducer_detects_changed_method_code(inputs):
    report = ScientificProvenancePipeline().run(**inputs)
    methods = Path(report["artifacts"]["methods_code"]["path"])
    sentinel = methods.parent / "must-not-run.txt"
    methods.write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n" + methods.read_text())
    process = subprocess.run([sys.executable, report["artifacts"]["reproduce_code"]["path"]], capture_output=True, text=True, timeout=30)
    assert process.returncode != 0
    assert "methods_hash_mismatch" in process.stdout
    assert not sentinel.exists()


def test_welch_compares_predefined_groups(inputs):
    from scipy.stats import ttest_ind
    result = execute_analysis(inputs["dataset_csv"], "welch_t",
                              {"value": "y", "group": "group", "groups": ["a", "b"]})
    expected = ttest_ind([2, 5, 4], [8, 7, 12], equal_var=False)
    assert result["statistic"] == pytest.approx(expected.statistic)
    assert result["p_value"] == pytest.approx(expected.pvalue)
    assert result["group_sizes"] == {"a": 3, "b": 3}


@pytest.mark.parametrize("change", ["missing_reference", "synthetic_reference", "synthetic_dataset", "hash_changed", "unknown_method", "nonfinite"])
def test_bad_evidence_blocks_before_output(inputs, change):
    if change == "missing_reference":
        inputs["reference_sources"][0]["path"] += ".absent"
    elif change == "synthetic_reference":
        Path(inputs["reference_sources"][0]["path"]).write_text(json.dumps({"status": "offline", "synthetic": True, "records": [{"title": "fake"}]}))
    elif change == "synthetic_dataset":
        inputs["dataset_provenance"]["evidence_kind"] = "synthetic"
    elif change == "hash_changed":
        inputs["dataset_provenance"]["sha256"] = "0" * 64
    elif change == "unknown_method":
        inputs["method"] = "exec arbitrary code"
    elif change == "nonfinite":
        Path(inputs["dataset_csv"]).write_text("x,y\n1,nan\n2,2\n3,3\n4,4\n5,5\n")
    report = ScientificProvenancePipeline().run(**inputs)
    assert report["status"] == "blocked"
    assert report["experiment_executed"] is False
    assert not Path(inputs["output_dir"]).exists()


def test_reproducer_detects_modified_dataset(inputs):
    report = ScientificProvenancePipeline().run(**inputs)
    snapshot = Path(report["artifacts"]["dataset"]["path"])
    snapshot.write_text(snapshot.read_text().replace("1,2,a", "1,9,a"))
    process = subprocess.run([sys.executable, report["artifacts"]["reproduce_code"]["path"]], capture_output=True, text=True, timeout=30)
    assert process.returncode != 0
    assert "dataset_hash_mismatch" in process.stdout


@pytest.mark.parametrize("source", ["zenodo", "datacite", "uci", "figshare"])
def test_dataset_network_failure_does_not_invent_references(monkeypatch, source):
    def offline(*_args, **_kwargs):
        raise OSError("offline fixture")
    monkeypatch.setattr("urllib.request.urlopen", offline)
    result = DatasetDataSource().search("anything", source=source)
    assert result["results"] == []
    assert result["evidence_eligible"] is False
    assert result["status"] == "unavailable"
    assert result["provenance"]["acquisition"] == "failed_http_request"


def test_dataset_examples_require_explicit_demonstration(monkeypatch):
    def offline(*_args, **_kwargs):
        raise OSError("offline fixture")
    monkeypatch.setattr("urllib.request.urlopen", offline)
    result = DatasetDataSource(allow_demo_fallback=True).search("anything", source="zenodo")
    assert result["results"]
    assert result["synthetic"] is True
    assert result["evidence_kind"] == "demonstration"
    assert result["evidence_eligible"] is False


def test_research_hub_preserves_ineligible_provenance(tmp_path, monkeypatch):
    from research.hub import ResearchHub
    class OfflineHub:
        def search(self, _topic):
            return {"status": "offline", "source": "zenodo", "domain": "dataset",
                    "evidence_kind": "demonstration", "synthetic": True,
                    "evidence_eligible": False, "results": [{"doi": "made-up"}],
                    "count": 1, "provenance": {"acquisition": "demonstration_fallback"}}
    hub = ResearchHub("fixture", output_root=str(tmp_path), data_hub=OfflineHub())
    monkeypatch.setattr(hub.searcher, "search", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(hub.osint, "analyze_references", lambda *_args: {})
    report = hub.run(download=False, use_data_hub=True)
    knowledge = report["data_knowledge"]
    assert knowledge["status"] == "offline"
    assert knowledge["evidence_kind"] == "demonstration"
    assert knowledge["synthetic"] is True
    assert knowledge["results"] == []
    assert knowledge["diagnostic_results"] == [{"doi": "made-up"}]
    assert knowledge["provenance"]["acquisition"] == "demonstration_fallback"


def test_legacy_deep_research_simulation_cannot_claim_execution():
    from agentic_science_v2.deep_research import ExecutionSandbox, KnowledgeBaseRegistry, run_deep_research
    execution = ExecutionSandbox().execute("print(42)")
    assert execution["success"] is False
    assert execution["executed"] is False
    assert execution["evidence_kind"] == "simulation"
    query = ExecutionSandbox().query_api("pubmed", {"q": "fixture"})
    assert query["status"] == "simulation"
    assert query["evidence_eligible"] is False
    validation = ExecutionSandbox().cross_validate([{"text": "fixture", "sources": ["demo"]}])
    assert validation[0]["verified"] is False
    assert all(item["synthetic"] for item in KnowledgeBaseRegistry().query("pubmed", "diabetes"))
    report = run_deep_research("fixture", max_rounds=1)
    assert report["status"] == "simulation"
    assert report["evidence_eligible"] is False


def test_governance_without_executor_blocks_before_scientific_claim(monkeypatch):
    import mci.pipeline.scientific_governance_pipeline as governance
    def forbidden(*_args, **_kwargs):
        raise AssertionError("must not generate/register evidence without executor")
    monkeypatch.setattr(governance, "run_scientific_cycle", forbidden)
    report = governance.run_scientific_governance_pipeline("fixture", executor_fn=None)
    assert report["status"] == "blocked"
    assert report["pipeline_success"] is False
    assert report["experiment_executed"] is False
    assert report["reason"] == "executor_missing"
