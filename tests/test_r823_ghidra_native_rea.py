"""R823: transporte hermético real; fixture não representa prova do provider."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time

import pytest

from integrations.rea_bridge import ReaBridge

SERVER = r'''
import json,os,sys,time,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent.parent
(root/'pid').write_text(str(os.getpid()))
mode=(root/'mode').read_text()
tools=[{'name':n,'inputSchema':{'type':'object','properties':p}} for n,p in (
 ('open_binary',{'path':{},'provider_id':{}}),('analyze_function',{'procedure':{}}),
 ('binary_session',{}),('close_binary',{}),('run_binary',{}))]
target=None;closed=False
for line in sys.stdin:
 m=json.loads(line)
 with (root/'requests.jsonl').open('a') as f:f.write(json.dumps(m)+'\n')
 if 'id' not in m:continue
 method=m.get('method')
 if method=='initialize':r={'protocolVersion':m['params']['protocolVersion'],'capabilities':{'tools':{}},'serverInfo':{'name':'rea-hermetic','version':'6.4.0'}}
 elif method=='tools/list':r={'tools':tools}
 elif method=='tools/call':
  n=m['params']['name'];a=m['params'].get('arguments',{})
  if n=='open_binary':
   closed=False;target=Path(a['path']);v={'result':{'open':True,'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}}
  elif n=='analyze_function':
   (root/'analysis-ready.tmp').write_text(str(os.getpid()))
   (root/'analysis-ready.tmp').replace(root/'analysis-ready')
   if mode=='stall':time.sleep(60)
   digest=hashlib.sha256(target.read_bytes()).hexdigest()
   v={'evidence_id':'ev_'+'a'*64,'operation':'analyze_function','provider':{'id':'ghidra','name':'Ghidra','version':'12.1.4'},'subject':{'local_path':str(target),'digest':{'sha256':digest}},'normalized_result':{'procedure':{'name':a['procedure']},'pseudocode':'int fixture_add(int a,int b) { return a+b; }'},'limitations':['Hermetic artificial fixture'], 'confidence':'observed','authority':'shipped-artifact'}
   if mode=='wrong-provider':v['provider']['id']='hopper'
   if mode=='wrong-digest':v['subject']['digest']['sha256']='b'*64
   if mode=='missing-evidence':v={'message':'no Evidence'}
   if mode=='analysis-error':v={'error':{'code':'ANALYSIS_FAILED'}}
   if mode=='mutate':target.write_bytes(b'changed')
  elif n=='binary_session':v={'result':{'open':False}} if closed else {'result':{'open':True,'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'analysis_provider_binding':{'provider':{'id':'ghidra','name':'Ghidra','version':'12.1.4'}}}}
  elif n=='close_binary':
   closed=mode not in ('close-error','lying-close')
   v={'result':None} if mode=='null-close' else {'result':{'open':False}} if mode!='close-error' else {'error':{'code':'CLOSE_FAILED'}}
  else:v={'error':{'code':'FORBIDDEN'}}
  r={'content':[{'type':'text','text':json.dumps(v)}],'structuredContent':v,'isError':False}
 else:r={}
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':r}),flush=True)
'''


@pytest.fixture
def native(tmp_path, monkeypatch):
    runtime=tmp_path/'runtime'
    (runtime/'scripts').mkdir(parents=True)
    (runtime/'dist').mkdir(); (runtime/'node_modules').mkdir()
    (runtime/'scripts/rea.mjs').write_text(SERVER)
    (runtime/'dist/main.js').write_text('// fixture')
    (runtime/'package.json').write_text(json.dumps({'name':'rea-agents','version':'6.4.0'}))
    (runtime/'mode').write_text('success')
    ghidra=tmp_path/'ghidra'; (ghidra/'support').mkdir(parents=True)
    (ghidra/'support/analyzeHeadless').write_text('#!/bin/sh\nexit 1\n')
    (ghidra/'support/analyzeHeadless').chmod(0o700)
    java=tmp_path/'jdk'; (java/'bin').mkdir(parents=True)
    for name in ('java','javac'):(java/'bin'/name).symlink_to(sys.executable)
    monkeypatch.setenv('REA_SOURCE_DIR',str(runtime)); monkeypatch.setenv('REA_NODE_BIN',sys.executable)
    monkeypatch.setenv('GHIDRA_INSTALL_DIR',str(ghidra)); monkeypatch.setenv('JAVA_HOME',str(java))
    target=tmp_path/'known binary'; target.write_bytes(b'\x7fELF'+b'inert-fixture'); target.chmod(0o600)
    return runtime,target


def call_names(runtime):
    return [v['params']['name'] for v in map(json.loads,(runtime/'requests.jsonl').read_text().splitlines()) if v.get('method')=='tools/call']


def test_native_analysis_preserves_real_transport_evidence_and_closes(native,tmp_path):
    runtime,target=native
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    result=ReaBridge(tmp_path).action({'operation':'analyze_binary','path':str(target),'procedure':'fixture_add','timeout_seconds':5})
    assert result['success'],result
    assert call_names(runtime)==['open_binary','analyze_function','binary_session','close_binary','binary_session']
    assert result['response']['analysis']['structuredContent']['normalized_result']['pseudocode'].startswith('int fixture_add')
    assert result['provenance']['target_sha256']==digest
    assert result['cleanup']['closed'] is True
    assert target.read_bytes()==b'\x7fELFinert-fixture'


@pytest.mark.parametrize('mode',['wrong-provider','wrong-digest','missing-evidence','analysis-error','close-error','mutate'])
def test_native_incompatible_results_never_confirm_success_and_always_close(native,tmp_path,mode):
    runtime,target=native; (runtime/'mode').write_text(mode)
    result=ReaBridge(tmp_path).action({'operation':'analyze_binary','path':str(target),'timeout_seconds':5})
    assert result['success'] is False and result['status']=='failed'
    assert 'close_binary' in call_names(runtime)
    assert result['error']


@pytest.mark.parametrize('key,value',[('GHIDRA_INSTALL_DIR','relative'),('GHIDRA_INSTALL_DIR',''),('JAVA_HOME','relative'),('JAVA_HOME','')])
def test_invalid_explicit_native_override_never_falls_back_or_starts(native,tmp_path,monkeypatch,key,value):
    runtime,target=native; monkeypatch.setenv(key,value)
    result=ReaBridge(tmp_path).action({'operation':'analyze_binary','path':str(target)})
    assert result['success'] is False
    assert result['error_code']=='provider_unavailable'
    assert not (runtime/'pid').exists()


@pytest.mark.parametrize('extra',[{'path':'.'},{'procedure':''},{'procedure':'x\x00y'},{'procedure':'x'*257},{'provider':'hopper'},{'tool':'run_binary'}])
def test_native_invalid_config_rejected_before_transport(native,tmp_path,extra):
    runtime,target=native
    config={'operation':'analyze_binary','path':str(target),**extra}
    with pytest.raises(ValueError):ReaBridge(tmp_path).action(config)
    assert not (runtime/'pid').exists()


def test_native_cli_reaches_primary_with_literal_procedure(native,capsys):
    from marceloclaro.rea_cli import run_rea_cli
    runtime,target=native
    class Primary:
        def __init__(self,**kwargs):assert kwargs=={'auto_load_agents':False}
        def rea_action(self,config):return ReaBridge(target.parent).action(config)
    assert run_rea_cli(['analyze_binary',str(target),'--procedure','fixture_add','--timeout','5'],Primary)==0
    assert json.loads(capsys.readouterr().out)['success'] is True
    assert call_names(runtime)[1]=='analyze_function'


def test_native_summary_exports_full_pipeline_artifact(native,tmp_path):
    from marceloclaro.rea_reports import compact_rea_report
    runtime,target=native
    report=ReaBridge(tmp_path).action({'operation':'analyze_binary','path':str(target),'timeout_seconds':5})
    compact=compact_rea_report(report,tmp_path)
    assert compact['success'] and compact['evidence']['provider']['id']=='ghidra'
    assert compact['evidence']['procedure']=={'name':'main'}
    artifact=compact['evidence_artifact']
    preserved=json.loads(Path(artifact['path']).read_text())
    assert preserved['close']['structuredContent']['result']['open'] is False
    assert len(json.dumps(compact))<12000


def test_native_cancel_waits_for_process_cleanup(native,tmp_path,request):
    from integrations.execution_control import run_cancellable
    runtime,target=native; (runtime/'mode').write_text('stall')
    async def cancel():
        waiting_started = time.monotonic()
        task=asyncio.create_task(run_cancellable(ReaBridge(tmp_path).action,{'operation':'analyze_binary','path':str(target),'timeout_seconds':20}))
        ready = runtime/'analysis-ready'
        # O prazo separado cobre inicialização/imports sob carga. Não mede limpeza.
        ready_deadline = time.monotonic() + 30
        try:
            while not ready.exists():
                if task.done():
                    pytest.fail(f'Transporte terminou antes da operação bloqueada: {task.result()}')
                assert time.monotonic() < ready_deadline, 'Operação bloqueada não iniciou em 30s'
                await asyncio.sleep(.01)
            pid = int(ready.read_text())
            assert pid == int((runtime/'pid').read_text())
            request.node.user_properties.append(('readiness_seconds', time.monotonic()-waiting_started))
            started = time.monotonic()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            return time.monotonic()-started,pid
        finally:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    cleanup_seconds,pid=asyncio.run(cancel())
    request.node.user_properties.append(('cleanup_seconds', cleanup_seconds))
    request.node.user_properties.append(('cancelled_child_pid', pid))
    assert cleanup_seconds<12, f'Limpeza após cancelamento: {cleanup_seconds:.3f}s'
    stat=Path(f'/proc/{pid}/stat')
    assert not stat.exists() or stat.read_text().split()[2]=='Z'


def test_status_exposes_only_native_configuration_without_starting(native,tmp_path):
    runtime,_=native
    result=ReaBridge(tmp_path).status()
    assert result['native_provider']['configuration_available'] is True
    assert result['native_provider']['verification']=='installation_only'
    assert result['native_provider']['provider']=='ghidra'
    assert not (runtime/'pid').exists()


def test_raw_mcp_launcher_uses_child_environment_without_mutating_parent(native,monkeypatch):
    import integrations.rea_bridge as module
    recorded={};before=dict(os.environ)
    monkeypatch.setattr(module.os,'execv',lambda *args: pytest.fail('Launcher deve transportar env explícito'))
    monkeypatch.setattr(module.os,'execve',lambda executable,args,environment: recorded.update(executable=executable,args=args,environment=environment))
    assert module.main(['mcp'])==0
    assert recorded['environment']['GHIDRA_INSTALL_DIR']==before['GHIDRA_INSTALL_DIR']
    assert recorded['environment']['JAVA_HOME']==before['JAVA_HOME']
    assert dict(os.environ)==before


@pytest.mark.parametrize('mode,success',[('null-close',True),('lying-close',False)])
def test_native_close_is_confirmed_by_followup_session_not_close_return_shape(native,tmp_path,mode,success):
    runtime,target=native; (runtime/'mode').write_text(mode)
    result=ReaBridge(tmp_path).action({'operation':'analyze_binary','path':str(target),'timeout_seconds':5})
    assert result['success'] is success


def test_cancelled_context_never_starts_mcp_transport(native,tmp_path,monkeypatch):
    from integrations.execution_control import cancellation_scope
    from mcp.client import stdio
    runtime,target=native
    event=threading.Event();event.set()
    def forbidden_transport(*args,**kwargs):
        raise AssertionError('Cancelamento prévio não autoriza iniciar transporte')
    monkeypatch.setattr(stdio,'stdio_client',forbidden_transport)
    with cancellation_scope(event):
        result=ReaBridge(tmp_path).action({'operation':'analyze_binary','path':str(target),'timeout_seconds':5})
    assert result['success'] is False and result['error_code']=='cancelled'
    assert not (runtime/'pid').exists()
