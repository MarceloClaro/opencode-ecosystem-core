"""Motor de revisão local: objeções rastreáveis, sem certificar qualidade científica."""
from dataclasses import asdict
import hashlib,json,math,time
from .contracts import ResearchReview
from .evidence import intake
from .guards import check_specialist
from .registry import SPECIALISTS,FAMILIES,specialist
from .router import route
from .banca import BancaSessionStore

def review_research(project,*,max_steps=34,timeout_seconds=30,cancelled=False,on_start=None,on_result=None,profile_scope='full'):
    if type(max_steps) is not int or not 1<=max_steps<=34: raise ValueError('Orçamento de 1 a 34 especialistas')
    if isinstance(timeout_seconds,bool) or not isinstance(timeout_seconds,(int,float)) or not math.isfinite(timeout_seconds) or not 0<timeout_seconds<=120: raise ValueError('Prazo inválido')
    if type(cancelled) is not bool: raise ValueError('Cancelamento inválido')
    if profile_scope not in {'pilot','full'}: raise ValueError('Escopo de perfis inválido')
    started=time.monotonic(); p,artifact,manifest=intake(project)
    selected=route(p)
    if profile_scope=='pilot':
        from .registry import PILOT_NUMBERS
        selected=[r for r in selected if r['number'] in PILOT_NUMBERS]
    objections=[]; results=[]; gaps=[]; flow=[]; legacy=None
    def legacy_review():
        from academic.rigorous_board import RigorousBoard
        value=RigorousBoard().review(artifact['text'],venue='auto').to_dict()
        value.update(binding=False,evaluation_scope='legacy_keyword_heuristic',external_validation=False)
        return value
    for role in selected:
        from integrations.execution_control import is_cancelled
        if is_cancelled(): cancelled=True
        if cancelled or len(results)>=max_steps or time.monotonic()-started>=timeout_seconds: break
        stage={'A01':'intake','A02':'intake','A03':'evidence_ledger','A04':'coordination','A32':'adversarial_examiner','A33':'rubric_status','A34':'remediation'}.get(role['number'],'specialists')
        if role['number']=='A34':
            legacy=legacy_review();flow.append({'stage':'legacy_board','binding':False})
        result={'agent_id':role['agent_id'],'number':role['number'],'status':'local_check_completed','evaluation_scope':'local_rule_checks','artifact_sha256':artifact['sha256'],'target_claim_ids':[c['claim_id'] for c in p['claims']],'objections':[],'llm_inference_executed':False}
        try:
            ticket=on_start(role,p,artifact) if on_start else None
            found=check_specialist(role,p,manifest);result['objections']=found
            result['stage_output']={'A01':{'artifact_bytes':artifact['bytes']},'A03':{'source_count':len(manifest)},'A04':{'coordinator':'marceloclaro','selected_roles':len(selected)},'A32':{'question_families':8},'A33':{'automatic_scores':False},'A34':{'recommended_actions':list(dict.fromkeys(o['required_evidence'] for o in objections))}}.get(role['number'],{'checks':'conditional_rules_on_explicit_claims'})
            if on_result:
                result['orchestration']=on_result(ticket,role,result)
                if result['orchestration'].get('verification',{}).get('verified') is not True or result['orchestration'].get('task_status')!='completed': raise RuntimeError('Contrato da saída não aprovado')
        except Exception as exc:
            result.update(status='failed',error=type(exc).__name__,reason=str(exc)[:500])
            # Conservar achados produzidos mesmo quando o transporte/contrato falha.
            objections.extend(result['objections'])
            results.append(result);gaps.append({'code':'specialist_failed','agent_id':role['agent_id'],'reason':type(exc).__name__})
            break
        flow.append({'stage':stage,'agent_id':role['agent_id']})
        results.append(result);objections.extend(result['objections'])
        for claim in p['claims']:
            if role['agent_id'] not in claim['reviewer_agent_ids']: claim['reviewer_agent_ids'].append(role['agent_id'])
    complete=len(results)==len(selected) and not cancelled and not artifact['truncated'] and all(r['status']=='local_check_completed' for r in results)
    if not complete: gaps.append({'code':'execution_incomplete','remaining_agents':[r['agent_id'] for r in selected[len(results):]],'reason':'cancelled' if cancelled else 'budget_or_timeout'})
    if artifact['truncated']: gaps.append({'code':'artifact_truncated','reason':'Apenas parte do artefato foi extraída; não alegar revisão integral.'})
    gaps.extend({'objection_id':o['objection_id'],'severity':o['severity'],'code':o['code']} for o in objections)
    critical=any(o['severity']=='critical' for o in objections)
    status='cancelled' if cancelled else ('blocked' if critical or not complete else ('needs_revision' if any(o['severity']=='major' for o in objections) else 'ready_for_human_review'))
    families=[]
    for family,(number,question,condition) in FAMILIES.items():
        responsible=specialist(number)['agent_id']
        specific=next((o for o in objections if o['responsible_agent']==responsible),None)
        families.append({'family':family,'question':specific['question'] if specific else question,'replica':'Que evidência verificável poderia confirmar ou enfraquecer essa resposta?','resolution_condition':specific['required_evidence'] if specific else condition,'responsible_agent':responsible,'target_claim_ids':[c['claim_id'] for c in p['claims']]})
    if legacy is None: legacy={'status':'not_executed','binding':False,'evaluation_scope':'legacy_keyword_heuristic','external_validation':False}
    gates=[]
    mapping={'G0':not not(p['problem'] and p['objectives'] and p['spec_id']),
       'G1':not any(o['code'] in {'claim_without_evidence','source_not_inspected','citation_not_verified'} for o in objections),
       'G2':not any(o['severity']=='critical' and o['responsible_agent'] in {specialist(n)['agent_id'] for n in ('A08','A11','A13','A24')} for o in objections),
       'G3':not any(o['code'] in {'human_ethics_pending','community_governance_pending','public_is_not_authorization'} for o in objections),
       'G4':not critical,'G5':not critical and not any(o['code'] in {'negative_evidence','generalization_not_supported','metric_category_error','metric_not_linguistic_reconstruction','territory_not_novelty','timeline_not_permission','affinity_not_empirical_scope'} for o in objections),'G6':False}
    for gate,passed in mapping.items():
        passed=bool(passed and complete)
        gates.append({'gate':gate,'passed':passed,'status':'pending_human_review' if gate=='G6' else ('inconclusive_execution' if not complete else ('local_contract_satisfied' if passed else 'pending')),'scope':'local_preflight_not_scientific_approval'})
    report=asdict(ResearchReview(p['research_id'],p['spec_id'],artifact['sha256'],p['claims'],objections,gaps,list(dict.fromkeys(o['required_evidence'] for o in objections)),manifest,status))
    report.update(context=p['context'],problem=p['problem'],objectives=p['objectives'],study_type=p['study_type'],artifact={k:v for k,v in artifact.items() if k!='text'},
       question_families=families,specialist_results=results,selected_agent_ids=[r['agent_id'] for r in selected],execution_complete=complete,
       execution_scope='local_rule_checks',profile_scope=profile_scope,llm_inference_executed=False,legacy_board=legacy,gates=gates,flow=flow,
       scientifically_approved=False,external_validation=False,limitations=['Verificações estruturais e regras locais, sem equivalência medida a banca humana.','Metadados de método e alegações foram fornecidos pelo responsável; não são observação independente.','Fontes externas não são recuperadas automaticamente nesta operação.','Somente alegações explicitamente submetidas foram avaliadas; não há extração semântica exaustiva.'])
    report['report_sha256']=hashlib.sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return report
