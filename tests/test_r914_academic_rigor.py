"""Contraprovas científicas e de estado; regras locais não certificam ciência."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import pytest

def engine():
    name='academic.adversarial_research.board'
    assert importlib.util.find_spec('academic.adversarial_research') is not None, 'Motor adversarial ainda ausente'
    return importlib.import_module(name)

@pytest.fixture
def project(tmp_path):
    artifact=tmp_path/'research.md'
    artifact.write_text('Projeto real de teste: investigar aprendizagem. Conclusão relatada, sem validação externa.')
    return {'research_id':'study-1','spec_id':'SPEC-935-R914','artifact_path':str(artifact),
            'problem':'Como estudar aprendizagem?','objectives':['Descrever o caso'],
            'study_type':'qualitative','claims':[{'claim_id':'c1','statement':'Conclusão relatada',
             'claim_type':'inferential','source_refs':[],'evidence_status':'reported','limitations':[],
             'reviewer_agent_ids':[],'attributes':{}}],
            'sources':[],'context':{'humans':False,'indigenous_knowledge':False,'personal_data':False}}

def review(project,**kwargs): return engine().review_research(project,**kwargs)
def codes(report): return {x['code'] for x in report['objections']}

def test_critical_claim_without_evidence_is_blocked(project):
    r=review(project)
    assert r['review_status']=='blocked'
    assert 'claim_without_evidence' in codes(r)
    assert r['human_review_required'] is True

def test_novelty_requires_literature_support(project):
    project['claims'][0]['attributes']={'novelty_basis':'new_territory','claims_novelty':True}
    assert 'novelty_without_literature' in codes(review(project))

def test_operationalization_rejects_category_error(project):
    project['claims'][0]['attributes']={'epistemic_injustice_from_factual_error_alone':True}
    assert 'category_error' in codes(review(project))

def test_corpus_count_distinguishes_independence(project):
    project['context'].update(planned_responses=192,observed_responses=None,independent_units=None)
    project['claims'][0]['attributes']={'independent_observations':192}
    r=review(project)
    assert 'independence_not_established' in codes(r)
    assert r['context']['observed_responses'] is None

def test_causal_auditor_rejects_uncontrolled_effect_claim(project):
    project['study_type']='before_after'
    project['context']['control_group']=False
    project['claims'][0]['attributes']={'causal_claim':True}
    assert 'causality_not_identified' in codes(review(project))

def test_llm_cosine_similarity_not_translation_accuracy(project):
    project['claims'][0]['attributes']={'metric':'cosine_similarity','value':.90,'interpretation':'translation_accuracy'}
    assert 'metric_category_error' in codes(review(project))
    project['claims'][0]['attributes']['interpretation']='semantic_similarity'
    assert 'metric_category_error' not in codes(review(project))

def test_indigenous_governance_requires_contextual_review(project):
    project['context'].update(indigenous_knowledge=True,community_authorization=None)
    project['claims'][0]['attributes']={'public_source_implies_unrestricted_use':True}
    assert 'community_governance_pending' in codes(review(project))

def test_unverified_citation_not_promoted_to_verified(project,tmp_path):
    source=tmp_path/'citation.txt';source.write_text('Referência ainda não checada')
    project['sources']=[{'source_id':'s1','path':str(source),'locator':'linha 1','verification':'not_checked'}]
    project['claims'][0].update(source_refs=['s1'],evidence_status='verified')
    r=review(project)
    assert r['claims'][0]['evidence_status']!='verified'
    assert r['evidence_manifest'][0]['verification_scope']=='local_artifact_integrity_only'

def test_negative_evidence_not_suppressed(project):
    project['sources']=[{'source_id':'negative-case','path':project['artifact_path'],'locator':'parágrafo 1'}]
    project['claims'][0]['source_refs']=['negative-case']
    project['claims'][0]['evidence_status']='contradicted'
    r=review(project)
    assert r['claims'][0]['evidence_status']=='contradicted'
    assert 'negative_evidence' in codes(r)
    assert next(g for g in r['gates'] if g['gate']=='G5')['passed'] is False

def test_examiner_waits_for_candidate_answer(project,tmp_path):
    from_module=engine()
    session=from_module.BancaSessionStore(tmp_path/'sessions')
    started=session.start(review(project))
    first=session.question(started['session_id'])
    assert len(first['questions'])==1
    again=session.question(started['session_id'])
    assert again['questions']==first['questions']
    response=session.answer(started['session_id'],'Ainda preciso recuperar a evidência e justificar a amostragem.')
    assert response['turn_kind']=='replica'
    assert len(response['questions'])==1
    assert 'resposta_modelo' not in response

def test_scoring_marks_unobserved_competence(project,tmp_path):
    store=engine().BancaSessionStore(tmp_path/'sessions')
    started=store.start(review(project))
    final=store.finish(started['session_id'])
    assert all(x['score'] is None for x in final['scores'])
    assert final['unanswered_objections']
    assert final['approved'] is False

def test_blackboard_metabus_evidence_trace(project):
    r=review(project)
    assert r['reviewed_artifact_hash']
    assert len(r['question_families'])==8
    assert all(x['target_claim_ids'] and x['responsible_agent'] for x in r['objections'])
    assert r['execution_scope']=='local_rule_checks'
    assert r['llm_inference_executed'] is False

def test_existing_rigorous_board_backward_compatibility(project):
    from academic.rigorous_board import RigorousBoard
    before=RigorousBoard().review('Uma contribuição com lacuna e referências.',venue='auto').to_dict()
    report=review(project)
    after=RigorousBoard().review('Uma contribuição com lacuna e referências.',venue='auto').to_dict()
    assert before['status']==after['status']
    assert before['overall_score']==after['overall_score']
    assert report['legacy_board']['binding'] is False

def test_agent_registry_no_duplicate_ids():
    registry=engine().SPECIALISTS
    assert len(registry)==34
    assert len({x['agent_id'] for x in registry})==34
    assert all(x['required_evidence'] and x['limitations'] and x['test_case'] for x in registry)

def test_budget_timeout_and_cancellation(project):
    r=review(project,max_steps=1)
    assert r['execution_complete'] is False
    assert r['unresolved_gaps']
    r=review(project,cancelled=True)
    assert r['review_status']=='cancelled'
    assert r['specialist_results']==[]
    with pytest.raises(ValueError): review(project,timeout_seconds=True)

def test_sdd_green_without_fabricated_external_validation(project):
    r=review(project)
    assert r['external_validation'] is False
    assert r['human_review_required'] is True
    assert r['scientifically_approved'] is False
    assert {x['gate'] for x in r['gates']}=={f'G{i}' for i in range(7)}

def test_qualitative_study_does_not_require_statistical_power(project):
    r=review(project)
    assert not any('poder estatístico' in x['required_evidence'].lower() for x in r['objections'])

def test_changed_artifact_requires_new_review(project):
    before=review(project)
    Path(project['artifact_path']).write_text('Artefato alterado depois da leitura')
    after=review(project)
    assert before['reviewed_artifact_hash']!=after['reviewed_artifact_hash']


def test_contract_only_completion_does_not_request_confidence_learning(monkeypatch):
    from mci.blackboard import Blackboard,BlackboardTask,AgentCard,metabus
    board=object.__new__(Blackboard)
    task=BlackboardTask('fixture-task','Auditoria local',[],{})
    task.assigned_to='fixture-auditor';task.status='assigned'
    board.tasks={task.task_id:task}
    board.registry={'fixture-auditor':AgentCard('fixture-auditor','Fixture','Somente teste',[],{})}
    published=[]
    monkeypatch.setattr(metabus,'publish',lambda topic,*args,**kwargs:published.append(topic))
    board._handle_completion({'source':'marceloclaro','payload':{'task_id':task.task_id,'agent_id':'fixture-auditor','status':'completed','result':{'scope':'local_contract'},'learning_scope':'contract_only'}})
    assert task.status=='completed'
    assert board.registry['fixture-auditor'].status=='available'
    assert 'metacognition.reflect_request' not in published


def test_input_cannot_claim_specialist_execution(project):
    project['claims'][0]['reviewer_agent_ids']=['invented-reviewer']
    report=review(project)
    assert 'invented-reviewer' not in report['claims'][0]['reviewer_agent_ids']


def test_orchestration_failure_is_partial_and_stops(project):
    def fail(*args): raise RuntimeError('Fixture: executor indisponível')
    report=review(project,on_start=fail)
    assert report['execution_complete'] is False
    assert report['review_status']=='blocked'
    assert report['specialist_results'][0]['status']=='failed'
    assert report['gates'][4]['passed'] is False


def test_flow_orders_evidence_before_examination_and_remediation(project):
    report=review(project)
    stages=[x['stage'] for x in report['flow']]
    assert stages.index('evidence_ledger')<stages.index('specialists')<stages.index('adversarial_examiner')
    assert stages.index('adversarial_examiner')<stages.index('legacy_board')<stages.index('remediation')


def test_rubric_scores_require_observed_answer_and_document(project,tmp_path):
    import hashlib
    source=tmp_path/'rubric.md';source.write_text('Critério: fundamentação, de 0 a 2. Documento de treinamento.')
    rubric={'source_path':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'locator':'parágrafo 1','criteria':[{'criterion_id':'fundamentacao','maximum':2}]}
    store=engine().BancaSessionStore(tmp_path/'sessions')
    start=store.start(review(project),rubric)
    with pytest.raises(ValueError): store.rate(start['session_id'],'fundamentacao',1,['unobserved'],'Avaliador declarou nota','fixture-human')
    store.answer(start['session_id'],'Minha interpretação ainda não foi confrontada com fontes rivais.',start['turn_id'])
    result=store.rate(start['session_id'],'fundamentacao',1,[start['turn_id']],'Resposta reconheceu a limitação, sem apresentar a evidência.','fixture-human')
    assert result['scores'][0]['score']==1
    assert result['scores'][0]['status']=='reviewer_reported_simulated'
    assert result['approved'] is False
    with pytest.raises(ValueError): store.rate(start['session_id'],'fundamentacao',3,[start['turn_id']],'Fora do máximo','fixture-human')


def test_malformed_counts_are_rejected(project):
    project['claims'][0]['attributes']={'independent_observations':'192'}
    with pytest.raises(ValueError): review(project)


def test_service_facade_and_mcp_are_present():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    from integrations import ecosystem_mcp
    assert callable(getattr(MarceloClaroOrchestrator,'academic_rigor_action',None))
    assert callable(getattr(ecosystem_mcp,'ecosystem_research_rigor',None))


@pytest.mark.parametrize('value',[1,'true',None])
def test_claim_flags_are_strict_booleans(project,value):
    project['claims'][0]['attributes']['causal_claim']=value
    with pytest.raises(ValueError): review(project)


def test_failed_contract_does_not_satisfy_gates(project):
    result=review(project,on_result=lambda *args:{'verification':{'verified':False},'task_status':'failed'})
    assert result['execution_complete'] is False
    assert all(g['passed'] is False for g in result['gates'])
    assert result['claims'][0]['reviewer_agent_ids']==[]


def test_stale_banca_rejected_at_start_and_report(project,tmp_path):
    store=engine().BancaSessionStore(tmp_path/'session')
    report=review(project);started=store.start(report)
    Path(project['artifact_path']).write_text('Texto modificado.')
    with pytest.raises(ValueError): store.start(report)
    assert store.finish(started['session_id'])['status']=='stale_artifact'
    with pytest.raises(ValueError): store.answer(started['session_id'],'Uma resposta ao documento antigo',started['turn_id'])


def test_cli_and_mcp_use_same_primary(monkeypatch,capsys):
    import asyncio
    from marceloclaro.rigor_cli import run_rigor_cli
    from integrations import ecosystem_mcp
    calls=[]
    class Primary:
        def academic_rigor_action(self,config):
            calls.append(config);return {'status':'pending_registration','scientific_validation':False}
    primary=Primary()
    assert run_rigor_cli(['status'],primary)==0
    assert json.loads(capsys.readouterr().out)['scientific_validation'] is False
    monkeypatch.setattr(ecosystem_mcp,'get_library_orchestrator',lambda:primary)
    assert asyncio.run(ecosystem_mcp.ecosystem_research_rigor({'operation':'status'}))['scientific_validation'] is False
    assert calls==[{'operation':'status'}]*2


def test_service_plan_does_not_count_declared_url_as_retrieval(project,tmp_path):
    from academic.adversarial_research.service import AdversarialResearchService
    project['sources']=[{'source_id':'url1','url':'https://example.invalid/not-retrieved','locator':'declared'}]
    service=AdversarialResearchService(None,tmp_path/'state')
    result=service.action({'operation':'plan','project':project})
    assert result['local_sources_inspected']==0
    assert result['external_sources_retrieved']==0


@pytest.mark.parametrize('attributes,code',[
    ({'novelty_basis':'new_territory'},'territory_not_novelty'),
    ({'epistemic_injustice_from_factual_error_alone':True},'category_error'),
    ({'independent_observations':192},'independence_not_established'),
    ({'causal_claim':True},'causality_not_identified'),
    ({'public_source_implies_unrestricted_use':True},'public_is_not_authorization'),
    ({'linguistic_reconstruction_from_metric':True},'metric_not_linguistic_reconstruction'),
    ({'timeline_implies_professional_release':True},'timeline_not_permission'),
    ({'conceptual_affinity_implies_empirical_international':True},'affinity_not_empirical_scope')])
def test_eight_adversarial_benchmark_cases(project,attributes,code):
    project['context']['indigenous_knowledge']=True
    project['claims'][0]['attributes']=attributes
    result=review(project)
    found=[o for o in result['objections'] if o['code']==code]
    assert len(found)==1
    assert found[0]['scientific_rationale'] and found[0]['required_evidence']
    assert found[0]['target_claim_ids']==['c1']
    assert found[0]['severity'] in {'critical','major'}
    project['claims'][0]['attributes']={}
    assert code not in codes(review(project))


def test_registered_profiles_close_real_a2a_contracts_without_confidence_gain(project,tmp_path):
    import copy
    from academic.adversarial_research.service import AdversarialResearchService
    from agents.lifecycle import AgentLifecycleService
    from marceloclaro.orchestrator import MarceloClaroOrchestrator,blackboard,metabus
    from academic.adversarial_research.registry import SPECIALISTS
    primary=MarceloClaroOrchestrator(auto_load_agents=False)
    lifecycle=AgentLifecycleService()
    for role in SPECIALISTS:
        checked=lifecycle.validate(role['agent_id'])
        assert checked['definition_validated'] is True
        assert checked['profile']['allow_edit'] is False
        assert checked['profile']['parent']=='marceloclaro'
        assert primary.agent_profile_action({'operation':'register','agent_id':role['agent_id']})['registered'] is True
    confidence=copy.deepcopy(metabus.memory.confidence_ledger)
    report=AdversarialResearchService(primary,tmp_path/'state').review(project,timeout_seconds=120)
    assert report['execution_complete'] is True
    assert len(report['specialist_results'])==len(report['selected_agent_ids'])
    for result in report['specialist_results']:
        contract=result['orchestration']
        assert contract['verification']['verified'] is True
        assert blackboard.tasks[contract['task_id']].status=='completed'
        assert contract['confidence_promoted'] is False
    assert primary.task_stakes=={}
    assert confidence==metabus.memory.confidence_ledger


def test_service_unknown_spec_cannot_pass_g0(project,tmp_path,monkeypatch):
    from academic.adversarial_research.service import AdversarialResearchService
    project['spec_id']='does-not-exist'
    # Sem tarefas nesta sonda: o ponto medido é a ausência de spec real.
    service=AdversarialResearchService(None,tmp_path/'state')
    from academic.adversarial_research import service as module
    monkeypatch.setattr(module,'review_research',lambda value,**kwargs:review(value,max_steps=1))
    result=service.review(project)
    assert result['specification_loaded'] is False
    assert result['gates'][0]['passed'] is False
    assert result['review_status']=='blocked'


def test_declared_unretrieved_literature_cannot_satisfy_novelty(project):
    project['sources']=[{'source_id':'s1','url':'https://example.invalid/source','locator':'declarado'}]
    project['context']['literature_source_refs']=['s1']
    project['claims'][0]['attributes']['claims_novelty']=True
    assert 'novelty_without_literature' in codes(review(project))


def test_failed_output_preserves_already_detected_critical_objection(project):
    result=review(project,on_result=lambda *args:{'verification':{'verified':False},'task_status':'failed'},on_start=None,profile_scope='pilot')
    assert result['execution_complete'] is False
    assert 'claim_without_evidence' in codes(result)


def test_changed_rubric_makes_banca_report_stale(project,tmp_path):
    import hashlib
    source=tmp_path/'rubric.md';source.write_text('Rubrica inicial de treinamento')
    rubric={'source_path':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'locator':'parágrafo 1','criteria':[{'criterion_id':'clareza','maximum':2}]}
    store=engine().BancaSessionStore(tmp_path/'session')
    session=store.start(review(project),rubric)
    source.write_text('Rubrica diferente, após a abertura da banca')
    assert store.finish(session['session_id'])['status']=='stale_rubric'
