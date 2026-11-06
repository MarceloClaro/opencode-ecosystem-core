"""R1061 — MCP curado do storage-operator (7 ferramentas)."""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from . import approvals, drive, inventory, manifest, policy

TOOL_NAMES = frozenset({
    "storage_status", "storage_report", "storage_scan",
    "drive_plan", "drive_upload", "drive_verify", "storage_purge",
})
_READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False, openWorldHint=False)


def _safe(fn, *args, **kwargs) -> dict:
    try:
        return fn(*args, **kwargs)
    except (approvals.ApprovalError, manifest.ManifestError,
            policy.StorageDenied, drive.PurgeError) as exc:
        return {"ok": False, "error": {"code": exc.code, "message": exc.reason}}


def _plan(config: policy.StorageConfig, root: str | None) -> dict:
    target = policy.validate_root(config, root or config.allowed_roots[0])
    data = manifest.build_manifest(config, target)
    state = Path(config.state_dir).expanduser() / "manifests"
    state.mkdir(parents=True, exist_ok=True)
    path = state / f"{data['manifest_sha256']}.json"
    manifest.write_manifest(path, data)
    return {"ok": True, "manifest_path": str(path),
            "manifest_sha256": data["manifest_sha256"],
            "root": data["root"], "remote_path": data["remote_path"],
            "totals": data["totals"],
            "files": [{"relpath": f["relpath"], "size": f["size"],
                       "upload": f["upload"], "delete": f["delete"],
                       "sensitive": f["sensitive"], "reason": f["reason"]}
                      for f in data["files"]],
            "excluded": data["excluded"]}


def create_server() -> FastMCP:
    server = FastMCP("storage-operator")

    @server.tool(name="storage_status", annotations=_READ)
    def storage_status() -> dict:
        """Mostra raízes, remote e presença do rclone; não lê conteúdo."""
        config = policy.load_config()
        return {"ok": True, "roots": list(config.allowed_roots),
                "drive_remote": config.drive_remote,
                "rclone": bool(__import__("shutil").which("rclone")),
                "backend": "rclone", "external_validation": False}

    @server.tool(name="storage_report", annotations=_READ)
    def storage_report() -> dict:
        """Relata uso e espaço livre das raízes autorizadas."""
        return {"ok": True, **inventory.report(policy.load_config())}

    @server.tool(name="storage_scan", annotations=_READ)
    def storage_scan(root: str | None = None) -> dict:
        """Inventaria arquivos, extensões e candidatos; não altera nada."""
        return _safe(inventory.scan, policy.load_config(), root)

    @server.tool(name="drive_plan", annotations=_READ)
    def drive_plan(root: str | None = None) -> dict:
        """Cria manifesto com SHA-256 e pasta remota planejada; não envia."""
        return _safe(_plan, policy.load_config(), root)

    @server.tool(name="drive_upload", annotations=_WRITE)
    def drive_upload(manifest_path: str, approval_token: str) -> dict:
        """Envia o manifesto via rclone copy com checksum; exige aprovação."""
        return _safe(drive.upload, policy.load_config(), manifest_path, approval_token)

    @server.tool(name="drive_verify", annotations=_READ)
    def drive_verify(manifest_path: str) -> dict:
        """Confere o remoto com rclone check; não apaga nada."""
        return _safe(drive.verify, policy.load_config(), manifest_path)

    @server.tool(name="storage_purge", annotations=_WRITE)
    def storage_purge(manifest_path: str, approval_token: str) -> dict:
        """Apaga somente arquivos de manifesto verificado, com aprovação."""
        return _safe(drive.purge, policy.load_config(), manifest_path, approval_token)

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
