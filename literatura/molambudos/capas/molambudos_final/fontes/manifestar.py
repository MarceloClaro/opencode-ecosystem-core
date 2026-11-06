from pathlib import Path
import hashlib,json
from PIL import Image

OUT=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.suffix in {'.pdf','.png','.json','.md','.py','.tex'} and p.name not in {'manifesto.json','layout.pdf','variante.tex'}:
        files.append({'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)})
art=[]
for name in ['arte_frontal_original.png','arte_contracapa_original.png']:
    p=OUT/'fontes'/name
    with Image.open(p) as im:
        art.append({'path':str(p.relative_to(OUT)),'pixels':list(im.size),'mode':im.mode,
                    'ai_assisted_text_cleanup':True,'placed_width_mm':86,
                    'effective_dpi':im.width/86*25.4,'sha256':sha(p)})
data={'schema_version':1,'status':'digital_cover_for_editorial_review',
      'author_selected_layout':'black and antique gold, central illustration',
      'art_direction':'Piranesi/Pencz engraved linework with Brazilian motifs from author-provided artwork',
      'source_image_observed_pixels':[2000,1405],
      'ai_generated_or_edited':True,'tool':'image_gen.imagegen','model_version':'not_exposed',
      'fictional_reconstruction':True,'upscale_to_claim_dpi':False,
      'external_print_approval':False,'physical_proof':False,'published':False,
      'paper_assumption':'KDP paperback premium color white paper',
      'profile_editorial_task':'task-0c4481f8',
      'profile_evidence_scope':'verified excerpts supplied by primary; not own file reading',
      'artwork':art,'files':files}
(OUT/'manifesto.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(files),'artwork':art},ensure_ascii=False,indent=2))
