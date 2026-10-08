# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R711 — Pesquisador polímata GitHub.

Suíte hermética: sem rede/subprocesso/LLM; fixtures sintéticas em tmp.
"""
import json
import os

import pytest

from integrations.github_polymath_labs import (
    ALLOWLIST,
    gerar_manifesto,
    listar_labs,
    rotulo_epistemico,
    validar_url,
    verificar_clones,
)


def test_allowlist_fechada_e_schema():
    labs = listar_labs()
    assert len(labs) >= 16
    urls = [l["url"] for l in labs]
    # Nenhuma duplicata (normalizada em minúsculas)
    assert len(set(u.lower() for u in urls)) == len(urls)
    for lab in labs:
        for chave in ("id", "url", "tipo_raciocinio", "uso_polimata", "licenca", "status_licenca"):
            assert chave in lab, f"ausente {chave} em {lab.get('id')}"
        assert lab["url"].startswith("https://github.com/")
        assert isinstance(lab["tipo_raciocinio"], list) and len(lab["tipo_raciocinio"]) >= 1
        assert lab["status_licenca"] in ("ok", "license_undeclared")
    # Mutação do retorno não contamina o registro interno
    labs[0]["url"] = "https://github.com/evil/hack"
    assert ALLOWLIST[0]["url"] != "https://github.com/evil/hack"


def test_validar_url_fail_closed():
    ok = validar_url("https://github.com/pgmpy/pgmpy")
    assert ok == "https://github.com/pgmpy/pgmpy"
    # Normaliza .git e case
    assert validar_url("https://github.com/PGMPY/pgmpy.git") == "https://github.com/pgmpy/pgmpy"
    with pytest.raises(ValueError):
        validar_url("http://github.com/pgmpy/pgmpy")
    with pytest.raises(ValueError):
        validar_url("git@github.com:pgmpy/pgmpy.git")
    with pytest.raises(ValueError):
        validar_url("https://github.com/evil/hack")
    with pytest.raises(ValueError):
        validar_url("https://gitlab.com/pgmpy/pgmpy")
    with pytest.raises(ValueError):
        validar_url(" ")
    with pytest.raises(ValueError):
        validar_url("https://github.com/somente-org")


def test_gerar_manifesto_schema_em_tmp(tmp_path):
    r = gerar_manifesto(str(tmp_path))
    alvo = tmp_path / "labs_manifest.json"
    assert alvo.exists()
    payload = json.loads(alvo.read_text(encoding="utf-8"))
    assert payload["spec_id"] == "SPEC-935-R711"
    assert payload["gerador"] == "marceloclaro"
    assert payload["total"] == len(ALLOWLIST)
    assert len(payload["entradas"]) == len(ALLOWLIST)
    for ent in payload["entradas"]:
        assert ent["url"].startswith("https://github.com/")
        assert len(ent["sha256_url"]) == 64
        assert "tipo_raciocinio" in ent and "uso_polimata" in ent
    assert r["ok"] is True and r["manifesto"] == str(alvo)


def test_verificar_clones_fixtures_sinteticas(tmp_path):
    # Cria 1 clone simulado: org__repo com README + .git/HEAD lido como arquivo
    base = tmp_path / "clones"
    base.mkdir()
    sim = base / "pgmpy__pgmpy"
    sim.mkdir()
    (sim / "README.md").write_text("# pgmpy simulado\n", encoding="utf-8")
    gitdir = sim / ".git"
    gitdir.mkdir()
    (gitdir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    rel = verificar_clones(str(base))
    assert rel["total"] == len(ALLOWLIST)
    por_id = {e["id"]: e for e in rel["entradas"]}
    assert por_id["pgmpy"]["existe"] is True
    assert por_id["pgmpy"]["HEAD"] == "ref: refs/heads/main"
    assert len(por_id["pgmpy"]["sha256_readme_ou_gitignore"]) == 64
    # Ausente nunca é erro fatal
    assert por_id["z3"]["existe"] is False
    assert "audit_trail" in rel and rel["gerador"] == "marceloclaro"


def test_rotulo_epistemico_nunca_aprova():
    r = rotulo_epistemico()
    assert r["rotulo"] == "candidato_a_inspecao"
    assert r["exige_validacao_externa"] is True
    proibidos = ("verificado", "qualis", "superhumano", "aprovado", "provado", "cura", "eficaz")
    blob = json.dumps(r, ensure_ascii=False).lower()
    for termo in proibidos:
        assert termo not in blob


def test_modulo_nao_executa_rede_nem_subprocesso():
    import integrations.github_polymath_labs as mod
    src = open(mod.__file__, encoding="utf-8").read()
    for proibido in ("import subprocess", "import socket", "import requests", "from urllib", "os.system", "os.popen", "Popen"):
        assert proibido not in src
