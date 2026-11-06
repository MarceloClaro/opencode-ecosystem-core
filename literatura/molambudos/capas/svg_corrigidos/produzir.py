"""Entrega editorial SVG: gravuras traçadas e texto recomposto, sem bitmaps no SVG."""
from pathlib import Path
import copy
import base64
import io
import hashlib
import json
import math
import re
import random
import subprocess
import xml.etree.ElementTree as ET
from html import escape
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools import subset

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
CACHE = HERE / '.tracado'
CACHE.mkdir(exist_ok=True)
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
GOLD = '#ead260'
INK = '#090b08'
FONTFILES = {
    'regular': '/home/marceloclaro/.local/share/fonts/ebgaramond/EBGaramond-Regular.otf',
    'italic': '/home/marceloclaro/.local/share/fonts/ebgaramond/EBGaramond-Italic.otf',
    'bold': '/usr/share/fonts/opentype/freefont/FreeSerifBold.otf',
    'zh': '/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf',
    'sans': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
}
FAMILIES = {'regular':'EB Garamond','italic':'EB Garamond','bold':'FreeSerif',
            'zh':'AR PL SungtiL GB','sans':'DejaVu Sans'}
FONTS = {k:TTFont(v) for k,v in FONTFILES.items()}
METRICS = {k:(f.getBestCmap(),f['hmtx'].metrics,f['head'].unitsPerEm) for k,f in FONTS.items()}
TEXTS = []
BOUNDS = []

def el(tag, **attrs):
    return ET.Element(f'{{{NS}}}{tag}', {k.replace('_','-'):str(v) for k,v in attrs.items()})

def width(text,size,face='regular'):
    cmap,met,upm = METRICS[face]
    missing = sorted({c for c in text if ord(c) not in cmap})
    if missing:
        raise ValueError(f'Glifos ausentes em {face}: {missing}')
    return sum(met[cmap[ord(c)]][0] for c in text)/upm*size

def text(parent,content,x,y,size,face='regular',anchor='start',fill=GOLD,maxwidth=None):
    if maxwidth and width(content,size,face)>maxwidth:
        size *= maxwidth/width(content,size,face)
    attrs=dict(x=x,y=y,fill=fill,font_family=FAMILIES[face],font_size=f'{size:.4f}',
               text_anchor=anchor,font_kerning='none',font_variant_ligatures='none')
    if face=='italic': attrs['font_style']='italic'
    if face=='bold': attrs['font_weight']='bold'
    e=el('text',**attrs)
    e.set('data-face',face)
    e.text=content
    parent.append(e)
    TEXTS.append(content)
    return e

def wrap(content,size,maxwidth,face):
    # CJK breaks by character, Latin by word; punctuation stays with its sentence.
    units=list(content) if face=='zh' else content.split()
    lines=[]
    current=''
    sep='' if face=='zh' else ' '
    for unit in units:
        candidate=current+sep+unit if current else unit
        if width(candidate,size,face)>maxwidth and current:
            if face=='zh' and unit in '，。；：！？、）》':
                current += unit
                lines.append(current)
                current=''
            else:
                lines.append(current)
                current=unit
        else: current=candidate
    if current: lines.append(current)
    return lines

def paragraph(parent,content,x,y,w,size=10.5,leading=11.7,face='regular',gap=3):
    for para in content.split('\n'):
        for line in wrap(para,size,w,face):
            text(parent,line,x,y,size,face)
            y+=leading
        y+=gap
    return y-gap

def rect(parent,x,y,w,h,fill=INK,stroke=None,sw=1,rx=0):
    attrs=dict(x=x,y=y,width=w,height=h,fill=fill)
    if stroke: attrs.update(stroke=stroke,stroke_width=sw)
    if rx: attrs['rx']=rx
    parent.append(el('rect',**attrs))

def line(parent,x1,y1,x2,y2,stroke=GOLD,sw=.6):
    parent.append(el('path',d=f'M{x1},{y1}H{x2}' if y1==y2 else f'M{x1},{y1}L{x2},{y2}',
                     fill='none',stroke=stroke,stroke_width=sw))

def softpanel(parent,x,y,w,h,pad=9,grain=False):
    """A vector fade joins replacement lettering to the distressed dark surface."""
    defs=parent.find(f'{{{NS}}}defs')
    # Nested groups use local definitions; all paint servers remain internal.
    if defs is None:
        defs=el('defs');parent.insert(0,defs)
    prefix='fundo-'+str(len(list(parent)))
    directions=[('e',0,0,1,0,0,1),('d',0,0,1,0,1,0),
                ('s',0,0,0,1,0,1),('i',0,0,0,1,1,0)]
    for side,x1,y1,x2,y2,a,b in directions:
        grad=el('linearGradient',id=prefix+side,x1=x1,y1=y1,x2=x2,y2=y2)
        grad.append(el('stop',offset='0',stop_color=INK,stop_opacity=a))
        grad.append(el('stop',offset='1',stop_color=INK,stop_opacity=b))
        defs.append(grad)
    rect(parent,x,y,w,h)
    for side,box in [('e',(x-pad,y,pad,h)),('d',(x+w,y,pad,h)),
                     ('s',(x,y-pad,w,pad)),('i',(x,y+h,w,pad))]:
        rect(parent,*box,'url(#'+prefix+side+')')
    if grain:
        rng=random.Random(1260)
        g=group(parent)
        g.set('opacity','.12')
        for _ in range(int(w*h/38)):
            px=x+rng.random()*w;py=y+rng.random()*h
            g.append(el('path',d=f'M{px:.2f},{py:.2f}l{rng.uniform(.2,1.7):.2f},{rng.uniform(-.5,.5):.2f}',
                        stroke='#b89c31',stroke_width=f'{rng.uniform(.15,.5):.2f}',fill='none'))

def trace(name):
    source=SRC/f'{name}.png'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    target=CACHE/f'{name}-{digest[:12]}-potrace-v3.svg'
    if not target.exists():
        im=Image.open(source).convert('RGB')
        # Palette restrained to the supplied black/gold engraving. Preserve small marks.
        rgb=np.asarray(im,dtype=np.float32)
        levels=np.array([0,13,27,45,68,96,130,168,205,238],dtype=float)
        bins=np.abs(rgb[:,:,0,None]-levels).argmin(axis=2)
        bins[(rgb[:,:,2]>rgb[:,:,0]*.65)&(rgb[:,:,0]>170)]=0
        palette=np.array([[7,9,6],[15,17,9],[27,29,11],[45,45,12],[68,65,14],
                          [96,89,19],[130,120,27],[168,153,40],[205,185,58],[238,216,91]],dtype=np.uint8)
        traced=el('svg',width=im.width,height=im.height,viewBox=f'0 0 {im.width} {im.height}')
        rect(traced,0,0,im.width,im.height,'#070906')
        # Successive tonal silhouettes keep dark holes and smooth engraving contours.
        for i in range(1,len(palette)):
            temp=CACHE/f'{name}-tom-{i}.pbm'
            Image.fromarray(np.where(bins>=i,0,255).astype(np.uint8)).convert('1').save(temp)
            layer=CACHE/f'{name}-tom-{i}.svg'
            subprocess.run(['/tmp/molambudos-potrace/usr/bin/potrace',str(temp),'-s','-o',str(layer),
                            '--turdsize','0','--alphamax','0.45','--opttolerance','0.08','--unit','100'],check=True)
            lr=ET.parse(layer).getroot()
            color='#'+''.join(f'{int(v):02x}' for v in palette[i])
            for child in lr:
                if child.tag==f'{{{NS}}}g':
                    child.set('fill',color)
                    traced.append(child)
        write(traced,target)
        print(f'Traçado {name}: {target.stat().st_size} bytes',flush=True)
    root=ET.parse(target).getroot()
    return list(root)

def group(parent,ident=None,transform=None,clip=None):
    attrs={}
    if ident: attrs['id']=ident
    if transform: attrs['transform']=transform
    if clip: attrs['clip-path']=f'url(#{clip})'
    g=el('g',**attrs); parent.append(g); return g

def art(parent,name,clip=None,transform=None):
    defs=parent.find(f'{{{NS}}}defs')
    sid='fonte-'+name.lower()
    if not any(e.get('id')==sid for e in defs):
        source=el('g',id=sid)
        source.extend(copy.deepcopy(trace(name)))
        defs.append(source)
    g=group(parent,transform=transform,clip=clip)
    use=el('use',href='#'+sid)
    use.set('{http://www.w3.org/1999/xlink}href','#'+sid)
    g.append(use)
    return g

def cliprect(defs,ident,x,y,w,h):
    c=el('clipPath',id=ident); c.append(el('rect',x=x,y=y,width=w,height=h)); defs.append(c)

def new(w,h,label):
    root=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}',version='1.1',role='img')
    title=el('title'); title.text=label; root.append(title)
    desc=el('desc'); desc.text='Gravuras vetorizadas do original fornecido; textos corrigidos em português, inglês e chinês simplificado. Proporções originais; sem escala física de impressão definida.';root.append(desc)
    defs=el('defs');root.append(defs)
    return root,defs

def ornament(parent,cx,y,w=45):
    line(parent,cx-w,y,cx-8,y,sw=.6);line(parent,cx+8,y,cx+w,y,sw=.6)
    parent.append(el('path',d=f'M{cx},{y-3}l3,3 -3,3 -3,-3Z',fill=GOLD))

def border(parent,w,h):
    rect(parent,9,9,w-18,h-18,'none','#b89c31',.8)
    rect(parent,13,13,w-26,h-26,'none','#b89c31',.35)
    for x,y,sx,sy in [(18,18,1,1),(w-18,18,-1,1),(18,h-18,1,-1),(w-18,h-18,-1,-1)]:
        g=group(parent,transform=f'translate({x} {y}) scale({sx} {sy})')
        g.append(el('path',d='M0 31V0H31 M4 22V4H22 M2 13C20 11 12 1 6 7S17 22 18 5 M9 1Q1 9 9 17',fill='none',stroke=GOLD,stroke_width='.7'))

def cover():
    root,defs=new(500,749,'Molambudos — capa corrigida')
    cliprect(defs,'area-arte',4,3,492,742)
    art(root,'CAPA','area-arte')
    # Recompose subtitles, tagline and credits in their original dark reserves.
    softpanel(root,126,115,253,75,7,True)
    g=group(root,'subtitulos')
    text(g,'O Diário do Paciente 1.260',252,136,21,anchor='middle',maxwidth=247)
    text(g,'The Diary of Patient 1,260',252,159,20.5,anchor='middle',maxwidth=250)
    text(g,'1260号病人的日记',252,184,18,'zh','middle',maxwidth=228)
    softpanel(root,151,196,198,44,5,True)
    g=group(root,'epigrafe')
    text(g,'Ela não é um monstro. Ela é uma consequência.',250,207,10.8,'italic','middle',maxwidth=195)
    text(g,'She is not a monster. She is a consequence.',250,221,10.8,'italic','middle',maxwidth=193)
    text(g,'她不是怪物。她是这一切的后果。',250,236,9.5,'zh','middle',maxwidth=193)
    # In-world lettering: signs, notebook and photograph retain their perspective.
    g=group(root,'placa-currais',transform='translate(46 321) rotate(2)')
    rect(g,-31,-31,62,61,'#20220d','#a78f2d',.8)
    for s,y in [('CURRAIS',-18),('DO GOVERNO',-6),('CEARÁ',6),('1915',18)]:
        text(g,s,0,y,10,'bold','middle','#cbb43f',maxwidth=58)
    g=group(root,'placa-hospital',transform='translate(374 237) rotate(-2)')
    rect(g,-34,-12,68,23,'#b5a037','#2e2a0c',.65)
    text(g,'HOSPITAL COLÔNIA',0,-1,6.8,'bold','middle','#171b09',maxwidth=65)
    text(g,'DE BARBACENA',0,7,7,'bold','middle','#171b09',maxwidth=63)
    g=group(root,'titulo-no-diario',transform='translate(249 406) rotate(13)')
    softpanel(g,-72,-53,144,108,8,True)
    ornament(g,0,-45,38)
    for s,y in [('DIÁRIO DO',-23),('PACIENTE',4),('N.º 1.260',31)]:
        text(g,s,0,y,24,anchor='middle',maxwidth=137)
    ornament(g,0,42,37)
    g=group(root,'ficha-paciente',transform='translate(381 588) rotate(13)')
    rect(g,-49,-10,98,20,'#b7a34b')
    text(g,'Paciente n.º 1.260',0,3,10.4,'regular','middle','#171c0c',maxwidth=94)
    softpanel(root,56,627,390,46,8,True)
    text(root,'Marcelo Dias de Carvalho Filho',250,649,24,anchor='middle',maxwidth=391)
    text(root,'Coautor e ilustrador: Marcelo Claro',250,668,15.5,'italic','middle',maxwidth=329)
    return root

SYNOPSES={
'pt':'Molambudos revela, em forma de diário, a jornada de Joaquim Antônio Correia, o Paciente 1.260: uma criança sertaneja que sobrevive à fome, à sede e ao abandono na seca de 1915, confinada nos “Currais do Governo”, campos de concentração criados para isolar e silenciar milhares de retirantes.\nInternado em 1917 no Hospital Colônia de Barbacena, Joaquim registra memórias, delírios e verdades ao longo de 62 anos. Durante sua exumação, em 1979, o diário vem à tona. Mas, com ele, algo mais também desperta.',
'en':'Told through a diary, Molambudos follows Joaquim Antônio Correia, Patient 1,260: a child from Brazil’s backlands who survives hunger, thirst, and abandonment in the drought of 1915, confined in the “Government Corrals,” concentration camps created to isolate and silence thousands of drought refugees.\nInstitutionalized at Hospital Colônia in Barbacena in 1917, Joaquim records memories, delusions, and truths over 62 years. During his exhumation in 1979, the diary resurfaces. But with it, something else also awakens.',
'zh':'《Molambudos》以日记的形式，讲述若阿金·安东尼奥·科雷亚——1260号病人的经历。1915年大旱期间，年幼的他在巴西东北部腹地忍受饥饿、干渴与遗弃，被关进塞阿拉州的“政府围栏”——为隔离并压制成千上万逃荒者而设立的集中营。\n1917年，他被送入巴尔巴塞纳的科洛尼亚精神病院，在此后的62年间记录自己的记忆、幻觉与真相。1979年，他的遗体被掘出，日记也重见天日。然而，随之苏醒的，还有别的东西。'}

def badge(parent,label,x,y,w=32):
    rect(parent,x,y-10,w,14,INK,GOLD,.7,2)
    text(parent,label,x+w/2,y,9,'bold' if label!='ZH' else 'regular','middle')

def back():
    root,defs=new(533,777,'Molambudos — contracapa corrigida')
    rect(root,0,0,533,777)
    cliprect(defs,'gravura-lateral',413,17,106,512)
    art(root,'CONTACAPA','gravura-lateral')
    border(root,533,777)
    # Three language blocks, each independently laid out and proofread.
    headings={
    'pt':['HÁ LUGARES ONDE A DOR NÃO PEDE LICENÇA PARA EXISTIR.','E HÁ HISTÓRIAS QUE O TEMPO ENTERRA… MAS NÃO APAGA.'],
    'en':['THERE ARE PLACES WHERE PAIN DOES NOT ASK PERMISSION TO EXIST.','AND THERE ARE STORIES THAT TIME BURIES… BUT CANNOT ERASE.'],
    'zh':['有些地方，痛苦无需请求许可便存在。','有些故事，时间将其掩埋……却无法抹去。']}
    for lang,top,end in [('pt',35,140),('en',156,261),('zh',278,379)]:
        g=group(root,'sinopse-'+lang)
        badge(g,{'pt':'PT-BR','en':'EN','zh':'ZH'}[lang],31,top,38 if lang=='pt' else 30)
        for n,s in enumerate(headings[lang]):
            text(g,s,78,top-1+n*12,10.4,'zh' if lang=='zh' else 'bold',maxwidth=329)
        y=paragraph(g,SYNOPSES[lang],32,top+29,377,10.5 if lang!='zh' else 10.1,
                    11.5 if lang!='zh' else 13.1,'zh' if lang=='zh' else 'regular',gap=3)
        BOUNDS.append({'block':'sinopse-'+lang,'bottom':y-(13.1 if lang=='zh' else 11.5)+2.5,'limit':end})
    line(root,27,386,506,386,sw=.7)
    # Keep the cart visible without placing running text over a bright engraving.
    shade=el('rect',x=338,y=390,width=180,height=179,fill=INK,opacity='.91')
    root.append(shade)
    # Synchronized three-column description of the book.
    cols=[('pt',29,144),('en',185,144),('zh',342,159)]
    heads={
      'pt':['ESTE LIVRO É MAIS DO QUE','UM ROMANCE. É UM ARQUIVO.','É UMA INVESTIGAÇÃO.','É UM CICLO QUE CONTINUA.'],
      'en':['THIS BOOK IS MORE THAN','A NOVEL. IT IS AN ARCHIVE.','IT IS AN INVESTIGATION.','IT IS A CYCLE THAT CONTINUES.'],
      'zh':['这不仅是一部小说。','它是一份档案，一场调查，','也是一个不断延续的循环。']}
    bullets={
      'pt':['Amor, perda e sobrevivência no sertão.','Os campos de concentração no Ceará.','Os horrores do Hospital Colônia de Barbacena.','Documentos, laudos, fotos e investigações forenses.','Um ciclo de contaminação narrativa de leitor em leitor.'],
      'en':['Love, loss, and survival in Brazil’s backlands.','Ceará’s concentration camps.','The horrors of Hospital Colônia in Barbacena.','Documents, reports, photographs, and forensic investigations.','Narrative contamination spreading from reader to reader.'],
      'zh':['爱、失去与巴西东北部腹地的求生。','塞阿拉州集中营的阴暗图景。','巴尔巴塞纳科洛尼亚精神病院的恐怖。','文件、鉴定报告、照片与法医调查。','在读者间不断蔓延的叙事污染。']}
    for lang,x,w in cols:
        g=group(root,'conteudo-'+lang)
        badge(g,{'pt':'PT-BR','en':'EN','zh':'ZH'}[lang],x,403,38 if lang=='pt' else 30)
        for i,s in enumerate(heads[lang]):
            text(g,s,x,419+i*10.3,9.5,'zh' if lang=='zh' else 'bold',maxwidth=w)
        y=464
        for s in bullets[lang]:
            text(g,'•',x,y,9.3)
            y=paragraph(g,s,x+8,y,w-8,9.4,10,'zh' if lang=='zh' else 'regular',gap=0)+1.4
        BOUNDS.append({'block':'conteudo-'+lang,'bottom':y-10+2.5,'limit':568})
    line(root,178,394,178,566,sw=.35);line(root,335,394,335,566,sw=.35)
    # Warning remains a fictional address to the reader, Patient 1,263.
    rect(root,23,575,487,91,'none','#b89c31',.7,4)
    cliprect(defs,'cranio-esquerdo',30,553,49,65)
    cliprect(defs,'cranio-direito',462,549,47,72)
    art(root,'CONTACAPA','cranio-esquerdo',transform='translate(0 38)')
    art(root,'CONTACAPA','cranio-direito',transform='translate(-1 42)')
    warnings={
      'pt':['CUIDADO','Este livro contém um ciclo de','contaminação narrativa.','Ao ler, você se torna o','Paciente 1.263.','Ao final, não será possível','devolvê-lo à estante como','se nunca o tivesse aberto.'],
      'en':['WARNING','This book contains a cycle','of narrative contamination.','By reading it, you become','Patient 1,263.','By the end, you cannot return','it to the shelf as though','you had never opened it.'],
      'zh':['警告','本书的叙事污染会循环蔓延。','阅读本书，你就成了','1263号病人。','读到最后，你将无法再把它','放回书架，假装自己','从未翻开过。']}
    for lang,x,w in [('pt',79,115),('en',207,130),('zh',350,111)]:
        g=group(root,'aviso-'+lang)
        text(g,warnings[lang][0],x+w/2,589,12,'zh' if lang=='zh' else 'bold','middle',maxwidth=w)
        for i,s in enumerate(warnings[lang][1:]):
            text(g,s,x+w/2,602+i*9.3,9,'zh' if lang=='zh' else 'regular','middle',maxwidth=w)
    line(root,200,584,200,657,sw=.35);line(root,343,584,343,657,sw=.35)
    text(root,'Marcelo Dias de Carvalho Filho',131,688,12,anchor='middle',maxwidth=201)
    text(root,'AUTOR / AUTHOR /',115,701,9.5,anchor='middle',maxwidth=150)
    text(root,'作者',169,701,9.3,'zh','middle')
    ornament(root,131,710,76)
    text(root,'Marcelo Claro',131,727,13,anchor='middle')
    text(root,'COAUTOR E ILUSTRADOR',131,740,9,'regular','middle',maxwidth=202)
    text(root,'COAUTHOR AND ILLUSTRATOR',131,751,8.4,'regular','middle',maxwidth=202)
    text(root,'合著者兼插画师',131,762,9.2,'zh','middle')
    return root

def spine():
    root,defs=new(109,772,'Molambudos — lombada corrigida')
    cliprect(defs,'area-lombada',2,3,105,766)
    art(root,'LOMBADA','area-lombada')
    rect(root,13,452,84,92)
    g=group(root,'subtitulos-lombada')
    for s,y in [('O Diário do',466),('Paciente 1.260',480)]:
        text(g,s,54.5,y,13,anchor='middle',maxwidth=82)
    ornament(g,54.5,488,35)
    for s,y in [('The Diary of',502),('Patient 1,260',516)]:
        text(g,s,54.5,y,12.6,anchor='middle',maxwidth=82)
    text(g,'1260号病人的日记',54.5,537,9.6,'zh','middle',maxwidth=83)
    rect(root,12,611,86,40)
    for s,y in [('Marcelo Dias de',622),('Carvalho Filho',638)]:
        text(root,s,54.5,y,13.6,anchor='middle',maxwidth=84)
    return root

def outline(root):
    root=copy.deepcopy(root)
    defs=root.find(f'{{{NS}}}defs')
    glyphids={}
    for parent in list(root.iter()):
        for node in list(parent):
            if node.tag!=f'{{{NS}}}text': continue
            content=node.text or ''
            face=node.get('data-face')
            font=FONTS[face]; cmap,metrics,upm=METRICS[face]
            size=float(node.get('font-size'))
            advance=width(content,size,face)
            anchor=node.get('text-anchor','start')
            x=float(node.get('x'))-(advance/2 if anchor=='middle' else advance if anchor=='end' else 0)
            y=float(node.get('y'))
            g=el('g',fill=node.get('fill'),transform=f'translate({x:.5f} {y:.5f}) scale({size/upm:.8f} {-size/upm:.8f})')
            g.set('aria-label',content)
            title=el('title');title.text=content;g.append(title)
            cursor=0
            for char in content:
                glyph=cmap[ord(char)]
                key=(face,glyph)
                if key not in glyphids:
                    gid=f'glifo-{face}-{ord(char):x}'
                    pen=SVGPathPen(font.getGlyphSet());font.getGlyphSet()[glyph].draw(pen)
                    d=pen.getCommands()
                    defs.append(el('path',id=gid,d=d))
                    glyphids[key]=gid
                use=el('use',href='#'+glyphids[key],x=cursor)
                use.set('{http://www.w3.org/1999/xlink}href','#'+glyphids[key])
                g.append(use)
                cursor+=metrics[glyph][0]
            idx=list(parent).index(node);parent.remove(node);parent.insert(idx,g)
    return root

def write(root,path):
    ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)

def embed_fonts(root):
    rules=[]
    for face in FONTFILES:
        chars=''.join(e.text or '' for e in root.iter(f'{{{NS}}}text') if e.get('data-face')==face)
        if not chars: continue
        font=TTFont(FONTFILES[face])
        options=subset.Options()
        options.layout_features=[]
        sub=subset.Subsetter(options=options)
        sub.populate(text=chars);sub.subset(font)
        font.flavor='woff2'
        buf=io.BytesIO();font.save(buf)
        enc=base64.b64encode(buf.getvalue()).decode('ascii')
        style='italic' if face=='italic' else 'normal'
        weight='bold' if face=='bold' else 'normal'
        rules.append('@font-face{font-family:"'+FAMILIES[face]+'";font-style:'+style+';font-weight:'+weight+
                     ';src:url(data:font/woff2;base64,'+enc+') format("woff2")}')
    style=el('style',type='text/css');style.text='\n'.join(rules)
    root.find(f'{{{NS}}}defs').append(style)

def render(path,out,w):
    subprocess.run(['rsvg-convert','--width',str(w),'--output',str(out),str(path)],check=True)

def main():
    source_hashes={name:hashlib.sha256((SRC/(name+'.png')).read_bytes()).hexdigest()
                   for name in ['CAPA','CONTACAPA','LOMBADA']}
    result=[]
    for name,func in [('CAPA',cover),('CONTRACAPA',back),('LOMBADA',spine)]:
        print('Compondo '+name,flush=True)
        root=func()
        edit=HERE/(name+'_EDITAVEL.svg'); final=HERE/(name+'.svg')
        curves=outline(root)
        embed_fonts(root)
        write(root,edit);write(curves,final)
        w=int(float(root.get('width')))*3
        render(final,HERE/(name+'_PREVIA.png'),w)
        render(edit,CACHE/(name+'_EDITAVEL.png'),w)
        result.append({'arquivo':final.name,'editavel':edit.name,'viewBox':root.get('viewBox'),
            'curvas':len(list(ET.parse(final).getroot().iter(f'{{{NS}}}path'))),
            'bytes':final.stat().st_size,'sha256':hashlib.sha256(final.read_bytes()).hexdigest()})
    (HERE/'textos_corrigidos.txt').write_text('\n'.join(TEXTS),encoding='utf-8')
    (HERE/'manifesto.json').write_text(json.dumps({'originais':source_hashes,'resultados':result,
        'blocos':BOUNDS,'metodo':'Potrace 1.16; 10 tons preto/dourado; letras recompostas com FontTools; sem imagens no SVG',
        'fontes':FONTFILES,'tarefa_editorial':'task-b8f38e52','validacao_externa':False},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(BOUNDS,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
