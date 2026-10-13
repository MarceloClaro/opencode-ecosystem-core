"""Contratos da revisão REA; contrapróvas locais sem inferência LLM."""
from pathlib import Path
import asyncio
import importlib
import json
import os

import pytest
from integrations.rea_assistant import LocalReaAssistant, explain_report, run_isolated_worker, setup_local_agent
from marceloclaro.rea_cli import run_rea_cli


def api(name):
    module = importlib.import_module('integrations.rea_assistant')
    assert hasattr(module, name), 'bootstrap da nova interface, separado das contrapróvas funcionais'
    return getattr(module, name)


def mock_client_runner(module, monkeypatch, runner):
    # O mesmo oráculo observa os bytes anteriores e o helper supervisionado;
    # somente o ponto de I/O muda, sem simular permissões ou a validação.
    if callable(getattr(module, '_run_agent_client', None)):
        monkeypatch.setattr(module, '_run_agent_client', runner)
    else:
        monkeypatch.setattr(module.subprocess, 'run', runner)


def test_javascript_avulso_preserva_bytes_no_diretorio_estatico(tmp_path):
    source=tmp_path/'original.js'
    data=b'process.exit(99); module.exports = (a,b)=>a+b;'
    source.write_bytes(data)
    with api('prepare_javascript_target')(source) as prepared:
        path=Path(prepared)
        assert path.is_dir() and (path/'original.js').read_bytes()==data
        assert path!=tmp_path
    assert not path.exists() and source.read_bytes()==data


@pytest.mark.parametrize('directory',[True,False])
def test_diretorio_e_asar_nao_sao_reempacotados(tmp_path,directory):
    source=tmp_path/'app' if directory else tmp_path/'app.asar'
    source.mkdir() if directory else source.write_bytes(b'known-static-bytes')
    with api('prepare_javascript_target')(source) as prepared:
        assert Path(prepared)==source
    assert source.exists()


def test_perfil_define_primario_e_modelo_auxiliar_locais(tmp_path):
    report=setup_local_agent(root=tmp_path,model='local-model')
    profile=json.loads(Path(report['profile_path']).read_text())
    assert profile.get('default_agent')=='marceloclaro'
    assert profile.get('small_model')==profile['model']=='rea_local/local-model'
    assert profile['permission'].get('*')=='deny'
    assert profile['agent']['marceloclaro'].get('permission',{}).get('*')=='deny'
    assert profile.get('autoupdate') is False and profile.get('plugin')==[]


def test_lancamento_isola_configuracoes_e_credenciais(tmp_path,monkeypatch):
    module=importlib.import_module('integrations.rea_assistant')
    setup_local_agent(root=tmp_path,model='local-model')
    binary=tmp_path/'opencode';binary.write_text('placeholder');binary.chmod(0o700)
    monkeypatch.setenv('OPENCODE_BIN',str(binary))
    monkeypatch.setenv('OPENAI_API_KEY','credential-that-must-not-be-forwarded')
    seen=[]
    def run(command,**kwargs):
        seen.append((command,kwargs))
        config=json.loads(kwargs['env']['OPENCODE_CONFIG_CONTENT'])
        assert config['model']=='rea_local/local-model'
        assert kwargs['cwd']!=tmp_path and not Path(kwargs['cwd']).is_relative_to(tmp_path)
        assert kwargs['env']['HOME']!=os.environ['HOME']
        assert 'OPENAI_API_KEY' not in kwargs['env']
        assert kwargs['env']['OPENCODE_DISABLE_MODELS_FETCH']=='true'
        assert config['mcp']['rea-local-assistant']['environment']['HOME']==os.environ['HOME']
        kwargs['stdout'].write(json.dumps(config));kwargs['stdout'].flush()
        return type('Done',(),{'returncode':0,'stderr':''})()
    mock_client_runner(module, monkeypatch, run)
    report=api('launch_local_agent')(root=tmp_path,check_only=True)
    assert report['success'] is True and report['model_inference_verified'] is False
    assert len(seen)==1 and seen[0][0][1:]==['debug','config']


@pytest.mark.parametrize('field',['endpoint','mcp-command','primary-permission'])
def test_lancamento_recusa_configuracao_resolvida_divergente(tmp_path,monkeypatch,field):
    module=importlib.import_module('integrations.rea_assistant')
    setup_local_agent(root=tmp_path,model='local-model')
    binary=tmp_path/'opencode';binary.write_text('placeholder');binary.chmod(0o700)
    monkeypatch.setenv('OPENCODE_BIN',str(binary))
    def run(command,**kwargs):
        config=json.loads(kwargs['env']['OPENCODE_CONFIG_CONTENT'])
        if field=='endpoint':config['provider']['rea_local']['options']['baseURL']='https://remote.invalid/v1'
        elif field=='mcp-command':config['mcp']['rea-local-assistant']['command']=['/local/foreign-client']
        else:config['agent']['marceloclaro']['permission']['*']='allow'
        kwargs['stdout'].write(json.dumps(config));kwargs['stdout'].flush()
        return type('Done',(),{'returncode':0,'stderr':''})()
    mock_client_runner(module, monkeypatch, run)
    rejected=False
    try:api('launch_local_agent')(root=tmp_path,check_only=True)
    except ValueError:rejected=True
    assert rejected is True


def test_cli_encaminha_agente_check_ao_primario(capsys):
    calls=[]
    class Primary:
        def rea_assistant_action(self,config):
            calls.append(config);return {'success':True,'operation':'agent','verification':'configuration_only'}
    assert run_rea_cli(['agent','--check'],lambda **kwargs:Primary())==0
    assert calls[0]['operation']=='agent' and calls[0]['check_only'] is True
    assert json.loads(capsys.readouterr().out)['success'] is True


def test_servidor_mcp_reutiliza_primario(monkeypatch):
    from integrations.rea_assistant_mcp import create_mcp_server
    from marceloclaro import orchestrator
    created=[]
    class Primary:
        def __init__(self,**kwargs):created.append(self)
        def rea_assistant_action(self,config):return {'success':True,'operation':config['operation']}
    monkeypatch.setattr(orchestrator,'MarceloClaroOrchestrator',Primary)
    server=create_mcp_server()
    async def calls():
        await server.call_tool('core_rea_status',{})
        await server.call_tool('core_rea_status',{})
    asyncio.run(calls())
    assert len(created)==1


def test_setup_texto_mostra_caminhos_sem_alegar_inspecao():
    text=explain_report({'success':True,'operation':'setup','profile_path':'/local/profile.json',
        'mcp_linux_path':'/local/mcp-linux.json','mcp_windows_path':'/local/mcp-windows.json',
        'limitations':['Configuração não comprova inferência.']})
    assert '/local/profile.json' in text and '/local/mcp-windows.json' in text
    assert 'Inspeção local estática' not in text and 'não comprova inferência' in text


def test_status_nao_aprova_guard_falho(tmp_path,monkeypatch):
    monkeypatch.setattr('integrations.rea_assistant.run_isolated_worker',lambda *a,**kw:{'success':False,'status':'blocked'})
    monkeypatch.setattr('integrations.rea_bridge.ReaBridge.status',lambda self:{'available':True})
    report=LocalReaAssistant(root=tmp_path).action({'operation':'status'})
    assert report['success'] is False


def test_worker_preserva_erro_local_estruturado(tmp_path):
    report=run_isolated_worker({'operation':'inspect','path':str(tmp_path/'absent.js'),'kind':'javascript'},root=tmp_path,timeout_seconds=20)
    assert report['success'] is False and report['status']=='failed'
    assert 'absent.js' in report['error']


@pytest.mark.parametrize('timeout',[True,False])
def test_timeout_booleano_recusado(tmp_path,timeout):
    rejected=False
    try:
        run_isolated_worker({'operation':'probe'},root=tmp_path,timeout_seconds=timeout)
    except ValueError:
        rejected=True
    assert rejected is True


def test_explicacao_expoe_metadados_reais_sem_inventar_comportamento():
    evidence={'evidence_id':'ev-managed-local','operation':'inspect_managed_artifact',
        'normalized_result':{'assembly':{'name':'Biblioteca.Exemplo','version':'1.2.3.4'},
            'target_frameworks':['.NETCoreApp,Version=v8.0'],
            'metadata':{'table_row_counts':{'TypeDef':2,'MethodDef':3}},
            'references':[{'name':'System.Runtime','version':'8.0.0.0'}]}}
    text=explain_report({'success':True,'target_kind':'dotnet','provider_report':{'response':{'structuredContent':evidence}},
        'findings':[],'limitations':['A aplicação alvo não foi executada.']})
    assert 'Biblioteca.Exemplo' in text and '1.2.3.4' in text and 'ev-managed-local' in text
    assert '2 tipo(s)' in text and '3 método(s)' in text and 'System.Runtime' in text
    assert 'A aplicação alvo não foi executada' in text
    assert 'recuperado integralmente' not in text


def test_explicacao_expoe_funcao_nativa_com_limite_estatico():
    evidence={'evidence_id':'ev-native-local','operation':'analyze_function',
        'normalized_result':{'procedure':{'name':'calcular','address':'0x00401000'},
            'decompilation':{'text':'int calcular(void) { return 7; }'}}}
    text=explain_report({'success':True,'target_kind':'native','provider_report':{'response':{'analysis':{'structuredContent':evidence}}},
        'findings':[],'limitations':['A aplicação alvo não foi executada.']})
    assert 'calcular' in text and '0x00401000' in text and 'ev-native-local' in text
    assert 'A aplicação alvo não foi executada' in text
