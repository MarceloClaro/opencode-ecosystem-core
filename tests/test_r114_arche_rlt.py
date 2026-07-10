# -*- coding: utf-8 -*-
"""
Testes R114 — ARCHE RLT (Reasoning Logic Tree, SPEC-057)
==========================================================
Testa reasoning/arche_rlt.py: os 6 tipos de inferência de Peirce,
RLTNode, ReasoningMapper, RLTBuilder, RLTValidator e RLTVisualizer.

Requisitos (SPEC-057, primeira implementação em código):
  - 6 tipos de Peirce (DR, DC, IC, IH, AK, AP)
  - Mapeamento cobre 100% dos motores reais de MultiReasoningEngine
  - RLTBuilder constrói árvore a partir de ensemble() real
  - RLTValidator detecta profundidade excessiva e ausência de fecho
  - RLTVisualizer exporta dict e Mermaid válidos
"""

import pytest

from reasoning.arche_rlt import (
    PeirceType, RLTNode, ReasoningMapper, RLTBuilder, RLTValidator,
    RLTVisualizer, ArcheRLT, ENGINE_TO_PEIRCE,
)
from reasoning.engines import ReasoningResult


class TestPeirceTypes:
    def test_six_types_defined(self):
        assert len(PeirceType) == 6
        assert {t.name for t in PeirceType} == {"DR", "DC", "IC", "IH", "AK", "AP"}


class TestReasoningMapper:
    def test_maps_z3_to_deduction_rule(self):
        assert ReasoningMapper().classify_engine_name("z3") == PeirceType.DR

    def test_maps_kanren_to_abduction_knowledge(self):
        """SPEC-057 Secao 5: 'AK: miniKanren logica relacional'."""
        assert ReasoningMapper().classify_engine_name("kanren") == PeirceType.AK

    def test_maps_critical_to_abduction_phenomenon(self):
        """SPEC-057 Secao 5: 'AP: Critical (falacias + vieses)'."""
        assert ReasoningMapper().classify_engine_name("critical") == PeirceType.AP

    def test_unknown_engine_defaults_to_dr(self):
        assert ReasoningMapper().classify_engine_name("motor_inexistente") == PeirceType.DR

    def test_coverage_report_covers_all_real_engines(self):
        report = ReasoningMapper().coverage_report()
        assert report["coverage_pct"] == 100.0
        assert report["unmapped"] == []

    def test_all_twelve_engines_have_explicit_mapping(self):
        assert len(ENGINE_TO_PEIRCE) == 12


class TestRLTNode:
    def test_depth_of_leaf_is_one(self):
        node = RLTNode(inference_type=PeirceType.DR, premise="p", conclusion="c")
        assert node.depth() == 1

    def test_depth_grows_with_children(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="p", conclusion="c")
        child = RLTNode(inference_type=PeirceType.IC, premise="p", conclusion="c2")
        grandchild = RLTNode(inference_type=PeirceType.AK, premise="p", conclusion="c3")
        child.add_child(grandchild)
        root.add_child(child)
        assert root.depth() == 3

    def test_to_dict_includes_peirce_code(self):
        node = RLTNode(inference_type=PeirceType.AP, premise="p", conclusion="c")
        d = node.to_dict()
        assert d["inference_code"] == "AP"
        assert d["inference_type"] == "Abduction-Phenomenon"


class TestRLTBuilder:
    def test_build_from_results_classifies_each_engine(self):
        results = [
            ReasoningResult(engine="z3", query="q", conclusion="conclusao z3", confidence=0.8),
            ReasoningResult(engine="kanren", query="q", conclusion="conclusao kanren", confidence=0.6),
        ]
        tree = RLTBuilder().build_from_results("q", results)
        types = {c.inference_type for c in tree.children}
        assert PeirceType.DR in types  # z3
        assert PeirceType.AK in types  # kanren

    def test_unavailable_results_are_skipped(self):
        results = [
            ReasoningResult(engine="z3", query="q", conclusion="c", confidence=0.5, available=False),
        ]
        tree = RLTBuilder().build_from_results("q", results)
        assert len(tree.children) == 0

    def test_build_from_ensemble_real_multi_reasoning_engine(self):
        from reasoning.engines import MultiReasoningEngine
        mre = MultiReasoningEngine()
        ensemble = mre.ensemble("Se todo A é B e X é A, X é B?")
        tree = RLTBuilder().build_from_ensemble("Se todo A é B e X é A, X é B?", ensemble)
        assert tree.conclusion
        assert len(tree.children) >= 1
        used_types = {c.inference_type for c in tree.children}
        assert len(used_types) >= 2  # multiplos motores -> multiplos tipos Peirce


class TestRLTValidator:
    def test_valid_tree_reports_well_formed(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="q", conclusion="conclusao final")
        root.add_child(RLTNode(inference_type=PeirceType.IC, premise="q", conclusion="conclusao final apoiada"))
        result = RLTValidator().validate(root)
        assert result["well_formed"] is True
        assert result["depth"] == 2

    def test_missing_closure_flagged(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="q", conclusion="")
        result = RLTValidator().validate(root)
        assert result["well_formed"] is False
        assert any("Fecho" in i for i in result["issues"])

    def test_excessive_depth_flagged(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="q", conclusion="c0")
        current = root
        for i in range(12):
            child = RLTNode(inference_type=PeirceType.IC, premise="q", conclusion=f"c{i+1}")
            current.add_child(child)
            current = child
        result = RLTValidator(max_depth=10).validate(root)
        assert result["well_formed"] is False
        assert any("Profundidade" in i for i in result["issues"])

    def test_counts_untraceable_children_without_blocking(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="gatos e cachorros", conclusion="conclusao")
        root.add_child(RLTNode(inference_type=PeirceType.IC, premise="x", conclusion="totalmente sem relacao nenhuma"))
        result = RLTValidator().validate(root)
        assert result["untraceable_children"] == 1
        assert result["well_formed"] is True  # heuristico, nao bloqueia sozinho


class TestRLTVisualizer:
    def test_to_json_dict_roundtrip(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="q", conclusion="c")
        d = RLTVisualizer().to_json_dict(root)
        assert d["id"] == root.id

    def test_to_mermaid_contains_graph_declaration(self):
        root = RLTNode(inference_type=PeirceType.DR, premise="q", conclusion="c")
        child = RLTNode(inference_type=PeirceType.AK, premise="q", conclusion="c2")
        root.add_child(child)
        mermaid = RLTVisualizer().to_mermaid(root)
        assert mermaid.startswith("graph TD")
        assert f"{root.id} --> {child.id}" in mermaid


class TestArcheRLTFacade:
    def test_analyze_returns_tree_mermaid_and_validation(self):
        from reasoning.engines import MultiReasoningEngine
        mre = MultiReasoningEngine()
        ensemble = mre.ensemble("Qual a causa mais provável do fenômeno observado?")
        result = ArcheRLT().analyze("Qual a causa mais provável do fenômeno observado?", ensemble)
        assert "tree" in result and "mermaid" in result and "validation" in result
        assert result["validation"]["depth"] <= RLTBuilder.MAX_DEPTH

    def test_singleton_available(self):
        from reasoning import arche_rlt
        assert isinstance(arche_rlt, ArcheRLT)
