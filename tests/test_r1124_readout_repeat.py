#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da repetição da leitura com mitigação (R1124)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1124-readout-repeat.md"
SCRIPT = RAIZ / "harnesses" / "quantum-error-mitigation" / "readout_repeat_analysis.py"
RESULT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "readout_repeat.json"
REPORT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "RELATORIO_READOUT_REPEAT.md"


def _load() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_arquivos_existem():
    for caminho in (SPEC, SCRIPT, RESULT, REPORT):
        assert caminho.exists(), caminho


def test_tres_runs():
    payload = _load()
    assert payload["summary"]["n_runs"] == 3
    assert set(payload["runs"]) == {"original", "set1", "set2"}
    for name, item in payload["runs"].items():
        assert item["status"] == "ok"
        assert item["baseline_mitigated_tvd"] > 0
        assert item["optimized_mitigated_tvd"] > 0
        assert item["baseline_physical"] == [0, 1]
        assert item["optimized_physical"] == [106, 107]
    assert payload["summary"]["sign_stable"] is False
    assert payload["summary"]["different_physical_qubits"] is True


def test_decisao_nao_comparar():
    payload = _load()
    assert payload["decision"]["compare_layouts_now"] is False
    reasons = " ".join(payload["decision"]["reasons"])
    for termo in ("qubits físicos", "sinal", "prep coerente", "r1", "mitigação"):
        assert termo in reasons
    assert payload["hardware_executed"] is False


def test_relatorio():
    text = REPORT.read_text(encoding="utf-8")
    assert "Comparar layouts agora: **False**" in text
    assert "Otimizado TVD" in text
    assert "106" in text and "107" in text
    assert "mitigação" in text.lower()


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
    assert payload["summary"]["n_runs"] == 3


def test_sem_segredo_ou_overclaim():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    proibidos = (
        "layout superior comprovado",
        "vantagem quântica comprovada",
        "speedup garantido",
        "r1 corrigido por software",
    )
    for caminho in (SPEC, SCRIPT):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
