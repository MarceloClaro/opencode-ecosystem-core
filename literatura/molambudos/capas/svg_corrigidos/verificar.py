"""Verificação estrutural, geométrica e de preservação dos artefatos entregues."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.pens.boundsPen import BoundsPen
import produzir as p

HERE=Path(__file__).resolve().parent
SVG='{http://www.w3.org/2000/svg}'

def transform(value):
    result=np.eye(3)
    for name,values in re.findall(r'([a-zA-Z]+)\(([^)]*)\)',value or ''):
        v=[float(x) for x in re.split(r'[\s,]+',values.strip())]
        m=np.eye(3)
        if name=='translate': m[:2,2]=[v[0],v[1] if len(v)>1 else 0]
        elif name=='scale': m[0,0]=v[0];m[1,1]=v[1] if len(v)>1 else v[0]
        elif name=='rotate':
            assert len(v)==1
            a=np.deg2rad(v[0]);m[:2,:2]=[[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]
        elif name=='matrix': m=np.array([[v[0],v[2],v[4]],[v[1],v[3],v[5]],[0,0,1]])
        else: raise AssertionError('Transformação não tratada: '+name)
        result=result@m
    return result

def text_bounds(root):
    w,h=map(float,[root.get('width'),root.get('height')])
    out=[]
    def walk(node,mat):
        mat=mat@transform(node.get('transform'))
        if node.tag==SVG+'text':
            s=node.text or '';face=node.get('data-face');f=p.FONTS[face]
            cmap,metrics,upm=p.METRICS[face];size=float(node.get('font-size'))
            advance=p.width(s,size,face)
            x=float(node.get('x'));y=float(node.get('y'))
            anchor=node.get('text-anchor')
            x-=advance/2 if anchor=='middle' else advance if anchor=='end' else 0
            bounds=[];cursor=0
            for c in s:
                glyph=cmap[ord(c)];pen=BoundsPen(f.getGlyphSet());f.getGlyphSet()[glyph].draw(pen)
                if pen.bounds:
                    x0,y0,x1,y1=pen.bounds
                    for xx,yy in [(x0,y0),(x0,y1),(x1,y0),(x1,y1)]:
                        bounds.append(mat@np.array([x+(cursor+xx)*size/upm,y-yy*size/upm,1]))
                cursor+=metrics[glyph][0]
            a=np.array(bounds);mins=a.min(axis=0);maxs=a.max(axis=0)
            assert mins[0]>=0 and mins[1]>=0 and maxs[0]<=w and maxs[1]<=h,(s,mins,maxs)
            out.append({'texto':s,'bbox':[round(float(x),3) for x in [mins[0],mins[1],maxs[0],maxs[1]]]})
        for child in node:walk(child,mat)
    walk(root,np.eye(3))
    return out

def main():
    manifest=json.loads((HERE/'manifesto.json').read_text())
    for name,sha in manifest['originais'].items():
        assert hashlib.sha256((HERE.parent/(name+'.png')).read_bytes()).hexdigest()==sha
    for block in manifest['blocos']: assert block['bottom']<=block['limit'],block
    reports=[]
    for name in ['CAPA','CONTRACAPA','LOMBADA']:
        for edit in [False,True]:
            file=HERE/(name+('_EDITAVEL' if edit else '')+'.svg')
            raw=file.read_text();root=ET.fromstring(raw)
            ids=[e.get('id') for e in root.iter() if e.get('id')]
            assert len(ids)==len(set(ids)),'ID duplicado em '+file.name
            identifiers=set(ids)
            for node in root.iter():
                tag=node.tag.split('}')[-1]
                assert tag not in {'image','foreignObject','script','filter'},(file.name,tag)
                for attr,value in node.attrib.items():
                    if attr.split('}')[-1]=='href': assert value.startswith('#') and value[1:] in identifiers
                    for ref in re.findall(r'url\(#([^)]+)\)',value): assert ref in identifiers
            for u in re.findall(r'url\(([^)]+)\)',raw):
                assert u.startswith('#') or u.startswith('data:font/woff2;base64,'),u[:80]
            texts=list(root.iter(SVG+'text'))
            if edit:
                assert texts and 'data:font/woff2;base64,' in raw
                bounds=text_bounds(root)
            else: assert not texts
            reports.append({'arquivo':file.name,'curvas':len(list(root.iter(SVG+'path'))),
                            'textos_editaveis':len(texts),'imagens':0,
                            'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                            'bytes':file.stat().st_size})
        a=np.array(Image.open(HERE/(name+'_PREVIA.png')).convert('RGB'),dtype=float)
        b=np.array(Image.open(HERE/'.tracado'/(name+'_EDITAVEL.png')).convert('RGB'),dtype=float)
        mae=float(np.abs(a-b).mean())
        assert mae<5,(name,mae)
        reports[-1]['diferenca_media_render_0_255']=round(mae,4)
        (HERE/(name+'_LIMITES_TEXTO.json')).write_text(json.dumps(bounds,ensure_ascii=False,indent=2),encoding='utf-8')
    result={'status':'PASS_LOCAL','arquivos_svg':6,'originais_preservados':True,
            'caracteres_cobertos':True,'textos_dentro_da_prancheta':True,
            'referencias_internas_integras':True,'validacao_externa':False,'resultados':reports,
            'limites':'Inspeção estrutural, geométrica e visual local. Sem prova física de impressão. A renderização de texto editável pode variar entre aplicativos; as versões em curvas fixam a aparência.'}
    (HERE/'validacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    # Compact visual review of all three rendered vector pieces.
    height=1100;gap=25;top=65
    panels=[]
    for name in ['CAPA','LOMBADA','CONTRACAPA']:
        im=Image.open(HERE/(name+'_PREVIA.png')).convert('RGB')
        panels.append((name,im.resize((round(im.width*height/im.height),height),Image.Resampling.LANCZOS)))
    sheet=Image.new('RGB',(sum(im.width for _,im in panels)+gap*4,height+top+gap),'#191b13')
    draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    x=gap
    for name,im in panels:
        draw.text((x,24),name,font=font,fill='#ead260');sheet.paste(im,(x,top));x+=im.width+gap
    sheet.save(HERE/'PREVIA_CONJUNTO.png')
    print(json.dumps({k:v for k,v in result.items() if k!='resultados'},ensure_ascii=False,indent=2))
    print([(r['arquivo'],r['bytes'],r.get('diferenca_media_render_0_255')) for r in reports])

if __name__=='__main__':main()
