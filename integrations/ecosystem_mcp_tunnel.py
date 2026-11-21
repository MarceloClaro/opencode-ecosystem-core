"""R1222/R1257: discovery e fronteira fail-closed do túnel completo.

stdout do filho passa por correlação e filtro. O MCP separado de status não
é alterado. Concessão de autorização por MCP não existe nesta fronteira.
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
import threading
from collections.abc import Awaitable, Callable
from typing import Any

from integrations.tunnel_tool_policy import (
    CORE_TOOL_NAMES, READ_TOOLS, PolicyDenied, ToolPolicy, canonical, strict_json,
)

CHILD_MODULE = 'integrations.ecosystem_mcp'
DISCOVER_METHOD = 'server/discover'
SUPPORTED_VERSION = '2025-11-25'
SERVER_NAME = 'ecosystem-network'
SERVER_VERSION = '1.28.1'
CAPABILITIES = {'tools': {'listChanged': False}}
Send = Callable[[str], Awaitable[None]]


def make_discover_result(request_id: Any) -> dict[str, Any]:
    return {'jsonrpc': '2.0', 'id': request_id, 'result': {
        'resultType': 'complete', 'supportedVersions': [SUPPORTED_VERSION],
        'capabilities': dict(CAPABILITIES),
        'instructions': (
            'Servidor MCP 2025-11-25; tools/list e tools/call sob política local. '
            'Efeitos exigem params._meta.authorization={grant_id,spec_id,scope} '
            'correspondente a grant privado local de uso único. '
            'Não há concessão de autorização por MCP.'),
        '_meta': {'io.modelcontextprotocol.serverInfo': {
            'name': SERVER_NAME, 'version': SERVER_VERSION}},
        'ttlMs': 0, 'cacheScope': 'private'}}


def is_discover_request(payload: Any) -> bool:
    return (isinstance(payload, dict)
            and payload.get('method') == DISCOVER_METHOD and 'id' in payload)


class TunnelBridge:
    """Uma instância por sessão, compartilhada pelos dois fluxos stdio."""

    def __init__(self, policy: ToolPolicy | None = None):
        self.policy = policy or ToolPolicy()
        self.pending: dict[str, tuple[Any, str]] = {}
        self.sequence = 0
        self.lock = threading.RLock()

    async def _error(self, rid, send, code=-32602):
        result = canonical({'jsonrpc': '2.0', 'id': rid, 'error': {
            'code': code, 'message': 'Mensagem negada pela política local do túnel.'}})
        if send is not None:
            await send(result + '\n')
        return result

    async def process_line(self, line: str, send_to_child: Send,
                           send_to_client: Send | None = None):
        rid = None
        has_id = True
        try:
            payload = strict_json(line)
            if not isinstance(payload, dict):
                raise PolicyDenied()
            has_id = 'id' in payload
            rid = payload.get('id')
            if (set(payload) - {'jsonrpc', 'id', 'method', 'params'}
                    or payload.get('jsonrpc') != '2.0'):
                raise PolicyDenied()
            if has_id and (type(rid) not in (str, int)
                           or isinstance(rid, str) and len(rid) > 128):
                raise PolicyDenied()
            method = payload.get('method')
            params = payload.get('params', {})
            if not isinstance(method, str) or not isinstance(params, dict):
                raise PolicyDenied()
            if not has_id:
                if method == 'notifications/initialized' and not params:
                    await send_to_child(canonical(payload) + '\n')
                # Chamadas, cancelamentos e callbacks sem id não são repassados.
                return None
            with self.lock:
                if any(type(original) is type(rid) and original == rid
                       for original, _ in self.pending.values()):
                    raise PolicyDenied()
                if method == DISCOVER_METHOD:
                    response = canonical(make_discover_result(rid))
                    if send_to_client is not None:
                        await send_to_client(response + '\n')
                    return response
                if len(self.pending) >= 256:
                    raise PolicyDenied()
                if method == 'tools/call':
                    if (set(params) - {'name', 'arguments', '_meta'}
                            or not {'name', 'arguments'} <= params.keys()):
                        raise PolicyDenied()
                    name, args = params['name'], params['arguments']
                    if not isinstance(name, str) or not isinstance(args, dict):
                        raise PolicyDenied()
                    meta = params.get('_meta', {})
                    if not isinstance(meta, dict) or set(meta) - {'authorization'}:
                        raise PolicyDenied()
                    # Consumo durável precede envio; falha do filho não reabilita.
                    self.policy.authorize(name, args, meta.get('authorization'))
                    payload['params'] = {'name': name, 'arguments': args}
                elif method in {'tools/list', 'ping'}:
                    if params:
                        raise PolicyDenied()
                elif method == 'initialize':
                    if (set(params) - {'protocolVersion', 'capabilities', 'clientInfo'}
                            or not {'protocolVersion', 'capabilities', 'clientInfo'} <= params.keys()):
                        raise PolicyDenied()
                    if (params['protocolVersion'] != SUPPORTED_VERSION
                            or not isinstance(params['capabilities'], dict)
                            or not isinstance(params['clientInfo'], dict)):
                        raise PolicyDenied()
                    # Sampling/elicitation não são capacidades desta fronteira.
                    payload['params'] = {**params, 'capabilities': {}}
                else:
                    raise PolicyDenied()
                self.sequence += 1
                internal = f'tunnel-{self.sequence}'
                self.pending[internal] = (rid, method)
                payload['id'] = internal
            try:
                await send_to_child(canonical(payload) + '\n')
            except (OSError, ValueError):
                with self.lock:
                    self.pending.pop(internal, None)
                return await self._error(rid, send_to_client, -32603)
            return None
        except (OSError, ValueError, TypeError, KeyError, RecursionError):
            if has_id:
                return await self._error(rid, send_to_client)
            return None

    async def process_child_line(self, line: str, send_to_client: Send):
        try:
            payload = strict_json(line)
            if not isinstance(payload, dict) or payload.get('jsonrpc') != '2.0':
                return
            internal = payload.get('id')
            if not isinstance(internal, str):
                return
            with self.lock:
                pending = self.pending.pop(internal, None)
            if pending is None:
                return
            rid, method = pending
            if (set(payload) - {'jsonrpc', 'id', 'result', 'error'}
                    or ('result' in payload) == ('error' in payload)):
                return await self._error(rid, send_to_client, -32603)
            if 'error' in payload:
                # Erros upstream podem incluir comandos/argumentos sensíveis.
                return await self._error(rid, send_to_client, -32603)
            result = payload['result']
            if method == 'tools/list':
                if (not isinstance(result, dict) or set(result) != {'tools'}
                        or not isinstance(result['tools'], list)):
                    return await self._error(rid, send_to_client, -32603)
                tools = result['tools']
                names = [t.get('name') if isinstance(t, dict) else None for t in tools]
                if (any(not isinstance(n, str) for n in names)
                        or len(names) != len(set(names))):
                    return await self._error(rid, send_to_client, -32603)
                retained = []
                for tool in tools:
                    name = tool['name']
                    if self.policy.visible(name):
                        projected = {k: v for k, v in tool.items() if k in {
                            'name', 'title', 'description', 'inputSchema', 'outputSchema'}}
                        projected['annotations'] = {
                            'readOnlyHint': name in READ_TOOLS,
                            'destructiveHint': name not in READ_TOOLS,
                            'openWorldHint': name not in READ_TOOLS}
                        if name not in READ_TOOLS:
                            projected['description'] = projected.get('description', '') + (
                                '\nExige params._meta.authorization={grant_id,spec_id,scope} '
                                'de uso único, criado localmente pelo operador.')
                        retained.append(projected)
                result = {'tools': retained}
            elif method == 'initialize':
                if (not isinstance(result, dict)
                        or result.get('protocolVersion') != SUPPORTED_VERSION):
                    return await self._error(rid, send_to_client, -32603)
                result = {**result, 'capabilities': dict(CAPABILITIES),
                          'instructions': make_discover_result(rid)['result']['instructions']}
            await send_to_client(canonical({'jsonrpc': '2.0', 'id': rid, 'result': result}) + '\n')
        except (OSError, ValueError, TypeError, KeyError, RecursionError):
            return


async def process_line(line: str, send_to_child: Send,
                       send_to_client: Send | None = None) -> str | None:
    """Compatibilidade unitária; main mantém uma instância por sessão."""
    return await TunnelBridge().process_line(line, send_to_child, send_to_client)


def main() -> int:
    session = TunnelBridge()
    child = subprocess.Popen(
        [sys.executable, '-B', '-m', CHILD_MODULE], cwd=session.policy.root,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1)
    output_lock = threading.Lock()

    async def send_to_client(line):
        with output_lock:
            sys.stdout.write(line)
            sys.stdout.flush()

    def filtered_stdout():
        try:
            for line in child.stdout:
                asyncio.run(session.process_child_line(line, send_to_client))
        except (BrokenPipeError, ValueError):
            return

    worker = threading.Thread(target=filtered_stdout, name='r1257-filtered-stdout', daemon=True)
    worker.start()

    async def send_to_child(line):
        child.stdin.write(line)
        child.stdin.flush()

    try:
        for line in sys.stdin:
            asyncio.run(session.process_line(line, send_to_child, send_to_client))
    except (BrokenPipeError, KeyboardInterrupt):
        pass
    finally:
        try:
            child.stdin.close()
        except (BrokenPipeError, ValueError):
            pass
        try:
            code = child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                code = child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                code = child.wait()
        worker.join(timeout=5)
    return code or 0


if __name__ == '__main__':
    raise SystemExit(main())
