"""Contraprovas sobre alegações e metadados declarados; não são árbitro de verdade."""
from dataclasses import asdict
import hashlib
from .contracts import AdversarialObjection

def check_specialist(role,project,manifest):
    number=role['number']; context=project['context']; claims=project['claims']
    output=[]; all_ids=[x['claim_id'] for x in claims]
    source_map={x['source_id']:x for x in manifest}
    def add(code,question,rationale,evidence,severity='major',claim=None):
        targets=[claim['claim_id']] if claim else all_ids
        refs=list(claim['source_refs']) if claim else list(source_map)
        key='|'.join([project['research_id'],role['agent_id'],code,*targets])
        item=AdversarialObjection('obj-'+hashlib.sha256(key.encode()).hexdigest()[:20],targets,question,rationale,evidence,severity,
             'Detecção local sobre documentos/metadados fornecidos; confirmação semântica e parecer especializado permanecem necessários.',refs,role['agent_id'],code)
        output.append(asdict(item))
    def missing(key,label,evidence,severity='major'):
        if not context.get(key): add('missing_'+key,'Como sustentar '+label+'?', 'A documentação pertinente não foi identificada no intake.',evidence,severity)
    for claim in claims:
        a=claim['attributes']
        supported=bool(claim['source_refs']) and all(source_map.get(r,{}).get('integrity_checked') is True for r in claim['source_refs'])
        if number=='A03' and not supported and claim['evidence_status'] not in {'proposed','hypothetical'}:
            add('claim_without_evidence','Qual evidência recuperada sustenta esta alegação?','Uma alegação relatada não pode ser apresentada como comprovação sem suporte rastreável.','Fonte recuperada, localizador e relação explícita entre fonte e alegação.','critical',claim)
        if number=='A05' and a.get('claims_novelty') is True and not context.get('literature_source_refs'):
            add('novelty_without_literature','Qual lacuna subsiste diante da literatura recuperada?','A originalidade exige contraste com trabalhos pertinentes; ausência de recuperação não comprova ausência de estudos.','Busca documentada, fontes recuperadas, limites e comparação de contribuições.','critical',claim)
        if number=='A06' and a.get('novelty_basis')=='new_territory':
            add('territory_not_novelty','O que é novo além do território ou público?','Mudança de território, isoladamente, não estabelece inovação teórica, metodológica ou empírica.','Contraste bibliográfico e contribuição delimitada.','major',claim)
        if number=='A08' and a.get('epistemic_injustice_from_factual_error_alone') is True:
            add('category_error','Que elementos distinguem erro factual de injustiça epistêmica neste caso?','A ocorrência isolada de erro não estabelece por si só mecanismos de silenciamento, credibilidade ou exclusão.','Definição operacional, contexto e evidências dos mecanismos alegados.','critical',claim)
        if number=='A11' and a.get('independent_observations') is not None:
            declared=a['independent_observations']; units=context.get('independent_units'); observed=context.get('observed_responses')
            if units is None or observed is None or declared>units or declared>observed:
                add('independence_not_established','Quais são as unidades independentes e quais respostas são repetidas ou apenas planejadas?','Contar saídas previstas não demonstra coleta nem independência; dependências precisam ser explicitadas.','Contagens observadas, unidades, identificadores de agrupamento e plano analítico que respeite dependências.','critical',claim)
        if number=='A13' and a.get('causal_claim') is True and (context.get('control_group') is not True or not context.get('causal_identification')):
            add('causality_not_identified','Como a intervenção foi distinguida de confundidores, seleção, maturação e efeito de teste?','Mudança antes/depois ou associação não identifica automaticamente um efeito causal.','Identificação causal justificada ou revisão da conclusão para associação/mudança observada.','critical',claim)
        if number=='A17' and a.get('population_generalization') is True and not context.get('generalization_strategy'):
            add('generalization_not_supported','Qual estratégia sustenta a extrapolação além do corpus ou amostra?','Generalização estatística, analítica e transferibilidade exigem justificativas diferentes.','População-alvo, seleção, pressupostos e limites de extrapolação.','major',claim)
        if number=='A19' and a.get('public_source_implies_unrestricted_use') is True:
            add('public_is_not_authorization','Quem possui autoridade para autorizar e interpretar este conhecimento?','Publicidade de uma fonte não elimina, por si só, governança e responsabilidades contextuais.','Protocolos pertinentes, autoridade comunitária e avaliação humana contextual.','critical',claim)
        if number=='A23' and claim['declared_evidence_status']=='verified':
            add('citation_not_verified','Qual verificação semântica independente foi efetivamente realizada?','A leitura e o hash de um arquivo comprovam somente integridade no escopo local, sem autenticar automaticamente o conteúdo.','Registro de inspeção pertinente, localizador e limites da verificação.','major',claim)
        if number=='A24' and a.get('metric')=='cosine_similarity' and a.get('interpretation')=='translation_accuracy':
            add('metric_category_error','Por que similaridade de vetores está sendo interpretada como precisão de tradução?','Uma similaridade de 0,90 não equivale a 90% de traduções corretas.','Definição da métrica, referência de avaliação e avaliação linguística apropriada.','critical',claim)
        if number=='A24' and a.get('linguistic_reconstruction_from_metric') is True:
            add('metric_not_linguistic_reconstruction','Que evidência linguística sustenta a reconstrução alegada?','Métricas computacionais isoladas não estabelecem reconstrução linguística.','Corpus pertinente, método linguístico, fontes e revisão especializada.','critical',claim)
        if number=='A26' and claim['evidence_status']=='contradicted':
            add('negative_evidence','Como a conclusão incorpora a evidência contraditória?','Evidências desfavoráveis não devem ser ocultadas nem convertidas em apoio.','Revisão proporcional da alegação, hipóteses rivais e registro das contradições.','major',claim)
        if number=='A28' and a.get('timeline_implies_professional_release') is True:
            add('timeline_not_permission','Que documento comprova a disponibilidade profissional declarada?','Cronograma planejado não comprova liberação, acesso ou recursos.','Comprovação de disponibilidade ou reformulação do plano e contingências.','major',claim)
        if number=='A30' and a.get('conceptual_affinity_implies_empirical_international') is True:
            add('affinity_not_empirical_scope','Qual atividade ou evidência sustenta o escopo internacional empírico declarado?','Afinidade conceitual não equivale à execução de pesquisa internacional empírica.','Mapeamento explícito entre objetivos, atividades, evidências e critérios documentados.','major',claim)
    if number=='A02' and not project.get('hypotheses'): add('rival_question','Quais perguntas ou interpretações alternativas delimitam o estudo?','Nem todo desenho exige hipótese estatística, mas perguntas e pressupostos precisam ser explícitos.','Perguntas verificáveis e pressupostos proporcionais ao desenho.','advisory')
    if number=='A07': missing('concept_source_refs','a genealogia e os limites dos conceitos','Fontes conceituais pertinentes e distinções operacionais.','advisory')
    if number=='A09': missing('rival_hypotheses','a análise de interpretações rivais','Hipóteses ou interpretações alternativas e condições que as distinguiriam.','advisory')
    if number=='A10' and project['study_type']!='bibliographic': missing('sampling_frame','os critérios de seleção','Quadro de seleção, unidades e suficiência apropriada ao desenho; explicitar vieses.')
    if number=='A12':
        missing('model_versions','as versões e configurações dos modelos','Versões, parâmetros, repetições, sementes pertinentes e recibos de execução.')
    if number=='A14': missing('instruments','a adequação dos instrumentos','Instrumentos, rubricas e procedimentos de pilotagem pertinentes ao desenho.')
    if number=='A15': missing('triangulation_plan','a relação entre fontes e métodos','Convergências, divergências e justificativa da estratégia escolhida.','advisory')
    if number=='A16': missing('independent_review','a revisão independente quando pertinente','Procedimentos, desacordos e limites da classificação.','advisory')
    if number=='A18' and context.get('humans') is not False:
        if not context.get('ethics_source_refs'): add('human_ethics_pending','Que avaliação ética, consentimento ou justificativa de inaplicabilidade está documentada?','O contexto de participação humana e suas exigências não foi esclarecido por documento rastreável.','Contexto, documentos pertinentes e avaliação institucional/humana aplicável.','critical' if context.get('humans') is True else 'major')
    if number=='A19' and context.get('indigenous_knowledge') is True and not context.get('community_authorization'):
        add('community_governance_pending','Como a autoridade comunitária e os protocolos próprios foram respeitados?','O sistema não pode autorizar uso de conhecimento coletivo ou culturalmente sensível.','Documentação contextual, participação comunitária pertinente e revisão humana especializada.','critical')
    if number=='A20' and context.get('personal_data') is True: missing('data_governance','a proteção de dados pessoais','Minimização, finalidade, acesso, retenção e avaliação competente aplicável.')
    if number=='A21': missing('interpretive_authority','a autoridade interpretativa e a prevenção de extração epistêmica','Participação e governança pertinentes, incluindo divergências e limites da representação.','advisory')
    if number=='A22' and any(not x['integrity_checked'] for x in manifest): add('source_not_inspected','Que fontes ainda precisam ser recuperadas ou localizadas?','Fontes não recuperadas ou sem localizador permanecem não verificadas.','Arquivos/fontes recuperados, identificadores, localizadores e proveniência.')
    if number=='A25' and project['study_type'] in {'computational','experimental','quantitative','mixed'}: missing('reproducibility','a reprodução dos resultados','Dados pertinentes, protocolo, versões, parâmetros e recibos, preservando restrições de acesso.')
    if number=='A27': missing('timeline','as precedências e os prazos','Cronograma consistente, dependências e entregas verificáveis.','advisory')
    if number=='A28': missing('resources','a disponibilidade de recursos','Acesso, infraestrutura, custos e disponibilidade documentada.','advisory')
    if number=='A29': missing('contingencies','as contingências','Cenários de atraso, indisponibilidade e revisão metodológica.','advisory')
    if number=='A30': missing('institutional_source_refs','a aderência institucional','Edital, linha ou rubrica com documento/localizador e mapeamento explícito do projeto.')
    if number=='A31': missing('disciplinary_integration','a integração entre disciplinas','Relações metodológicas/conceituais concretas; lista de referências não basta.')
    return output
