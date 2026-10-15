"""R897: processos locais reais sobre targets controlados; sem perfil real do Core."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import subprocess
import time

import psutil
import pytest

from scripts.validate_scientific_profile import PROFILE_GROUPS


CORE = Path(__file__).resolve().parents[1]
FIRST_TARGET = PROFILE_GROUPS[0][1][0]


def api():
    try:
        return importlib.import_module("integrations.local_ci")
    except ModuleNotFoundError:
        pytest.fail("R897 exige o backend local real, ainda ausente")


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init", "-q")
    (root / "scripts").mkdir()
    for name in ("validate_scientific_profile.py", "quality_report.py"):
        (root / "scripts" / name).write_bytes((CORE / "scripts" / name).read_bytes())
    (root / "scripts/__init__.py").write_text("")
    (root / "pytest.ini").write_text("[pytest]\npythonpath = .\n")
    (root / "calculation.py").write_text("VALUE = 1\n")
    targets = {}
    for _, group in PROFILE_GROUPS:
        for target in group:
            filename, *selectors = target.split("::")
            targets.setdefault(filename, set()).add(selectors[0] if selectors else "test_fixture")
    for filename, functions in targets.items():
        path = root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(f"def {name}():\n    assert 2 + 3 == 5\n" for name in sorted(functions)))
    git(root, "add", ".")
    git(root, "-c", "user.name=R897 Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "Fixture local controlada")
    return root


def service(project, tmp_path):
    return api().LocalCIService(repo_root=project, state_dir=tmp_path / "ci-state")


def wait_terminal(ci, run_id, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = ci.status(run_id)
        if result["status"] in {"passed", "blocked", "cancelled"}:
            return result
        time.sleep(0.05)
    ci.cancel(run_id)
    pytest.fail("Supervisor não concluiu no prazo da prova dirigida")


def start_passed(ci):
    started = ci.start()
    assert started["status"] in {"queued", "running"}
    result = wait_terminal(ci, started["run_id"])
    assert result["status"] == "passed", result
    return result


def test_idle_is_not_a_passing_run(project, tmp_path):
    ci = service(project, tmp_path)
    assert ci.status()["status"] == "idle"
    assert ci.runs()["runs"] == []
    assert not (tmp_path / "ci-state/runs").exists()


def test_real_async_run_has_validated_fresh_receipts_and_scope(project, tmp_path):
    ci = service(project, tmp_path)
    started = ci.start()
    assert started["status"] in {"queued", "running"}
    result = wait_terminal(ci, started["run_id"])
    assert result["status"] == "passed", result
    assert result["receipt_validation"]["verified"] is True
    assert result["current_compatibility"] == {"sources_match": True, "head_matches": True, "applicable": True}
    assert result["scope"] == "enumerated_scientific_regression_profile"
    assert result["github_check_created"] is False
    assert result["external_validation"] is False
    assert result["head_start"] == result["head_end"] == git(project, "rev-parse", "HEAD").stdout.strip()
    assert result["totals"]["passed"] > 0 and result["totals"]["failed"] == 0
    assert Path(result["report_path"]).is_relative_to(Path(result["run_dir"]))
    assert ci.runs(limit=1)["runs"][0]["run_id"] == started["run_id"]


@pytest.mark.parametrize("changed", ["source", "head"])
def test_historical_result_remains_separate_from_current_compatibility(project, tmp_path, changed):
    ci = service(project, tmp_path)
    result = start_passed(ci)
    if changed == "source":
        (project / "calculation.py").write_text("VALUE = 7\n")
    else:
        git(project, "-c", "user.name=R897 Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "--allow-empty", "-qm", "Novo HEAD de fixture")
    checked = ci.status(result["run_id"])
    assert checked["status"] == "passed"
    assert checked["receipt_validation"]["verified"] is True
    assert checked["current_compatibility"]["applicable"] is False
    assert checked["current_compatibility"]["sources_match"] is (changed != "source")
    assert checked["current_compatibility"]["head_matches"] is (changed != "head")


def test_single_writer_blocks_other_process_and_cancel_releases_lock(project, tmp_path):
    (project / FIRST_TARGET).write_text("import time\ndef test_wait(): time.sleep(30)\n")
    ci = service(project, tmp_path)
    first = ci.start()
    other = api().LocalCIService(project, tmp_path / "ci-state")
    busy = other.start()
    assert busy["status"] == "busy"
    assert busy["reason_codes"] == ["single_writer_busy"]
    assert ci.cancel(first["run_id"])["status"] == "cancellation_requested"
    assert wait_terminal(ci, first["run_id"])["status"] == "cancelled"
    second = other.start()
    assert second["status"] in {"queued", "running"}
    assert second["run_id"] != first["run_id"]
    other.cancel(second["run_id"])
    assert wait_terminal(other, second["run_id"])["status"] == "cancelled"


def test_cancel_cleans_owned_descendant_in_separate_session(project, tmp_path):
    (project / FIRST_TARGET).write_text(
        "import subprocess,sys,time\nfrom pathlib import Path\ndef test_wait():\n"
        "    p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],start_new_session=True)\n"
        "    Path('owned.pid').write_text(str(p.pid))\n    time.sleep(60)\n")
    ci = service(project, tmp_path)
    started = ci.start()
    deadline = time.monotonic() + 15
    while not (project / "owned.pid").exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert (project / "owned.pid").exists(), ci.status(started["run_id"])
    pid = int((project / "owned.pid").read_text())
    neighbour = subprocess.Popen([os.sys.executable, "-c", "import time;time.sleep(30)"], start_new_session=True)
    try:
        assert ci.cancel(started["run_id"])["status"] == "cancellation_requested"
        result = wait_terminal(ci, started["run_id"])
        assert result["status"] == "cancelled"
        assert result["cleanup_complete"] is True
        assert not psutil.pid_exists(pid) or psutil.Process(pid).status() == psutil.STATUS_ZOMBIE
        assert neighbour.poll() is None
    finally:
        neighbour.terminate()
        neighbour.wait(timeout=5)


@pytest.mark.parametrize("body", [
    "def test_failure(): assert False\n",
    "import os\ndef test_exit_without_receipt(): os._exit(0)\n",
    "import pytest\n@pytest.mark.skip(reason='não executado')\ndef test_skip(): pass\n",
])
def test_failure_skip_or_zero_exit_without_receipt_never_pass(project, tmp_path, body):
    (project / FIRST_TARGET).write_text(body)
    ci = service(project, tmp_path)
    result = wait_terminal(ci, ci.start()["run_id"])
    assert result["status"] == "blocked"
    assert result["receipt_validation"]["verified"] is False


def test_source_change_during_run_blocks_acceptance(project, tmp_path):
    (project / FIRST_TARGET).write_text(
        "from pathlib import Path\ndef test_change(): Path('calculation.py').write_text('VALUE = 9\\n')\n")
    ci = service(project, tmp_path)
    result = wait_terminal(ci, ci.start()["run_id"])
    assert result["status"] == "blocked"
    assert result["receipt_validation"]["verified"] is False


@pytest.mark.parametrize("change", ["deselect_target", "extra_target"])
def test_collection_must_preserve_exact_registered_target_scope(project, tmp_path, change):
    if change == "deselect_target":
        hook = ("def pytest_collection_modifyitems(items):\n"
                f"    items[:] = [item for item in items if item.nodeid.split('::')[0] != {FIRST_TARGET!r}]\n")
    else:
        (project / "tests/test_outside_selection.py").write_text("def test_outside(): assert True\n")
        hook = ("import pytest\nfrom pathlib import Path\ndef pytest_collection_modifyitems(items):\n"
                "    module = pytest.Module.from_parent(items[0].session, path=Path(__file__).parent/'tests/test_outside_selection.py')\n"
                "    items.extend(module.collect())\n")
    (project / "conftest.py").write_text(hook)
    ci = service(project, tmp_path)
    result = wait_terminal(ci, ci.start()["run_id"])
    assert result["status"] == "blocked", result
    assert result["receipt_validation"]["verified"] is False


def test_previous_summary_cannot_be_reused_in_a_new_execution(project, tmp_path):
    ci = service(project, tmp_path)
    old = start_passed(ci)
    previous = Path(old["report_path"])
    started = ci.start()
    assert started["run_id"] != old["run_id"]
    reports = Path(started["run_dir"]) / "reports"
    deadline = time.monotonic() + 10
    while not reports.is_dir() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert reports.is_dir()
    stale = reports / previous.parent.name
    stale.mkdir()
    (stale / "summary.json").write_bytes(previous.read_bytes())
    result = wait_terminal(ci, started["run_id"])
    assert result["status"] == "blocked"
    assert result["receipt_validation"]["verified"] is False


@pytest.mark.parametrize("damage", ["metadata", "summary", "junit", "ledger", "delete", "symlink"])
def test_tampered_metadata_or_artifacts_never_display_passed(project, tmp_path, damage):
    ci = service(project, tmp_path)
    result = start_passed(ci)
    summary_path = Path(result["report_path"])
    summary = json.loads(summary_path.read_text())
    if damage == "metadata":
        record_path = Path(result["record_path"])
        envelope = json.loads(record_path.read_text())
        envelope["payload"]["head_start"] = "0" * 40
        record_path.write_text(json.dumps(envelope))
    elif damage == "summary":
        summary["totals"]["passed"] += 1
        summary_path.write_text(json.dumps(summary))
    else:
        target = Path(summary["groups"][0]["junit_path" if damage == "junit" else "ledger_path"])
        if damage == "delete":
            target.unlink()
        elif damage == "symlink":
            saved = tmp_path / "outside.json"
            saved.write_bytes(target.read_bytes())
            target.unlink()
            target.symlink_to(saved)
        else:
            target.write_text("{}")
    checked = ci.status(result["run_id"])
    assert checked["status"] == "blocked"
    assert checked["receipt_validation"]["verified"] is False


@pytest.mark.parametrize("limit_kind", ["time", "memory"])
def test_supervisor_enforces_lowered_bounds(project, tmp_path, limit_kind):
    (project / FIRST_TARGET).write_text("import time\ndef test_wait(): time.sleep(30)\n")
    ci = service(project, tmp_path)
    ci._limits["timeout_seconds" if limit_kind == "time" else "max_rss_bytes"] = 0.5 if limit_kind == "time" else 32 * 1024 * 1024
    result = wait_terminal(ci, ci.start()["run_id"])
    assert result["status"] == "blocked"
    assert ("timeout" if limit_kind == "time" else "memory_limit") in result["reason_codes"]
    assert result["cleanup_complete"] is True


@pytest.mark.parametrize("value", [None, True, 1, "all", "tests/", "scientific; echo unsafe"])
def test_public_profile_rejects_arbitrary_commands_and_types(project, tmp_path, value):
    with pytest.raises(ValueError):
        service(project, tmp_path).start(profile=value)


@pytest.mark.parametrize("value", [True, 0, -1, 101, "20"])
def test_run_listing_requires_bounded_integer(project, tmp_path, value):
    with pytest.raises(ValueError):
        service(project, tmp_path).runs(limit=value)


def test_ids_and_state_symlinks_are_rejected(project, tmp_path):
    ci = service(project, tmp_path)
    with pytest.raises(ValueError):
        ci.status("../private")
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "ci-state").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        ci.start()
    assert list(outside.iterdir()) == []
