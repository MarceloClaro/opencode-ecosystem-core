#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do scorecard híbrido de resiliência quântica (R1116)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1116-quantum-resilience-scorecard.md"
DOC = RAIZ / "docs" / "RESILIENCIA_QUANTICA_HIBRIDA_R1116.md"
MODULE = RAIZ / "quantum_mitigation" / "resilience.py"
RUNNER = RAIZ / "harnesses" / "quantum-error-mitigation" / "runner.py"
AGENTE = RAIZ / "agents" / "catalog" / "quantum-error-mitigation.md"
ZNE = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "hardware_zne_tomography" / "zne.json"
TOMO_Q0 = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "hardware_zne_tomography" / "tomography.json"
TOMO_Q1 = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "hardware_tomography_q1" / "comparison.json"
READOUT = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "resultados" / "baihua" / "E05_comparacao" / "comparacao.json"


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    assert match, f"frontmatter ausente: {path}"
    return yaml.safe_load(match.group(1))


def test_arquivos_existem():
    for caminho in (SPEC, DOC, MODULE, RUNNER, ZNE, TOMO_Q0, TOMO_Q1, READOUT):
        assert caminho.exists(), caminho


def _real_inputs():
    zne = json.loads(ZNE.read_text(encoding="utf-8"))
    q0_payload = json.loads(TOMO_Q0.read_text(encoding="utf-8"))
    q1_payload = json.loads(TOMO_Q1.read_text(encoding="utf-8"))
    return {
        "readout": json.loads(READOUT.read_text(encoding="utf-8")),
        "zne": zne,
        "tomography_q0": q0_payload.get("fit", q0_payload),
        "tomography_q1": q1_payload["q1"]["fit_combined"],
        "uncertainty": q1_payload["q1"]["bootstrap_combined"],
        "pec": {"gamma_total": 1.006, "samples_required": 10120.78},
        "surface": {"planned": True},
        "pulse_dd": {"planned": True},
    }


def test_scorecard_real():
    from quantum_mitigation import resilience_scorecard

    payload = resilience_scorecard(**_real_inputs())
    assert payload["status"] == "partial"
    blocked = {item["technique"] for item in payload["blocked"]}
    assert "ZNE" in blocked
    assert "QEC de superfície" in blocked
    assert "DD pulse-level" in blocked
    actions = " ".join(item["action"] for item in payload["recommendations"])
    assert "q1" in actions
    assert "state preparation" in actions
    assert "layout" in actions
    assert payload["readout"]["winner"] == "baseline"
    assert payload["tomography"]["q1"]["min_prep_fidelity"] < payload["tomography"]["q0"]["min_prep_fidelity"]


def test_scorecard_flags():
    from quantum_mitigation import resilience_scorecard

    payload = resilience_scorecard(
        tomography_q0={"prep_fidelity": {"0": 0.99, "1": 0.98}, "readout_p1_given_prep0": 0.01, "readout_p0_given_prep1": 0.02},
        tomography_q1={"prep_fidelity": {"0": 0.99, "1": 0.90}, "readout_p1_given_prep0": 0.01, "readout_p0_given_prep1": 0.08},
        uncertainty={"prep_fidelity": {"1": {"low": 0.88, "high": 0.92}}, "readout": {"r1": {"low": 0.07, "high": 0.09}}},
    )
    actions = " ".join(item["action"] for item in payload["recommendations"])
    assert "state preparation" in actions
    assert "leitura em q1" in actions
    assert "repetições" in actions


def test_harness_resilience(tmp_path: Path):
    pec = tmp_path / "pec.json"
    pec.write_text(json.dumps({"gamma_total": 1.006, "samples_required": 10120.78}), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable, str(RUNNER), "resilience",
            "--readout", str(READOUT),
            "--zne", str(ZNE),
            "--tomography-q0", str(TOMO_Q0),
            "--tomography-q1", str(TOMO_Q1),
            "--pec", str(pec),
            "--surface", "--pulse-dd",
            "--out", str(tmp_path / "res"),
        ],
        cwd=RAIZ, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    payload = json.loads((tmp_path / "res" / "resultado.json").read_text(encoding="utf-8"))
    assert payload["status"] == "partial"
    assert (tmp_path / "res" / "RELATORIO.md").exists()


def test_agente_resilience():
    meta = _frontmatter(AGENTE)
    bash = meta["permission"]["bash"]
    key = (
        ".venv-quantum/bin/python harnesses/quantum-error-mitigation/"
        "agent_qem.py resilience*"
    )
    assert bash[key] == "allow"
    from agents.lifecycle import validate_managed_card

    assert validate_managed_card(RAIZ, AGENTE, AGENTE.read_bytes())["definition_validated"] is True
    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    assert cfg["agent"]["quantum-error-mitigation"]["permission"]["bash"][key] == "allow"


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, DOC, MODULE, RUNNER):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"


def test_sem_overclaim():
    proibidos = (
        "fidelidade medida com sucesso",
        "vantagem quântica comprovada",
        "speedup garantido",
        "prova experimental de emaranhamento",
        "benchmark definitivo",
        "scorecard certifica",
    )
    for caminho in (SPEC, DOC):
        text = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in text, f"overclaim em {caminho}: {termo}"
