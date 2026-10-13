"""MCP stdio do assistente local; nunca inicia inferência externa."""
from __future__ import annotations

from contextlib import redirect_stdout
import os
from pathlib import Path
import sys
from threading import RLock
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

TimeoutArgument = Annotated[float, Field(strict=True, gt=0, le=180, allow_inf_nan=False)] | Literal[""]


def create_mcp_server():
    server = FastMCP("core_rea_local_mcp")
    primary = None
    primary_lock = RLock()

    def action(config, *, retain_provider=False):
        nonlocal primary
        # Uma instância por servidor evita acumular subscrições MetaBus a cada
        # pedido. Inicialização serial; análises continuam canceláveis por pedido.
        with primary_lock:
            if primary is None:
                with redirect_stdout(sys.stderr):
                    from marceloclaro.orchestrator import MarceloClaroOrchestrator
                    primary = MarceloClaroOrchestrator(auto_load_agents=False)
        result = primary.rea_assistant_action(config)
        return result if retain_provider else {key: value for key, value in result.items() if key != "provider_report"}

    annotations = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
    from integrations.execution_control import run_cancellable

    @server.tool(name="core_rea_status", annotations=annotations)
    async def status() -> dict:
        """Confere instalação e isolamento local; prontidão não comprova análise ou inferência."""
        return await run_cancellable(action, {"operation": "status"})

    @server.tool(name="core_rea_inspect", annotations=annotations)
    async def inspect(path: str, kind: Literal["", "auto", "javascript", "native", "dotnet", "html", "plist", "android", "firmware", "elf-layout"] = "auto",
                timeout_seconds: TimeoutArgument = 60, procedure: str = "main") -> dict:
        """Inspeciona alvo local estaticamente em rede privada; retorna achados e recibo local por hash."""
        return await run_cancellable(action, {"operation": "inspect", "path": path, "kind": kind or "auto",
                       "timeout_seconds": 60 if timeout_seconds == "" else timeout_seconds,
                       "procedure": procedure or "main"})

    @server.tool(name="core_rea_explain", annotations=annotations)
    async def explain(receipt_path: str) -> dict:
        """Lê recibo íntegro do diretório local do assistente; conserva evidências e limites."""
        from integrations.rea_assistant import explain_report
        report = await run_cancellable(action, {"operation": "explain", "path": receipt_path}, retain_provider=True)
        return {"report": {key: value for key, value in report.items() if key != "provider_report"},
                "explanation": explain_report(report)}

    @server.tool(name="core_rea_setup", annotations=annotations)
    async def setup(model: str = "modelo-local", model_endpoint: str = "http://127.0.0.1:11434/v1") -> dict:
        """Registra perfis locais Linux/WSL; não altera configuração global nem instala modelos."""
        return await run_cancellable(action, {"operation": "setup", "model": model, "model_endpoint": model_endpoint})

    return server


if __name__ == "__main__":
    workspace = Path(os.environ.get("CORE_REA_WORKSPACE", Path(__file__).resolve().parents[1])).resolve()
    os.environ["CORE_REA_WORKSPACE"] = str(workspace)
    create_mcp_server().run(transport="stdio")
