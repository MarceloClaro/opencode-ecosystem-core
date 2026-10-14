"""R886: observações recuperáveis e raciocínio sem autopromoção de confiança.

O estado e os eventos são persistidos somente no diretório temporário do teste.
Os contratos exercitam os componentes existentes, sem inferência externa.
"""

from __future__ import annotations

import copy
import importlib

import pytest

from reasoning.engines import MultiReasoningEngine, ReasoningResult
from transformer.memory import HierarchicalMemory


@pytest.fixture()
def isolated_memory(tmp_path, monkeypatch):
    module = importlib.import_module("mci.metabus")
    monkeypatch.setattr(module, "MEMORY_FILE", str(tmp_path / "memory.json"))
    monkeypatch.setattr(module, "EVENTS_FILE", str(tmp_path / "events.jsonl"))
    memory = module.MetacognitiveMemory()
    monkeypatch.setattr(module.metabus, "memory", memory)
    monkeypatch.setattr(module.metabus, "subscribers", {})
    return memory


def test_search_memory_recovers_nested_observation_evidence(isolated_memory):
    observation = {
        "status": "failed",
        "evidence": [{"ref": "ultramarine_delta", "cause": "checksum divergente"}],
        "next_strategy": "recalcular o checksum antes de repetir",
    }
    ident = isolated_memory.record_observation("auditor", "execução local", observation)
    isolated_memory.record_observation("auditor", "execução local", {"status": "unrelated"})

    found = isolated_memory.search_memory("ultramarine_delta")

    assert [entry["id"] for entry in found] == [ident]
    assert found[0]["type"] == "observation"
    assert found[0]["observation"] == observation


def test_search_observation_respects_limit_and_recency(isolated_memory):
    first = isolated_memory.record_observation(
        "auditor", "contexto neutro", {"reason": "ultramarine_delta", "attempt": 1})
    second = isolated_memory.record_observation(
        "auditor", "contexto neutro", {"reason": "ultramarine_delta", "attempt": 2})

    found = isolated_memory.search_memory("ultramarine_delta", limit=1)

    assert [entry["id"] for entry in found] == [second]
    assert found[0]["id"] != first
    assert found[0]["observation"]["attempt"] == 2


def test_hierarchical_entry_text_contains_observation_without_mutating_it(isolated_memory):
    isolated_memory.record_observation("auditor", "execução local", {
        "evidence": [{"ref": "ultramarine_delta"}],
        "cause": "integridade ausente",
    })
    entry = isolated_memory.episodic[-1]
    before = copy.deepcopy(entry)

    text = HierarchicalMemory(isolated_memory)._entry_text(entry)

    assert "ultramarine_delta" in text
    assert "integridade ausente" in text
    assert entry == before


def test_hierarchical_retrieve_ranks_observation_content(isolated_memory, monkeypatch):
    isolated_memory.record_observation("auditor", "contexto neutro", {"cause": "irrelevante"})
    relevant = isolated_memory.record_observation(
        "auditor", "contexto neutro", {"evidence": {"ref": "ultramarine_delta"}})
    memory = HierarchicalMemory(isolated_memory)
    # O vetor determinístico isola a integração texto -> recuperação; evita
    # que colisões do feature hashing substituam o contrato desta unidade.
    monkeypatch.setattr(memory.embedder, "embed_text", lambda text: [
        float("ultramarine_delta" in text), float("irrelevante" in text)])

    found = memory.retrieve("ultramarine_delta", top_entries=1)

    assert [entry["id"] for entry in found] == [relevant]
    assert found[0]["relevance"] > 0.0
    assert found[0]["observation"]["evidence"]["ref"] == "ultramarine_delta"


def test_reasoning_self_score_does_not_update_confidence_or_semantic_lessons(isolated_memory):
    isolated_memory.confidence_ledger.update({"reasoning:critical": 0.23, "auditor": 0.71})
    isolated_memory.upsert_semantic_topic(
        "reasoning.critical", lesson="Lição anterior com evidência independente.",
        metadata={"source": "retained-evidence"})
    ledger_before = dict(isolated_memory.confidence_ledger)
    semantic_before = copy.deepcopy(isolated_memory.semantic)

    result = MultiReasoningEngine().reason(
        "Examinar a alegação de que toda correlação demonstra causalidade.", engine="critical")

    assert isinstance(result, ReasoningResult)
    assert result.engine == "critical"
    assert result.available is True
    assert isolated_memory.confidence_ledger == ledger_before
    assert isolated_memory.semantic == semantic_before


@pytest.mark.parametrize("confidence", [0.0, 0.5, 0.99])
def test_reasoning_result_declares_uncalibrated_nonpromoting_score(confidence):
    result = ReasoningResult(
        engine="critical", query="consulta", conclusion="Conclusão local delimitada.",
        confidence=confidence, steps=["etapa observada"], duration_s=0.25)

    payload = result.to_dict()

    assert payload.get("calibrated") is False
    assert payload.get("confidence_promoted") is False
    assert payload["confidence"] == confidence
    assert payload["engine"] == "critical"
    assert payload["query"] == "consulta"
    assert payload["conclusion"] == result.conclusion
    assert payload["steps"] == ["etapa observada"]
    assert payload["available"] is True
    assert payload["duration_s"] == 0.25
