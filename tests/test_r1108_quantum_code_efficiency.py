#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da camada de eficiência de código quântico (R1108)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1108-quantum-code-efficiency.md"
SKILL = RAIZ / ".opencode" / "skills" / "eficiencia-codigo-quantico" / "SKILL.md"
AGENTE = RAIZ / "agents" / "catalog" / "quantum-code-efficiency.md"
AUDITOR = RAIZ / "agents" / "catalog" / "quantum-benchmark-audit.md"
DOC = RAIZ / "docs" / "EFICIENCIA_CODIGO_QUANTICO_R1108.md"
RUNNER = RAIZ / "harnesses" / "quantum-code-efficiency" / "runner.py"


def _frontmatter(texto: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", texto, flags=re.S)
    assert m, "frontmatter ausente"
    return m.group(1)


def test_arquivos_existem():
    for caminho in (SPEC, SKILL, AGENTE, AUDITOR, DOC, RUNNER):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_agentes_managed_v1():
    for caminho, agent_id in (
        (AGENTE, "quantum-code-efficiency"),
        (AUDITOR, "quantum-benchmark-audit"),
    ):
        fm = _frontmatter(caminho.read_text(encoding="utf-8"))
        for termo in (
            f"agent_id: {agent_id}",
            "lifecycle: managed-v1",
            "type: specialist",
            "language: pt-BR",
            "parent: marceloclaro",
            "spec_file: specs/SPEC-935-R1108-quantum-code-efficiency.md",
            "test_file: tests/test_r1108_quantum_code_efficiency.py",
            "external_validation: false",
        ):
            assert termo in fm, f"{caminho.name}: {termo}"


def test_skill_conteudo():
    texto = SKILL.read_text(encoding="utf-8")
    for termo in (
        "TVD",
        "1e-9",
        "num_2q",
        "depth",
        "hardware",
        "speedup",
        "transpilação",
        "Limites",
    ):
        assert termo.lower() in texto.lower(), termo


def test_documento_resultado_e_limites():
    texto = DOC.read_text(encoding="utf-8")
    for termo in (
        "7",
        "31,3%",
        "25,6%",
        "TVD",
        "hardware",
        "Limites",
    ):
        assert termo.lower() in texto.lower(), termo


def test_harness_quick():
    pytest.importorskip("qiskit")
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(
            [sys.executable, str(RUNNER), "--quick", "--out", tmp],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=RAIZ,
        )
        assert r.returncode == 0, r.stderr[-2000:]
        dados = json.loads((Path(tmp) / "resultados.json").read_text(encoding="utf-8"))
        assert dados["resumo"]["benchmarks"] == 7
        assert dados["resumo"]["fail"] == 0
        for b in dados["benchmarks"]:
            assert b["status"] == "pass", b["benchmark"]
            assert b["tvd"] <= 1e-9, b["benchmark"]
            assert b["hardware"] is False
            assert b["network"] is False


def test_experimentos_benchmarks():
    pytest.importorskip("qiskit")
    from quantum_efficiency.experiment_benchmarks import benchmarks_experimentos

    itens = benchmarks_experimentos()
    assert len(itens) == 25
    assert len({x["experiment"] for x in itens}) == 18
    assert {"E01", "E07", "E10"} <= {x["experiment"] for x in itens}


def test_sweep_bell():
    pytest.importorskip("qiskit")
    from quantum_efficiency.benchmarks import bell
    from quantum_efficiency.sweep import varrer_circuito

    r = varrer_circuito(
        bell(), "bell", "E05", "Bell", niveis=(0, 3), ruidos=(0.0,), shots=256
    )
    assert r["melhor"]["status"] == "pass"
    assert r["melhor"]["tvd"] <= 1e-9
    assert r["hardware"] is False
    assert r["network"] is False
    assert all(n["status"] == "pass" for n in r["niveis"])


def test_runner_experiments_quick(tmp_path: Path):
    pytest.importorskip("qiskit")
    r = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--mode",
            "experiments",
            "--quick",
            "--only",
            "E01",
            "E05",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=RAIZ,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    dados = json.loads(
        (tmp_path / "resultados_experimentos.json").read_text(encoding="utf-8")
    )
    assert dados["resumo"]["circuitos"] == 2
    assert dados["resumo"]["fail"] == 0
    for c in dados["circuitos"]:
        assert c["hardware"] is False
        assert c["network"] is False
    relatorio = (tmp_path / "RELATORIO_EXPERIMENTOS.md").read_text(encoding="utf-8")
    assert "p = 0" in relatorio
    assert "ruído de amostragem" in relatorio


def test_registro_no_opencode():
    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    for agent_id in ("quantum-code-efficiency", "quantum-benchmark-audit"):
        assert agent_id in cfg["agent"]
        assert cfg["agent"][agent_id]["prompt"] == (
            f"{{file:./agents/catalog/{agent_id}.md}}"
        )


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*[\"'][A-Za-z0-9_-]{16,}[\"']"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, SKILL, AGENTE, AUDITOR, DOC):
        texto = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(texto), f"segredo em {caminho}"


def test_sem_overclaim():
    proibidos = (
        "speedup garantido",
        "vantagem quântica comprovada",
        "hardware executado",
        "fidelidade de estado medida",
        "benchmark definitivo",
    )
    for caminho in (SKILL, AGENTE, AUDITOR, DOC):
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in texto, f"overclaim em {caminho}: {termo}"
