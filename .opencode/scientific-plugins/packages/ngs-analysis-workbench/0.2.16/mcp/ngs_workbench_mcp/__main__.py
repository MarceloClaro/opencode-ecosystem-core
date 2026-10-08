"""Console entrypoint for the NGS Analysis Workbench MCP server."""

from .app import mcp
from .workflows.defaults import bootstrap_default_workflows


def main() -> None:
    bootstrap_default_workflows()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
