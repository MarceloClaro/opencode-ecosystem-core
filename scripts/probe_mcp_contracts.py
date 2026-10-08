"""Prova R660 com clientes MCP e processos stdio reais, sem inferência simulada."""

from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import socket
import sys
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = [
    "integrations/mcp_validation.py", "mci/mcp_server.py", "mci/metabus.py",
    "mci/blackboard.py", "synthetic_university/mcp_security.py",
    "synthetic_university/mcp_server.py", "scanners/scanners_mcp_server.py",
    "colibri/colibri_mcp_server.py", "integrations/colibri_provider.py",
    "scripts/probe_mcp_contracts.py",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes() if path.exists() else b"").hexdigest()


def _data(result):
    return json.loads(result.content[0].text)


def _result(result):
    return result.model_dump(mode="json", exclude_none=True)


@asynccontextmanager
async def _session(module: str, state: Path, logs: Path, extra_env: dict | None = None):
    state.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ, "MCI_AUTOREGISTER": "0", "MCI_STATE_DIR": str(state),
        "PYTHONUNBUFFERED": "1", **(extra_env or {}),
    }
    parameters = StdioServerParameters(
        command=sys.executable, args=["-m", module], env=env, cwd=str(ROOT),
    )
    with logs.open("w", encoding="utf-8") as errlog:
        async with stdio_client(parameters, errlog=errlog) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=25)) as session:
                initialized = await session.initialize()
                yield session, initialized


async def _probe(report: dict, temporary: Path):
    state = temporary / "mci"
    events = state / "metabus_events.jsonl"
    async with _session("mci.mcp_server", state, temporary / "mci.stderr") as (session, initialized):
        tools = await session.list_tools()
        before = _data(await session.call_tool("mci_get_blackboard_state", {}))
        assert before == {"agents": [], "tasks": {}}
        before_events_hash = _sha256(events)
        negative_results = []
        for name, arguments in [
            ("mci_register_agent", {"agent_id": "invalid", "name": "Invalid", "capabilities": [3]}),
            ("mci_post_task", {"description": "Invalid task", "required_capabilities": [3]}),
            ("mci_get_memory", {"limit": True}),
            ("mci_get_memory", {"limit": 1001}),
        ]:
            result = await session.call_tool(name, arguments)
            assert result.isError is True
            negative_results.append({"tool": name, "arguments": arguments, "result": _result(result)})
        after_negatives = _data(await session.call_tool("mci_get_blackboard_state", {}))
        assert after_negatives == before
        assert _sha256(events) == before_events_hash
        card = {"agent_id": "r660-probe", "name": "R660 real stdio probe", "capabilities": ["contract_probe"],
                "description": "Local transport proof", "schema": {"type": "object"}}
        registered = await session.call_tool("mci_register_agent", card)
        assert registered.isError is False
        posted = await session.call_tool("mci_post_task", {
            "task_id": "r660-stdio-task", "description": "Real stdio registration and task transport",
            "required_capabilities": ["contract_probe"], "context": {"evidence": "stdio_real"},
        })
        assert posted.isError is False
        after = _data(await session.call_tool("mci_get_blackboard_state", {}))
        assert [agent["agent_id"] for agent in after["agents"]] == ["r660-probe"]
        assert after["tasks"] == {"r660-stdio-task": "open"}
        memory = await session.call_tool("mci_get_memory", {"limit": 2.0})
        assert memory.isError is False
        topics = [json.loads(line)["topic"] for line in events.read_text().splitlines()]
        assert topics == ["agent.register", "task.post", "task.cfp"]
        report["servers"]["mci"] = {
            "pass": True, "server_info": initialized.serverInfo.model_dump(),
            "protocol_version": initialized.protocolVersion, "tool_names": [tool.name for tool in tools.tools],
            "initial_state": before, "negatives": negative_results,
            "state_after_negatives": after_negatives, "event_hash_unchanged_after_negatives": True,
            "final_state": after, "persisted_topics": topics, "event_sha256": _sha256(events),
            "memory_result": _result(memory), "agent_execution_completed": False,
        }

    state = temporary / "synthetic_university"
    async with _session("synthetic_university.mcp_server", state, temporary / "su.stderr") as (session, initialized):
        tools = await session.list_tools()
        invalid = await session.call_tool("su_generate", {"n_pairs": True})
        assert invalid.isError is True
        valid = await session.call_tool("su_generate", {"n_pairs": 1.0})
        assert valid.isError is False and _data(valid)["count"] == 1
        assert _data(valid)["fallback"] is True
        report["servers"]["synthetic_university"] = {
            "pass": True, "server_info": initialized.serverInfo.model_dump(),
            "tool_names": [tool.name for tool in tools.tools], "negative": _result(invalid),
            "valid": _result(valid), "generation_mode": "local_synthetic_fallback", "llm_inference_completed": False,
        }

    state = temporary / "scanners"
    events = state / "metabus_events.jsonl"
    async with _session("scanners.scanners_mcp_server", state, temporary / "scanners.stderr") as (session, initialized):
        tools = await session.list_tools()
        before_events_hash = _sha256(events)
        negatives = []
        for name, arguments in [("super_rigor_audit", {}), ("literary_scanner_suite", {"text": "probe", "metadata": []})]:
            result = await session.call_tool(name, arguments)
            assert result.isError is True
            negatives.append({"tool": name, "result": _result(result)})
        assert _sha256(events) == before_events_hash
        valid = await session.call_tool("scientific_reasoning_scan", {
            "text": "A hipótese foi avaliada em um estudo observacional; as limitações impedem inferência causal.",
        })
        assert valid.isError is False
        report["servers"]["scanners"] = {
            "pass": True, "server_info": initialized.serverInfo.model_dump(),
            "tool_names": [tool.name for tool in tools.tools], "negatives": negatives,
            "event_hash_unchanged_after_negatives": True, "valid": _result(valid),
            "external_scientific_validation": False,
        }

    state = temporary / "colibri"
    # Reservar uma porta sem listen impede conflito ou conexão com motor existente.
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
        async with _session("colibri.colibri_mcp_server", state, temporary / "colibri.stderr",
                            {"COLIBRI_HOST": "127.0.0.1", "COLIBRI_PORT": str(port)}) as (session, initialized):
            tools = await session.list_tools()
            invalid = await session.call_tool("colibri_generate", {"prompt": "probe", "max_tokens": True})
            assert invalid.isError is True
            offline = await session.call_tool("colibri_generate", {"prompt": "probe", "max_tokens": 1, "auto_start": False})
            assert offline.isError is True and _data(offline)["ok"] is False
            assert _data(offline)["result"]["success"] is False
            report["servers"]["colibri"] = {
                "pass": True, "server_info": initialized.serverInfo.model_dump(),
                "tool_names": [tool.name for tool in tools.tools], "negative": _result(invalid),
                "provider_unavailable_result": _result(offline), "provider_probe": "real_connection_refused_reserved_local_port",
                "engine_autostart": False, "llm_inference_completed": False,
            }
    report["stderr_hashes"] = {path.name: _sha256(path) for path in temporary.glob("*.stderr")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/evidence/R660_MCP_STDIO.json")
    parser.add_argument("--timeout", type=float, default=90)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300:
        parser.error("timeout deve estar entre 1 e 300 segundos")
    report = {
        "spec_id": "SPEC-935-R660", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_type": "real_mcp_stdio_processes", "mocked_handlers": False,
        "runtime": {"python": sys.version, "executable": sys.executable, "mcp": version("mcp"), "jsonschema": version("jsonschema")},
        "source_sha256": {name: _sha256(ROOT / name) for name in SOURCE_FILES},
        "servers": {}, "isolated_state": True, "state_retained": False,
        "global_timeout_seconds": args.timeout, "pass": False,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="r660-mcp-proof-") as temporary:
            asyncio.run(asyncio.wait_for(_probe(report, Path(temporary)), timeout=args.timeout))
        report["pass"] = True
    except Exception as exc:
        report["error_type"] = type(exc).__name__
        report["error"] = str(exc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "output": str(args.output), "servers": list(report["servers"])}))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
