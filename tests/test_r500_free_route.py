# -*- coding: utf-8 -*-
"""Testes do roteamento free automático (R500) — curadoria do benchmark R499."""

from __future__ import annotations

import pytest

from integrations.free_model_catalog import (
    BEST_FREE_BY_TASK,
    best_free_model,
    list_free_models,
)
from integrations.model_router import model_router


class TestCatalog:
    def test_catalog_tem_5_free_curados(self):
        models = list_free_models()
        assert len(models) == 5
        ids = {m["model_id"] for m in models}
        assert "opencode/mimo-v2.5-free" in ids
        assert "opencode/big-pickle" in ids
        assert "opencode/muse-spark-1.3-contributor-free" in ids

    def test_best_free_por_tarefa(self):
        assert best_free_model("academic") == "opencode/mimo-v2.5-free"
        assert best_free_model("math") == "opencode/mimo-v2.5-free"
        # muse spark com acurácia 0 NUNCA antes dos corretos
        order = BEST_FREE_BY_TASK["academic"]
        assert "opencode/muse-spark-1.3-contributor-free" in order[-2:]

    def test_best_free_fallback_disponiveis(self):
        assert best_free_model("academic", available=["opencode/big-pickle"]) == (
            "opencode/big-pickle")


class TestRouter:
    def test_list_all_models_inclui_big_pickle(self):
        models = model_router.list_all_models()
        ids = [m.get("model_id", m.get("id")) for m in models]
        assert "opencode/big-pickle" in ids
        assert "opencode/mimo-v2.5-free" in ids

    def test_route_academic_prefer_free(self):
        r = model_router.route("academic", prefer_free=True)
        assert r.model_id == "opencode/mimo-v2.5-free"
        assert "R499" in r.reason or "curadoria" in r.reason

    def test_route_sem_prefer_free_inalterado(self):
        r = model_router.route("coding")
        # comportamento anterior preservado: não força o catálogo free
        assert r.model_id != "opencode/mimo-v2.5-free" or "prefer_free" not in r.reason

    def test_route_reasoning_prefer_free_usa_curadoria(self):
        r = model_router.route("reasoning", prefer_free=True)
        assert r.model_id == "opencode/mimo-v2.5-free"
        assert r.alternatives  # fallbacks listados