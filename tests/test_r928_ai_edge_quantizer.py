"""R928: integração fechada; testes rápidos não importam TensorFlow no Core."""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

REPO='MarceloClaro/ai-edge-quantizer'
COMMIT='87cda53576a55a71114a4945b3ff18e27c2fa42b'


def module():
    name='integrations.ai_edge_quantizer_core'
    assert importlib.util.find_spec(name) is not None, 'Integração AI Edge Quantizer ausente'
    return importlib.import_module(name)


def sha(raw): return hashlib.sha256(raw).hexdigest()
def blob(raw): return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def canonical(data): return json.dumps(data,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode()
def deny(*_a,**_kw): raise AssertionError('Execução indevida neste teste')


def sources():
    return {'LICENSE':b'Apache License\nVersion 2.0, January 2004\n',
        'setup.py':b'raise RuntimeError("ACQUIRE_MUST_NOT_EXECUTE")\n',
        'requirements.txt':b'fixture==1\n','ai_edge_quantizer/__init__.py':b'',
        'ai_edge_quantizer/quantizer.py':b'# fixture quantizer\n',
        'ai_edge_quantizer/recipe.py':b'# fixture recipe\n'}


@pytest.fixture
def root(tmp_path):
    root=tmp_path/'core'; root.mkdir()
    (root/'integrations/ai-edge-quantizer-locks').mkdir(parents=True)
    (root/'integrations/ai-edge-quantizer-locks/py312.txt').write_text('fixture==1 --hash=sha256:'+'a'*64+'\n')
    (root/'integrations/ai_edge_quantizer_worker.py').write_text('# worker fixture\n')
    return root


def seed_source(root):
    source=root/'.ai-edge-quantizer/source'; files={}
    for relative,raw in sources().items():
        path=source/relative; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
        files[relative]={'sha256':sha(raw),'git_blob_sha1':blob(raw),'bytes':len(raw)}
    manifest={'schema_version':1,'repo':REPO,'commit':COMMIT,'files':files}
    (root/'.ai-edge-quantizer/source-manifest.json').write_text(json.dumps(manifest))
    return source


def network_fixture(monkeypatch,m,unsafe=None):
    entries=[{'path':name,'mode':'100644','type':'blob','sha':blob(raw),'size':len(raw)} for name,raw in sources().items()]
    entries.append({'path':'ai_edge_quantizer/tests/models/external.tflite','mode':'100644','type':'blob','sha':'f'*40,'size':99})
    if unsafe is not None: entries.append(unsafe)
    calls=[]
    def download(url,*_a,**_kw):
        calls.append(url)
        if 'api.github.com' in url: return json.dumps({'sha':COMMIT,'truncated':False,'tree':entries}).encode()
        for name,raw in sources().items():
            if url.endswith('/'+name): return raw
        assert False, 'Foi solicitado arquivo externo/modelo não autorizado'
    monkeypatch.setattr(m,'_download',download)
    return calls


def test_status_and_source_plan_are_inert_and_pinned(root,monkeypatch):
    m=module(); monkeypatch.setattr(subprocess,'Popen',deny)
    core=m.EdgeQuantizerCore(root); status=core.status(); plan=core.source_plan()
    assert status['source_ready'] is status['environment_ready'] is False
    assert plan['repo']==REPO and plan['commit']==COMMIT and plan['execution_started'] is False
    assert plan['plan_sha256']==sha(canonical({k:v for k,v in plan.items() if k!='plan_sha256'}))
    assert not (root/'.ai-edge-quantizer').exists()


def test_source_acquisition_checks_git_blobs_and_never_downloads_models(root,monkeypatch):
    m=module(); calls=network_fixture(monkeypatch,m); monkeypatch.setattr(subprocess,'Popen',deny)
    core=m.EdgeQuantizerCore(root); plan=core.source_plan()
    with pytest.raises(ValueError): core.acquire_source(plan)
    result=core.acquire_source(plan,confirm=True)
    assert result['status']=='source_verified' and result['external_checkpoint_downloaded'] is False
    assert not any('.tflite' in call for call in calls)
    manifest=json.loads((root/'.ai-edge-quantizer/source-manifest.json').read_text())
    assert manifest['files']['ai_edge_quantizer/quantizer.py']['git_blob_sha1']==blob(sources()['ai_edge_quantizer/quantizer.py'])


@pytest.mark.parametrize('entry',[
    {'path':'ai_edge_quantizer/../../escape.py','mode':'100644','type':'blob','sha':'0'*40,'size':1},
    {'path':'ai_edge_quantizer/link.py','mode':'120000','type':'blob','sha':'0'*40,'size':1},
    {'path':'ai_edge_quantizer/large.py','mode':'100644','type':'blob','sha':'0'*40,'size':2000000},
])
def test_source_acquisition_rejects_unsafe_entries_without_publication(root,monkeypatch,entry):
    m=module(); network_fixture(monkeypatch,m,entry); core=m.EdgeQuantizerCore(root)
    with pytest.raises(ValueError): core.acquire_source(core.source_plan(),confirm=True)
    assert not (root/'.ai-edge-quantizer/source').exists()


def test_environment_plan_uses_dedicated_lock_and_confirmation(root,monkeypatch):
    m=module(); seed_source(root); monkeypatch.setattr(subprocess,'Popen',deny)
    core=m.EdgeQuantizerCore(root); plan=core.environment_plan()
    assert plan['environment']==str(root/'.ai-edge-quantizer/venv')
    assert plan['lock_sha256'] and plan['worker_sha256'] and plan['commit']==COMMIT
    assert '.its-fine' not in plan['environment']
    with pytest.raises(ValueError): core.prepare(plan)


def test_existing_foreign_environment_is_preserved(root,monkeypatch):
    m=module(); seed_source(root); core=m.EdgeQuantizerCore(root)
    env=root/'.ai-edge-quantizer/venv'; env.mkdir(); original=env/'user.txt'; original.write_text('preserve')
    monkeypatch.setattr(subprocess,'Popen',deny)
    with pytest.raises(ValueError): core.prepare(core.environment_plan(),confirm=True)
    assert original.read_text()=='preserve'


def test_prepare_does_not_inflate_subsecond_budget(root,monkeypatch):
    m=module(); seed_source(root); core=m.EdgeQuantizerCore(root); observed=[]
    def run(*_a,**kw):
        observed.append(kw['timeout_seconds'])
        return {'status':'timeout','returncode':-9,'stdout':b'','stderr':b'',
                'process_group_closed':True,'process_started':True}
    monkeypatch.setattr(m,'run_bounded',run)
    result=core.prepare(core.environment_plan(),confirm=True,timeout_seconds=0.1)
    assert result['status']=='preparation_failed'
    assert observed and 0<observed[0]<=0.1, 'Prazo solicitado foi ampliado para um segundo'


def fake_ready(core,monkeypatch):
    monkeypatch.setattr(core,'_environment_receipt',lambda:{'receipt_sha256':'a'*64,'python':str(core.root/'.ai-edge-quantizer/venv/bin/python')})


def test_demo_plan_is_sealed_fixed_and_has_no_external_model_input(root,monkeypatch):
    m=module(); seed_source(root); core=m.EdgeQuantizerCore(root); fake_ready(core,monkeypatch)
    monkeypatch.setattr(subprocess,'Popen',deny)
    plan=core.demo_plan('toy')
    assert plan['recipe']=='dynamic_wi8_afp32' and plan['seed']==42 and plan['samples']==16
    assert plan['training_executed'] is plan['external_checkpoint_downloaded'] is False
    assert plan['plan_sha256']==sha(canonical({k:v for k,v in plan.items() if k!='plan_sha256'}))
    for config in ({'operation':'demo_plan','model_path':'x.gguf'},
                   {'operation':'demo_plan','recipe':'arbitrary'},{'operation':'status','url':'https://evil.invalid'}):
        with pytest.raises(ValueError): m.validate_config(config)


def test_demo_requires_confirmation_and_rejects_stale_plan(root,monkeypatch):
    m=module(); source=seed_source(root); core=m.EdgeQuantizerCore(root); fake_ready(core,monkeypatch)
    plan=core.demo_plan('toy'); monkeypatch.setattr(subprocess,'Popen',deny)
    with pytest.raises(ValueError): core.demo(plan)
    altered=copy.deepcopy(plan); altered['seed']=123
    with pytest.raises(ValueError): core.demo(altered,confirm=True)
    (source/'ai_edge_quantizer/quantizer.py').write_text('# changed')
    with pytest.raises(ValueError): core.demo(plan,confirm=True)


def test_worker_namespace_has_no_network_or_workspace_mount(root,tmp_path):
    m=module(); core=m.EdgeQuantizerCore(root)
    runtime=tmp_path/'python-prefix'; runtime.mkdir(); env=root/'.ai-edge-quantizer/venv'; env.mkdir(parents=True)
    work=tmp_path/'job'; work.mkdir()
    argv=core._sandbox_argv(runtime,env,work,'probe')
    assert '--unshare-all' in argv and '--clearenv' in argv and '--die-with-parent' in argv
    assert str(root) not in argv
    assert '--ro-bind' in argv and '--bind' in argv and '/work' in argv


def test_worker_namespace_binds_only_the_declared_python_alias(root,tmp_path):
    m=module(); core=m.EdgeQuantizerCore(root)
    runtime=tmp_path/'python/cpython-3.12.14-linux-x86_64-gnu'; runtime.mkdir(parents=True)
    alias=runtime.parent/'cpython-3.12-linux-x86_64-gnu'
    env=root/'.ai-edge-quantizer/venv'; env.mkdir(parents=True)
    (env/'pyvenv.cfg').write_text('home = '+str(alias/'bin')+'\nversion_info = 3.12\n')
    work=tmp_path/'work'; work.mkdir()
    argv=core._sandbox_argv(runtime,env,work,'probe')
    assert any(argv[i:i+3]==['--ro-bind',str(runtime),str(alias)] for i in range(len(argv)-2)), 'Alias de Python declarado pela venv não foi montado'
    assert str(runtime.parent) not in argv and str(root) not in argv


def test_environment_sources_remain_attested(tmp_path):
    from sdd.tdd_history import TDDHistory
    root=tmp_path/'core'; env=root/'.ai-edge-quantizer/venv'; site=env/'lib/python3.12/site-packages'
    site.mkdir(parents=True); code=site/'fixture.py'; code.write_text('value=1\n')
    (env/'core-environment.json').write_text(json.dumps({'kind':'core_edge_quantizer_environment_v1','root':str(root),'group':'edge-quantizer'}))
    (env/'pyvenv.cfg').write_text('version_info = 3.12.14\n')
    h=TDDHistory(root=root,state_dir=tmp_path/'history'); before=h._sources(); code.write_text('value=2\n'); after=h._sources()
    assert before!=after, 'Novo ambiente foi ignorado no histórico de fontes'
    assert site.relative_to(root).as_posix() in after.get('dependency_trees',{})


def valid_metrics():
    return {'conversion_max_abs':0.0,'quantized_mse':0.00001,'quantized_max_abs':0.01,
            'int8_tensor_count':1,'float_bytes':1000,'quantized_bytes':800,'samples':16}


@pytest.mark.parametrize('key,value', [('quantized_mse',float('nan')),('quantized_max_abs',float('inf')),
    ('int8_tensor_count',0),('conversion_max_abs',1.0),('quantized_mse',0.1),('float_bytes',True),('samples',0)])
def test_metrics_reject_nonfinite_values_and_false_success(key,value):
    m=module(); data=valid_metrics(); assert m.validate_metrics(data) is True
    data[key]=value
    with pytest.raises(ValueError): m.validate_metrics(data)


def test_failed_worker_never_publishes_success(root,monkeypatch):
    m=module(); seed_source(root); core=m.EdgeQuantizerCore(root); fake_ready(core,monkeypatch)
    monkeypatch.setattr(core,'_runtime_prefix',lambda _python:root.parent/'python-runtime')
    monkeypatch.setattr(m,'run_bounded',lambda *_a,**_kw:{'status':'timeout','returncode':-9,'stdout':b'','stderr':b'PRIVATE',
        'process_group_closed':True,'process_started':True})
    result=core.demo(core.demo_plan('failed'),confirm=True)
    assert result['status']=='worker_failed' and result['externally_validated'] is False
    assert not (root/'.ai-edge-quantizer/runs/failed/manifest.json').exists()
    assert 'PRIVATE' not in str(result)


def test_report_rechecks_artifact_hashes_and_paths(root):
    m=module(); core=m.EdgeQuantizerCore(root)
    run=root/'.ai-edge-quantizer/runs/toy'; run.mkdir(parents=True)
    data={'status':'synthetic_smoke_passed','run_id':'toy','artifacts':{'../escape':{'sha256':'a'*64,'bytes':1}}}
    data['report_sha256']=sha(canonical(data)); (run/'manifest.json').write_text(json.dumps(data))
    with pytest.raises(ValueError): core.report('toy')
    with pytest.raises(ValueError): core.report('../outside')


@pytest.mark.parametrize('tamper',['external_claim','metrics','artifact'])
def test_report_refuses_overclaims_and_numeric_drift(root,tamper):
    m=module(); core=m.EdgeQuantizerCore(root); run=root/'.ai-edge-quantizer/runs/toy'; run.mkdir(parents=True)
    (run/'float.tflite').write_bytes(b'\0\0\0\0TFL3'+b'\0'*992)
    (run/'quantized.tflite').write_bytes(b'\0\0\0\0TFL3'+b'\0'*792)
    (run/'recipe.json').write_text('[]')
    (run/'evaluation.json').write_text(json.dumps({key:[[0.0]*64 for _ in range(16)] for key in ('float','quantized','reference')}))
    metrics={**valid_metrics(),'conversion_max_abs':0.0,'quantized_mse':0.0,'quantized_max_abs':0.0}
    (run/'metrics.json').write_text(json.dumps(metrics))
    artifacts=core._artifacts(run); actual=core._metrics(run,artifacts)
    report={'status':'synthetic_smoke_passed','run_id':'toy','commit':COMMIT,'artifacts':artifacts,
        'metrics':actual,'synthetic_inference_executed':True,'quantization_executed':True,**m._flags()}
    report['report_sha256']=sha(canonical(report)); (run/'manifest.json').write_text(json.dumps(report))
    assert core.report('toy')['status']=='synthetic_smoke_passed'
    if tamper=='external_claim': report['externally_validated']=True
    elif tamper=='metrics': report['metrics']['quantized_mse']=0.0001
    else: (run/'quantized.tflite').write_bytes(b'\0\0\0\0TFL3tampered')
    report['report_sha256']=sha(canonical({k:v for k,v in report.items() if k!='report_sha256'}))
    (run/'manifest.json').write_text(json.dumps(report))
    try: core.report('toy')
    except ValueError: pass
    else: assert False, 'Relatório alterado foi promovido apesar do selo recalculado'


def test_primary_dispatch_is_closed_and_preserves_plan_seal(root,monkeypatch):
    m=module(); from marceloclaro.orchestrator import MarceloClaroOrchestrator
    assert callable(getattr(MarceloClaroOrchestrator,'ai_edge_quantizer_action',None)), 'Fachada primária ausente'
    real=m.EdgeQuantizerCore; monkeypatch.setattr(m,'EdgeQuantizerCore',lambda _root:real(root))
    primary=object.__new__(MarceloClaroOrchestrator); observations=[]
    primary._record_knowledge_outcome=lambda *args:observations.append(args) or {'persisted':True}
    plan=primary.ai_edge_quantizer_action({'operation':'source_plan'})
    assert plan['plan_sha256']==sha(canonical({k:v for k,v in plan.items() if k!='plan_sha256'}))
    assert observations
    with pytest.raises(ValueError): primary.ai_edge_quantizer_action({'operation':'shell','command':'x'})


def test_primary_preserves_sealed_results(root,monkeypatch):
    m=module(); from marceloclaro.orchestrator import MarceloClaroOrchestrator
    report={'status':'synthetic_smoke_passed','run_id':'toy','externally_validated':False}
    report['report_sha256']=sha(canonical(report))
    class Service:
        def demo(self,**_kw): return copy.deepcopy(report)
    monkeypatch.setattr(m,'EdgeQuantizerCore',lambda _root:Service())
    primary=object.__new__(MarceloClaroOrchestrator)
    primary._record_knowledge_outcome=lambda *_a:{'persisted':True}
    result=primary.ai_edge_quantizer_action({'operation':'demo','plan':{},'confirm':True})
    assert result['report_sha256']==sha(canonical({k:v for k,v in result.items() if k!='report_sha256'})), 'Primário alterou relatório depois do selo'
