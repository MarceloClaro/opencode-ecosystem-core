"""SPEC-935-R1249: rota HTTP direta e preparo AT-SPI no WSL2, sem alvo."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_plan_selects_official_streamable_http_without_java_or_proxy():
    from integrations.burp_wsl2_plan import load_plan

    plan = load_plan(ROOT)
    assert plan["spec_id"] == "SPEC-935-R1249"
    assert plan["status"] == "blocked_missing_bapp"
    assert plan["transport"] == "remote_streamable_http"
    assert plan["endpoint"] == "http://127.0.0.1:9876/mcp"
    assert plan["requires_java"] is False
    assert plan["requires_proxy_jar"] is False
    assert plan["source"]["repository"] == "PortSwigger/mcp-server"
    assert plan["source"]["commit"] == "291034081160bc944b6df3eccd60c6fc99b477e1"
    assert plan["source"]["bapp_version"] == "1.4.0"
    assert plan["source"]["supported_products"] == ["Pro", "Community"]


def test_plan_remains_loopback_only_and_does_not_claim_target_activity():
    from integrations.burp_wsl2_plan import load_plan

    safety = load_plan(ROOT)["safety"]
    assert safety["bind_host"] == "127.0.0.1"
    assert safety["burp_started"] is False
    assert safety["extension_installed"] is False
    assert safety["opencode_server_configured"] is False
    assert safety["mcp_connected"] is False
    assert safety["http_requests_sent"] is False
    assert safety["target_testing_authorized"] is False
    assert safety["burp_config_edited"] is False


def test_catalog_surfaces_plan_without_claiming_burp_enabled():
    from integrations.claude_bughunter_catalog import load_catalog

    catalog = load_catalog(ROOT)
    plan = catalog["wsl2_transport_plan"]
    assert plan["transport"] == "remote_streamable_http"
    assert plan["safety"]["opencode_server_configured"] is False
    assert catalog["burp_mcp"]["enabled"] is False
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert "burp" not in json.dumps(config.get("mcp", {}), ensure_ascii=False).casefold()


def test_atspi_backend_is_available_after_typelib_staging():
    env = dict(os.environ)
    env["DESKTOP_OPERATOR_BACKEND"] = "atspi"
    result = subprocess.run(
        ["/usr/bin/python3", "-m", "integrations.desktop_operator", "status"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["backend"] == "atspi"
    assert payload["data"]["scope"]["linux_apps"] is True
    assert payload["data"]["scope"]["windows_apps"] is False
