"""CLI de rigor acadêmico: mesma fachada primária usada por MCP."""
import argparse,json
from pathlib import Path

class _Parser(argparse.ArgumentParser):
    def error(self,message): raise ValueError(message)

def run_rigor_cli(argv,orchestrator=None):
    parser=_Parser(prog='rigor',description='Auditoria adversarial local e banca com respostas efetivas.')
    parser.add_argument('operation',choices=['status','inventory','plan','review','report','banca_start','banca_question','banca_answer','banca_report','banca_rate','banca_cancel','configure'])
    parser.add_argument('--config',type=Path,help='Objeto JSON com os argumentos da operação')
    try:
        args=parser.parse_args(argv);config={}
        if args.config:
            if args.config.stat().st_size>4*1024*1024: raise ValueError('Configuração acima de 4 MiB')
            config=json.loads(args.config.read_text(encoding='utf-8-sig'))
            if not isinstance(config,dict): raise ValueError('Configuração deve ser objeto')
            if 'operation' in config and config['operation']!=args.operation: raise ValueError('Operações divergentes')
        from academic.adversarial_research.service import validate_rigor_config
        config=validate_rigor_config({**config,'operation':args.operation})
        if orchestrator is None:
            from marceloclaro.orchestrator import MarceloClaroOrchestrator
            orchestrator=MarceloClaroOrchestrator(auto_load_agents=False)
        result=orchestrator.academic_rigor_action(config)
        print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
        return 1 if result.get('status')=='error' else 0
    except (ValueError,OSError,RuntimeError,KeyError,ImportError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc),'scientifically_approved':False},ensure_ascii=False))
        return 2
