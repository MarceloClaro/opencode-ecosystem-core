"""R923: adaptador original, sem importar runtime upstream ou usar modelos."""
import copy
import hashlib
import importlib
import importlib.util
import json
import io
import os
from pathlib import Path
import subprocess

import pytest


def module():
    name='integrations.itsfine_core'
    assert importlib.util.find_spec(name) is not None, 'Ponte ITS-FINE/Core ausente'
    return importlib.import_module(name)


def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
        allow_nan=False,separators=(',',':')).encode()).hexdigest()


@pytest.fixture
def installed(tmp_path):
    home=tmp_path/'.its-fine'; (home/'bin').mkdir(parents=True)
    cli=home/'bin/fine.py'
    cli.write_text('import json,sys\nprint(json.dumps({"next":"fine-objective","reason":"missing:objective"} if "route" in sys.argv else {"hf-peft":{"preparado":False}}))\n')
    manifest={'version':'0.0.15','engines':['opencode'],'training_engines':['hf-peft'],
        'files':{'.its-fine/bin/fine.py':hashlib.sha256(cli.read_bytes()).hexdigest()}}
    (home/'install-manifest.json').write_text(json.dumps(manifest))
    (home/'policy.json').write_text('{"allow_process":false,"allow_data_to_harness":false}')
    return tmp_path


def test_status_checks_hashes_without_running_installed_code(installed,monkeypatch):
    m=module()
    def deny(*_a,**_kw): raise AssertionError('Status executou código')
    monkeypatch.setattr(subprocess,'Popen',deny)
    result=m.ItsFineCore(installed).status()
    assert result['installed'] is True and result['integrity_ok'] is True
    assert result['version']=='0.0.15' and result['verification']=='local_file_hashes_only'
    assert result['training_executed'] is result['inference_executed'] is False
    assert result['human_approval_required'] is True


@pytest.mark.parametrize('kind',['bytes','traversal','symlink'])
def test_tampered_or_unsafe_installation_blocks_execution(installed,monkeypatch,kind):
    m=module(); service=m.ItsFineCore(installed); plan=service.plan()
    if kind=='bytes': (installed/'.its-fine/bin/fine.py').write_text('raise RuntimeError("BAD")')
    elif kind=='traversal':
        path=installed/'.its-fine/install-manifest.json'; data=json.loads(path.read_text())
        data['files']['../outside']='a'*64; path.write_text(json.dumps(data))
    else:
        path=installed/'.its-fine/bin/fine.py'; path.unlink(); path.symlink_to(installed/'.its-fine/policy.json')
    def deny(*_a,**_kw): raise AssertionError('Executou instalação adulterada')
    monkeypatch.setattr(subprocess,'Popen',deny)
    try: service.run_safe(plan)
    except ValueError: pass
    else: assert False, 'Instalação adulterada aceita'


def test_plan_is_pure_and_sealed(installed,monkeypatch):
    m=module(); service=m.ItsFineCore(installed)
    def deny(*_a,**_kw): raise AssertionError('Planejamento executou processo')
    monkeypatch.setattr(subprocess,'Popen',deny)
    policy=(installed/'.its-fine/policy.json').read_bytes()
    plan=service.plan('demo')
    assert plan==service.plan('demo')
    assert plan['plan_sha256']==sha({k:v for k,v in plan.items() if k!='plan_sha256'})
    assert plan['actions']==['verify','engines','route'] and plan['execution_started'] is False
    assert policy==(installed/'.its-fine/policy.json').read_bytes()
    for bad in ('../escape','--submit','x/y'):
        with pytest.raises(ValueError): service.plan(bad)


def test_safe_run_executes_only_fixed_read_only_commands(installed):
    m=module(); service=m.ItsFineCore(installed)
    policy=(installed/'.its-fine/policy.json').read_bytes()
    result=service.run_safe(service.plan('demo'))
    assert result['status']=='awaiting_human' and result['next_skill']=='fine-objective'
    assert result['steps_executed']==3 and result['processes_executed']==2
    assert result['training_executed'] is result['inference_executed'] is False
    assert result['policy_modified'] is result['externally_validated'] is False
    assert result['human_approval_required'] is True
    assert policy==(installed/'.its-fine/policy.json').read_bytes()


def test_forged_or_stale_plan_never_runs(installed,monkeypatch):
    m=module(); service=m.ItsFineCore(installed)
    plan=service.plan(); altered=copy.deepcopy(plan); altered['actions']=['submit']
    altered['plan_sha256']=sha({k:v for k,v in altered.items() if k!='plan_sha256'})
    def deny(*_a,**_kw): raise AssertionError('Executou plano inválido')
    monkeypatch.setattr(subprocess,'Popen',deny)
    with pytest.raises(ValueError): service.run_safe(altered)
    (installed/'.its-fine/policy.json').write_text('{"allow_process":true}')
    with pytest.raises(ValueError): service.run_safe(plan)


def test_budget_cancel_timeout_and_errors_are_explicit(installed,monkeypatch):
    m=module(); service=m.ItsFineCore(installed); plan=service.plan()
    result=service.run_safe(plan,cancelled=True)
    assert result['status']=='cancelled' and result['processes_executed']==0
    result=service.run_safe(plan,max_steps=1)
    assert result['status']=='partial' and result['processes_executed']==0
    for kw in ({'max_steps':True},{'max_steps':0},{'timeout_seconds':float('nan')},{'cancelled':1}):
        with pytest.raises(ValueError): service.run_safe(plan,**kw)
    from integrations import itsfine_lifecycle as lifecycle
    def timeout(*_a,**_kw):
        return {'status':'timeout','returncode':-9,'stdout':b'','stderr':b'','process_group_closed':True,'process_started':True}
    monkeypatch.setattr(lifecycle,'run_bounded',timeout)
    assert service.run_safe(plan)['status']=='timeout'
    monkeypatch.setattr(lifecycle,'run_bounded',lambda *_a,**_kw:{'status':'completed','returncode':1,
        'stdout':b'PRIVATE_OUTPUT','stderr':b'PRIVATE_ERROR','process_group_closed':True,'process_started':True})
    failed=service.run_safe(plan)
    assert failed['status']=='failed' and 'PRIVATE' not in str(failed)


def test_primary_dispatch_and_cli_contract(installed,monkeypatch,capsys):
    m=module()
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    assert callable(getattr(MarceloClaroOrchestrator,'itsfine_action',None)), 'Fachada primária ausente'
    primary=object.__new__(MarceloClaroOrchestrator)
    primary._record_knowledge_outcome=lambda *_a,**_kw:{'persisted':True}
    real=m.ItsFineCore
    monkeypatch.setattr(m,'ItsFineCore',lambda _root:real(installed))
    result=primary.itsfine_action({'operation':'status'})
    assert result['integrity_ok'] is True
    plan=primary.itsfine_action({'operation':'plan','run_id':'demo'})
    assert plan['plan_sha256']==sha({k:v for k,v in plan.items() if k!='plan_sha256'}), 'Primário alterou plano já selado'
    assert primary.itsfine_action({'operation':'run','plan':plan})['status']=='awaiting_human'
    with pytest.raises(ValueError): primary.itsfine_action({'operation':'submit'})
    with pytest.raises(ValueError): primary.itsfine_action({'operation':'status','command':'whoami'})
    assert m.main(['status'])==0
    assert json.loads(capsys.readouterr().out)['integrity_ok'] is True


def test_selected_extraction_preserves_old_version_metadata(tmp_path):
    helper_path=Path(__file__).with_name('test_r921_local_plugin_extraction.py')
    helper_spec=importlib.util.spec_from_file_location('r923_plugin_fixtures',helper_path)
    helper=importlib.util.module_from_spec(helper_spec); helper_spec.loader.exec_module(helper)
    from integrations.scientific_plugins import PLUGINS,ScientificPluginService
    cache=tmp_path/'cache'; helper.package(cache)
    repo=tmp_path/'repo'; storage=repo/'.opencode/scientific-plugins'
    old=storage/'packages/data/0.0.1'; old.mkdir(parents=True)
    (old/'README.md').write_text('Preservar instalação legada; não é a versão atual.')
    entry={'id':'data','name':PLUGINS['data'][0],'version':'0.0.1',
        'source_root':str(tmp_path/'historical-source'),'package_root':str(old),
        'files':{'README.md':hashlib.sha256((old/'README.md').read_bytes()).hexdigest()},
        'skills':[],'origin':'third_party_or_user'}
    (storage/'registry.json').write_text(json.dumps({'data':entry}))
    unrelated=storage/'packages/unrelated/1.0.0'; unrelated.mkdir(parents=True)
    (unrelated/'auth.json').write_text('DO_NOT_READ_OR_COPY')
    try:
        result=ScientificPluginService(repo).extract_selected(cache_root=cache,plugin_ids=['zotero'])
    except ValueError as exc:
        assert False, f'Metadado legado íntegro impediu extração independente: {exc}'
    assert result['executed'] is False
    assert json.loads((storage/'registry.json').read_text())['data']==entry


def test_drvfs_options_are_opaque_and_specific_mount_required(tmp_path,monkeypatch):
    from integrations.local_plugin_extraction import _drvfs_synthetic_modes
    info=tmp_path.stat(); device=f'{os.major(info.st_dev)}:{os.minor(info.st_dev)}'
    base=f'1 0 {device} / / rw - 9p C:\\134 rw,aname=drvfs;path=C:\\;uid=1000\n'
    original=Path.open
    for suffix,expected in (('',True),(';metadata',False),('nested',False)):
        content=base if not suffix else base.rstrip('\n')+suffix+'\n'
        if suffix=='nested': content=base+f'2 1 {device} / {tmp_path} rw - ext4 /dev/mock rw\n'
        def opened(path,*args,**kw):
            return io.BytesIO(content.encode()) if str(path)=='/proc/self/mountinfo' else original(path,*args,**kw)
        monkeypatch.setattr(Path,'open',opened)
        assert _drvfs_synthetic_modes(tmp_path) is expected


def test_selected_scope_caps_bytes_read_not_unread_script_sizes(tmp_path,monkeypatch):
    helper_path=Path(__file__).with_name('test_r921_local_plugin_extraction.py')
    helper_spec=importlib.util.spec_from_file_location('r923_scope_fixtures',helper_path)
    helper=importlib.util.module_from_spec(helper_spec); helper_spec.loader.exec_module(helper)
    from integrations import local_plugin_extraction as extraction
    cache=tmp_path/'cache'; package=helper.package(cache)
    helper.manifest(package,skills='./skills/')
    (package/'scripts').mkdir(); (package/'scripts/never.bin').write_bytes(b'x'*5000)
    monkeypatch.setattr(extraction,'MAX_FILE_BYTES',4096)
    original=extraction._read
    def guarded(path,*args,**kw):
        assert 'scripts' not in Path(path).parts, 'Lido corpo excluído'
        return original(path,*args,**kw)
    monkeypatch.setattr(extraction,'_read',guarded)
    try: report=extraction.inventory_selected_plugins(cache,['zotero'])
    except ValueError as exc: assert False, f'Bytes não lidos consumiram teto de leitura: {exc}'
    assert report['plugins'][0]['disposition']=='eligible'
    assert 'scripts/never.bin' not in report['plugins'][0]['files']
