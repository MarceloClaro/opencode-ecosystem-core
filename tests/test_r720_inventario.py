# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R720 — Inventário 100% local.

Hermético: clone sintético em tmp; sem rede/subprocesso.
"""
import json
import os


def _clone(tmp_path):
    c = tmp_path / "pgmpy__pgmpy"
    (c / ".git").mkdir(parents=True)
    (c / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (c / "README.md").write_text("# r\n", encoding="utf-8")
    (c / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (c / "pyproject.toml").write_text("[x]\n", encoding="utf-8")
    t = c / "tests"
    t.mkdir()
    (t / "t1.py").write_text("x=1\n", encoding="utf-8")
    return str(c)


def test_inventariar_marcos_e_limites(tmp_path):
    from integrations import polymath_inventario as inv
    c = _clone(tmp_path)
    r = inv.inventariar(c)
    assert r["total_arquivos"] == 4
    assert r["marcos"]["README.md"]["presente"] is True
    assert len(r["marcos"]["LICENSE"]["sha256"]) == 64
    assert r["head"] == "ref: refs/heads/main"
    assert ".git" not in json.dumps(r)


def test_relatorio_so_prontos(tmp_path):
    from integrations import polymath_inventario as inv
    base = tmp_path / "int"
    base.mkdir()
    (base / "intencoes.json").write_text(json.dumps({
        "intencoes": [
            {"url": "https://github.com/pgmpy/pgmpy", "classe": "ativo", "status": "aprovada"},
            {"url": "https://github.com/sympy/sympy", "classe": "formal-estavel", "status": "aguardando_humano"}],
        "retidas_informativas": []}), encoding="utf-8")
    (base / "readiness.json").write_text(json.dumps({
        "avaliadas": [
            {"url": "https://github.com/pgmpy/pgmpy", "avaliado": True, "pronto_para_R621": True, "pendencias": []},
            {"url": "https://github.com/sympy/sympy", "avaliado": False, "motivo": "aguardando"}]}), encoding="utf-8")
    clones = tmp_path / "clones" / "pgmpy__pgmpy"
    clones.mkdir(parents=True)
    (clones / "README.md").write_text("# r\n", encoding="utf-8")
    out = inv.relatorio(str(base), str(tmp_path / "clones"), str(tmp_path / "out"))
    assert out["ok"] is True and out["prontas"] == 1
    payload = json.loads(open(os.path.join(str(tmp_path / "out"), "relatorio_autonomo.json"), encoding="utf-8").read())
    assert payload["spec_id"] == "SPEC-935-R720"
    # determinismo do conteúdo sem gerado_em
    h1 = inv.sha_conteudo(payload)
    payload["gerado_em"] = "x"
    assert inv.sha_conteudo(payload) == h1
    src = open(inv.__file__, encoding="utf-8").read()
    for proibido in ("urlopen(", "import subprocess", "os.system(", "Popen("):
        assert proibido not in src
