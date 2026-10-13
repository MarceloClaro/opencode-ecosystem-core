"""Contratos locais do allocator de IDs; fixture não é medida de produção."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from evolution import cycles_manager


FIXTURE = Path(__file__).parent / "fixtures" / "r836" / "ledger_sparse.json"


def test_next_id_usa_maximo_numerico_do_ledger_retido():
    before = FIXTURE.read_bytes()
    out = cycles_manager.next_id(FIXTURE)
    assert out["next"] == "R42"
    assert out["total"] == 5
    assert out["status"] == "ready"
    assert "R" not in out
    assert FIXTURE.read_bytes() == before


def test_next_id_respeita_ledger_configurado(monkeypatch):
    monkeypatch.setenv("EVOLUTION_STATE_PATH", str(FIXTURE))
    assert cycles_manager.next_id()["next"] == "R42"


def test_ledger_valido_vazio_inicia_sem_offset(tmp_path):
    ledger = tmp_path / "cycles.json"
    ledger.write_text('{"cycles": []}', encoding="utf-8")
    out = cycles_manager.next_id(ledger)
    assert out["status"] == "ready"
    assert out["next"] == "R1"
    assert out["total"] == 0


def test_ledger_ausente_nao_fabrica_id_nem_cria_arquivo(tmp_path):
    ledger = tmp_path / "ausente.json"
    out = cycles_manager.next_id(ledger)
    assert out["status"] == "unavailable"
    assert out["next"] is None
    assert out["total"] is None
    assert out["error"] == "ledger_missing"
    assert not ledger.exists()


@pytest.mark.parametrize("payload", [
    "{", "[]", "null", "{}", '{"cycles": {}}',
    '{"cycles": [null]}', '{"cycles": [{}]}',
    '{"cycles": [{"round_id": 41}]}',
    '{"cycles": [{"round_id": "R41garbage!"}]}',
    '{"cycles": [{"round_id": "R0"}]}',
    '{"cycles": [{"round_id": "R-41"}]}',
    '{"cycles": [{"round_id": "R41"}, {"round_id": "invalid"}]}',
])
def test_ledger_invalido_falha_fechado_sem_reparo(tmp_path, payload):
    ledger = tmp_path / "cycles.json"
    ledger.write_text(payload, encoding="utf-8")
    before = ledger.read_bytes()
    out = cycles_manager.next_id(ledger)
    assert out["status"] == "unavailable"
    assert out["next"] is None
    assert out["total"] is None
    assert out["error"] == "ledger_invalid"
    assert ledger.read_bytes() == before


def test_ledger_com_numerais_nao_usa_ordenacao_lexicografica(tmp_path):
    ledger = tmp_path / "cycles.json"
    ledger.write_text(json.dumps({"cycles": [
        {"round_id": "R9"}, {"round_id": "R100"}, {"round_id": "R80-final"}
    ]}), encoding="utf-8")
    assert cycles_manager.next_id(ledger)["next"] == "R101"


def test_ledger_diretorio_falha_fechado(tmp_path):
    out = cycles_manager.next_id(tmp_path)
    assert out["status"] == "unavailable"
    assert out["next"] is None
    assert out["error"] == "ledger_invalid"


def test_ledger_utf8_invalido_falha_fechado(tmp_path):
    ledger = tmp_path / "cycles.json"
    ledger.write_bytes(b'\xff')
    out = cycles_manager.next_id(ledger)
    assert out["status"] == "unavailable"
    assert out["next"] is None
    assert out["error"] == "ledger_invalid"
    assert ledger.read_bytes() == b'\xff'


def test_ledger_json_profundo_falha_fechado(tmp_path):
    ledger = tmp_path / "cycles.json"
    depth = sys.getrecursionlimit() + 100
    ledger.write_text("[" * depth + "0" + "]" * depth, encoding="utf-8")
    out = cycles_manager.next_id(ledger)
    assert out["status"] == "unavailable"
    assert out["next"] is None
    assert out["error"] == "ledger_invalid"


@pytest.mark.parametrize("action, trust", [("acao-auditada", 0.9), ("", 0.1)])
def test_fachada_preserva_decisao_canonica_completa(action, trust):
    from protocolos.behavioral_gate import check
    from trust.behavioral_gate import allow

    expected = allow(action, trust=trust, threshold=0.7)
    assert check(action, trust=trust, threshold=0.7) == expected
    assert expected["allowed"] is (trust >= 0.7)
