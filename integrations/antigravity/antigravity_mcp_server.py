#!/usr/bin/env python3
"""
ANTIGRAVITY MCP SERVER v1.0
============================
Servidor MCP que expõe as capacidades do Antigravity (Google DeepMind
Advanced Agentic Coding) como ferramentas utilizáveis pelo OpenCode Ecosystem.

Este servidor implementa o protocolo MCP (Model Context Protocol) e age como
ponte entre o runtime do OpenCode e o Antigravity, traduzindo chamadas de
ferramenta em instruções estruturadas que o Antigravity pode executar.

Ferramentas expostas:
  - antigravity_delegate_task: Delega qualquer tarefa ao Antigravity
  - antigravity_generate_image: Solicita geração de imagem
  - antigravity_browser_action: Solicita automação de browser
  - antigravity_web_search: Solicita pesquisa web com síntese
  - antigravity_read_url: Solicita leitura de URL específica
  - antigravity_run_subagent: Solicita execução de subagente paralelo
  - antigravity_get_bridge_state: Retorna estado atual da ponte
  - antigravity_query_rag: Solicita ao Antigravity que consulte o MASWOS RAG local

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import json
import sys
import os
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AntigravityMCP] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("antigravity-mcp")

# ============================================================
# Constantes
# ============================================================

MCP_SERVER_VERSION = "1.0.0"
STATE_DIR = Path(__file__).parent.parent / ".evolve"
BRIDGE_STATE_FILE = STATE_DIR / "antigravity-bridge-state.json"
TASK_LOG_FILE = STATE_DIR / "antigravity-task-log.jsonl"
OBSERVABILITY_LOG = STATE_DIR / "antigravity-observability.jsonl"

# Tipos de tarefa suportados
TASK_TYPES = {
    "delegate": "Delegação genérica de tarefa ao Antigravity",
    "image": "Geração de imagem via generate_image",
    "browser": "Automação de browser via browser_subagent",
    "search": "Pesquisa web via search_web",
    "url": "Leitura de URL via read_url_content",
    "subagent": "Execução de subagente paralelo",
    "analysis": "Análise aprofundada com contexto completo",
    "orchestration": "Orquestração multi-agente",
    "rag": "Consulta inteligente ao banco de dados RAG local",
}

# ============================================================
# Gerenciamento de Estado
# ============================================================

def ensure_state_dir() -> None:
    """Garante que o diretório de estado existe."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_bridge_state() -> dict:
    """Carrega o estado atual da ponte Antigravity."""
    ensure_state_dir()
    if BRIDGE_STATE_FILE.exists():
        try:
            return json.loads(BRIDGE_STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Erro ao carregar estado: {e}")
    return {
        "version": MCP_SERVER_VERSION,
        "totalDelegated": 0,
        "totalCompleted": 0,
        "totalFailed": 0,
        "successRate": 1.0,
        "healthScore": 100,
        "lastSync": None,
        "pendingQueue": [],
        "tasks": [],
    }


def save_bridge_state(state: dict) -> None:
    """Persiste o estado da ponte."""
    ensure_state_dir()
    BRIDGE_STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def log_task(task: dict) -> None:
    """Registra tarefa no log de observabilidade."""
    ensure_state_dir()
    entry = json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server": "antigravity-mcp-v1",
        **task,
    }, ensure_ascii=False) + "\n"
    try:
        with open(TASK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except IOError as e:
        logger.error(f"Erro ao registrar tarefa: {e}")


def generate_task_id() -> str:
    """Gera ID único para tarefa."""
    timestamp = int(time.time() * 1000)
    short_uuid = str(uuid.uuid4()).replace("-", "")[:8]
    return f"anti-{timestamp:x}-{short_uuid}"


# ============================================================
# Formatadores de Prompt Antigravity
# ============================================================

def format_delegation_prompt(
    task_type: str,
    prompt: str,
    context: Optional[str] = None,
    priority: str = "normal",
    task_id: Optional[str] = None,
) -> str:
    """Formata prompt estruturado para delegação ao Antigravity."""
    task_id = task_id or generate_task_id()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Carregar contexto do ecossistema
    eco_state = {}
    eco_state_file = Path(__file__).parent.parent / ".evolve" / "ecosystem-state.json"
    if eco_state_file.exists():
        try:
            eco_state = json.loads(eco_state_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    health = eco_state.get("overallHealth", "N/A")
    mcp_count = len(eco_state.get("mcps", {}))
    last_sync = eco_state.get("lastSync", "N/A")

    context_section = f"\n### Contexto Adicional\n{context}\n" if context else ""

    return f"""## [DELEGAÇÃO OPENCODE → ANTIGRAVITY]
**ID Tarefa**: {task_id}
**Tipo**: {task_type}
**Prioridade**: {priority}
**Timestamp**: {timestamp}
**Servidor MCP**: antigravity-mcp-v{MCP_SERVER_VERSION}

### Contexto do Ecossistema OpenCode
- Saúde do ecossistema: {health}%
- MCPs ativos: {mcp_count}
- Última sincronização: {last_sync}
- Modelo: big-pickle (OpenCode Zen)
- Timezone: UTC-3 (Brasil)

### Tarefa
{prompt}
{context_section}
### Formato de Retorno Esperado
- Resultado em português brasileiro formal (zero caracteres CJK)
- Métricas de execução quando disponíveis
- Caminho de artefato gerado (se aplicável)
- Prefixo `[ERRO ANTIGRAVITY]:` em caso de falha
"""


def format_image_prompt(description: str, style: str = "professional", context: Optional[str] = None) -> str:
    """Formata prompt para geração de imagem."""
    style_map = {
        "professional": "design profissional, limpo, moderno",
        "diagram": "diagrama técnico, setas, caixas organizadas, fundo branco",
        "ui": "interface de usuário moderna, dark mode, glassmorphism",
        "academic": "figura acadêmica, estilo científico, escalas e legendas",
        "infographic": "infográfico colorido, ícones, dados visuais",
    }
    style_desc = style_map.get(style, style)

    base = f"""Gere uma imagem com as seguintes especificações:

**Descrição**: {description}
**Estilo**: {style_desc}
**Qualidade**: Alta resolução, adequada para publicação

**Requisitos técnicos**:
- Texto em português brasileiro
- Sem caracteres CJK ou asiáticos
- Cores harmoniosas e profissionais
- Tipografia legível
"""
    if context:
        base += f"\n**Contexto adicional**: {context}\n"
    return base


def format_browser_prompt(
    url: str,
    action: str,
    task_name: str,
    recording: bool = True,
) -> str:
    """Formata prompt para automação de browser."""
    return f"""Execute a seguinte automação de browser:

**URL inicial**: {url}
**Nome da tarefa**: {task_name}
**Ação a realizar**: {action}
**Gravar sessão**: {"Sim — salvar como WebP animado" if recording else "Não"}

**Instruções**:
1. Abrir o URL indicado
2. Executar a ação especificada
3. Capturar resultado (screenshots ou WebP)
4. Retornar: URL final, resultado da ação, caminho do artefato gravado

**Idioma da interface**: PT-BR preferencial
"""


def format_search_prompt(query: str, depth: str = "summary", sources: int = 5) -> str:
    """Formata prompt para pesquisa web."""
    depth_map = {
        "quick": "resposta rápida com 2-3 fontes",
        "summary": "resumo abrangente com 5 fontes citadas",
        "deep": "análise aprofundada com 10+ fontes e síntese crítica",
        "academic": "pesquisa acadêmica com foco em papers e publicações científicas",
    }
    depth_desc = depth_map.get(depth, depth)

    return f"""Realize pesquisa web sobre:

**Query**: {query}
**Profundidade**: {depth_desc}
**Fontes mínimas**: {sources}

**Formato do resultado**:
1. Resumo principal (2-3 parágrafos)
2. Principais fontes com URLs
3. Data das informações encontradas
4. Lacunas ou incertezas identificadas

**Idioma**: Português brasileiro formal
"""


# ============================================================
# Protocolo MCP — Handlers de Ferramentas
# ============================================================

class AntigravityMCPServer:
    """Servidor MCP que expõe capacidades do Antigravity."""

    def __init__(self):
        self.state = load_bridge_state()
        logger.info(f"AntigravityMCPServer v{MCP_SERVER_VERSION} inicializado")
        logger.info(f"Estado carregado: {self.state.get('totalDelegated', 0)} tarefas históricas")

    def get_tools(self) -> list[dict]:
        """Retorna lista de ferramentas disponíveis no formato MCP."""
        return [
            {
                "name": "antigravity_delegate_task",
                "description": "Delega qualquer tarefa ao Antigravity (Google DeepMind). Use para tarefas que requerem capacidades exclusivas: geração de imagem, browser, pesquisa web, subagentes paralelos.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_type": {
                            "type": "string",
                            "enum": list(TASK_TYPES.keys()),
                            "description": "Tipo da tarefa a delegar",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Descrição detalhada da tarefa em português",
                        },
                        "context": {
                            "type": "string",
                            "description": "Contexto adicional opcional (resultado de etapas anteriores, etc.)",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "normal", "low"],
                            "default": "normal",
                            "description": "Prioridade de execução",
                        },
                    },
                    "required": ["task_type", "prompt"],
                },
            },
            {
                "name": "antigravity_generate_image",
                "description": "Solicita ao Antigravity a geração de uma imagem (diagrama, mockup, UI, figura acadêmica, infográfico).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Descrição detalhada da imagem a gerar",
                        },
                        "style": {
                            "type": "string",
                            "enum": ["professional", "diagram", "ui", "academic", "infographic"],
                            "default": "professional",
                            "description": "Estilo visual da imagem",
                        },
                        "context": {
                            "type": "string",
                            "description": "Contexto do projeto para a imagem",
                        },
                    },
                    "required": ["description"],
                },
            },
            {
                "name": "antigravity_browser_action",
                "description": "Solicita ao Antigravity automação de browser com gravação de sessão em WebP. Ideal para demonstrações, testes E2E e captura de estado de interfaces.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL inicial para navegação",
                        },
                        "action": {
                            "type": "string",
                            "description": "Descrição da ação a realizar no browser",
                        },
                        "task_name": {
                            "type": "string",
                            "description": "Nome descritivo da tarefa (usado no arquivo gravado)",
                        },
                        "recording": {
                            "type": "boolean",
                            "default": True,
                            "description": "Se deve gravar a sessão como WebP animado",
                        },
                    },
                    "required": ["url", "action", "task_name"],
                },
            },
            {
                "name": "antigravity_web_search",
                "description": "Solicita ao Antigravity pesquisa web com síntese de múltiplas fontes. Mais rica que o websearch MCP padrão.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query de pesquisa",
                        },
                        "depth": {
                            "type": "string",
                            "enum": ["quick", "summary", "deep", "academic"],
                            "default": "summary",
                            "description": "Profundidade da pesquisa",
                        },
                        "sources": {
                            "type": "integer",
                            "default": 5,
                            "minimum": 2,
                            "maximum": 20,
                            "description": "Número mínimo de fontes a consultar",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "antigravity_read_url",
                "description": "Solicita ao Antigravity leitura e extração de conteúdo de uma URL específica (sem JS, mais rápido que Playwright).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL a ser lida",
                        },
                        "extract_focus": {
                            "type": "string",
                            "description": "O que extrair da página (ex: 'abstract do paper', 'preços', 'metodologia')",
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "antigravity_get_bridge_state",
                "description": "Retorna o estado atual da ponte OpenCode ↔ Antigravity: tarefas delegadas, taxa de sucesso, saúde da integração.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "antigravity_query_rag",
                "description": "Solicita ao Antigravity que realize uma consulta avançada utilizando o servidor RAG local do OpenCode, sintetizando o resultado.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A pergunta a ser feita ao banco vetorial RAG."
                        },
                        "strategy": {
                            "type": "string",
                            "enum": ["vanilla", "hybrid", "memory", "graph", "crag", "adaptive", "fusion", "hyde", "agentic"],
                            "default": "agentic",
                            "description": "Estratégia de RAG a utilizar (agentic é o roteamento automático)."
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def handle_delegate_task(self, args: dict) -> dict:
        """Processa delegação genérica ao Antigravity."""
        task_id = generate_task_id()
        task_type = args.get("task_type", "delegate")
        prompt = args.get("prompt", "")
        context = args.get("context")
        priority = args.get("priority", "normal")

        formatted_prompt = format_delegation_prompt(
            task_type=task_type,
            prompt=prompt,
            context=context,
            priority=priority,
            task_id=task_id,
        )

        # Registrar no estado
        task_record = {
            "id": task_id,
            "type": task_type,
            "prompt": prompt[:200],
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "formatted",
        }
        self.state["pendingQueue"] = self.state.get("pendingQueue", [])
        self.state["pendingQueue"].append(task_record)
        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)
        log_task({"event": "task.formatted", **task_record})

        logger.info(f"Tarefa {task_id} ({task_type}, {priority}) formatada para delegação")

        return {
            "task_id": task_id,
            "type": task_type,
            "priority": priority,
            "status": "pronto_para_delegacao",
            "antigravity_prompt": formatted_prompt,
            "instrucao": (
                f"Copie o campo 'antigravity_prompt' e envie ao Antigravity. "
                f"ID {task_id} registrado para rastreamento. "
                f"Total histórico: {self.state['totalDelegated']} tarefas."
            ),
        }

    def handle_generate_image(self, args: dict) -> dict:
        """Processa solicitação de geração de imagem."""
        task_id = generate_task_id()
        description = args.get("description", "")
        style = args.get("style", "professional")
        context = args.get("context")

        image_prompt = format_image_prompt(description, style, context)
        delegation_prompt = format_delegation_prompt(
            task_type="image",
            prompt=image_prompt,
            priority="normal",
            task_id=task_id,
        )

        task_record = {
            "id": task_id,
            "type": "image",
            "description": description[:100],
            "style": style,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "formatted",
        }
        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)
        log_task({"event": "image.task.formatted", **task_record})

        return {
            "task_id": task_id,
            "type": "image_generation",
            "style": style,
            "antigravity_prompt": delegation_prompt,
            "instrucao": (
                f"Envie o campo 'antigravity_prompt' ao Antigravity para gerar a imagem. "
                f"O artefato será salvo na pasta de artefatos do Antigravity."
            ),
        }

    def handle_browser_action(self, args: dict) -> dict:
        """Processa solicitação de automação de browser."""
        task_id = generate_task_id()
        url = args.get("url", "")
        action = args.get("action", "")
        task_name = args.get("task_name", "browser_task")
        recording = args.get("recording", True)

        browser_prompt = format_browser_prompt(url, action, task_name, recording)
        delegation_prompt = format_delegation_prompt(
            task_type="browser",
            prompt=browser_prompt,
            priority="high",
            task_id=task_id,
        )

        task_record = {
            "id": task_id,
            "type": "browser",
            "url": url,
            "action": action[:100],
            "recording": recording,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "formatted",
        }
        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)
        log_task({"event": "browser.task.formatted", **task_record})

        return {
            "task_id": task_id,
            "type": "browser_automation",
            "url": url,
            "recording": recording,
            "antigravity_prompt": delegation_prompt,
            "instrucao": (
                f"Envie o campo 'antigravity_prompt' ao Antigravity. "
                f"A sessão será gravada como WebP animado na pasta de artefatos."
            ),
        }

    def handle_web_search(self, args: dict) -> dict:
        """Processa solicitação de pesquisa web."""
        task_id = generate_task_id()
        query = args.get("query", "")
        depth = args.get("depth", "summary")
        sources = args.get("sources", 5)

        search_prompt = format_search_prompt(query, depth, sources)
        delegation_prompt = format_delegation_prompt(
            task_type="search",
            prompt=search_prompt,
            priority="normal",
            task_id=task_id,
        )

        task_record = {
            "id": task_id,
            "type": "search",
            "query": query[:100],
            "depth": depth,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "formatted",
        }
        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)
        log_task({"event": "search.task.formatted", **task_record})

        return {
            "task_id": task_id,
            "type": "web_search",
            "query": query,
            "depth": depth,
            "antigravity_prompt": delegation_prompt,
        }

    def handle_read_url(self, args: dict) -> dict:
        """Processa solicitação de leitura de URL."""
        task_id = generate_task_id()
        url = args.get("url", "")
        extract_focus = args.get("extract_focus", "conteúdo principal")

        prompt = f"""Leia e extraia conteúdo da URL:
**URL**: {url}
**Foco da extração**: {extract_focus}

Retorne:
1. Conteúdo extraído (foco no solicitado)
2. Título da página
3. Data de publicação (se disponível)
4. URL canônica
"""

        delegation_prompt = format_delegation_prompt(
            task_type="url",
            prompt=prompt,
            priority="normal",
            task_id=task_id,
        )

        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)

        return {
            "task_id": task_id,
            "type": "url_read",
            "url": url,
            "extract_focus": extract_focus,
            "antigravity_prompt": delegation_prompt,
        }

    def handle_query_rag(self, args: dict) -> dict:
        """Processa delegação de consulta RAG para o Antigravity."""
        task_id = generate_task_id()
        query = args.get("query", "")
        strategy = args.get("strategy", "agentic")

        prompt = f"""Consulte o sistema RAG do OpenCode Ecosystem para a seguinte questão:
**Query**: {query}
**Estratégia Solicitada**: {strategy}

**Instruções para o Antigravity**:
Você deve utilizar as suas ferramentas internas ou requisições HTTP locais (porta 3003) para acessar a base de conhecimento do OpenCode. 
Analise os resultados do RAG e forneça uma síntese completa e aprofundada, cruzando com o seu próprio conhecimento.
"""

        delegation_prompt = format_delegation_prompt(
            task_type="rag",
            prompt=prompt,
            priority="high",
            task_id=task_id,
        )

        self.state["totalDelegated"] = self.state.get("totalDelegated", 0) + 1
        save_bridge_state(self.state)

        return {
            "task_id": task_id,
            "type": "query_rag",
            "query": query,
            "strategy": strategy,
            "antigravity_prompt": delegation_prompt,
            "instrucao": "Envie o prompt gerado ao Antigravity para que ele processe a consulta RAG e sintetize a resposta."
        }

    def handle_get_bridge_state(self, _args: dict) -> dict:
        """Retorna estado atual da ponte."""
        self.state = load_bridge_state()
        pending = len(self.state.get("pendingQueue", []))
        completed = self.state.get("totalCompleted", 0)
        total = self.state.get("totalDelegated", 0)
        failed = self.state.get("totalFailed", 0)
        success_rate = (completed / total * 100) if total > 0 else 100.0

        return {
            "versao": MCP_SERVER_VERSION,
            "saude": f"{self.state.get('healthScore', 100):.1f}%",
            "total_delegadas": total,
            "total_concluidas": completed,
            "total_falhas": failed,
            "taxa_sucesso": f"{success_rate:.1f}%",
            "fila_pendente": pending,
            "ultima_sincronizacao": self.state.get("lastSync", "N/A"),
            "capacidades": {
                "geracao_imagem": True,
                "automacao_browser": True,
                "pesquisa_web": True,
                "leitura_url": True,
                "subagentes_paralelos": True,
                "criacao_artefatos": True,
            },
            "status_geral": "operacional" if success_rate >= 80 else "degradado" if success_rate >= 50 else "critico",
        }

    def handle_tool_call(self, tool_name: str, arguments: dict) -> Any:
        """Roteador central de chamadas de ferramenta."""
        handlers = {
            "antigravity_delegate_task": self.handle_delegate_task,
            "antigravity_generate_image": self.handle_generate_image,
            "antigravity_browser_action": self.handle_browser_action,
            "antigravity_web_search": self.handle_web_search,
            "antigravity_read_url": self.handle_read_url,
            "antigravity_get_bridge_state": self.handle_get_bridge_state,
            "antigravity_query_rag": self.handle_query_rag,
        }

        handler = handlers.get(tool_name)
        if not handler:
            return {"erro": f"Ferramenta desconhecida: {tool_name}"}

        try:
            start = time.time()
            result = handler(arguments)
            latency_ms = int((time.time() - start) * 1000)
            logger.info(f"Ferramenta {tool_name} executada em {latency_ms}ms")
            return result
        except Exception as e:
            logger.error(f"Erro em {tool_name}: {e}")
            return {"erro": f"Falha na execução de {tool_name}: {str(e)}"}

    # ============================================================
    # Loop MCP Stdio (JSON-RPC 2.0)
    # ============================================================

    def send_response(self, response: dict) -> None:
        """Envia resposta via stdout no formato JSON-RPC."""
        line = json.dumps(response, ensure_ascii=False)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def handle_request(self, request: dict) -> Optional[dict]:
        """Processa uma requisição MCP e retorna a resposta."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "antigravity-mcp-server",
                        "version": MCP_SERVER_VERSION,
                    },
                },
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools()},
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = self.handle_tool_call(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False),
                        }
                    ]
                },
            }

        elif method == "notifications/initialized":
            return None  # Notificação — sem resposta

        else:
            logger.warning(f"Método desconhecido: {method}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Método não encontrado: {method}",
                },
            }

    def run(self) -> None:
        """Loop principal do servidor MCP via stdio."""
        logger.info(f"AntigravityMCPServer v{MCP_SERVER_VERSION} aguardando requisições via stdio...")

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"JSON inválido recebido: {e}")
                continue

            response = self.handle_request(request)
            if response is not None:
                self.send_response(response)


# ============================================================
# Entrypoint
# ============================================================

if __name__ == "__main__":
    ensure_state_dir()
    server = AntigravityMCPServer()
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no servidor: {e}")
        sys.exit(1)
