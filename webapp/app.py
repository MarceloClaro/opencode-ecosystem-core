# -*- coding: utf-8 -*-
"""
OpenCode Ecosystem Core — Interface Web (Streamlit)
===================================================
Painel de controle interativo do orquestrador central `marceloclaro`.

Uso (a partir da raiz do repositório):
    streamlit run webapp/app.py

Abas disponíveis:
    - Dashboard: status do ecossistema, agentes, Trust Engine, Token Economy
    - Delegação: roteamento por atenção explicável e delegação de tarefas
    - Pesquisa Acadêmica: buscadores multiplataforma e pipeline de fichamentos
    - Enxame & Jogos: MiroFish swarm, meta-raciocínio e equilíbrio de Nash
    - Diagnóstico: Deep Diagnose M1-M5 sobre um corpus arbitrário
    - Raciocínio & Quântico: motores formais e simulador statevector
"""
import json
import os
import sys
import tempfile

import streamlit as st

# Garante a raiz do repositório no path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from marceloclaro.orchestrator import MarceloClaroOrchestrator  # noqa: E402

st.set_page_config(
    page_title="OpenCode Ecosystem Core",
    page_icon="🧠",
    layout="wide",
)


@st.cache_resource(show_spinner="Inicializando orquestrador marceloclaro...")
def get_orchestrator() -> MarceloClaroOrchestrator:
    return MarceloClaroOrchestrator()


def show_json(data, height: int = 300):
    """Renderiza um dict/list como JSON legível."""
    st.json(json.loads(json.dumps(data, ensure_ascii=False, default=str)))


orch = get_orchestrator()

st.title("🧠 OpenCode Ecosystem Core")
st.caption(
    "Painel do orquestrador metacognitivo **marceloclaro** — "
    "Transformer Routing · Trust Engine · Token Economy · MiroFish · Qualis A1"
)

tabs = st.tabs([
    "📊 Dashboard",
    "🎯 Delegação",
    "📚 Pesquisa Acadêmica",
    "🐟 Enxame & Jogos",
    "🔬 Diagnóstico",
    "🧮 Raciocínio & Quântico",
])

# ---------------------------------------------------------------- Dashboard
with tabs[0]:
    status = orch.status()
    agents = orch.list_agents()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Agentes Registrados", len(agents))
    col2.metric("Tarefas", str(status.get("tasks", status.get("active_tasks", 0))))
    col3.metric("Eventos no Workspace", str(status.get("workspace_events", status.get("events", "—"))))
    col4.metric("Subsistemas", str(len([k for k in status.keys()])))

    st.subheader("Status Completo do Ecossistema")
    show_json(status)

    st.subheader("Catálogo de Agentes")
    query = st.text_input("Filtrar agentes por nome ou capacidade", "")
    filtered = [
        a for a in agents
        if not query or query.lower() in json.dumps(a, ensure_ascii=False, default=str).lower()
    ]
    st.write(f"{len(filtered)} agentes encontrados")
    st.dataframe(filtered, use_container_width=True, height=350)

# ---------------------------------------------------------------- Delegação
with tabs[1]:
    st.subheader("Roteamento por Atenção (Explicável)")
    desc = st.text_area(
        "Descrição da tarefa",
        "Escrever revisão de literatura sobre aprendizado quântico de máquina",
        key="delegate_desc",
    )
    caps = st.text_input("Capacidades exigidas (separadas por vírgula, opcional)", "")
    cap_list = [c.strip() for c in caps.split(",") if c.strip()] or None

    col_a, col_b = st.columns(2)
    if col_a.button("🔍 Explicar Roteamento", use_container_width=True):
        with st.spinner("Calculando scores de atenção..."):
            explanation = orch.explain_routing(desc, required_capabilities=cap_list)
        show_json(explanation)

    if col_b.button("🚀 Delegar Tarefa", use_container_width=True):
        with st.spinner("Emitindo CFP no blackboard A2A..."):
            task_id = orch.delegate(desc, required_capabilities=cap_list)
        st.success(f"Tarefa delegada: `{task_id}`")
        show_json(orch.perceive(limit=5))

    st.divider()
    st.subheader("Pipeline Gerar → Verificar → Revisar (Reflexion)")
    pipe_desc = st.text_input("Tarefa do pipeline", "Resumo executivo do ecossistema")
    if st.button("▶️ Executar Pipeline"):
        def _executor(prompt, feedback=None):
            base = f"Rascunho para: {prompt}"
            if feedback:
                base += f" [revisado: {feedback}]"
            return base

        with st.spinner("Executando ciclo Reflexion..."):
            result = orch.run_pipeline(pipe_desc, _executor)
        show_json(result)

# ------------------------------------------------------- Pesquisa Acadêmica
with tabs[2]:
    st.subheader("Busca Acadêmica Multiplataforma")
    topic = st.text_input("Tópico de pesquisa", "quantum machine learning")
    platforms = st.multiselect(
        "Plataformas",
        ["arxiv", "openalex", "crossref", "semantic_scholar", "github", "kaggle"],
        default=["arxiv"],
    )
    limit = st.slider("Resultados por plataforma", 1, 20, 5)

    if st.button("🔎 Buscar"):
        with st.spinner("Consultando APIs acadêmicas..."):
            try:
                results = orch.research_search(topic, platforms=platforms, limit_per_platform=limit)
                st.write(f"{len(results)} resultados")
                st.dataframe(results, use_container_width=True)
            except Exception as exc:  # rede indisponível etc.
                st.error(f"Falha na busca: {exc}")

    st.divider()
    st.subheader("Pipeline Completo (Download + PDF→MD + Fichamentos)")
    st.caption("Gera uma pasta de produção com PDFs, conversões e fichamentos ABNT/APA.")
    max_papers = st.slider("Máximo de papers", 1, 10, 2)
    use_llm = st.checkbox("Enriquecer fichamentos e resenhas com LLM", value=False)
    llm_provider, llm_model = "auto", None
    if use_llm:
        from research.llm_client import LLMClient
        col_llm1, col_llm2 = st.columns(2)
        llm_provider = col_llm1.selectbox(
            "Provedor LLM", ["auto", "ollama", "openai"],
            help="'auto' prioriza Ollama local (privacidade e custo zero)")
        local_models = LLMClient.ollama_models()
        if local_models:
            llm_model = col_llm2.selectbox("Modelo local (Ollama)", local_models)
            st.success(f"Ollama detectado com {len(local_models)} modelo(s) local(is)")
        else:
            llm_model = col_llm2.text_input("Modelo", "llama3.2")
            st.info("Servidor Ollama não detectado em localhost:11434 — "
                    "instale com `curl -fsSL https://ollama.com/install.sh | sh` "
                    "e rode `ollama pull llama3.2`, ou use provedor 'openai'.")
    if st.button("📥 Executar Pesquisa Completa"):
        prod = tempfile.mkdtemp(prefix="producao_")
        with st.spinner("Executando funil de pesquisa..."):
            try:
                research = orch.research(
                    topic, production_folder=prod,
                    max_papers=max_papers, platforms=platforms or None,
                    use_llm=use_llm, llm_provider=llm_provider,
                    llm_model=llm_model,
                )
                st.success(f"Produção salva em `{prod}`")
                show_json(research)
            except Exception as exc:
                st.error(f"Falha na pesquisa: {exc}")

    st.divider()
    st.subheader("Pipeline MASWOS (Manuscrito Qualis A1)")
    manuscript = st.text_area("Rascunho do manuscrito", "O ruído pode atuar como regularizador implícito em VQCs.")
    if st.button("📝 Executar MASWOS"):
        with st.spinner("Orquestrando agentes acadêmicos..."):
            result = orch.academic_pipeline(topic=topic, manuscript=manuscript)
        show_json(result)

# ---------------------------------------------------------- Enxame & Jogos
with tabs[3]:
    st.subheader("Predição por Enxame (MiroFish)")
    question = st.text_input("Pergunta", "A adoção de agentes autônomos crescerá em 2026?")
    signal = st.slider("Sinal inicial (0=não, 1=sim)", 0.0, 1.0, 0.7)
    col_p, col_v = st.columns(2)
    if col_p.button("🐟 Predizer", use_container_width=True):
        show_json(orch.swarm_predict(question, signal=signal))
    if col_v.button("✅ Validar (Delphi + GraphMemory)", use_container_width=True):
        show_json(orch.swarm_validate(question, signal=signal))

    st.divider()
    st.subheader("Meta-Raciocínio (38 Tipos)")
    meta_topic = st.text_input("Tópico", "Como garantir reprodutibilidade em pesquisa com LLMs?")
    if st.button("🧩 Meta-Raciocinar"):
        show_json(orch.meta_reason(meta_topic))

    st.divider()
    st.subheader("Teoria dos Jogos")
    game = st.selectbox("Jogo", ["prisoners_dilemma", "stag_hunt", "chicken", "battle_of_sexes"])
    if st.button("♟️ Analisar Equilíbrio de Nash"):
        try:
            show_json(orch.nash_analysis(game=game))
        except Exception as exc:
            st.error(f"Jogo não suportado: {exc}")

# -------------------------------------------------------------- Diagnóstico
with tabs[4]:
    st.subheader("Deep Diagnose (M1–M5)")
    st.caption(
        "Engenharia reversa epistemológica: varredura noológica, teleológica, "
        "priorização epistêmica e geração de sucessores."
    )
    corpus = st.text_area(
        "Corpus a diagnosticar",
        "Sistema multiagente com roteamento estático apresenta gargalos de "
        "escalabilidade e ausência de gates de qualidade.",
        height=150,
    )
    domain = st.text_input("Domínio", "software architecture")
    deep = st.checkbox("Diagnóstico profundo (deep=True)", value=True)
    if st.button("🔬 Diagnosticar"):
        with st.spinner("Executando pipeline de scanners..."):
            diagnosis = orch.diagnose(corpus, domain=domain, deep=deep)
        show_json(diagnosis)

# ------------------------------------------------- Raciocínio & Quântico
with tabs[5]:
    st.subheader("Motores de Raciocínio Formal")
    query = st.text_input("Consulta (equação, proposição...)", "2*x + 4 = 10")
    engine = st.selectbox("Motor", ["auto", "sympy", "z3", "kanren", "critical"])
    if st.button("🧮 Raciocinar"):
        try:
            show_json(orch.reason(query, engine=engine))
        except Exception as exc:
            st.error(f"Falha no motor: {exc}")

    st.divider()
    st.subheader("Experimento Quântico (Statevector Simulator)")
    n_qubits = st.slider("Número de qubits", 1, 8, 3)
    shots = st.slider("Shots", 128, 4096, 1024, step=128)
    if st.button("⚛️ Executar Experimento"):
        with st.spinner("Simulando circuito..."):
            show_json(orch.quantum_experiment(n_qubits=n_qubits, shots=shots))

st.sidebar.image(os.path.join(ROOT, "assets", "bmc_qr.png") if os.path.exists(
    os.path.join(ROOT, "assets", "bmc_qr.png")) else None, width=160)
st.sidebar.markdown(
    "### OpenCode Ecosystem Core\n"
    "Orquestrador metacognitivo com 134 agentes especializados.\n\n"
    "[☕ Buy Me a Coffee](https://buymeacoffee.com/geomaker)\n\n"
    "[📖 Documentação](https://github.com/MarceloClaro/opencode-ecosystem-core)"
)
