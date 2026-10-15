"""R891: o perfil enumerado exige execução completa, atual e delimitada."""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest


def api():
    try:
        return importlib.import_module("scripts.validate_scientific_profile")
    except ModuleNotFoundError:
        pytest.fail("R891 não possui executor delimitado do perfil científico")


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "tests").mkdir()
    (root / "pytest.ini").write_text("[pytest]\npythonpath = .\n")
    (root / "calculation.py").write_text("def result(): return 5\n")
    return root


def execute(root, tmp_path, source, *, timeout=15, memory=256 * 1024 * 1024):
    module = api()
    (root / "tests/test_contract.py").write_text(source, encoding="utf-8")
    return module.run_profile(
        root, tmp_path / "receipts", groups=(("contract", ("tests/test_contract.py",)),),
        group_timeout=timeout, max_rss_bytes=memory,
    )


def test_profile_is_closed_explicit_and_bounded():
    module = api()
    assert tuple(name for name, _ in module.PROFILE_GROUPS) == (
        "provenance_release", "manuscripts", "workflow_memory", "reasoning_integrity",
        "delivery_contracts", "managed_agents_plugins", "python_graph",
        "local_ci_lifecycle", "local_ci_receipt_integrity", "local_ci_selection_freshness",
    )
    targets = [target for _, group in module.PROFILE_GROUPS for target in group]
    assert len(targets) == len(set(targets))
    assert all(target.startswith("tests/test_") and "*" not in target for target in targets)
    assert module.DEFAULT_GROUP_TIMEOUT == 180
    assert module.DEFAULT_MAX_RSS_BYTES == 1536 * 1024 * 1024
    assert {"tests/test_r891_scientific_profile.py", "tests/test_r894_agent_lifecycle.py",
            "tests/test_r894_orchestration_surfaces.py", "tests/test_r895_requested_plugins.py",
            "tests/test_r896_python_code_graph.py"} <= set(targets)
    assert "tests/test_r897_local_ci.py::test_tampered_metadata_or_artifacts_never_display_passed" in targets
    assert "tests/test_r897_local_ci.py::test_collection_must_preserve_exact_registered_target_scope" in targets
    assert all("lean" not in target.split("::", 1)[0].lower() for target in targets)


def test_real_passing_run_records_selection_hashes_and_junit(project, tmp_path, monkeypatch):
    monkeypatch.setenv("PYTEST_ADDOPTS", "--impossible-external-option")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "external"))
    report = execute(project, tmp_path,
        "import os\nfrom calculation import result\n"
        "def test_result():\n    assert result() == 5\n"
        "    assert 'PYTEST_ADDOPTS' not in os.environ\n"
        "    assert 'PYTHONPATH' not in os.environ\n"
        "    assert os.environ['OPENBLAS_NUM_THREADS'] == '1'\n")
    assert report["status"] == "passed"
    assert report["scope"] == "enumerated_scientific_regression_profile"
    assert report["global_suite_executed"] is False
    assert report["external_scientific_validation"] is False
    assert report["source_before"]["digest"] == report["source_after"]["digest"]
    assert "calculation.py" in report["source_before"]["files"]
    assert report["totals"] == {"total": 1, "passed": 1, "failed": 0, "errors": 0, "skipped": 0}
    group = report["groups"][0]
    assert group["selected_nodeids"] == ["tests/test_contract.py::test_result"]
    assert group["executed_nodeids"] == group["selected_nodeids"]
    assert group["peak_rss_bytes"] > 0
    assert Path(group["junit_path"]).is_file()
    assert Path(group["log_path"]).is_file()
    assert json.loads(Path(report["report_path"]).read_text())["status"] == "passed"


def test_recorder_survives_test_patching_os_replace_until_teardown(project, tmp_path):
    report = execute(project, tmp_path,
        "import os, pytest\n"
        "def test_replace_failure(monkeypatch):\n"
        "    def unavailable(*args, **kwargs):\n"
        "        raise OSError('falha deliberada de substituicao')\n"
        "    monkeypatch.setattr(os, 'replace', unavailable)\n"
        "    with pytest.raises(OSError, match='falha deliberada'):\n"
        "        os.replace('origem', 'destino')\n")
    assert report["status"] == "passed"
    assert report["totals"] == {"total": 1, "passed": 1, "failed": 0, "errors": 0, "skipped": 0}
    group = report["groups"][0]
    nodeid = "tests/test_contract.py::test_replace_failure"
    assert group["selected_nodeids"] == group["executed_nodeids"] == [nodeid]
    ledger = json.loads((Path(group["junit_path"]).parent / "execution.json").read_text())
    assert ledger["session_complete"] is True and ledger["exit_code"] == 0
    assert [(item["nodeid"], item["when"], item["outcome"]) for item in ledger["reports"]] == [
        (nodeid, "setup", "passed"), (nodeid, "call", "passed"), (nodeid, "teardown", "passed")]
    cases = list(ET.parse(group["junit_path"]).getroot().iter("testcase"))
    assert len(cases) == 1 and cases[0].get("name") == "test_replace_failure"
    assert cases[0].find("failure") is None and cases[0].find("error") is None
    assert report["source_before"]["digest"] == report["source_after"]["digest"]


def test_real_atomic_recording_failure_is_not_suppressed(tmp_path):
    destination = tmp_path / "execution.json"
    destination.mkdir()
    with pytest.raises(OSError):
        api()._write_json(destination, {"session_complete": True})
    assert destination.is_dir()
    assert not list(destination.iterdir())


@pytest.mark.parametrize("source,reason", [
    ("def test_bad():\n    assert False\n", "pytest_exit"),
    ("import pytest\n@pytest.mark.skip(reason='sem execução')\ndef test_bad(): pass\n", "skipped"),
    ("raise RuntimeError('collection failed')\n", "pytest_exit"),
    ("VALUE = 1\n", "zero_tests"),
])
def test_real_incomplete_run_never_passes(project, tmp_path, source, reason):
    report = execute(project, tmp_path, source)
    assert report["status"] == "blocked"
    assert any(reason in problem for problem in report["groups"][0]["problems"])


def test_source_mutation_during_execution_blocks_acceptance(project, tmp_path):
    report = execute(project, tmp_path,
        "from pathlib import Path\ndef test_change():\n"
        "    Path('calculation.py').write_text('def result(): return 6\\n')\n")
    assert report["groups"][0]["status"] == "passed"
    assert report["status"] == "blocked"
    assert "source_changed" in report["problems"]
    assert report["changed_sources"] == ["calculation.py"]


def test_run_never_reuses_old_output_directory(project, tmp_path):
    first = execute(project, tmp_path, "def test_ok(): pass\n")
    second = execute(project, tmp_path, "def test_ok(): pass\n")
    assert first["run_id"] != second["run_id"]
    assert first["run_dir"] != second["run_dir"]
    assert Path(first["report_path"]).is_file()
    assert Path(second["report_path"]).is_file()


def test_snapshot_includes_untracked_and_tracked_changes_but_not_private_outputs(project):
    module = api()
    subprocess.run(["git", "add", "calculation.py"], cwd=project, check=True)
    for name in ["docs/note.py", "artigos/a.py", "reports/out.py", ".venv/lib.py",
                 "vendor/pkg.py", "secrets.json", ".env", "config/.env.local"]:
        p = project / name
        p.parent.mkdir(exist_ok=True, parents=True)
        p.write_text("not production")
    (project / "new.py").write_text("NEW = True\n")
    initial = module.source_snapshot(project)
    assert {"calculation.py", "new.py", "pytest.ini"} <= set(initial["files"])
    assert not any(".env" in key or "secrets" in key for key in initial["files"])
    assert not any(key.startswith(("docs/", "artigos/", "reports/", ".venv/", "vendor/")) for key in initial["files"])
    (project / "calculation.py").write_text("def result(): return 7\n")
    assert module.source_snapshot(project)["digest"] != initial["digest"]


def test_missing_git_snapshot_blocks_without_starting_tests(tmp_path):
    module = api()
    root = tmp_path / "not-git"
    root.mkdir()
    report = module.run_profile(root, tmp_path / "receipts",
        groups=(("contract", ("tests/test_contract.py",)),))
    assert report["status"] == "blocked"
    assert report["groups"] == []
    assert "source_snapshot_failed" in report["problems"]


def test_timeout_stops_owned_child_and_records_unexecuted_group(project, tmp_path):
    module = api()
    (project / "tests/test_contract.py").write_text(
        "import subprocess,sys,time\nfrom pathlib import Path\ndef test_wait():\n"
        "    child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])\n"
        "    Path('owned.pid').write_text(str(child.pid))\n    time.sleep(30)\n")
    report = module.run_profile(project, tmp_path / "receipts",
        groups=(("slow", ("tests/test_contract.py",)), ("later", ("tests/test_contract.py::test_wait",))),
        group_timeout=1.5, max_rss_bytes=256 * 1024 * 1024)
    assert report["status"] == "blocked"
    assert "timeout" in report["groups"][0]["problems"]
    assert report["not_executed_groups"] == ["later"]
    pidfile = project / "owned.pid"
    assert pidfile.exists(), "O teste deve realmente iniciar o descendente"
    pid = int(pidfile.read_text())
    process = module.psutil.Process(pid) if module.psutil.pid_exists(pid) else None
    assert process is None or process.status() == module.psutil.STATUS_ZOMBIE


def test_memory_budget_stops_real_allocation(project, tmp_path):
    report = execute(project, tmp_path,
        "import time\ndef test_allocate():\n"
        "    payload = bytearray(80 * 1024 * 1024)\n    time.sleep(5)\n",
        memory=64 * 1024 * 1024)
    assert report["status"] == "blocked"
    assert "memory_limit" in report["groups"][0]["problems"]


@pytest.mark.parametrize("damage", ["missing_ledger", "wrong_run", "old_junit", "partial_ledger", "missing_case",
                                  "non_object_ledger", "malformed_phase", "truthy_exit"])
def test_report_validation_blocks_stale_or_incomplete_receipts(project, tmp_path, damage):
    module = api()
    report = execute(project, tmp_path, "def test_ok(): pass\n")
    group = report["groups"][0]
    folder = Path(group["junit_path"]).parent
    ledger_path = folder / "execution.json"
    ledger = json.loads(ledger_path.read_text())
    if damage == "missing_ledger":
        ledger_path.unlink()
    elif damage == "wrong_run":
        ledger["run_id"] = "previous-run"
        ledger_path.write_text(json.dumps(ledger))
    elif damage == "old_junit":
        os.utime(group["junit_path"], ns=(1, 1))
    elif damage == "partial_ledger":
        ledger["session_complete"] = False
        ledger_path.write_text(json.dumps(ledger))
    elif damage == "missing_case":
        ledger["selected_nodeids"].append("tests/test_contract.py::test_missing")
        ledger_path.write_text(json.dumps(ledger))
    elif damage == "non_object_ledger":
        ledger_path.write_text("[]")
    elif damage == "malformed_phase":
        ledger["reports"] = ["passed"]
        ledger_path.write_text(json.dumps(ledger))
    else:
        ledger["exit_code"] = False
        ledger_path.write_text(json.dumps(ledger))
    checked = module.validate_group_receipts(folder, report["run_id"],
        group["started_ns"], time.time_ns(), 0)
    assert checked["status"] == "blocked"
    assert checked["problems"]


def test_failure_exit_is_not_masked_by_passing_junit(project, tmp_path):
    module = api()
    report = execute(project, tmp_path, "def test_ok(): pass\n")
    group = report["groups"][0]
    checked = module.validate_group_receipts(Path(group["junit_path"]).parent,
        report["run_id"], group["started_ns"], time.time_ns(), 2)
    assert checked["status"] == "blocked"
    assert "pytest_exit:2" in checked["problems"]


@pytest.mark.parametrize("options", [
    {"group_timeout": 0}, {"group_timeout": float("nan")},
    {"max_rss_bytes": 0}, {"max_rss_bytes": True}, {"groups": ()},
    {"groups": (("escape", ("../outside.py",)),)},
    {"groups": (("unsafe-name/../../elsewhere", ("tests/test_contract.py",)),)},
])
def test_invalid_limits_or_selection_fail_before_process(project, tmp_path, options):
    with pytest.raises(ValueError):
        api().run_profile(project, tmp_path / "receipts", **options)
