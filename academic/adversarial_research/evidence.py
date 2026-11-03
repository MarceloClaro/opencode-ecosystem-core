"""Integridade física e contratos de entrada; sem verificação semântica inventada."""
import copy,hashlib,json,re
from pathlib import Path
from dataclasses import asdict
from .contracts import ResearchClaim

STATUSES={'verified','reported','proposed','hypothetical','contradicted','insufficient','not_checked'}
TYPES={'factual','theoretical','methodological','inferential','normative','teórica','metodológica','inferencial','normativa'}

def text(value,label,maximum=12000):
    if not isinstance(value,str) or not value.strip() or len(value)>maximum or '\x00' in value: raise ValueError(label+' inválido')
    return value.strip()

def identifier(value,label):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}',value): raise ValueError(label+' inválido')
    return value

def read_artifact(value):
    path=Path(text(value,'artifact_path',3000)).expanduser().resolve(strict=True)
    if not path.is_file() or path.stat().st_size>16*1024*1024: raise ValueError('Artefato ausente ou acima de 16 MiB')
    raw=path.read_bytes(); suffix=path.suffix.lower(); pages=None
    if suffix=='.pdf':
        import fitz
        with fitz.open(path) as doc:
            pages=len(doc); result='\n'.join(doc[i].get_text() for i in range(min(pages,300)))
    elif suffix=='.docx':
        import zipfile
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist())>32*1024*1024: raise ValueError('DOCX descompactado excede o limite')
        from docx import Document
        doc=Document(path); result='\n'.join(p.text for p in doc.paragraphs)
        result+='\n'+'\n'.join(' | '.join(c.text for c in row.cells) for table in doc.tables for row in table.rows)
    elif suffix in {'.txt','.md','.tex','.json','.csv'}:
        result=raw.decode('utf-8-sig')
    else: raise ValueError('Formato de artefato não suportado')
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'text':result[:2000000],'truncated':len(result)>2000000 or (pages is not None and pages>300),'pages':pages,'bytes':len(raw)}

def intake(project):
    if not isinstance(project,dict): raise ValueError('Projeto deve ser objeto JSON')
    # Também recusa NaN/objetos arbitrários e limita o volume antes de copiar.
    encoded=json.dumps(project,allow_nan=False,ensure_ascii=False)
    if len(encoded)>4*1024*1024: raise ValueError('Intake excessivo')
    p=copy.deepcopy(project)
    for key in ('research_id','spec_id'): identifier(p.get(key),key)
    text(p.get('problem'),'problem')
    if not isinstance(p.get('objectives'),list) or not p['objectives'] or len(p['objectives'])>30: raise ValueError('Objetivos obrigatórios')
    for item in p['objectives']: text(item,'objective')
    if p.get('study_type') not in {'bibliographic','qualitative','quantitative','experimental','before_after','mixed','computational','protocol'}: raise ValueError('Desenho não suportado')
    artifact=read_artifact(p.get('artifact_path'))
    context=p.setdefault('context',{})
    if not isinstance(context,dict): raise ValueError('Contexto inválido')
    for key in ('humans','indigenous_knowledge','personal_data','control_group'):
        if key in context and context[key] is not None and type(context[key]) is not bool: raise ValueError(key+' precisa ser booleano ou null')
    manifests=[]; source_ids=set()
    sources=p.setdefault('sources',[])
    if not isinstance(sources,list) or len(sources)>300: raise ValueError('Fontes inválidas')
    for source in sources:
        if not isinstance(source,dict): raise ValueError('Fonte inválida')
        sid=identifier(source.get('source_id'),'source_id')
        if sid in source_ids: raise ValueError('Fonte duplicada')
        source_ids.add(sid)
        locator=source.get('locator'); valid_locator=isinstance(locator,str) and bool(locator.strip()) and len(locator)<=1000
        entry={'source_id':sid,'locator':locator,'integrity_checked':False,'verification_scope':'local_artifact_integrity_only','declared_verification':source.get('verification','not_checked')}
        if source.get('path'):
            try:
                item=read_artifact(source['path'])
                expected=source.get('sha256')
                entry.update(path=item['path'],sha256=item['sha256'],integrity_checked=bool(valid_locator and (expected is None or expected==item['sha256'])))
            except (OSError,ValueError,UnicodeError) as exc: entry['error']=type(exc).__name__
        elif source.get('url'): entry.update(url=text(source['url'],'URL',2000),reason='Fonte externa não recuperada nesta operação')
        manifests.append(entry)
    claims=p.get('claims')
    if not isinstance(claims,list) or not 1<=len(claims)<=200: raise ValueError('Forneça de 1 a 200 alegações explícitas; não há extração semântica automática exaustiva')
    claim_ids=set(); normalized=[]
    for claim in claims:
        if not isinstance(claim,dict): raise ValueError('Alegação inválida')
        cid=identifier(claim.get('claim_id'),'claim_id')
        if cid in claim_ids: raise ValueError('Alegação duplicada')
        claim_ids.add(cid)
        statement=text(claim.get('statement'),'statement')
        kind=claim.get('claim_type'); declared=claim.get('evidence_status')
        if kind not in TYPES or declared not in STATUSES: raise ValueError('Tipo/status de alegação inválido')
        for key in ('source_refs','limitations','reviewer_agent_ids'):
            if not isinstance(claim.get(key),list) or not all(isinstance(x,str) and len(x)<=3000 for x in claim[key]): raise ValueError(key+' inválido')
        if set(claim['source_refs'])-source_ids: raise ValueError('Referência a fonte inexistente')
        attrs=claim.get('attributes',{})
        if not isinstance(attrs,dict): raise ValueError('Atributos inválidos')
        status='reported' if declared=='verified' else declared
        limits=list(claim['limitations'])
        if declared=='verified': limits.append('Verificação semântica não foi reproduzida; integridade local não comprova a alegação.')
        normalized.append(asdict(ResearchClaim(cid,statement,kind,list(claim['source_refs']),status,limits,list(claim['reviewer_agent_ids']),attrs,declared)))
    p['claims']=normalized
    return p,artifact,manifests
