"""Instalação de perfis pelo primário; nunca publica cartões manualmente."""
from .registry import SPECIALISTS,PILOT_NUMBERS

def install_profiles(primary,*,phase='pilot'):
    if phase not in {'pilot','full'}: raise ValueError('Fase inválida')
    rows=[]
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    for role in SPECIALISTS:
        if phase=='pilot' and role['number'] not in PILOT_NUMBERS: continue
        document={
            'agent_id':role['agent_id'],'name':role['number']+' — '+role['agent_id'],
            'description':role['responsibility'],'capabilities':['academic_rigor','evidence_integrity','adversarial_research'],
            'spec_file':'specs/SPEC-935-R914-rigor-academico-adversarial.md',
            'test_file':'tests/test_r914_academic_rigor.py','allow_edit':False,
            'source':'SPEC-OCRE-ACADEMIC-RIGOR-v1-user; R914; functional_scope_requires_execution',
            'prompt':f"""Responsabilidade: {role['responsibility']}

Entrada: projeto, artefato com hash, alegações ResearchClaim, fontes/localizadores,
metadados declarados e contexto autorizado, recebidos exclusivamente pelo MarceloClaro.
Saída: status, findings (AdversarialObjection com target_claim_ids), evidence e limitations.
Exija: {role['required_evidence']}
Limite de competência: {role['limitations']}
Caso de teste correspondente: {role['test_case']}

Protocolo: identifique a alegação; inspecione a fonte disponível sem inventá-la;
formule pergunta/objeção pertinente e condição de resolução; considere interpretações
rivais; classifique severidade/incerteza; proponha correção proporcional ao desenho.
Não invente objeção quando não houver sinal; declare not_checked e solicite contexto.
Uma ausência de alerta em regra local não comprova que a pesquisa foi validada.
O handler local desta R914 usa regras sobre alegações explícitas, sem inferência LLM.
Para revisão semântica pelo agente, MarceloClaro deve atribuir executor elegível e
anexar recibo real; perfil registrado não comprova essa execução.
A04 coordena somente o parecer científico sob o primário, nunca outros runtimes.
Preserve hipóteses, resultados nulos e contradições. Não promova confiança pela própria
avaliação. Não ateste originalidade sem literatura recuperada, causalidade sem
identificação, ética sem contexto ou qualidade institucional por métrica interna.
SDD/TDD: leia a spec, execute o caso correspondente quando autorizado, preserve RED
histórico, GREEN e regressão; entregue evidência, sem inventar execução passada.
"""}
        exists=(root/'agents/catalog'/(role['agent_id']+'.md')).exists()
        result=primary.agent_profile_action({'operation':'register','agent_id':role['agent_id']} if exists else {'operation':'create','profile':document})
        if result.get('definition_validated') is not True or result.get('registered') is not True: raise RuntimeError('Perfil não validado/registrado: '+role['agent_id'])
        rows.append({'agent_id':role['agent_id'],'definition_validated':True,'registered':True,'source_sha256':result['source_sha256'],'inference_executed':False})
    return {'phase':phase,'profiles':rows,'count':len(rows),'scientific_validation':False}
