"""R829: leitura/exportação fiel do grafo real, sem gerar evidências."""
import copy
import json

import pytest

from agentic_science_v2.evidence_graph import EvidenceGraph
from webapp.pipeline_helpers import _build_graph_from_export, query_evidence_graph


def real_graph(weight=2.5):
    graph = EvidenceGraph()
    braf = graph.add_entity(
        "BRAF", "gene", description="Descrição completa " * 30,
        aliases=["B-Raf", "BRAF1", "BRAF2", "BRAF3"], metadata={"local": True},
        evidence_text="Evidência textual completa " * 30, source="pmid:1", source_type="pubmed",
    )
    drug = graph.add_entity("Vemurafenib", "drug", evidence_text="Descrição do fármaco.", source="pmid:2", source_type="pubmed")
    relation = graph.add_relation(braf.id, drug.id, "TARGETS", weight=weight,
                                  evidence_text="Vínculo observado na fonte.", source="pmid:3", bidirectional=True)
    assert relation is not None
    return graph, braf, drug, relation


def test_exportacao_publica_preserva_referencias_conteudo_e_instante():
    graph, braf, drug, relation = real_graph()
    exported = graph.to_dict()
    assert exported["entities"][braf.id]["evidence"] == braf.evidence
    assert exported["entities"][braf.id]["metadata"] == {"local": True}
    assert exported["entities"][braf.id]["description"] == braf.description
    assert exported["entities"][braf.id]["aliases"] == braf.aliases
    assert exported["relations"][relation.id]["evidence"] == relation.evidence
    assert exported["relations"][relation.id]["bidirectional"] is True
    first_id = braf.evidence[0]
    assert exported["evidence"][first_id]["text"] == graph.evidence_store[first_id].text
    assert exported["evidence"][first_id]["timestamp"] == graph.evidence_store[first_id].timestamp


@pytest.mark.parametrize("weight", [0.0, 2.5])
def test_reidratacao_preserva_ids_pesos_e_grafo_inteiro(weight):
    graph, braf, drug, relation = real_graph(weight)
    exported = json.loads(graph.to_json())
    before = copy.deepcopy(exported)
    restored = _build_graph_from_export(exported)
    assert set(restored.entities) == {braf.id, drug.id}
    assert set(restored.relations) == {relation.id}
    assert restored.relations[relation.id].weight == weight
    assert restored.relations[relation.id].bidirectional is True
    assert restored.entities[braf.id].evidence == braf.evidence
    assert set(restored.evidence_store) == set(graph.evidence_store)
    assert restored.to_dict() == exported
    assert exported == before


def test_browser_braf_tem_tres_evidencias_reais_sem_dupla_contagem():
    graph, braf, drug, relation = real_graph()
    # Uma referência compartilhada continua sendo uma única evidência.
    relation.evidence.append(braf.evidence[0])
    exported = graph.to_dict()
    before = copy.deepcopy(exported)
    result = query_evidence_graph("BRAF", exported)
    assert result["entities_found"] == 2
    assert result["relations_found"] == 1
    assert result["evidences_found"] == 3
    assert result["evidence_membership"] == "known"
    assert {item["id"] for item in result["subgraph"]["entities"]} == {braf.id, drug.id}
    assert {item["id"] for item in result["subgraph"]["relations"]} == {relation.id}
    evidence = result["subgraph"]["evidence"]
    assert set(evidence) == set(graph.evidence_store)
    assert {item["source"] for item in evidence.values()} == {"pmid:1", "pmid:2", "pmid:3"}
    assert exported == before


def test_exportacao_antiga_sem_refs_declara_vinculo_desconhecido():
    graph, braf, _, relation = real_graph()
    exported = graph.to_dict()
    for item in list(exported["entities"].values()) + list(exported["relations"].values()):
        item.pop("evidence", None)
        item.pop("evidence_membership", None)
    for item in exported["evidence"].values():
        item.pop("timestamp", None)
    restored = _build_graph_from_export(exported)
    assert set(restored.entities) == set(graph.entities)
    assert set(restored.evidence_store) == set(graph.evidence_store)
    assert restored.entities[braf.id].evidence == []
    assert restored.relations[relation.id].evidence == []
    assert all(e.timestamp is None for e in restored.evidence_store.values())
    result = query_evidence_graph("BRAF", exported)
    assert result["evidences_found"] is None
    assert result["evidence_membership"] == "unknown"
    assert result["subgraph"]["evidence"] == {}


def test_referencia_ausente_permanece_identificada_sem_evidencia_fabricada():
    graph, braf, _, _ = real_graph()
    exported = graph.to_dict()
    missing = braf.evidence[0]
    exported["evidence"].pop(missing)
    restored = _build_graph_from_export(exported)
    assert missing in restored.entities[braf.id].evidence
    assert missing not in restored.evidence_store
    result = query_evidence_graph("BRAF", exported)
    assert result["evidences_found"] == 2
    assert result["evidence_membership"] == "partial"
    assert result["subgraph"]["unresolved_evidence_ids"] == [missing]


def test_evidencia_duplicada_por_id_e_deduplicada_sem_substituir_origem():
    graph, _, _, _ = real_graph()
    exported = graph.to_dict()
    pieces = list(exported["evidence"].values())
    exported["evidence"] = pieces + [copy.deepcopy(pieces[0])]
    restored = _build_graph_from_export(exported)
    assert len(restored.evidence_store) == 3
    assert restored.evidence_store[pieces[0]["id"]].source == pieces[0]["source"]
    assert restored.evidence_store[pieces[0]["id"]].text == pieces[0]["text"]
    conflicting = copy.deepcopy(pieces[0]); conflicting["source"] = "pmid:conflito"
    exported["evidence"].append(conflicting)
    with pytest.raises(ValueError, match="duplicado"):
        _build_graph_from_export(exported)


@pytest.mark.parametrize("weight", [float("nan"), float("inf"), True, "desconhecido"])
def test_peso_invalido_nao_e_trocado_por_um(weight):
    graph, _, _, relation = real_graph()
    exported = graph.to_dict(); exported["relations"][relation.id]["weight"] = weight
    with pytest.raises(ValueError):
        _build_graph_from_export(exported)


def test_ids_das_chaves_e_viz_antiga_preservados_sem_inventar_evidencia():
    graph = _build_graph_from_export({
        "nodes": [{"id": "BRAF-original", "label": "BRAF", "group": "gene"},
                  {"id": "drug-original", "label": "Vemurafenib", "group": "drug"}],
        "edges": [{"id": "rel-original", "from": "BRAF-original", "to": "drug-original", "label": "TARGETS", "width": 0.0}],
    })
    assert set(graph.entities) == {"BRAF-original", "drug-original"}
    assert set(graph.relations) == {"rel-original"}
    assert graph.relations["rel-original"].weight == 0.0
    assert graph.evidence_store == {}
