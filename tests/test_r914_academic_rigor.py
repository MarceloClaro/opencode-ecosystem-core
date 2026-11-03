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
    project['claims'][0]['evidence_status']='contradicted'
    r=review(project)
    assert r['claims'][0]['evidence_status']=='contradicted'
    assert 'negative_evidence' in codes(r)

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
