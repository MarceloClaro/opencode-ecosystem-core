# -*- coding: utf-8 -*-
"""Testes RED/GREEN da SPEC-935-R723 — Dossiê sem decidir.

Hermético: artefatos sintéticos em tmp.
"""
import json
import os


def _piloto(tmp_path):
    base = tmp_path / "piloto"
    base.mkdir(exist_ok=True)
    (base / "intencoes.json").write_text(json.dumps(
        {"intencoes": [{"url": "https://github.com/pgmpy/pgmpy", "status": "aprovada"}],
         "retidas_informativas": []}), encoding="utf-8")
    (base / "pareceres.json").write_text(json.dumps({"pareceres": []}), encoding="utf-8")
    return str(base)


def test_dossie_schema_e_ausente(tmp_path):
    from integrations import polymath_dossie as do
    base = _piloto(tmp_path)
    out = do.emitir(base, str(tmp_path / "out"))
    assert out["ok"] is True
    payload = json.loads(open(os.path.join(str(tmp_path / "out"), "dossie_final.json"), encoding="utf-8").read())
    assert payload["spec_id"] == "SPEC-935-R723"
    nomes = [a["arquivo"] for a in payload["artefatos"]]
    assert "intencoes.json" in nomes and "pareceres.json" in nomes
    aus = [a for a in payload["artefatos"] if a.get("ausente")]
    assert len(aus) >= 1
    assert all(len(a.get("sha256", "x" * 64)) == 64 for a in payload["artefatos"] if not a.get("ausente"))
    assert payload["ratificacao_titular_pendente"] is True


def test_sem_rede_subprocesso_harness():
    import integrations.polymath_dossie as mod
    src = open(mod.__file__, encoding="utf-8").read()
    for proibido in ("urlopen(", "import subprocess", "os.system(", "Popen(", "harness_federation"):
        assert proibido not in src
