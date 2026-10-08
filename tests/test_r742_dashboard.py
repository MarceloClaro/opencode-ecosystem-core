# -*- coding: utf-8 -*-
"""Testes da SPEC-935-R742 — Painel sincronizado com os JSONs.

Hermético: lê workbench do repo.
"""
import json
import re


def test_painel_sincronizado():
    txt = open("workbench/polymath/DASHBOARD.md", encoding="utf-8").read()
    nodos = json.load(open("workbench/rede_polimata/nodos.json", encoding="utf-8"))
    fed = json.load(open("workbench/rede_polimata/federados.json", encoding="utf-8"))
    assert f"Nodos: {nodos['total']}" in txt and f"Federados: {fed['total']}" in txt
    linhas = re.findall(r"^\| (polymath:[^ ]+) \|", txt, re.M)
    assert len(linhas) == fed["total"] == 16
    assert len(set(linhas)) == 16
    for x in fed["federados"]:
        assert x["agent_id"] in txt
    assert "Commit: pendente" in txt
