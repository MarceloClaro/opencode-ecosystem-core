"""R664: hipóteses e composição por registros de capacidade, sem modelos."""
from __future__ import annotations

import copy
import json

import pytest

from scanners.knowledge_composition import KnowledgeComposition
from scanners.potentiality_scanner import (
    PotentialityCandidate, PotentialityScanner, StructuralDNA,
)


def modules():
    return {
        "reader": [{"id": "extract", "state": "available",
                    "evidence": [{"kind": "availability", "ref": "probe:reader",
                                  "success": True}],
                    "outputs": ["document_text"], "tags": ["documents"],
                    "composition": {"conceitos": ["documento"],
                                    "metodos": ["extração textual"],
                                    "bases": ["documentação da extração"],
                                    "ferramentas": ["reader"],
                                    "dominios": ["engenharia de dados"],
                                    "validacoes": ["comparar texto extraído"],
                                    "recursos": ["arquivo de entrada"]}}],
        "indexer": [{"id": "index", "state": "executed",
                     "evidence": [{"kind": "execution", "ref": "tests:index:pass",
                                   "success": True}],
                     "inputs": ["document_text"], "requires": ["store"],
                     "tags": ["documents"],
                     "composition": {"conceitos": ["índice"],
                                     "ferramentas": ["store"],
                                     "recursos": ["disco local"]},
                     "validation_criteria": ["reabrir o índice sem perder fontes"]}],
    }


def test_dna_distinguishes_evidence_levels_and_never_promotes_bare_claims():
    supplied = modules()
    supplied["claimed"] = [{"id": "world_model", "state": "externally_validated"}]
    dna = PotentialityScanner(supplied).extract_dna()
    assert dna["capability_map"]["extract"]["state"] == "available"
    assert dna["capability_map"]["index"]["state"] == "executed"
    assert dna["capability_map"]["world_model"]["state"] == "declared"
    assert dna["capability_map"]["world_model"]["providers"][0]["declared_state"] == "externally_validated"
    assert dna["absent"] == ["store"]
    assert dna["evidence_scope"] == "provided_references"


def test_external_level_requires_explicit_external_evidence():
    source = {"one": [{"id": "x", "state": "externally_validated",
                       "evidence": [{"kind": "external_validation", "ref": "audit:x",
                                     "success": True, "validator": "independent-lab"}]}]}
    assert PotentialityScanner(source).extract_dna()["capability_map"]["x"]["state"] == "externally_validated"
    del source["one"][0]["evidence"][0]["validator"]
    assert PotentialityScanner(source).extract_dna()["capability_map"]["x"]["state"] == "declared"


def test_default_capabilities_are_only_declared():
    dna = PotentialityScanner().extract_dna()
    assert dna["capability_map"]
    assert {row["state"] for row in dna["capability_map"].values()} == {"declared"}


def test_dna_redundancy_counts_distinct_modules_not_duplicate_strings():
    dna = StructuralDNA({"one": ["x", "x"], "two": ["y"]})
    assert dna.redundant == set()
    assert dna.central == set()
    dna = StructuralDNA({"one": ["x", "x"], "two": ["x"]})
    assert dna.redundant == {"x"}


def test_dependency_hubs_are_central_without_being_redundant():
    dna = StructuralDNA({"one": ["store", {"id": "search", "requires": ["store"]},
                                 {"id": "archive", "requires": ["store"]}]})
    assert dna.redundant == set()
    assert "store" in dna.central


def test_code_text_is_not_a_capability_catalog():
    with pytest.raises(ValueError):
        PotentialityScanner({"module": {"code": "def magic(): return quantum"}})


def test_scoring_deduplicates_requirements_and_explains_missing_evidence():
    report = PotentialityScanner(modules()).scan([
        PotentialityCandidate("search", "Consulta com proveniência", ["extract", "extract", "index", "store"])
    ])
    hypothesis = report.by_id["search"]
    assert hypothesis.requires == ["extract", "index", "store"]
    assert hypothesis.coverage == pytest.approx(2 / 3, abs=1e-4)
    assert hypothesis.present == ["extract", "index"]
    assert hypothesis.missing == ["store"]
    assert hypothesis.operational_coverage == pytest.approx(2 / 3, abs=1e-4)
    assert hypothesis.score_kind == "heuristic"
    assert hypothesis.probability_calibrated is False
    assert hypothesis.hypothesis_only is True
    assert hypothesis.explanation and hypothesis.evidence
    assert 0 <= hypothesis.heuristic_score <= 1
    assert hypothesis.heuristic_resistance == pytest.approx(1 - hypothesis.heuristic_score, abs=1e-4)


def test_declared_coverage_is_not_operational_readiness():
    report = PotentialityScanner({"one": ["x"]}).scan([
        PotentialityCandidate("future", "Hipótese", ["x"])])
    candidate = report.by_id["future"]
    assert candidate.coverage == 1
    assert candidate.operational_coverage == 0
    assert candidate.resistance_factors["not_available"] == ["x"]


def test_discover_combines_interfaces_and_retains_missing_dependencies():
    scanner = PotentialityScanner(modules())
    candidates = scanner.discover(max_candidates=12, max_pair_checks=50)
    generated = [row for row in candidates if row.origin == "interfaces"]
    assert generated
    assert any(set(row.requires) == {"extract", "index", "store"} for row in generated)
    assert generated[0].interfaces[0]["type"] == "document_text"
    assert scanner.discover(max_candidates=12, max_pair_checks=50) == candidates


def test_discover_uses_metadata_and_external_relations_as_hypotheses():
    scanner = PotentialityScanner({"one": [{"id": "x", "tags": ["same"]}],
                                   "two": [{"id": "y", "tags": ["same"]}]})
    assert any(row.origin == "metadata" for row in scanner.discover())
    scanner = PotentialityScanner({"one": ["x"], "two": ["y"]},
                                   relations=[{"source": "x", "target": "y", "relation": "enables"}])
    assert any(row.origin == "relations" for row in scanner.discover())


def test_discovery_bounds_are_explicit_and_preserve_input():
    supplied = {f"m{i}": [{"id": f"c{i}", "tags": ["common"]}] for i in range(30)}
    before = copy.deepcopy(supplied)
    scanner = PotentialityScanner(supplied)
    candidates = scanner.discover(max_candidates=5, max_pair_checks=3)
    assert len(candidates) <= 5
    assert scanner.scan(candidates).params["discovery"]["pair_checks"] <= 3
    assert scanner.scan(candidates).params["discovery"]["truncated"] is True
    assert supplied == before


@pytest.mark.parametrize("limit", [True, 0, 129, "5"])
def test_invalid_candidate_bounds_are_rejected(limit):
    with pytest.raises(ValueError):
        PotentialityScanner().discover(max_candidates=limit)


def test_scan_no_argument_and_mapping_methods_restore_pipeline_contract():
    report = PotentialityScanner().scan()
    assert list(report.items())
    assert report.get("latent_potentials")
    assert report.to_dict()["n_candidates"] > 0
    assert PotentialityScanner().scan([]).candidates == []
    json.dumps(report.to_dict(), allow_nan=False)


def test_duplicate_candidate_ids_are_not_silently_overwritten():
    with pytest.raises(ValueError):
        PotentialityScanner().scan([
            PotentialityCandidate("same", "one", ["x"]),
            PotentialityCandidate("same", "two", ["y"])], strict_ids=True)


def test_legacy_display_name_collisions_are_disambiguated_without_data_loss():
    scanner = PotentialityScanner({"one": ["x"], "two": ["y"]})
    candidates = [PotentialityCandidate("display", "same name", ["x"]),
                  PotentialityCandidate("display", "same name", ["y"])]
    report = scanner.scan(candidates)
    assert len(report.candidates) == len(report.by_id) == 2
    assert {tuple(item.requires) for item in report.candidates} == {("x",), ("y",)}
    assert report.params["id_aliases"]["display"] == sorted(report.by_id)
    assert report.warnings


def test_compose_metadata_has_seven_categories_internal_dependencies_and_gaps():
    dna = PotentialityScanner(modules()).extract_dna()
    insight = KnowledgeComposition().compose("extract", dna=dna)
    assert insight.origem == "metadata"
    assert insight.recursos == ["arquivo de entrada"]
    assert all(getattr(insight, name) for name in
               ("conceitos", "metodos", "bases", "ferramentas", "dominios", "validacoes", "recursos"))
    assert insight.dependencies
    assert insight.inputs and insight.missing
    assert insight.validation_criteria
    assert insight.construction_map["nodes"] == insight.inputs
    assert insight.construction_map["edges"] == insight.dependencies
    assert all(edge["relation"] == "requires" for edge in insight.dependencies)
    assert all(edge["origin"] for edge in insight.dependencies)
    assert all(node["origin"] == "module:reader:extract" for node in insight.inputs)


def test_compose_records_absent_capability_requirements_and_missing_categories():
    dna = PotentialityScanner(modules()).extract_dna()
    insight = KnowledgeComposition().compose("index", dna=dna)
    assert insight.missing_capabilities == ["store"]
    assert "metodos" in insight.missing_categories
    assert any(edge["source"] == "index" and edge["target"] == "store"
               for edge in insight.dependencies)
    assert any("reabrir" in item["description"] for item in insight.validation_criteria)


def test_composition_fallback_marks_unknowns_and_never_invents_complete_recipe():
    insight = KnowledgeComposition().compose("invented.quantum_causality")
    assert insight.origem == "lexical"
    assert insight.warning
    assert "metodos" in insight.missing_categories
    assert "validacoes" in insight.missing_categories
    assert not insight.validacoes and not insight.recursos


def test_compose_many_serializes_and_keeps_legacy_bank_unchanged():
    composition = KnowledgeComposition()
    dna = PotentialityScanner(modules()).extract_dna()
    before = copy.deepcopy(dna)
    report = composition.compose_many(["extract", "index"], dna=dna)
    assert set(report.by_capability) == {"extract", "index"}
    data = report.to_dict()
    assert data["by_capability"]["index"]["missing_capabilities"] == ["store"]
    json.dumps(data, allow_nan=False)
    assert dna == before
    assert composition.compose("metodos.Meta-análise").origem == "bank"
    assert composition.compose_many([]).matches == []


def test_generated_hypothesis_composition_preserves_component_requirements():
    scanner = PotentialityScanner(modules())
    candidates = scanner.discover()
    hypothesis = next(item for item in candidates if item.origin == "interfaces")
    report = KnowledgeComposition().compose_many([hypothesis.id], dna=scanner.extract_dna(),
                                                candidates=candidates)
    insight = report.by_capability[hypothesis.id]
    assert insight.ferramentas == hypothesis.requires
    assert insight.missing_capabilities == ["store"]
    assert "validacoes" in insight.missing_categories
    assert insight.planning_only is True
    assert any(node["state"] == "executed" for node in insight.inputs)
    assert all(node["origin"] == "hypothesis:interfaces" for node in insight.inputs)


def test_available_validation_materials_are_not_completed_validation():
    supplied = {"one": [{"id": "capacity", "composition": {"validacoes": ["criterion"]}},
                         {"id": "criterion", "state": "available",
                          "evidence": [{"kind": "availability", "ref": "installed:criterion",
                                        "success": True}]}]}
    insight = KnowledgeComposition().compose("capacity", dna=PotentialityScanner(supplied).extract_dna())
    assert insight.validation_criteria[0]["state"] == "pending"
    assert insight.missing_validation_criteria == [insight.validation_criteria[0]["id"]]
    assert insight.construction_map["validation_pending"]


def test_execution_provenance_roundtrips_through_dna_and_composition():
    proof = {"kind": "execution", "ref": "docs/evidence/runtime.json", "success": True,
             "sha256": "A1" * 32, "scope": "  actual_local_execution  ",
             "runtime": {"name": "python", "version": "3.14", "flags": ["offline"]},
             "artifact": {"path": "docs/evidence/runtime.json", "run": 7}}
    scanner = PotentialityScanner({"one": [{"id": "component", "state": "executed",
                                            "evidence": [proof]}]})
    dna = scanner.extract_dna()
    recorded = dna["capability_map"]["component"]["evidence"][0]
    assert {key: recorded[key] for key in proof} == proof
    candidate = PotentialityCandidate("hypothesis", "Composição", ["component"], origin="interfaces")
    # Este ID já possui uma declaração; a hipótese continua identificada como tal.
    dna["capability_map"]["hypothesis"] = {"state": "declared", "requires": ["component"]}
    insight = KnowledgeComposition().compose("hypothesis", dna=dna, candidate=candidate)
    assert insight.origem == "metadata"
    assert insight.inputs[0]["origin"] == "hypothesis:interfaces"
    input_proof = insight.inputs[0]["evidence"][0]
    assert {key: input_proof[key] for key in proof} == proof
    assert insight.construction_map["complete"] is False
    assert proof["runtime"]["flags"] == ["offline"]


def test_hash_scope_and_artifacts_do_not_promote_evidence_levels():
    proof = {"kind": "execution", "ref": "runtime:one", "success": True,
             "sha256": "a" * 64, "scope": "external_validation",
             "runtime": "external", "artifact": {"externally_validated": True}}
    scanner = PotentialityScanner({"one": [{"id": "component", "state": "externally_validated",
                                            "evidence": [proof]}]})
    assert scanner.extract_dna()["capability_map"]["component"]["state"] == "executed"
    proof["kind"] = "note"
    scanner = PotentialityScanner({"one": [{"id": "component", "state": "externally_validated",
                                            "evidence": [proof]}]})
    assert scanner.extract_dna()["capability_map"]["component"]["state"] == "declared"


@pytest.mark.parametrize("sha", ["short", "g" * 64, 42, None])
def test_invalid_evidence_hashes_are_rejected(sha):
    with pytest.raises(ValueError):
        PotentialityScanner({"one": [{"id": "x", "evidence": [
            {"kind": "note", "ref": "provided", "sha256": sha}]}]})


def test_provenance_json_is_bounded_and_json_only():
    for artifact in ({"bad": float("nan")}, {"code": object()}, {"large": "x" * 9000}):
        with pytest.raises(ValueError):
            PotentialityScanner({"one": [{"id": "x", "evidence": [
                {"kind": "note", "ref": "provided", "artifact": artifact}]}]})
