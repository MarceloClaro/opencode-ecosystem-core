"""MCP R1041 local: quatro ferramentas compactas, sem síntese nem shell livre.

Requer DUBBING_PROJECT_ROOT do operador. Usa o MCP SDK 1.x instalado.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations import dubbing_batch


def create_server(root=None):
    value = root if root is not None else os.environ.get('DUBBING_PROJECT_ROOT')
    if not value or not Path(value).is_dir():
        raise ValueError('DUBBING_PROJECT_ROOT must be an existing operator-selected directory')
    root = Path(value).absolute()
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError('symlink root not allowed')
    server = FastMCP('dubbing-local')
    read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    write = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False,
                            idempotentHint=True)

    def compact(result):
        encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
        if len(encoded) > 8000:
            return {'status': result.get('status', 'detail_in_local_artifact'),
                    'artifact': result.get('artifact', result.get('run_dir')),
                    'truncated': True, 'reason': 'read targeted local artifact for details'}
        return result

    @server.tool(annotations=read)
    def dubbing_status() -> dict:
        """Contagens e impedimentos do lote; confere hashes, não aprova áudio."""
        return compact(dubbing_batch.status(root))

    @server.tool(annotations=write)
    def dubbing_prepare() -> dict:
        """Prepara/retoma rascunhos locais de todas as partes. NÃO dubla ou renderiza."""
        return compact(dubbing_batch.prepare(root))

    @server.tool(annotations=read)
    def dubbing_part(part_id: str) -> dict:
        """Consulta IDs e bloqueios de uma parte, sem retornar a transcrição inteira."""
        if not dubbing_batch.ID.fullmatch(part_id):
            raise ValueError('invalid part ID')
        return compact(dubbing_batch.part(root, part_id))

    @server.tool(annotations=read)
    def dubbing_audit_pilot() -> dict:
        """Reconfere WAVs do piloto e ASR histórico; não é escuta humana."""
        return compact(dubbing_batch.audit_pilot(root))

    return server


if __name__ == '__main__':
    create_server().run(transport='stdio')
