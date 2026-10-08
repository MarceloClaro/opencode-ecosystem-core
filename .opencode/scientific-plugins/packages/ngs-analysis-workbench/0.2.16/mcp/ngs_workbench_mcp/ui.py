"""Serve the bundled React app and its MCP metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any

PLAN_REVIEW_RESOURCE_URI = "ui://ngs-analysis-workbench/plan-review.html"
RUN_STATUS_RESOURCE_URI = "ui://ngs-analysis-workbench/run-status.html"
LEGACY_RUN_REVIEW_RESOURCE_URI = "ui://ngs-analysis-workbench/run-review.html"
APP_MIME_TYPE = "text/html;profile=mcp-app"
RUN_REVIEW_HTML_PATH = Path(__file__).resolve().parents[1] / "mcp-inline.html"


def plan_tool_meta() -> dict[str, Any]:
    """Mount the passive review card for one immutable execution plan."""
    return _inline_tool_meta(
        invoking="Preparing an execution plan…",
        invoked="Immutable execution plan is ready for review.",
        resource_uri=PLAN_REVIEW_RESOURCE_URI,
    )


def run_tool_meta() -> dict[str, Any]:
    """Mount the read-only workflow receipt after native plan approval."""
    return _inline_tool_meta(
        invoking="Revalidating the approved plan…",
        invoked="Approved plan request completed.",
        resource_uri=RUN_STATUS_RESOURCE_URI,
    )


def _inline_tool_meta(
    *,
    invoking: str,
    invoked: str,
    resource_uri: str,
) -> dict[str, Any]:
    return {
        "ui": {
            "resourceUri": resource_uri,
            "visibility": ["model"],
        },
        "ui/resourceUri": resource_uri,
        "openai/outputTemplate": resource_uri,
        "openai/toolInvocation/invoking": invoking,
        "openai/toolInvocation/invoked": invoked,
    }


def model_tool_meta() -> dict[str, Any]:
    """Keep state-changing tools unavailable to embedded apps."""
    return {"ui": {"visibility": ["model"]}}


def inline_read_tool_meta() -> dict[str, Any]:
    """Allow a Workbench inline receipt to refresh its agent-owned run."""
    return {"ui": {"visibility": ["model", "app"]}}


def resource_meta(
    *,
    fullscreen: bool,
    prefers_border: bool,
    clipboard_write: bool = False,
    widget_accessible: bool = False,
) -> dict[str, Any]:
    """Keep each self-contained app disconnected from external origins."""
    csp = {"connectDomains": [], "resourceDomains": [], "frameDomains": []}
    permissions = {"clipboardWrite": {}} if clipboard_write else None
    return {
        "ui": {
            "csp": csp,
            "supportsFullscreen": fullscreen,
            "prefersBorder": prefers_border,
            **({"permissions": permissions} if permissions is not None else {}),
        },
        "openai/widgetCSP": csp,
        "openai/widgetSupportsFullscreen": fullscreen,
        **({"openai/widgetAccessible": True} if widget_accessible else {}),
    }


def read_run_review_html() -> str:
    """Read the compact single-file plan review app produced by the frontend build."""
    if not RUN_REVIEW_HTML_PATH.is_file():
        raise FileNotFoundError(
            "NGS run review app is not built: "
            f"{RUN_REVIEW_HTML_PATH}. Run npm run build from the plugin root."
        )
    return RUN_REVIEW_HTML_PATH.read_text(encoding="utf-8")
