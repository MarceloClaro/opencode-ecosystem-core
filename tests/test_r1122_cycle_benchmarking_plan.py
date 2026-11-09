#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do plano de cycle benchmarking (R1122)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1122-cycle-benchmarking-plan.md"
SCRIPT = RAIZ / "harnesses" / "quantum-error-mitigation" / "cycle_benchmarking_plan.py"
RESULT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "cycle_benchmarking_plan.json"
REPORT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "RELATORIO_CYCLE_BENCHMARKING_PLAN.md"


def _load() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_arquivos_existem():
    for caminho in (SPEC, SCRIPT, RESULT, REPORT):
        assert caminho.exists(), caminho


def test_plano_15_paulis():
    payload = _load()
    assert len(payload["paulis"]) == 15
    assert len(set(payload["paulis"])) == 15
    assert "II" not in payload["paulis"]
    assert payload["depths"] == [1, 2, 4, 8, 16]
    assert payload["sets"] == 2
    assert payload["jobs"] == 15 * 5 * 2 == 150
    assert payload["processes"] == 8
    assert payload["process_limit"] == 20
    assert payload["shots"] == 4096
    assert payload["total_shots"] == 150 * 4096


def test_nao_mede_taxas_nem_hardware():
    payload = _load()
    assert payload["rates_measured"] is False
    assert payload["hardware_executed"] is False
    text = REPORT.read_text(encoding="utf-8")
    assert "Nenhuma taxa foi medida" in text
    assert "O plano não executa hardware" in text


def test_script_reproduz():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    payload = _load()
    assert payload["jobs"] == 150


def test_sem_segredo_ou_overclaim():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    proibidos = (
        "taxas medidas",
        "vantagem quântica comprovada",
        "speedup garantido",
        "benchmark definitivo",
    )
    for caminho in (SPEC, SCRIPT):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
