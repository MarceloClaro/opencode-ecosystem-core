"""Regressão do fix EvolutionRegistry._load (R581, SPEC-974).

Antes: UMA entrada malformada (formato antigo id/titulo) lançava TypeError
dentro do comprehension → o except zerava o registro inteiro → o próximo
record() sobrescrevia evolution/cycles.json perdendo histórico (425→1).

Garantia: entrada inválida é ignorada individualmente; as válidas carregam.
"""

from __future__ import annotations

import json

from evolution.cycles import EvolutionRegistry

import pytest


def _write_state(tmp_path, entries) -> str:
    path = tmp_path / "cycles.json"
    path.write_text(json.dumps({"cycles": entries}), encoding="utf-8")
    return str(path)


def test_loader_ignora_entrada_legada_e_mantem_validas(tmp_path):
    path = _write_state(
        tmp_path,
        [
            {"round_id": "R574", "objective": "redesign ux", "changes": ["x"], "score": 9.0},
            {"round_id": "R575", "objective": "figuras", "changes": ["y"], "legacy": True},
            {"id": "R550", "titulo": "formato antigo", "spec": "SPEC-970"},
        ],
    )
    reg = EvolutionRegistry(state_path=path)
    assert len(reg.cycles) == 2, "entrada legada não pode derrubar as válidas"
    assert {c.round_id for c in reg.cycles} == {"R574", "R575"}


def test_loader_arquivo_inteiro_zerado_nao_escreve_historia_falsa(tmp_path):
    path = _write_state(tmp_path, ["não-é-dict"])
    reg = EvolutionRegistry(state_path=path)
    assert reg.cycles == []
    # record() precisa funcionar sem destruir estado pré-existente
    reg.record(objective="novo", changes=["c"], round_id="R600")
    assert [c.round_id for c in reg.cycles] == ["R600"]


if __name__ == "__main__":
    pytest.main([__file__, "-q"])