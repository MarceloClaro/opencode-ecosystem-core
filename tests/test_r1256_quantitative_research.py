from __future__ import annotations

import math
import importlib
import importlib.util

import pytest


def _api(module_name: str, symbol: str):
    module_spec = importlib.util.find_spec(module_name)
    assert module_spec is not None, f"módulo ainda não implementado: {module_name}"
    module = importlib.import_module(module_name)
    assert hasattr(module, symbol), f"API ainda não implementada: {module_name}.{symbol}"
    return getattr(module, symbol)


def test_catalog_contains_200_unique_typed_calculations_and_fails_closed_for_planned_items():
    get_calculation_catalog = _api("research.calculation_catalog", "get_calculation_catalog")
    resolve_calculator = _api("research.calculation_catalog", "resolve_calculator")
    catalog = get_calculation_catalog()
    assert len(catalog) == 200
    assert len({item["id"] for item in catalog}) == 200
    assert {"statistics", "biostatistics", "bioinformatics", "meta_analysis",
            "finance", "physical_chemistry", "physics_quantum_astrophysics"} <= {
                item["domain"] for item in catalog
            }
    assert {"implemented", "planned"} == {item["status"] for item in catalog}
    for item in catalog:
        assert item["id"] and item["name"] and item["inputs"] and item["outputs"]
        if item["status"] == "planned":
            with pytest.raises(NotImplementedError):
                resolve_calculator(item["id"])


def test_catalog_implemented_entries_resolve_to_their_tested_api():
    get_calculation_catalog = _api("research.calculation_catalog", "get_calculation_catalog")
    resolve_calculator = _api("research.calculation_catalog", "resolve_calculator")
    entries = [item for item in get_calculation_catalog() if item["status"] == "implemented"]
    assert len(entries) >= 20
    assert all(callable(resolve_calculator(item["id"])) for item in entries)


def test_sample_size_proportion_uses_finite_population_and_documents_variability():
    calculate_sample_size_proportion = _api("research.quantitative_calculators", "calculate_sample_size_proportion")
    result = calculate_sample_size_proportion(
        population_size=10_000,
        margin_error=0.05,
        confidence_level=0.95,
        expected_proportion=0.5,
    )
    assert result["z_score"] == pytest.approx(1.9599639845)
    assert result["infinite_population_n"] == pytest.approx(384.145882)
    assert result["required_completes"] == 370
    assert result["recruitment_target"] == 370
    assert result["population_size"] == 10_000
    assert result["assumptions"]["population_model"] == "Bernoulli proportion"
    assert "máxima variância" in result["assumptions"]["proportion_choice"]
    assert any("heterogeneidade geográfica" in item for item in result["limitations"])


def test_sample_size_adjusts_for_design_effect_and_nonresponse_without_exceeding_population():
    calculate_sample_size_proportion = _api("research.quantitative_calculators", "calculate_sample_size_proportion")
    result = calculate_sample_size_proportion(
        population_size=100,
        margin_error=0.01,
        confidence_level=0.99,
        expected_proportion=0.5,
        design_effect=1.5,
        nonresponse_rate=0.25,
    )
    assert result["required_completes"] <= 100
    assert result["recruitment_target"] <= 100
    assert result["recruitment_target_feasible"] is False
    assert result["design_effect"] == 1.5
    assert result["nonresponse_rate"] == 0.25


def test_sample_size_mean_uses_standard_deviation_and_finite_correction():
    calculate_sample_size_mean = _api("research.quantitative_calculators", "calculate_sample_size_mean")
    infinite = calculate_sample_size_mean(None, 10, 2, confidence_level=0.95)
    finite = calculate_sample_size_mean(1_000, 10, 2, confidence_level=0.95)
    assert infinite["infinite_population_n"] == pytest.approx(96.036, rel=1e-4)
    assert infinite["required_completes"] == 97
    assert finite["required_completes"] < infinite["required_completes"]
    assert finite["outcome_model"] == "mean with population standard deviation"


@pytest.mark.parametrize("kwargs", [
    {"population_size": 0, "margin_error": 0.05},
    {"population_size": 10, "margin_error": 0},
    {"population_size": 10, "margin_error": 0.05, "confidence_level": 1},
    {"population_size": 10, "margin_error": 0.05, "expected_proportion": 1.5},
    {"population_size": 10, "margin_error": 0.05, "design_effect": 0},
    {"population_size": 10, "margin_error": 0.05, "nonresponse_rate": 1},
])
def test_sample_size_rejects_invalid_inputs(kwargs):
    calculate_sample_size_proportion = _api("research.quantitative_calculators", "calculate_sample_size_proportion")
    with pytest.raises(ValueError):
        calculate_sample_size_proportion(**kwargs)


def test_design_experiment_uses_only_explicit_sample_size_parameters():
    from mci.experiment_designer import design_experiment
    from mci.hypothesis_engine import generate_hypothesis

    absent = design_experiment(generate_hypothesis("Uma intervenção altera o desfecho?"))
    assert "sample_size_calculation" not in absent["experimental_design"]
    claim = design_experiment(
        generate_hypothesis("Uma intervenção altera a proporção de resposta?"),
        context={"sample_size_parameters": {
            "outcome_type": "proportion", "population_size": 1000,
            "margin_error": 0.05, "confidence_level": 0.95,
        }},
    )
    assert "sample_size_calculation" in claim["experimental_design"]
    plan = claim["experimental_design"]["sample_size_calculation"]
    assert plan["required_completes"] > 0
    assert plan["outcome_type"] == "proportion"
    assert plan["execution_authorized"] is False


def test_wilson_interval_and_advanced_biostatistics():
    wilson_interval = _api("research.quantitative_calculators", "wilson_interval")
    diagnostic_accuracy = _api("research.advanced_statistics", "diagnostic_accuracy")
    odds_ratio = _api("research.advanced_statistics", "odds_ratio")
    risk_ratio = _api("research.advanced_statistics", "risk_ratio")
    interval = wilson_interval(56, 100, confidence_level=0.95)
    assert interval["estimate"] == pytest.approx(0.56)
    assert interval["lower"] < 0.56 < interval["upper"]
    rr = risk_ratio(30, 100, 10, 100)
    assert rr["estimate"] == pytest.approx(3.0)
    assert rr["confidence_interval"][0] < 3 < rr["confidence_interval"][1]
    odds = odds_ratio(30, 70, 10, 90)
    assert odds["estimate"] == pytest.approx((30 * 90) / (70 * 10))
    diagnostic = diagnostic_accuracy(tp=80, fn=20, tn=90, fp=10)
    assert diagnostic["sensitivity"] == pytest.approx(0.8)
    assert diagnostic["specificity"] == pytest.approx(0.9)


def test_benjamini_hochberg_is_monotone_and_preserves_input_order():
    benjamini_hochberg = _api("research.advanced_statistics", "benjamini_hochberg")
    adjusted = benjamini_hochberg([0.04, 0.001, 0.02, 0.5])
    by_original = adjusted["adjusted_p_values"]
    assert len(by_original) == 4
    assert by_original[1] == pytest.approx(0.004)
    sorted_adjusted = [adjusted["adjusted_p_values"][i] for i in adjusted["rank_order"]]
    assert sorted_adjusted == sorted(sorted_adjusted)
    assert all(0 <= p <= 1 for p in by_original)


def test_anova_spearman_and_meta_analysis_cochrans_q():
    cochrans_q_meta_analysis = _api("research.advanced_statistics", "cochrans_q_meta_analysis")
    one_way_anova = _api("research.advanced_statistics", "one_way_anova")
    spearman_correlation = _api("research.advanced_statistics", "spearman_correlation")
    anova = one_way_anova([[1, 2, 3], [2, 3, 4], [5, 6, 7]])
    assert anova["statistic"] == pytest.approx(13)
    assert anova["df_between"] == 2
    assert anova["p_value"] < 0.05
    assert 0 <= anova["eta_squared"] <= 1
    correlation = spearman_correlation([1, 2, 3, 4], [2, 4, 6, 8])
    assert correlation["estimate"] == pytest.approx(1)
    q = cochrans_q_meta_analysis([0.2, 0.4, 0.8], [0.01, 0.04, 0.02])
    assert q["statistic"] > 0
    assert q["df"] == 2
    assert 0 <= q["p_value"] <= 1
    assert 0 <= q["i_squared_percent"] <= 100


def test_research_csv_pipeline_accepts_anova_spearman_and_cochrans_q(tmp_path):
    from research.statistical_methods import execute_analysis, validate_configuration
    from research import statistical_methods

    assert {"anova_one_way", "spearman", "cochrans_q_meta_analysis"} <= set(statistical_methods.METHODS)

    csv_file = tmp_path / "groups.csv"
    csv_file.write_text(
        "value,group,x,y,effect,variance\n"
        "1,A,1,2,0.2,0.01\n2,A,2,4,0.4,0.04\n3,A,3,6,0.8,0.02\n"
        "2,B,4,8,0.1,0.03\n3,B,5,10,0.3,0.05\n4,B,6,12,0.6,0.02\n",
        encoding="utf-8",
    )
    validate_configuration("anova_one_way", {"value": "value", "group": "group", "groups": ["A", "B"]})
    anova = execute_analysis(csv_file, "anova_one_way", {"value": "value", "group": "group", "groups": ["A", "B"]})
    spearman = execute_analysis(csv_file, "spearman", {"x": "x", "y": "y"})
    q = execute_analysis(csv_file, "cochrans_q_meta_analysis", {"effect_size": "effect", "variance": "variance"})
    assert anova["execution_attempted"] is True
    assert spearman["estimate"] == pytest.approx(1)
    assert q["degrees_of_freedom"] == 5


def test_advanced_methods_are_allowed_by_scientific_core_configuration():
    from marceloclaro.knowledge_evolution import validate_science_config

    for method, variables in (
        ("anova_one_way", {"value": "y", "group": "group", "groups": ["A", "B"]}),
        ("spearman", {"x": "x", "y": "y"}),
        ("cochrans_q_meta_analysis", {"effect_size": "effect", "variance": "variance"}),
    ):
        try:
            result = validate_science_config({
                "question": "Associação entre variáveis do estudo?",
                "dataset_csv": "dataset.csv",
                "dataset_provenance": {},
                "method": method,
                "variables": variables,
                "output_dir": "analysis-output",
            })
        except Exception as exc:
            result = None
            error = str(exc)
        assert result is not None, f"método avançado rejeitado pelo Core: {method}: {error if result is None else ''}"
        assert result["method"] == method


def test_q_exponential_uses_tsallis_limit_and_domain():
    q_exponential = _api("research.quantitative_calculators", "q_exponential")
    assert q_exponential(1.25, 1.0) == pytest.approx(math.exp(1.25))
    assert q_exponential(1.0, 0.5) == pytest.approx(2.25)
    assert q_exponential(-3.0, 0.5) == 0.0
    with pytest.raises(ValueError):
        q_exponential(3.0, 1.5)


def test_financial_calculators_use_explicit_conventions():
    break_even = _api("research.quantitative_calculators", "break_even")
    contribution_margin = _api("research.quantitative_calculators", "contribution_margin")
    cost_of_goods_sold = _api("research.quantitative_calculators", "cost_of_goods_sold")
    internal_rate_of_return = _api("research.quantitative_calculators", "internal_rate_of_return")
    markup_price = _api("research.quantitative_calculators", "markup_price")
    net_present_value = _api("research.quantitative_calculators", "net_present_value")
    return_on_investment = _api("research.quantitative_calculators", "return_on_investment")
    weighted_average_cost = _api("research.quantitative_calculators", "weighted_average_cost")
    weighted_average_cost_of_capital = _api("research.quantitative_calculators", "weighted_average_cost_of_capital")

    be = break_even(fixed_cost=1000, unit_price=50, unit_variable_cost=30)
    assert be["units_exact"] == pytest.approx(50)
    assert be["units_to_break_even"] == 50
    assert contribution_margin(100, 60)["margin_ratio"] == pytest.approx(0.4)
    assert markup_price(100, 0.25)["selling_price"] == pytest.approx(125)
    assert net_present_value(0.1, [-100, 60, 60])["npv"] == pytest.approx(4.1322314)
    assert cost_of_goods_sold(1000, 500, 200)["cogs"] == 1300
    assert return_on_investment(100, 150)["roi_percent"] == pytest.approx(50)
    assert weighted_average_cost([10, 20], [2, 3])["weighted_average_cost"] == pytest.approx(16)
    wacc = weighted_average_cost_of_capital(600, 400, 0.12, 0.08, 0.25)
    assert wacc["wacc"] == pytest.approx(0.086)
    irr = internal_rate_of_return([-100, 60, 60])
    assert irr["status"] == "unique_root"
    assert irr["irr"] == pytest.approx(0.130662386, rel=1e-6)


def test_irr_reports_multiple_roots_instead_of_selecting_one():
    internal_rate_of_return = _api("research.quantitative_calculators", "internal_rate_of_return")
    result = internal_rate_of_return([-100, 230, -132])
    assert result["status"] == "multiple_roots"
    assert result["irr"] is None
    assert len(result["roots"]) == 2
    assert result["roots"] == pytest.approx([0.1, 0.2], abs=1e-7)


def test_complex_quantum_state_operations_and_born_rule():
    born_probabilities = _api("reasoning.quantum", "born_probabilities")
    density_matrix = _api("reasoning.quantum", "density_matrix")
    inner_product = _api("reasoning.quantum", "inner_product")
    normalize_state_vector = _api("reasoning.quantum", "normalize_state_vector")

    state = normalize_state_vector([1 + 1j, 1 - 1j])
    assert sum(abs(amplitude) ** 2 for amplitude in state) == pytest.approx(1)
    assert inner_product(state, state) == pytest.approx(1 + 0j)
    assert born_probabilities(state) == pytest.approx([0.5, 0.5])
    rho = density_matrix(state)
    assert rho[0][1] == pytest.approx(0.5j)
    assert sum(rho[i][i].real for i in range(2)) == pytest.approx(1)


def test_quantum_expectation_requires_hermitian_operator_and_normalized_state():
    expectation_value = _api("reasoning.quantum", "expectation_value")
    assert expectation_value([1 + 0j, 0j], [[1, 0], [0, -1]]) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        expectation_value([2 + 0j, 0j], [[1, 0], [0, -1]])
    with pytest.raises(ValueError):
        expectation_value([1 + 0j, 0j], [[1, 1], [0, 1]])
