"""R1090: fachada stdio de diagnóstico para conexão autorizada do ChatGPT.

Não cria túnel, credenciais ou endpoint público. O cliente deve conectar este
processo separadamente; sua existência não comprova ativação no ChatGPT Chat.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations.ecosystem_mcp import ecosystem_integration_status


def create_server() -> FastMCP:
    """Registra somente o diagnóstico existente, sem alterar o MCP completo."""
    server = FastMCP("opencode-core-status")
    server.add_tool(
        ecosystem_integration_status,
        annotations=ToolAnnotations(
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
