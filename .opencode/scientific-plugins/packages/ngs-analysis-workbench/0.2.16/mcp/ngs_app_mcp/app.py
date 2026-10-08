"""Serve the global NGS shell and its app-only read contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

APP_RESOURCE_URI = "ui://ngs-app/main.html"
APP_MIME_TYPE = "text/html;profile=mcp-app"
APP_HTML_PATH = Path(__file__).resolve().parents[1] / "mcp-app.html"

mcp = FastMCP("ngs-app")


def _app_tool_meta() -> dict[str, Any]:
    return {"ui": {"visibility": ["app"]}}


def _entrypoint_meta() -> dict[str, Any]:
    return {
        "ui": {
            "resourceUri": APP_RESOURCE_URI,
            "visibility": ["app"],
            "supportsFullscreen": True,
        },
        "openai/widgetAccessible": True,
        "openai/ui": {"entrypoints": [{"type": "global"}]},
        "com.openai": {"ui": {"entrypoints": [{"type": "global"}]}},
        "openai/toolInvocation/invoking": "Opening NGS Analysis Workbench…",
        "openai/toolInvocation/invoked": "NGS Analysis Workbench is open.",
    }


@mcp.resource(
    APP_RESOURCE_URI,
    name="ngs-app",
    title="NGS Analysis Workbench",
    description="Browse durable NGS runs, workflows, and configured compute targets.",
    mime_type=APP_MIME_TYPE,
    meta={
        "ui": {
            "csp": {"connectDomains": [], "resourceDomains": [], "frameDomains": []},
            "supportsFullscreen": True,
            "prefersBorder": False,
            "permissions": {"clipboardWrite": {}},
        },
        "openai/widgetCSP": {
            "connectDomains": [],
            "resourceDomains": [],
            "frameDomains": [],
        },
        "openai/widgetSupportsFullscreen": True,
        "openai/widgetAccessible": True,
    },
)
def ngs_app() -> str:
    """Return the bundled global React app."""
    if not APP_HTML_PATH.is_file():
        raise FileNotFoundError(
            f"NGS app is not built: {APP_HTML_PATH}. Run npm run build from the plugin root."
        )
    return APP_HTML_PATH.read_text(encoding="utf-8")


@mcp.tool(
    title="NGS Analysis Workbench",
    description="Open the read-only workspace for NGS runs, workflows, and compute targets.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_entrypoint_meta(),
    structured_output=True,
)
def open_ngs_workbench() -> dict[str, Any]:
    """Open the global NGS application."""
    return {"ok": True}


@mcp.tool(
    title="List NGS workflows for the app",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def list_workflows(engine: Literal["nextflow", "snakemake"] | None = None) -> dict[str, Any]:
    """Return the workflow catalog used by the global app."""
    from ngs_workbench_mcp.workflows import catalog_store

    return catalog_store.list_workflows(engine)


@mcp.tool(
    title="List compute target summaries for the app",
    description="List app-safe configuration facts without workflow-readiness claims.",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def list_compute_target_summaries() -> dict[str, Any]:
    """Return the daemon-owned, app-safe compute inventory."""
    from ngs_workbench_daemon import server

    return server.list_target_summaries()


@mcp.tool(
    title="List NGS runs for the app",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def list_ngs_runs(
    statuses: list[str] | None = None,
    binding: str | None = None,
    pipeline: str | None = None,
    first_run_id: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return bounded durable run summaries for the global app."""
    from ngs_workbench_mcp import runs

    return runs.list_registry_runs(
        statuses=statuses,
        binding=binding,
        pipeline=pipeline,
        first_run_id=first_run_id,
        limit=limit,
    )


@mcp.tool(
    title="List NGS run lineages for the app",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def list_ngs_run_lineages(limit: int = 20) -> dict[str, Any]:
    """Return recent lineages without allowing attempts to consume the group limit."""
    from ngs_workbench_mcp import runs

    return runs.list_registry_run_lineages(limit=limit)


@mcp.tool(
    title="Get an NGS run for the app",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def get_ngs_run(registry_run_id: str) -> dict[str, Any]:
    """Return one local durable run projection for the global app."""
    from ngs_workbench_mcp import runs

    return runs.get_registry_run(registry_run_id)


@mcp.tool(
    title="Observe an NGS run for the app",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def observe_ngs_run(registry_run_id: str) -> dict[str, Any]:
    """Return current lifecycle and bounded execution evidence for the global app."""
    from ngs_workbench_mcp import runs

    return runs.observe_registry_run(registry_run_id)


@mcp.tool(
    title="Get an NGS run report for the app",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
    meta=_app_tool_meta(),
    structured_output=True,
)
def get_ngs_run_report(registry_run_id: str) -> dict[str, Any]:
    """Return the local completed-result projection for the global app."""
    from ngs_workbench_mcp import runs

    return runs.get_registry_run_report(registry_run_id)
