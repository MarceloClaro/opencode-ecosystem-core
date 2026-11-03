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
    positive=verifier.verify('theorem core_demo (n : Nat) : n = n := by rfl')
    negative=verifier.verify('theorem core_false : (0 : Nat) = 1 := by rfl')
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
