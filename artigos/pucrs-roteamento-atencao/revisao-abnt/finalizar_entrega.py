from pathlib import Path
import hashlib
import json
import shutil
import sys
import fitz

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parents[1]
sys.path.insert(0,str(PROJECT))
review=ROOT/'revisao-abnt'
pdf=review/'compilacao'/'dissertacao.pdf'
qa=json.loads((review/'conferencia_pdf.json').read_text(encoding='utf-8'))
assert qa['pages']==len(fitz.open(pdf))
assert not qa['boundary_findings']
assert not qa['unresolved_markers_count']
assert all(qa['table_call_counts'].values())
log=(review/'compilacao'/'dissertacao.log').read_text(encoding='utf-8')
assert 'Overfull' not in log
assert 'Missing character' not in log
assert 'undefined' not in log
out=ROOT/'output'/'pdf';out.mkdir(parents=True,exist_ok=True)
shutil.copy2(pdf,out/'dissertacao-abnt.pdf')
shutil.copy2(pdf,ROOT/'dissertacao.pdf')

from marceloclaro.orchestrator import MarceloClaroOrchestrator
orchestrator=MarceloClaroOrchestrator(auto_load_agents=False)
graph=orchestrator.nanogranulate('Revisão editorial e normativa ABNT da dissertação: conteúdo, referências, composição e conferência visual',expected_artifact=str(out/'dissertacao-abnt.pdf'))
plan={'orchestrator':'MarceloClaroOrchestrator','graph_id':graph.graph_id,'nodes_count':len(graph.nodes),'kind':'decomposição determinística consultada; não representa execução de agentes do catálogo'}
(review/'consulta_orquestrador.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')

from evolution import evolution_registry
cycle=evolution_registry.record(
    objective='Revisão editorial e ABNT atualizada da dissertação PUCRS de roteamento inspirado em atenção',
    changes=['Apresentação NBR14724 corrigida2025, citações10520:2023 e referências6023:2025',
             '51 referências conferidas em fontes primárias; autor-data e correspondência integral',
             'Escopo científico corrigido: reais versus floats, intervalos exploratórios, agrupamento, sementes e cartões sem execução',
             'PDF97 páginas e fonte consolidada; QA sem referências indefinidas, caixas excedentes ou caracteres ausentes',
             'Backup original e pendências autorais/institucionais preservados'],
    score=None,
    lessons=['Adequação editorial não equivale à validação externa ou aprovação institucional.',
             'Normalização softmax não demonstra calibração probabilística.',
             'A alteração de qw com cobertura unitária reescala a perda; não testa outro ranking do oráculo.'])
(review/'ciclo_revisao.json').write_text(json.dumps({'round_id':cycle.round_id,'objective':cycle.objective,'audited':cycle.audited,'score':cycle.score},ensure_ascii=False,indent=2),encoding='utf-8')
report=review/'relatorio_revisao_abnt.md'
report.write_text(report.read_text(encoding='utf-8')+'\nRegistro evolutivo da revisão: **'+cycle.round_id+'**, sem escore atribuído e sem auditoria externa declarada.\n',encoding='utf-8')
files=[out/'dissertacao-abnt.pdf',ROOT/'dissertacao-abnt.tex',ROOT/'dissertacao.tex',report,review/'auditoria_referencias.json',review/'conferencia_pdf.json',review/'manifesto_fontes.json']
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(review/'manifesto_entrega.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pdf':str(out/'dissertacao-abnt.pdf'),'pages':qa['pages'],'bibliography':qa['bibliography_entries'],'cycle':cycle.round_id,'sha256':manifest['output/pdf/dissertacao-abnt.pdf']},ensure_ascii=False))
