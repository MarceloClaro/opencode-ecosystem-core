"""R829: observação local real, limites e separação de demonstração."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from webapp.memory_network_visualizer import (
    CoreMemoryNetworkSource, MemoryNetworkGraph, MemoryNetworkSimulator,
    MemoryNetworkVisualizer, NodeType,
)
from webapp.memory_network_view import build_network_html


def write_state(root, memory=None, events=()):
    state = root / '.mci_state'
    state.mkdir(exist_ok=True)
    (state / 'shared_memory.json').write_text(json.dumps(memory or {'episodic': [], 'semantic': {}}))
    (state / 'metabus_events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))


def event(topic, payload, ident='event-1', timestamp=100):
    return {'event_id': ident, 'timestamp': timestamp, 'topic': topic,
            'source': 'marceloclaro', 'payload': payload}


def test_real_flow_preserves_ids_and_does_not_reactivate_history(tmp_path):
    events = [event('task.post', {'task_id':'T1','description':'Consulta real'}),
              event('task.assigned', {'task_id':'T1','agent_id':'A1'}, 'event-2'),
              event('task.complete', {'task_id':'T1','agent_id':'A1','status':'completed','result':'Resposta registrada'},'event-3')]
    write_state(tmp_path, events=events)
    source = CoreMemoryNetworkSource(tmp_path, clock=lambda: 101)
    snap = source.snapshot()
    assert snap['mode']=='observed' and not snap['externally_validated']
    nodes={n['id']: n for n in snap['nodes']}
    assert nodes['task:T1']['label']=='Consulta real'
    assert nodes['response:T1']['label']=='Resposta registrada'
    assert nodes['agent:A1']['active']
    assert any(e['source']=='agent:A1' and e['target']=='response:T1' for e in snap['edges'])
    source.clock=lambda: 200
    assert not any(n['active'] for n in source.snapshot()['nodes'])


def test_opening_view_does_not_write_or_fabricate_flow(tmp_path):
    write_state(tmp_path)
    before={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    snap=CoreMemoryNetworkSource(tmp_path).snapshot()
    assert snap['nodes']==[] and snap['edges']==[]
    assert before=={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


def test_memory_and_evidence_are_not_calibrated_probabilities(tmp_path):
    write_state(tmp_path, {'episodic':[{'id':'M1','context':'Memória real','timestamp':100}],
                           'semantic':{'contexto':{'lesson':'Conceito local'}}})
    graph={'entities':{'E1':{'id':'E1','name':'Entidade','type':'concept','evidence':['V1']}},
           'relations':{},'evidence':{'V1':{'id':'V1','text':'Fragmento','confidence':.8,'source':'local'}}}
    snap=CoreMemoryNetworkSource(tmp_path,clock=lambda:101).snapshot(science_graph=graph)
    nodes={n['id']:n for n in snap['nodes']}
    assert nodes['memory:M1']['label']=='Memória real'
    assert nodes['r102.entity:E1']['original_id']=='E1'
    assert nodes['r102.evidence:V1']['relevance'] is None
    assert not nodes['r102.evidence:V1']['metric_calibrated']
    assert any(e['target']=='r102.evidence:V1' for e in snap['edges'])


def test_public_r102_export_is_consumed_without_mutation(tmp_path):
    from agentic_science_v2.evidence_graph import EvidenceGraph
    graph=EvidenceGraph(); one=graph.add_entity('Origem'); two=graph.add_entity('Destino')
    graph.add_relation(one.id,two.id,'CITES',weight=2.5)
    before=graph.to_json()
    snap=CoreMemoryNetworkSource(tmp_path).snapshot(science_graph=graph)
    assert any(e['label']=='CITES' and e['weight']==2.5 for e in snap['edges'])
    assert graph.to_json()==before


@pytest.mark.parametrize('bad',[float('nan'),float('inf'),True,'not-a-number'])
def test_unknown_metrics_remain_unknown(tmp_path,bad):
    write_state(tmp_path)
    snap=CoreMemoryNetworkSource(tmp_path).snapshot(registry=[{'agent_id':'A','name':'Agente','confidence_score':bad,'status':'available'}])
    node=next(n for n in snap['nodes'] if n['id']=='agent:A')
    assert node['relevance'] is None and node['metadata']['internal_confidence'] is None
    assert not node['active']
    json.dumps(snap,allow_nan=False)


def test_capacity_keeps_edges_with_existing_endpoints(tmp_path):
    events=[event('task.post',{'task_id':f'T{i}','description':str(i)},f'E{i}') for i in range(30)]
    write_state(tmp_path,events=events)
    snap=CoreMemoryNetworkSource(tmp_path,max_nodes=8,max_edges=5).snapshot()
    assert len(snap['nodes'])<=8 and len(snap['edges'])<=5
    ids={n['id'] for n in snap['nodes']}
    assert all(e['source'] in ids and e['target'] in ids for e in snap['edges'])
    assert snap['limits']['omitted_nodes']>0


def test_partial_json_and_log_rotation_are_visible(tmp_path):
    write_state(tmp_path, events=[event('task.post',{'task_id':'T1','description':'Primeiro'})])
    source=CoreMemoryNetworkSource(tmp_path)
    assert source.snapshot()['nodes']
    (tmp_path/'.mci_state/shared_memory.json').write_text('{')
    (tmp_path/'.mci_state/metabus_events.jsonl').write_text('{partial')
    snap=source.snapshot()
    assert snap['warnings'] and snap['nodes']==[]
    write_state(tmp_path,events=[event('task.post',{'task_id':'T2','description':'Após rotação'})])
    assert any(n['id']=='task:T2' for n in source.snapshot()['nodes'])


def test_future_events_do_not_claim_current_activation(tmp_path):
    write_state(tmp_path,events=[event('task.post',{'task_id':'T1','description':'Futuro'},timestamp=300)])
    assert not any(n['active'] for n in CoreMemoryNetworkSource(tmp_path,clock=lambda:100).snapshot()['nodes'])


def test_demo_is_isolated_and_explicit(tmp_path):
    write_state(tmp_path)
    before=(tmp_path/'.mci_state/shared_memory.json').read_bytes()
    snap=MemoryNetworkSimulator().snapshot('Pergunta demonstrativa',now=100)
    assert snap['mode']=='demonstration' and all(n['synthetic'] for n in snap['nodes'])
    assert 'DEMONSTRAÇÃO' in MemoryNetworkVisualizer(snap).render_ascii_graph()
    assert CoreMemoryNetworkSource(tmp_path).snapshot()['nodes']==[]
    assert (tmp_path/'.mci_state/shared_memory.json').read_bytes()==before


def test_terminal_controls_and_html_are_inert():
    graph=MemoryNetworkGraph()
    graph.add_node('n',NodeType.MEMORY,'evil\x1b[2J</script><script>alert(7)</script>')
    snap=graph.to_dict(now=100)
    text=MemoryNetworkVisualizer(snap).render_ascii_graph(color=False)
    assert '\x1b' not in text
    html=build_network_html(snap)
    assert '</script><script>alert(7)</script>' not in html
    assert 'textContent' in html and 'prefers-reduced-motion' in html


def test_cli_once_json_is_finite_and_does_not_require_streamlit(tmp_path):
    write_state(tmp_path,events=[event('task.post',{'task_id':'T1','description':'Consulta local'})])
    p=subprocess.run([sys.executable,'-m','webapp.memory_network_visualizer','--root',str(tmp_path),'--once','--json'],capture_output=True,text=True,timeout=20)
    assert p.returncode==0, p.stderr
    snap=json.loads(p.stdout)
    assert snap['mode']=='observed' and any(n['id']=='task:T1' for n in snap['nodes'])


def test_non_tty_frames_are_bounded_without_cursor_controls(tmp_path):
    write_state(tmp_path)
    p=subprocess.run([sys.executable,'-m','webapp.memory_network_visualizer','--root',str(tmp_path),'--frames','2','--interval','0.01'],capture_output=True,text=True,timeout=20)
    assert p.returncode==0 and p.stdout.count('REDE DE MEMÓRIA')==2
    assert '\x1b' not in p.stdout


def test_terminal_prioriza_consulta_recente_e_anima_somente_evento_real():
    from webapp.memory_network_visualizer import EdgeType
    graph=MemoryNetworkGraph()
    for i in range(40):
        graph.add_node(f'old{i}',NodeType.MEMORY,f'Histórico {i}',at=1)
    graph.add_node('query',NodeType.QUERY,'CONSULTA RECENTE',at=100)
    graph.add_node('memory',NodeType.MEMORY,'MEMÓRIA RECUPERADA',at=100)
    graph.add_edge('query','memory',EdgeType.RETRIEVAL,at=100)
    viewer=MemoryNetworkVisualizer(graph.to_dict(now=101))
    frame0=viewer.render_ascii_graph(frame=0)
    frame1=viewer.render_ascii_graph(frame=1)
    assert 'CONSULTA RECENTE' in frame0 and 'MEMÓRIA RECUPERADA' in frame0
    assert 'query -> memory' in frame0 and 'query => memory' in frame1
    historic=MemoryNetworkVisualizer(graph.to_dict(now=106))
    assert historic.render_ascii_graph(frame=0)==historic.render_ascii_graph(frame=1)


def test_primary_snapshot_observes_without_delegation(tmp_path,monkeypatch):
    from types import SimpleNamespace
    import marceloclaro.orchestrator as module
    write_state(tmp_path,events=[event('task.post',{'task_id':'T1','description':'Local'})])
    primary=module.MarceloClaroOrchestrator.__new__(module.MarceloClaroOrchestrator)
    primary.id='marceloclaro'
    primary._memory_network_source=CoreMemoryNetworkSource(tmp_path)
    monkeypatch.setattr(module,'blackboard',SimpleNamespace(registry={}))
    snap=primary.memory_network_snapshot()
    assert snap['coordinator']=='marceloclaro' and any(n['id']=='task:T1' for n in snap['nodes'])


def test_existing_graph_browser_uses_exported_evidence_counts():
    from webapp.consultation_helpers import get_evidence_graph_summary
    data={'entities':{'e':{'id':'e','name':'Origem','type':'concept'}},
          'relations':{},'evidence':{'v':{'id':'v','source':'arquivo local'}}}
    summary=get_evidence_graph_summary(data)
    assert summary['entity_count']==summary['evidence_count']==1
    assert 'error' not in summary


def test_real_memory_query_is_observable_without_score_promotion(tmp_path,monkeypatch):
    import importlib
    module=importlib.import_module('mci.metabus')
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    write_state(tmp_path,{'episodic':[{'id':'M1','agent_id':'a','context':'memória RAG local','reflection':'registro local','timestamp':100}], 'semantic':{},'confidence_ledger':{'a':.5}})
    monkeypatch.setattr(module,'MEMORY_FILE',str(tmp_path/'.mci_state/shared_memory.json'))
    monkeypatch.setattr(module,'EVENTS_FILE',str(tmp_path/'.mci_state/metabus_events.jsonl'))
    memory=module.MetacognitiveMemory()
    monkeypatch.setattr(module.metabus,'memory',memory)
    primary=MarceloClaroOrchestrator.__new__(MarceloClaroOrchestrator);primary.id='marceloclaro'
    before=dict(memory.confidence_ledger)
    result=primary.memory_network_query('RAG',limit=5)
    snap=CoreMemoryNetworkSource(tmp_path).snapshot()
    assert result['verification']=='local_memory_search' and result['matches']==1
    assert memory.confidence_ledger==before
    assert any(n['type']=='consulta' and n['label']=='RAG' for n in snap['nodes'])
    assert any(e['label']=='recuperacao' for e in snap['edges'])


def test_memory_search_accepts_structured_legacy_lessons_without_writing(tmp_path,monkeypatch):
    import importlib
    module=importlib.import_module('mci.metabus')
    write_state(tmp_path,{'episodic':[], 'semantic':{'rag':{'lessons':[{'text':'RAG legado'}]},'invalid':None},'confidence_ledger':{'a':.5}})
    monkeypatch.setattr(module,'MEMORY_FILE',str(tmp_path/'.mci_state/shared_memory.json'))
    before=(tmp_path/'.mci_state/shared_memory.json').read_bytes()
    memory=module.MetacognitiveMemory()
    result=memory.search_memory('RAG')
    assert len(result)==1 and result[0]['kind']=='semantic' and result[0]['topic']=='rag'
    assert result[0]['lessons']==[{'text':'RAG legado'}]
    assert (tmp_path/'.mci_state/shared_memory.json').read_bytes()==before
