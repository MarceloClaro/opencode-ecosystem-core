"""R913: contratos fechados das fachadas locais; sem novo orquestrador."""
from __future__ import annotations
import math
import json
from pathlib import Path

MODEL_CONFIGURATION=Path.home()/'.local/share/opencode-core/mirofish-local-model.json'

def model_configuration():
    if not MODEL_CONFIGURATION.exists(): return None
    if MODEL_CONFIGURATION.stat().st_size>8192: raise ValueError('Configuração de modelo excessiva')
    value=json.loads(MODEL_CONFIGURATION.read_text())
    allowed={'model','base_url','binary','binary_sha256','model_path','model_bytes'}
    if not isinstance(value,dict) or set(value)-allowed: raise ValueError('Configuração local de modelo inválida')
    from integrations.live_scientific_runtime import validate_runtime_config
    validate_runtime_config({'runtime':'mirofish','prompt':'Verificação de configuração','output_dir':'/tmp/not-executed','model':value.get('model'),'base_url':value.get('base_url')})
    return value

def validate_component_request(component,config):
    if component not in {'rea','mirofish','lean4'} or not isinstance(config,dict): raise ValueError('Componente/configuração inválido')
    out=dict(config)
    operation=out.get('operation')
    if operation=='status':
        if set(out)!={'operation'}: raise ValueError('Status não aceita outros campos')
        return out
    if component=='rea':
        from integrations.rea_bridge import ReaBridge
        if operation not in ReaBridge.OPERATIONS: raise ValueError('Operação REA inválida')
        return out  # rea_action valida seu contrato completo antes dos efeitos.
    if component=='mirofish':
        if operation!='run' or ('runtime' in out and out['runtime']!='mirofish'): raise ValueError('Somente execução MiroFish')
        out.pop('operation')
        out['runtime']='mirofish'
        local=model_configuration()
        if 'base_url' not in out and local and out.get('model')==local['model']:
            out['base_url']=local['base_url']
        from integrations.live_scientific_runtime import validate_runtime_config
        return {'operation':'run',**validate_runtime_config(out)}
    if operation!='verify' or set(out)-{'operation','code','use_mathlib','timeout_seconds'}: raise ValueError('Contrato Lean inválido')
    code=out.get('code')
    timeout=out.setdefault('timeout_seconds',30)
    if not isinstance(code,str) or not code.strip() or len(code)>40000 or '\x00' in code: raise ValueError('Fonte Lean inválida')
    if type(out.setdefault('use_mathlib',False)) is not bool: raise ValueError('use_mathlib deve ser booleano')
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not math.isfinite(timeout) or not 1<=timeout<=60: raise ValueError('Prazo Lean inválido')
    return out

def dispatch_component(primary,component,config):
    config=validate_component_request(component,config)
    operation=config.pop('operation')
    if component=='rea': return primary.rea_action({'operation':operation,**config})
    if component=='mirofish':
        local=model_configuration()
        if operation=='run':
            if local and config['model']==local['model'] and config['base_url']==local['base_url']:
                from integrations.local_mirofish_model import managed_endpoint
                with managed_endpoint(local) as lifecycle:
                    result=primary.scientific_runtime_run(**config)
                result['local_model_lifecycle']=lifecycle
                return result
            return primary.scientific_runtime_run(**config)
        from integrations.live_scientific_runtime import LiveScientificRuntime, DEFAULTS
        try:
            runtime=LiveScientificRuntime()._resolve({'runtime':'mirofish','runtime_dir':DEFAULTS['mirofish']})
            return {'status':'installed','available':True,'verification':'installation_only','runtime':runtime,'configured_local_model':local,'inference_executed':False,'backend_required_for_cli':False,'scientific_claim_eligible':False}
        except (ValueError,OSError,RuntimeError) as exc:
            return {'status':'unavailable','available':False,'reason':str(exc),'inference_executed':False}
    from integrations.local_lean import LocalLeanVerifier
    verifier=LocalLeanVerifier()
    return verifier.status() if operation=='status' else verifier.verify(**config)
