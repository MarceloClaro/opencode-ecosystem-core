# -*- coding: utf-8 -*-
"""
Memory Network Streamlit Component — Visualização interativa de rede de memória
================================================================================

Integra o visualizador de rede de memória com Streamlit para exibição
em tempo real dentro da webapp de OpenCode Ecosystem.
"""

from __future__ import annotations

import json
import time
import threading
from typing import Any, Dict, List, Optional

import streamlit as st

# Importa o visualizador
from webapp.memory_network_visualizer import (
    MemoryNetworkGraph,
    MemoryNetworkVisualizer,
    MemoryNetworkSimulator,
    NodeType,
    EdgeType,
)


@st.cache_resource
def get_memory_graph() -> MemoryNetworkGraph:
    """Cache global do grafo de memória."""
    return MemoryNetworkGraph(max_nodes=100, max_edges=150)


def render_memory_network_streamlit():
    """Renderiza rede de memória em interface Streamlit."""
    
    st.title("🧠 Memory Network Visualizer")
    st.markdown(
        """
        Visualize em **tempo real** como o LLM consulta memória, contexto e agentes.
        - 🔵 **CONSULTA** — Pergunta do usuário
        - 🟢 **MEMÓRIA** — Chunks recuperados
        - 🟡 **CONTEXTO** — Entidades e relações
        - 🟠 **AGENTES** — Skills orquestrados
        - 🟣 **RESPOSTA** — Saída sintetizada
        """
    )
    
    graph = get_memory_graph()
    visualizer = MemoryNetworkVisualizer(graph)
    simulator = MemoryNetworkSimulator(graph)
    
    # Controles
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Iniciar Simulação Demo", use_container_width=True):
            st.session_state.demo_running = True
    
    with col2:
        if st.button("⏹️ Parar", use_container_width=True):
            st.session_state.demo_running = False
    
    with col3:
        fps = st.slider("FPS", 1, 10, 2)
    
    st.divider()
    
    # Abas
    tab_viz, tab_events, tab_graph, tab_stats = st.tabs([
        "📊 Visualização",
        "📋 Eventos",
        "🕸️ Grafo",
        "📈 Estatísticas"
    ])
    
    # ===== TAB 1: VISUALIZAÇÃO =====
    with tab_viz:
        col_network, col_legend = st.columns([3, 1])
        
        with col_network:
            st.subheader("Rede de Memória em Tempo Real")
            
            # Container para atualização de frames
            frame_placeholder = st.empty()
            
            def update_frames():
                """Atualiza frames continuamente."""
                while st.session_state.get("demo_running", False):
                    # Renderizar ASCII
                    ascii_graph = visualizer.render_ascii_graph()
                    
                    with frame_placeholder.container():
                        st.code(ascii_graph, language="text")
                    
                    time.sleep(1.0 / fps)
            
            # Iniciar thread de atualização se demo está rodando
            if st.session_state.get("demo_running", False):
                update_frames()
        
        with col_legend:
            st.subheader("Legenda")
            
            legend_items = [
                ("◉", "Nó Ativo", "🔴"),
                ("○", "Nó Inativo", "⚪"),
                ("→", "Recuperação", "🔵"),
                ("⟿", "Raciocínio", "🟢"),
                ("⟹", "Execução", "🟡"),
                ("╌", "Referência", "🔗"),
            ]
            
            for symbol, label, emoji in legend_items:
                st.text(f"{emoji} {symbol} {label}")
    
    # ===== TAB 2: EVENTOS =====
    with tab_events:
        st.subheader("Log de Eventos")
        
        event_placeholder = st.empty()
        
        if st.button("🔄 Atualizar Eventos", key="refresh_events"):
            pass
        
        # Exibir eventos em container
        with event_placeholder.container():
            if graph.event_log:
                for event in list(graph.event_log)[-20:]:
                    if "ERRO" in event or "ERROR" in event:
                        st.error(event)
                    elif "SUCESSO" in event or "CONCLUIDO" in event:
                        st.success(event)
                    elif "FASE" in event:
                        st.info(event)
                    else:
                        st.write(event)
            else:
                st.caption("Nenhum evento registrado ainda.")
    
    # ===== TAB 3: GRAFO =====
    with tab_graph:
        st.subheader("Estrutura do Grafo")
        
        col_nodes, col_edges = st.columns(2)
        
        with col_nodes:
            st.metric("Nós Ativos", len(graph.nodes))
            st.markdown("**Nós por Tipo:**")
            
            node_counts = {}
            for node in graph.nodes.values():
                node_counts[node.node_type.value] = node_counts.get(node.node_type.value, 0) + 1
            
            for node_type, count in sorted(node_counts.items()):
                icon = {
                    "memoria": "🔵",
                    "contexto": "🟢",
                    "agente": "🟡",
                    "consulta": "❓",
                    "resposta": "✓",
                }.get(node_type, "•")
                st.write(f"{icon} {node_type.capitalize()}: {count}")
        
        with col_edges:
            st.metric("Arestas", len(graph.edges))
            st.markdown("**Arestas por Tipo:**")
            
            edge_counts = {}
            for edge in graph.edges:
                edge_counts[edge.edge_type.value] = edge_counts.get(edge.edge_type.value, 0) + 1
            
            for edge_type, count in sorted(edge_counts.items()):
                st.write(f"→ {edge_type.capitalize()}: {count}")
        
        st.divider()
        
        # Tabela detalhada de nós
        st.markdown("**Detalhes dos Nós:**")
        
        node_data = []
        for node in list(graph.nodes.values())[-15:]:
            node_data.append({
                "ID": node.id[:20],
                "Rótulo": node.label[:30],
                "Tipo": node.node_type.value,
                "Relevância": f"{node.relevance:.2f}",
                "Ativo": "⚡" if node.active else "—",
            })
        
        if node_data:
            st.dataframe(node_data, use_container_width=True)
        else:
            st.caption("Nenhum nó no grafo.")
    
    # ===== TAB 4: ESTATÍSTICAS =====
    with tab_stats:
        st.subheader("Estatísticas e Métricas")
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            avg_relevance = (
                sum(n.relevance for n in graph.nodes.values()) / len(graph.nodes)
                if graph.nodes else 0
            )
            st.metric("Relevância Média", f"{avg_relevance:.2f}")
        
        with col_s2:
            active_nodes = sum(1 for n in graph.nodes.values() if n.active)
            st.metric("Nós Ativos Agora", active_nodes)
        
        with col_s3:
            active_edges = sum(1 for e in graph.edges if e.active)
            st.metric("Arestas Ativas Agora", active_edges)
        
        with col_s4:
            edge_density = (
                len(graph.edges) / (len(graph.nodes) * (len(graph.nodes) - 1) / 2)
                if len(graph.nodes) > 1 else 0
            )
            st.metric("Densidade de Grafo", f"{edge_density:.2f}")
        
        st.divider()
        
        # Gráfico de timeline
        st.markdown("**Timeline de Ativação de Nós:**")
        
        timeline_data = []
        for node in sorted(graph.nodes.values(), key=lambda n: n.timestamp):
            timeline_data.append({
                "Timestamp": time.strftime("%H:%M:%S", time.localtime(node.timestamp)),
                "Rótulo": node.label[:20],
                "Tipo": node.node_type.value,
                "Relevância": node.relevance,
            })
        
        if timeline_data:
            st.line_chart(
                {item["Tipo"]: item["Relevância"] for item in timeline_data[-20:]},
                use_container_width=True
            )
        
        st.divider()
        
        # Controle de simulação manual
        st.markdown("**Simulação Manual:**")
        
        col_query, col_run = st.columns([3, 1])
        
        with col_query:
            manual_query = st.text_input(
                "Digite uma consulta para simular:",
                placeholder="Ex: Como funciona o RAG?",
                key="manual_query"
            )
        
        with col_run:
            if st.button("🚀 Executar Simulação", use_container_width=True, key="run_sim"):
                if manual_query:
                    with st.spinner("Simulando consulta..."):
                        simulator.simulate_query_execution(
                            manual_query,
                            num_memory_chunks=4,
                            num_entities=3,
                            num_agents=2
                        )
                    st.success("✅ Simulação concluída!")


def add_memory_viz_tab_to_streamlit(tabs: List[Any]) -> int:
    """
    Adiciona aba de Memory Visualizer às abas principais.
    
    Uso dentro do app.py:
    ```python
    from webapp.memory_network_streamlit import add_memory_viz_tab_to_streamlit
    
    tabs = st.tabs([...existentes...])
    viz_tab_index = add_memory_viz_tab_to_streamlit(tabs)
    
    with tabs[viz_tab_index]:
        render_memory_network_streamlit()
    ```
    """
    return len(tabs)


# Ponto de entrada direto
if __name__ == "__main__":
    # Para testes locais: streamlit run webapp/memory_network_streamlit.py
    if "demo_running" not in st.session_state:
        st.session_state.demo_running = False
    
    render_memory_network_streamlit()
