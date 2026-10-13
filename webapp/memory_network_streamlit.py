"""R829: UI não bloqueante, demonstração isolada e detalhes por sessão."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from webapp.memory_network_visualizer import (  # noqa: E402 — inicialização do caminho da execução avulsa
    CoreMemoryNetworkSource, MemoryNetworkSimulator, MemoryNetworkVisualizer,
)
from webapp.memory_network_view import build_network_html  # noqa: E402 — mesmo ponto de entrada avulso


def render_memory_network_streamlit(orchestrator=None, research_result=None):
    import streamlit as st

    st.subheader('Rede de memória, contexto e evidências')
    st.caption('Projeção dos registros do Core. Não revela pesos nem atenção interna de um LLM.')
    controls = st.columns([2,1,1])
    with controls[0]:
        mode = st.radio('Fonte da visualização', ['Dados locais', 'Demonstração'], horizontal=True,
                        key='memory_network_mode')
    with controls[1]:
        automatic = st.toggle('Atualização automática', value=True, key='memory_network_refresh')
    with controls[2]:
        motion = st.toggle('Animar atividade', value=True, key='memory_network_motion')
    types = st.multiselect('Tipos exibidos', ['consulta','memoria','contexto','agente','evidencia','resposta'],
                          default=['consulta','memoria','contexto','agente','evidencia','resposta'],
                          key='memory_network_types')
    if mode == 'Demonstração':
        st.warning('DEMONSTRAÇÃO: nós e fluxo simulados. Nenhum resultado tem valor probatório.')
        st.text_input('Consulta de demonstração', value='Como uma consulta usa memória e evidências?',
                      key='memory_network_demo_query')
    else:
        with st.form('memory_network_search'):
            query = st.text_input('Consultar memória local', max_chars=1000,
                                  help='Busca lexical nos registros existentes; não executa um LLM.')
            submitted = st.form_submit_button('Buscar e observar o fluxo')
        if submitted:
            try:
                if orchestrator is None:
                    from marceloclaro.orchestrator import MarceloClaroOrchestrator
                    coordinator = MarceloClaroOrchestrator(auto_load_agents=False)
                else:
                    coordinator = orchestrator
                result = coordinator.memory_network_query(query)
                st.session_state['memory_network_search_result'] = result
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
        if st.session_state.get('memory_network_search_result'):
            result = st.session_state['memory_network_search_result']
            st.caption(f"Última busca: {result['matches']} registros encontrados. Operação lexical local; inferência não executada.")
    if '_memory_network_source' not in st.session_state:
        st.session_state['_memory_network_source'] = CoreMemoryNetworkSource(ROOT)

    @st.fragment(run_every=1 if automatic else None)
    def render_snapshot():
        if mode == 'Demonstração':
            snapshot = MemoryNetworkSimulator().snapshot(st.session_state['memory_network_demo_query'])
        else:
            current_research = research_result or st.session_state.get('memory_network_research_result', {})
            exported_graph = current_research.get('graph_data') if isinstance(current_research,dict) else None
            if orchestrator is not None:
                snapshot = orchestrator.memory_network_snapshot(science_graph=exported_graph)
            else:
                snapshot = st.session_state['_memory_network_source'].snapshot(science_graph=exported_graph)
        visible = dict(snapshot)
        visible['nodes'] = [n for n in snapshot['nodes'] if n['type'] in types]
        ids = {n['id'] for n in visible['nodes']}
        visible['edges'] = [e for e in snapshot['edges'] if e['source'] in ids and e['target'] in ids]
        columns = st.columns(4)
        columns[0].metric('Nós na seleção', len(visible['nodes']))
        columns[1].metric('Arestas registradas',len(visible['edges']))
        columns[2].metric('Nós com evento recente',sum(n['active'] for n in visible['nodes']))
        columns[3].metric('Eventos na janela',len(snapshot['events']))
        choices = [n['id'] for n in visible['nodes']]
        labels = {n['id']: n['label'] for n in visible['nodes']}
        if choices:
            if st.session_state.get('memory_network_selected') not in choices:
                st.session_state['memory_network_selected'] = choices[0]
            selected = st.selectbox('Detalhes de um nó',choices,format_func=lambda ident: labels[ident],
                                    key='memory_network_selected')
        else:
            selected = None
            st.info('Nenhum nó nas fontes e filtros atuais. Não foi fabricada uma consulta.')
        st.iframe(build_network_html(visible,selected_id=selected,motion=motion),height=760,
                  alt='Mapa simultâneo: topologia por tipo e mapa de vetores com detalhes por nó')
        limits = snapshot['limits']
        st.caption(f"Visão simultânea: topologia por tipo + mapa de vetores (projeção hash determinística, sem semântica). "
                   f"Atividade: janela de {limits['activation_window_seconds']} segundos. "
                   f"Seleção limitada a {limits['max_nodes']} nós e {limits['max_edges']} arestas; "
                   f"{limits['omitted_nodes']} inclusões de nós omitidas. A animação não comprova inferência.")
        with st.expander('Eventos e origem dos registros'):
            st.dataframe(snapshot['events'], width='stretch')
            if snapshot['warnings']:
                st.write('Fontes ausentes, inválidas ou com janela limitada:')
                st.dataframe(snapshot['warnings'],width='stretch')
        with st.expander('Representação do terminal'):
            st.code(MemoryNetworkVisualizer(visible).render_ascii_graph(),language='text')
    render_snapshot()


if __name__ == '__main__':
    import streamlit as st
    st.set_page_config(page_title='Rede de memória — Core',layout='wide')
    render_memory_network_streamlit()
