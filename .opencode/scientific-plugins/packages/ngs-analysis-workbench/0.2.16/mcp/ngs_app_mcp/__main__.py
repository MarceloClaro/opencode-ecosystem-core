"""Console entrypoint for the NGS App MCP server."""

from .app import mcp


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
