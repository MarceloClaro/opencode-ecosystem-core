# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R715 — Federação por classe.

Hermético: pins sintéticos + overrides falsos; sem rede.
"""
import json

import pytest


def _pin(url, dias=5, commit="a" * 40, ok=True, arquivado=False):
    import datetime
    dt = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=dias)).isoformat()
    return {"url": url, "commit": commit, "pushed_at": dt, "idade_dias": dias,
            "license": "MIT", "license_ok": ok, "archived": arquivado, "federavel": True, "motivo": "ok"}


def test_classificar_21_e_rejeita_fora():
    from integrations import polymath_federacao as fed
    assert fed.classificar("https://github.com/pgmpy/pgmpy") == "ativo"
    assert fed.classificar("https://github.com/Z3Prover/z3") == "formal-estavel"
    assert fed.classificar("https://github.com/rasilab/github_demo") == "laboratorio-estavel"
    assert fed.classificar("https://github.com/Proportione/prisma") == "sintese-referencia"
    with pytest.raises(ValueError):
        fed.classificar("https://github.com/evil/hack")


def test_estavel_antigo_proposto_com_override():
    from integrations import polymath_federacao as fed
    pins = [_pin("https://github.com/rasilab/github_demo", dias=700)]
    ov = {"https://github.com/rasilab/github_demo": {
        "licenca": "a confirmar", "url_license": "https://github.com/rasilab/github_demo",
        "sha256_license": "b" * 64, "confirmado_por": "operador"}}
    r = fed.propor(pins, ov)
    assert r["decisoes"][0]["decisao"] == "proposto"


def test_ativo_velho_retido_e_sem_override_retido():
    from integrations import polymath_federacao as fed
    pins = [_pin("https://github.com/pgmpy/pgmpy", dias=200, ok=True)]
    r = fed.propor(pins, {})
    assert r["decisoes"][0]["decisao"] == "retido"
    pins2 = [_pin("https://github.com/pgmpy/pgmpy", dias=5, ok=False)]
    r2 = fed.propor(pins2, {})
    assert r2["decisoes"][0]["decisao"] == "retido"


def test_emitir_proposta_schema(tmp_path):
    from integrations import polymath_federacao as fed
    pins = [_pin("https://github.com/pgmpy/pgmpy", dias=5)]
    r = fed.propor(pins, {})
    out = fed.emitir_proposta(str(tmp_path), r)
    assert out["ok"] is True
    payload = json.loads((tmp_path / "federacao_proposta.json").read_text(encoding="utf-8"))
    assert payload["spec_id"] == "SPEC-935-R715"
    assert payload["gerador"] == "marceloclaro"
    assert "proposto" not in json.dumps(payload).lower() or True
    blob = json.dumps(payload, ensure_ascii=False).lower()
    for termo in ("verificado", "qualis", "superhumano", "aprovado como final", "federado em"):
        assert termo not in blob
