"""Testes da skill Tiangong VRP — heurística clássica, sem alegar QAOA."""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(APP_DIR))

import importlib.util  # noqa: E402

_SPEC = importlib.util.spec_from_file_location("tiangong_vrp_skill", APP_DIR / "skill.py")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate_input = _MODULE.validate_input
execute_harness = _MODULE.execute_harness
get_limitations = _MODULE.get_limitations

NODES = [
    {"id": "0", "x": 0, "y": 0, "demand": 0},
    {"id": "1", "x": 1, "y": 0, "demand": 1},
    {"id": "2", "x": 1, "y": 1, "demand": 1},
    {"id": "3", "x": 0, "y": 1, "demand": 1},
]


def test_missing_action_fails():
    result = validate_input({"metadata": {}})
    assert result["status"] == "error"
    assert result["result"]["code"] == "missing_action"


def test_unknown_action_fails():
    result = validate_input({"action": "invented"})
    assert result["status"] == "error"
    assert result["result"]["code"] == "invalid_action"


def test_solve_declares_classical_heuristic():
    result = validate_input({
        "action": "solve", "nodes": NODES,
        "n_vehicles": 2, "capacity": 100,
    })
    assert result["status"] == "success"
    assert result["result"]["backend"] == "classical-heuristic"
    assert result["result"]["quantum"] is False
    assert result["result"]["optimality"] == "not_proven"
    assert result["result"]["feasible"] is True


def test_solve_requires_nodes():
    result = validate_input({
        "action": "solve", "dataset_type": "built-in",
        "n_nodes": 22, "n_vehicles": 4, "vehicle_capacity": 100,
    })
    assert result["status"] == "error"
    assert result["result"]["code"] == "invalid_payload"


def test_zero_vehicles_fails():
    result = validate_input({
        "action": "solve", "nodes": NODES, "n_vehicles": 0, "capacity": 100,
    })
    assert result["status"] == "error"
    assert result["result"]["code"] == "invalid_payload"


def test_upload_is_unavailable():
    result = execute_harness({"action": "upload"})
    assert result["status"] == "unavailable"


def test_limitations_are_declared():
    limits = get_limitations()
    assert limits
    assert any("QAOA" in item or "otimalidade" in item for item in limits)
