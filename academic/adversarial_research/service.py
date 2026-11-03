"""Serviço de rigor acadêmico adversarial integrado ao orquestrador primário (R914/R916)."""
from __future__ import annotations
import hashlib, json, os, re, tempfile
from pathlib import Path
from .board import review_research
from .banca import BancaSessionStore
from .evidence import intake
from .registry import SPECIALISTS
from .router import route

def validate_rigor_config(config):
    fields={'status':set(),'inventory':set(),'plan':{'project'},'review':{'project','max_steps','timeout_seconds','cancelled','profile_scope'},
        'report':{'review_id'},'banca_start':{'review_id','project','rubric'},'banca_question':{'session_id'},
        'banca_answer':{'session_id','answer','turn_id'},'banca_report':{'session_id'},'banca_cancel':{'session_id'},
        'banca_rate':{'session_id','criterion_id','score','answer_turn_ids','justification','reviewer_id'},
        'simulation_plan':{'project','cases','seed','limits'},
        'simulation_run':{'plan','cancelled'},'simulation_report':{'simulation_id'},
        'configure':{'enabled'}}
    if not isinstance(config,dict) or config.get('operation') not in fields: raise ValueError('Operação de rigor acadêmico desconhecida')
    op=config['operation']
    if set(config)-fields[op]-{'operation'}: raise ValueError('Campos desconhecidos no contrato')
    if op in {'review','plan'} and not isinstance(config.get('project'),dict): raise ValueError('Projeto obrigatório')
    if op == 'review' and config.get('profile_scope', 'local_checks') not in {'local_checks', 'managed_profiles'}:
        raise ValueError('profile_scope deve ser local_checks ou managed_profiles')
    if op=='banca_start' and bool(config.get('project'))==bool(config.get('review_id')): raise ValueError('Forneça projeto ou review_id, exclusivamente')
    if op=='banca_answer' and (not isinstance(config.get('turn_id'),str) or not config['turn_id']): raise ValueError('turn_id da pergunta atual é obrigatório')
    if op=='configure' and type(config.get('enabled')) is not bool: raise ValueError('enabled deve ser booleano')
    if op=='simulation_plan' and type(config.get('project')) is not dict: raise ValueError('Projeto obrigatório')
    if op=='simulation_run' and type(config.get('plan')) is not dict: raise ValueError('Plano obrigatório')
    if op.startswith('simulation_'):
        from .simulation import _canonical_bytes
        _canonical_bytes(config)
    json.dumps(config,allow_nan=False)
    return dict(config)

def _write_json(path,value,*,separators=None):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,temp=tempfile.mkstemp(dir=path.parent,prefix='.rigor-',suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(value,stream,ensure_ascii=False,sort_keys=True,allow_nan=False,separators=separators)
            stream.flush();os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if Path(temp).exists(): Path(temp).unlink()

class AdversarialResearchService:
    def __init__(self,primary,state_dir=None):
        self.primary=primary
        self.root=Path(__file__).resolve().parents[2]
        self.state=Path(state_dir or Path(os.environ.get('MCI_STATE_DIR',str(self.root/'.mci_state')))/'academic_rigor')
        self.sessions=BancaSessionStore(self.state/'sessions')

    def enabled(self):
        config=self.state/'config.json'
        if not config.exists(): return True
        value=json.loads(config.read_text())
        if set(value)!={'enabled'} or type(value['enabled']) is not bool: raise ValueError('Configuração de rigor corrompida')
        return value['enabled']

    def preflight_text(self,content,topic):
        if not self.enabled(): return {'status':'disabled','scientifically_approved':False,'human_review_required':True}
        if not isinstance(content,str) or not content.strip(): return {'status':'needs_input','reason':'manuscript_not_available','scientifically_approved':False}
        raw=content.encode();digest=hashlib.sha256(raw).hexdigest()
        if len(raw)>16*1024*1024: raise ValueError('Manuscrito acima do limite de leitura')
        path=self.state/'intake'/(digest+'.md');path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        try:
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError:
            if path.is_symlink() or path.read_bytes()!=raw: raise ValueError('Snapshot de intake divergente')
        else:
            with os.fdopen(fd,'wb') as stream: stream.write(raw)
        project={'research_id':'auto-'+digest[:24],'spec_id':'SPEC-935-R914','artifact_path':str(path),
            'problem':str(topic)[:12000] or 'Avaliar o manuscrito produzido','objectives':['Identificar pendências para uma revisão científica com alegações explícitas.'],
            'study_type':'protocol','context':{},'sources':[],
            'claims':[{'claim_id':'review-request','statement':'Submeter este artefato à avaliação científica contextual.','claim_type':'normative','evidence_status':'proposed','source_refs':[],'limitations':['Intake automático não extraiu alegações semânticas do manuscrito.'],'reviewer_agent_ids':[]}]}
        report=self.review(project)
        if report.get('review_id'):
            return {'status':'needs_explicit_intake','review_id':report['review_id'],'report_sha256':report['report_sha256'],
                'review_status':report['review_status'],'objections':report['objections'],'execution_complete':report['execution_complete'],
                'claims_extracted':False,'scientifically_approved':False,'human_review_required':True,
                'reason':'Forneça alegações, fontes e contexto pelo comando rigor review; o preflight não fez revisão semântica exaustiva.'}
        return report

    def inventory(self):
        from agents.lifecycle import AgentLifecycleService
        lifecycle=AgentLifecycleService(self.root)
        rows=[]
        for role in SPECIALISTS:
            try:
                checked=lifecycle.validate(role['agent_id'])
                rows.append({'agent_id':role['agent_id'],'definition_validated':checked.get('definition_validated') is True,
                    'source_sha256':checked.get('source_sha256'),'handler':'local_rule_checks','inference_executed':False})
            except (OSError,ValueError) as exc:
                rows.append({'agent_id':role['agent_id'],'definition_validated':False,
                    'handler':'local_rule_checks','inference_executed':False,'reason':type(exc).__name__})
        ready=all(row['definition_validated'] for row in rows)
        return {'status':'definitions_validated' if ready else 'profiles_missing_or_unvalidated','enabled':self.enabled(),
            'profiles':rows,'count':len(rows),'scientific_validation':False,'inference_executed':False}

    def _start(self,role,project,artifact):
        from marceloclaro.orchestrator import blackboard,spec_registry
        from sdd.spec_engine import Specification
        from agents.lifecycle import AgentLifecycleService
        import uuid
        aid=role['agent_id']
        try:
            profile=AgentLifecycleService(self.root).validate(aid)
        except (OSError,ValueError):
            return {'dispatch_status':'profile_unavailable','agent_id':aid,
                'inference_executed':False,'task_created':False}
        if profile.get('definition_validated') is not True:
            return {'dispatch_status':'profile_unvalidated','agent_id':aid,
                'inference_executed':False,'task_created':False}
        sid='R917-AUDIT-'+uuid.uuid4().hex
        spec=Specification(sid,'Contrato de saída da auditoria local R917','Verificar estrutura/proveniência da observação, sem validar cientificamente a pesquisa.')
        digest=artifact['sha256']; known={c['claim_id'] for c in project['claims']}
        spec.add_criterion('Saída tipada e fonte física correspondente',lambda out:isinstance(out,dict) and out.get('agent_id')==aid and out.get('artifact_sha256')==digest and out.get('evaluation_scope')=='local_rule_checks')
        spec.add_criterion('Objeções com alvos existentes e responsável correto',lambda out:isinstance(out,dict) and isinstance(out.get('findings'),list) and all(isinstance(o,dict) and o.get('responsible_agent')==aid and bool(o.get('target_claim_ids')) and set(o['target_claim_ids'])<=known and o.get('severity') in {'critical','major','minor','advisory'} for o in out['findings']))
        spec.add_criterion('Contrato do perfil: status, evidência e limitações',lambda out:isinstance(out,dict) and out.get('status')=='local_check_completed' and isinstance(out.get('evidence'),list) and bool(out['evidence']) and isinstance(out.get('limitations'),list) and bool(out['limitations']))
        spec.status='red';spec_registry.specs[sid]=spec
        try:
            receipt=self.primary.agent_profile_action({'operation':'activate','agent_id':aid,
                'task':f"Auditoria acadêmica {role['number']} para {project['research_id']}: {role['responsibility']}"})
            if receipt.get('definition_validated') is not True or receipt.get('registered') is not True:
                raise RuntimeError('Perfil não validado/registrado pelo ciclo de vida do primário')
            tid=receipt.get('task_id')
            task=blackboard.tasks.get(tid) if tid else None
            if task is None or task.assigned_to not in (None,aid):
                raise RuntimeError('Tarefa A2A não confirmada ou atribuída a outro agente')
            self.primary.task_specs[tid]=sid
        except (OSError,RuntimeError,ValueError,KeyError,TypeError) as exc:
            spec_registry.specs.pop(sid,None)
            return {'dispatch_status':'dispatch_blocked','agent_id':aid,'reason':type(exc).__name__,
                'inference_executed':False,'task_created':False}
        return {'dispatch_status':'awaiting_executor','task_id':tid,'spec_id':sid,
            'agent_id':aid,'profile_sha256':profile.get('source_sha256'),
            'task_status':task.status,'assigned_to':task.assigned_to,'inference_executed':False}

    def _finish(self,ticket,role,result):
        """Não confunde a regra local com saída do agente nem fecha tarefas pendentes."""
        from marceloclaro.orchestrator import blackboard,spec_verifier,spec_registry
        if not ticket or not ticket.get('task_id'):
            return {**(ticket or {}),'local_check_executed':True,'inference_executed':False}
        task=blackboard.tasks.get(ticket['task_id'])
        if task is None:
            return {**ticket,'dispatch_status':'task_missing','local_check_executed':True,'inference_executed':False}
        if task.status!='completed':
            return {**ticket,'dispatch_status':'awaiting_executor','task_status':task.status,
                'local_check_executed':True,'inference_executed':False,
                'limitations':['A tarefa A2A foi criada, mas nenhum resultado do especialista foi observado nesta chamada.']}
        try:
            verification=spec_verifier.verify(ticket['spec_id'],task.result)
        except (OSError,RuntimeError,ValueError,TypeError,KeyError) as exc:
            verification={'verified':False,'status':'contract_verification_error','error_type':type(exc).__name__}
        if verification.get('verified') is True:
            spec_registry.specs.pop(ticket['spec_id'],None)
            self.primary.task_specs.pop(ticket['task_id'],None)
        reported_inference=(isinstance(task.result,dict) and task.result.get('llm_inference_executed') is True)
        return {**ticket,'dispatch_status':'agent_result_observed' if verification.get('verified') is True else 'agent_result_contract_failed',
            'task_status':task.status,'verification':verification,'local_check_executed':True,
            'inference_executed':reported_inference,'confidence_promoted':False,
            'verification_scope':'typed_output_contract_only'}

    def review(self,project,*,profile_scope='local_checks',**limits):
        if not self.enabled(): return {'status':'disabled','scientifically_approved':False,'human_review_required':True}
        if profile_scope not in {'local_checks','managed_profiles'}:
            raise ValueError('profile_scope deve ser local_checks ou managed_profiles')
        callbacks=({'on_start':self._start,'on_result':self._finish} if profile_scope=='managed_profiles' else {})
        report=review_research(project,**callbacks,**limits)
        from marceloclaro.orchestrator import spec_registry
        spec=spec_registry.get(report['spec_id'])
        report['specification_loaded']=spec is not None
        if spec is None:
            report['gates'][0].update(passed=False,status='spec_not_registered')
            report['unresolved_gaps'].append({'code':'spec_not_registered','spec_id':report['spec_id']})
            report['review_status']='blocked'
        report['review_id']='review-'+report['report_sha256'][:32]
        report['analysis_sha256']=report.pop('report_sha256')
        report['dispatch_scope']=profile_scope
        report['agent_inference_executed']=any(
            result.get('orchestration',{}).get('inference_executed') is True
            for result in report.get('specialist_results',[]))
        report['metacognition']={**self.primary._record_knowledge_outcome('research.rigor.review',project.get('research_id','unknown'),
            {'status':report['review_status'],'analysis_sha256':report['analysis_sha256'],
             'artifact_sha256':report['reviewed_artifact_hash'],'dispatch_scope':profile_scope,
             'local_rule_checks':len(report.get('specialist_results',[])),
             'agent_inference_executed':report['agent_inference_executed'],
             'scientifically_approved':False,'human_review_required':True,
             'confidence_promoted':False,'externally_validated':False}),
             'confidence_promoted':False,'externally_validated':False}
        report['report_sha256']=hashlib.sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()
        _write_json(self.state/'reports'/(report['review_id']+'.json'),report)
        return report

    def report(self,rid):
        if not isinstance(rid,str) or not re.fullmatch(r'review-[a-f0-9]{32}',rid): raise ValueError('Identificador de revisão inválido')
        path=self.state/'reports'/(rid+'.json')
        if path.is_symlink() or path.stat().st_size>8*1024*1024: raise ValueError('Relatório inválido')
        value=json.loads(path.read_text()); expected=value.pop('report_sha256')
        if hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()!=expected: raise ValueError('Relatório corrompido')
        return {**value,'report_sha256':expected}

    def simulation_plan(self,project,**options):
        """Intake sem persistência, registro de perfis ou acesso ao spec_registry."""
        from .simulation import plan_simulation
        return plan_simulation(project,**options)

    def _simulation_path(self,simulation_id):
        if not isinstance(simulation_id,str) or not re.fullmatch(r'academic-sim-[a-f0-9]{32}',simulation_id):
            raise ValueError('Identificador de simulação inválido')
        path=self.state/'simulations'/(simulation_id+'.json')
        if any(p.is_symlink() for p in (path,*path.parents)):
            raise ValueError('Symlinks não são permitidos no armazenamento de simulações')
        if path.exists() and not path.is_file():
            raise ValueError('Destino de relatório não é arquivo regular')
        if any(p.exists() and not p.is_dir() for p in path.parents):
            raise ValueError('Diretório de simulação inválido')
        return path

    def simulation_run(self,plan,*,cancelled=False):
        from .simulation import _canonical_bytes, _digest, _safeguards, run_simulation
        # Verificação do destino antes de executar; a validação integral dos
        # dados/fontes/plano continua pertencendo ao adaptador, não ao primário.
        self._simulation_path(plan.get('simulation_id'))
        report=run_simulation(plan,cancelled=cancelled)
        path=self._simulation_path(report['simulation_id'])
        if len(_canonical_bytes(report))>8*1024*1024:
            raise ValueError('Relatório de simulação acima de 8 MiB')
        observation={
            'status':report['status'],'simulation_id':report['simulation_id'],
            'plan_sha256':report['plan_sha256'],'trajectory_sha256':report['trajectory_sha256'],
            'artifact_sha256':report['artifact_sha256'],'usage':dict(report['usage']),
            'execution_started':report['execution_started'],
            'simulation_executed':report['simulation_executed'],
            'execution_complete':report['execution_complete'],
            'externally_validated':False,**_safeguards(),
        }
        receipt=self.primary._record_knowledge_outcome(
            'research.rigor.simulation',report['simulation_id'],observation)
        report['metacognition']={**receipt,'confidence_promoted':False,'externally_validated':False}
        report['report_sha256']=_digest(report)
        if len(_canonical_bytes(report))>8*1024*1024:
            raise ValueError('Relatório de simulação acima de 8 MiB')
        self._simulation_path(report['simulation_id'])
        _write_json(path,report,separators=(',',':'))
        return report

    def simulation_report(self,simulation_id):
        """Consulta limitada e somente leitura: não reexecuta revisão ou engine."""
        import stat
        from .simulation import _digest, _safeguards
        path=self._simulation_path(simulation_id)
        maximum=8*1024*1024
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
            with os.fdopen(fd,'rb') as stream:
                info=os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or not 0<info.st_size<=maximum:
                    raise ValueError('Relatório de simulação inválido ou excessivo')
                raw=stream.read(maximum+1)
        except OSError as exc:
            raise ValueError('Relatório de simulação indisponível') from exc
        if len(raw)>maximum:
            raise ValueError('Relatório de simulação acima de 8 MiB')

        def unique_object(pairs):
            value={}
            for key,child in pairs:
                if key in value: raise ValueError('Chave duplicada no relatório')
                value[key]=child
            return value

        try:
            value=json.loads(raw.decode('utf-8'),object_pairs_hook=unique_object)
        except (UnicodeError,RecursionError) as exc:
            raise ValueError('Relatório de simulação inválido') from exc
        if type(value) is not dict: raise ValueError('Relatório de simulação inválido')
        expected=value.get('report_sha256')
        if not isinstance(expected,str) or not re.fullmatch(r'[a-f0-9]{64}',expected):
            raise ValueError('Selo do relatório inválido')
        if _digest({k:v for k,v in value.items() if k!='report_sha256'})!=expected:
            raise ValueError('Relatório de simulação corrompido')
        if (value.get('simulation_id')!=simulation_id or value.get('spec_id')!='SPEC-935-R920'
                or value.get('status') not in ('completed','partial','cancelled')
                or any(value.get(k) is not v for k,v in _safeguards().items())
                or type(value.get('cases')) is not list
                or value.get('trajectory_sha256')!=_digest(value['cases'])):
            raise ValueError('Contrato do relatório de simulação divergente')
        return value

    def action(self,config):
        config=validate_rigor_config(config);op=config.pop('operation')
        if op in {'status','inventory'}: return self.inventory()
        if op=='configure':
            _write_json(self.state/'config.json',config)
            return {'status':'configured',**config,'prior_reports_preserved':True,'scientifically_approved':False}
        if op=='plan':
            project,artifact,manifest=intake(config['project'])
            return {'status':'planned','agent_ids':[r['agent_id'] for r in route(project)],'artifact_sha256':artifact['sha256'],'execution_started':False,'local_sources_inspected':sum(s['integrity_checked'] for s in manifest),'external_sources_retrieved':0}
        if op=='review': return self.review(**config)
        if op=='report': return self.report(config['review_id'])
        if op=='simulation_plan': return self.simulation_plan(**config)
        if op=='simulation_run': return self.simulation_run(**config)
        if op=='simulation_report': return self.simulation_report(config.get('simulation_id'))
        if op=='banca_start':
            review=self.report(config['review_id']) if config.get('review_id') else self.review(config['project'])
            return self.sessions.start(review,config.get('rubric'))
        sid=config.get('session_id')
        if op=='banca_question': return self.sessions.question(sid)
        if op=='banca_answer': return self.sessions.answer(sid,config.get('answer'),config['turn_id'])
        if op=='banca_report': return self.sessions.finish(sid)
        if op=='banca_cancel': return self.sessions.cancel(sid)
        if op=='banca_rate':
            handler=getattr(self.sessions,'rate',None)
            if not callable(handler):
                raise ValueError('Pontuação banca_rate indisponível: avaliador humano não implementado nesta versão')
            return handler(sid,config['criterion_id'],config['score'],config['answer_turn_ids'],config['justification'],config['reviewer_id'])
        raise ValueError('Operação não implementada')
