# -*- coding: utf-8 -*-
"""
Metacognitive Interconnect MCP Server
=====================================
Expõe a camada MCI (MetaBus, Blackboard, Reflexion, Memory) como um servidor MCP.
Permite que o OpenCode CLI, Antigravity e agentes interajam com o Global Workspace.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import sys
import json
import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger("mci-mcp-server")
logger.setLevel(logging.WARNING)

# Adiciona o root do projeto ao path para imports relativos funcionarem se rodado standalone
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mci.metabus import metabus
from mci.blackboard import blackboard

# Simula a estrutura do MCP SDK (assumindo que será rodado no contexto do ecossistema)
MCP_PROTOCOL_VERSION = "2024-11-05"
MCP_SERVER_VERSION = "1.0.0"


class SimpleMCPServer:
    """Implementação leve de servidor MCP via stdio."""

    def __init__(self, name: str, version: str = MCP_SERVER_VERSION):
        self.name = name
        self.version = version
        self.tools = {}

    def register_tool(self, name: str, description: str, schema: Dict, handler: callable):
        self.tools[name] = {
            "description": description,
            "schema": schema,
            "handler": handler
        }

    @staticmethod
    def _error(message: str, code: int) -> Dict[str, Any]:
        """Cria um erro de resultado MCP sem lançar exceções ao transporte."""
        return {
            "isError": True,
            "error": {"code": code, "message": message},
            "content": [{"type": "text", "text": message}],
        }

    def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna o handshake mínimo esperado por clientes MCP."""
        return {
            "protocolVersion": params.get("protocolVersion", MCP_PROTOCOL_VERSION),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": self.name, "version": self.version},
        }

    async def handle_request(self, req: Dict) -> Dict:
        """Processa uma requisição MCP e retorna somente o resultado da operação.

        O envelope JSON-RPC é responsabilidade de :meth:`run_stdio`, mantendo
        a compatibilidade histórica deste método assíncrono com os testes e
        consumidores internos do MCI.
        """
        if not isinstance(req, dict):
            return self._error(
                "A requisição MCP deve ser um objeto JSON.",
                -32600,
            )

        method = req.get("method")
        params = req.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return self._error(
                "Os parâmetros da requisição MCP devem ser um objeto JSON.",
                -32602,
            )

        if method == "initialize":
            return self._initialize(params)

        if method == "ping":
            return {}

        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": name,
                        "description": info["description"],
                        "inputSchema": info["schema"]
                    }
                    for name, info in self.tools.items()
                ]
            }

        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if not isinstance(tool_name, str) or not tool_name:
                return self._error(
                    "O nome da ferramenta deve ser uma string não vazia.",
                    -32602,
                )
            if not isinstance(tool_args, dict):
                return self._error(
                    "Os argumentos da ferramenta devem ser um objeto JSON.",
                    -32602,
                )

            info = self.tools.get(tool_name)
            if info is None:
                return self._error("Tool não encontrada", -32602)

            try:
                # Executa de forma síncrona para simplificar; handlers assíncronos
                # também são aceitos sem alterar o contrato síncrono existente.
                result = info["handler"](tool_args)
                if hasattr(result, "__await__"):
                    result = await result
                if isinstance(result, dict) and result.get("_mcp_error") is True:
                    message = result.get("message", "Erro na execução da tool")
                    return self._error(str(message), -32602)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False),
                        }
                    ]
                }
            except Exception as e:
                return self._error(f"Erro na execução da tool: {str(e)}", -32000)

        return self._error(f"Método não suportado: {method}", -32601)

    async def run_stdio(self):
        """Executa o transporte JSON-RPC stdio sem responder notificações.

        Linhas inválidas ou valores JSON que não sejam objetos são descartados
        com aviso no stderr, pois não possuem um ``id`` ao qual responder.
        O retorno normal ao encontrar EOF mantém o código de saída zero.
        """
        loop = asyncio.get_running_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        try:
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        except (OSError, RuntimeError) as exc:
            logger.warning("Não foi possível conectar o stdin do MCP: %s", exc)
            return

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                raw_line = line.decode("utf-8") if isinstance(line, bytes) else line
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                req = json.loads(raw_line)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning("JSON inválido recebido no MCP: %s", e)
                continue
            except Exception as e:
                logger.warning("Erro ao ler a entrada MCP: %s", e)
                continue

            if not isinstance(req, dict):
                logger.warning("Entrada MCP ignorada: esperava-se um objeto JSON")
                continue

            # Uma notificação não tem resposta JSON-RPC, inclusive quando id é
            # explicitamente nulo. Requests com id 0 ou string vazia são válidas.
            if "id" not in req or req.get("id") is None:
                continue

            request_id = req["id"]
            try:
                resp = await self.handle_request(req)
                response_obj = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": resp,
                }
            except Exception as exc:
                # O loop não deve vazar rastreamento de pilha para uma falha
                # inesperada de handler; preserve a resposta da request.
                logger.warning("Erro ao processar request MCP: %s", exc)
                response_obj = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": str(exc)},
                }

            try:
                sys.stdout.write(
                    json.dumps(response_obj, ensure_ascii=False) + "\n"
                )
                sys.stdout.flush()
            except (BrokenPipeError, OSError):
                return

# Instancia o servidor
mci_server = SimpleMCPServer("metacognitive-interconnect")

# --- Ferramentas MCP ---

def mci_register_agent(args: Dict[str, Any]) -> Dict[str, Any]:
    """Registra um agente no Blackboard (A2A Agent Card)."""
    metabus.publish("agent.register", args, source_agent="mcp_client")
    return {"status": "success", "message": f"Agente {args.get('name')} registrado."}

def mci_post_task(args: Dict[str, Any]) -> Dict[str, Any]:
    """Posta uma tarefa no Blackboard."""
    metabus.publish("task.post", args, source_agent="mcp_client")
    return {"status": "success", "message": "Tarefa postada no Blackboard."}

def mci_get_memory(args: Dict[str, Any]) -> Dict[str, Any]:
    """Recupera contexto da memória metacognitiva compartilhada."""
    limit = args.get("limit", 5)
    topic = args.get("topic")
    
    res = {"episodic": metabus.memory.get_recent_context(limit)}
    if topic:
        res["semantic_lessons"] = metabus.memory.extract_lessons(topic)
    return res

def mci_get_blackboard_state(args: Dict[str, Any]) -> Dict[str, Any]:
    """Retorna o estado atual do Blackboard."""
    return {
        "agents": [card.to_dict() for card in blackboard.registry.values()],
        "tasks": {tid: t.status for tid, t in blackboard.tasks.items()}
    }

# --- Registro de Ferramentas ---

mci_server.register_tool(
    name="mci_register_agent",
    description="Registra um agente no Blackboard declarando suas capacidades (Agent Card A2A).",
    schema={
        "type": "object",
        "properties": {
            "agent_id": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "capabilities": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["agent_id", "name", "capabilities"]
    },
    handler=mci_register_agent
)

mci_server.register_tool(
    name="mci_post_task",
    description="Posta uma tarefa no Blackboard para que agentes se voluntariem.",
    schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string"},
            "description": {"type": "string"},
            "required_capabilities": {"type": "array", "items": {"type": "string"}},
            "context": {"type": "object"}
        },
        "required": ["description"]
    },
    handler=mci_post_task
)

mci_server.register_tool(
    name="mci_get_memory",
    description="Recupera memória metacognitiva compartilhada (Global Workspace).",
    schema={
        "type": "object",
        "properties": {
            "limit": {"type": "integer"},
            "topic": {"type": "string"}
        }
    },
    handler=mci_get_memory
)

mci_server.register_tool(
    name="mci_get_blackboard_state",
    description="Obtém o estado atual dos agentes e tarefas no Blackboard.",
    schema={"type": "object", "properties": {}},
    handler=mci_get_blackboard_state
)

if __name__ == "__main__":
    asyncio.run(mci_server.run_stdio())
