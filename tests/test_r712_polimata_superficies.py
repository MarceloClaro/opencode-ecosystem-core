# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R712 — Superfícies do pesquisador polímata.

Hermético: sem rede/subprocesso/LLM; fixtures em tmp.
"""
import json
import os
import re

import pytest


def test_mcp_schemas_e_fail_closed():
    from integrations import polymath_labs_mcp as mcp
    for ferramenta in ("listar_labs", "validar_lab", "manifesto_labs", "auditar_clones", "rotulo_polimata"):
        assert ferramenta in mcp.TOOL_SCHEMAS
        assert ferramenta in mcp.TOOL_DESCRIPTIONS
        assert mcp.TOOL_SCHEMAS[ferramenta]["type"] == "object"
    # Funcional sem rede
    labs = mcp._tool_listar_labs()
    assert labs["ok"] is True and labs["total"] >= 16
    ok = mcp._tool_validar_lab("https://github.com/pgmpy/pgmpy")
    assert ok["ok"] is True and ok["id"] == "pgmpy"
    ruim = mcp._tool_validar_lab("https://github.com/evil/hack")
    assert ruim["ok"] is False
    vazio = mcp._tool_validar_lab(" ")
    assert vazio["ok"] is False


def test_mcp_manifesto_e_auditoria_em_tmp(tmp_path):
    from integrations import polymath_labs_mcp as mcp
    dest = str(tmp_path / "manif")
    r = mcp._tool_manifesto_labs(dest)
    assert r["ok"] is True
    assert os.path.isfile(os.path.join(dest, "labs_manifest.json"))
    # diretório vazio fail-closed
    assert mcp._tool_manifesto_labs(" ")["ok"] is False
    base = str(tmp_path / "clones")
    os.makedirs(base, exist_ok=True)
    sim = os.path.join(base, "pgmpy__pgmpy")
    os.makedirs(os.path.join(sim, ".git"), exist_ok=True)
    with open(os.path.join(sim, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("# sim\n")
    with open(os.path.join(sim, ".git", "HEAD"), "w", encoding="utf-8") as fh:
        fh.write("ref: refs/heads/main\n")
    rel = mcp._tool_auditar_clones(base)
    assert rel["ok"] is True and rel["total"] >= 16
    rot = mcp._tool_rotulo_polimata()
    assert rot["rotulo"] == "candidato_a_inspecao"
    assert rot["exige_validacao_externa"] is True
    blob = json.dumps({**rot, **rel}, ensure_ascii=False).lower()
    for termo in ("verificado", "qualis a1", "superhumano", "aprovado"):
        assert termo not in blob


def _ler(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_agentes_frontmatter_e_guarda_causal():
    base = "agents/catalog"
    arquivos = {
        "46_agente_pesquisador_polimata.md": "pesquisador-polimata",
        "47_agente_laboratorio_reproduzivel.md": "laboratorio-reproduzivel",
        "48_agente_auditoria_reprodutibilidade.md": "auditoria-reprodutibilidade",
    }
    for arq, slug in arquivos.items():
        texto = _ler(os.path.join(base, arq))
        assert texto.startswith("---")
        front = texto.split("---", 2)[1]
        for campo in ("name:", "description:", "skills:", "tags:", "examples:"):
            assert campo in front, f"{arq} sem {campo}"
        corpo = texto.split("---", 2)[2]
        assert "R711" in corpo and "R712" in corpo
        assert "sem desenho" in corpo.lower() or "sem alegar" in corpo.lower() or "f<10" in corpo.lower()


def test_skill_tabela_bloqueadores_e_sem_promessa():
    from pathlib import Path
    p = Path(".opencode/skills/pesquisador-polimata-labs/SKILL.md")
    assert p.exists(), "SKILL.md ausente"
    texto = p.read_text(encoding="utf-8")
    assert "name: pesquisador-polimata-labs" in texto
    for tipo in ("dedutivo", "abdutivo", "causal", "bayesiano", "contrafactual", "sintese", "auditoria"):
        assert tipo in texto.lower(), f"tipo {tipo} ausente na skill"
    for ferramenta in ("listar_labs", "validar_lab", "manifesto_labs", "auditar_clones"):
        assert ferramenta in texto
    assert "46" in texto and "48" in texto
    baixo = texto.lower()
    assert "garante aceite" not in baixo and "qualis a1 garantido" not in baixo
    assert "f<10" in baixo and "prior" in baixo


def test_hooks_deny_allow_sem_rede():
    from hooks.polymath_labs_guards import guard_clone_url, guard_claim, guard_third_party_exec
    from hooks.engine import HookMatcher, run_hooks
    # clone
    assert guard_clone_url("https://github.com/pgmpy/pgmpy")["allow"] is True
    assert guard_clone_url("https://github.com/evil/hack")["allow"] is False
    assert guard_clone_url("git@github.com:pgmpy/pgmpy.git")["allow"] is False
    # claim
    assert guard_claim("O tratamento causa cura definitiva.")["allow"] is False
    assert guard_claim("Efeito associado ao tratamento; limitação: amostra de conveniência.")["allow"] is True
    # third-party exec
    assert guard_third_party_exec("pip install evil")["allow"] is False
    assert guard_third_party_exec("ls -la")["allow"] is True
    # integração via engine: primeiro deny vence
    m = HookMatcher("polymath_*", hooks=[lambda t, a: guard_clone_url(a.get("url", ""))])
    r = run_hooks("PreToolUse", "polymath_clone", {"url": "https://github.com/evil/hack"}, [m])
    assert r["allow"] is False


def test_scanner_cobertura_licenca_reprodutibilidade():
    from scanners.polymath_labs_scanner import PolymathLabsScanner
    s = PolymathLabsScanner()
    pronta = {
        "tipos_cobertos": ["dedutivo", "indutivo", "abdutivo", "causal", "bayesiano", "contrafactual", "sintese"],
        "licencas": ["ok"] * 7,
        "tem_manifesto": True, "tem_head": True, "tem_hash": True,
    }
    r1 = s.varrer(pronta)
    assert r1["status"] == "pronto"
    assert r1["cobertura_tipos"]["cobertos"] >= 7
    parcial = dict(pronta, tipos_cobertos=["dedutivo", "causal"], licencas=["ok", "ok"])
    r2 = s.varrer(parcial)
    assert r2["status"] == "parcial"
    bloqueada = dict(pronta, licencas=["ok", "license_undeclared"], tem_hash=False)
    r3 = s.varrer(bloqueada)
    assert r3["status"] == "bloqueado"
    assert any("licen" in x.lower() for x in r3["riscos"])
    assert "recomendacoes" in r3 and "candidato_a_inspecao" in json.dumps(r3, ensure_ascii=False)
