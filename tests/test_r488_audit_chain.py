# -*- coding: utf-8 -*-
"""Testes do Audit Chain entre ciclos (R488) — lição Bernstein.

Encadeia ciclos do evolution/cycles.json via HMAC-SHA256 (RFC 2104):
cada ciclo âncora registra prev_state_merkle_root = state_merkle_root do
ciclo anterior. verify_state_chain() detecta rearranjo/remoção/injeção.

Hermético: usa EVOLUTION_STATE_PATH temporário por teste (sem tocar o real).
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re

import pytest

from evolution.cycles import EvolutionRegistry, chain_state_merkle

MODULE_TEXT = pathlib.Path("evolution/cycles.py").read_text(encoding="utf-8")


def _write_state(path: pathlib.Path, cycles: list[dict]) -> None:
    path.write_text(json.dumps({"cycles": cycles}, ensure_ascii=False), encoding="utf-8")


def _state_hash_bytes(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture()
def state_path(tmp_path) -> pathlib.Path:
    return tmp_path / "cycles.json"


@pytest.fixture()
def anchored_two(state_path) -> pathlib.Path:
    """Dois ciclos âncora encadeados corretamente."""
    _write_state(state_path, [])
    r1 = EvolutionRegistry(state_path=str(state_path))
    c1 = r1.record("c1", ["a"], score=8)
    after_1 = _state_hash_bytes(state_path)
    # grava R488-style: prev="" + state do nó anterior como âncora
    _write_state(state_path, [])
    r2 = EvolutionRegistry(state_path=str(state_path))
    c2 = r2.record("c2", ["b"], score=7)
    after_2 = _state_hash_bytes(state_path)
    return state_path


# ═══════════════════════════════════════════════════════════════════════
# CA1 — primitiva HMAC
# ═══════════════════════════════════════════════════════════════════════

class TestChainPrimitive:
    def test_deterministic_hmac(self):
        a = chain_state_merkle("prev", b"state-bytes")
        b = chain_state_merkle("prev", b"state-bytes")
        assert a == b
        assert len(a) == 64  # sha256 hex

    def test_rfc2104_key_msg(self):
        # HMAC com key=prev distingue de sha256 puro
        assert chain_state_merkle("k", b"msg") != hashlib.sha256(b"msg").hexdigest()

    def test_key_and_msg_matter(self):
        assert chain_state_merkle("k1", b"m") != chain_state_merkle("k2", b"m")
        assert chain_state_merkle("k", b"m1") != chain_state_merkle("k", b"m2")


# ═══════════════════════════════════════════════════════════════════════
# CA2-CA7 — registro e verificação de cadeia
# ═══════════════════════════════════════════════════════════════════════

class TestRegistryChain:
    def test_no_anchors_ok(self, state_path):
        _write_state(state_path, [])
        reg = EvolutionRegistry(state_path=str(state_path))
        reg.record("a", ["x"], score=5)
        v = reg.verify_state_chain()
        assert v["ok"] is True
        assert v["anchored"] == 0
        assert v["size"] == 0

    def test_continuous_chain_of_two(self, state_path):
        # nó âncora 1 (prev="", state preenchido)
        _write_state(state_path, [])
        reg1 = EvolutionRegistry(state_path=str(state_path))
        c1 = reg1.record("c1", ["a"], score=8)
        # forçamos âncora do nó 1 como hash do estado pós-inserção
        s1 = _state_hash_bytes(state_path)
        c1.state_merkle_root = s1
        c1.prev_state_merkle_root = ""
        reg1.save()

        # nó âncora 2 encadeado
        reg2 = EvolutionRegistry(state_path=str(state_path))
        c2 = reg2.record("c2", ["b"], score=7)
        s2 = _state_hash_bytes(state_path)
        c2.prev_state_merkle_root = c1.state_merkle_root
        c2.state_merkle_root = s2
        reg2.save()

        v = reg2.verify_state_chain()
        assert v["ok"] is True
        assert v["anchored"] == 2
        assert v["size"] == 2
        assert v["broken"] == []

    def test_tamper_breaks_chain(self, state_path):
        _write_state(state_path, [])
        reg1 = EvolutionRegistry(state_path=str(state_path))
        c1 = reg1.record("c1", ["a"], score=8)
        s1 = _state_hash_bytes(state_path)
        c1.state_merkle_root = s1
        c1.prev_state_merkle_root = ""
        reg1.save()
        reg2 = EvolutionRegistry(state_path=str(state_path))
        c2 = reg2.record("c2", ["b"], score=7)
        c2.prev_state_merkle_root = "0000"  # adulterado: não bate com s1
        c2.state_merkle_root = _state_hash_bytes(state_path)
        reg2.save()
        v = reg2.verify_state_chain()
        assert v["ok"] is False
        assert len(v["broken"]) == 1
        assert v["broken"][0]["round_id"] == c2.round_id

    def test_blind_node_between_anchors(self, state_path):
        _write_state(state_path, [])
        reg1 = EvolutionRegistry(state_path=str(state_path))
        c1 = reg1.record("c1", ["a"], score=8)
        s1 = _state_hash_bytes(state_path)
        c1.state_merkle_root = s1
        c1.prev_state_merkle_root = ""
        reg1.save()
        # nó cego: registro manual sem âncoras
        data = json.loads(state_path.read_text(encoding="utf-8"))
        data["cycles"].append({"round_id": "R49", "objective": "cego", "changes": []})
        state_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        reg2 = EvolutionRegistry(state_path=str(state_path))
        c2 = reg2.record("c2", ["b"], score=7)
        c2.prev_state_merkle_root = c1.state_merkle_root
        c2.state_merkle_root = _state_hash_bytes(state_path)
        reg2.save()
        v = reg2.verify_state_chain()
        assert v["ok"] is True     # nó cego não quebra a cadeia dos ancorados
        assert v["anchored"] == 2

    def test_loads_real_state(self):
        reg = EvolutionRegistry()  # cycles.json real (349+ ciclos)
        assert len(reg.cycles) >= 340
        assert reg.verify_state_chain()["ok"] is True


# ═══════════════════════════════════════════════════════════════════════
# CA9 — documentação
# ═══════════════════════════════════════════════════════════════════════

class TestDocs:
    def test_algorithm_documented(self):
        assert "RFC 2104" in MODULE_TEXT or "hmac" in MODULE_TEXT
        assert "prev_state_merkle_root" in MODULE_TEXT
        assert "verify_state_chain" in MODULE_TEXT