# -*- coding: utf-8 -*-
"""Testes da SPEC-935-R744 — Custódia durável das cadeias.

Hermético: reconfere MANIFESTO contra o disco.
"""
import hashlib
import json
import os

BASE = "workbench/polymath/cadeias"


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def test_manifesto_confere():
    man = json.load(open(os.path.join(BASE, "MANIFESTO.json"), encoding="utf-8"))
    assert man["spec_id"] == "SPEC-935-R744"
    assert man["total"] == len(man["artefatos"]) >= 80
    for ent in man["artefatos"]:
        assert _sha(os.path.join(BASE, ent["arquivo"])) == ent["sha256"]


def test_lotes_chave_presentes():
    for lote in ("polymath_federacao_final", "polymath_lote2", "polymath_intencoes_piloto",
                 "polymath_vivo_real", "polymath_dossie_final"):
        assert os.path.isdir(os.path.join(BASE, lote)), lote
    inv = json.load(open(os.path.join(BASE, "polymath_federacao_final", "intencoes.json"), encoding="utf-8"))
    assert sum(1 for i in inv["intencoes"] if i["status"] == "aprovada") == 2
