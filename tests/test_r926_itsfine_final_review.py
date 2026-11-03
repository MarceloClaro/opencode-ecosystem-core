"""R926: observações independentes convertidas em contraprovas locais."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest


def test_managed_text_dependencies_are_not_ignored(tmp_path):
    from sdd.tdd_history import TDDHistory
    root=tmp_path/'project'; env=root/'.its-fine/venv'
    site=env/'lib/python3.12/site-packages'; site.mkdir(parents=True)
    (site/'dependency.py').write_text('value=1\n')
    (env/'pyvenv.cfg').write_text('version_info = 3.12.14\n')
    (env/'core-environment.json').write_text(json.dumps({'kind':'core_itsfine_environment_v1','root':str(root),'group':'text'}))
    h=TDDHistory(root=root,state_dir=tmp_path/'private-history'); before=h._sources()
    (site/'dependency.py').write_text('value=2\n'); after=h._sources()
    assert before!=after, 'A venv gerenciada de texto ainda foi ignorada'
    assert site.relative_to(root).as_posix() in after.get('dependency_trees',{})


def policy_setup(tmp_path,monkeypatch,before,after):
    from integrations import itsfine_lifecycle as m
    root=tmp_path/'project'; (root/'.its-fine').mkdir(parents=True)
    policy=root/'.its-fine/policy.json'
    if before is not None: policy.write_text(json.dumps(before))
    raw_hash=hashlib.sha256(policy.read_bytes()).hexdigest() if policy.exists() else None
    plan=m._seal({'policy_sha256':raw_hash,'archive_path':'fixture.tgz','argv':['not-executed']})
    monkeypatch.setattr(m,'installation_plan',lambda *_a,**_kw:plan)
    monkeypatch.setattr(m.ItsFineCore,'status',lambda _self:{'integrity_ok':True})
    def run(*_a,**_kw):
        policy.write_text(json.dumps(after))
        return {'status':'completed','returncode':0,'stdout':b'','stderr':b'','process_group_closed':True,'process_started':True}
    monkeypatch.setattr(m,'run_bounded',run)
    return m.install_pinned(root,plan,confirm=True)


@pytest.mark.parametrize('before',[None,{'allow_process':False}])
def test_policy_changes_are_never_reported_preserved(tmp_path,monkeypatch,before):
    result=policy_setup(tmp_path,monkeypatch,before,{'allow_process':True})
    assert result['status']=='installation_failed'
    assert result['policy_preserved'] is False and result['policy_modified'] is True


def test_default_policy_creation_is_explicit(tmp_path,monkeypatch):
    result=policy_setup(tmp_path,monkeypatch,None,{'schema_version':1,'allow_process':False,'allow_data_to_harness':False})
    assert result.get('policy_created') is True
    assert result['policy_preserved'] is False and result['policy_modified'] is False
    assert result['status']=='installed_verified'


def test_legacy_diagnostics_use_bounded_output(tmp_path):
    from integrations.itsfine_core import ItsFineCore,MAX_OUTPUT
    home=tmp_path/'.its-fine'; (home/'bin').mkdir(parents=True)
    source=home/'bin/fine.py'; source.write_text('import sys;sys.stdout.write("x"*2000000)')
    (home/'policy.json').write_text('{"allow_process":false}')
    (home/'install-manifest.json').write_text(json.dumps({'version':'0.0.15',
        'files':{'.its-fine/bin/fine.py':hashlib.sha256(source.read_bytes()).hexdigest()}}))
    core=ItsFineCore(tmp_path); result=core.run_safe(core.plan())
    assert result['status']=='failed'
    assert result['receipts'][-1]['output_bytes']<=MAX_OUTPUT, 'Pipe foi limitado apenas após buffering'
    assert result['receipts'][-1]['process_group_closed'] is True


def test_wait_failure_is_structured_and_closes_pipes(tmp_path,monkeypatch):
    from integrations import itsfine_lifecycle as m
    real=subprocess.Popen; instances=[]
    class WaitFailure(real):
        def __init__(self,*a,**kw): super().__init__(*a,**kw); instances.append(self)
        def wait(self,timeout=None): raise subprocess.TimeoutExpired(self.args,timeout or 5)
    monkeypatch.setattr(subprocess,'Popen',WaitFailure)
    try: result=m.run_bounded(['/usr/bin/true'],cwd=tmp_path,timeout_seconds=2,max_output_bytes=1024)
    except subprocess.TimeoutExpired: assert False, 'Erro de cleanup escapou e pulou fechamento dos pipes'
    assert result['status']=='cleanup_incomplete' and result['process_group_closed'] is False
    assert all(p.stdout.closed and p.stderr.closed for p in instances)
