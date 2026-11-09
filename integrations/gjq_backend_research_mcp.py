"""MCP somente leitura para pesquisa de backends GJQ/Tiangong (R1104).

Este servidor não tem chave, não acessa a rede e não submete jobs. Ele organiza
o catálogo dos 19 recursos, resolve nomes/aliases, recomenda backend e produz
um plano de proveniência. Para estado ao vivo e submissão, use `gjq-runtime`.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations.gjq_backend_registry import (
    backend_limits,
    calibration_snapshot,
    catalog,
    compare_plan,
    provenance_template,
    research_plan,
    resolve_backend,
    select_backends,
    snapshot_summary,
)

FAMILIES = ("hardware", "cpu", "gpu", "mps", "npu")


def _validate_family(family: str | None) -> None:
    if family is not None and family not in FAMILIES:
        raise ValueError(f"family deve ser um de {list(FAMILIES)}")


def create_server() -> FastMCP:
    server = FastMCP("gjq-backend-research")
    readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)

    @server.tool(name="gjq_backend_catalog", annotations=readonly)
    def gjq_backend_catalog(
        family: str | None = None,
        include_maintenance: bool = True,
        only_online: bool = False,
    ) -> dict:
        """Lista os 19 recursos do snapshot; não acessa a nuvem."""
        _validate_family(family)
        return {
            **catalog(family=family, include_maintenance=include_maintenance,
                      only_online=only_online),
            "executed": False,
            "network_access": False,
            "api_key_required": False,
        }

    @server.tool(name="gjq_backend_snapshot", annotations=readonly)
    def gjq_backend_snapshot() -> dict:
        """Resume famílias, status e maior capacidade do snapshot."""
        return {
            **snapshot_summary(),
            "executed": False,
            "network_access": False,
        }

    @server.tool(name="gjq_resolve_backend", annotations=readonly)
    def gjq_resolve_backend(name: str) -> dict:
        """Resolve ID, nome exibido, nome de API ou alias; pode ser ambíguo."""
        matches = resolve_backend(name)
        return {
            "query": name,
            "matches": matches,
            "total": len(matches),
            "ambiguous": len(matches) > 1,
            "executed": False,
            "network_access": False,
            "note": (
                "Nome de API não verificado deve ser confirmado com "
                "gjq_list_backends antes de qualquer submissão."
            ),
        }

    @server.tool(name="gjq_select_backend", annotations=readonly)
    def gjq_select_backend(
        family: str | None = None,
        min_qubits: int = 1,
        status: str | None = "online",
        limit: int = 10,
    ) -> dict:
        """Seleciona backends por família, qubits e status do snapshot."""
        _validate_family(family)
        rows = select_backends(family=family, min_qubits=min_qubits,
                               status=status, limit=limit)
        return {
            "total": len(rows),
            "backends": rows,
            "executed": False,
            "network_access": False,
            "note": "Status do snapshot; confirme com gjq_list_backends.",
        }

    @server.tool(name="gjq_research_plan", annotations=readonly)
    def gjq_research_plan(
        goal: str,
        num_qubits: int,
        depth: int = 4,
        shots: int = 1024,
        hardware_allowed: bool = False,
        prefer: str | None = None,
        needs_single_amplitude: bool = False,
        needs_partial_amplitude: bool = False,
    ) -> dict:
        """Recomenda backend e protocolo; não executa nem reserva fila."""
        if needs_single_amplitude and needs_partial_amplitude:
            raise ValueError("escolha single_amplitude ou partial_amplitude, não ambos")
        return research_plan(
            goal=goal,
            num_qubits=num_qubits,
            depth=depth,
            shots=shots,
            hardware_allowed=hardware_allowed,
            prefer=prefer,
            needs_single_amplitude=needs_single_amplitude,
            needs_partial_amplitude=needs_partial_amplitude,
        )

    @server.tool(name="gjq_compare_plan", annotations=readonly)
    def gjq_compare_plan(
        num_qubits: int,
        shots: int = 1024,
        include_hardware: bool = False,
    ) -> dict:
        """Monta o plano simulador versus hardware, sem executar."""
        return compare_plan(num_qubits=num_qubits, shots=shots,
                            include_hardware=include_hardware)

    @server.tool(name="gjq_backend_limits", annotations=readonly)
    def gjq_backend_limits() -> dict:
        """Limites por família e restrições conhecidas."""
        return backend_limits()

    @server.tool(name="gjq_provenance_template", annotations=readonly)
    def gjq_provenance_template() -> dict:
        """Campos obrigatórios para registrar uma pesquisa reproduzível."""
        return provenance_template()

    @server.tool(name="gjq_calibration_snapshot", annotations=readonly)
    def gjq_calibration_snapshot() -> dict:
        """T1/T2 do snapshot; não substitui a calibração ao vivo."""
        return calibration_snapshot()

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
