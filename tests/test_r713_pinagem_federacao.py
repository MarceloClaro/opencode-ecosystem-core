# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R713 — Pinagem viva e federação.

Hermético: fetcher falso determinístico; sem rede/subprocesso/LLM reais.
"""
import datetime
import json
import os

import pytest


def _iso(dias_atras=5):
    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=dias_atras)
    return dt.isoformat()


def _fetcher_falso(mapa, chamadas=None):
    def _f(org, repo):
        if chamadas is not None:
            chamadas.append(f"{org}/{repo}")
        chave = f"{org.lower()}/{repo.lower()}"
        if chave not in mapa:
            raise ConnectionError(f"lab fora do ar: {chave}")
        return dict(mapa[chave])
    return _f


def test_pinar_federavel_fresco():
    from integrations import polymath_pinagem as pin
    f = _fetcher_falso({"pgmpy/pgmpy": {
        "commit": "a" * 40, "pushed_at": _iso(5), "license": "MIT", "license_ok": True, "archived": False}})
    r = pin.pinar_lab("https://github.com/pgmpy/pgmpy", f)
    assert r["federavel"] is True
    assert r["commit"] == "a" * 40
    assert len(r["sha256_registro"]) == 64
    assert r["motivo"] == "" or "dentro" in r["motivo"].lower() or r["motivo"] == "ok"


def test_pinar_bloqueios():
    from integrations import polymath_pinagem as pin
    velho = _fetcher_falso({"pgmpy/pgmpy": {
        "commit": "b" * 40, "pushed_at": _iso(120), "license": "MIT", "license_ok": True, "archived": False}})
    r1 = pin.pinar_lab("https://github.com/pgmpy/pgmpy", velho)
    assert r1["federavel"] is False and "90" in r1["motivo"]
    sem_lic = _fetcher_falso({"pgmpy/pgmpy": {
        "commit": "c" * 40, "pushed_at": _iso(5), "license": None, "license_ok": False, "archived": False}})
    r2 = pin.pinar_lab("https://github.com/pgmpy/pgmpy", sem_lic)
    assert r2["federavel"] is False and "licen" in r2["motivo"].lower()
    arq = _fetcher_falso({"pgmpy/pgmpy": {
        "commit": "d" * 40, "pushed_at": _iso(5), "license": "MIT", "license_ok": True, "archived": True}})
    r3 = pin.pinar_lab("https://github.com/pgmpy/pgmpy", arq)
    assert r3["federavel"] is False and "arquiv" in r3["motivo"].lower()


def test_fora_allowlist_sem_rede():
    from integrations import polymath_pinagem as pin
    chamadas = []
    f = _fetcher_falso({}, chamadas)
    with pytest.raises(ValueError):
        pin.pinar_lab("https://github.com/evil/hack", f)
    assert chamadas == []


def test_revalidar_tolera_falha_isolada():
    from integrations import polymath_pinagem as pin
    mapa = {
        "pgmpy/pgmpy": {"commit": "a" * 40, "pushed_at": _iso(5), "license": "MIT", "license_ok": True, "archived": False},
        "sympy/sympy": {"commit": "e" * 40, "pushed_at": _iso(200), "license": "BSD", "license_ok": True, "archived": False},
    }
    def f(org, repo):
        chave = f"{org.lower()}/{repo.lower()}"
        if chave in mapa:
            return dict(mapa[chave])
        raise ConnectionError("fora do ar")
    r = pin.revalidar_todos(f, dias=90)
    assert r["total"] >= 16
    assert r["federaveis"] >= 1
    assert r["bloqueados"] >= 1
    assert r["janela_dias"] == 90
    por_url = {e["url"].lower(): e for e in r["pins"]}
    assert por_url["https://github.com/pgmpy/pgmpy"]["federavel"] is True
    assert por_url["https://github.com/sympy/sympy"]["federavel"] is False


def test_emitir_pins_schema_tmp(tmp_path):
    from integrations import polymath_pinagem as pin
    f = _fetcher_falso({"pgmpy/pgmpy": {
        "commit": "a" * 40, "pushed_at": _iso(5), "license": "MIT", "license_ok": True, "archived": False}})
    res = pin.revalidar_todos(f, dias=90)
    out = pin.emitir_pins(str(tmp_path), res)
    assert out["ok"] is True
    for nome in ("labs_pins.json", "federacao_gate.json"):
        p = tmp_path / nome
        assert p.exists()
        payload = json.loads(p.read_text(encoding="utf-8"))
        assert payload["spec_id"] == "SPEC-935-R713"
        assert payload["gerador"] == "marceloclaro"
    gate = json.loads((tmp_path / "federacao_gate.json").read_text(encoding="utf-8"))
    assert gate["janela_dias"] == 90
    blob = json.dumps(gate, ensure_ascii=False).lower()
    for termo in ("verificado", "qualis a1", "superhumano", "aprovado"):
        assert termo not in blob


def test_sem_rede_real_no_modulo():
    import integrations.polymath_pinagem as mod
    src = open(mod.__file__, encoding="utf-8").read()
    for proibido in ("import requests", "urlopen(", "Popen(", "os.system("):
        assert proibido not in src
