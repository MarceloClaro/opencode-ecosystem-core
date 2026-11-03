"""Contraprovas R929: arquivos temporários e nenhuma inferência externa."""
from pathlib import Path
import hashlib,json,subprocess,sys
from types import SimpleNamespace

import pytest

from evolution.cycles import EvolutionRegistry


def history(tmp_path,content=None):
    path=tmp_path/'cycles.json'
    path.write_text(json.dumps(content if content is not None else {'cycles':[]}))
    return path


def test_record_preserves_unknown_fields_and_unmodeled_legacy_entries(tmp_path):
    old={'round_id':'R1','objective':'original','extension':{'owner':'human'}}
    legacy={'id':'R0','titulo':'arquivo histórico'}
    original={'schema_extension':{'version':7},'cycles':[old,legacy,'unmodeled']}
    path=history(tmp_path,original);registry=EvolutionRegistry(str(path))
    registry.record('new',['change'],round_id='R2')
    actual=json.loads(path.read_text())
    assert actual['schema_extension']==original['schema_extension']
    assert actual['cycles'][:3]==original['cycles']
    assert actual['cycles'][3]['round_id']=='R2'


@pytest.mark.parametrize('raw',['{','[]','null','{"cycles":null}','{"cycles":{}}'])
def test_invalid_history_blocks_record_without_replacing_bytes(tmp_path,raw):
    path=tmp_path/'cycles.json';path.write_text(raw)
    registry=EvolutionRegistry(str(path))
    with pytest.raises((ValueError,RuntimeError)):
        registry.record('must not erase history',[],round_id='R2')
    assert path.read_text()==raw
    assert registry.cycles==[]


def test_stale_writer_does_not_overwrite_new_cycle_or_keep_pending_memory(tmp_path):
    path=history(tmp_path);first=EvolutionRegistry(str(path));second=EvolutionRegistry(str(path))
    first.record('first',[],score=8,round_id='R1');committed=path.read_bytes()
    with pytest.raises((ValueError,RuntimeError),match='(?i)(mud|obsolet|concor|stale)'):
        second.record('second',[],score=9,round_id='R2')
    assert path.read_bytes()==committed
    assert second.cycles==[] and second.average_score() is None


def test_failed_atomic_publication_preserves_file_and_memory(tmp_path,monkeypatch):
    import evolution.cycles as module
    path=history(tmp_path);registry=EvolutionRegistry(str(path));before=path.read_bytes()
    def fail(*args,**kwargs):raise OSError('publication refused')
    monkeypatch.setattr(module.os,'replace',fail)
    with pytest.raises(OSError,match='publication refused'):
        registry.record('new',[],score=4,round_id='R1')
    assert path.read_bytes()==before
    assert registry.cycles==[] and registry.average_score() is None


@pytest.mark.parametrize('score',['8',True])
def test_invalid_loaded_scores_do_not_crash_or_disappear(tmp_path,score):
    path=history(tmp_path,{'cycles':[{'round_id':'R1','objective':'legacy','score':score}]})
    registry=EvolutionRegistry(str(path))
    assert registry.cycles==[]
    registry.record('new',[],round_id='R2')
    raw=json.loads(path.read_text())['cycles']
    assert raw[0]['score']==score and raw[1]['round_id']=='R2'


def test_nonfinite_history_is_refused_without_overwrite(tmp_path):
    path=history(tmp_path,{'cycles':[{'round_id':'R1','objective':'bad','score':float('inf')}]})
    original=path.read_bytes();registry=EvolutionRegistry(str(path))
    with pytest.raises((ValueError,RuntimeError)):
        registry.record('new',[],round_id='R2')
    assert path.read_bytes()==original


def test_registry_accepts_pathlike_state_path(tmp_path):
    path=tmp_path/'cycles.json'
    registry=EvolutionRegistry(path)
    registry.record('pathlike',[],round_id='R1')
    assert json.loads(path.read_text())['cycles'][0]['round_id']=='R1'


@pytest.mark.parametrize('argv',[
    ['pesquisa-full','topic','--unknown'],['pesquisa-full','topic','--per-source','bad'],
    ['podcast','input','--language'],['amplify','task','--iterations','0'],
    ['deepthink','problem','--budget','6'],['deepthink','problem','--unknown'],
])
def test_malformed_effectful_options_are_rejected_before_primary(argv,monkeypatch,capsys):
    import marceloclaro.cli as cli
    def forbidden(*args,**kwargs):pytest.fail('invalid options initialized primary')
    monkeypatch.setattr(cli,'MarceloClaroOrchestrator',forbidden)
    monkeypatch.setattr(sys,'argv',['cli',*argv])
    assert cli.main()==2
    assert capsys.readouterr().err.strip()


@pytest.mark.parametrize('argv',[
    ['amplify','task','--model','local','--type','coding','--iterations','3'],
    ['deepthink','problem','--budget','2','--domain','math'],
    ['podcast','folder','--title','Title','--language','pt-BR','--format','deep_dive'],
])
def test_valid_effectful_options_reach_the_primary_unchanged(argv,monkeypatch,capsys):
    import marceloclaro.cli as cli
    observed=[];response={'status':'prepared'}
    def capture(*args,**kwargs):observed.append((args,kwargs));return response
    monkeypatch.setattr(cli,'MarceloClaroOrchestrator',lambda **kw:SimpleNamespace(
        amplify_free_model_response=capture,deep_think=capture,podcast=capture))
    monkeypatch.setattr(sys,'argv',['cli',*argv])
    assert cli.main()==0
    expected={
        'amplify':((),{'prompt':'task','model':'local','task_type':'coding','iterations':3,'use_rag':True}),
        'deepthink':(('problem',),{'domain':'math','compute_budget':2}),
        'podcast':(('folder',),{'title':'Title','language':'pt-BR','fmt':'deep_dive'}),
    }
    assert observed==[expected[argv[0]]]
    assert json.loads(capsys.readouterr().out)==response


@pytest.mark.parametrize('argv',[
    ['does-not-exist'],['pesquisa','topic','--max-papers'],
    ['pesquisa','topic','--max-papers','abc'],['pesquisa','topic','--max-papers','0'],
    ['pesquisa','topic','--platforms',''],['pesquisa','topic','--not-a-flag'],
])
def test_invalid_cli_does_not_construct_or_call_primary(argv,monkeypatch,capsys):
    import marceloclaro.cli as cli
    def forbidden(*args,**kwargs):pytest.fail('invalid input initialized primary')
    monkeypatch.setattr(cli,'MarceloClaroOrchestrator',forbidden)
    monkeypatch.setattr(sys,'argv',['cli',*argv])
    assert cli.main()==2
    assert capsys.readouterr().err.strip()


@pytest.mark.parametrize('valid',[True,False])
def test_lean_cli_exit_status_reflects_the_verification_result(valid,monkeypatch,capsys):
    import marceloclaro.cli as cli
    report={'is_valid':valid,'status':'machine_checked' if valid else 'incomplete_sorry'}
    monkeypatch.setattr(cli,'MarceloClaroOrchestrator',lambda **kw:SimpleNamespace(lean4_verify_code=lambda *a,**k:report))
    monkeypatch.setattr(sys,'argv',['cli','lean4','theorem t : True := by trivial'])
    assert cli.main()==(0 if valid else 1)
    assert json.loads(capsys.readouterr().out)==report


@pytest.mark.parametrize('action',['ativar','registrar'])
def test_legacy_profile_refusal_is_not_reported_as_activation_success(action,capsys):
    from marceloclaro.governed_cli import run_governed_cli
    report={'status':'legacy_preserved','definition_validated':False,'registered':False,'executed':False}
    factory=lambda **kw:SimpleNamespace(agent_profile_action=lambda config:report)
    args=[action,'legacy-agent']+(['--task','Audit'] if action=='ativar' else [])
    assert run_governed_cli('agentes',args,factory)==1
    assert json.loads(capsys.readouterr().out)==report


@pytest.mark.parametrize('config',[None,[],{'operation':'query','tool':'ping','arguments':None}])
def test_invalid_code_context_is_structured_and_never_written_as_observation(tmp_path,config):
    from integrations.code_context import CodeContextProvider
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    primary=MarceloClaroOrchestrator.__new__(MarceloClaroOrchestrator)
    primary._code_context_provider=CodeContextProvider(repo_root=tmp_path,state_root=tmp_path/'state')
    def forbidden(*args,**kwargs):pytest.fail('invalid request reached metacognitive persistence')
    primary._record_knowledge_outcome=forbidden
    report=primary.code_context_action(config)
    assert report['status']=='invalid_request'
    assert not report.get('success',report.get('ok',False))


@pytest.mark.parametrize('case',['parse_errors','no_units','ambiguous'])
def test_graph_response_budget_always_terminates_even_for_error_metadata(case):
    code='''import hashlib,json,sys
from integrations.python_code_graph import analyze_python_graph,MAX_RESPONSE_BYTES
case=sys.argv[1]
def item(text):
 raw=text.encode();return {'_data':raw,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
sources={('nested/'*410)+str(i)+'.py':item('def target(): pass\\n' if case=='ambiguous' else 'def broken(') for i in range(20)}
if case=='parse_errors':sources['app.py']=item('def target(): pass\\n')
out=analyze_python_graph(sources,'get_symbol_usages',{'symbol_name':'target'},timeout_seconds=2)
encoded=json.dumps(out,ensure_ascii=True).encode()
print(json.dumps({'bytes':len(encoded),'limit':MAX_RESPONSE_BYTES,'truncated':out['truncated'],'complete':out['coverage_complete'],'status':out['status']}))
'''
    try:
        result=subprocess.run([sys.executable,'-c',code,case],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,timeout=6)
    except subprocess.TimeoutExpired:
        pytest.fail('response limiter did not terminate within the external deadline')
    assert result.returncode==0,result.stderr
    report=json.loads(result.stdout)
    assert report['bytes']<=report['limit']
    assert report['truncated'] is True and report['complete'] is False


def test_variadic_annotations_are_usages_in_declaration_scope():
    from integrations.python_code_graph import analyze_python_graph
    raw=b'def add(): return 1\ndef calculate(*args: add(), **kwargs: add()): pass\n'
    corpus={'app.py':{'_data':raw,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}}
    out=analyze_python_graph(corpus,'get_symbol_usages',{'symbol_name':'app.py::add'})
    assert [(u['caller_id'],u['start_line']) for u in out['usages']]==[('app.py::<module>',2),('app.py::<module>',2)]


def test_unimplemented_banca_rating_is_an_explicit_contract_refusal():
    from academic.adversarial_research.service import AdversarialResearchService
    service=AdversarialResearchService.__new__(AdversarialResearchService)
    service.sessions=SimpleNamespace()
    config={'operation':'banca_rate','session_id':'banca-'+'a'*32,'criterion_id':'method',
            'score':4,'answer_turn_ids':['turn'],'justification':'human review','reviewer_id':'reviewer'}
    with pytest.raises(ValueError,match='(?i)(indisponível|não implementad)'):
        service.action(config)


@pytest.mark.parametrize('method',['record','record_rejected','record_audited'])
def test_threaded_records_allocate_distinct_rounds_in_the_same_registry(tmp_path,monkeypatch,method):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    import time
    path=history(tmp_path);registry=EvolutionRegistry(path)
    monkeypatch.setenv('EVOLUTION_SPECS_PATH',str(tmp_path/'empty-specs'))
    original=registry.next_round_id
    def delayed_id():
        candidate=original();time.sleep(0.1);return candidate
    monkeypatch.setattr(registry,'next_round_id',delayed_id)
    monkeypatch.setattr(registry,'_anchor',lambda *a,**k:{'commit':'test','merkle':'test'})
    start=Barrier(2)
    def record(index):
        start.wait(timeout=5)
        kwargs={}
        if method!='record':kwargs.update(verifier_identity='reviewer',generator_identity='author')
        if method=='record_rejected':kwargs['reason']='test refusal'
        if method=='record_audited':kwargs.update(artifact_hashes={},external_verdict={'passed':True})
        return getattr(registry,method)(str(index),[],**kwargs).round_id
    with ThreadPoolExecutor(max_workers=2) as pool:
        rounds=list(pool.map(record,range(2)))
    assert set(rounds)=={'R47','R48'}
    assert {row['round_id'] for row in json.loads(path.read_text())['cycles']}==set(rounds)


def test_preserved_unmodeled_round_ids_are_reserved(tmp_path,monkeypatch):
    path=history(tmp_path,{'cycles':[{'round_id':'R47','objective':'old','score':'legacy'}]})
    monkeypatch.setenv('EVOLUTION_SPECS_PATH',str(tmp_path/'empty-specs'))
    registry=EvolutionRegistry(path)
    assert registry.record('new',[]).round_id=='R48'
    assert [row['round_id'] for row in json.loads(path.read_text())['cycles']]==['R47','R48']


def test_historical_numeric_prefix_with_suffix_remains_reserved(tmp_path,monkeypatch):
    path=history(tmp_path,{'cycles':[{'round_id':'R999-final','objective':'old'}]})
    monkeypatch.setenv('EVOLUTION_SPECS_PATH',str(tmp_path/'empty-specs'))
    registry=EvolutionRegistry(path)
    assert registry.record('new',[]).round_id=='R1000'


def test_out_of_float_range_integer_does_not_crash_or_erase_legacy_history(tmp_path):
    row={'round_id':'R47','objective':'old','score':10**400}
    path=history(tmp_path,{'cycles':[row]});registry=EvolutionRegistry(path)
    assert registry.cycles==[]
    registry.record('new',[],round_id='R48')
    assert json.loads(path.read_text())['cycles'][0]==row


def test_ambiguous_graph_reports_total_and_candidate_sampling():
    from integrations.python_code_graph import analyze_python_graph
    raw=b'def same(): pass\n'
    item={'_data':raw,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    out=analyze_python_graph({f'm{i}.py':dict(item) for i in range(21)},'get_symbol_usages',{'symbol_name':'same'})
    assert out['candidate_count']==21 and len(out['candidates'])==20
    assert out['candidate_sample_count']==20
    assert out['truncated'] is True and out['coverage_complete'] is False
    assert 'candidate_sample_limit' in out['truncation_reasons']


def test_irreducible_graph_refusal_reaches_provider_without_key_error(tmp_path,monkeypatch):
    from integrations.code_context import CodeContextProvider
    raw=('class '+'C'*20000+':\n def f(): pass\n').encode()
    sources={'app.py':{'_data':raw,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}}
    provider=CodeContextProvider(repo_root=tmp_path,state_root=tmp_path/'state')
    monkeypatch.setattr(provider,'_source_files',lambda:(sources,{},len(raw)))
    monkeypatch.setattr(provider,'_manifest_current',lambda *a:True)
    monkeypatch.setattr(provider,'_git',lambda *a:b'test-head')
    out=provider.run({'operation':'python_graph','tool':'get_symbol_usages','arguments':{'symbol_name':'f'}})
    assert out['status']=='response_too_large'
    assert out['success'] is False and out['upstream_not_used'] is True
    graph=out['response']['structuredContent']
    assert graph['truncated'] is True and graph['coverage_complete'] is False
    assert isinstance(out['limitations'],list) and out['limitations']


@pytest.mark.parametrize('ok',[True,False])
def test_podcast_cli_exit_code_reflects_explicit_service_failure(ok,monkeypatch,capsys):
    import marceloclaro.cli as cli
    report={'ok':ok,**({} if ok else {'error':'pasta não encontrada'})}
    monkeypatch.setattr(cli,'MarceloClaroOrchestrator',lambda **kw:SimpleNamespace(podcast=lambda *a,**k:report))
    monkeypatch.setattr(sys,'argv',['cli','podcast','folder'])
    assert cli.main()==(0 if ok else 1)
    assert json.loads(capsys.readouterr().out)==report


@pytest.mark.parametrize('status',['syntax_verified','incomplete_sorry','unknown',None])
def test_lean_cli_rejects_non_machine_checked_status_even_if_valid_is_true(status,monkeypatch,capsys):
    import marceloclaro.cli as cli
    report={'is_valid':True,'status':status}
    monkeypatch.setattr(cli,'MarceloClaroOrchestrator',lambda **kw:SimpleNamespace(lean4_verify_code=lambda *a,**k:report))
    monkeypatch.setattr(sys,'argv',['cli','lean4','theorem t : True := by trivial'])
    assert cli.main()==1
    assert json.loads(capsys.readouterr().out)==report


def test_doctor_compares_the_same_configured_history_on_both_sides(tmp_path,monkeypatch):
    from marceloclaro.doctor import _check_evolution_registry
    path=history(tmp_path,{'cycles':[{'round_id':'R1','objective':'isolated'}]})
    monkeypatch.setenv('EVOLUTION_STATE_PATH',str(path))
    check=_check_evolution_registry()
    assert check.status=='pass',check.detail
    assert '1/1' in check.detail


def test_doctor_distinguishes_preserved_unmodeled_rows_from_lost_data(tmp_path,monkeypatch):
    from marceloclaro.doctor import _check_evolution_registry
    path=history(tmp_path,{'cycles':[{'round_id':'R1','objective':'legacy','score':'not numeric'}]})
    monkeypatch.setenv('EVOLUTION_STATE_PATH',str(path))
    before=path.read_bytes();check=_check_evolution_registry()
    assert check.status=='warn',check.detail
    assert 'preservada' in check.detail and 'não modelada' in check.detail
    assert path.read_bytes()==before


def test_structural_cli_discovery_does_not_construct_an_executor(tmp_path,monkeypatch):
    from integrations.harness_runtime import HarnessRuntime
    from marceloclaro import doctor
    monkeypatch.setattr(HarnessRuntime,'__init__',lambda *a,**k:pytest.fail('discovery constructed runtime'))
    monkeypatch.setattr(doctor.shutil,'which',lambda name:'/isolated/bin/'+name)
    monkeypatch.delenv('R929_CLI_BIN',raising=False)
    assert doctor._resolve_external_cli('r929_cli')=='/isolated/bin/r929_cli'


def test_cli_discovery_observes_installation_removal_and_override_changes(tmp_path,monkeypatch):
    import os
    from marceloclaro import doctor
    one,two=tmp_path/'one',tmp_path/'two'
    one.mkdir();two.mkdir()
    first,second=one/'r929_cli',two/'r929_cli'
    for path in (first,second):path.write_text('#!/bin/sh\nexit 0\n');path.chmod(0o755)
    monkeypatch.setenv('PATH',os.pathsep.join([str(one),str(two)]))
    monkeypatch.delenv('R929_CLI_BIN',raising=False)
    assert doctor._resolve_external_cli('r929_cli')==str(first)
    first.unlink()
    assert doctor._resolve_external_cli('r929_cli')==str(second)
    monkeypatch.setenv('R929_CLI_BIN',str(first))
    assert doctor._resolve_external_cli('r929_cli') is None
    monkeypatch.setenv('R929_CLI_BIN',str(second))
    assert doctor._resolve_external_cli('r929_cli')==str(second)


def test_catalog_baseline_parse_is_reused_only_for_identical_fresh_bytes(tmp_path,monkeypatch):
    from agents import lifecycle
    root=tmp_path/'repo';path=root/'agents/catalog/legacy.md';path.parent.mkdir(parents=True)
    raw=str(tmp_path).encode();path.write_bytes(raw)
    baseline=root/'agents/lifecycle_baseline.json'
    baseline.write_text(json.dumps({'files':{'agents/catalog/legacy.md':hashlib.sha256(raw).hexdigest()}}))
    original=lifecycle.json.loads;calls=[]
    def counted(*a,**k):calls.append(1);return original(*a,**k)
    monkeypatch.setattr(lifecycle.json,'loads',counted)
    for _ in range(2):
        assert lifecycle.enforce_catalog_contract(path,raw,repo_root=root)['legacy_preserved'] is True
    assert len(calls)==1
    # Uma alteração no manifesto deve ser observada sem prazo de expiração.
    baseline.write_text('{"files":{}}')
    with pytest.raises(ValueError):lifecycle.enforce_catalog_contract(path,raw,repo_root=root)


def test_core_check_preserves_doctor_warning_as_degraded(monkeypatch):
    from marceloclaro import core_check
    monkeypatch.setattr(core_check,'_check_doctor',lambda:({'checks_total':22,'checks_warned':1},21,0))
    for name in ('_check_specs_loading','_check_evolution_registry','_check_default_sources'):
        monkeypatch.setattr(core_check,name,lambda:(True,'fixture'))
    monkeypatch.setattr(core_check,'_scan_docs',lambda:([],True))
    monkeypatch.setattr(core_check,'_check_hermetic_modules',lambda:[])
    out=core_check.run_core_check(verbose=False)
    assert out['overall']=='degraded' and out['checks_warned']==1
    check=next(c for c in out['checks'] if c['id']=='doctor')
    assert check['status']=='warn' and '21/22' in check['detail']


@pytest.mark.parametrize('cycles',[{'bad':'shape'},None,[]])
def test_core_check_refuses_invalid_or_empty_configured_ledger(tmp_path,monkeypatch,cycles):
    from marceloclaro.core_check import _check_evolution_registry
    path=history(tmp_path,{'cycles':cycles})
    monkeypatch.setenv('EVOLUTION_STATE_PATH',str(path))
    before=path.read_bytes();ok,_=_check_evolution_registry()
    assert ok is False
    assert path.read_bytes()==before
