# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R721 — Minuta sem federar.

Hermético: clones e relatório sintéticos em tmp.
"""
import json
import os


def _base(tmp_path, prontas=True):
    base = tmp_path / "int"
    base.mkdir(exist_ok=True)
    clones = tmp_path / "clones" / "pgmpy__pgmpy"
    clones.mkdir(parents=True)
    (clones / "README.md").write_text("# Pgmpy\nToolkit causal.\nLinha3\n", encoding="utf-8")
    (base / "relatorio_autonomo.json").write_text(json.dumps({
        "itens": [{"url": "https://github.com/pgmpy/pgmpy", "classe": "ativo",
                   "pronto_para_analise_R621": prontas,
                   "inventario": {"marcos": {}}}]}), encoding="utf-8")
    return str(base), str(tmp_path / "clones"), str(tmp_path / "out")


def test_minuta_schema_e_hash(tmp_path):
    from integrations import polymath_minuta as mi
    base, clones, out = _base(tmp_path)
    r = mi.emitir(base, clones, out, {},
                  {"https://github.com/pgmpy/pgmpy": {"tipo": ["causal"], "uso": "DAG"}})
    assert r["ok"] is True and r["total"] == 1
    payload = json.loads(open(os.path.join(out, "minuta_r621.json"), encoding="utf-8").read())
    assert payload["spec_id"] == "SPEC-935-R721"
    m = payload["minutas"][0]
    assert m["ecosystem"] == "polymath" and len(m["content_sha256"]) == 64
    assert m["source_path"].endswith("README.md")


def test_fallback_sem_readme(tmp_path):
    from integrations import polymath_minuta as mi
    base, clones, out = _base(tmp_path)
    os.remove(os.path.join(clones, "pgmpy__pgmpy", "README.md"))
    r = mi.emitir(base, clones, out, {},
                  {"https://github.com/pgmpy/pgmpy": {"tipo": ["causal"], "uso": "Uso fallback R711"}})
    payload = json.loads(open(os.path.join(out, "minuta_r621.json"), encoding="utf-8").read())
    assert "fallback" in payload["minutas"][0]["description"].lower() or "uso fallback" in payload["minutas"][0]["description"]


def test_sem_rede_subprocesso_harness():
    import integrations.polymath_minuta as mod
    src = open(mod.__file__, encoding="utf-8").read()
    for proibido in ("urlopen(", "import subprocess", "os.system(", "Popen(", "harness_federation"):
        assert proibido not in src
