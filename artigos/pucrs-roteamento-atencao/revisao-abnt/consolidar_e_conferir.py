from pathlib import Path
import hashlib
import json
import re
import fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
review=ROOT/'revisao-abnt'
manifest={}

def expand(path):
    text=path.read_text(encoding='utf-8')
    manifest[str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    def input_file(m):
        p=Path(m[1])
        if not p.is_absolute(): p=ROOT/p
        if not p.suffix: p=p.with_suffix('.tex')
        return '\n% Início da fonte: '+p.name+'\n'+expand(p)+'\n% Fim da fonte: '+p.name+'\n'
    text=re.sub(r'\\input\{([^}]+)\}',input_file,text)
    def listing(m):
        p=Path(m[1])
        raw=p.read_text(encoding='utf-8')
        if '\\end{lstlisting}' in raw:
            raise ValueError('Marcador conflitante no arquivo '+str(p))
        manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        return '\n% Artefato incorporado: '+p.name+'\n\\begin{lstlisting}\n'+raw.rstrip()+'\n\\end{lstlisting}\n'
    return re.sub(r'\\lstinputlisting\{([^}]+)\}',listing,text)

source=expand(ROOT/'dissertacao.tex')
(ROOT/'dissertacao-abnt.tex').write_text(source,encoding='utf-8')
(review/'manifesto_fontes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
active=re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}','',source,flags=re.S)
cited=set()
for c in re.findall(r'\\cite(?:p|t)?(?:\[[^]]*\])?\{([^}]+)\}',active):
    cited.update(c.split(','))
refs=set(re.findall(r'\\bibitem(?:\[[^]]*\])?\{([^}]+)\}',active))
assert not cited-refs, cited-refs
assert not refs-cited, refs-cited
table_calls={k:active.count('\\ref{'+k+'}') for k in re.findall(r'\\label\{(tab:[^}]+)\}',active)}
print('Chamadas de tabelas:',table_calls)

pdf=review/'compilacao'/'dissertacao.pdf'
if pdf.exists():
    doc=fitz.open(pdf)
    texts=[p.get_text() for p in doc]
    problems=[]
    for i,p in enumerate(doc):
        if not (abs(p.rect.width-595.28)<1 and abs(p.rect.height-841.89)<1):
            problems.append({'page':i+1,'issue':'dimensão diferente de A4'})
        for word in p.get_text('words'):
            if word[0]<83 or word[2]>541 or word[3]>789:
                problems.append({'page':i+1,'issue':'texto fora da área esperada','word':word[4],'bbox':list(word[:4])})
    full='\n'.join(texts)
    selected=[0,1,4,5]
    for term in ('1 INTRODUÇÃO','2 PRELIMINARES','5 PROVAS','6 AVALIAÇÃO','REFERÊNCIAS','GLOSSÁRIO','APÊNDICE A','APÊNDICE E','APÊNDICE F'):
        matches=[i for i,t in enumerate(texts) if term in t]
        if matches: selected.append(matches[-1] if term in ('REFERÊNCIAS','GLOSSÁRIO') else matches[0])
    selected=sorted(set(selected))
    selected.extend(row[2]-1 for row in doc.get_toc() if row[0]==1 and any(term in row[1].lower() for term in ('código lean','resultados em json','histórico de auditoria','transcrição da suíte')))
    selected.extend(i for i,t in enumerate(texts) if ('Código Lean integral' in t or 'Resultados em JSON' in t or 'Histórico de auditoria' in t) and i>15)
    selected=sorted(set(selected))
    visual=review/'visual';visual.mkdir(exist_ok=True)
    for i in selected:
        doc[i].get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(visual/f'pagina-{i+1:03}.png')
    for batch in range(0,len(selected),9):
        group=selected[batch:batch+9]
        sheet=Image.new('RGB',(1500,2160),'#d9d9d9');drawing=ImageDraw.Draw(sheet)
        for pos,i in enumerate(group):
            im=Image.open(visual/f'pagina-{i+1:03}.png');im.thumbnail((485,685))
            x=(pos%3)*500+(500-im.width)//2;y=(pos//3)*720+25
            sheet.paste(im,(x,y));drawing.text((x,y-18),f'Página física {i+1}',fill='black')
        sheet.save(visual/f'contato-{batch//9+1}.png')
    qa={'pages':len(doc),'bibliography_entries':len(refs),'citations_without_reference':sorted(cited-refs),'references_without_citation':sorted(refs-cited),'table_call_counts':table_calls,'boundary_findings':problems,'selected_visual_pages':[i+1 for i in selected],'unresolved_markers_count':full.count('??'),'title':doc.metadata.get('title')}
    (review/'conferencia_pdf.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in qa.items() if k!='boundary_findings'},ensure_ascii=False))
    print('Achados de limite de página:',len(problems))
print('Fonte consolidada:',len(source.encode('utf-8')),'bytes; artefatos:',len(manifest))
