"""R866: relatório da única execução e skips nunca convertidos em medição verde."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def report_module(monkeypatch):
    spec = importlib.util.spec_from_file_location("quality_r866", ROOT / "scripts/quality_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "estimate_coverage", lambda: {})
    monkeypatch.setattr(module, "check_lint", lambda: {"errors": 0, "status": "clean"})
    return module


def write_junit(tmp_path, content):
    path = tmp_path / "pytest.xml"
    path.write_text(content, encoding="utf-8")
    return path


def test_ci_instala_node_e_lock_antes_da_suite():
    steps = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())["jobs"]["test"]["steps"]
    node = next((i for i, step in enumerate(steps) if step.get("uses", "").startswith("actions/setup-node@")), None)
    npm = next((i for i, step in enumerate(steps) if step.get("run", "").strip() == "npm ci"), None)
    suite = next(i for i, step in enumerate(steps) if "python -m pytest tests/" in step.get("run", ""))
    assert node is not None and npm is not None and node < npm < suite
    assert int(str(steps[node]["with"]["node-version"]).split(".")[0]) >= 22
    assert steps[node]["with"]["cache-dependency-path"] == ".opencode/package-lock.json"
    assert steps[npm]["working-directory"] == ".opencode"


def test_ci_gera_junit_e_reutiliza_sem_segunda_suite():
    steps = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())["jobs"]["test"]["steps"]
    commands = [step.get("run", "") for step in steps]
    assert sum("python -m pytest tests/" in command for command in commands) == 1
    suite = next(command for command in commands if "python -m pytest tests/" in command)
    report = next(step for step in steps if "python scripts/quality_report.py" in step.get("run", ""))
    assert "--junitxml=reports/pytest.xml" in suite
    assert "--junit reports/pytest.xml" in report["run"]
    assert "--quick" not in report["run"]
    assert report["if"] == "always()"
    assert any(step.get("uses", "").startswith("actions/upload-artifact@") and step.get("if") == "always()" for step in steps)


def test_junit_conta_casos_sem_somar_agregados_duas_vezes(report_module, tmp_path):
    path = write_junit(tmp_path, '<testsuites tests="4"><testsuite tests="4" failures="1" errors="1" skipped="1">'
        '<testcase name="pass"/><testcase name="fail"><failure/></testcase>'
        '<testcase name="error"><error/></testcase><testcase name="skip"><skipped/></testcase>'
        '</testsuite></testsuites>')
    counts = report_module.load_junit_results(path)
    assert {key: counts[key] for key in ["total", "passed", "failed", "errors", "skipped"]} == {
        "total": 4, "passed": 1, "failed": 1, "errors": 1, "skipped": 1}
    assert counts["pass_rate"] == 25.0
    assert counts["source"] == "provided_junit"


def test_subtestes_apenas_no_agregado_pytest_nao_inventam_aprovacoes(report_module, tmp_path):
    path = write_junit(tmp_path, '<testsuites><testsuite name="pytest" tests="3" failures="0" errors="0" skipped="1">'
        '<testcase name="pass"/><testcase name="skip"><skipped/></testcase></testsuite></testsuites>')
    report = report_module.generate_report(junit_path=path)
    counts = report["test_results"]
    assert counts["total"] == 2 and counts["passed"] == 1 and counts["skipped"] == 1
    assert counts["declared_tests"] == 3 and counts["unrepresented_tests"] == 1
    assert counts["suite_aggregate_fully_represented"] is False
    assert counts["pass_rate"] == 50.0
    assert report["overall_status"] == "PASS_WITH_SKIPS"
    assert any("não incluídos" in item for item in report["recommendations"])


def test_relatorio_junit_nao_executa_pytest(report_module, monkeypatch, tmp_path):
    path = write_junit(tmp_path, '<testsuites><testsuite tests="2" skipped="1"><testcase name="pass"/>'
        '<testcase name="skip"><skipped/></testcase></testsuite></testsuites>')
    monkeypatch.setattr(report_module, "run_tests", lambda: pytest.fail("Suíte não pode ser repetida"))
    report = report_module.generate_report(junit_path=path)
    assert report["test_results"]["passed"] == 1
    assert report["test_results"]["skipped"] == 1
    assert report["overall_status"] == "PASS_WITH_SKIPS"


@pytest.mark.parametrize("element", ["failure", "error"])
def test_falha_e_erro_do_junit_nao_recebem_pass(report_module, tmp_path, element):
    path = write_junit(tmp_path, f'<testsuite><testcase name="failed"><{element}/></testcase></testsuite>')
    report = report_module.generate_report(junit_path=path)
    assert report["overall_status"] == "FAIL"
    assert report["test_results"]["passed"] == 0


def test_junit_so_com_skips_nao_recebe_pass(report_module, tmp_path):
    path = write_junit(tmp_path, '<testsuite tests="1" skipped="1"><testcase name="skip"><skipped/></testcase></testsuite>')
    report = report_module.generate_report(junit_path=path)
    assert report["overall_status"] == "NOT_RUN"
    assert report["test_results"]["pass_rate"] is None
    assert report["quality_score"]["overall_score"] is None


@pytest.mark.parametrize("content", ["<testsuites/>", '<testsuite tests="2"><testcase name="one"/></testsuite>',
    '<testsuite tests="1" failures="1"><testcase name="one"/></testsuite>', "not XML",
    '<!DOCTYPE testsuite [<!ENTITY sample "x">]><testsuite><testcase name="one"/></testsuite>'])
def test_junit_recusa_dados_ausentes_ou_incoerentes(report_module, tmp_path, content):
    path = write_junit(tmp_path, content)
    with pytest.raises(ValueError):
        report_module.load_junit_results(path)


def test_quick_nao_inventa_medicao_verde(report_module, monkeypatch):
    monkeypatch.setattr(report_module, "run_tests", lambda: pytest.fail("Modo quick não executa"))
    report = report_module.generate_report(quick=True)
    assert report["overall_status"] == "NOT_RUN"
    assert report["test_results"]["executed"] is False
    assert report["test_results"]["pass_rate"] is None
    assert report["quality_score"]["overall_score"] is None


def test_execucao_cli_default_mantem_timeout_suficiente(report_module, monkeypatch):
    observed = []

    def completed(*args, **kwargs):
        observed.append(kwargs["timeout"])
        return SimpleNamespace(returncode=0, stdout="1 passed in 1.0s", stderr="")

    monkeypatch.setattr(report_module.subprocess, "run", completed)
    result = report_module.run_tests()
    assert observed == [3600]
    assert result["passed"] == 1 and result["exit_code"] == 0


def test_returncode_nao_zero_reprova_mesmo_sem_contador_failed(report_module, monkeypatch):
    monkeypatch.setattr(report_module.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(
        returncode=2, stdout="collection interrupted", stderr=""))
    report = report_module.generate_report()
    assert report["overall_status"] == "FAIL"
    assert report["test_results"]["exit_code"] == 2


def test_timeout_cli_e_falha_tipificada(report_module, monkeypatch):
    def expired(*args, **kwargs):
        raise subprocess.TimeoutExpired([sys.executable, "-m", "pytest"], kwargs["timeout"])

    monkeypatch.setattr(report_module.subprocess, "run", expired)
    report = report_module.generate_report()
    assert report["overall_status"] == "FAIL"
    assert report["test_results"]["execution_error"] == "timeout"


def test_cli_junit_reprovado_retorna_falha(report_module, monkeypatch, tmp_path, capsys):
    path = write_junit(tmp_path, '<testsuite><testcase name="failed"><failure/></testcase></testsuite>')
    monkeypatch.setattr(sys, "argv", ["quality_report.py", "--junit", str(path), "--json"])
    assert report_module.main() == 1
    output = capsys.readouterr().out
    report = json.loads(output[output.index("{"):])
    assert report["overall_status"] == "FAIL"
