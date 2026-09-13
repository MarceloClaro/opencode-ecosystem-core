# -*- coding: utf-8 -*-
"""Testes do core-check (R481) — validação estrutural do ecossistema.

Hermético: sem rede, sem LLM, sem credenciais. Verifica que o subcomando
``python3 -m marceloclaro.cli core-check`` (e sua função ``run_core_check``)
audita doctor, specs, evolution registry, fontes padrão, anti-overclaim e
hermericidade dos módulos da série R471.
"""

from __future__ import annotations

from marceloclaro.core_check import run_core_check


def _result() -> dict:
    return run_core_check(verbose=False)


def test_core_check_happy_path_structure():
    r = _result()
    assert r["overall"] in {"healthy", "degraded"}
    assert r["checks_failed"] == 0, [c for c in r["checks"] if c["status"] == "fail"]
    assert r["checks_total"] >= 6
    assert r["checks_passed"] >= r["checks_total"] - 2  # warns tolerados


def test_core_check_includes_doctor_and_registry():
    r = _result()
    ids = {c["id"] for c in r["checks"]}
    assert {"doctor", "specs_loading", "evolution_registry"} <= ids


def test_core_check_default_sources_unchanged():
    r = _result()
    c = next(c for c in r["checks"] if c["id"] == "default_sources")
    assert c["status"] == "pass"
    assert "openalex" in c["detail"]
    assert "scihubeva" not in c["detail"].lower()


def test_core_check_anti_overclaim_docs():
    r = _result()
    c = next(c for c in r["checks"] if c["id"] == "anti_overclaim_docs")
    assert c["status"] in {"pass", "warn"}
    assert "não constitui certificação externa" in c.get("detail", "") or c["status"] == "pass"


def test_core_check_modules_hermetic():
    r = _result()
    c = next(c for c in r["checks"] if c["id"] == "modules_hermetic")
    assert c["status"] == "pass"
    assert "sem imports de rede" in c["detail"]


def test_core_check_no_claims_in_output():
    """O próprio JSON do core-check não contém alegações vedadas."""
    import json
    r = _result()
    rendered = json.dumps(r, ensure_ascii=False).lower()
    for word in ("superhuman", "qualis a1", "superação"):
        assert word not in rendered


def test_core_check_cli_subcommand_exits_zero():
    import subprocess
    import sys
    proc = subprocess.run(
        [sys.executable, "-m", "marceloclaro.cli", "core-check"],
        capture_output=True, text=True, cwd=None, timeout=60,
    )
    assert proc.returncode == 0
    assert '"overall"' in proc.stdout
    # O output JSON não pode ser "healthy" com falhas
    assert '"checks_failed": 0' in proc.stdout