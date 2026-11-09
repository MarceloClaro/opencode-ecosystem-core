#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da engenharia de loop GJQ (R1112)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1112-gjq-loop-engineering.md"
DOC = RAIZ / "docs" / "GJQ_LOOP_ENGINEERING_R1112.md"
LOOP = RAIZ / "gjq_hardware_opt" / "loop.py"
SIM = RAIZ / "gjq_hardware_opt" / "simulation.py"
RUNNER = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "loop_runner.py"
AGENTE = RAIZ / "agents" / "catalog" / "gjq-readout-mitigation.md"
WRAPPER = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "agent_readout.py"
PERFIL = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05"
    / "perfil.json"
)
COMPARACAO = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05_comparacao"
    / "comparacao.json"
)


def _run(*args: str, timeout: int = 600):
    return subprocess.run(
        [sys.executable, *args],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _temp_test(tmp_path: Path) -> Path:
    path = tmp_path / "test_loop_temp.py"
    path.write_text(
        "# Teste temporário do gate TDD do loop.\n"
        "# Não executa hardware, não acessa rede e não importa o runner.\n"
        "# O objetivo é apenas validar que o gate TDD chama pytest e recebe 0.\n"
        "\n"
        "def test_gate_tdd_ok():\n"
        "    assert True\n"
        "\n"
        "# Preenchimento para o gate SDD exigir conteúdo mínimo.\n"
        "# " + "x" * 220 + "\n",
        encoding="utf-8",
    )
    return path


def test_arquivos_existem():
    for caminho in (SPEC, DOC, LOOP, SIM, RUNNER, AGENTE, WRAPPER):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_sdd_gate_real():
    from gjq_hardware_opt.loop import run_sdd_gate

    result = run_sdd_gate(
        [str(SPEC), str(RAIZ / "specs" / "SPEC-935-R1110-gjq-readout-mitigation.md")],
        [str(Path(__file__)), str(RAIZ / "tests" / "test_r1110_gjq_readout_mitigation.py")],
    )
    assert result["ok"] is True
    assert result["failures"] == []


def test_tdd_gate_temp(tmp_path: Path):
    from gjq_hardware_opt.loop import run_tdd_gate

    test = _temp_test(tmp_path)
    result = run_tdd_gate([str(test)], timeout=120)
    assert result["ok"] is True
    assert result["returncode"] == 0


def test_plan_offline(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    result = _run(
        str(RUNNER),
        "plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "512",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    state = json.loads((tmp_path / "loop_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "planned"
    assert state["submissions_estimated"] == 6
    assert (tmp_path / "plan" / "plano_comparacao.json").exists()
    assert not (tmp_path / "comparacao" / "comparacao.json").exists()


def test_simulate_com_tdd_temp(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    plan_result = _run(
        str(RUNNER),
        "plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "512",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert plan_result.returncode == 0, plan_result.stderr[-2000:]
    test = _temp_test(tmp_path)
    result = _run(
        str(RUNNER),
        "simulate",
        "--state",
        str(tmp_path / "loop_state.json"),
        "--tdd-test",
        str(test),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    state = json.loads((tmp_path / "loop_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "simulated"
    assert state["gates"]["sdd"] is True
    assert state["gates"]["tdd"] is True
    assert state["gates"]["simulation"] is True
    sim = json.loads((tmp_path / "simulacao.json").read_text(encoding="utf-8"))
    assert sim["simulation"]["gate_ok"] is True
    assert sim["simulation"]["ideal_equivalence_tvd"] <= 1e-9
    assert not (tmp_path / "comparacao" / "comparacao.json").exists()


def test_run_sem_confirmacao_para_na_simulacao(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    test = _temp_test(tmp_path)
    result = _run(
        str(RUNNER),
        "run",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "512",
        "--quick",
        "--tdd-test",
        str(test),
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    state = json.loads((tmp_path / "loop_state.json").read_text(encoding="utf-8"))
    assert state["status"] == "simulated"
    assert state["gates"]["hardware"] is False
    assert not (tmp_path / "comparacao" / "comparacao.json").exists()
    assert "hardware" in result.stdout.lower()


def test_execute_bloqueado_sem_gates(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    plan_result = _run(
        str(RUNNER),
        "plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "512",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert plan_result.returncode == 0, plan_result.stderr[-2000:]
    result = _run(
        str(RUNNER),
        "execute",
        "--state",
        str(tmp_path / "loop_state.json"),
        "--confirm",
        "--allow-hardware",
        timeout=120,
    )
    assert result.returncode == 2
    assert "gates" in result.stdout.lower() or "bloqueado" in result.stdout.lower()
    assert not (tmp_path / "comparacao" / "comparacao.json").exists()


def test_score_comparacao_real(tmp_path: Path):
    if not COMPARACAO.exists():
        pytest.skip("comparação real ausente")
    state = {
        "schema_version": 1,
        "loop_id": "teste-loop",
        "backend": "Baihua",
        "profile_file": None,
        "circuit": "E05",
        "shots": 4096,
        "max_iterations": 1,
        "iteration": 1,
        "status": "executed",
        "gates": {"sdd": True, "tdd": True, "simulation": True, "hardware": True},
        "paths": {
            "out_dir": str(tmp_path),
            "plan_dir": str(tmp_path / "plan"),
            "plan": str(tmp_path / "plan" / "plano_comparacao.json"),
            "simulation": str(tmp_path / "simulacao.json"),
            "comparison": str(COMPARACAO),
            "report": str(tmp_path / "RELATORIO_LOOP.md"),
        },
        "history": [],
        "best": None,
        "lessons": [],
        "submissions_estimated": 6,
        "submissions_used": 6,
        "created_at": "2026-11-09T00:00:00-03:00",
        "updated_at": "2026-11-09T00:00:00-03:00",
    }
    state_path = tmp_path / "loop_state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    result = _run(
        str(RUNNER),
        "score",
        "--state",
        str(state_path),
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    updated = json.loads(state_path.read_text(encoding="utf-8"))
    assert updated["status"] == "scored"
    assert updated["history"]
    assert updated["lessons"]
    report = (tmp_path / "RELATORIO_LOOP.md").read_text(encoding="utf-8")
    assert "Score e reflexão" in report
    assert "não confirmou" in report or "Proxy confirmado: **False**" in report


def test_agente_tem_loop():
    meta = yaml.safe_load(
        re.match(
            r"^---\n(.*?)\n---\n",
            AGENTE.read_text(encoding="utf-8"),
            flags=re.S,
        ).group(1)
    )
    bash = meta["permission"]["bash"]
    for command in (
        "loop-plan*",
        "loop-simulate*",
        "loop-execute*",
        "loop-score*",
        "loop-run*",
        "loop-status*",
        "loop-report*",
    ):
        assert any(
            key.endswith("agent_readout.py " + command) for key in bash
        ), command
    assert not any("runner.py run" in key for key in bash)
    assert not any("runner.py compare" in key for key in bash)


def test_wrapper_loop_plan(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    result = _run(
        str(WRAPPER),
        "loop-plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "256",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert (tmp_path / "plan" / "plano_comparacao.json").exists()
    assert (tmp_path / "loop_state.json").exists()


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, DOC, LOOP, SIM, RUNNER):
        texto = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(texto), f"segredo em {caminho}"


def test_sem_overclaim():
    proibidos = (
        "fidelidade medida com sucesso",
        "vantagem quântica comprovada",
        "speedup garantido",
        "prova experimental de emaranhamento",
        "benchmark definitivo",
        "simulação comprova hardware",
    )
    for caminho in (SPEC, DOC):
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in texto, f"overclaim em {caminho}: {termo}"
