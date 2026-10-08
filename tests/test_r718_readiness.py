# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R718 — Readiness sem federar.

Hermético: intenções, pins e clones sintéticos em tmp.
"""
import json
import os


def _intencoes(tmp_path, status="aprovada"):
    base = tmp_path / "int"
    base.mkdir(exist_ok=True)
    (base / "intencoes.json").write_text(json.dumps({
        "intencoes": [{"intencao_id": "INT-ABCD", "url": "https://github.com/pgmpy/pgmpy",
                       "classe": "ativo", "status": status}],
        "retidas_informativas": []}), encoding="utf-8")
    return str(base)


def _pins(ok=True, com_pin=True):
    if not com_pin:
        return []
    return [{"url": "https://github.com/pgmpy/pgmpy", "commit": "a" * 40,
             "federavel": ok, "motivo": "ok" if ok else "velho",
             "license": "MIT", "license_ok": True, "archived": False}]


def test_pronta_completa(tmp_path):
    from integrations import polymath_readiness as rd
    d = _intencoes(tmp_path)
    clones = tmp_path / "clones" / "pgmpy__pgmpy" / ".git"
    clones.mkdir(parents=True)
    (clones / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    r = rd.avaliar(d, _pins(True), str(tmp_path / "clones"))
    assert r["avaliadas"][0]["pronto_para_R621"] is True


def test_pendencias_sem_clone_e_sem_pin(tmp_path):
    from integrations import polymath_readiness as rd
    d = _intencoes(tmp_path)
    r1 = rd.avaliar(d, _pins(True), str(tmp_path / "vazio"))
    assert r1["avaliadas"][0]["pronto_para_R621"] is False
    assert any("clone" in p for p in r1["avaliadas"][0]["pendencias"])
    r2 = rd.avaliar(d, _pins(False, com_pin=False), str(tmp_path / "vazio"))
    assert any("pin" in p for p in r2["avaliadas"][0]["pendencias"])


def test_aguardando_nao_avaliada_e_schema(tmp_path):
    from integrations import polymath_readiness as rd
    d = _intencoes(tmp_path, status="aguardando_humano")
    r = rd.avaliar(d, _pins(True), str(tmp_path))
    assert r["avaliadas"][0]["avaliado"] is False
    out = rd.emitir(d, r)
    assert out["ok"] is True
    payload = json.loads(open(os.path.join(d, "readiness.json"), encoding="utf-8").read())
    assert payload["spec_id"] == "SPEC-935-R718"
    src = open(rd.__file__, encoding="utf-8").read()
    for proibido in ("harness_federation", "urlopen(", "Popen(", "os.system("):
        assert proibido not in src
