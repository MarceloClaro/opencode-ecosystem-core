"""R920: ensaio sintético limitado, sem equivalência a revisão científica."""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

import pytest

STAGES = ('projeto','metodologia','qualificacao','analise','resultados','pre_defesa','defesa')


def module():
    name = 'academic.adversarial_research.simulation'
    assert importlib.util.find_spec(name) is not None, 'Adaptador acadêmico MiroFish ausente'
    return importlib.import_module(name)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def case(cid='one', stage='metodologia', scenario='base', **kw):
    return dict(case_id=cid, stage=stage, group='banca_interdisciplinar',
                scenario=scenario, rounds=2, agents=4, **kw)


def forbidden(*_a, **_kw):
    raise AssertionError('Efeito proibido na simulação local')


def safeguards(value):
    for field in ('scientifically_approved','external_validation','agent_inference_executed',
                  'llm_inference_executed','confidence_promoted'):
        assert value[field] is False
    assert value['human_review_required'] is True


@pytest.fixture
def project(tmp_path):
    artifact = tmp_path/'research.md'
    artifact.write_text('Pesquisa qualitativa com contradições e limites; sem resultado empírico nesta fixture.')
    source = tmp_path/'negative.md'
    source.write_text('Evidência negativa: a mudança não foi uniforme.')
    return {'research_id':'r920-demo','spec_id':'SPEC-935-R920','artifact_path':str(artifact),
        'problem':'Como compreender as diferenças entre casos?',
        'objectives':['Examinar interpretações alternativas'],'study_type':'qualitative',
        'context':{'humans':False,'personal_data':False,'control_group':False},
        'sources':[{'source_id':'s1','path':str(source),'locator':'linha 1',
                    'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'verification':'not_checked'}],
        'claims':[{'claim_id':'c1','statement':'A conclusão uniforme é contradita por casos negativos.',
            'claim_type':'inferential','source_refs':['s1'],'evidence_status':'contradicted',
            'limitations':[],'reviewer_agent_ids':[],'attributes':{}}]}


def test_plan_has_no_execution(project, monkeypatch):
    m = module()
    from academic.adversarial_research import board
    from mirofish.social.engine import SocialSimulationEngine
    monkeypatch.setattr(board,'review_research',forbidden)
    monkeypatch.setattr(m,'review_research',forbidden,raising=False)
    monkeypatch.setattr(SocialSimulationEngine,'run',forbidden)
    original = copy.deepcopy(project)
    plan = m.plan_simulation(project)
    assert project == original and plan['status'] == 'planned'
    assert plan['execution_started'] is plan['simulation_executed'] is False
    assert all(v == 0 for v in plan['usage'].values())
    assert plan['plan_sha256'] == digest({k:v for k,v in plan.items() if k!='plan_sha256'})
    assert plan['artifact_sha256'] == hashlib.sha256(Path(project['artifact_path']).read_bytes()).hexdigest()
    safeguards(plan)


def test_cases_are_deterministic_and_stage_specific(project):
    m = module()
    cases = [case(stage,stage) for stage in STAGES] + [
        case('divergent','defesa','banca_divergente'), case('missing','resultados','fonte_indisponivel')]
    plan = m.plan_simulation(project,cases=cases,seed=42)
    first, second = m.run_simulation(plan), m.run_simulation(plan)
    assert first['status'] == second['status'] == 'completed'
    assert first['cases'] == second['cases']
    assert first['trajectory_sha256'] == digest(first['cases']) == second['trajectory_sha256']
    assert {c['stage'] for c in first['cases']} == set(STAGES)
    indexed = {c['case_id']:c for c in first['cases']}
    assert indexed['defesa']['interaction_parameters'] != indexed['divergent']['interaction_parameters']
    assert indexed['missing']['scenario_assumptions']
    for row in first['cases']:
        assert len(row['participants']) == row['agents']
        assert row['questions']
        for q in row['questions']:
            assert q['stage'] == row['stage']
            assert q['question'] and q['required_evidence']
            assert q['target_claim_ids'] == ['c1']
            assert q['origin'] in {'local_rule','question_template','hypothetical'}
            assert 'poder estatístico' not in (q['question']+q['required_evidence']).lower()
    assert any(q['origin']=='hypothetical' and 's1' in q.get('source_refs',[]) for q in indexed['missing']['questions'])
    assert indexed['metodologia']['questions'][0]['question'] != indexed['analise']['questions'][0]['question']
    text = m.render_simulation_report(first).lower()
    assert 'simulação' in text and 'revisão humana' in text and 'não constitui validação científica' in text


def test_preserve_negative_evidence_without_approval(project,monkeypatch):
    m = module()
    from academic.adversarial_research import board
    original_review, calls = board.review_research, []
    def review(*args,**kw):
        calls.append(1)
        return original_review(*args,**kw)
    monkeypatch.setattr(board,'review_research',review)
    monkeypatch.setattr(m,'review_research',review,raising=False)
    original = copy.deepcopy(project)
    plan = m.plan_simulation(project,cases=[case('base'),case('missing',scenario='fonte_indisponivel')])
    before = copy.deepcopy(plan)
    result = m.run_simulation(plan)
    assert len(calls)==1 and project==original and plan==before
    assert result['base_review']['claims'][0]['evidence_status']=='contradicted'
    objections = result['base_review']['objections']
    assert any(o['code']=='negative_evidence' for o in objections)
    assert {o['objection_id'] for o in objections} <= set(result['unresolved_objection_ids'])
    assert 'legacy_board' not in result['base_review']
    safeguards(result)


def test_stale_or_tampered_plan_rejected_before_execution(project,monkeypatch):
    m = module()
    from mirofish.social.engine import SocialSimulationEngine
    monkeypatch.setattr(SocialSimulationEngine,'run',forbidden)
    plan=m.plan_simulation(project,cases=[case()])
    changed=copy.deepcopy(plan); changed['cases'][0]['scenario']='banca_divergente'
    with pytest.raises(ValueError): m.run_simulation(changed)
    changed=copy.deepcopy(plan); changed['cases'][0]['agents']=13
    changed['plan_sha256']=digest({k:v for k,v in changed.items() if k!='plan_sha256'})
    with pytest.raises(ValueError): m.run_simulation(changed)
    for path in (project['artifact_path'],project['sources'][0]['path']):
        p=Path(path); original=p.read_bytes()
        try:
            p.write_bytes(original+b'\nchanged')
            with pytest.raises(ValueError): m.run_simulation(plan)
        finally: p.write_bytes(original)


def test_strict_limits_and_global_reservations(project):
    m=module()
    for limits in ({'max_steps':True},{'max_rounds':0},{'max_actions':3457},
                   {'timeout_seconds':float('nan')},{'timeout_seconds':True},{'unknown':1}):
        with pytest.raises(ValueError): m.plan_simulation(project,limits=limits)
    with pytest.raises(ValueError): m.plan_simulation(project,seed=True)
    with pytest.raises(ValueError): m.plan_simulation(project,cases=[case(),case()])
    with pytest.raises(ValueError): m.plan_simulation(project,cases=[{**case(),'agents':13}])
    plan=m.plan_simulation(project,cases=[case('first'),case('second')],limits={'max_actions':8})
    result=m.run_simulation(plan)
    assert result['status']=='partial' and result['stop_reason']=='budget_exhausted'
    assert result['usage']['cases_executed']==1 and result['usage']['actions_reserved']==8
    assert result['usage']['actions_executed']<=8 and result['execution_complete'] is False
    assert result['unresolved_gaps']


def test_cooperative_cancel_and_timeout(project,monkeypatch):
    m=module()
    plan=m.plan_simulation(project,cases=[case('first'),case('second')])
    early=m.run_simulation(plan,cancelled=True)
    assert early['status']=='cancelled' and all(v==0 for v in early['usage'].values())
    with pytest.raises(ValueError): m.run_simulation(plan,cancelled=1)
    with pytest.raises(ValueError): m.run_simulation(plan,should_stop=True)
    from mirofish.social.engine import SocialSimulationEngine
    original_run=SocialSimulationEngine.run
    calls=[]
    def run(*args,**kw):
        calls.append(1); return original_run(*args,**kw)
    monkeypatch.setattr(SocialSimulationEngine,'run',run)
    result=m.run_simulation(plan,should_stop=lambda:bool(calls))
    assert result['status']=='cancelled' and result['usage']['cases_executed']==1
    import time
    clock=[100.0]
    monkeypatch.setattr(time,'monotonic',lambda:clock[0])
    def slow(*args,**kw):
        result=original_run(*args,**kw); clock[0]+=2; return result
    monkeypatch.setattr(SocialSimulationEngine,'run',slow)
    result=m.run_simulation(m.plan_simulation(project,cases=[case('first'),case('second')],limits={'timeout_seconds':1}))
    assert result['status']=='partial' and result['stop_reason']=='timeout'
    assert result['usage']['cases_executed']==1


def test_local_only_without_scores_or_answers(project,monkeypatch):
    m=module()
    import socket,subprocess,urllib.request
    monkeypatch.setattr(socket,'create_connection',forbidden)
    monkeypatch.setattr(urllib.request,'urlopen',forbidden)
    monkeypatch.setattr(subprocess,'Popen',forbidden)
    from mirofish.social import banca
    monkeypatch.setattr(banca,'summarize_banca',forbidden)
    monkeypatch.setattr(banca,'banca_verdict',forbidden)
    result=m.run_simulation(m.plan_simulation(project,cases=[case()]))
    def check(value):
        if isinstance(value,dict):
            assert not set(value)&{'score','weighted_score','overall_score','verdict','answer','answers'}
            for child in value.values(): check(child)
        elif isinstance(value,list):
            for child in value: check(child)
    check(result)
    safeguards(result)
    assert result['simulation_executed'] is True


def test_service_actions_persist_and_verify(project,tmp_path,monkeypatch):
    m=module()
    from academic.adversarial_research.service import AdversarialResearchService
    class Primary:
        def __init__(self): self.observations=[]
        def _record_knowledge_outcome(self,topic,context,observation):
            self.observations.append(observation); return {'persisted':True}
    primary=Primary(); service=AdversarialResearchService(primary,state_dir=tmp_path/'state')
    plan=service.action({'operation':'simulation_plan','project':project,'cases':[case()]})
    assert not service.state.exists() and not primary.observations
    result=service.action({'operation':'simulation_run','plan':plan})
    assert len(primary.observations)==1 and primary.observations[0]['confidence_promoted'] is False
    restored=service.action({'operation':'simulation_report','simulation_id':result['simulation_id']})
    assert restored==result
    assert restored['report_sha256']==digest({k:v for k,v in restored.items() if k!='report_sha256'})
    for config in ({'operation':'simulation_report','simulation_id':'../x'},
                   {'operation':'simulation_plan','project':project,'unknown':1}):
        with pytest.raises(ValueError): service.action(config)
    path=service.state/'simulations'/(result['simulation_id']+'.json')
    corrupted=json.loads(path.read_text()); corrupted['status']='invented'
    path.write_text(json.dumps(corrupted))
    with pytest.raises(ValueError): service.action({'operation':'simulation_report','simulation_id':result['simulation_id']})
