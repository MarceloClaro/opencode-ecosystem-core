#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da suíte de reprodução E01–E18 + E19."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
REPRO = RAIZ / "experimentos_reproduzidos"


def _json_estrito(caminho: Path) -> dict:
    def rejeita(constante: str):
        raise ValueError(f"constante JSON não permitida: {constante}")

    return json.loads(caminho.read_text(encoding="utf-8"), parse_constant=rejeita)


def test_spec_e_arquivos():
    for nome in ("SPEC.md", "MINDQUANTUM.md", "reproduzir.py", "e19_mermin.py"):
        assert (REPRO / nome).exists(), nome


def test_reproduz_amostra_rapida(tmp_path: Path):
    r = subprocess.run(
        [
            sys.executable,
            str(REPRO / "reproduzir.py"),
            "--quick",
            "--only",
            "E01",
            "E07",
            "E10",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    resumo = _json_estrito(tmp_path / "RESUMO.json")
    assert set(resumo["experimentos"]) == {"E01", "E07", "E10"}
    for exp in resumo["experimentos"].values():
        assert exp["reproduzido"]["leitura_agregada"]
        assert exp["protocolo"]["total_shots"] == 2 * 1024
        assert exp["reproduzido"]["tvd_media"] >= 0.0


def test_e19_rapido(tmp_path: Path):
    r = subprocess.run(
        [
            sys.executable,
            str(REPRO / "e19_mermin.py"),
            "--quick",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    dados = _json_estrito(tmp_path / "E19.json")
    assert dados["medido"]["M"] > 3.9
    assert dados["medido"]["p_valor_M_maior_que_2"] <= 1e-12
    assert dados["medido"]["significancia_sigma"] is None
    por_p = {r["p"]: r for r in dados["ruido"]}
    assert por_p[0.05]["M"] < por_p[0.0]["M"]
    assert por_p[0.01]["M"] < por_p[0.0]["M"]


def test_sem_constantes_nao_json():
    for caminho in (REPRO / "resultados").glob("*.json"):
        _json_estrito(caminho)


def test_mindquantum_nao_declarado_executado():
    texto = (REPRO / "MINDQUANTUM.md").read_text(encoding="utf-8")
    assert "nenhum código MindQuantum foi executado" in texto
    assert "Python 3.14" in texto
    assert "MindSpore" in texto


def test_relatorio_nao_alega_hardware():
    texto = (REPRO / "RELATORIO.md").read_text(encoding="utf-8")
    assert "AerSimulator" in texto
    assert "Nenhum job foi enviado ao GJQ/Tiangong" in texto
    assert "não é replicação experimental" in texto


def test_resultados_completos_se_existirem():
    resumo_path = REPRO / "resultados" / "RESUMO.json"
    if not resumo_path.exists():
        pytest.skip("resultados completos ainda não gerados")
    resumo = _json_estrito(resumo_path)
    assert len(resumo["experimentos"]) == 18
    for exp_id, exp in resumo["experimentos"].items():
        assert exp_id.startswith("E")
        assert exp["reproduzido"]["leitura_agregada"]
        assert exp["reproduzido"]["tvd_media"] >= 0.0
        assert len(exp["reproduzido"]["dist_media"]) == len(
            exp["reproduzido"]["counts_agregados"]
        )


def test_e19_completo_se_existir():
    caminho = REPRO / "resultados" / "E19.json"
    if not caminho.exists():
        pytest.skip("E19 completo ainda não gerado")
    dados = _json_estrito(caminho)
    assert dados["medido"]["M"] > 3.9
    assert len(dados["medido"]["por_setting"]) == 4
    assert len(dados["ruido"]) == 4
