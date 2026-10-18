"""Notas declaradas de treinamento, vinculadas a evidências observadas."""
import math
from .evidence import text,read_artifact

def observed_rating(state,criterion_id,score,answer_turn_ids,justification,reviewer_id):
    rubric=state.get('rubric')
    if not rubric: raise ValueError('Rubrica documentada obrigatória para pontuar')
    if read_artifact(rubric['source_path'])['sha256']!=rubric['source_sha256']: raise ValueError('Rubrica alterada')
    criterion=next((c for c in rubric['criteria'] if c['criterion_id']==criterion_id),None)
    if not criterion: raise ValueError('Critério fora da rubrica')
    if type(score) not in (int,float) or not math.isfinite(score) or not 0<=score<=criterion['maximum']: raise ValueError('Nota fora dos limites')
    observed={a['turn_id'] for a in state['answers']}
    if not isinstance(answer_turn_ids,list) or not answer_turn_ids or not all(isinstance(t,str) and t in observed for t in answer_turn_ids): raise ValueError('Toda nota deve citar respostas observadas')
    return {'dimension':criterion_id,'score':score,'maximum':criterion['maximum'],'status':'reviewer_reported_simulated',
        'answer_turn_ids':list(dict.fromkeys(answer_turn_ids)),'justification':text(justification,'justificativa',12000),
        'reviewer_id':text(reviewer_id,'avaliador declarado',200),'reviewer_authenticated':False,'institutional_validity':False}
