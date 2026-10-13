"""R809: regressões de auditoria estrutural, sem rede ou agentes externos."""

import json
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("source", [
    "import urllib.request\n",
    "import urllib.request as fetch\n",
    "from urllib.request import urlopen\n",
    "from urllib import request\n",
    "from urllib import request as fetch\n",
    "import subprocess as process\n",
    "from socket import socket\n",
])
def test_gate_rejects_network_and_process_imports(tmp_path, monkeypatch, source):
    from marceloclaro import core_check

    (tmp_path / "candidate.py").write_text(source, encoding="utf-8")
    monkeypatch.setattr(core_check, "ROOT", tmp_path)
    monkeypatch.setattr(core_check, "HERMETIC_MODULES", ("candidate.py",))

    findings = core_check._check_hermetic_modules()

    assert len(findings) == 1
    assert findings[0].startswith("candidate.py:")


@pytest.mark.parametrize("source", [
    "import urllib.parse\n",
    "from urllib.parse import urlparse\n",
    "from urllib import parse\n",
    "import pathlib\n",
])
def test_gate_preserves_permitted_imports(tmp_path, monkeypatch, source):
    from marceloclaro import core_check

    (tmp_path / "candidate.py").write_text(source, encoding="utf-8")
    monkeypatch.setattr(core_check, "ROOT", tmp_path)
    monkeypatch.setattr(core_check, "HERMETIC_MODULES", ("candidate.py",))

    assert core_check._check_hermetic_modules() == []


@pytest.mark.parametrize("identifier", [
    {}, {"id": None}, {"id": ""}, {"id": " \t "},
    {"id": 7}, {"id": True}, {"id": ["a"]}, {"id": {"a": 1}},
])
def test_diagnostic_rejects_missing_or_invalid_id(tmp_path, identifier):
    from scanners.diagnostic_pipeline import DiagnosticPipeline

    check = {"tipo": "nomes", "arquivo": str(tmp_path / "absent.txt"),
             "regex": r"(\w+)", **identifier}

    with pytest.raises(ValueError, match="ID|id"):
        DiagnosticPipeline().varrer({"conjuntos": [check]})


@pytest.mark.parametrize("identifiers", [("a", "a"), ("a", " a ")])
def test_duplicate_ids_are_rejected_before_reading_artifacts(monkeypatch, identifiers):
    from scanners import diagnostic_pipeline

    reads = []
    monkeypatch.setattr(diagnostic_pipeline, "_ler", lambda path: reads.append(path) or "")
    checks = [{"tipo": "nomes", "id": identifier,
               "arquivo": f"artifact-{index}.txt", "regex": r"(\w+)"}
              for index, identifier in enumerate(identifiers)]

    with pytest.raises(ValueError, match="duplicado|repetido"):
        diagnostic_pipeline.DiagnosticPipeline().varrer({"conjuntos": checks})
    assert reads == []


def test_distinct_failed_checks_are_counted_independently(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline

    checks = [{"tipo": "nomes", "id": identifier,
               "arquivo": str(tmp_path / f"absent-{index}.txt"), "regex": r"(\w+)"}
              for index, identifier in enumerate((" primeiro ", "segundo"))]

    result = DiagnosticPipeline().varrer({"conjuntos": checks})

    assert (result["total_checks"], result["falharam"], result["passaram"]) == (2, 2, 0)
    assert [gap["id"] for gap in result["gaps"]] == ["primeiro", "segundo"]


def test_spec_r809_is_registered():
    from sdd.spec_engine import spec_registry

    assert spec_registry.get("SPEC-935-R809") is not None


@pytest.mark.parametrize("imports", [
    "import scanners\nimport scanners.diagnostic_pipeline\n",
    "import scanners.diagnostic_pipeline\nimport scanners\n",
])
def test_gap_module_keeps_legacy_scanner_run_in_both_import_orders(imports):
    code = (imports + "from scanners import diagnostic_pipeline\n"
            "import json\n"
            "report = diagnostic_pipeline.run('Texto para diagnóstico.', domain='general')\n"
            "print(json.dumps({'domain': report['domain'], "
            "'noological': 'noological' in report, 'teleological': 'teleological' in report}))\n")

    result = subprocess.run([sys.executable, "-c", code],
                            cwd=Path(__file__).resolve().parent.parent,
                            capture_output=True, text=True, timeout=30)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"domain": "general", "noological": True,
                                       "teleological": True}
