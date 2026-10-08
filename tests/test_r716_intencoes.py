# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R716 — Intenções sem auto-federar.

Hermético: proposta sintética em tmp; sem rede.
"""
import json

import pytest


def _proposta_falsa():
    return {
        "spec_id": "SPEC-935-R715", "gerador": "marceloclaro",
        "total": 3, "propostos": 2, "retidos": 1,
        "decisoes": [
            {"url": "https://github.com/pgmpy/pgmpy", "classe": "ativo", "decisao": "proposto", "motivo": "ok", "licenca": "MIT"},
            {"url": "https://github.com/sympy/sympy", "classe": "formal-estavel", "decisao": "proposto", "motivo": "ok", "licenca": "BSD"},
            {"url": "https://github.com/evil/hack", "classe": None, "decisao": "retido", "motivo": "fora"},
        ],
    }


def test_importar_so_propostos(tmp_path):
    from integrations import polymath_intencoes as inten
    prop = tmp_path / "federacao_proposta.json"
    prop.write_text(json.dumps(_proposta_falsa()), encoding="utf-8")
    out = inten.importar(str(prop), str(tmp_path / "int"))
    assert out["ok"] is True and out["intencoes"] == 2 and out["retidas_informativas"] == 1
    inv = json.loads((tmp_path / "int" / "intencoes.json").read_text(encoding="utf-8"))
    assert len(inv["intencoes"]) == 2
    assert all(i["status"] == "aguardando_humano" for i in inv["intencoes"])
    assert all(i["intencao_id"].startswith("INT-") for i in inv["intencoes"])


def test_decidir_exige_humano(tmp_path):
    from integrations import polymath_intencoes as inten
    prop = tmp_path / "federacao_proposta.json"
    prop.write_text(json.dumps(_proposta_falsa()), encoding="utf-8")
    inten.importar(str(prop), str(tmp_path / "int"))
    base = str(tmp_path / "int")
    with pytest.raises(ValueError):
        inten.decidir(base, "https://github.com/pgmpy/pgmpy", "aprovada", humano=False, motivo="ok", responsavel="op")
    with pytest.raises(ValueError):
        inten.decidir(base, "https://github.com/pgmpy/pgmpy", "talvez", humano=True, motivo="ok", responsavel="op")
    with pytest.raises(ValueError):
        inten.decidir(base, "https://github.com/evil/hack", "aprovada", humano=True, motivo="ok", responsavel="op")
    r = inten.decidir(base, "https://github.com/pgmpy/pgmpy", "aprovada", humano=True, motivo="revisado", responsavel="marcelo")
    assert r["status"] == "aprovada" and r["pronta_para_federacao"] is False
    assert r["exige_artefato_local"] is True


def test_resumo_e_sem_auto_federacao(tmp_path):
    from integrations import polymath_intencoes as inten
    prop = tmp_path / "federacao_proposta.json"
    prop.write_text(json.dumps(_proposta_falsa()), encoding="utf-8")
    inten.importar(str(prop), str(tmp_path / "int"))
    base = str(tmp_path / "int")
    inten.decidir(base, "https://github.com/sympy/sympy", "rejeitada", humano=True, motivo="fora de escopo", responsavel="marcelo")
    s = inten.resumo(base)
    assert s["total"] == 2 and s["rejeitadas"] == 1 and s["aguardando"] == 1
    src = open(inten.__file__, encoding="utf-8").read()
    for proibido in ("harness_federation", "os.system", "Popen(", "import requests"):
        assert proibido not in src
    blob = json.dumps(s, ensure_ascii=False).lower()
    for termo in ("federado", "verificado", "qualis"):
        assert termo not in blob
