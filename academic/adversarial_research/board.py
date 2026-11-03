"""Motor de revisão local: objeções rastreáveis, sem certificar qualidade científica."""
from dataclasses import asdict
import hashlib,json,math,time
from .contracts import ResearchReview
from .evidence import intake
from .guards import check_specialist
from .registry import SPECIALISTS,FAMILIES,specialist
from .router import route
from .banca import BancaSessionStore

def review_research(project,*,max_steps=34,timeout_seconds=30,cancelled=False,on_start=None,on_result=None):
    if type(max_steps) is not int or not 1<=max_steps<=34: raise ValueError('Orçamento de 1 a 34 especialistas')
    if isinstance(timeout_seconds,bool) or not isinstance(timeout_seconds,(int,float)) or not math.isfinite(timeout_seconds) or not 0<timeout_seconds<=120: raise ValueError('Prazo inválido')
    if type(cancelled) is not bool: raise ValueError('Cancelamento inválido')
    started=time.monotonic(); p,artifact,manifest=intake(project)
    selected=route(p); objections=[]; results=[]; gaps=[]
    for role in selected:
        if cancelled or len(results)>=max_steps or time.monotonic()-started>=timeout_seconds: break
        ticket=on_start(role,p,artifact) if on_start else None
        found=check_specialist(role,p,manifest)
        result={'agent_id':role['agent_id'],'number':role['number'],'status':'local_check_completed','evaluation_scope':'local_rule_checks','artifact_sha256':artifact['sha256'],'target_claim_ids':[c['claim_id'] for c in p['claims']],'objections':found,'llm_inference_executed':False}
        if on_result: result['orchestration']=on_result(ticket,role,result)
        results.append(result);objections.extend(found)
        for claim in p['claims']:
            if role['agent_id'] not in claim['reviewer_agent_ids']: claim['reviewer_agent_ids'].append(role['agent_id'])
    complete=len(results)==len(selected) and not cancelled
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
    from academic.rigorous_board import RigorousBoard
    legacy=RigorousBoard().review(artifact['text'],venue='auto').to_dict()
    legacy.update(binding=False,evaluation_scope='legacy_keyword_heuristic',external_validation=False)
    gates=[]
    mapping={'G0':not not(p['problem'] and p['objectives'] and p['spec_id']),
       'G1':not any(o['code'] in {'claim_without_evidence','source_not_inspected','citation_not_verified'} for o in objections),
       'G2':not any(o['severity']=='critical' and o['responsible_agent'] in {specialist(n)['agent_id'] for n in ('A08','A11','A13','A24')} for o in objections),
       'G3':not any(o['code'] in {'human_ethics_pending','community_governance_pending','public_is_not_authorization'} for o in objections),
       'G4':not critical,'G5':not critical,'G6':False}
    for gate,passed in mapping.items(): gates.append({'gate':gate,'passed':passed,'status':'pending_human_review' if gate=='G6' else ('local_contract_satisfied' if passed else 'pending'),'scope':'local_preflight_not_scientific_approval'})
    report=asdict(ResearchReview(p['research_id'],p['spec_id'],artifact['sha256'],p['claims'],objections,gaps,list(dict.fromkeys(o['required_evidence'] for o in objections)),manifest,status))
    report.update(context=p['context'],problem=p['problem'],objectives=p['objectives'],study_type=p['study_type'],artifact={k:v for k,v in artifact.items() if k!='text'},
       question_families=families,specialist_results=results,selected_agent_ids=[r['agent_id'] for r in selected],execution_complete=complete,
       execution_scope='local_rule_checks',llm_inference_executed=False,legacy_board=legacy,gates=gates,
       scientifically_approved=False,external_validation=False,limitations=['Verificações estruturais e regras locais, sem equivalência medida a banca humana.','Metadados de método e alegações foram fornecidos pelo responsável; não são observação independente.','Fontes externas não são recuperadas automaticamente nesta operação.','Somente alegações explicitamente submetidas foram avaliadas; não há extração semântica exaustiva.'])
    report['report_sha256']=hashlib.sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return report
