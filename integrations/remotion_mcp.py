"""R1025 — MCP local read-only para auditoria de projetos Remotion.

As ferramentas não instalam, renderizam, abrem navegador ou acessam a rede.
Elas resumem licença, inspecionam arquivos locais, pré-checam um plano R1024 e
decidem se um comando de shell exige aprovação.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations import remotion_guard


def create_server() -> FastMCP:
    server = FastMCP("remotion-audit")
    local_read = ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, openWorldHint=False
    )

    @server.tool(name="license_scope", annotations=local_read)
    def license_scope(
        entity_type: str,
        employees: int | None = None,
        commercial_use: bool = True,
        resell: bool = False,
    ) -> dict:
        """Resume elegibilidade da Remotion License; não é parecer jurídico."""
        return remotion_guard.license_scope(
            entity_type, employees, commercial_use, resell
        )

    @server.tool(name="project_scan", annotations=local_read)
    def project_scan(path: str) -> dict:
        """Lê package.json, licença, configs e composições; não executa o projeto."""
        return remotion_guard.scan_project(path)

    @server.tool(name="render_preflight", annotations=local_read)
    def render_preflight(
        plan: dict,
        composition_id: str | None = None,
        output_path: str | None = None,
        project_path: str | None = None,
    ) -> dict:
        """Valida o plano R1024 e confere composição/saída; não renderiza."""
        return remotion_guard.render_preflight(
            plan, composition_id, output_path, project_path
        )

    @server.tool(name="command_policy", annotations=local_read)
    def command_policy(
        command: str,
        render_approved: bool = False,
        license_ack: bool = False,
    ) -> dict:
        """Classifica um comando de shell; não executa o comando."""
        return remotion_guard.command_policy(
            command, render_approved, license_ack
        )

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
