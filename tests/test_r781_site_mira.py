"""Functional acceptance tests for the R781 didactic routing laboratory."""

import json
import math
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "artigos" / "pucrs-roteamento-atencao" / "site" / "router.mjs"


def execute_node(body, *, check=True):
    node = shutil.which("node")
    assert node, "Node.js is required to test the browser routing module."
    script = (
        f"import {{ rankCandidates, stableSoftmax }} from {json.dumps(ROUTER.as_uri())};\n"
        + body
    )
    return subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=check,
    )


def rank(candidates, required=("lean",)):
    result = execute_node(
        "process.stdout.write(JSON.stringify(rankCandidates("
        + json.dumps(candidates)
        + ", "
        + json.dumps(list(required))
        + ")));"
    )
    return json.loads(result.stdout)


def candidate(identifier, **changes):
    row = {
        "id": identifier,
        "name": identifier,
        "status": "available",
        "capabilities": ["lean", "python"],
        "semantic": 0.8,
        "trust": 0.9,
        "load": 0.1,
    }
    row.update(changes)
    return row


def test_published_example_and_normalization():
    result = rank(
        [
            candidate("ana", name="Ana", semantic=0.8417),
            candidate("cid", name="Cid", semantic=0.7703, trust=0.7, load=0.4),
        ]
    )
    ana, cid = result["ranked"]
    assert result["excluded"] == []
    assert [ana["id"], cid["id"]] == ["ana", "cid"]
    assert ana["coverage"] == cid["coverage"] == 1
    assert ana["utility"] == pytest.approx(0.91751)
    assert cid["utility"] == pytest.approx(0.81609)
    expected_ana = 1 / (1 + math.exp(cid["utility"] - ana["utility"]))
    assert ana["weight"] == pytest.approx(expected_ana, abs=1e-12)
    assert cid["weight"] == pytest.approx(1 - expected_ana, abs=1e-12)
    assert sum(row["weight"] for row in result["ranked"]) == pytest.approx(1)


def test_mask_precedes_softmax_and_requires_every_capability():
    result = rank(
        [
            candidate("valid"),
            candidate("busy", status="busy", semantic=1),
            candidate("missing", capabilities=["lean"], semantic=1),
            candidate("unknown", capabilities=None),
        ],
        required=("lean", "python"),
    )
    assert [row["id"] for row in result["ranked"]] == ["valid"]
    assert result["ranked"][0]["weight"] == 1
    assert {row["id"] for row in result["excluded"]} == {"busy", "missing", "unknown"}
    assert all(isinstance(row["reason"], str) and row["reason"] for row in result["excluded"])


def test_every_duplicate_occurrence_is_excluded_even_if_one_is_unavailable():
    result = rank(
        [candidate("same"), candidate("same", status="busy"), candidate("unique")]
    )
    assert [row["id"] for row in result["ranked"]] == ["unique"]
    assert [row["id"] for row in result["excluded"]] == ["same", "same"]
    assert all("duplic" in row["reason"].lower() for row in result["excluded"])


@pytest.mark.parametrize("identifier", ["", "  ", None, 7])
def test_invalid_ids_cannot_enter_ranking(identifier):
    result = rank([candidate(identifier)])
    assert result["ranked"] == []
    assert len(result["excluded"]) == 1
    assert result["excluded"][0]["reason"]


def test_empty_and_fully_masked_pools_are_empty():
    assert rank([]) == {"ranked": [], "excluded": []}
    result = rank([candidate("busy", status="offline")])
    assert result["ranked"] == []
    assert len(result["excluded"]) == 1


def test_single_eligible_candidate_has_weight_one_and_empty_requirements_are_covered():
    row = rank([candidate("only", capabilities=[])], required=())["ranked"][0]
    assert row["weight"] == 1
    assert row["coverage"] == 1


def test_ties_use_codepoint_id_order_and_do_not_mutate_inputs():
    result = execute_node(
        "const pool = "
        + json.dumps([candidate("a"), candidate("Z"), candidate("A")])
        + "; const before = JSON.stringify(pool);"
        + " const result = rankCandidates(pool, ['lean']);"
        + " process.stdout.write(JSON.stringify({result, unchanged: before === JSON.stringify(pool)}));"
    )
    output = json.loads(result.stdout)
    assert output["unchanged"]
    assert [row["id"] for row in output["result"]["ranked"]] == ["A", "Z", "a"]
    assert all(row["weight"] == pytest.approx(1 / 3) for row in output["result"]["ranked"])


def test_nonfinite_missing_and_out_of_range_values_are_normalized():
    output = execute_node(
        "const result = rankCandidates(["
        "{id:'nonfinite', name:'N', status:'available', capabilities:['lean'],"
        " semantic:NaN, trust:Infinity, load:-Infinity},"
        "{id:'bounds', name:'B', status:'available', capabilities:['lean'],"
        " semantic:8, trust:-3, load:4},"
        "{id:'missing', name:'M', status:'available', capabilities:['lean']}"
        "], ['lean']); process.stdout.write(JSON.stringify(result));"
    )
    rows = {row["id"]: row for row in json.loads(output.stdout)["ranked"]}
    assert [rows["nonfinite"][key] for key in ("semantic", "trust", "load")] == [0.5, 0.5, 0.5]
    assert [rows["missing"][key] for key in ("semantic", "trust", "load")] == [0.5, 0.5, 0.5]
    assert [rows["bounds"][key] for key in ("semantic", "trust", "load")] == [1, 0, 1]
    assert rows["bounds"]["utility"] == pytest.approx(0.65)


@pytest.mark.parametrize("scores", [[], [1000], [1000, 999, -1000], [-1000, -1001]])
def test_stable_softmax_handles_empty_singleton_and_extreme_scores(scores):
    output = execute_node(
        f"process.stdout.write(JSON.stringify(stableSoftmax({json.dumps(scores)})));"
    )
    weights = json.loads(output.stdout)
    if not scores:
        assert weights == []
        return
    assert len(weights) == len(scores)
    assert all(math.isfinite(weight) and 0 <= weight <= 1 for weight in weights)
    assert sum(weights) == pytest.approx(1)
    shifted = [math.exp(score - max(scores)) for score in scores]
    assert weights == pytest.approx([score / sum(shifted) for score in shifted])


@pytest.mark.parametrize("scores", ["[NaN]", "[Infinity]", "[-Infinity]", "[1, '2']", "null"])
def test_softmax_rejects_nonfinite_or_nonnumeric_input(scores):
    output = execute_node(f"stableSoftmax({scores});", check=False)
    assert output.returncode != 0
    assert "TypeError" in output.stderr or "RangeError" in output.stderr
