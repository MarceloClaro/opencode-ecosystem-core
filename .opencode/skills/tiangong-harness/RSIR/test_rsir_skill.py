"""Testes da skill Tiangong RSIR — delegação honesta ao MCP local."""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(APP_DIR))

import importlib.util  # noqa: E402

_SPEC = importlib.util.spec_from_file_location("tiangong_rsir_skill", APP_DIR / "skill.py")
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
validate_input = _MODULE.validate_input
execute_harness = _MODULE.execute_harness
get_limitations = _MODULE.get_limitations


def test_missing_action_fails():
    result = validate_input({"metadata": {}})
    assert result["status"] == "error"
    assert result["result"]["code"] == "missing_action"


def test_unknown_action_fails():
    result = validate_input({"action": "bad_action"})
    assert result["status"] == "error"
    assert result["result"]["code"] == "invalid_action"


def test_features_768_is_local_and_deterministic():
    features = [0.5] * 768
    result = validate_input({"action": "features", "features": features})
    assert result["status"] == "success"
    assert result["result"]["dimension"] == 768
    assert result["result"]["mean"] == 0.5


def test_features_dimension_mismatch_fails():
    result = validate_input({"action": "features", "features": [0.1] * 10})
    assert result["status"] == "error"
    assert result["result"]["code"] == "dimension_mismatch"


def test_analyze_and_classify_are_unavailable():
    for action in ("analyze", "classify"):
        result = execute_harness({"action": action})
        assert result["status"] == "unavailable"
        assert result["result"]["class_label"] is None
        assert result["result"]["probabilities"] is None


def test_limitations_are_declared():
    limits = get_limitations()
    assert limits
    assert any("ViT" in item or "modelo" in item.lower() for item in limits)
