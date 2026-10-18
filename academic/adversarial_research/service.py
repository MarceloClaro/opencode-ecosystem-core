"""Fachada de pesquisa: usa ciclo de vida, Blackboard, MetaBus e SDD do primário."""
from __future__ import annotations
import hashlib,json,os,re,tempfile
from pathlib import Path
from .board import review_research
from .banca import BancaSessionStore
from .evidence import intake
from .registry import SPECIALISTS
from .router import route

def validate_rigor_config(config):
    fields={'status':set(),'inventory':set(),'plan':{'project'},'review':{'project','max_steps','timeout_seconds','profile_scope'},
        'report':{'review_id'},'banca_start':{'review_id','project','rubric'},'banca_question':{'session_id'},
        'banca_answer':{'session_id','answer','turn_id'},'banca_report':{'session_id'},'banca_cancel':{'session_id'},
        'banca_rate':{'session_id','criterion_id','score','answer_turn_ids','justification','reviewer_id'},
        'configure':{'enabled'}}
    if not isinstance(config,dict) or config.get('operation') not in fields: raise ValueError('Operação de rigor acadêmico desconhecida')
    op=config['operation']
    if set(config)-fields[op]-{'operation'}: raise ValueError('Campos desconhecidos no contrato')
    if op in {'review','plan'} and not isinstance(config.get('project'),dict): raise ValueError('Projeto obrigatório')
    if op=='banca_start' and bool(config.get('project'))==bool(config.get('review_id')): raise ValueError('Forneça projeto ou review_id, exclusivamente')
    if op=='banca_answer' and (not isinstance(config.get('turn_id'),str) or not config['turn_id']): raise ValueError('turn_id da pergunta atual é obrigatório')
    if op=='configure' and type(config.get('enabled')) is not bool: raise ValueError('enabled deve ser booleano')
    json.dumps(config,allow_nan=False)
    return dict(config)

def _write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd,temp=tempfile.mkstemp(dir=path.parent,prefix='.rigor-',suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(value,stream,ensure_ascii=False,sort_keys=True,allow_nan=False)
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
        """Conecta produtores legados; exige intake explícito para parecer semântico."""
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
            # Conservar o recibo original sem alterar o relatório já selado.
            return {'status':'needs_explicit_intake','review_id':report['review_id'],'report_sha256':report['report_sha256'],
                'review_status':report['review_status'],'objections':report['objections'],'execution_complete':report['execution_complete'],
                'claims_extracted':False,'scientifically_approved':False,'human_review_required':True,
                'reason':'Forneça alegações, fontes e contexto pelo comando rigor review; o preflight não fez revisão semântica exaustiva.'}
        return report

    def inventory(self):
        from agents.lifecycle import AgentLifecycleService
        lifecycle=AgentLifecycleService(self.root); rows=[]
        for role in SPECIALISTS:
            try:
                checked=lifecycle.validate(role['agent_id'])
                valid=checked.get('definition_validated') is True
                rows.append({'agent_id':role['agent_id'],'definition_validated':valid,'source_sha256':checked.get('source_sha256'),'handler':'local_rule_checks','inference_executed':False})
            except (OSError,ValueError) as exc: rows.append({'agent_id':role['agent_id'],'definition_validated':False,'reason':type(exc).__name__})
        return {'status':'definitions_validated' if all(r['definition_validated'] for r in rows) else 'pending_registration','enabled':self.enabled(),'profiles':rows,'count':len(rows),'scientific_validation':False,'inference_executed':False}

    def _start(self,role,project,artifact):
        from marceloclaro.orchestrator import blackboard,spec_registry
        from sdd.spec_engine import Specification
        import uuid
        sid='R914-AUDIT-'+uuid.uuid4().hex
        spec=Specification(sid,'Contrato de saída da auditoria local','Verificar estrutura/proveniência da observação, sem validar cientificamente a pesquisa.')
        aid=role['agent_id']; digest=artifact['sha256']; known={c['claim_id'] for c in project['claims']}
        spec.add_criterion('Saída tipada e fonte física correspondente',lambda out:isinstance(out,dict) and out.get('agent_id')==aid and out.get('artifact_sha256')==digest and out.get('evaluation_scope')=='local_rule_checks')
        spec.add_criterion('Objeções com alvos existentes e responsável correto',lambda out:isinstance(out,dict) and isinstance(out.get('findings'),list) and all(isinstance(o,dict) and o.get('responsible_agent')==aid and bool(o.get('target_claim_ids')) and set(o['target_claim_ids'])<=known and o.get('severity') in {'critical','major','minor','advisory'} for o in out['findings']))
        spec.add_criterion('Contrato do perfil: status, evidência e limitações',lambda out:isinstance(out,dict) and out.get('status')=='local_check_completed' and isinstance(out.get('evidence'),list) and bool(out['evidence']) and isinstance(out.get('limitations'),list) and bool(out['limitations']))
        spec.status='red';spec_registry.specs[sid]=spec
        try:
            receipt=self.primary.agent_profile_action({'operation':'activate','agent_id':role['agent_id'],
                'task':f"Auditoria local {role['number']} de {project['research_id']}: {role['responsibility']}"})
            if receipt.get('definition_validated') is not True or receipt.get('status')!='assigned' or receipt.get('assigned_to')!=aid: raise RuntimeError('Especialista indisponível ou atribuição não confirmada')
            tid=receipt['task_id'];self.primary.task_specs[tid]=sid
            if blackboard.tasks[tid].assigned_to!=aid: raise RuntimeError('Atribuição alterada')
        except Exception:
            spec_registry.specs.pop(sid,None)
            if 'receipt' in locals() and receipt.get('task_id'): self._close(receipt['task_id'],aid,False,{'status':'failed','reason':'setup_failed'})
            raise
        return {'task_id':tid,'spec_id':sid,'profile_sha256':receipt['source_sha256']}

    def _close(self,tid,aid,success,packet,verification=None):
        from marceloclaro.orchestrator import blackboard,metabus
        task=blackboard.tasks.get(tid)
        if task is None or task.assigned_to!=aid: raise RuntimeError('Fechamento de tarefa divergente recusado')
        metabus.publish('task.complete',{'task_id':tid,'agent_id':aid,'status':'completed' if success else 'failed',
            'result':packet,'sdd_verification':verification,'learning_scope':'contract_only'},source_agent=self.primary.id)
        if tid in self.primary.task_stakes:
            self.primary.economy.resolve(tid,success=success)
            self.primary.task_stakes.pop(tid,None)
        self.primary.task_specs.pop(tid,None)

    def _finish(self,ticket,role,result):
        from marceloclaro.orchestrator import blackboard,metabus,spec_verifier
        from agents.lifecycle import AgentLifecycleService
        packet={**result,'findings':result['objections'],'evidence':[{'artifact_sha256':result['artifact_sha256'],'target_claim_ids':result['target_claim_ids']}],
             'limitations':[role['limitations'],'Contrato estrutural não comprova validade científica; nenhuma inferência LLM foi executada.']}
        try:
            current=AgentLifecycleService(self.root).validate(role['agent_id'])
            if current.get('source_sha256')!=ticket['profile_sha256']: raise RuntimeError('Perfil alterado durante execução')
            verification=spec_verifier.verify(ticket['spec_id'],packet)
        except Exception:
            self._close(ticket['task_id'],role['agent_id'],False,{'status':'failed','reason':'contract_verification_failed'})
            raise
        self._close(ticket['task_id'],role['agent_id'],verification.get('verified') is True,packet,verification)
        from marceloclaro.orchestrator import spec_registry
        spec_registry.specs.pop(ticket['spec_id'],None)
        observation=self.primary._record_knowledge_outcome('research.rigor.specialist',role['agent_id'],{'task_id':ticket['task_id'],'artifact_sha256':result['artifact_sha256'],'contract_verified':verification.get('verified') is True,'llm_inference_executed':False})
        return {**ticket,'task_status':blackboard.tasks[ticket['task_id']].status,'verification':verification,'metacognition':observation,'confidence_promoted':False,'verification_scope':'typed_output_contract_only'}

    def review(self,project,**limits):
        if not self.enabled(): return {'status':'disabled','scientifically_approved':False,'human_review_required':True}
        report=review_research(project,on_start=self._start,on_result=self._finish,**limits)
        from marceloclaro.orchestrator import spec_registry
        spec=spec_registry.get(report['spec_id'])
        report['specification_loaded']=spec is not None
        if spec is None:
            report['gates'][0].update(passed=False,status='spec_not_registered')
            report['unresolved_gaps'].append({'code':'spec_not_registered','spec_id':report['spec_id']})
            report['review_status']='blocked'
        report['review_id']='review-'+report['report_sha256'][:32]
        report['analysis_sha256']=report.pop('report_sha256')
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
        if op=='banca_start':
            review=self.report(config['review_id']) if config.get('review_id') else self.review(config['project'])
            return self.sessions.start(review,config.get('rubric'))
        sid=config.get('session_id')
        if op=='banca_question': return self.sessions.question(sid)
        if op=='banca_answer': return self.sessions.answer(sid,config.get('answer'),config['turn_id'])
        if op=='banca_report': return self.sessions.finish(sid)
        if op=='banca_cancel': return self.sessions.cancel(sid)
        if op=='banca_rate': return self.sessions.rate(sid,config['criterion_id'],config['score'],config['answer_turn_ids'],config['justification'],config['reviewer_id'])
        raise ValueError('Operação não implementada')
