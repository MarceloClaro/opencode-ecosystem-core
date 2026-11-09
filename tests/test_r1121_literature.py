#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do dossiê de literatura dos gaps (R1121)."""
from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1121-literature-mitigation-gaps.md"
DOC = RAIZ / "docs" / "LITERATURA_MITIGACAO_QUANTICA_R1121.md"
JSON = RAIZ / "docs" / "literatura_mitigacao_r1121.json"

REQUIRED_GAPS = {
    "RC/Pauli-frame",
    "GST",
    "Pauli-Lindblad rates",
    "PEC 2q",
    "ZNE",
    "surface code",
    "readout",
    "SPAM",
}


def _payload() -> dict:
    return json.loads(JSON.read_text(encoding="utf-8"))


def test_arquivos_existem():
    for caminho in (SPEC, DOC, JSON):
        assert caminho.exists(), caminho


def test_referencias_estruturais():
    payload = _payload()
    refs = payload["references"]
    assert len(refs) >= 15
    ids = [ref["id"] for ref in refs]
    assert len(ids) == len(set(ids))
    dois = [ref["doi"] for ref in refs if ref.get("doi")]
    assert len(dois) == len(set(dois))
    for ref in refs:
        assert ref["title"].strip()
        assert isinstance(ref["year"], int)
        assert ref["gaps"]
        assert ref["technique"].strip()
        assert ref["verified_via"].strip()
        assert ref["url"].startswith("https://")
        if ref.get("doi"):
            assert re.match(r"^10\.\d{4,9}/\S+$", ref["doi"]), ref["doi"]
        if ref.get("arxiv"):
            assert re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", ref["arxiv"]), ref["arxiv"]
        assert ref.get("doi") or ref.get("arxiv"), ref["id"]


def test_gaps_cobertos():
    payload = _payload()
    covered = set()
    for ref in payload["references"]:
        covered.update(ref["gaps"])
    missing = REQUIRED_GAPS - covered
    assert not missing, missing


def test_documento_mapeia_gaps():
    text = DOC.read_text(encoding="utf-8")
    for termo in (
        "RC / Pauli-frame",
        "15 taxas Pauli-Lindblad",
        "GST",
        "PEC 2q",
        "ZNE",
        "Superfície",
        "Readout",
        "Crosstalk",
    ):
        assert termo in text, termo
    assert "não promete" in text.lower() or "nao promete" in text.lower()
    assert "cycle benchmarking" in text.lower()


def test_sem_overclaim_ou_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    proibidos = (
        "garante 10/10",
        "resultado 10/10",
        "vantagem quântica comprovada",
        "solução definitiva",
        "qualis a1 garantido",
        "fidelidade comprovada",
    )
    for caminho in (SPEC, DOC):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
