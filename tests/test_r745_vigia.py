# -*- coding: utf-8 -*-
"""Testes da SPEC-935-R745 — Vigia com datas fixas, sem rede."""
import datetime
import json
import os


def _agora():
    return datetime.datetime(2026, 10, 7, tzinfo=datetime.timezone.utc)


def test_estados():
    from integrations import polymath_vigia as vg
    base = _agora()
    iso = lambda d: (base - datetime.timedelta(days=d)).isoformat()
    pins = [{"url": "a", "pushed_at": iso(80)}, {"url": "b", "pushed_at": iso(85)},
            {"url": "c", "pushed_at": iso(95)}, {"url": "d", "pushed_at": ""}]
    r = vg.verificar(pins, {"a": 90, "b": 90, "c": 90}, agora=base)
    por = {i["url"]: i["estado"] for i in r["itens"]}
    assert por == {"a": "ok", "b": "aviso_7d", "c": "vencido", "d": "sem_dados"}
    assert (r["ok"], r["avisos"], r["vencidos"], r["sem_dados"]) == (1, 1, 1, 1)


def test_relatorio_schema(tmp_path):
    from integrations import polymath_vigia as vg
    r = vg.verificar([{"url": "a", "pushed_at": _agora().isoformat()}], {"a": 90}, agora=_agora())
    out = vg.emitir_relatorio(str(tmp_path), r)
    assert out["ok"] is True
    payload = json.loads(open(os.path.join(str(tmp_path), "vigia.json"), encoding="utf-8").read())
    assert payload["spec_id"] == "SPEC-935-R745"
    src = open(vg.__file__, encoding="utf-8").read()
    for proibido in ("urlopen(", "import subprocess", "os.system("):
        assert proibido not in src
