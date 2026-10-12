# -*- coding: utf-8 -*-
"""
Memory Network Visualizer — Terminal Animado de Memória e Contexto LLM
=======================================================================

Exibe em tempo real como o LLM consulta:
- Memória (nós de documentos, embeddings, chunks)
- Contexto (nós de entidades, relações, conceitos)
- Agentes (nós de skills, orquestrador, ferramentas)
- Fluxo de recuperação (arestas animadas entre nós)

Usa rich para renderização de rede em terminal com:
- Animação de frame-by-frame
- Cores por tipo de nó
- Tamanho relativo à relevância
- Status em tempo real
"""

from __future__ import annotations

import json
import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.table import Table
    from rich.align import Align
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class NodeType(Enum):
    """Tipos de nó na rede."""
    MEMORY = "memoria"           # Chunks, embeddings, documentos
    CONTEXT = "contexto"         # Entidades, relações, conceitos
    AGENT = "agente"             # Skill, orquestrador, ferramenta
    QUERY = "consulta"           # Pergunta do usuário
    RESPONSE = "resposta"        # Resposta gerada


class EdgeType(Enum):
    """Tipos de aresta."""
    RETRIEVAL = "recuperacao"    # Busca de memória
    REASONING = "raciocinio"     # Conexão lógica
    EXECUTION = "execucao"       # Chamada de skill/agente
    REFERENCE = "referencia"     # Citação/evidência


@dataclass
class Node:
    """Nó na rede de memória."""
    id: str
    label: str
    node_type: NodeType
    relevance: float = 0.5       # 0.0 a 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = False
    
    def get_color(self) -> str:
        """Retorna cor ANSI para o tipo de nó."""
        colors = {
            NodeType.MEMORY: "\033[94m",      # Azul
            NodeType.CONTEXT: "\033[92m",     # Verde
            NodeType.AGENT: "\033[93m",       # Amarelo
            NodeType.QUERY: "\033[96m",       # Ciano
            NodeType.RESPONSE: "\033[95m",    # Magenta
        }
        return colors.get(self.node_type, "\033[37m")  # Branco por padrão
    
    def get_symbol(self) -> str:
        """Símbolo visual para o nó."""
        if self.active:
            symbols = {
                NodeType.MEMORY: "◉",
                NodeType.CONTEXT: "●",
                NodeType.AGENT: "⬢",
                NodeType.QUERY: "❓",
                NodeType.RESPONSE: "✓",
            }
        else:
            symbols = {
                NodeType.MEMORY: "○",
                NodeType.CONTEXT: "∘",
                NodeType.AGENT: "⬡",
                NodeType.QUERY: "？",
                NodeType.RESPONSE: "✗",
            }
        return symbols.get(self.node_type, "•")


@dataclass
class Edge:
    """Aresta na rede de memória."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    timestamp: float = field(default_factory=time.time)
    active: bool = False
    
    def get_symbol(self) -> str:
        """Símbolo da aresta."""
        symbols = {
            EdgeType.RETRIEVAL: "→",
            EdgeType.REASONING: "⟿",
            EdgeType.EXECUTION: "⟹",
            EdgeType.REFERENCE: "╌",
        }
        return symbols.get(self.edge_type, "—")


class MemoryNetworkGraph:
    """Grafo de rede de memória."""
    
    def __init__(self, max_nodes: int = 50, max_edges: int = 100):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.event_log: deque = deque(maxlen=20)
        self.active_queries: Set[str] = set()
        
    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: NodeType,
        relevance: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> Node:
        """Adiciona nó ao grafo."""
        if len(self.nodes) >= self.max_nodes:
            # Remove nó mais antigo
            oldest = min(self.nodes.values(), key=lambda n: n.timestamp)
            del self.nodes[oldest.id]
        
        node = Node(
            id=node_id,
            label=label,
            node_type=node_type,
            relevance=relevance,
            metadata=metadata or {}
        )
        self.nodes[node_id] = node
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        weight: float = 1.0
    ) -> Optional[Edge]:
        """Adiciona aresta ao grafo."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        if len(self.edges) >= self.max_edges:
            self.edges.pop(0)
        
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight
        )
        self.edges.append(edge)
        return edge
    
    def activate_node(self, node_id: str, duration: float = 1.0):
        """Ativa um nó por um tempo."""
        if node_id in self.nodes:
            self.nodes[node_id].active = True
            
            def deactivate():
                time.sleep(duration)
                if node_id in self.nodes:
                    self.nodes[node_id].active = False
            
            threading.Thread(target=deactivate, daemon=True).start()
    
    def activate_edge(
        self,
        source_id: str,
        target_id: str,
        duration: float = 0.5
    ):
        """Ativa uma aresta por um tempo."""
        for edge in self.edges:
            if edge.source_id == source_id and edge.target_id == target_id:
                edge.active = True
                
                def deactivate():
                    time.sleep(duration)
                    edge.active = False
                
                threading.Thread(target=deactivate, daemon=True).start()
                break
    
    def log_event(self, event_type: str, message: str):
        """Registra evento na log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.event_log.append(f"[{timestamp}] {event_type}: {message}")


class MemoryNetworkVisualizer:
    """Renderizador de terminal para rede de memória."""
    
    def __init__(self, graph: MemoryNetworkGraph):
        self.graph = graph
        self.console = Console() if HAS_RICH else None
        self.frame_count = 0
        self.running = False
        
    def render_ascii_graph(self) -> str:
        """Renderiza grafo em ASCII art."""
        lines = []
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║           MEMORY NETWORK — LLM CONTEXT RETRIEVAL              ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        
        # Organizar nós por tipo
        nodes_by_type = defaultdict(list)
        for node in self.graph.nodes.values():
            nodes_by_type[node.node_type].append(node)
        
        # Renderizar nós por camada
        y_pos = 3
        for node_type in [NodeType.QUERY, NodeType.MEMORY, NodeType.CONTEXT, NodeType.AGENT, NodeType.RESPONSE]:
            nodes = nodes_by_type.get(node_type, [])
            if not nodes:
                continue
            
            type_label = {
                NodeType.QUERY: "CONSULTA",
                NodeType.MEMORY: "MEMÓRIA",
                NodeType.CONTEXT: "CONTEXTO",
                NodeType.AGENT: "AGENTES",
                NodeType.RESPONSE: "RESPOSTA",
            }[node_type]
            
            lines.append(f"║ {type_label:^62} ║")
            
            for node in nodes[:5]:  # Max 5 nós por tipo
                symbol = node.get_symbol()
                active_marker = "⚡" if node.active else "  "
                relevance_bar = "█" * int(node.relevance * 10) + "░" * (10 - int(node.relevance * 10))
                
                line = f"║  {active_marker} {symbol} {node.label[:30]:<30} [{relevance_bar}] ║"
                lines.append(line)
            
            lines.append("║" + "─" * 62 + "║")
        
        # Eventos recentes
        lines.append("║ EVENTOS RECENTES:                                               ║")
        for event in list(self.graph.event_log)[-3:]:
            lines.append(f"║  {event[:60]:<60} ║")
        
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)
    
    def render_rich_graph(self) -> Optional[Panel]:
        """Renderiza grafo usando rich (se disponível)."""
        if not self.console:
            return None
        
        # Tabela de nós
        table = Table(title="Memory Network State", show_header=True, header_style="bold magenta")
        table.add_column("Tipo", style="cyan")
        table.add_column("Rótulo", style="green")
        table.add_column("Relevância", style="yellow")
        table.add_column("Status", style="red")
        
        for node in list(self.graph.nodes.values())[-10:]:
            status = "🔴 ATIVO" if node.active else "⚪ inativo"
            relevance_bar = "█" * int(node.relevance * 5) + "░" * (5 - int(node.relevance * 5))
            table.add_row(
                node.node_type.value,
                node.label[:30],
                relevance_bar,
                status
            )
        
        return Panel(table, title="[bold]LLM Memory Network[/bold]", expand=False)
    
    def print_frame(self):
        """Imprime um frame da visualização."""
        if self.console and HAS_RICH:
            self.console.clear()
            panel = self.render_rich_graph()
            if panel:
                self.console.print(panel)
        else:
            # Fallback ASCII
            graph_str = self.render_ascii_graph()
            print("\033[2J\033[H")  # Clear screen
            print(graph_str)
        
        self.frame_count += 1
    
    def run_animation(self, fps: int = 2, duration: float = 30.0):
        """Executa animação contínua."""
        self.running = True
        start_time = time.time()
        frame_interval = 1.0 / fps
        
        while self.running and (time.time() - start_time) < duration:
            self.print_frame()
            time.sleep(frame_interval)
        
        self.running = False


class MemoryNetworkSimulator:
    """Simula uma execução de consulta/resposta com rede de memória."""
    
    def __init__(self, graph: MemoryNetworkGraph):
        self.graph = graph
        
    def simulate_query_execution(
        self,
        query: str,
        num_memory_chunks: int = 5,
        num_entities: int = 4,
        num_agents: int = 3
    ):
        """Simula execução de uma consulta."""
        self.graph.log_event("INICIO", f"Consultando: {query}")
        
        # Criar nó de consulta
        query_node = self.graph.add_node(
            f"query_{int(time.time())}",
            query[:30],
            NodeType.QUERY
        )
        self.graph.activate_node(query_node.id, duration=2.0)
        
        # Fase 1: Recuperar memória
        self.graph.log_event("FASE 1", "Buscando chunks de memória...")
        memory_nodes = []
        for i in range(num_memory_chunks):
            mem_node = self.graph.add_node(
                f"mem_{i}_{int(time.time())}",
                f"Chunk {i+1}",
                NodeType.MEMORY,
                relevance=0.8 - i * 0.1
            )
            memory_nodes.append(mem_node)
            self.graph.activate_node(mem_node.id, duration=1.0)
            self.graph.add_edge(query_node.id, mem_node.id, EdgeType.RETRIEVAL)
            time.sleep(0.2)
        
        # Fase 2: Extrair contexto (entidades e relações)
        self.graph.log_event("FASE 2", "Extraindo entidades e contexto...")
        context_nodes = []
        for i in range(num_entities):
            ctx_node = self.graph.add_node(
                f"ctx_{i}_{int(time.time())}",
                f"Entidade {i+1}",
                NodeType.CONTEXT,
                relevance=0.7 - i * 0.05
            )
            context_nodes.append(ctx_node)
            self.graph.activate_node(ctx_node.id, duration=1.0)
            
            # Conectar a um chunk de memória aleatório
            if memory_nodes:
                import random
                mem = random.choice(memory_nodes)
                self.graph.add_edge(mem.id, ctx_node.id, EdgeType.REASONING)
            
            time.sleep(0.15)
        
        # Fase 3: Chamar agentes
        self.graph.log_event("FASE 3", "Orquestrando agentes...")
        agent_nodes = []
        for i in range(num_agents):
            agent_node = self.graph.add_node(
                f"agent_{i}_{int(time.time())}",
                f"Agent {i+1}",
                NodeType.AGENT,
                relevance=0.6 + i * 0.1
            )
            agent_nodes.append(agent_node)
            self.graph.activate_node(agent_node.id, duration=1.5)
            
            # Conectar a contexto e memória
            if context_nodes:
                import random
                ctx = random.choice(context_nodes)
                self.graph.add_edge(ctx.id, agent_node.id, EdgeType.EXECUTION)
            
            time.sleep(0.25)
        
        # Fase 4: Gerar resposta
        self.graph.log_event("FASE 4", "Sintetizando resposta...")
        response_node = self.graph.add_node(
            f"resp_{int(time.time())}",
            "Resposta LLM",
            NodeType.RESPONSE,
            relevance=0.95
        )
        self.graph.activate_node(response_node.id, duration=2.0)
        
        # Conectar agentes à resposta
        for agent in agent_nodes:
            self.graph.add_edge(agent.id, response_node.id, EdgeType.EXECUTION)
        
        self.graph.log_event("CONCLUIDO", "Consulta processada com sucesso!")


def create_memory_network_demo():
    """Cria uma demo da rede de memória."""
    graph = MemoryNetworkGraph(max_nodes=50, max_edges=100)
    visualizer = MemoryNetworkVisualizer(graph)
    simulator = MemoryNetworkSimulator(graph)
    
    # Executar simulação em thread
    def run_simulation():
        queries = [
            "Como o RAG funciona em LLMs?",
            "Qual é a arquitetura do transformer?",
            "Como agentes autônomos tomam decisões?"
        ]
        
        for query in queries:
            simulator.simulate_query_execution(query, num_memory_chunks=4, num_entities=3, num_agents=2)
            time.sleep(2.0)
    
    sim_thread = threading.Thread(target=run_simulation, daemon=True)
    sim_thread.start()
    
    # Iniciar animação
    visualizer.run_animation(fps=2, duration=30.0)


def run_interactive_terminal():
    """Executa terminal interativo de rede de memória."""
    graph = MemoryNetworkGraph()
    visualizer = MemoryNetworkVisualizer(graph)
    simulator = MemoryNetworkSimulator(graph)
    
    if not HAS_RICH:
        print("⚠️  Rich não instalado. Use: pip install rich")
        print("Usando modo ASCII...")
    
    print("\n🧠 Memory Network Visualizer — Terminal Animado")
    print("════════════════════════════════════════════════")
    print("Digite uma consulta para visualizar a rede de memória em tempo real")
    print("Digite 'sair' para encerrar\n")
    
    visualizer.running = True
    anim_thread = threading.Thread(
        target=lambda: visualizer.run_animation(fps=1, duration=999),
        daemon=True
    )
    anim_thread.start()
    
    try:
        while visualizer.running:
            query = input("Consulta> ").strip()
            
            if query.lower() == "sair":
                visualizer.running = False
                break
            
            if query:
                simulator.simulate_query_execution(query)
                time.sleep(3.0)
    
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        visualizer.running = False


if __name__ == "__main__":
    # Executar demo ou terminal interativo
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        create_memory_network_demo()
    else:
        run_interactive_terminal()
