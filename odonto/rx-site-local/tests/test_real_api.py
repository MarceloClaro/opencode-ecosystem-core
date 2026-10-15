# -*- coding: utf-8 -*-
"""Testes da API real dos laboratórios locais (SPEC-935-R900 FR-013).

Exercitam o backend por import direto (sem servidor), cobrindo: sanidade,
inventário real + SHA do manuscript, amostra, allowlist/traversal fail-closed,
modelos reais, autômato celular (determinismo e regra ajustada), gate de coorte
e um job de treino real curto.

Executar:  python3 -m pytest odonto/rx-site-local/tests/test_real_api.py -q
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SITE))

from backend import api, ca_lab, datasets, labs  # noqa: E402


def get(path: str, query: dict | None = None):
    resp = api.handle_get(path, query or {})
    assert resp is not None, f"rota GET não reconhecida: {path}"
    return resp.status, json.loads(resp.body)


def post(path: str, payload: dict):
    resp = api.handle_post(
        path, {}, json.dumps(payload).encode(), "application/json"
    )
    assert resp is not None, f"rota POST não reconhecida: {path}"
    return resp.status, json.loads(resp.body)


# --------------------------------------------------------------------- health
def test_health_real_e_capacidades():
    status, d = get("/api/health")
    assert status == 200
    assert d["real"] is True and d["mock"] is False
    assert d["capabilities"]["odontoca"] is True
    assert d["datasets"] >= 1
    assert d["ca_states"] == ["H", "C", "F", "M"]
    assert d["claim_levels"]["ca"] == "descritivo_nao_causal"


def test_handle_get_desconhecido_retorna_none():
    # Não é rota /api/*: o servidor deixa o backend simulado (R899) responder.
    assert api.handle_get("/predict/images", {}) is None
    assert api.handle_get("/", {}) is None


# ------------------------------------------------------------------ inventário
def test_inventario_real_contem_table_s1_e_sha_ok():
    status, d = get("/api/datasets")
    assert status == 200 and d["real"] is True
    names = {x["name"] for x in d["datasets"]}
    assert "Table_S1.xlsx" in names
    assert "caries_features.csv" in names
    ts1 = next(x for x in d["datasets"] if x["name"] == "Table_S1.xlsx")
    assert ts1["sha256"] == datasets.SOURCE_SHA256
    assert ts1["sha256_ok"] is True
    assert "Table_S1.xlsx" in d["allowlist"]


def test_amostra_real_de_csv():
    status, d = get("/api/datasets/sample", {"name": ["caries_features.csv"], "n": ["3"]})
    assert status == 200
    assert d["n"] == 3
    assert len(d["columns"]) > 0
    assert len(d["rows"]) == 3


def test_amostra_traversal_e_desconhecido_fail_closed():
    s1, _ = get("/api/datasets/sample", {"name": ["../etc/passwd"]})
    assert s1 == 404
    s2, _ = get("/api/datasets/sample", {"name": ["nao_existe.csv"]})
    assert s2 == 404


def test_amostra_sem_nome_e_400():
    status, d = get("/api/datasets/sample", {})
    assert status == 400
    assert "name" in d["detail"]


# --------------------------------------------------------------------- modelos
def test_modelos_reais_com_metricas():
    status, d = get("/api/models")
    assert status == 200 and d["real"] is True and d["mock"] is False
    assert d["count"] >= 1
    assert d["claim_level"] == "comparacao_empirica"
    lab = d["laboratories"][0]
    assert lab["real"] is True
    assert lab["n_rows"] and lab["n_rows"] > 0
    assert "auroc" in lab["metrics"]


# --------------------------------------------------------- autômato celular
def test_ca_demo_deterministico_e_descritivo():
    s1, d1 = get("/api/ca/demo")
    s2, d2 = get("/api/ca/demo")
    assert s1 == s2 == 200
    assert d1 == d2  # seed fixo → reprodutível
    assert d1["claim_level"] == "descritivo_nao_causal"
    assert d1["rule"] == "prior"
    assert len(d1["history"]) == d1["steps"]
    assert len(d1["final"]) == d1["n_teeth"]
    for item in d1["history"]:
        assert 0.0 <= item["prevalence_caries"] <= 1.0


def test_ca_simulate_post_prior():
    status, d = post("/api/ca/simulate", {"rule": "prior", "steps": 2, "seed": 1, "n_teeth": 16})
    assert status == 200
    assert d["rule"] == "prior" and d["n_teeth"] == 16
    assert d["mock"] is False


def test_ca_regra_fitted_aprendida():
    rule = ca_lab.fitted_rule()  # ajusta/carrega cache
    status, d = post("/api/ca/simulate", {"rule": "fitted", "steps": 2, "seed": 0, "n_teeth": 32})
    assert status == 200
    assert d["rule"] == "fitted"
    assert "Table_S1" in d["evidence"]
    assert rule is not None


# ------------------------------------------------------------------ validação
def test_validation_gate_travado():
    status, d = get("/api/validation")
    assert status == 200 and d["real"] is True
    gate = d["cohort_gate"]
    assert gate["locked_ok"] is True, gate
    assert gate["observed"] == labs.LOCKED_COHORT
    assert gate["sha256_ok"] is True
    assert d["external_validation"]["status"] == "bloqueado"
    assert d["honest_tier"]["not_validated"]
    assert any("RETIRADO" in n or "retirado" in n.lower() for n in d["notes"])


# -------------------------------------------------------------- treino real
def test_job_de_treino_real_curto():
    status, d = post(
        "/api/train",
        {"dataset": "caries_features.csv", "task": "default", "folds": 2,
         "seed": 0, "sample_rows": 200},
    )
    assert status == 202 and d["accepted"] is True
    jid = d["job"]["id"]
    assert d["job"]["mock"] is False

    deadline = time.time() + 180
    final = None
    while time.time() < deadline:
        _, st = get("/api/train/status", {"id": [jid]})
        if st["state"] in {"done", "error"}:
            final = st
            break
        time.sleep(0.5)
    assert final is not None, "job não terminou no prazo"
    assert final["state"] == "done", final.get("error")
    assert final["n_rows"] == 200
    assert final["subsampled"] is True
    assert final["report"]["claim_level"] == "comparacao_empirica"
    assert final["report"]["n_rows"] == 200


def test_job_recusa_dataset_fora_da_allowlist():
    status, d = post("/api/train", {"dataset": "/etc/passwd", "folds": 2})
    assert status == 400
    assert "allowlist" in d["detail"]


# ------------------------------------------------------ integração com serve
def test_serve_declara_paginas_de_laboratorio():
    import serve  # noqa: E402  (mesmo diretório, já em sys.path)

    assert {"review", "validacao", "cadastro", "docs"} <= set(serve.LAB_PAGES)
    for name in ("review", "validacao", "cadastro", "docs"):
        assert (SITE / "pages" / f"{name}.html").is_file(), name


def test_training_progress_shape():
    p = labs.training_progress()
    assert {"completed", "target", "remaining", "percentage"} <= set(p)
    assert p["target"] >= 1
    assert p["real"] is True and p["mock"] is False
