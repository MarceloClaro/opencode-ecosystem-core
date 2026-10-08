"""SPEC-935-R658: integridade dos dados e comparações, sem treinar modelos."""

import copy
import math

import pytest

from integrations.finetuning_data import evaluation_gate, validate_and_split


def records():
    return [
        {"id": f"pair-{group}-{item}", "group_id": f"source-{group}",
         "input": f"Pergunta {group}/{item}", "output": f"Resposta {group}/{item}"}
        for group in range(6) for item in range(2)
    ]


def result(score=0.6, **overrides):
    data = {"dataset_sha256": "a" * 64, "metric": "accuracy",
            "direction": "higher", "sample_count": 20, "value": score}
    data.update(overrides)
    return data


def codes(report):
    return {diagnostic["code"] for diagnostic in report["diagnostics"]}


def test_valid_data_keep_groups_whole_and_hashes_reproducible():
    data = records()
    report = validate_and_split(data)
    assert report["status"] == "accepted"
    assert validate_and_split(list(reversed(data))) == report
    assert all(report["splits"].values())
    groups = [{item["group_id"] for item in split} for split in report["splits"].values()]
    assert all(not groups[i] & groups[j] for i in range(3) for j in range(i + 1, 3))
    assert sum(map(len, report["splits"].values())) == len(data)
    assert len(report["manifest"]["dataset_sha256"]) == 64
    assert all(len(value) == 64 for value in report["manifest"]["split_sha256"].values())
    assert report["manifest"]["semantic_deduplication"] is False


def test_does_not_mutate_input_and_changed_content_changes_hash():
    data = records()
    original = copy.deepcopy(data)
    before = validate_and_split(data)
    assert data == original
    data[0]["output"] += " alterada"
    assert validate_and_split(data)["manifest"]["dataset_sha256"] != before["manifest"]["dataset_sha256"]


def test_selected_prompt_and_response_formatting_are_preserved():
    data = records()
    data[0]["input"] = "Pergunta\n  item\n\n```code```"
    data[0]["output"] = "Resposta\n    código"
    report = validate_and_split(data)
    selected = next(item for split in report["splits"].values()
                    for item in split if item["id"] == data[0]["id"])
    assert selected["input"] == data[0]["input"]
    assert selected["output"] == data[0]["output"]


def test_normalized_duplicates_connect_sources_and_cannot_cross_splits():
    data = records()
    data.append({"id": "duplicate", "group_id": "source-1",
                 "input": "  Pergunta\n0/0  ", "output": "Resposta ０/０"})
    report = validate_and_split(data)
    assert report["status"] == "accepted"
    assert report["manifest"]["deduplicated_count"] == 1
    assert report["manifest"]["effective_group_count"] == 5
    source_splits = {}
    for split_name, split in report["splits"].items():
        for item in split:
            source_splits[item["group_id"]] = split_name
    assert source_splits["source-0"] == source_splits["source-1"]
    assert validate_and_split(list(reversed(data))) == report


def test_duplicate_transitivity_can_leave_too_few_independent_groups():
    data = [
        {"id": "a", "group_id": "A", "input": "one", "output": "x"},
        {"id": "b", "group_id": "B", "input": "one", "output": "x"},
        {"id": "c", "group_id": "B", "input": "two", "output": "y"},
        {"id": "d", "group_id": "C", "input": "two", "output": "y"},
        {"id": "e", "group_id": "D", "input": "three", "output": "z"},
    ]
    report = validate_and_split(data)
    assert report["status"] == "blocked"
    assert "insufficient_independent_groups" in codes(report)
    assert not any(report["splits"].values())


def test_accents_and_case_are_not_semantic_deduplication():
    data = records()
    data += [
        {"id": "accent", "group_id": "source-0", "input": "ação", "output": "Sim"},
        {"id": "ascii", "group_id": "source-0", "input": "acao", "output": "sim"},
    ]
    assert validate_and_split(data)["manifest"]["deduplicated_count"] == 0


@pytest.mark.parametrize("field,value", [
    ("id", ""), ("group_id", "  "), ("input", None), ("output", []), ("id", True),
    ("input", "\ud800"),
])
def test_malformed_records_are_blocked_without_echoing_data(field, value):
    data = records()
    data[0][field] = value
    data[1]["input"] = "SEGREDO-PERGUNTA"
    report = validate_and_split(data)
    assert report["status"] == "blocked"
    assert "invalid_records" in codes(report)
    assert "SEGREDO-PERGUNTA" not in str(report)


@pytest.mark.parametrize("bad_records", [None, {}, [], [True]])
def test_non_dataset_inputs_block(bad_records):
    assert validate_and_split(bad_records)["status"] == "blocked"


@pytest.mark.parametrize("seed", [True, 4.2, "42", None])
def test_seed_requires_an_integer(seed):
    assert validate_and_split(records(), seed=seed)["status"] == "blocked"


def test_duplicate_ids_and_conflicting_answers_block():
    data = records()
    data.append(dict(data[0]))
    assert "duplicate_ids" in codes(validate_and_split(data))
    data = records()
    data.append({"id": "conflict", "group_id": "source-5",
                 "input": " Pergunta 0/0 ", "output": "Resposta conflitante"})
    assert "conflicting_answers" in codes(validate_and_split(data))


def test_less_than_three_groups_block():
    assert validate_and_split(records()[:4])["status"] == "blocked"


def test_evaluation_accepts_strict_improvement_and_reports_scope():
    report = evaluation_gate(result(0.6), result(0.7))
    assert report["status"] == "accepted"
    assert report["improvement"] == pytest.approx(0.1)
    assert report["verification_scope"] == "reported_results_only"


def test_lower_direction_and_explicit_threshold():
    assert evaluation_gate(result(0.5, direction="lower"), result(0.3, direction="lower"), 0.1)["status"] == "accepted"
    assert evaluation_gate(result(0.5), result(0.6), 0.2)["status"] == "blocked"
    assert evaluation_gate(result(0.5), result(0.5))["status"] == "blocked"
    assert evaluation_gate(result(0.5), result(0.4))["status"] == "blocked"


@pytest.mark.parametrize("baseline,candidate,direction", [
    (0.5, 0.6, "higher"), (0.6, 0.5, "lower"),
])
def test_decimal_threshold_boundary_is_stable(baseline, candidate, direction):
    report = evaluation_gate(result(baseline, direction=direction),
                             result(candidate, direction=direction), 0.1)
    assert report["status"] == "accepted"
    assert report["improvement"] == pytest.approx(0.1)


def test_materially_below_threshold_is_rejected():
    assert evaluation_gate(result(0.5), result(0.5999999), 0.1)["status"] == "blocked"


def test_microscopic_gain_still_requires_strict_positive_and_scaled_threshold():
    assert evaluation_gate(result(0), result(1e-20))["status"] == "accepted"
    assert evaluation_gate(result(0), result(0))["status"] == "blocked"
    assert evaluation_gate(result(0), result(1e-20), 1e-20)["status"] == "accepted"
    assert evaluation_gate(result(0), result(1e-20), 2e-20)["status"] == "blocked"


@pytest.mark.parametrize("field,value", [
    ("dataset_sha256", "b" * 64), ("metric", "loss"),
    ("direction", "lower"), ("sample_count", 21),
])
def test_incomparable_evaluation_blocks(field, value):
    assert evaluation_gate(result(), result(0.7, **{field: value}))["status"] == "blocked"


@pytest.mark.parametrize("field,value", [
    ("dataset_sha256", "short"), ("dataset_sha256", "g" * 64),
    ("metric", ""), ("direction", "unknown"),
    ("sample_count", True), ("sample_count", 0), ("sample_count", 20.0),
    ("value", True), ("value", math.nan), ("value", math.inf),
    ("value", "0.7"), ("value", None), ("value", 10 ** 1000),
])
def test_invalid_evaluation_evidence_blocks(field, value):
    bad = result(0.7, **{field: value})
    assert evaluation_gate(result(), bad)["status"] == "blocked"
    assert evaluation_gate(bad, result())["status"] == "blocked"


@pytest.mark.parametrize("threshold", [True, math.nan, math.inf, -1, "0.1", None])
def test_invalid_improvement_threshold_blocks(threshold):
    assert evaluation_gate(result(), result(0.7), threshold)["status"] == "blocked"


def test_missing_evidence_and_benchmark_identity_blocks():
    incomplete = result(0.7)
    del incomplete["value"]
    assert evaluation_gate(result(), incomplete)["status"] == "blocked"
    assert evaluation_gate(None, result())["status"] == "blocked"
    assert evaluation_gate(result(benchmark_ids_sha256="c" * 64), result(0.7))["status"] == "blocked"
    assert evaluation_gate(result(benchmark_ids_sha256="c" * 64), result(0.7, benchmark_ids_sha256="d" * 64))["status"] == "blocked"
    assert evaluation_gate(result(benchmark_ids_sha256="c" * 64), result(0.7, benchmark_ids_sha256="c" * 64))["status"] == "accepted"
