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
from typing import Dict, Any, List

# Adiciona o root do projeto ao path para imports relativos funcionarem se rodado standalone
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mci.metabus import metabus
from mci.blackboard import blackboard
from mci.reflexion import reflexion_engine

# Simula a estrutura do MCP SDK (assumindo que será rodado no contexto do ecossistema)
class SimpleMCPServer:
    """Implementação leve de servidor MCP via stdio."""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        
    def register_tool(self, name: str, description: str, schema: Dict, handler: callable):
        self.tools[name] = {
            "description": description,
            "schema": schema,
            "handler": handler
        }
        
    async def handle_request(self, req: Dict) -> Dict:
        method = req.get("method")
        params = req.get("params", {})
        
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
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name in self.tools:
                try:
                    # Executa de forma síncrona para simplificar, em prod seria await
                    result = self.tools[tool_name]["handler"](tool_args)
                    return {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    }
                except Exception as e:
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Erro na execução da tool: {str(e)}"}]
                    }
            return {"isError": True, "content": [{"type": "text", "text": "Tool não encontrada"}]}
            
        return {"isError": True, "content": [{"type": "text", "text": "Método não suportado"}]}

    async def run_stdio(self):
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        writer = sys.stdout
        
        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                req = json.loads(line.decode('utf-8'))
                
                # Responde JSON-RPC
                resp = await self.handle_request(req)
                response_obj = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": resp
                }
                writer.write(json.dumps(response_obj) + "\n")
                writer.flush()
            except Exception as e:
                pass

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
    # Inicializa as instâncias globais
    _ = blackboard
    _ = reflexion_engine
    
    asyncio.run(mci_server.run_stdio())
