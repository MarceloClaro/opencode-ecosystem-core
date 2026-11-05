"""R1065 — MCP local somente leitura para dados científicos."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from . import inspect as inspector, policy

TOOL_NAMES = frozenset({"scientific_status", "scientific_inspect", "scientific_preview"})
_READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)


def create_server() -> FastMCP:
    server = FastMCP("scientific-data")

    @server.tool(name="scientific_status", annotations=_READ)
    def scientific_status() -> dict:
        """Mostra versões de xarray/h5py/rasterio/zarr e formatos suportados."""
        return inspector.status()

    @server.tool(name="scientific_inspect", annotations=_READ)
    def scientific_inspect(path: str) -> dict:
        """Lê metadados de NetCDF/HDF5/Zarr/GeoTIFF sem carregar o arquivo inteiro."""
        config = policy.load_config()
        try:
            return inspector.inspect(config, path)
        except (policy.ScientificDenied, inspector.InspectError) as exc:
            return {"ok": False, "error": {"code": exc.code, "message": exc.message}}

    @server.tool(name="scientific_preview", annotations=_READ)
    def scientific_preview(path: str, variable: str | None = None,
                           selector: dict | None = None, band: int = 1,
                           max_points: int = 2000) -> dict:
        """Mostra estatísticas e uma amostra limitada; nunca despeja o array inteiro."""
        config = policy.load_config()
        try:
            return inspector.preview(config, path, variable=variable, selector=selector,
                                     band=band, max_points=max_points)
        except (policy.ScientificDenied, inspector.InspectError) as exc:
            return {"ok": False, "error": {"code": exc.code, "message": exc.message}}

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
