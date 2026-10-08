# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R722 — Parecer sem decidir.

Hermético: clones sintéticos em tmp.
"""
import json
import os


def _clone(tmp_path, readme="# T\nDoc longa de teste com mais de duzentos caracteres. " * 5, com_tests=True):
    c = tmp_path / "c"
    c.mkdir(exist_ok=True)
    (c / "README.md").write_text(readme, encoding="utf-8")
    (c / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (c / "pyproject.toml").write_text("[x]\n", encoding="utf-8")
    if com_tests:
        t = c / "tests"
        t.mkdir(exist_ok=True)
        (t / "t.py").write_text("x\n", encoding="utf-8")
    return str(c)


def test_maduro_ratificar_com_ressalvas(tmp_path):
    from integrations import polymath_parecer as pa
    c = _clone(tmp_path)
    r = pa.parecer("https://github.com/pgmpy/pgmpy", c, "MIT", ["causal"])
    assert r["maturidade"] >= 7
    assert r["recomendacao_tecnica"] == "ratificar_com_ressalvas"
    assert r["ratificacao_titular_pendente"] is True


def test_minimo_aguardar(tmp_path):
    from integrations import polymath_parecer as pa
    c = tmp_path / "vazio"
    c.mkdir(exist_ok=True)
    r = pa.parecer("https://github.com/x/y", str(c), "", [])
    assert r["recomendacao_tecnica"] == "aguardar_evidencia"
    assert r["maturidade"] <= 3


def test_emitir_schema(tmp_path):
    from integrations import polymath_parecer as pa
    c = _clone(tmp_path)
    out = pa.emitir_pareceres(
        [{"url": "https://github.com/pgmpy/pgmpy", "licenca": "MIT", "capacidades": ["causal"]}],
        { "https://github.com/pgmpy/pgmpy": c }, str(tmp_path / "out"))
    assert out["ok"] is True
    payload = json.loads(open(os.path.join(str(tmp_path / "out"), "pareceres.json"), encoding="utf-8").read())
    assert payload["spec_id"] == "SPEC-935-R722"
    blob = json.dumps(payload, ensure_ascii=False).lower()
    for termo in ("\"aprovada\"", "federado", "verificado"):
        assert termo not in blob
    src = open(pa.__file__, encoding="utf-8").read()
    for proibido in ("urlopen(", "import subprocess", "os.system(", "Popen(", "harness_federation"):
        assert proibido not in src
