"""Regressão SPEC-935-R611: next_round_id() não pode colidir com specs/.

Histórico: EvolutionRegistry.record() sem round_id explícito derivava o próximo
numeral SÓ dos ciclos carregados (cycles.json); como specs/SPEC-935-R607.md já
existia, o ciclo do reparo das descrições foi gravado como R607 (colisão).
R611 faz next_round_id() varrer também o diretório de specs (EVOLUTION_SPECS_PATH)
e devolver o próximo numeral livre em ambas as fontes.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from evolution.cycles import EvolutionRegistry


def _registry(tmp: Path, spec_ids: list[str], cycle_ids: list[str]):
    specs = tmp / "specs"
    specs.mkdir(exist_ok=True)
    for sid in spec_ids:
        (specs / f"SPEC-935-{sid}-titulo.md").write_text("---\nnome: x\n---\n")
    state = tmp / "cycles.json"
    state.write_text(
        "{\n  \"cycles\": [\n"
        + ",\n".join(
            f'{{"round_id": "{rid}", "objective": "o", "changes": [], '
            f'"lessons": [], "timestamp": 1.0}}'
            for rid in cycle_ids
        )
        + "\n]}\n",
        encoding="utf-8",
    )
    return {
        "EVOLUTION_STATE_PATH": str(state),
        "EVOLUTION_SPECS_PATH": str(specs),
    }


def test_nao_colide_com_spec_existente(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        env = _registry(Path(d), ["R607", "R610"], ["R609"])
        monkeypatch.setenv("EVOLUTION_STATE_PATH", env["EVOLUTION_STATE_PATH"])
        monkeypatch.setenv("EVOLUTION_SPECS_PATH", env["EVOLUTION_SPECS_PATH"])
        r = EvolutionRegistry()  # reload com env isolado
        # cycles max=609, specs max=610 -> próximo livre: 611
        assert r.next_round_id() == "R611"


def test_peca_maior_over_specs(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        env = _registry(Path(d), ["R700"], ["R606"])
        monkeypatch.setenv("EVOLUTION_STATE_PATH", env["EVOLUTION_STATE_PATH"])
        monkeypatch.setenv("EVOLUTION_SPECS_PATH", env["EVOLUTION_SPECS_PATH"])
        r = EvolutionRegistry()
        assert r.next_round_id() == "R701"


def test_record_sem_round_id_herda_seq_sem_colisao(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        env = _registry(Path(d), ["R700"], [])
        monkeypatch.setenv("EVOLUTION_STATE_PATH", env["EVOLUTION_STATE_PATH"])
        monkeypatch.setenv("EVOLUTION_SPECS_PATH", env["EVOLUTION_SPECS_PATH"])
        r = EvolutionRegistry()
        c = r.record(objective="sem colisão", changes=["x"], score=1.0)
        assert c.round_id == "R701"
        # segundo registro consecutivo também avança
        c2 = r.record(objective="seguinte", changes=["y"], score=1.0)
        assert c2.round_id == "R702"


def test_diretorio_specs_ausente_nao_quebra(monkeypatch, tmp_path):
    state = tmp_path / "cycles.json"
    state.write_text("{\"cycles\": []}\n", encoding="utf-8")
    monkeypatch.setenv("EVOLUTION_STATE_PATH", str(state))
    monkeypatch.setenv("EVOLUTION_SPECS_PATH", str(tmp_path / "nao-existe"))
    r = EvolutionRegistry()
    assert r.next_round_id() == "R47"  # fallback: R46 base + 1