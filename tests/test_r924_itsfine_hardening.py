"""R924: oráculos locais sem credenciais/datasets/modelos; instalação simulada."""
import base64
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
from types import SimpleNamespace

import pytest


def lifecycle():
    name='integrations.itsfine_lifecycle'
    assert importlib.util.find_spec(name) is not None, 'Ciclo seguro ITS-FINE ausente'
    return importlib.import_module(name)


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':')).encode()


def fixtures(name):
    path=Path(__file__).with_name(name)
    spec=importlib.util.spec_from_file_location('r924_'+path.stem,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


@pytest.fixture
def project(tmp_path):
    root=tmp_path/'project'; root.mkdir(); home=root/'.its-fine'; (home/'bin').mkdir(parents=True)
    cli=home/'bin/fine.py'; cli.write_text('print("ok")\n')
    (home/'policy.json').write_text('{"allow_process":false,"allow_data_to_harness":false}')
    (home/'install-manifest.json').write_text(json.dumps({'version':'0.0.15','engines':['opencode'],
        'files':{'.its-fine/bin/fine.py':hashlib.sha256(cli.read_bytes()).hexdigest()}}))
    return root


@pytest.fixture
def archive(tmp_path):
    path=tmp_path/'itsfine.tgz'
    meta={'name':'@sandeco/itsfine','version':'0.0.15','scripts':{'test':'node --test tests/install.test.mjs'}}
    with tarfile.open(path,'w:gz') as tar:
        body=json.dumps(meta).encode(); info=tarfile.TarInfo('package/package.json'); info.size=len(body)
        tar.addfile(info,io.BytesIO(body))
    return path


def trust_fixture(m,path,monkeypatch):
    monkeypatch.setattr(m,'DIST_SRI','sha512-'+base64.b64encode(hashlib.sha512(path.read_bytes()).digest()).decode())


def test_distribution_sri_and_missing_upstream_tests_are_explicit(archive,monkeypatch):
    m=lifecycle(); trust_fixture(m,archive,monkeypatch)
    report=m.audit_distribution(archive)
    assert report['version']=='0.0.15' and report['sri_verified'] is True
    assert report['upstream_tests_status']=='not_shipped'
    assert report['upstream_tests_executed'] is False
    archive.write_bytes(archive.read_bytes()+b'x')
    with pytest.raises(ValueError): m.audit_distribution(archive)


@pytest.mark.parametrize('kind',['traversal','link','duplicate','identity'])
def test_distribution_rejects_links_traversal_and_wrong_identity(tmp_path,monkeypatch,kind):
    m=lifecycle(); path=tmp_path/'unsafe.tgz'
    with tarfile.open(path,'w:gz') as tar:
        meta={'name':'wrong' if kind=='identity' else '@sandeco/itsfine','version':'0.0.15'}
        raw=json.dumps(meta).encode(); info=tarfile.TarInfo('package/package.json'); info.size=len(raw)
        tar.addfile(info,io.BytesIO(raw))
        if kind!='identity':
            info=tarfile.TarInfo('package/../escape' if kind=='traversal' else 'package/package.json' if kind=='duplicate' else 'package/link')
            if kind=='link': info.type=tarfile.SYMTYPE; info.linkname='/etc/passwd'
            tar.addfile(info,io.BytesIO(b''))
    trust_fixture(m,path,monkeypatch)
    with pytest.raises(ValueError): m.audit_distribution(path)


def test_install_plan_is_noninteractive_offline_and_version_pinned(project,archive,monkeypatch):
    m=lifecycle(); trust_fixture(m,archive,monkeypatch)
    monkeypatch.setattr(subprocess,'Popen',lambda *_a,**_kw:(_ for _ in ()).throw(AssertionError('Plano executou processo')))
    plan=m.installation_plan(project,archive)
    argv=plan['argv']
    assert '--offline' in argv and '--yes' in argv and '--no-deps' in argv
    assert argv[argv.index('--engines')+1]=='opencode'
    assert not any(word in ' '.join(argv) for word in ('latest','update','upgrade'))
    assert plan['execution_started'] is False
    assert plan['plan_sha256']==hashlib.sha256(canonical({k:v for k,v in plan.items() if k!='plan_sha256'})).hexdigest()


def test_install_requires_confirmation_and_unchanged_package_and_policy(project,archive,monkeypatch):
    m=lifecycle(); trust_fixture(m,archive,monkeypatch)
    plan=m.installation_plan(project,archive)
    with pytest.raises(ValueError): m.install_pinned(project,plan)
    mutated=copy.deepcopy(plan); mutated['argv'].append('--bogus')
    with pytest.raises(ValueError): m.install_pinned(project,mutated,confirm=True)
    (project/'.its-fine/policy.json').write_text('{"allow_process":true}')
    with pytest.raises(ValueError): m.install_pinned(project,plan,confirm=True)


def test_bounded_runner_limits_output_timeout_and_kills_descendants(tmp_path):
    m=lifecycle()
    noisy=m.run_bounded([sys.executable,'-c','import sys; sys.stdout.write("x"*2000000)'],
                        cwd=tmp_path,timeout_seconds=5,max_output_bytes=1024)
    assert noisy['status']=='output_limit' and len(noisy['stdout'])+len(noisy['stderr'])<=1024
    timed=m.run_bounded([sys.executable,'-c','import time; time.sleep(5)'],
                        cwd=tmp_path,timeout_seconds=0.1,max_output_bytes=1024)
    assert timed['status']=='timeout' and timed['process_group_closed'] is True
    if os.name=='posix':
        childfile=tmp_path/'childpid'
        code='import subprocess,sys; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print(p.pid,flush=True)'
        child=m.run_bounded([sys.executable,'-c',code],cwd=tmp_path,timeout_seconds=3,max_output_bytes=1024)
        assert child['process_group_closed'] is True
        pid=int(child['stdout'].strip())
        end=time.monotonic()+2
        while time.monotonic()<end:
            try: state=Path(f'/proc/{pid}/stat').read_text().split()[2]
            except FileNotFoundError: break
            if state=='Z': break
            time.sleep(0.02)
        else: assert False, 'Descendente continuou ativo após encerramento do pai'


def seed_engine_inputs(root):
    manifest_path=root/'.its-fine/install-manifest.json'
    manifest=json.loads(manifest_path.read_text())
    for engine in ('hf-peft','hf-encoder','hf-tts'):
        folder=root/'.its-fine/engines'/engine; folder.mkdir(parents=True)
        (folder/'engine.json').write_text(json.dumps({'engine':engine,'version':'0.0.15'}))
        manifest['files'][f'.its-fine/engines/{engine}/engine.json']=hashlib.sha256((folder/'engine.json').read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    locks=root/'integrations/itsfine-locks'; locks.mkdir(parents=True)
    for name in ('text-py312.txt','voice-py312.txt'):
        (locks/name).write_text('fixture==1.0 --hash=sha256:'+'a'*64+'\n')


def test_engine_plan_separates_text_and_voice_and_pins_lock(project,monkeypatch):
    m=lifecycle(); seed_engine_inputs(project)
    text=m.engine_plan(project,'hf-peft'); encoder=m.engine_plan(project,'hf-encoder'); voice=m.engine_plan(project,'hf-tts')
    assert text['environment']==encoder['environment']!=voice['environment']
    assert text['lock_sha256'] and voice['lock_sha256']
    assert text['training_executed'] is voice['training_executed'] is False
    for invalid in ('../outside','shell','latest'):
        with pytest.raises(ValueError): m.engine_plan(project,invalid)


def test_engine_prepare_is_explicit_and_never_marks_gpu_ready_from_metadata(project):
    m=lifecycle(); seed_engine_inputs(project)
    plan=m.engine_plan(project,'hf-peft')
    with pytest.raises(ValueError): m.prepare_engine(project,plan)
    (project/'.its-fine/engine-setup.json').write_text('{"engines_prontos":["hf-peft","hf-tts"],"pronto":true}')
    statuses=m.engines_status(project)
    assert all(not row['training_ready'] for row in statuses['engines'])
    assert all(not row['dependencies_ready'] for row in statuses['engines'])


def test_engine_status_rechecks_receipt_and_environment(project):
    m=lifecycle(); seed_engine_inputs(project)
    result=m.engines_status(project)
    assert result['training_executed'] is False
    assert {row['engine'] for row in result['engines']}=={'hf-peft','hf-encoder','hf-tts'}
    assert all(row['status'] in {'not_prepared','receipt_invalid','environment_missing'} for row in result['engines'])


def test_engine_status_does_not_trust_a_forged_ready_receipt(project,monkeypatch):
    m=lifecycle(); seed_engine_inputs(project); plan=m.engine_plan(project,'hf-peft')
    env=Path(plan['environment']); (env/'bin').mkdir(parents=True)
    (env/'bin/python').symlink_to(sys.executable)
    receipt={k:plan[k] for k in ('engine','environment','engine_sha256','lock_sha256','policy_sha256')}
    receipt.update(status='dependencies_verified_cpu',dependencies_ready=True,cpu_probe_passed=True,
        accelerator_available=False,training_ready=False,
        python_fingerprint=hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest())
    receipt['receipt_sha256']=hashlib.sha256(canonical(receipt)).hexdigest()
    folder=project/'.its-fine/core/engines'; folder.mkdir(parents=True)
    (folder/'hf-peft.json').write_text(json.dumps(receipt))
    monkeypatch.setattr(m,'run_bounded',lambda *_a,**_kw:{'status':'completed','returncode':0,
        'stdout':b'{"cpu_probe_passed":false}', 'stderr':b'', 'process_group_closed':True,'process_started':True})
    row=next(r for r in m.engines_status(project)['engines'] if r['engine']=='hf-peft')
    assert row['dependencies_ready'] is row['training_ready'] is False


def test_primary_exposes_verified_lifecycle_without_arbitrary_commands(project,monkeypatch):
    lifecycle()
    from integrations import itsfine_core
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    core=object.__new__(MarceloClaroOrchestrator); core._record_knowledge_outcome=lambda *_a,**_kw:{'persisted':True}
    real=itsfine_core.ItsFineCore; monkeypatch.setattr(itsfine_core,'ItsFineCore',lambda _root:real(project))
    try: result=core.itsfine_action({'operation':'verify'})
    except ValueError as exc: assert False, f'Fachada verify ausente: {exc}'
    assert result['integrity_ok'] is True
    with pytest.raises(ValueError): core.itsfine_action({'operation':'install','plan':{},'command':'curl x'})


def test_verifier_refuses_parent_symlink_race_before_body_read(tmp_path,monkeypatch):
    from integrations.itsfine_core import _read
    parent=tmp_path/'parent'; parent.mkdir(); (parent/'data').write_text('inside')
    outside=tmp_path/'outside'; outside.mkdir(); (outside/'data').write_text('outside')
    real_open=os.open; swapped=[]
    def racing(path,flags,*args,**kw):
        if not swapped and Path(path)==parent/'data':
            swapped.append(1); parent.rename(tmp_path/'saved'); parent.symlink_to(outside,target_is_directory=True)
        return real_open(path,flags,*args,**kw)
    monkeypatch.setattr(os,'open',racing)
    try: data=_read(parent/'data')
    except ValueError: return
    assert data!=b'outside', 'Verificador seguiu diretório pai trocado por symlink'


def test_duplicate_yaml_cannot_hide_restricted_license_or_invocation_policy(tmp_path):
    from integrations import local_plugin_extraction as x
    helper=fixtures('test_r921_local_plugin_extraction.py')
    cache=tmp_path/'cache'; package=helper.package(cache)
    (package/'skills/curate/SKILL.md').write_text('---\nname: curate\nlicense: Proprietary\nlicense: MIT\n---\nRESTRICTED BODY\n')
    try: report=x.inventory_selected_plugins(cache,['zotero'])
    except ValueError: report=None
    assert report is None or report['plugins'][0]['disposition']=='reference_only'
    helper.put(package/'skills/curate/SKILL.md',helper.SKILL)
    helper.put(package/'skills/curate/agents/openai.yaml','policy:\n  allow_implicit_invocation: false\n  allow_implicit_invocation: true\n')
    try: x.inventory_selected_plugins(cache,['zotero'])
    except ValueError: pass
    else: assert False, 'Política YAML duplicada foi aceita'


@pytest.mark.parametrize('code',[
    'theorem admitted : False := sorryAx False true',
    'theorem first : True := by trivial\ntheorem second : True := by trivial',
])
def test_lean_rejects_sorryax_and_multiple_theorems_before_compiler(code,monkeypatch):
    from integrations.local_lean import LocalLeanVerifier
    verifier=LocalLeanVerifier(); calls=[]
    def runtime(): calls.append(1); raise RuntimeError('unexpected compiler')
    monkeypatch.setattr(verifier,'_runtime',runtime)
    result=verifier.verify(code)
    assert result['status']=='source_rejected' and result['compiler_executed'] is False
    assert not calls


def fake_lean(monkeypatch,tmp_path,output,returncode):
    from integrations.local_lean import LocalLeanVerifier
    verifier=LocalLeanVerifier()
    monkeypatch.setattr(verifier,'_runtime',lambda:tmp_path)
    monkeypatch.setattr(verifier,'_namespace',lambda _prefix:[])
    def run(_argv,**kw):
        kw['stdout'].write(output.encode()); kw['stdout'].flush()
        return SimpleNamespace(returncode=returncode)
    monkeypatch.setattr(subprocess,'run',run)
    return verifier


def test_lean_rejects_sorry_axiom_in_compiler_output(tmp_path,monkeypatch):
    verifier=fake_lean(monkeypatch,tmp_path,"'core_ok' depends on axioms: [sorryAx]\n",0)
    result=verifier.verify('theorem core_ok : True := by trivial')
    assert result['is_valid'] is False and result['status']!='machine_checked'


def test_lean_resource_failure_is_not_semantic_rejection(tmp_path,monkeypatch):
    verifier=fake_lean(monkeypatch,tmp_path,'failed to create thread: Resource temporarily unavailable\n',1)
    result=verifier.verify('theorem core_ok : True := by trivial')
    assert result['is_valid'] is False and result['status']=='resource_exhausted'
