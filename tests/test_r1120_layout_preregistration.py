#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do pré-registro de layout (R1120)."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1120-layout-preregistration.md"
SCRIPT = RAIZ / "harnesses" / "quantum-error-mitigation" / "preregister_layout.py"
RESULT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "preregistration_layout.json"
REPORT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "RELATORIO_PREREGISTRO.md"


def _load() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_arquivos_existem():
    for caminho in (SPEC, SCRIPT, RESULT, REPORT):
        assert caminho.exists(), caminho


def test_hash_reproduzivel():
    payload = _load()
    stored = payload.pop("hash")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == stored


def test_n_calculado_pelo_preregister_ci():
    from quantum_mitigation import preregister_ci

    payload = _load()
    for half_width, item in payload["n_options"].items():
        expected = preregister_ci(
            p=payload["planning"]["p"],
            half_width=float(half_width),
            confidence=payload["planning"]["confidence"],
        )
        assert item["n_per_circuit"] == expected["n"]
    assert payload["chosen"]["n_per_circuit"] == payload["n_options"]["0.005"]["n_per_circuit"]


def test_gates_e_decisao():
    payload = _load()
    gates = payload["gates"]
    assert set(gates) == {
        "coherence_prep_ge_0.99",
        "r1_le_0.05",
        "layout_effect_ge_0.01",
        "drift_resolved",
    }
    assert gates["coherence_prep_ge_0.99"]["pass"] is False
    assert gates["r1_le_0.05"]["pass"] is False
    assert gates["layout_effect_ge_0.01"]["pass"] is False
    assert gates["drift_resolved"]["pass"] is False
    assert payload["decision"]["compare_layouts_now"] is False
    reasons = " ".join(payload["decision"]["reasons"])
    for termo in ("prep coerente", "r1", "layout", "drift"):
        assert termo in reasons
    assert payload["budget"]["jobs"] == 12
    assert payload["budget"]["shots_per_job"] == payload["chosen"]["n_per_circuit"]
    assert payload["hardware_executed"] is False


def test_relatorio_declara_decisao():
    text = REPORT.read_text(encoding="utf-8")
    assert "Comparar layouts agora: **False**" in text
    assert "38,411" in text
    assert "Não comparar layouts se qualquer gate falhar" in text


def test_script_reproduz(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert RESULT.exists()
    assert REPORT.exists()


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
        "benchmark definitivo",
    )
    for caminho in (SPEC, SCRIPT):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
