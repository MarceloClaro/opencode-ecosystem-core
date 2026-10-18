import importlib
import importlib.util
import json
from pathlib import Path

import pytest


def module(name):
    assert importlib.util.find_spec(name) is not None, f'Implementação ausente: {name}'
    return importlib.import_module(name)


@pytest.mark.parametrize('component,name', [('rea','opencode-rea'),('mirofish','opencode-mirofish-offline'),('lean4','opencode-lean4')])
def test_component_package_has_own_identity_and_launcher(tmp_path, component, name):
    provider=module('integrations.component_plugins')
    root=tmp_path/'core com espaços'
    (root/'integrations').mkdir(parents=True)
    (root/'integrations/ecosystem_mcp.py').touch()
    (root/'integrations/component_mcp.py').touch()
    (root/'.venv/bin').mkdir(parents=True)
    (root/'.venv/bin/python').touch()
    destination=tmp_path/'package'
    receipt=provider.build_component_plugin(root,destination,component=component,target='windows-wsl')
    manifest=json.loads((destination/'plugin.json').read_text())
    overlay=json.loads((destination/'.codex-plugin/plugin.json').read_text())
    assert manifest['name']==overlay['name']==receipt['name']==name
    assert manifest['extensions']['com.openai']['requires_local_executor'] is True
    assert len(manifest['extensions']['com.openai']['interface']['shortDescription'])<=30
    server=next(iter(json.loads((destination/'mcp.json').read_text())['mcpServers'].values()))
    assert server['args'][-4:]==['-m','integrations.component_mcp','--component',component]
    assert str(root) in server['args']
    assert len(receipt['files'])==5 and receipt['installed'] is False
    assert 'MarceloClaro' in (destination/'skills/core-orchestrator/SKILL.md').read_text()


def test_unknown_component_does_not_create_package(tmp_path):
    provider=module('integrations.component_plugins')
    with pytest.raises(ValueError): provider.build_component_plugin(tmp_path,tmp_path/'pkg',component='cloud')
    assert not (tmp_path/'pkg').exists()


@pytest.mark.parametrize('component,names', [('rea',{'rea_status','rea_action'}),('mirofish',{'mirofish_status','mirofish_run'}),('lean4',{'lean4_status','lean4_verify'})])
def test_mcp_catalog_is_component_specific(component,names):
    import asyncio
    server=module('integrations.component_mcp').create_server(component)
    listed=asyncio.run(server.list_tools())
    assert {tool.name for tool in listed}==names


@pytest.mark.parametrize('config', [{'operation':'verify','code':'theorem x : True := by trivial','timeout_seconds':True}, {'operation':'verify','code':'x','project_dir':'/tmp'}, {'operation':'verify','code':'','use_mathlib':False}])
def test_invalid_lean_request_rejected_before_effects(config):
    actions=module('integrations.component_actions')
    with pytest.raises(ValueError): actions.validate_component_request('lean4',config)


def test_mirofish_cannot_select_another_runtime():
    actions=module('integrations.component_actions')
    with pytest.raises(ValueError): actions.validate_component_request('mirofish',{'operation':'run','runtime':'hermes'})


@pytest.mark.parametrize('source', ["theorem x : False := by sorry", "axiom x : False", '#eval IO.println "x"\ntheorem t : True := by trivial'])
def test_lean_incomplete_or_effectful_source_is_not_a_proof(source):
    verifier=module('integrations.local_lean').LocalLeanVerifier()
    result=verifier.verify(source)
    assert result['is_valid'] is False
    assert result['status']=='source_rejected'
    assert result['compiler_executed'] is False


def test_installed_lean_accepts_truth_and_rejects_false():
    verifier=module('integrations.local_lean').LocalLeanVerifier()
    if not verifier.status()['available']:
        pytest.skip('Compilador e namespace locais indisponíveis neste host')
    positive=verifier.verify('theorem core_demo (n : Nat) : n = n := by rfl',timeout_seconds=60)
    negative=verifier.verify('theorem core_false : (0 : Nat) = 1 := by rfl',timeout_seconds=60)
    assert positive['is_valid'] is True, positive
    assert positive['status']=='machine_checked'
    assert negative['is_valid'] is False
    assert negative['status']=='compiler_rejected', negative


def test_component_execution_passes_through_real_primary():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    assert hasattr(MarceloClaroOrchestrator,'local_component_action')
    primary=MarceloClaroOrchestrator(auto_load_agents=False)
    report=primary.local_component_action('lean4',{'operation':'verify','code':'theorem blocked : False := by sorry'})
    assert report['is_valid'] is False
    assert report['compiler_executed'] is False
    assert report['metacognition']['persisted'] is True


def test_mirofish_model_loading_is_explicitly_offline(tmp_path):
    from integrations.live_scientific_runtime import LiveScientificRuntime
    _,environment=LiveScientificRuntime()._command({'runtime':'mirofish','prompt':'Sintético','model':'local-model'}, {'python':'/usr/bin/python3','entry':'/local/oasis.py'},tmp_path,'http://127.0.0.1:1234/v1')
    assert environment['HF_HUB_OFFLINE']=='1'
    assert environment['TRANSFORMERS_OFFLINE']=='1'


def test_mirofish_uses_configured_local_endpoint(tmp_path,monkeypatch):
    actions=module('integrations.component_actions')
    config=tmp_path/'local-model.json'
    config.write_text(json.dumps({'model':'core-local','base_url':'http://127.0.0.1:11436/v1'}))
    monkeypatch.setattr(actions,'MODEL_CONFIGURATION',config,raising=False)
    value=actions.validate_component_request('mirofish',{'operation':'run','model':'core-local','prompt':'Sintético','output_dir':str(tmp_path/'run')})
    assert value['base_url']=='http://127.0.0.1:11436/v1'


def test_local_model_requests_ignore_external_proxy(monkeypatch):
    from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
    import threading
    runtime=importlib.import_module('integrations.live_scientific_runtime')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_GET(self):
            self.send_response(200);self.end_headers();self.wfile.write(b'{"local":true}')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    monkeypatch.setenv('http_proxy','http://127.0.0.1:1')
    monkeypatch.setenv('HTTP_PROXY','http://127.0.0.1:1')
    monkeypatch.setenv('no_proxy','');monkeypatch.setenv('NO_PROXY','')
    try:
        opener=getattr(runtime,'local_model_opener',None)
        assert callable(opener), 'Endpoint loopback precisa de transporte direto, sem proxy externo'
        with opener().open(f'http://127.0.0.1:{server.server_port}/',timeout=2) as response:
            assert json.load(response)=={'local':True}
    finally: server.shutdown();server.server_close();thread.join(timeout=2)


def test_local_model_redirect_is_rejected():
    import urllib.request,urllib.error
    from integrations.live_scientific_runtime import _RejectModelRedirect
    request=urllib.request.Request('http://127.0.0.1:11434/v1/models')
    with pytest.raises(urllib.error.URLError):
        _RejectModelRedirect().redirect_request(request,None,302,'Moved',{},'https://outside.invalid')


def test_lean_timeout_reports_that_compiler_executed(tmp_path,monkeypatch):
    import subprocess
    provider=module('integrations.local_lean');verifier=provider.LocalLeanVerifier()
    monkeypatch.setattr(verifier,'_runtime',lambda:tmp_path)
    monkeypatch.setattr(verifier,'_namespace',lambda _:['fixture-compiler'])
    def expire(*args,**kwargs): raise subprocess.TimeoutExpired(args[0],1)
    monkeypatch.setattr(provider.subprocess,'run',expire)
    report=verifier.verify('theorem timeout_test : True := by trivial',timeout_seconds=1)
    assert report['status']=='timeout'
    assert report['compiler_executed'] is True
    assert report['is_valid'] is False


def test_valid_lean_colon_without_space_is_accepted():
    verifier=module('integrations.local_lean').LocalLeanVerifier()
    result=verifier.verify('theorem compact: True := by trivial',timeout_seconds=60)
    assert result['is_valid'] is True, result
    assert result['status']=='machine_checked'


def test_lean_reports_axioms_for_every_submitted_theorem():
    verifier=module('integrations.local_lean').LocalLeanVerifier()
    result=verifier.verify('theorem first: True := by trivial\ntheorem second (n : Nat) : n = n := by rfl',timeout_seconds=60)
    assert result.get('theorem_names')==['first','second']
    assert len(result.get('axiom_reports',[]))==2
    assert result['is_valid'] is True
