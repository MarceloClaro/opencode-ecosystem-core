from pathlib import Path
import fitz, json, re, subprocess, sys
from PIL import Image, ImageOps, ImageDraw
root=Path.cwd(); out=root/'outputs/core-r911'; imgs=out/'pages'; imgs.mkdir(exist_ok=True)
doc=fitz.open(root/'livro-core/main.pdf')
labels={}
for line in (root/'livro-core/main.aux').read_text(errors='replace').splitlines():
 m=re.match(r'\\newlabel\{(fig:(?:AR\d\d-(?:mental|structure|flow)|global-[^}]+))\}\{\{[^}]*\}\{([^}]+)\}',line)
 if m:labels[m[1]]=m[2]
# Locate actual physical pages by visible titles, independently of TeX page numbers.
figures={}; global_terms={'global-mental':'Mapa mental completo dos 18 temas','global-processes':'Diagrama geral: entradas, instâncias e caminhos','global-flow':'Fluxograma geral de uso e conferência','global-matrix':'Matriz completa das relações entre camadas estáticas'}
words_off=[]; margin_bad=[]; max_extend=0; drawing_bad=[]; node_font_min=100; node_count=0; overlaps=[]; bbox_candidates=[]
colors=[(235/255,243/255,253/255),(27/255,42/255,74/255),(255/255,248/255,225/255)]
def intersection_area(points, rect):
 for axis,bound,greater in [(0,rect.x0,True),(0,rect.x1,False),(1,rect.y0,True),(1,rect.y1,False)]:
  output=[]
  if not points:return 0
  previous=points[-1]; prev_in=(previous[axis]>=bound if greater else previous[axis]<=bound)
  for current in points:
   cur_in=(current[axis]>=bound if greater else current[axis]<=bound)
   if cur_in!=prev_in:
    ratio=(bound-previous[axis])/(current[axis]-previous[axis]); output.append(tuple(previous[k]+ratio*(current[k]-previous[k]) for k in range(2)))
   if cur_in:output.append(current)
   previous=current;prev_in=cur_in
  points=output
 return abs(sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))/2) if points else 0

for n,page in enumerate(doc):
 text=page.get_text(); normalized=' '.join(text.split())
 for a in range(1,19):
  for kind,title in [('mental','Mapa mental'),('structure','Diagrama de arquitetura'),('flow','Fluxograma')]:
   if re.search(rf'AR{a:02}\s*[·•]?\s*{title}',normalized):figures[f'fig:AR{a:02}-{kind}']=n+1
 for key,term in global_terms.items():
  if term in normalized:figures['fig:'+key]=n+1
 words=page.get_text('words')
 footer=[x[4] for x in words if x[1]>page.rect.height-55 and x[4].isdigit()]
 # main.tex is explicitly oneside: inner margin is always left.
 left=2.65*72/2.54; right=page.rect.width-2.25*72/2.54
 for w in words:
  if w[0]<-.5 or w[1]<-.5 or w[2]>page.rect.width+.5 or w[3]>page.rect.height+.5:words_off.append([n+1,w])
  if n>0 and 76<w[1]<page.rect.height-64:
   delta=max(left-w[0],w[2]-right,0);max_extend=max(max_extend,delta)
   if delta>2:margin_bad.append([n+1,delta,w])
 if n+1 in figures.values():
  page_spans=[s for b in page.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
  node_rects=[]; node_shapes=[]
  for d in page.get_drawings():
   fill=d.get('fill')
   if fill and any(max(abs(x-y) for x,y in zip(fill,c))<.005 for c in colors):
    rect=d['rect']
    if rect.width>45 and rect.height>15 and rect.width<190:
     node_count+=1; node_rects.append(rect); node_shapes.append([tuple(v[1]) for v in d['items']] if len(d['items'])==4 and all(v[0]=='l' for v in d['items']) else [(rect.x0,rect.y0),(rect.x1,rect.y0),(rect.x1,rect.y1),(rect.x0,rect.y1)])
     spans=[s for s in page_spans if rect.contains(fitz.Rect(s['bbox']))]
     if spans:node_font_min=min(node_font_min,*[s['size'] for s in spans])
     if rect.x0<left-1 or rect.x1>right+1 or rect.y0<60 or rect.y1>page.rect.height-60:drawing_bad.append([n+1,list(rect)])
  for i,a in enumerate(node_rects):
   for b in node_rects[i+1:]:
    intersection=a & b
    if not intersection.is_empty and intersection.get_area()>1:
     bbox_candidates.append([n+1,list(a),list(b),intersection.get_area()])
     if intersection_area(node_shapes[i],b)>1 and intersection_area(node_shapes[i+1+node_rects[i+1:].index(b)],a)>1:overlaps.append([n+1,list(a),list(b)])
assert len(figures)==58,(len(figures),figures)
for n in sorted(set(figures.values())):
 target=imgs/f'p{n:03}.png'
 if '--skip-render' not in sys.argv: subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-scale-to','1800','-png',str(root/'livro-core/main.pdf'),str(target.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
images=sorted(set(figures.values()))
sheets=[]
for k in range(0,len(images),4):
 group=images[k:k+4]; sheet=Image.new('RGB',(2100,3060),'#dbe4ed'); draw=ImageDraw.Draw(sheet)
 for i,num in enumerate(group):
  im=Image.open(imgs/f'p{num:03}.png').convert('RGB');im.thumbnail((1020,1470))
  x=20+(i%2)*1050;y=35+(i//2)*1520
  sheet.paste(im,(x,y));draw.text((x,y-23),f'PDF {num}',fill='black')
 target=out/f'sheet-{k//4+1:02}.jpg';sheet.save(target,quality=92);sheets.append(str(target.relative_to(root)))
report={'pdf_pages':len(doc),'figures':figures,'tex_labels':labels,'offpage_words':words_off,'horizontal_margin_violations_above_2pt':margin_bad,'maximum_horizontal_extension_pt':max_extend,'drawing_boundary_violations':drawing_bad,'colored_node_bbox_candidates':bbox_candidates,'colored_node_shape_overlaps':overlaps,'minimum_detected_node_font_pt':node_font_min,'detected_colored_nodes':node_count,'sheets':sheets,'scope':'Coordenadas em todas as páginas e renderização de todas as 58 vistas novas; inspeção visual assistida por IA registrada separadamente.'}
(out/'visual-geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in report.items() if k not in ['figures','tex_labels','sheets']},ensure_ascii=False))
