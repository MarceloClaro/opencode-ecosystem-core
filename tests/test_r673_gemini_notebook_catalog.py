"""Política pura e inventário isolado para o checkout Gemini Notebook."""

import json
import copy
import os
import subprocess
from pathlib import Path

import pytest

from integrations.gemini_notebook_catalog import (
    MCP_NAMES,
    SKILL_DESTINATIONS,
    classify_cli_argv,
    classify_mcp_operation,
)


def test_catalog_has_exactly_49_tools():
    assert len(MCP_NAMES) == len(set(MCP_NAMES)) == 49
    assert {"collection_create", "notebook_query_start", "download_all_artifacts"} <= set(MCP_NAMES)


@pytest.mark.parametrize("name,args,effect", [
    ("notebook_list", {}, "read"),
    ("notebook_describe", {}, "inference"),
    ("notebook_query", {}, "inference"),
    ("notebook_query_status", {}, "read"),
    ("source_describe", {}, "inference"),
    ("source_get_content", {}, "read"),
    ("note", {"action": "list"}, "read"),
    ("note", {"action": "create"}, "write"),
    ("note", {"action": "delete"}, "destructive"),
    ("label", {"action": "list"}, "write"),
    ("label", {"action": "reorganize"}, "destructive"),
    ("label", {"action": "reorganize", "unlabeled_only": True}, "write"),
    ("tag", {"action": "select"}, "read"),
    ("tag", {"action": "remove"}, "write"),
    ("research_status", {}, "read"),
    ("research_status", {"auto_import": True}, "write"),
    ("studio_status", {}, "read"),
    ("studio_status", {"action": "list_types"}, "read"),
    ("studio_status", {"action": "rename"}, "write"),
    ("batch", {"action": "query"}, "inference"),
    ("batch", {"action": "studio", "confirm": False}, "write"),
    ("batch", {"action": "delete"}, "destructive"),
    ("pipeline", {"action": "list"}, "read"),
    ("pipeline", {"action": "run"}, "destructive"),
    ("pipeline", {"action": "run", "steps": [{"action": "notebook_query"}]}, "inference"),
    ("pipeline", {"action": "run", "steps": [{"action": "source_add"}, {"action": "notebook_delete"}]}, "destructive"),
    ("download_artifact", {}, "download"),
    ("export_artifact", {}, "publish"),
    ("notebook_share_public", {}, "publish"),
    ("notebook_share_public", {"is_public": False}, "write"),
    ("collection_delete", {}, "destructive"),
    ("save_auth_tokens", {}, "auth_private"),
    ("refresh_auth", {}, "auth_private"),
])
def test_mcp_effects(name, args, effect):
    assert classify_mcp_operation(name, args) == effect


@pytest.mark.parametrize("name,args", [
    ("shell", {}), ("note", {"action": "execute"}), ("label", {}),
    ("studio_status", {"action": "shell"}), ("batch", {"action": "run"}),
    ("pipeline", {"action": "run", "steps": [{"action": "shell"}]}),
    ("research_status", {"auto_import": "false"}),
])
def test_mcp_unknown_or_ambiguous_effect_is_rejected(name, args):
    with pytest.raises(ValueError):
        classify_mcp_operation(name, args)


@pytest.fixture(scope="module")
def real_catalog():
    checkout = Path("/home/marceloclaro/projetos/gemini-notebook-mcp-cli-core/src")
    if not checkout.is_dir():
        pytest.skip("Checkout pinado ausente; o inventário real exige pacote instalado.")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(checkout)
    proc = subprocess.run(
        [os.sys.executable, "-m", "integrations.gemini_notebook_catalog"],
        env=env, capture_output=True, text=True, timeout=30, check=True,
    )
    return json.loads(proc.stdout)


def test_real_inventory_covers_leaf_and_group_callbacks(real_catalog):
    assert len(real_catalog) == 155
    paths = {tuple(row["path"]) for row in real_catalog}
    assert {(), ("login",), ("doctor",), ("usage",), ("create", "audio"), ("slides", "revise")} <= paths


@pytest.mark.parametrize("argv,path,effect", [
    (["notebook", "list", "--json"], ["notebook", "list"], "read"),
    (["list", "notebooks", "--json"], ["list", "notebooks"], "read"),
    (["notebook", "query", "abc", "What is the result?"], ["notebook", "query"], "inference"),
    (["source", "delete", "a", "b", "--confirm"], ["source", "delete"], "destructive"),
    (["label", "list", "abc"], ["label", "list"], "write"),
    (["pipeline", "list"], ["pipeline", "list"], "read"),
    (["pipeline", "run", "multi-format", "--notebook", "abc"], ["pipeline", "run"], "destructive"),
    (["usage", "--json"], ["usage"], "read"),
    (["login", "--check"], ["login"], "read"),
    (["login"], ["login"], "auth_private"),
    (["share", "public", "abc"], ["share", "public"], "publish"),
    (["--ai"], [], "read"),
    (["source", "--help"], ["source"], "read"),
    (["notebook", "delete", "--help"], ["notebook", "delete"], "read"),
])
def test_cli_effects_and_shapes(real_catalog, argv, path, effect):
    result = classify_cli_argv(argv, real_catalog)
    assert result["command_path"] == path
    assert result["effect"] == effect


@pytest.mark.parametrize("argv", [
    ["notebook", "bogus"], ["notebook", "list", "--execute-shell"],
    ["notebook", "list", ";", "rm"], ["--debug", "notebook", "list"],
    ["notebook", "list", "--profile"], ["source", "add", "abc", "--text", "`whoami`"],
    ["login", "--file", "cookies.txt"], ["notebook", "delete"],
    ["studio", "status", "abc", "--limit", "not-an-int"],
])
def test_cli_rejects_unknown_flags_shell_and_private_auth(real_catalog, argv):
    with pytest.raises(ValueError):
        classify_cli_argv(argv, real_catalog)


def test_cli_multiple_source_options_remain_literal_and_valid(real_catalog):
    result = classify_cli_argv(["source", "add", "abc", "--url", "https://one.example", "--url", "https://two.example"], real_catalog)
    assert result["effect"] == "write"
    assert result["parameters"]["url"] == ["https://one.example", "https://two.example"]


@pytest.mark.parametrize("name,args", [
    ("source_add", {"source_type": "shell"}),
    ("studio_create", {"artifact_type": "shell"}),
    ("download_artifact", {"artifact_type": "shell"}),
    ("export_artifact", {"export_type": "shell"}),
    ("research_start", {"mode": "shell"}),
])
def test_mcp_unknown_subtypes_are_rejected(name, args):
    with pytest.raises(ValueError):
        classify_mcp_operation(name, args)


def test_cli_policy_never_mutates_inventory(real_catalog):
    original = copy.deepcopy(real_catalog)
    classify_cli_argv(["source", "add", "abc", "--url", "https://one.example"], real_catalog)
    assert real_catalog == original


def test_all_155_commands_have_a_policy_without_callback_execution(real_catalog):
    seen = set()
    for row in real_catalog:
        argv = list(row["path"])
        for param in row["params"]:
            if not param["required"]:
                continue
            value = param["choices"][0] if param["choices"] else ("1" if "Int" in param["type_name"] else "example")
            if not param["argument"]:
                argv.append(param["opts"][0])
            argv.append(value)
        result = classify_cli_argv(argv, real_catalog)
        assert result["effect"] in {"read", "inference", "write", "destructive", "publish", "download", "auth_private"}
        seen.add(tuple(result["command_path"]))
    assert len(seen) == 155


def test_real_inventory_does_not_read_profiles_or_connect_to_network():
    checkout = Path("/home/marceloclaro/projetos/gemini-notebook-mcp-cli-core/src")
    if not checkout.is_dir():
        pytest.skip("Checkout pinado ausente.")
    code = """
import socket
from notebooklm_tools.core.auth import AuthManager
def forbidden(*args, **kwargs):
    raise AssertionError('Inventário tentou acessar rede ou credenciais')
socket.socket.connect = forbidden
AuthManager.load_profile = forbidden
from integrations.gemini_notebook_catalog import cli_inventory
assert len(cli_inventory()) == 155
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(checkout)
    subprocess.run([os.sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=30, check=True)


@pytest.mark.parametrize("argv,path,effect", [
    (["nlm", "login", "--check"], ["login"], "read"),
    (["nlm", "notebook", "list", "--json"], ["notebook", "list"], "read"),
    (["nlm", "doctor"], ["doctor"], "read"),
    (["nlm", "--help"], [], "read"),
    (["nlm"], [], "read"),
])
def test_fixed_nlm_executable_prefix_is_supported(real_catalog, argv, path, effect):
    operation = classify_cli_argv(argv, real_catalog)
    assert operation["command_path"] == path
    assert operation["effect"] == effect


@pytest.mark.parametrize("argv", [
    ["notebooklm-mcp"], ["nlm", "server", "--transport", "stdio"],
    ["nlm", "mcp", "run"], ["bash", "-c", "nlm notebook list"],
    ["nlm", "--debug", "notebook", "list"],
])
def test_server_and_arbitrary_boot_commands_cannot_be_captured(real_catalog, argv):
    with pytest.raises(ValueError):
        classify_cli_argv(argv, real_catalog)


@pytest.mark.parametrize("argv", [["nlm", "chat", "start", "--help"], ["nlm", "login", "--help"]])
def test_help_for_interactive_commands_remains_noninteractive(real_catalog, argv):
    operation = classify_cli_argv(argv, real_catalog)
    assert operation["effect"] == "read"
    assert operation["interactive"] is False


@pytest.mark.parametrize("name,args", [
    ("batch", {"action": "query", "unknown_field": True}),
    ("pipeline", {"action": "run", "unknown_field": True}),
    ("batch", {"action": "studio", "artifact_type": "shell"}),
])
def test_unknown_composed_operation_fields_cannot_hide_effects(name, args):
    with pytest.raises(ValueError):
        classify_mcp_operation(name, args)


def test_skill_destination_metadata_covers_twelve_original_targets():
    assert len(SKILL_DESTINATIONS) == 12
    assert {"opencode", "codex", "hermes", "antigravity", "gemini-cli"} <= set(SKILL_DESTINATIONS)


def test_profiles_and_short_download_directory_are_preserved_as_metadata(real_catalog):
    profile = classify_cli_argv(["nlm", "login", "profile", "list"], real_catalog)
    assert profile["effect"] == "read"
    download = classify_cli_argv(["nlm", "download", "all", "abc", "-d", "nested"], real_catalog)
    assert download["effect"] == "download"
    assert download["parameters"]["output_dir"] == "nested"
