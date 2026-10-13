"""R826: páginas positivas, soma exata e validação com escopo declarado."""
from copy import deepcopy
import json
import math

import pytest

from nano_orchestration import NanoPlan
from nano_orchestration.planner import NanoPlanner


INVALID_NUMBERS = [0, -1, True, False, 1.0, 0.5, float("nan"), float("inf"), -float("inf"), "2", None]


@pytest.mark.parametrize("pages", INVALID_NUMBERS)
def test_preview_rejects_invalid_page_total_before_creating_blocks(monkeypatch, pages):
    monkeypatch.setattr("nano_orchestration.planner.default_nano_block",
                        lambda **_: pytest.fail("Página inválida iniciou a criação de blocos."))
    with pytest.raises(ValueError):
        NanoPlanner().estimate_from_pages(pages)


@pytest.mark.parametrize("pages", [1, 2, 3, 4, 5])
def test_default_preview_requires_enough_pages_for_all_six_sections(pages):
    with pytest.raises(ValueError, match="seções"):
        NanoPlanner().estimate_from_pages(pages)


@pytest.mark.parametrize("pages", [1, 2, 3, 4, 5])
def test_small_preview_accepts_explicit_compatible_sections(pages):
    names = ["Seção " + str(number) for number in range(pages)]
    result = NanoPlanner().estimate_from_pages(pages, names)
    assert result["sections"] == [(name, 1) for name in names]
    assert result["total_pages"] == pages and result["total_blocks"] == pages * 10
    assert result["validation"]["valid"] is True
    assert result["validation"]["page_allocation_checked"] is True


@pytest.mark.parametrize("pages", [6, 7, 8, 9, 10, 11, 12, 17, 99, 100, 500])
def test_default_preview_preserves_positive_allocation_and_exact_sum(pages):
    result = NanoPlanner().estimate_from_pages(pages)
    allocation = result["sections"]
    assert len(allocation) == 6 and sum(value for _, value in allocation) == pages
    assert all(type(value) is int and value > 0 for _, value in allocation)
    assert result["total_blocks"] == sum(result["blocks_per_section"].values()) == pages * 10
    assert result["validation"]["valid"] is True
    assert result["validation"]["page_allocation_checked"] is True
    assert result["validation"]["validation_scope"] == "pages_and_structure"


@pytest.mark.parametrize("names", ["Introdução", [], ["A", "A"], ["", "B"], ["A", 1], [" A ", "A"], [None]])
def test_preview_rejects_invalid_or_duplicate_section_names(names):
    with pytest.raises(ValueError):
        NanoPlanner().estimate_from_pages(10, names)


@pytest.mark.parametrize("pages", INVALID_NUMBERS)
def test_plan_rejects_invalid_section_pages_before_building(monkeypatch, pages):
    monkeypatch.setattr("nano_orchestration.planner.default_nano_block",
                        lambda **_: pytest.fail("Página inválida iniciou a criação de blocos."))
    with pytest.raises(ValueError):
        NanoPlanner().plan("Teste", [("Seção", pages)])


@pytest.mark.parametrize("total", INVALID_NUMBERS[:-1] + [3])
def test_explicit_total_must_be_positive_integer_and_equal_to_section_sum(total):
    with pytest.raises(ValueError):
        NanoPlanner().plan("Teste", [("Seção", 2)], total_pages=total)


@pytest.mark.parametrize("keyword,value", [("blocks_per_page", 0), ("blocks_per_page", True),
                                          ("blocks_per_page", 2.5), ("blocks_per_page", float("nan")),
                                          ("lines_per_page", 0), ("lines_per_page", -1),
                                          ("lines_per_page", True)])
def test_discretization_parameters_must_be_positive_integers(keyword, value):
    with pytest.raises(ValueError):
        NanoPlanner(**{keyword: value})


@pytest.mark.parametrize("pages", [0, -1, True, 1.0, float("nan")])
def test_validate_plan_rejects_invalid_total_without_claiming_validity(pages):
    planner = NanoPlanner()
    plan = planner.plan("Teste", [("Seção", 2)])
    plan.total_pages = pages
    result = planner.validate_plan(plan)
    assert result["valid"] is False and result["errors"]
    assert math.isfinite(result["score"]) and 0 <= result["score"] < 10


@pytest.mark.parametrize("allocation", [[["Seção", -1]], [["Seção", 0]], [["Seção", True]],
                                         [["Seção", 1]], [["Outra", 2]], [["Seção", float("nan")]]])
def test_validate_plan_rejects_invalid_persisted_allocation(allocation):
    planner = NanoPlanner()
    plan = planner.plan("Teste", [("Seção", 2)])
    plan.metadata["section_pages"] = allocation
    result = planner.validate_plan(plan)
    assert result["valid"] is False and result["errors"]


def test_empty_plan_is_invalid_instead_of_vacuously_scoring_ten():
    result = NanoPlanner().validate_plan(NanoPlan(total_pages=2, sections=["Seção"]))
    assert result["valid"] is False and result["errors"]


def test_legacy_plan_without_allocation_declares_only_structural_scope():
    planner = NanoPlanner()
    plan = planner.plan("Legado", [("Seção", 2)])
    plan.metadata.pop("section_pages", None)
    result = planner.validate_plan(plan)
    assert result["valid"] is True
    assert result["page_allocation_checked"] is False
    assert result["validation_scope"] == "structure_only_missing_page_allocation"
    assert result["warnings"]


def test_sections_and_block_counters_cannot_diverge():
    planner = NanoPlanner()
    plan = planner.plan("Teste", [("Seção", 2)])
    altered = deepcopy(plan)
    altered.sections.append("Sem blocos")
    assert planner.validate_plan(altered)["valid"] is False
    altered = deepcopy(plan)
    altered.blocks.pop()
    assert planner.validate_plan(altered)["valid"] is False


def test_block_budget_is_rejected_before_allocation(monkeypatch):
    monkeypatch.setattr("nano_orchestration.planner.default_nano_block",
                        lambda **_: pytest.fail("Plano excessivo iniciou a criação de blocos."))
    with pytest.raises(ValueError, match="blocos"):
        NanoPlanner().plan("Excessivo", [("Seção", 10**12)])


@pytest.mark.parametrize("legacy", [False, True])
def test_real_checkpoint_loader_preserves_validation_and_allocation_scope(tmp_path, legacy):
    from nano_orchestration.orchestrator import NanoOrchestrator
    plan = NanoPlanner().plan("Checkpoint", [("Introdução", 1), ("Conclusão", 1)])
    if legacy:
        plan.metadata.pop("section_pages")
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"plan": plan.to_dict(), "phase": "planning", "phases_completed": ["planning"]}))
    orchestrator = NanoOrchestrator(dry_run=True)
    assert orchestrator.load_checkpoint(str(path)) == "planning"
    result = orchestrator.planner.validate_plan(orchestrator._plan)
    assert result["valid"] is True
    assert result["page_allocation_checked"] is (not legacy)
    assert result["block_types"] == {"descritivo": 1, "argumentativo": 8, "transicao": 1, "conclusao": 10}


def test_persisted_density_is_checked_independently_of_validator_configuration():
    plan = NanoPlanner(blocks_per_page=2).plan("Densidade", [("Seção", 2)])
    assert NanoPlanner().validate_plan(plan)["valid"] is True
    plan.metadata["blocks_per_page"] = 3
    assert NanoPlanner().validate_plan(plan)["valid"] is False


@pytest.mark.parametrize("sections", [None, "Seção", [("A", 1), ("A", 1)], [("", 1)],
                                      [(None, 1)], ["A"], [("A", 1, 2)]])
def test_explicit_plan_rejects_invalid_section_structure(sections):
    with pytest.raises(ValueError):
        NanoPlanner().plan("Teste", sections)


def test_weighted_preview_preserves_historical_hundred_page_distribution():
    result = NanoPlanner().estimate_from_pages(100)
    assert result["sections"] == [("Introdução", 12), ("Fundamentação Teórica", 25),
                                  ("Metodologia", 15), ("Resultados", 18),
                                  ("Discussão", 20), ("Conclusão", 10)]


def test_equal_weight_preview_breaks_integer_remainder_ties_deterministically():
    result = NanoPlanner().estimate_from_pages(5, ["A", "B", "C"])
    assert result["sections"] == [("A", 2), ("B", 2), ("C", 1)]
    assert result["total_blocks"] == 50
