"""Testes da skill Tiangong HDR — delegação honesta ao MCP local."""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(APP_DIR))

import importlib.util  # noqa: E402

_SPEC = importlib.util.spec_from_file_location("tiangong_hdr_skill", APP_DIR / "skill.py")
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
    result = validate_input({"action": "invented"})
    assert result["status"] == "error"
    assert result["result"]["code"] == "invalid_action"


def test_image_path_is_refused():
    result = validate_input({"action": "preprocess", "image_path": "/tmp/digit.png"})
    assert result["status"] == "error"
    assert result["result"]["code"] == "path_not_allowed"


def test_preprocess_28x28_pixels_returns_784_features():
    pixels = [[0.5 for _ in range(28)] for _ in range(28)]
    result = validate_input({"action": "preprocess", "pixels": pixels})
    assert result["status"] == "success"
    assert result["result"]["feature_dim"] == 784
    assert len(result["result"]["feature_vector"]) == 784
    assert result["result"]["input_sha256"]


def test_recognize_is_unavailable_without_fabricated_digit():
    result = execute_harness({"action": "recognize"})
    assert result["status"] == "unavailable"
    assert result["result"]["digit"] is None
    assert result["result"]["confidence"] is None


def test_compare_requires_two_vectors():
    result = validate_input({"action": "compare", "left": [0.0] * 784})
    assert result["status"] == "error"
    assert result["result"]["code"] == "missing_input"


def test_limitations_are_declared():
    limits = get_limitations()
    assert limits
    assert any("QNN" in item or "Backend" in item for item in limits)
