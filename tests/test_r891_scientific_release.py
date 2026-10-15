"""R891: fixtures de contrato não são aquisição científica externa."""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

from research.provenance_pipeline import ScientificProvenancePipeline


def api():
    try:
        return importlib.import_module("research.scientific_release")
    except ModuleNotFoundError:
        pytest.fail("R891 ainda não oferece verificação científica local")


@pytest.fixture(scope="module")
def packages(tmp_path_factory):
    root = tmp_path_factory.mktemp("scientific-contract")
    dataset = root / "input.csv"
    dataset.write_text("x,y,group\n1,2,a\n2,5,a\n3,4,a\n4,8,b\n5,7,b\n6,12,b\n")
    refs = root / "refs.json"
    refs.write_text(
        json.dumps(
            {
                "status": "online",
                "evidence_kind": "retrieved_http_metadata",
                "records": [
                    {
                        "title": "Fixture bibliográfica de contrato",
                        "url": "https://example.org/fixture",
                        "abstract": "Association x y",
                        "source": "fixture",
                    }
                ],
            }
        )
    )
    results = {}
    for method, variables in [
        ("descriptive", {"value": "y"}),
        ("pearson", {"x": "x", "y": "y"}),
        ("welch_t", {"value": "y", "group": "group", "groups": ["a", "b"]}),
    ]:
        target = root / method
        result = ScientificProvenancePipeline().run(
            question="Associação entre x e y?",
            dataset_csv=str(dataset),
            dataset_provenance={
                "title": "Fixture CSV de contrato",
                "source_url": "https://example.org/fixture.csv",
                "evidence_kind": "real_observations",
            },
            method=method,
            variables=variables,
            output_dir=str(target),
            reference_sources=[
                {"path": str(refs), "source_url": "https://example.org/metadata"}
            ],
        )
        assert result["status"] == "completed"
        results[method] = target
    return results


@pytest.fixture
def package(packages, tmp_path):
    target = tmp_path / "relocated-study"
    shutil.copytree(packages["descriptive"], target)
    return target


def mutate(package, role, transform):
    manifest_path = package / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entry = manifest["artifacts"][role]
    artifact = package / Path(entry["path"]).name
    value = (
        json.loads(artifact.read_text())
        if artifact.suffix == ".json"
        else artifact.read_text()
    )
    changed = transform(value)
    raw = (
        json.dumps(
            changed, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        )
        if artifact.suffix == ".json"
        else changed
    ).encode()
    artifact.write_bytes(raw)
    entry.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    manifest_path.write_text(json.dumps(manifest))
    return manifest


@pytest.mark.parametrize("method", ["descriptive", "pearson", "welch_t"])
def test_three_actual_methods_replay_with_trusted_core(packages, method):
    report = api().verify_scientific_package(package_dir=str(packages[method]))
    assert report["status"] == "locally_verified", report
    assert report["success"] is True
    assert report["local_computational_acceptance"] is True
    assert report["human_submission_acceptance"] is False
    assert report["external_validation"] is False
    assert report["confidence_promoted"] is False
    assert report["replay"]["process_executed"] is True
    assert report["replay"]["matched"] is True
    assert report["replay"]["method"] == method
    assert report["verified_artifacts"]["dataset"]["sha256"]
    assert len(report["report_sha256"]) == 64


def test_relocated_absolute_paths_use_only_internal_bytes(package):
    manifest_path = package / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["artifacts"].values():
        entry["path"] = "/absent-original-study/" + Path(entry["path"]).name
    manifest_path.write_text(json.dumps(manifest))
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "locally_verified", report


@pytest.mark.parametrize(
    "config",
    [
        {},
        {"package_dir": True},
        {"package_dir": "x", "timeout_seconds": True},
        {"package_dir": "x", "timeout_seconds": 0},
        {"package_dir": "x", "timeout_seconds": 61},
        {"package_dir": "x", "timeout_seconds": float("nan")},
        {"package_dir": "x", "command": "echo"},
    ],
)
def test_config_rejects_wrong_types_unknown_fields_and_bad_limits(config):
    with pytest.raises(ValueError):
        api().validate_verify_config(config)


def test_config_default_is_bounded(package):
    assert api().validate_verify_config({"package_dir": str(package)}) == {
        "package_dir": str(package),
        "timeout_seconds": 45,
    }


@pytest.mark.parametrize(
    "role",
    [
        "dataset",
        "analysis",
        "methods_code",
        "reproduce_code",
        "article",
        "reference_source_1",
    ],
)
def test_every_declared_artifact_hash_is_checked(package, role):
    doc = json.loads((package / "manifest.json").read_text())
    target = package / Path(doc["artifacts"][role]["path"]).name
    target.write_bytes(target.read_bytes() + b"changed")
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["local_computational_acceptance"] is False
    assert report["replay"]["process_executed"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("experiment_executed", "true"),
        ("experiment_executed", 1),
        ("experiment_executed", False),
        ("external_validation", "false"),
        ("external_validation", True),
        ("model_inference_executed", 0),
        ("status", "partial"),
        ("evidence_kind", "synthetic"),
    ],
)
def test_manifest_execution_flags_are_strict(package, field, value):
    path = package / "manifest.json"
    doc = json.loads(path.read_text())
    doc[field] = value
    path.write_text(json.dumps(doc))
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False


@pytest.mark.parametrize(
    "case",
    [
        "missing_file",
        "missing_role",
        "missing_hash",
        "invalid_hash",
        "wrong_bytes",
        "path_traversal",
        "symlink",
        "duplicate_path",
        "unknown_role",
        "empty_file",
    ],
)
def test_missing_or_unsafe_artifacts_block(package, tmp_path, case):
    path = package / "manifest.json"
    doc = json.loads(path.read_text())
    entry = doc["artifacts"]["article"]
    target = package / "article.md"
    if case == "missing_file":
        target.unlink()
    elif case == "missing_role":
        del doc["artifacts"]["article"]
    elif case == "missing_hash":
        del entry["sha256"]
    elif case == "invalid_hash":
        entry["sha256"] = "a"
    elif case == "wrong_bytes":
        entry["bytes"] = True
    elif case == "path_traversal":
        entry["path"] = "../article.md"
    elif case == "symlink":
        outside = tmp_path / "outside.md"
        target.rename(outside)
        target.symlink_to(outside)
    elif case == "duplicate_path":
        entry["path"] = doc["artifacts"]["dataset"]["path"]
    elif case == "unknown_role":
        doc["artifacts"]["hook"] = dict(entry)
    elif case == "empty_file":
        target.write_bytes(b"")
    path.write_text(json.dumps(doc))
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False


@pytest.mark.parametrize(
    "raw",
    [
        '{"status":"completed","status":"completed"}',
        '{"value":NaN}',
        '{"value":Infinity}',
        "{",
    ],
)
def test_json_duplicate_keys_nonfinite_and_invalid_block(package, raw):
    (package / "manifest.json").write_text(raw)
    assert (
        api().verify_scientific_package(package_dir=str(package))["status"] == "blocked"
    )


def test_self_consistent_malicious_code_is_never_executed(package, tmp_path):
    sentinel = tmp_path / "malicious-ran"
    payload = (
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n"
    )
    doc = mutate(package, "methods_code", lambda _: payload)
    methods_hash = doc["artifacts"]["methods_code"]["sha256"]
    mutate(
        package,
        "configuration",
        lambda value: {**value, "methods_sha256": methods_hash},
    )
    mutate(package, "reproduce_code", lambda _: payload)
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False
    assert not sentinel.exists()


@pytest.mark.parametrize(
    "role,change",
    [
        ("reproduction", {"matched": "true"}),
        ("reproduction", {"process_executed": 1}),
        ("reproduction", {"exit_code": False}),
        ("computational_review", {"passed": 1}),
        ("references", None),
        ("reference_source_1", {"evidence_kind": "demonstration"}),
    ],
)
def test_rehashed_invalid_computational_or_bibliographic_receipts_block(
    package, role, change
):
    mutate(package, role, lambda value: [] if change is None else {**value, **change})
    assert (
        api().verify_scientific_package(package_dir=str(package))["status"] == "blocked"
    )


def test_recomputed_hashes_cannot_hide_numeric_mismatch(package):
    doc = mutate(
        package, "analysis", lambda value: {**value, "estimate": value["estimate"] + 10}
    )
    changed = json.loads((package / "analysis.json").read_text())
    doc["analysis"] = changed
    (package / "manifest.json").write_text(json.dumps(doc))
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["local_computational_acceptance"] is False


def test_replay_timeout_cannot_become_acceptance(package, monkeypatch):
    module = api()

    def expire(*args, **kwargs):
        raise subprocess.TimeoutExpired("trusted replay", 1)

    monkeypatch.setattr(module.subprocess, "run", expire)
    report = module.verify_scientific_package(
        package_dir=str(package), timeout_seconds=1
    )
    assert report["status"] == "blocked"
    assert report["reason"] == "replay_timeout"
    assert report["replay"]["matched"] is False


def test_root_symlink_is_rejected(package, tmp_path):
    link = tmp_path / "linked-package"
    link.symlink_to(package, target_is_directory=True)
    report = api().verify_scientific_package(package_dir=str(link))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False


def test_fully_rehashed_forged_result_is_rejected_by_actual_replay(package):
    from research.provenance_pipeline import _article, _json

    doc = mutate(
        package, "analysis", lambda value: {**value, "estimate": value["estimate"] + 10}
    )
    analysis = json.loads((package / "analysis.json").read_text())
    doc["analysis"] = analysis
    (package / "manifest.json").write_text(json.dumps(doc))
    doc = mutate(
        package,
        "reproduction",
        lambda value: {
            **value,
            "analysis_sha256": hashlib.sha256(_json(analysis).encode()).hexdigest(),
        },
    )
    reproduction = json.loads((package / "reproduction.json").read_text())
    doc["reproduction"] = reproduction
    (package / "manifest.json").write_text(json.dumps(doc))
    references = json.loads((package / "references.json").read_text())
    article = _article(
        doc["question"],
        doc["provenance"]["dataset"],
        analysis,
        references,
        reproduction,
    )
    mutate(package, "article", lambda _: article)
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["reason"] == "trusted_replay_analysis_mismatch"
    assert report["replay"]["process_executed"] is True
    assert report["replay"]["matched"] is False


def test_unlisted_python_shadow_module_is_not_imported(package, tmp_path):
    sentinel = tmp_path / "module-imported"
    (package / "json.py").write_text(
        f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('bad')\nraise RuntimeError('bad')\n"
    )
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "locally_verified", report
    assert report["replay"]["package_code_executed"] is False
    assert not sentinel.exists()


def test_windows_legacy_absolute_paths_are_relocated_without_external_reads(package):
    path = package / "manifest.json"
    doc = json.loads(path.read_text())
    for entry in doc["artifacts"].values():
        entry["path"] = "C:\\old-study\\" + Path(entry["path"]).name
    path.write_text(json.dumps(doc))
    assert (
        api().verify_scientific_package(package_dir=str(package))["status"]
        == "locally_verified"
    )


def test_process_start_failure_does_not_claim_execution(package, monkeypatch):
    module = api()

    def unavailable(*args, **kwargs):
        raise OSError("process cannot start")

    monkeypatch.setattr(module.subprocess, "Popen", unavailable)
    report = module.verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False


def test_fifo_artifact_is_rejected_without_waiting(package):
    import os

    target = package / "article.md"
    target.unlink()
    os.mkfifo(target)
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False


def test_rehashed_reference_title_must_match_source_snapshot(package):
    mutate(
        package, "references", lambda refs: [{**refs[0], "title": "Claim sem fonte"}]
    )
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["reason"] == "references_snapshot_mismatch"
    assert report["replay"]["process_executed"] is False


def test_rehashed_nonfinite_analysis_is_rejected(package):
    path = package / "analysis.json"
    raw = path.read_bytes().replace(
        b'"estimate": 6.333333333333333', b'"estimate": 1e999'
    )
    assert raw != path.read_bytes()
    path.write_bytes(raw)
    manifest_path = package / "manifest.json"
    doc = json.loads(manifest_path.read_text())
    doc["artifacts"]["analysis"].update(
        sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)
    )
    manifest_path.write_text(json.dumps(doc))
    report = api().verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["replay"]["process_executed"] is False


@pytest.mark.parametrize("delta", ["one_ulp", "bounded_absolute"])
def test_replay_accepts_only_bounded_float_variation_and_reports_it(
    package, monkeypatch, delta
):
    module = api()
    replay = module._replay

    def vary_float(*args, **kwargs):
        result = replay(*args, **kwargs)
        estimate = result["analysis"]["estimate"]
        result["analysis"]["estimate"] = (
            math.nextafter(estimate, math.inf)
            if delta == "one_ulp"
            else estimate + 5e-13
        )
        return result

    monkeypatch.setattr(module, "_replay", vary_float)
    report = module.verify_scientific_package(package_dir=str(package))
    assert report["status"] == "locally_verified", report
    assert report["replay"]["numeric_tolerance"] == {"rtol": 1e-12, "atol": 1e-12}
    assert 0 < report["replay"]["max_abs_difference"] < 1e-12
    assert report["replay"]["runtime"]["scipy"]


@pytest.mark.parametrize(
    "change",
    [
        "outside_tolerance",
        "count_float",
        "count_integer",
        "seed",
        "boolean",
        "missing_key",
        "unknown_key",
        "text",
        "nonfinite",
        "alpha",
    ],
)
def test_replay_float_tolerance_never_relaxes_schema_counts_flags_or_configuration(
    package, monkeypatch, change
):
    module = api()
    replay = module._replay

    def vary_output(*args, **kwargs):
        result = replay(*args, **kwargs)
        analysis = result["analysis"]
        if change == "outside_tolerance":
            analysis["estimate"] += 1e-8
        elif change == "count_float":
            analysis["n"] = float(analysis["n"])
        elif change == "count_integer":
            analysis["n"] += 1
        elif change == "seed":
            analysis["seed"] += 1
        elif change == "boolean":
            analysis["experiment_executed"] = 1
        elif change == "missing_key":
            del analysis["limitations"]
        elif change == "unknown_key":
            analysis["extra"] = 1
        elif change == "text":
            analysis["limitations"].reverse()
        elif change == "nonfinite":
            analysis["estimate"] = float("inf")
        elif change == "alpha":
            analysis["alpha"] = math.nextafter(analysis["alpha"], math.inf)
        return result

    monkeypatch.setattr(module, "_replay", vary_output)
    report = module.verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["reason"] == "trusted_replay_analysis_mismatch"
    assert report["replay"]["process_executed"] is True
    assert report["replay"]["matched"] is False


@pytest.mark.parametrize(
    "actual,expected,accepted",
    [
        ({"p_value": -1e-16}, {"p_value": 0.0}, False),
        ({"p_value": 1.0000000000000002}, {"p_value": 1.0}, False),
        ({"p_value": 1e-16}, {"p_value": 0.0}, True),
        ({"estimate": 100000000.00005}, {"estimate": 100000000.0}, True),
        ({"estimate": 100000000.001}, {"estimate": 100000000.0}, False),
    ],
)
def test_numeric_portability_keeps_probability_domain_and_relative_budget(
    actual, expected, accepted
):
    matched, difference = api()._compare_replayed_analysis(actual, expected)
    assert matched is accepted
    assert math.isfinite(difference)


def test_extreme_finite_replay_difference_preserves_structured_block(
    package, monkeypatch
):
    from research.provenance_pipeline import _article, _json

    doc = mutate(package, "analysis", lambda value: {**value, "estimate": 1e308})
    analysis = json.loads((package / "analysis.json").read_text())
    doc["analysis"] = analysis
    (package / "manifest.json").write_text(json.dumps(doc))
    doc = mutate(
        package,
        "reproduction",
        lambda value: {
            **value,
            "analysis_sha256": hashlib.sha256(_json(analysis).encode()).hexdigest(),
        },
    )
    reproduction = json.loads((package / "reproduction.json").read_text())
    doc["reproduction"] = reproduction
    (package / "manifest.json").write_text(json.dumps(doc))
    references = json.loads((package / "references.json").read_text())
    article = _article(
        doc["question"],
        doc["provenance"]["dataset"],
        analysis,
        references,
        reproduction,
    )
    mutate(package, "article", lambda _: article)
    module = api()
    replay = module._replay

    def extreme_result(*args, **kwargs):
        result = replay(*args, **kwargs)
        result["analysis"][
            "estimate"
        ] = -1e308  # Retorno extremo controlado; processo real acima.
        return result

    monkeypatch.setattr(module, "_replay", extreme_result)
    report = module.verify_scientific_package(package_dir=str(package))
    assert report["status"] == "blocked"
    assert report["reason"] == "trusted_replay_analysis_mismatch"
    assert report["replay"]["process_executed"] is True
    assert report["replay"]["matched"] is False
    assert report["replay"]["max_abs_difference"] is None
    assert report["replay"]["numeric_difference_overflow"] is True
    assert len(report["report_sha256"]) == 64
