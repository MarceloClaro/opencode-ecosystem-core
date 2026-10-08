from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import create_autospec, patch

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PLUGIN_ROOT / "mcp"
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from ngs_app_mcp import app as global_app  # noqa: E402
from ngs_workbench_daemon import server as daemon_server  # noqa: E402
from ngs_workbench_mcp import app, runs, ui  # noqa: E402


def _write_fake_codex_python(executable: Path) -> None:
    fake_python_source = (
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "arguments = sys.argv[1:]\n"
        "print(json.dumps({'arguments': arguments, 'executable': sys.argv[0]}))\n"
    )
    executable.parent.mkdir(parents=True)
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "arguments = sys.argv[1:]\n"
        "with Path(os.environ['FAKE_PYTHON_LOG']).open('a', encoding='utf-8') as log:\n"
        "    log.write(json.dumps(arguments) + '\\n')\n"
        "if arguments[:2] == ['-m', 'venv']:\n"
        "    python = Path(arguments[-1]) / 'bin' / 'python'\n"
        "    python.parent.mkdir(parents=True, exist_ok=True)\n"
        f"    python.write_text({fake_python_source!r}, encoding='utf-8')\n"
        "    python.chmod(0o755)\n"
        "elif arguments[:2] == ['-m', 'pip']:\n"
        "    print('Installing Workbench requirements')\n"
        "else:\n"
        "    raise SystemExit(f'unexpected fake Python arguments: {arguments!r}')\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)


class McpUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tools = {tool.name: tool for tool in asyncio.run(app.mcp.list_tools())}
        cls.resources = {
            str(resource.uri): resource for resource in asyncio.run(app.mcp.list_resources())
        }
        cls.app_tools = {tool.name: tool for tool in asyncio.run(global_app.mcp.list_tools())}
        cls.app_resources = {
            str(resource.uri): resource for resource in asyncio.run(global_app.mcp.list_resources())
        }

    def test_full_workbench_is_the_only_app_global_entrypoint(self) -> None:
        tool = self.app_tools["open_ngs_workbench"]
        meta = tool.meta

        self.assertEqual(tool.title, "NGS Analysis Workbench")
        self.assertEqual(meta["ui"]["resourceUri"], global_app.APP_RESOURCE_URI)
        self.assertEqual(meta["ui"]["visibility"], ["app"])
        self.assertTrue(meta["ui"]["supportsFullscreen"])
        self.assertEqual(meta["openai/ui"], {"entrypoints": [{"type": "global"}]})
        self.assertNotIn("openai/outputTemplate", meta)
        self.assertNotIn("ui/resourceUri", meta)

        global_entrypoints = [
            tool.name
            for tool in [*self.tools.values(), *self.app_tools.values()]
            if tool.meta.get("openai/ui", {}).get("entrypoints") == [{"type": "global"}]
        ]
        self.assertEqual(global_entrypoints, ["open_ngs_workbench"])

        resource_meta = self.app_resources[global_app.APP_RESOURCE_URI].meta
        self.assertTrue(resource_meta["ui"]["supportsFullscreen"])
        self.assertEqual(
            resource_meta["ui"]["permissions"],
            {"clipboardWrite": {}},
        )

        plan_meta = self.resources[ui.PLAN_REVIEW_RESOURCE_URI].meta
        self.assertNotIn("permissions", plan_meta["ui"])
        self.assertTrue(plan_meta["openai/widgetAccessible"])

        run_meta = self.resources[ui.RUN_STATUS_RESOURCE_URI].meta
        self.assertNotIn("permissions", run_meta["ui"])
        self.assertTrue(run_meta["openai/widgetAccessible"])

    def test_workflow_planner_mounts_only_the_passive_plan_app(self) -> None:
        self.assertNotIn("plan_workflow", self.tools)
        for name in ("plan_nextflow", "plan_snakemake"):
            with self.subTest(tool=name):
                meta = self.tools[name].meta
                self.assertEqual(meta["ui"]["resourceUri"], ui.PLAN_REVIEW_RESOURCE_URI)
                self.assertEqual(meta["ui"]["visibility"], ["model"])
                self.assertEqual(meta["openai/outputTemplate"], ui.PLAN_REVIEW_RESOURCE_URI)
                self.assertNotIn("openai/widgetAccessible", meta)

    def test_workflow_planners_expose_only_engine_specific_configuration(self) -> None:
        nextflow = self.tools["plan_nextflow"].inputSchema["properties"]
        snakemake = self.tools["plan_snakemake"].inputSchema["properties"]

        self.assertTrue({"workflow_id", "params_file", "profile"}.issubset(nextflow))
        self.assertTrue({"config_file", "cores"}.issubset(snakemake))
        self.assertTrue(
            {"engine", "config_file", "cores", "revision", "workflow_source"}.isdisjoint(nextflow)
        )
        self.assertTrue(
            {
                "engine",
                "params_file",
                "profile",
                "revision",
                "workflow_parameters",
                "workflow_source",
            }.isdisjoint(snakemake)
        )
        self.assertTrue(nextflow["params_file"]["description"])
        self.assertTrue(snakemake["config_file"]["description"])

    def test_execute_plan_is_identity_only_and_mounts_run_receipt(self) -> None:
        tool = self.tools["execute_plan"]
        self.assertEqual(
            set(tool.inputSchema["properties"]),
            {"plan_name", "plan_id", "plan_checksum"},
        )
        self.assertEqual(set(tool.inputSchema["required"]), set(tool.inputSchema["properties"]))
        self.assertEqual(tool.meta["ui"]["resourceUri"], ui.RUN_STATUS_RESOURCE_URI)
        self.assertEqual(tool.meta["ui"]["visibility"], ["model"])
        self.assertNotIn("openai/widgetAccessible", tool.meta)
        self.assertNotIn("start_nfcore_run", self.tools)
        self.assertNotIn("start_snakemake_run", self.tools)

    def test_workflow_catalog_exposes_entry_and_version_lifecycle(self) -> None:
        save = self.tools["save_workflow"]
        self.assertEqual(
            set(save.inputSchema["required"]), {"workflow_id", "name", "engine", "source"}
        )
        self.assertEqual(
            set(save.inputSchema["properties"]),
            {"workflow_id", "name", "engine", "source", "description"},
        )
        self.assertTrue(save.inputSchema["properties"]["source"].get("oneOf"))
        self.assertNotIn("remove_workflow", self.tools)
        self.assertTrue(
            {
                "update_workflow",
                "list_workflow_versions",
                "activate_workflow_version",
                "archive_workflow",
                "restore_workflow",
            }.issubset(self.tools)
        )

    def test_workbench_tools_are_model_only(self) -> None:
        for name in (
            "list_workflows",
            "get_runtime_environment",
            "check_nextflow_readiness",
            "check_snakemake_readiness",
            "list_ngs_runs",
            "get_ngs_run",
            "update_ngs_run_analysis_summary",
        ):
            with self.subTest(tool=name):
                meta = self.tools[name].meta
                self.assertEqual(meta, {"ui": {"visibility": ["model"]}})
        self.assertNotIn("open_ngs_workbench", self.tools)
        self.assertNotIn("list_compute_targets", self.tools)
        self.assertEqual(
            self.tools["observe_ngs_run"].meta,
            {"ui": {"visibility": ["model", "app"]}},
        )

    def test_global_app_tools_are_app_only(self) -> None:
        self.assertEqual(
            set(self.app_tools),
            {
                "open_ngs_workbench",
                "list_workflows",
                "list_compute_target_summaries",
                "list_ngs_runs",
                "list_ngs_run_lineages",
                "get_ngs_run",
                "observe_ngs_run",
                "get_ngs_run_report",
            },
        )
        for tool in self.app_tools.values():
            with self.subTest(tool=tool.name):
                self.assertEqual(tool.meta["ui"]["visibility"], ["app"])

    def test_global_app_history_routes_lineage_queries_and_filters(self) -> None:
        with patch(
            "ngs_workbench_mcp.runs.list_registry_run_lineages",
            return_value={"ok": True, "runs": []},
        ) as list_lineages:
            asyncio.run(global_app.mcp.call_tool("list_ngs_run_lineages", {"limit": 12}))
            list_lineages.assert_called_once_with(limit=12)

        filters = {
            "first_run_id": "run-a",
            "limit": 200,
        }
        with patch(
            "ngs_workbench_mcp.runs.list_registry_runs",
            return_value={"ok": True, "runs": []},
        ) as list_runs:
            asyncio.run(global_app.mcp.call_tool("list_ngs_runs", filters))
            list_runs.assert_called_once_with(**filters, statuses=None, binding=None, pipeline=None)

    def test_compute_target_list_projects_only_app_safe_inventory(self) -> None:
        safe_target = {
            "target_id": "research-slurm",
            "title": "Research Slurm",
            "provider": "ngs-compute",
            "controller_transport": "ssh",
            "executor": "slurm",
            "workspace_access": "remote_filesystem",
            "description": "Run a workflow controller through SSH.",
            "workspace_root": "/shared/rosalind",
            "executor_configuration": {"partition": "genomics"},
        }
        raw_target = {
            **safe_target,
            "config_hash": "sha256:private-identity",
            "host_access": {"alias": "research-login"},
        }
        with patch.object(daemon_server, "_list_targets", return_value={"targets": [raw_target]}):
            result = daemon_server.list_target_summaries()

        self.assertEqual(result, {"count": 1, "targets": [safe_target]})

    def test_global_app_reads_only_the_daemon_owned_summary(self) -> None:
        with patch.object(
            daemon_server,
            "list_target_summaries",
            return_value={"count": 0, "targets": []},
        ) as list_summaries:
            result = global_app.list_compute_target_summaries()

        self.assertEqual(result, {"count": 0, "targets": []})
        list_summaries.assert_called_once_with()

    def test_global_app_lists_runs_across_the_registry(self) -> None:
        expected = {"count": 0, "runs": []}
        list_runs = create_autospec(runs.list_registry_runs, return_value=expected)
        with patch.object(runs, "list_registry_runs", list_runs):
            result = global_app.list_ngs_runs()

        self.assertEqual(result, expected)
        list_runs.assert_called_once_with(
            statuses=None,
            binding=None,
            pipeline=None,
            first_run_id=None,
            limit=50,
        )

    def test_run_cancellation_is_not_visible_to_embedded_apps(self) -> None:
        self.assertEqual(
            self.tools["cancel_ngs_run"].meta,
            {"ui": {"visibility": ["model"]}},
        )

    def test_all_ui_resources_are_registered(self) -> None:
        self.assertEqual(set(self.app_resources), {global_app.APP_RESOURCE_URI})
        self.assertNotIn(global_app.APP_RESOURCE_URI, self.resources)
        self.assertIn(ui.PLAN_REVIEW_RESOURCE_URI, self.resources)
        self.assertIn(ui.RUN_STATUS_RESOURCE_URI, self.resources)
        self.assertTrue(global_app.ngs_app().lstrip().lower().startswith("<!doctype html>"))
        self.assertIn(ui.LEGACY_RUN_REVIEW_RESOURCE_URI, self.resources)

    def test_legacy_run_review_resource_preserves_the_read_only_receipt(self) -> None:
        legacy_resource = self.resources[ui.LEGACY_RUN_REVIEW_RESOURCE_URI]
        run_resource = self.resources[ui.RUN_STATUS_RESOURCE_URI]
        legacy_contents = list(
            asyncio.run(app.mcp.read_resource(ui.LEGACY_RUN_REVIEW_RESOURCE_URI))
        )
        run_contents = list(asyncio.run(app.mcp.read_resource(ui.RUN_STATUS_RESOURCE_URI)))

        self.assertEqual(legacy_resource.meta, run_resource.meta)
        self.assertNotIn("permissions", legacy_resource.meta["ui"])
        self.assertTrue(legacy_resource.meta["openai/widgetAccessible"])
        self.assertEqual(len(legacy_contents), 1)
        self.assertEqual(legacy_contents[0].content, run_contents[0].content)
        self.assertIn("Execution blocked", legacy_contents[0].content)

    def test_bundled_inline_resource_renders_execution_failures_as_blocked(self) -> None:
        inline_resource = ui.read_run_review_html()

        self.assertIn("Execution blocked", inline_resource)
        self.assertIn(
            "Refresh the runtime environment, then create and review a new execution plan.",
            inline_resource,
        )

    def test_only_execute_plan_uses_native_prompt_approval(self) -> None:
        config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        app_server = config["mcpServers"]["ngs-app"]
        server = config["mcpServers"]["ngs-analysis-workbench"]

        self.assertEqual(app_server["args"], ["ngs_app_mcp"])
        self.assertEqual(app_server["default_tools_approval_mode"], "auto")
        self.assertNotIn("tools", app_server)
        self.assertEqual(server["default_tools_approval_mode"], "auto")
        self.assertEqual(server["tools"], {"execute_plan": {"approval_mode": "prompt"}})

    def test_mcp_server_prefers_bundled_python_over_uv_and_reuses_ready_environment(self) -> None:
        config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8"))
        server = config["mcpServers"]["ngs-analysis-workbench"]

        with tempfile.TemporaryDirectory() as temporary:
            user_home = Path(temporary) / "home"
            bundled_python = (
                user_home
                / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
            )
            _write_fake_codex_python(bundled_python)
            user_bin = user_home / ".local" / "bin"
            user_bin.mkdir(parents=True)
            for name in ("uv", "python3"):
                executable = user_bin / name
                executable.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
                executable.chmod(0o755)
            fake_python_log = Path(temporary) / "python.jsonl"
            codex_home = Path(temporary) / "codex-home"
            environment = {
                **os.environ,
                "CODEX_HOME": str(codex_home),
                "FAKE_PYTHON_LOG": str(fake_python_log),
                "HOME": str(user_home),
                "PATH": str(user_bin),
                "NGS_ANALYSIS_WORKBENCH_UV": str(user_bin / "uv"),
            }
            cold_result = subprocess.run(
                [server["command"], *server["args"]],
                cwd=MCP_ROOT,
                env=environment,
                capture_output=True,
                check=True,
                text=True,
            )
            warm_result = subprocess.run(
                [server["command"], "ngs_compute_mcp"],
                cwd=MCP_ROOT,
                env=environment,
                capture_output=True,
                check=True,
                text=True,
            )
            python_launches = [
                json.loads(line)
                for line in fake_python_log.read_text(encoding="utf-8").splitlines()
            ]
            expected_venv = (
                codex_home
                / "cache/ngs-analysis-workbench/venvs"
                / (MCP_ROOT / "PLUGIN_VENV_VERSION").read_text(encoding="utf-8").strip()
            )
            expected_python = expected_venv / "bin" / "python"

            self.assertTrue((expected_venv / ".ready").is_file())
            self.assertEqual(len(python_launches), 2)
            self.assertTrue(cold_result.stderr)
            self.assertEqual(
                json.loads(cold_result.stdout),
                {"arguments": ["-m", "ngs_workbench_mcp"], "executable": str(expected_python)},
            )
            self.assertEqual(
                json.loads(warm_result.stdout),
                {"arguments": ["-m", "ngs_compute_mcp"], "executable": str(expected_python)},
            )

            environment.pop("HOME")
            environment.pop("NGS_ANALYSIS_WORKBENCH_UV")
            alternate_codex_home = Path(temporary) / "codex-home-without-home"
            environment["CODEX_HOME"] = str(alternate_codex_home)
            runtime_dependencies = bundled_python.parents[2]
            environment["PATH"] = (
                f"{user_bin}:{runtime_dependencies / 'bin' / 'override'}:/usr/bin:/bin"
            )
            without_home_result = subprocess.run(
                [server["command"], *server["args"]],
                cwd=MCP_ROOT,
                env=environment,
                capture_output=True,
                check=True,
                text=True,
            )
            self.assertEqual(
                json.loads(without_home_result.stdout)["arguments"],
                ["-m", "ngs_workbench_mcp"],
            )

            system_python = Path(temporary) / "system-bin" / "python3"
            _write_fake_codex_python(system_python)
            environment["HOME"] = str(Path(temporary) / "home-without-bundled-python")
            environment["CODEX_HOME"] = str(Path(temporary) / "codex-home-system-python")
            environment["PATH"] = f"{system_python.parent}:{user_bin}:/usr/bin:/bin"
            system_python_result = subprocess.run(
                [server["command"], *server["args"]],
                cwd=MCP_ROOT,
                env=environment,
                capture_output=True,
                check=True,
                text=True,
            )
            self.assertEqual(
                json.loads(system_python_result.stdout)["arguments"],
                ["-m", "ngs_workbench_mcp"],
            )

    def test_preparation_is_nested_in_workflow_planner(self) -> None:
        for name in ("plan_nextflow", "plan_snakemake"):
            with self.subTest(tool=name):
                preparation_schema = self.tools[name].inputSchema["properties"]["preparation"]
                self.assertIn("anyOf", preparation_schema)
        self.assertNotIn("plan_setup", self.tools)
        self.assertNotIn("list_public_demo_setups", self.tools)
        self.assertNotIn("plan_public_demo_setup", self.tools)
        self.assertNotIn("execute_setup_plan", self.tools)

    def test_inline_plan_stays_static_and_only_receipts_poll_run_status(self) -> None:
        source = (PLUGIN_ROOT / "src" / "inline" / "RunReviewApp.tsx").read_text(encoding="utf-8")
        client = (PLUGIN_ROOT / "src" / "inline" / "client.ts").read_text(encoding="utf-8")
        self.assertEqual(source.count("<button"), 1)
        self.assertIn("onClick={onRefresh}", source)
        self.assertIn('client.call("observe_ngs_run"', source)
        self.assertNotIn("lookupPlannedRun", source)
        self.assertNotIn("restoredPlanRun", source)
        self.assertLess(source.index("if (plan) {"), source.index("if (run) {"))
        self.assertIn('"Refresh"', source)
        self.assertNotIn("Approve and start", source)
        self.assertIn("callServerTool", client)
        self.assertNotIn('client.call("execute_plan"', source)

    def test_full_workbench_has_no_plan_or_execution_path(self) -> None:
        hook = (PLUGIN_ROOT / "src" / "hooks" / "useNgsWorkbench.ts").read_text(encoding="utf-8")
        client_contract = (PLUGIN_ROOT / "src" / "mcp" / "ngs.ts").read_text(encoding="utf-8")

        self.assertNotIn("plan_nextflow", hook + client_contract)
        self.assertNotIn("plan_snakemake", hook + client_contract)
        self.assertNotIn("execute_plan", hook + client_contract)
        self.assertFalse((PLUGIN_ROOT / "src" / "components" / "RunConfiguration.tsx").exists())

    def test_default_prompts_fit_the_app_server_contract(self) -> None:
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        prompts = manifest["interface"]["defaultPrompt"]

        self.assertGreater(len(prompts), 0)
        self.assertLessEqual(len(prompts), 3)
        self.assertTrue(all(prompt.strip() for prompt in prompts))
        self.assertTrue(all(len(prompt) <= 128 for prompt in prompts))


if __name__ == "__main__":
    unittest.main()
