# -*- coding: utf-8 -*-
"""
OpenCode Ecosystem Core v3.0 — Framework de Consulta e Producao
================================================================
Interface web interativa (Streamlit) para todo o ecossistema:
- Pipeline Academico Agentivo completo (R101-R105)
- Consulta a ciclos evolutivos, evidencias e producoes
- Gerenciamento de revisoes, composicao e publicacao

Uso:
    streamlit run webapp/app.py

Framework de 8 abas organizadas em dois modos:
    [PRODUCAO]  Home | Pipeline | Deep Research | Peer Review | Paper Composer
    [CONSULTA]  Evolution | Consultation | System
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Helpers locais ────────────────────────────────────────────────
from webapp.pipeline_helpers import (
    run_evosci, explain_evosci_components,
    run_deep_research, query_evidence_graph,
    run_peer_review, get_rubric_descriptions,
    run_manuscript_revision,
    compose_paper,
    run_full_academic_pipeline,
)
from webapp.consultation_helpers import (
    load_evolution_cycles, get_evolution_stats, search_cycles,
    list_producoes, get_evidence_graph_summary,
    search_academic, list_specs, get_mcp_tools_list,
    get_quality_summary, get_dashboard_html,
)
from webapp.legal_impact_helpers import (
    build_legal_params,
    resolve_domain_knowledge_base_selection,
    summarize_domain_knowledge_base,
    summarize_legal_domain_route,
    summarize_legal_impact_section,
)
from marceloclaro.orchestrator import MarceloClaroOrchestrator

# ── Configuracao ──────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenCode Ecosystem Core v3.0",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Inicializando orquestrador marceloclaro...")
def get_orchestrator() -> MarceloClaroOrchestrator:
    return MarceloClaroOrchestrator()


def show_json(data, height: int = 300):
    """Renderiza dict/list como JSON identado."""
    st.json(json.loads(json.dumps(data, ensure_ascii=False, default=str)))


def section_header(title: str, description: str, icon: str = ""):
    """Cabecalho padrao de secao com titulo e descricao."""
    st.subheader(f"{icon} {title}")
    st.caption(description)


def card(text: str, label: str = ""):
    """Exibe um cartao simples com label e valor."""
    if label:
        st.metric(label=label, value=text)
    else:
        st.info(text)


# ── Inicializacao ─────────────────────────────────────────────────
orch = get_orchestrator()

# Carrega dados globais
EVOLUTION_CYCLES = load_evolution_cycles()
EVO_STATS = get_evolution_stats(EVOLUTION_CYCLES)
MCP_TOOLS = get_mcp_tools_list()

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.image(str(ROOT / "assets" / "bmc_qr.png"), width=160) if (ROOT / "assets" / "bmc_qr.png").exists() else None
    st.markdown("""
    ## OpenCode Ecosystem Core v3.0
    **Framework de Consulta e Producao**

    | Metrica | Valor |
    |---|---|
    | Testes | 1050 |
    | Ciclos | 64 |
    | MCP Tools | 14 |
    | Score Medio | 9.4/10 |

    [![GitHub](https://img.shields.io/badge/GitHub-Repo-blue)](https://github.com/MarceloClaro/opencode-ecosystem-core)
    """)
    st.divider()
    st.markdown("### Modos")
    st.caption("""
    **PRODUCAO:** Pipeline completo do problema ao artigo
    **CONSULTA:** Navegue por ciclos, evidencias e historico
    """)

# ── Tabs ──────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Home",
    "🔬 Pipeline",
    "📚 Deep Research",
    "📝 Peer Review",
    "📄 Paper Composer",
    "🧬 Evolution",
    "🔎 Consultation",
    "⚙️ System",
])

# =====================================================================
# TAB 0: HOME
# =====================================================================
with tabs[0]:
    st.title("🧠 OpenCode Ecosystem Core v3.0")
    st.markdown("""
    **Framework de Consulta e Producao Academica** — 64 ciclos evolutivos,
    1050 testes, pipeline academico agentivo completo (R101-R105).
    """)

    # Linha de metricas principais
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ciclos de Evolucao", EVO_STATS["count"])
    c2.metric("Score Medio", f'{EVO_STATS["avg_score"]:.1f}/10')
    c3.metric("Testes", "1050")
    c4.metric("MCP Tools", len(MCP_TOOLS))
    c5.metric("Licoes Registradas", EVO_STATS["total_lessons"])

    # Dois cards grandes: Producao e Consulta
    col_prod, col_cons = st.columns(2)
    with col_prod:
        st.info("""
        ### 🏭 Producao
        Pipeline de 5 estagios: do problema ao artigo formatado.
        - **EvoSci** (R101): descoberta cientifica autonomia
        - **Deep Research** (R102): grafo de evidencias
        - **Peer Review** (R103): revisao 8-dimensoes
        - **Revision** (R104d): diff com rollback
        - **Paper Composer** (R105): ABNT/APA/IEEE
        """)
    with col_cons:
        st.info("""
        ### 🔎 Consulta
        Navegue pelo historico completo do ecossistema.
        - **Evolution Cycles:** 64 registros (R47-R106)
        - **Evidence Graph:** entidades, relacoes, evidencias
        - **Producoes Anteriores:** pastas de pesquisa
        - **Specs:** especificacoes formais SDD
        """)

    st.divider()

    # Ciclos recentes
    st.subheader("🔄 Ciclos Recentes")
    recent = EVOLUTION_CYCLES[-8:] if EVOLUTION_CYCLES else []
    if recent:
        cols = st.columns(len(recent))
        for i, cycle in enumerate(recent):
            with cols[i]:
                st.metric(
                    label=cycle.get("round_id", "?"),
                    value=f'{cycle.get("score", 0):.1f}',
                    delta=cycle.get("objective", "")[:30] + "..."
                )
    else:
        st.caption("Nenhum ciclo encontrado em evolution/cycles.json")

    st.divider()

    # Qualidade
    st.subheader("📊 Qualidade do Ecossistema")
    quality = get_quality_summary()
    cq1, cq2, cq3 = st.columns(3)
    cq1.metric("Score Geral", f'{quality.get("quality_score", {}).get("overall_score", "N/A")}/10')
    cq2.metric("Status", quality.get("overall_status", "N/A"))
    cq3.metric("Testes", f'{quality.get("test_results", {}).get("passed", 0)} passados')

    # Quick actions
    st.divider()
    st.subheader("🚀 Acoes Rapidas")
    qc1, qc2, qc3, qc4 = st.columns(4)
    if qc1.button("🔬 Pipeline Completo", use_container_width=True):
        st.switch_page("webapp/app.py")  # Vai para tab Pipeline
    if qc2.button("📚 Deep Research", use_container_width=True):
        st.info("Vá para a aba 'Deep Research' para executar pesquisas profundas.")
    if qc3.button("📝 Revisao por Pares", use_container_width=True):
        st.info("Vá para a aba 'Peer Review' para revisar manuscritos.")
    if qc4.button("🔎 Consultar", use_container_width=True):
        st.info("Vá para a aba 'Consultation' para buscar no historico.")

# =====================================================================
# TAB 1: PIPELINE ACADEMICO
# =====================================================================
with tabs[1]:
    st.title("🔬 Pipeline Academico Agentivo (R101-R105)")
    st.markdown("""
    Pipeline completo de 5 estagios que transforma um problema em artigo 
    academico formatado. Cada estagio alimenta o proximo automaticamente.
    """)

    # ── Fluxo visual ──
    with st.expander("📖 Como funciona o Pipeline?", expanded=True):
        st.markdown("""
        ```
        Problema → R101:EvoSci → R102:DeepResearch → R103:PeerReview → R104d:Revision → R105:Composer → Artigo
        ```
        **Estagios:**
        1. **R101 EvoSci** — Agentes Mentor/Researcher/Reviewer + Engine Evolutivo (Selection/Crossover/Mutation/Inheritance)
        2. **R102 Deep Research** — Evidence Graph, BFRS (largura), DFRS (profundidade), Gate de Suficiencia
        3. **R103 Peer Review** — Rubrica 8 dimensoes, Ledger claim-evidence-risk, 4 Criticos Especialistas
        4. **R104d Revision** — Analyzer, SectionMapper, ProposalGenerator, DiffEngine com Rollback
        5. **R105 Paper Composer** — StructurePlanner, SectionWriter, CitationFormatter, CrossConsistencyVerifier
        """)

    # ── Configuracao ──
    with st.expander("⚙️ Configuracao do Pipeline", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            seed_domain = st.text_input(
                "Dominio/Problema da Pesquisa",
                value="Quantum Ethics in Artificial Intelligence: A Framework for Moral AI Systems",
                help="O problema ou topico central que sera investigado pelo pipeline completo.",
                key="pipeline_seed"
            )
            venue = st.selectbox(
                "Formato de Saida (Venue)",
                ["abnt", "apa", "ieee"],
                index=0,
                help="ABNT (NBR 6023/10520), APA 7th ed., ou IEEE",
                key="pipeline_venue"
            )
        with col2:
            max_rounds = st.slider(
                "Geracoes EvoSci (max_rounds)",
                1, 10, 3,
                help="Numero de geracoes evolutivas do EvoSci. Mais geracoes = mais refinamento, mas mais tempo.",
                key="pipeline_rounds"
            )
            verbose = st.checkbox(
                "Log detalhado (verbose)",
                value=False,
                help="Exibe logs detalhados de cada estagio do pipeline.",
                key="pipeline_verbose"
            )

    # ── Executar ──
    if st.button("🚀 EXECUTAR PIPELINE COMPLETO", type="primary", use_container_width=True):
        with st.spinner("Executando pipeline academico de 5 estagios... Isso pode levar varios minutos."):
            result = run_full_academic_pipeline(
                seed_domain=seed_domain,
                max_rounds=max_rounds,
                venue=venue,
                verbose=verbose,
            )

        st.success(f"✅ Pipeline concluido em {result.get('timeline', {}).get('total', '?')} segundos!")

        # Timeline
        st.subheader("⏱️ Timeline")
        timeline = result.get("timeline", {})
        tl_cols = st.columns(len(timeline))
        for i, (k, v) in enumerate(timeline.items()):
            with tl_cols[i]:
                st.metric(label=k, value=f"{v}s")

        # Resultados por estagio
        with st.expander("🔬 R101 - EvoSci (Descoberta)", expanded=True):
            evo = result.get("evosci", {})
            st.metric("Melhor Solucao Score", f'{evo.get("best_solution", {}).get("score", "N/A")}')
            st.text_area("Melhor Solucao (Conteudo)", evo.get("best_solution", {}).get("content", ""), height=100)
            show_json(evo.get("evolutionary_trajectory", []))

        with st.expander("📚 R102 - Deep Research (Evidencias)"):
            deep = result.get("deep_research", {})
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("Entidades", deep.get("entity_count", 0))
            dc2.metric("Evidencias", deep.get("evidence_count", 0))
            dc3.metric("Gate Suficiencia", deep.get("sufficiency_gate", {}).get("status", "N/A"))
            st.text_area("Resposta Sintetizada", deep.get("answer", ""), height=150)

        with st.expander("📝 R103 - Peer Review (Revisao)"):
            review = result.get("peer_review", {})
            scores = review.get("scores", {})
            if scores:
                score_cols = st.columns(len(scores))
                for i, (dim, score) in enumerate(scores.items()):
                    with score_cols[i]:
                        st.metric(label=dim, value=f"{score:.1f}")
            st.text_area("Meta-Review", review.get("meta_review", ""), height=100)
            st.text_area("Repair Plan", json.dumps(review.get("repair_plan", []), indent=2), height=100)

        with st.expander("✏️ R104d - Revision (Correcoes)"):
            revision = result.get("manuscript_revision", {})
            st.metric("Alteracoes Aplicadas", revision.get("changes_applied", 0))
            st.text_area("Carta de Rebuttal", revision.get("rebuttal_letter", ""), height=150)

        with st.expander("📄 R105 - Paper Composer (Artigo Final)"):
            paper = result.get("paper", {})
            st.markdown(f"**Venue:** {paper.get('venue', 'N/A').upper()}")
            st.text_area("Texto Completo do Artigo", paper.get("full_text", ""), height=300)
            st.text_area("Referencias Formatadas", 
                        "\n".join(paper.get("citations_formatted", [])), height=100)
            consist = paper.get("consistency_report", {})
            if consist:
                c_cols = st.columns(len(consist))
                for i, (k, v) in enumerate(consist.items()):
                    with c_cols[i]:
                        st.metric(label=k, value=v)

    # ── Execucao individual ──
    st.divider()
    st.subheader("🧪 Executar Estagio Individual")
    ind_stage = st.selectbox(
        "Selecione o estagio",
        ["EvoSci (R101)", "Deep Research (R102)", "Peer Review (R103)",
         "Manuscript Revision (R104d)", "Paper Composer (R105)"],
        key="pipeline_individual"
    )
    if st.button("▶️ Executar Estagio", key="pipeline_run_ind"):
        st.info(f"Execute o estagio '{ind_stage}' na aba correspondente.")

# =====================================================================
# TAB 2: DEEP RESEARCH
# =====================================================================
with tabs[2]:
    st.title("📚 Deep Research Console (R102)")
    st.markdown("""
    Sistema de pesquisa profunda com **Evidence Graph**, busca em largura (BFRS) 
    e profundidade (DFRS). Constroi um grafo epistemologico de entidades, 
    relacoes e evidencias com proveniencia completa.
    """)

    tab_dr_search, tab_dr_evidence, tab_dr_kb = st.tabs([
        "🔎 Pesquisar", "🕸️ Evidence Graph", "📚 Knowledge Base"
    ])

    # ── Search ──
    with tab_dr_search:
        section_header("Pesquisa Profunda", 
                       "Fac,a uma pergunta de pesquisa e deixe o sistema explorar a literatura em largura e profundidade.",
                       "🔎")
        question = st.text_area(
            "Pergunta de Pesquisa",
            "What is the relationship between quantum coherence and ethical decision-making in AI systems?",
            height=100, key="dr_question"
        )
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            max_depth = st.slider("Profundidade Maxima (DFRS)", 1, 5, 3, key="dr_depth")
        with col_d2:
            max_rounds = st.slider("Max Rounds", 1, 10, 5, key="dr_rounds")
        with col_d3:
            dr_verbose = st.checkbox("Verbose", value=False, key="dr_verbose")

        if st.button("🔎 Executar Pesquisa Profunda", type="primary", use_container_width=True):
            with st.spinner("Executando BFRS (largura) + DFRS (profundidade)..."):
                result = run_deep_research(question, max_depth, max_rounds, dr_verbose)
            st.success("Pesquisa concluida!")
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("Entidades no Grafo", result.get("entity_count", 0))
            dc2.metric("Evidencias Coletadas", result.get("evidence_count", 0))
            dc3.metric("Fontes Consultadas", len(result.get("knowledge_sources", [])))
            st.subheader("Resposta Sintetizada")
            st.markdown(result.get("answer", "Nenhuma resposta gerada."))
            if result.get("sufficiency_gate"):
                gate = result["sufficiency_gate"]
                st.metric("Gate de Suficiencia", 
                         f'{gate.get("status", "N/A")} ({gate.get("score", 0)}/{gate.get("threshold", 0)})')
            with st.expander("JSON Completo"):
                show_json(result)

    # ── Evidence Graph ──
    with tab_dr_evidence:
        section_header("Evidence Graph Browser",
                       "Navegue pelo grafo epistemologico: entidades, relacoes e evidencias acumuladas.",
                       "🕸️")
        eg_summary = get_evidence_graph_summary()
        ec1, ec2, ec3 = st.columns(3)
        ec1.metric("Entidades", eg_summary.get("entity_count", 0))
        ec2.metric("Relacoes", eg_summary.get("relation_count", 0))
        ec3.metric("Evidencias", eg_summary.get("evidence_count", 0))

        entity_query = st.text_input("Consultar entidade especifica", "", key="eg_query")
        if st.button("🔍 Consultar", key="eg_consult"):
            result = query_evidence_graph(entity_query)
            st.metric("Entidades Encontradas", result.get("entities_found", 0))
            st.metric("Relacoes Encontradas", result.get("relations_found", 0))
            st.metric("Evidencias Encontradas", result.get("evidences_found", 0))
            with st.expander("Subgrafo Completo"):
                show_json(result.get("subgraph", {}))

        if eg_summary.get("entity_types"):
            st.subheader("Tipos de Entidade")
            st.write(", ".join(eg_summary["entity_types"]))
        if eg_summary.get("relation_types"):
            st.subheader("Tipos de Relacao")
            st.write(", ".join(eg_summary["relation_types"]))

    # ── Knowledge Base ──
    with tab_dr_kb:
        section_header("Knowledge Base Registry",
                       "Fontes de conhecimento disponiveis para consulta.",
                       "📚")
        kb_sources = [
            {"name": "PubMed", "type": "Biomedical", "status": "simulated"},
            {"name": "arXiv", "type": "CS/Physics/Math", "status": "simulated"},
            {"name": "OpenAlex", "type": "Multidisciplinary", "status": "simulated"},
            {"name": "Semantic Scholar", "type": "CS", "status": "simulated"},
            {"name": "Internal Evidence Graph", "type": "Epistemological", "status": "active"},
        ]
        st.dataframe(kb_sources, use_container_width=True)
        st.caption("Fontes marcadas como 'simulated' operam com dados sinteticos para demonstracao. "
                  "Em producao, conectam-se as APIs reais.")

# =====================================================================
# TAB 3: PEER REVIEW
# =====================================================================
with tabs[3]:
    st.title("📝 Peer Review Studio (R103)")
    st.markdown("""
    Sistema agentivo de revisao por pares com **rubrica de 8 dimensoes**,
    **ledger claim-evidence-risk**, **grafo de auditoria** e 
    **4 criticos especialistas** executando em paralelo.
    """)

    tab_pr_review, tab_pr_rubric, tab_pr_history = st.tabs([
        "📝 Executar Revisao", "📋 Rubrica", "📜 Historico"
    ])

    with tab_pr_review:
        section_header("Executar Revisao por Pares",
                       "Submeta um manuscrito para revisao agentiva completa.",
                       "📝")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            rev_title = st.text_input("Titulo do Manuscrito",
                                      "Quantum Ethics: A Framework for Moral AI", key="rev_title")
            rev_abstract = st.text_area("Abstract", 
                                        "This paper presents a framework for moral AI systems...",
                                        height=100, key="rev_abstract")
        with col_p2:
            rev_intro = st.text_area("Introducao", "Context and motivation...", height=80, key="rev_intro")
            rev_methods = st.text_area("Metodos", "Methodology description...", height=80, key="rev_methods")
            rev_results = st.text_area("Resultados", "Key findings...", height=80, key="rev_results")

        sections = {}
        if rev_intro: sections["introduction"] = rev_intro
        if rev_methods: sections["methods"] = rev_methods
        if rev_results: sections["results"] = rev_results

        if st.button("📝 Executar Revisao", type="primary", use_container_width=True, key="pr_run"):
            with st.spinner("Executando 4 criticos em paralelo (Methodology, Results, Literature, Ethics)..."):
                review = run_peer_review(rev_title, rev_abstract, sections, verbose=False)

            st.success("Revisao concluida!")

            # Scores
            scores = review.get("scores", {})
            if scores:
                st.subheader("📊 Scores por Dimensao")
                score_cols = st.columns(len(scores))
                for i, (dim, score) in enumerate(scores.items()):
                    with score_cols[i]:
                        st.metric(label=dim, value=f"{score:.1f}")

            # Meta-review
            st.subheader("Meta-Review")
            st.markdown(review.get("meta_review", "Nenhuma meta-review gerada."))

            # Repair Plan
            repair = review.get("repair_plan", [])
            if repair:
                st.subheader("🔧 Repair Plan")
                for item in repair:
                    sev = item.get("severity", "minor")
                    emoji = {"critical": "🔴", "major": "🟡", "minor": "🟢"}.get(sev, "⚪")
                    st.markdown(f"{emoji} **[{sev.upper()}]** {item.get('claim', '')} "
                               f"— *{item.get('evidence', '')}*")

            # Verification Agenda
            agenda = review.get("verification_agenda", [])
            if agenda:
                st.subheader("✅ Verification Agenda")
                for item in agenda:
                    st.markdown(f"- {item}")

            with st.expander("JSON Completo da Revisao"):
                show_json(review)

    with tab_pr_rubric:
        section_header("Rubrica de Avaliacao (8 Dimensoes)",
                       "Cada dimensao possui peso, polaridade e descricao especifica.",
                       "📋")
        rubrics = get_rubric_descriptions()
        for r in rubrics:
            polarity_icon = "📈" if r["polarity"] == "positiva" else "📉"
            st.markdown(f"**{r['dimension']}** {polarity_icon}  "
                       f"Peso: {r['weight']} | {r['description']}")

    with tab_pr_history:
        section_header("Historico de Revisoes",
                       "Revisoes executadas anteriormente no ecossistema.",
                       "📜")
        st.info("O historico de revisoes sera populado a medida que revisoes forem executadas. "
               "Cada revisao fica registrada no EvolutionRegistry.")

# =====================================================================
# TAB 4: PAPER COMPOSER
# =====================================================================
with tabs[4]:
    st.title("📄 Paper Composer (R104d + R105)")
    st.markdown("""
    Sistema de revisao de manuscritos (R104d) e composicao final (R105).
    Permite revisar textos pos-peer-review e compor artigos completos
    nos formatos ABNT, APA e IEEE.
    """)

    tab_comp_compose, tab_comp_revision, tab_comp_export = st.tabs([
        "📄 Compor Paper", "✏️ Revisar Manuscrito", "📤 Exportar"
    ])

    with tab_comp_compose:
        section_header("Compor Novo Paper",
                       "Planeje, escreva e formate um artigo academico completo.",
                       "📄")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            comp_title = st.text_input("Titulo do Paper",
                                       "Quantum Ethics: A Framework for Moral AI Systems",
                                       key="comp_title")
            comp_venue = st.selectbox("Formato (Venue)", ["abnt", "apa", "ieee"], 
                                      index=0, key="comp_venue")
        with col_c2:
            comp_abstract = st.text_area("Abstract", "This paper presents...", height=100, key="comp_abstract")
            comp_intro = st.text_area("Introducao", "Context and motivation...", height=80, key="comp_intro")
            comp_methods = st.text_area("Metodos", "Methodology...", height=80, key="comp_methods")

        comp_results = st.text_area("Resultados", "Key findings...", height=80, key="comp_results")
        comp_discussion = st.text_area("Discussao", "Interpretation...", height=80, key="comp_discussion")
        comp_conclusion = st.text_area("Conclusao", "Summary...", height=80, key="comp_conclusion")

        sections = {}
        if comp_abstract: sections["abstract"] = comp_abstract
        if comp_intro: sections["introduction"] = comp_intro
        if comp_methods: sections["methods"] = comp_methods
        if comp_results: sections["results"] = comp_results
        if comp_discussion: sections["discussion"] = comp_discussion
        if comp_conclusion: sections["conclusion"] = comp_conclusion

        if st.button("📄 Compor Paper", type="primary", use_container_width=True):
            with st.spinner(f"Compondo paper em formato {comp_venue.upper()}..."):
                paper = compose_paper(comp_title, sections, comp_venue, verbose=False)
            st.success("Paper composto com sucesso!")
            st.subheader("Texto Completo")
            st.text_area("", paper.get("full_text", ""), height=400, key="comp_result")
            st.subheader("Referencias")
            st.text("\n".join(paper.get("citations_formatted", [])))
            consist = paper.get("consistency_report", {})
            if consist:
                st.subheader("Verificacao de Consistencia")
                for k, v in consist.items():
                    st.metric(label=k, value=v)

    with tab_comp_revision:
        section_header("Revisar Manuscrito (R104d)",
                       "Aplique correcoes pos-peer-review com diff controlado e rollback.",
                       "✏️")
        rev_manuscript = st.text_area("Manuscrito Original",
                                      "O ruido quantico pode atuar como regularizador implicito...",
                                      height=200, key="rev_manuscript")
        if st.button("✏️ Revisar Manuscrito", type="primary", use_container_width=True):
            with st.spinner("Aplicando revisao com DiffEngine..."):
                result = run_manuscript_revision(rev_manuscript)
            st.success(f"Revisao aplicada! {result.get('changes_applied', 0)} alteracoes feitas.")
            st.subheader("Carta de Rebuttal")
            st.text_area("", result.get("rebuttal_letter", ""), height=200)

    with tab_comp_export:
        section_header("Exportar",
                       "Exporte o paper compilado nos formatos disponiveis.",
                       "📤")
        st.info("""
        Formatos de exportacao planejados:
        - **DOCX** — Microsoft Word
        - **LaTeX** — Overleaf/TexStudio
        - **PDF** — via LaTeX ou WeasyPrint
        - **HTML** — pagina web formatada
        - **Markdown** — para GitHub/GitLab
        
        A exportacao nativa sera implementada no proximo ciclo (R107).
        """)

# =====================================================================
# TAB 5: EVOLUTION
# =====================================================================
with tabs[5]:
    st.title("🧬 Evolution Lab (R97 + R98)")
    st.markdown("""
    Navegue pelo registro evolutivo completo do ecossistema. 
    64 ciclos (R47-R106) com scores, licoes e trajetoria.
    """)

    tab_ev_cycles, tab_ev_memory, tab_ev_novelty, tab_ev_rag = st.tabs([
        "🔄 Ciclos", "🧠 Memoria", "✨ Novidade", "📖 RAG Evolved"
    ])

    with tab_ev_cycles:
        section_header("Evolution Registry",
                       f"{EVO_STATS['count']} ciclos registrados. Score medio: {EVO_STATS['avg_score']:.1f}/10.",
                       "🔄")
        ec1, ec2, ec3, ec4 = st.columns(4)
        ec1.metric("Total", EVO_STATS["count"])
        ec2.metric("Score Medio", f'{EVO_STATS["avg_score"]:.1f}')
        ec3.metric("Score Maximo", f'{EVO_STATS["max_score"]:.1f}')
        ec4.metric("Score Minimo", f'{EVO_STATS["min_score"]:.1f}')

        search_q = st.text_input("Buscar em ciclos (objetivo, licoes, mudancas)", "", key="ev_search")
        filtered = search_cycles(search_q, EVOLUTION_CYCLES) if search_q else EVOLUTION_CYCLES
        st.write(f"{len(filtered)} ciclos encontrados")
        for cycle in reversed(filtered[-50:]):
            rid = cycle.get("round_id", "?")
            score = cycle.get("score", 0)
            obj = cycle.get("objective", "")
            with st.expander(f"**{rid}** — Score: {score}/10 | {obj[:80]}..."):
                st.markdown(f"**Objetivo:** {obj}")
                st.markdown("**Mudancas:**")
                for ch in cycle.get("changes", []):
                    st.markdown(f"- {ch}")
                st.markdown("**Licoes:**")
                for l in cycle.get("lessons", []):
                    st.markdown(f"- {l}")
                st.caption(f"Timestamp: {cycle.get('timestamp', 'N/A')}")

    with tab_ev_memory:
        section_header("Evolutionary Memory (R97)",
                       "Memoria persistente de ideacao, experimentacao, reflexao e deteccao de estagnacao.",
                       "🧠")
        st.markdown("""
        **Componentes:**
        - **IdeationMemory:** Registra direcoes de pesquisa, scores e estrategias
        - **ExperimentationMemory:** Armazena outcomes de experimentos e recursos gastos
        - **HeartbeatReflection:** Reflexao periodica a cada N ciclos
        - **StagnationDetector:** Detecta plateau de score e sugere pivot
        
        **Uso:**
        ```python
        from synthetic_university.evolutionary_memory import EvolutionaryMemorySubstrate
        memory = EvolutionaryMemorySubstrate()
        memory.record_ideation(direction="Quantum Ethics", score=0.85, strategy="explore")
        memory.record_experiment(direction="Quantum Ethics", outcome="promising", resources=0.7)
        reflection = memory.reflect()
        print(reflection["stagnation_status"])
        ```
        """)

    with tab_ev_novelty:
        section_header("Analisador de Novidade V2 (R98)",
                       "Pipeline OpenNovelty-style com extracao granular de contribution points.",
                       "✨")
        st.markdown("""
        **Componentes:**
        - **ContributionPointExtractor:** 4 tipos de claim (hipotese, metodologia, framework, aplicacao)
        - **PointwiseLiteratureRetriever:** Retrieval multi-source ponto-a-ponto
        - **PointwiseNoveltyScorer:** Pesos diferenciais por tipo de claim
        - **HierarchicalTaxonomyBuilder:** Taxonomia hierarquica por tipo de ponto
        
        **Metricas:**
        - Score global de novidade (0-10)
        - Scores por ponto individual
        - Areas taxonomicas cobertas
        - Discrepancia e posicionamento
        """)

    with tab_ev_rag:
        section_header("Scientific RAG Evolved (R99)",
                       "RAG adaptativo com analise de complexidade e citacoes em grafo.",
                       "📖")
        st.markdown("""
        **Componentes:**
        - **AdaptiveRetriever:** Analisa complexidade (simple/moderate/complex) com 3 estrategias
        - **CitationGraph:** Grafo direcionado com BFS ate max_depth
        - **OutlineSynthesizer:** Gera outlines com templates tematicos
        - **RAGEvolved:** Roteia entre answer_simple e answer_structured
        
        O RAG Evolved alimenta diretamente o Deep Research (R102) com citacoes em grafo.
        """)

# =====================================================================
# TAB 6: CONSULTATION
# =====================================================================
with tabs[6]:
    st.title("🔎 Consultation Framework")
    st.markdown("""
    Busque, navegue e consulte todo o historico de producao do ecossistema.
    Este framework integra as funcionalidades de consulta academica,
    producoes anteriores, especificacoes e ferramentas MCP.
    """)

    tab_cons_search, tab_cons_prods, tab_cons_specs, tab_cons_mcp = st.tabs([
        "🔎 Busca Academica", "📁 Producoes", "📋 Specs", "🔧 MCP Tools"
    ])

    with tab_cons_search:
        section_header("Busca Academica Multiplataforma",
                       "Consulte artigos em arXiv, OpenAlex, Crossref, Semantic Scholar e mais.",
                       "🔎")
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_topic = st.text_input("Topico de pesquisa", "quantum machine learning ethics", 
                                         key="cons_search_topic")
        with col_s2:
            search_limit = st.slider("Max resultados", 1, 20, 5, key="cons_search_limit")
        platforms = st.multiselect(
            "Plataformas",
            ["arxiv", "openalex", "crossref", "semantic_scholar", "github", "kaggle"],
            default=["arxiv"], key="cons_platforms"
        )
        if st.button("🔎 Buscar", type="primary", use_container_width=True, key="cons_search_btn"):
            with st.spinner("Consultando APIs academicas..."):
                results = search_academic(search_topic, platforms, search_limit)
            if results:
                st.success(f"{len(results)} resultados encontrados")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning("Nenhum resultado encontrado (ou APIs indisponiveis). "
                          "As buscas requerem conexao com a internet e podem falhar "
                          "em ambientes offline.")

    with tab_cons_prods:
        section_header("Producoes Cientificas Anteriores",
                       "Pastas de producao geradas pelo pipeline de pesquisa.",
                       "📁")
        producoes = list_producoes()
        if producoes:
            for prod in producoes[:10]:
                with st.expander(f"📁 {prod['folder']}"):
                    st.markdown(f"**Criado em:** {prod['created']}")
                    st.markdown(f"**PDFs:** {'Sim' if prod['has_pdfs'] else 'Nao'}")
                    st.markdown(f"**Markdowns:** {'Sim' if prod['has_md'] else 'Nao'}")
                    if prod.get("manifest"):
                        show_json(prod["manifest"])
        else:
            st.info("Nenhuma producao encontrada em producao_cientifica/. "
                   "As producoes serao listadas apos executar o pipeline de pesquisa.")

    with tab_cons_specs:
        section_header("Especificacoes Formais (SDD)",
                       "Todas as especificacoes de ciclo registradas no formato SPEC-935-R*.",
                       "📋")
        specs = list_specs()
        if specs:
            st.write(f"{len(specs)} especificacoes encontradas")
            for spec in specs:
                st.markdown(f"- **{spec['filename']}**: {spec['title']}")
        else:
            st.info("Nenhuma spec encontrada em specs/.")

    with tab_cons_mcp:
        section_header("Ferramentas MCP Disponiveis",
                       f"{len(MCP_TOOLS)} ferramentas registradas no servidor MCP.",
                       "🔧")
        st.dataframe(MCP_TOOLS, use_container_width=True)
        st.caption("Todas as ferramentas sao acessiveis via MCP Server stdio JSON-RPC "
                  "ou via API Gateway FastAPI REST.")

# =====================================================================
# TAB 7: SYSTEM
# =====================================================================
with tabs[7]:
    st.title("⚙️ System — Administracao")
    st.markdown("""
    Painel de administracao do ecossistema: status do orquestrador,
    seguranca MCP, pipeline CI/CD e qualidade.
    """)

    tab_sys_status, tab_sys_security, tab_sys_cicd, tab_sys_legal = st.tabs([
        "📊 Status", "🔒 Seguranca (R100)", "🚀 CI/CD (R106)", "⚖️ Juridico"
    ])

    with tab_sys_status:
        section_header("Status do Ecossistema",
                       "Informacoes em tempo real do orquestrador e subsistemas.",
                       "📊")
        if st.button("🔄 Atualizar Status", key="sys_refresh"):
            status = orch.status()
            agents = orch.list_agents()
            c1, c2, c3 = st.columns(3)
            c1.metric("Agentes Registrados", len(agents))
            c2.metric("Tarefas Ativas", str(status.get("tasks", status.get("active_tasks", 0))))
            c3.metric("Subsistemas", str(len(status.keys())))
            with st.expander("Status JSON"):
                show_json(status)
            with st.expander("Agentes JSON"):
                show_json(agents)

    with tab_sys_security:
        section_header("MCP Security (R100)",
                       "Camada de seguranca do servidor MCP.",
                       "🔒")
        st.markdown("""
        **4 Componentes de Seguranca:**

        1. **MCPGuard** — Validacao de argumentos contra JSON Schema + wrap de handlers
        2. **AuditLogger** — Registro estruturado com timestamp, ferramenta, args sanitizados, resultado
        3. **ToolVetter** — Deteccao de:
           - Prompt injection (11 patterns)
           - Command injection (6 patterns)  
           - Path traversal
           - SQL injection
        4. **RateLimiter** — Token bucket por caller com max_calls/window_seconds configuravel

        **Status:** Ativo em todas as 14 ferramentas MCP.
        **23 testes TDD** | Score: 9.5/10
        """)

    with tab_sys_cicd:
        section_header("CI/CD Pipeline (R106)",
                       "Infraestrutura de qualidade profissional.",
                       "🚀")
        st.markdown("""
        **GitHub Actions (`.github/workflows/ci.yml`):**
        - **Job 1 — Lint:** Ruff check + format (Python 3.12)
        - **Job 2 — Test:** Matrix Python 3.10-3.14, pytest full suite
        - **Job 3 — Package:** Build 3 pacotes pip + verify imports

        **Scripts de Qualidade:**
        - `scripts/quality_report.py` — Score 0-10, cobertura, lint, recomendacoes
        - `scripts/check_coverage.py` — Gate: testes OK, coverage >= 80%, lint OK
        - `scripts/run_full_suite.sh` — Suite completa com modo --ci

        **18 testes TDD** | Score: 9.2/10
        """)

        quality = get_quality_summary()
        if quality.get("quality_score"):
            cq1, cq2, cq3 = st.columns(3)
            cq1.metric("Score", f'{quality["quality_score"].get("overall_score", "N/A")}/10')
            cq2.metric("Status", quality.get("overall_status", "N/A"))
            cq3.metric("Testes", quality.get("test_results", {}).get("passed", 0))
            if quality.get("recommendations"):
                st.subheader("Recomendacoes")
                for rec in quality["recommendations"]:
                    st.markdown(f"- {rec}")

        if st.button("🔄 Executar Quality Report", key="sys_qr"):
            import subprocess
            with st.spinner("Gerando relatorio de qualidade..."):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "quality_report.py"), "--quick", "--json"],
                    capture_output=True, text=True, timeout=30
                )
                output = result.stdout.strip()
                json_start = output.find("{")
                if json_start >= 0:
                    data = json.loads(output[json_start:])
                    show_json(data)

    with tab_sys_legal:
        section_header("⚖️ Visao Juridica",
                       "Avaliacao de impacto juridico, LGPD, compliance e riscos.",
                       "⚖️")
        legal_corpus = st.text_area(
            "Texto para analise juridica",
            "Pesquisa envolvendo LGPD, consentimento informado, licenca Creative Commons, "
            "dados pessoais e conformidade regulatoria.",
            height=150, key="sys_legal_corpus"
        )
        if st.button("⚖️ Analisar Impacto Juridico", key="sys_legal_btn"):
            params = build_legal_params(
                titulo="Analise Juridica do Artefato",
                corpus=legal_corpus,
                palavras_chave_csv="lgpd, compliance, licenca, consentimento",
                area_conhecimento="direito digital",
            )
            with st.spinner("Executando Legal Impact Scanner..."):
                result = orch.diagnose(
                    legal_corpus,
                    domain="direito digital",
                    include_legal_impact=True,
                    legal_params=params,
                )
            legal_section = result.get("legal_impact", {})
            if legal_section:
                summary = summarize_legal_impact_section(legal_section)
                lc1, lc2, lc3, lc4 = st.columns(4)
                lc1.metric("Score Juridico", summary["overall_score"])
                lc2.metric("Ganho Metacognitivo", summary["metacognitive_gain_score"])
                lc3.metric("Readiness", summary["legal_readiness"])
                lc4.metric("Flags de Risco", summary["high_risk_count"])
                if summary["high_risk_flags"]:
                    st.warning("Flags: " + ", ".join(summary["high_risk_flags"]))
            with st.expander("JSON Completo"):
                show_json(result)


# ── Footer ────────────────────────────────────────────────────────
st.divider()
st.caption(
    "OpenCode Ecosystem Core v3.0 — Pipeline Academico Agentivo | "
    "64 ciclos evolutivos | 1050 testes | Score medio 9.4/10 | "
    "[GitHub](https://github.com/MarceloClaro/opencode-ecosystem-core)"
)
