"""Contratos herméticos para roadmap e jogos com payoffs explícitos (R665)."""

import math

import pytest


def cap(key, **kwargs):
    return {"id": key, "evidence": [f"fixture:{key}"], **kwargs}


def dep(source, target, **kwargs):
    return {"source": source, "target": target, "relation": "requires",
            "evidence": [f"fixture:{source}->{target}"], **kwargs}


def plan(capabilities, dependencies, targets, **kwargs):
    from scanners.evolutionary_sequencing import EvolutionarySequencer

    return EvolutionarySequencer().plan(capabilities, dependencies, targets, **kwargs)


def test_parallel_join_and_transitive_closure():
    result = plan([cap("A"), cap("B"), cap("C"), cap("D")],
                  [dep("D", "C"), dep("C", "B"), dep("C", "A")], ["D"])
    assert result["phases"] == [["A", "B"], ["C"], ["D"]]
    assert result["prerequisites"]["C"] == ["A", "B"]
    assert result["successors"]["C"] == ["D"]
    assert result["convergences"][0]["capability"] == "C"
    assert result["convergences"][0]["predecessors"] == ["A", "B"]
    assert result["execution_verified"] is False
    assert result["necessity_proven"] is False


def test_observed_with_evidence_prunes_regression():
    result = plan([cap("A", observed=True), cap("C")],
                  [dep("C", "A"), dep("A", "unknown")], ["C"])
    assert result["phases"] == [["C"]]
    assert result["closure"] == ["A", "C"]
    assert result["missing_dependencies"] == []


def test_missing_dependency_explicit_blocks_transitive_dependants():
    result = plan([cap("A"), cap("B"), cap("C")],
                  [dep("B", "missing"), dep("C", "B")], ["A", "C"])
    assert result["phases"] == [["A"]]
    assert result["missing_dependencies"] == [
        {"capability": "B", "dependency": "missing", "reason": "unknown_capability"}]
    assert result["blocked_nodes"] == ["B", "C"]
    assert result["status"] == "blocked"


def test_unknown_target_is_reported_and_never_silently_dropped():
    result = plan([cap("A")], [], ["unknown"])
    assert result["missing_targets"] == ["unknown"]
    assert result["phases"] == []
    assert result["status"] == "blocked"


def test_cycle_and_descendant_blocked_but_independent_phase_available():
    result = plan([cap(k) for k in ["A", "B", "C", "D"]],
                  [dep("A", "B"), dep("B", "A"), dep("C", "B")], ["C", "D"])
    assert result["cycle_components"] == [["A", "B"]]
    assert result["blocked_nodes"] == ["A", "B", "C"]
    assert result["phases"] == [["D"]]


def test_self_cycle_blocked():
    result = plan([cap("A")], [dep("A", "A")], ["A"])
    assert result["cycle_components"] == [["A"]]
    assert result["phases"] == []


def test_enables_direction_and_cooccurrence_not_requirement():
    result = plan([cap(k) for k in ["A", "B", "C"]],
                  [dep("A", "B", relation="enables"),
                   dep("B", "C", relation="co_occurs")], ["B"])
    assert result["phases"] == [["A"], ["B"]]
    assert "C" not in result["closure"]
    assert len(result["affinities"]) == 1


def test_evidence_missing_is_explicit_and_prevents_satisfied_claim():
    result = plan([cap("A", observed=True, evidence=[]), cap("B")],
                  [dep("B", "A")], ["B"])
    assert result["observed_capabilities"] == []
    assert result["missing_evidence"] == ["A"]
    assert result["blocked_nodes"] == ["A", "B"]


def test_declared_or_available_does_not_satisfy_operational_requirement():
    result = plan([cap("A", observed=True, state="available"),
                   cap("B", state="executed", observed=True)], [], ["A", "B"])
    assert result["observed_capabilities"] == ["B"]
    assert result["phases"] == [["A"]]
    assert result["capability_states"] == {"A": "available", "B": "executed"}


def test_explicit_observed_argument_requires_execution_state_and_evidence():
    result = plan([cap("A", state="declared"), cap("B", state="executed")],
                  [], ["A", "B"], observed=["A", "B"])
    assert result["observed_capabilities"] == ["B"]
    assert result["phases"] == [["A"]]


def test_dna_external_validation_state_alias_satisfies_explicit_observation():
    result = plan([cap("A", state="externally_validated", evidence=[
        {"kind": "external_validation", "ref": "fixture:independent-review", "validator": "reviewer"}])],
        [], ["A"], observed=["A"])
    assert result["observed_capabilities"] == ["A"]
    assert result["evolution_gap"] == []
    assert result["status"] == "already_satisfied"
    assert result["necessity_proven"] is False


def test_edge_without_evidence_is_not_accepted_as_necessary():
    result = plan([cap("A"), cap("B")], [dep("B", "A", evidence=[])], ["B"])
    assert result["unassessed_dependencies"][0]["source"] == "B"
    assert result["blocked_nodes"] == ["B"]
    assert result["status"] == "blocked"


def test_estimated_critical_path_cost_and_resistance():
    result = plan([cap("A", estimated_duration=2, estimated_cost=3, resistance=0.1),
                   cap("B", estimated_duration=5, estimated_cost=4, resistance=0.2),
                   cap("C", estimated_duration=1, estimated_cost=2, resistance=0.5)],
                  [dep("C", "A", estimated_cost=1, resistance=0.3),
                   dep("C", "B", estimated_cost=2, resistance=0.4)], ["C"])
    schedule = result["estimated_schedule"]
    assert schedule["kind"] == "conditional_estimate"
    assert schedule["nodes"]["C"] == {"start": 5.0, "finish": 6.0, "duration": 1.0}
    assert schedule["makespan"] == 6.0
    assert result["estimated_total_cost"] == 12.0
    route = next(r for r in result["routes"] if r["path"] == ["A", "C"])
    assert route["estimated_cost"] == 6.0
    assert route["resistance_index"] == pytest.approx(0.9)
    assert route["kind"] == "precedence_chain"


def test_missing_estimates_are_unknown_and_do_not_invent_zero_cost():
    result = plan([cap("A", estimated_duration=2), cap("B", estimated_duration=1)],
                  [dep("B", "A")], ["B"])
    assert result["estimated_total_cost"] is None
    assert result["routes"][0]["estimated_cost"] is None
    assert result["routes"][0]["resistance_index"] is None
    assert result["estimated_schedule"]["makespan"] == 3.0
    unknown = plan([cap("A"), cap("B", estimated_duration=1)],
                   [dep("B", "A")], ["B"])
    assert unknown["estimated_schedule"]["nodes"]["B"]["start"] is None
    assert unknown["estimated_schedule"]["makespan"] is None


def test_deterministic_reordered_input_and_routes_limited():
    capabilities = [cap(k) for k in ["A", "B", "C", "D"]]
    dependencies = [dep("C", "A"), dep("C", "B"), dep("D", "C")]
    a = plan(capabilities, dependencies, ["D"], max_routes=1)
    b = plan(list(reversed(capabilities)), list(reversed(dependencies)), ["D"], max_routes=1)
    assert a == b
    assert len(a["routes"]) == 1
    assert a["routes_truncated"] is True


def test_equivalent_requires_enables_not_double_counted_and_order_independent():
    capabilities = [cap("A", estimated_cost=1), cap("B", estimated_cost=2)]
    dependencies = [dep("B", "A", estimated_cost=3),
                    dep("A", "B", relation="enables", estimated_cost=3)]
    a = plan(capabilities, dependencies, ["B"])
    b = plan(capabilities, list(reversed(dependencies)), ["B"])
    assert a == b
    assert a["estimated_total_cost"] == 6.0
    assert len(a["dependencies"]) == 1


def test_declared_hypothesis_remains_a_planning_assumption():
    result = plan([cap("A"), cap("B")], [dep("B", "A", necessity="hypothesis")], ["B"])
    assert result["dependencies"][0]["necessity"] == "hypothesis"
    assert result["necessity_proven"] is False


def test_depth_bound_reports_incomplete_routes():
    result = plan([cap(k) for k in ["A", "B", "C"]],
                  [dep("B", "A"), dep("C", "B")], ["C"], max_depth=1)
    assert result["routes"] == []
    assert result["routes_truncated"] is True
    assert result["phases"] == [["A"], ["B"], ["C"]]


def test_intermediate_target_does_not_hide_route_to_later_target():
    result = plan([cap(k) for k in ["A", "B", "C"]],
                  [dep("B", "A"), dep("C", "B")], ["B", "C"])
    assert [r["path"] for r in result["routes"]] == [["A", "B"], ["A", "B", "C"]]


def test_non_finite_or_non_json_evidence_rejected():
    with pytest.raises(ValueError):
        plan([cap("A", evidence=[{"confidence": math.nan}])], [], ["A"])


def test_adapter_does_not_change_legacy_mapper_api():
    from scanners.trajectory_mapper import TrajectoryMapper

    result = TrajectoryMapper().sequence([cap("A"), cap("B")], [dep("B", "A")], ["B"])
    assert result["phases"] == [["A"], ["B"]]


@pytest.mark.parametrize("updates", [{"estimated_duration": -1}, {"estimated_cost": math.nan},
                                    {"resistance": 2}, {"estimated_cost": True}])
def test_invalid_estimates_rejected(updates):
    with pytest.raises(ValueError):
        plan([cap("A", **updates)], [], ["A"])


def test_duplicate_capability_rejected():
    with pytest.raises(ValueError):
        plan([cap("A"), cap("A")], [], ["A"])


def test_unknown_relation_rejected():
    with pytest.raises(ValueError):
        plan([cap("A"), cap("B")], [dep("B", "A", relation="probably")], ["B"])


def test_pareto_does_not_include_dominated_defection():
    from gametheory.phd_auditor import NashSolver

    result = NashSolver.prisoners_dilemma()
    assert ["Trair", "Trair"] not in result["pareto_frontier"]
    assert len(result["pareto_frontier"]) == 3
    assert result["payoffs"]["(1, 1)"] == [1.0, 1.0]


def test_rectangular_game_uses_each_players_axis_size():
    from gametheory.phd_auditor import NashSolver

    result = NashSolver.pure_nash([[[1, 0, 2], [0, 1, 3]],
                                   [[1, 0, 3], [0, 1, 4]]],
                                  [["A", "B"], ["X", "Y", "Z"]])
    assert result["n_strategies"] == [2, 3]
    assert result["nash_equilibria"] == [{"strategies": ["B", "Z"], "indices": [1, 2]}]
    assert result["pareto_frontier"] == [["B", "Z"]]
    assert result["total_combinations"] == 6
    assert result["is_prisoners_dilemma"] is False


def test_three_player_tensor_nash_and_pareto():
    from gametheory.phd_auditor import NashSolver

    tensor = [[[0, 0], [0, 0]], [[0, 0], [0, 10]]]
    result = NashSolver.pure_nash([tensor, tensor, tensor])
    assert result["n_players"] == 3
    assert result["pareto_frontier"] == [["S1_2", "S2_2", "S3_2"]]
    assert result["payoffs"]["(1, 1, 1)"] == [10.0, 10.0, 10.0]


@pytest.mark.parametrize("payoffs", [[], [[[1]], [[1, 2]]],
                                      [[[math.inf]], [[0]]], [[[True]], [[0]]],
                                      [[[1, 2], [3]], [[1, 2], [3, 4]]]])
def test_invalid_payoff_tensors_rejected(payoffs):
    from gametheory.phd_auditor import NashSolver

    with pytest.raises(ValueError):
        NashSolver.pure_nash(payoffs)


def test_strategy_name_dimensions_rejected():
    from gametheory.phd_auditor import NashSolver

    with pytest.raises(ValueError):
        NashSolver.pure_nash([[[1]], [[1]]], [["A"], []])


def test_non_prisoners_game_not_misclassified():
    from gametheory.phd_auditor import NashSolver

    result = NashSolver.pure_nash([[[4, 0], [2, 2]], [[4, 2], [0, 2]]])
    assert result["is_prisoners_dilemma"] is False


def test_prisoner_parameters_must_satisfy_payoff_inequality():
    from gametheory.phd_auditor import NashSolver

    with pytest.raises(ValueError):
        NashSolver.prisoners_dilemma(t=1, r=3, p=1, s=0)


def test_payoff_space_limit_enforced():
    from gametheory.phd_auditor import NashSolver

    with pytest.raises(ValueError):
        NashSolver.pure_nash([[[1, 2], [3, 4]], [[1, 2], [3, 4]]], max_combinations=3)
