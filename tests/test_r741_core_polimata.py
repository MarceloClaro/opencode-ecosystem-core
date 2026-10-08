# -*- coding: utf-8 -*-
"""Testes da SPEC-935-R741 — Registro MCP + persistência polímata.

Hermético: lê opencode.json e workbench/polymath do repo.
"""
import hashlib
import json
import os


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def test_mcp_registrado():
    cfg = json.load(open("opencode.json", encoding="utf-8"))
    mcp = cfg["mcp"]["polymath-labs-mcp"]
    assert mcp["type"] == "local" and mcp["enabled"] is True
    assert mcp["command"] == [".venv/bin/python", "integrations/polymath_labs_mcp.py"]
    assert os.path.isfile("integrations/polymath_labs_mcp.py")


def test_indice_conferivel_sem_segredo():
    indice = json.load(open("workbench/polymath/INDICE.json", encoding="utf-8"))
    assert indice["spec_id"] == "SPEC-935-R741"
    for ent in indice["artefatos"]:
        p = os.path.join("workbench/polymath", ent["arquivo"])
        assert os.path.isfile(p)
        assert _sha(p) == ent["sha256"]
    blob = json.dumps(indice, ensure_ascii=False).lower()
    assert "bearer" not in blob and "github_token" not in blob
