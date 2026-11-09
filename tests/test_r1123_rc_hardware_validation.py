#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da validação RC em hardware (R1123)."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1123-rc-hardware-validation.md"
MODULE = RAIZ / "quantum_mitigation" / "rc_validation.py"
SCRIPT = RAIZ / "harnesses" / "quantum-error-mitigation" / "hardware_rc_validation.py"


def _script_module():
    spec = importlib.util.spec_from_file_location("rc_hw", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_arquivos_existem():
    for caminho in (SPEC, MODULE, SCRIPT):
        assert caminho.exists(), caminho


def test_distribuicao_ideal():
    from quantum_mitigation import base_circuit, ideal_probabilities

    ideal = ideal_probabilities(base_circuit())
    assert set(ideal) == {"00", "01", "10", "11"}
    assert sum(ideal.values()) == pytest.approx(1.0)
    assert ideal["00"] == pytest.approx(0.5, abs=1e-9)
    assert ideal["11"] == pytest.approx(0.5, abs=1e-9)
    assert ideal["01"] == pytest.approx(0.0, abs=1e-9)
    assert ideal["10"] == pytest.approx(0.0, abs=1e-9)


def test_tvd():
    from quantum_mitigation import tvd

    ideal = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}
    assert tvd({"00": 4800, "11": 4800}, ideal) == pytest.approx(0.0)
    assert tvd({"00": 9600}, ideal) == pytest.approx(0.5)
    assert tvd({"00": 7200, "11": 2400}, ideal) == pytest.approx(0.25)


def test_plano_4_mais_4():
    from quantum_mitigation import rc_validation_plan, verify_equivalence

    plan = rc_validation_plan((101, 102, 103, 104))
    assert len(plan["baseline"]) == 4
    assert len(plan["twirled"]) == 4
    assert plan["seeds"] == [101, 102, 103, 104]
    assert all(item["n_twirls"] == 4 for item in plan["twirls"])
    for circuit in plan["twirled"]:
        assert verify_equivalence(plan["baseline"][0], circuit)["equivalent_up_to_phase"] is True
    assert plan["ideal"]["00"] == pytest.approx(0.5, abs=1e-9)


def test_bootstrap_e_decisao():
    from quantum_mitigation import bootstrap_tvd_difference, decision

    ideal = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}
    counts = [{"00": 4800, "01": 0, "10": 0, "11": 4800} for _ in range(4)]
    summary = bootstrap_tvd_difference(
        counts, counts, ideal, n_bootstrap=200, seed=7
    )
    assert abs(summary["mean_difference"]) < 0.01
    assert summary["low"] <= 0 <= summary["high"]
    assert decision(summary)["verdict"] == "sem efeito detectável"
    assert decision({"mean_difference": -0.1, "low": -0.2, "high": -0.01})["verdict"] == "twirled melhor"
    assert decision({"mean_difference": 0.1, "low": 0.01, "high": 0.2})["verdict"] == "twirled pior"


def test_script_bloqueado():
    module = _script_module()
    assert module.main(["--set", "1"]) == 2
    assert module.main(["--set", "1", "--confirm"]) == 2


def test_analise_sintetica(tmp_path: Path):
    module = _script_module()
    ideal = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}
    good = {"00": 4800, "01": 0, "10": 0, "11": 4800}
    bad = {"00": 4300, "01": 200, "10": 300, "11": 4800}
    for index in (1, 2):
        payload = {
            "shots": 9600,
            "ideal": ideal,
            "counts": {
                "baseline": [good for _ in range(4)],
                "twirled": [bad for _ in range(4)],
            },
        }
        (tmp_path / f"set{index}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
    assert module.analyze(str(tmp_path)) == 0
    result = json.loads((tmp_path / "rc_validation.json").read_text(encoding="utf-8"))
    assert result["summary"]["mean_difference"] > 0
    assert result["decision"]["verdict"] in {"twirled pior", "sem efeito detectável"}
    assert (tmp_path / "RELATORIO_RC.md").exists()


def test_sem_segredo_ou_overclaim():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    proibidos = (
        "rc comprovado",
        "redução de erro comprovada",
        "vantagem quântica comprovada",
        "speedup garantido",
    )
    for caminho in (SPEC, MODULE, SCRIPT):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
