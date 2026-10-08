# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R724 — Decisão, rede e federação polímata.

Hermético: intenções/minuta/parecer sintéticos em tmp.
"""
import json
import os

import pytest


def _base(tmp_path):
    base = tmp_path / "int"
    base.mkdir(exist_ok=True)
    (base / "intencoes.json").write_text(json.dumps({
        "intencoes": [
            {"intencao_id": "INT-A", "url": "https://github.com/pgmpy/pgmpy", "classe": "ativo", "status": "aguardando_humano"},
            {"url": "https://github.com/sympy/sympy", "classe": "formal-estavel", "status": "aguardando_humano"}],
        "retidas_informativas": []}), encoding="utf-8")
    (base / "minuta_r621.json").write_text(json.dumps({"minutas": [
        {"artifact_id": "polymath:spec:third_party:pgmpy-pgmpy", "source_path": "/c/README.md",
         "description": "d", "license": "MIT", "capabilities": ["causal"], "content_sha256": "a" * 64}]}), encoding="utf-8")
    (base / "pareceres.json").write_text(json.dumps({"pareceres": [
        {"url": "https://github.com/pgmpy/pgmpy", "maturidade": 8,
         "recomendacao_tecnica": "ratificar_com_ressalvas"}]}), encoding="utf-8")
    (base / "readiness.json").write_text(json.dumps({"avaliadas": [
        {"url": "https://github.com/pgmpy/pgmpy", "pronto_para_R621": True, "pendencias": []}]}), encoding="utf-8")
    return str(base)


def test_sem_humano_recusa(tmp_path):
    from integrations import polymath_federar as fed
    base = _base(tmp_path)
    with pytest.raises(ValueError):
        fed.decidir_titular(base, humano=False, ordem="decida e federe",
                            responsavel="titular", motivos={"https://github.com/pgmpy/pgmpy": "ok"})


def test_decide_rede_federa(tmp_path):
    from integrations import polymath_federar as fed
    base = _base(tmp_path)
    rede = str(tmp_path / "rede")
    r = fed.decidir_titular(base, humano=True, ordem="decida, adicione a rede e federe",
                            responsavel="titular",
                            motivos={"https://github.com/pgmpy/pgmpy": "parecer 8, inventário íntegro"})
    assert r["aprovadas"] == 1
    n = fed.adicionar_rede(base, rede)
    assert n["nodos"] == 1
    f = fed.federar(rede, base)
    assert f["federados"] == 1
    payload = json.loads(open(os.path.join(rede, "federados.json"), encoding="utf-8").read())
    assert payload["escopo"] == "polimata"
    assert payload["federados"][0]["federado_no_escopo_polimata"] is True
    src = open(fed.__file__, encoding="utf-8").read()
    for proibido in ("harness_federation", "Popen(", "os.system(", "pip install"):
        assert proibido not in src
