"""R1099: MCP Core-native de pesquisa quântica GJQ."""
from __future__ import annotations

import pytest

pytest.importorskip("gjq_client")
pytest.importorskip("mcp")

QASM = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""


def _tools():
    from integrations.gjq_runtime_mcp import create_server

    return create_server()._tool_manager._tools


def test_gjq_runtime_tools_and_status():
    tools = _tools()
    assert set(tools) >= {
        "gjq_runtime_status",
        "gjq_list_backends",
        "gjq_least_busy",
        "gjq_backend_config",
        "gjq_backend_properties",
        "gjq_sample",
        "gjq_estimate",
        "gjq_task_status",
        "gjq_task_result",
        "gjq_task_detail",
        "gjq_list_tasks",
        "gjq_audit_counts",
        "gjq_provider_status",
        "gjq_provider_submit",
        "gjq_provider_result",
        "gjq_provider_compilation",
        "gjq_research_status",
        "gjq_research_plan",
    }
    status = tools["gjq_runtime_status"].fn()
    assert status["sdk_present"] is True
    assert status["sdk_version"] == "0.2.1"
    assert status["confirm_required"] is True
    assert status["allow_hardware_required"] is True
    assert status["executed"] is False
    assert status["network_access"] is False
    assert "GJQ_API_KEY" not in str(status)


def test_gjq_runtime_confirm_and_hardware_gates():
    tools = _tools()
    with pytest.raises(ValueError):
        tools["gjq_sample"].fn(QASM, "FAS-CPU", 1024, 1, True, None, False, False)
    blocked = tools["gjq_sample"].fn(QASM, "Guoji08", 1024, 1, True, None, False, True)
    assert blocked["status"] == "blocked"
    assert blocked["executed"] is False
    with pytest.raises(ValueError):
        tools["gjq_estimate"].fn(QASM, "FAS-CPU", [["ZZ", 1.0]], 1024, 1, True, None, False, False)


def test_gjq_runtime_without_key_is_blocked(monkeypatch):
    monkeypatch.delenv("GJQ_API_KEY", raising=False)
    tools = _tools()
    for name, args in (
        ("gjq_list_backends", ()),
        ("gjq_least_busy", ()),
        ("gjq_sample", (QASM, "FAS-CPU", 1024, 1, True, None, False, True)),
    ):
        result = tools[name].fn(*args)
        assert result["status"] == "blocked"
        assert "GJQ_API_KEY" in result["reason"]


def test_gjq_provider_tools_fail_closed(monkeypatch):
    monkeypatch.delenv("GJQ_API_KEY", raising=False)
    tools = _tools()
    status = tools["gjq_provider_status"].fn()
    assert status["network_access"] is False
    assert status["hardware_executed"] is False
    blocked = tools["gjq_provider_submit"].fn(
        QASM, "FAS-CPU", 1024, False, False, False, 1, True, None
    )
    assert blocked["status"] == "blocked"
    result = tools["gjq_provider_result"].fn("task-x", None, False)
    assert result["status"] == "blocked"
    compilation = tools["gjq_provider_compilation"].fn("Baihua", [106, 107], False)
    assert compilation["status"] == "blocked"


def test_gjq_runtime_audit_counts():
    tools = _tools()
    ok = tools["gjq_audit_counts"].fn({"00": 512, "11": 512}, 1024)
    assert ok["ok"] is True
    assert abs(sum(ok["probabilities"].values()) - 1.0) < 1e-9
    bad = tools["gjq_audit_counts"].fn({"00": 512, "11": 512}, 1000)
    assert bad["ok"] is False
    assert bad["alerts"]
