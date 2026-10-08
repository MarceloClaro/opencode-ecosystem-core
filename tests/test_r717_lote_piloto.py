# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R717 — Lote piloto atômico.

Hermético: intenções sintéticas em tmp.
"""
import json

import pytest


def _base(tmp_path):
    from integrations import polymath_intencoes as inten
    prop = tmp_path / "federacao_proposta.json"
    prop.write_text(json.dumps({
        "spec_id": "SPEC-935-R715", "total": 3,
        "decisoes": [
            {"url": "https://github.com/pgmpy/pgmpy", "classe": "ativo", "decisao": "proposto", "motivo": "ok"},
            {"url": "https://github.com/sympy/sympy", "classe": "formal-estavel", "decisao": "proposto", "motivo": "ok"},
            {"url": "https://github.com/proportione/prisma", "classe": "sintese-referencia", "decisao": "proposto", "motivo": "ok"},
        ]}), encoding="utf-8")
    inten.importar(str(prop), str(tmp_path / "int"))
    return str(tmp_path / "int")


def test_lote_2_mais_1(tmp_path):
    from integrations import polymath_lote as lote
    base = _base(tmp_path)
    out = lote.decidir_lote(base, [
        {"url": "https://github.com/pgmpy/pgmpy", "decisao": "aprovada", "motivo": "núcleo causal"},
        {"url": "https://github.com/sympy/sympy", "decisao": "aprovada", "motivo": "formal auditado"},
        {"url": "https://github.com/proportione/prisma", "decisao": "rejeitada", "motivo": "fora do piloto"},
    ], humano=True, responsavel="piloto")
    assert out["ok"] is True and out["aplicadas"] == 3
    assert (tmp_path / "int" / "lote_piloto.json").exists()


def test_falha_aborta_restante(tmp_path):
    from integrations import polymath_lote as lote
    from integrations import polymath_intencoes as inten
    base = _base(tmp_path)
    with pytest.raises(ValueError):
        lote.decidir_lote(base, [
            {"url": "https://github.com/pgmpy/pgmpy", "decisao": "aprovada", "motivo": "ok"},
            {"url": "https://github.com/evil/hack", "decisao": "aprovada", "motivo": "ok"},
            {"url": "https://github.com/sympy/sympy", "decisao": "aprovada", "motivo": "ok"},
        ], humano=True, responsavel="piloto")
    s = inten.resumo(base)
    assert s["aprovadas"] == 1 and s["aguardando"] == 2


def test_sem_humano_recusa(tmp_path):
    from integrations import polymath_lote as lote
    base = _base(tmp_path)
    with pytest.raises(ValueError):
        lote.decidir_lote(base, [{"url": "https://github.com/pgmpy/pgmpy", "decisao": "aprovada", "motivo": "ok"}],
                          humano=False, responsavel="piloto")
