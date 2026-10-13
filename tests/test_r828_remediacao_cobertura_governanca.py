"""R828: fronteiras reais do primário e interpretação delimitada do diagnose."""
from types import SimpleNamespace

import pytest


def primary_and_bus(monkeypatch):
    import marceloclaro.orchestrator as module
    calls=[]
    ledger={'marceloclaro':.5}
    memory=SimpleNamespace(confidence_ledger=ledger,
        add_reflection=lambda **kwargs: ledger.update({kwargs['agent_id']:kwargs['score']}),
        record_observation=lambda **kwargs: calls.append(('observation',kwargs)))
    bus=SimpleNamespace(memory=memory,publish=lambda topic,payload,**kwargs: calls.append((topic,payload)))
    monkeypatch.setattr(module,'metabus',bus)
    primary=module.MarceloClaroOrchestrator.__new__(module.MarceloClaroOrchestrator)
    primary.id='marceloclaro';primary.strict_sdd=True;primary.task_specs={};primary.results={};primary.task_stakes={}
    primary.trust=SimpleNamespace(learn=lambda action_id,success: calls.append(('trust',success)))
    primary.economy=SimpleNamespace(resolve=lambda task_id,success: calls.append(('stake',success)))
    return module,primary,bus,calls


def test_gate_barra_sem_spec_e_nao_recompensa_agente(monkeypatch):
    _,primary,_,calls=primary_and_bus(monkeypatch)
    primary.task_stakes['T1']={'agent':'A1'}
    primary.report_completion('T1','A1',{'result':'entrega sem vínculo'},True)
    event=next(payload for topic,payload in calls if topic=='task.complete')
    assert event['status']=='failed'
    assert event['sdd_verification']['verified'] is False
    assert ('trust',False) in calls and ('stake',False) in calls


def test_modo_legado_e_explicitamente_nao_verificado(monkeypatch):
    _,primary,_,calls=primary_and_bus(monkeypatch)
    primary.strict_sdd=False
    primary.report_completion('T1','A1','resultado legado',True)
    event=next(payload for topic,payload in calls if topic=='task.complete')
    assert event['status']=='completed' and event['sdd_verification']['verified'] is False
    assert event['sdd_verification']['status']=='legacy_unverified'


def test_spec_inexistente_bloqueia_mesmo_no_modo_legado(monkeypatch):
    _,primary,_,calls=primary_and_bus(monkeypatch)
    primary.strict_sdd=False
    primary.task_specs['T1']='SPEC-935-INEXISTENTE-REVISAO-R828'
    primary.report_completion('T1','A1','alegação sem contrato',True)
    event=next(payload for topic,payload in calls if topic=='task.complete')
    assert event['status']=='failed' and event['sdd_verification']['verified'] is False
    assert ('trust',False) in calls


def test_contrato_unitario_diagnose_nao_promove_confianca(monkeypatch):
    module,primary,bus,calls=primary_and_bus(monkeypatch)
    # Dublê de contrato: esta saída não é uma medição de cobertura.
    report={'noological':{},'evolutionary':{'total_gaps':58,'recommendation':'Fortalecer conhecimento'}}
    monkeypatch.setattr(module,'diagnostic_pipeline',SimpleNamespace(run=lambda *args,**kwargs:report))
    before=dict(bus.memory.confidence_ledger)
    result=primary.diagnose('Corpus com conceitos do projeto',domain='ecosystem')
    assert bus.memory.confidence_ledger==before
    assert any(topic=='observation' for topic,payload in calls)
    assert result['measurement_scope']['functional_validation'] is False


def test_diagnose_real_pipeline_retido_mede_sem_promover_confianca(monkeypatch):
    import hashlib
    from pathlib import Path
    module,primary,bus,calls=primary_and_bus(monkeypatch)
    from scanners.pipeline import DiagnosticPipeline
    monkeypatch.setattr(module,'diagnostic_pipeline',DiagnosticPipeline(domain='ecosystem'))
    corpus=(Path(__file__).parent/'fixtures/r828/retained-review.txt').read_text(encoding='utf-8')
    digest=hashlib.sha256(corpus.encode('utf-8')).hexdigest()
    before=dict(bus.memory.confidence_ledger)
    result=primary.diagnose(corpus,domain='ecosystem',corpus_mode='retained',
                            corpus_id='r828-human-review',expected_corpus_sha256=digest)
    assert bus.memory.confidence_ledger==before
    assert result['measurement']['measured_corpus_sha256']==digest
    assert result['measurement']['kind']=='retained_input_lexical'
    noo=result['noological']
    summary=noo['summary']
    assert noo['coverage']==round(100*summary['categories_covered']/summary['total_categories'])
    assert summary['categories_covered']+summary['categories_absent']==summary['total_categories']
    assert result['measurement']['functional_validation'] is False


def test_explanation_does_not_turn_scores_into_quality_or_probability():
    from marceloclaro.diagnostic_explanations import explain_diagnostic_report
    # Dados artificiais apenas para testar formatação, sem valor de medição.
    report={'noological':{'overall_coverage_pct':17,'total_categories':41,'categories_covered':7,'categories_absent':34,'gaps':[]},
            'teleological':{'score':.381,'gaps':[]},'noise':{'sps':.9451},'compression':{'cr':.9563}}
    text=explain_diagnostic_report(report)
    assert 'corpus' in text.lower() and '34' in text
    assert '48' not in text
    assert 'não certificam' in text.lower()
    assert '38% de aderência' not in text and 'diagnóstico íntegro' not in text
