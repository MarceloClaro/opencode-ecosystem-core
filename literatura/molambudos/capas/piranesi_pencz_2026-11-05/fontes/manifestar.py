"""Empacota proveniência sem incorporar logs temporários ou arquivos anteriores."""
from pathlib import Path
import hashlib
import json
from PIL import Image

OUT = Path(__file__).resolve().parent.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

original = json.loads((OUT/'provas_deterministicas/manifesto_original.json').read_text())
for item in original['items']:
    assert sha(OUT/'provas_deterministicas'/item['output']) == item['output_sha256']
assert sha(OUT/'provas_deterministicas/contact_sheet.png') == original['contact_sheet']['sha256']

arts = []
for name in ['sertao','confinamento','arquivo']:
    p = OUT/'fontes'/f'arte_{name}.png'
    with Image.open(p) as im:
        arts.append({'name':name, 'path':str(p.relative_to(OUT)), 'sha256':sha(p),
                     'pixels':list(im.size),'mode':im.mode,'ai_generated':True,
                     'fictional':True,'placed_mm':[42,63],
                     'effective_dpi':im.width/42*25.4,'upscale':False})
files=[]
for p in sorted(OUT.rglob('*')):
    if not p.is_file() or p.suffix not in {'.pdf','.png','.json','.md','.py','.tex'}:
        continue
    if p.name in {'manifesto.json','variante.tex','layout.pdf'}:
        continue
    files.append({'path':str(p.relative_to(OUT)),'sha256':sha(p),'bytes':p.stat().st_size})
manifest={
    'schema_version':1,'project':'Molambudos','direction':'Piranesi/Pencz R1081',
    'spec':'SPEC-935-R1082-molambudos-capas-piranesi-pencz',
    'status':'digital_artwork_composed_for_editorial_review',
    'ai_generated_artwork':True,'external_print_approval':False,
    'physical_proof':False,'published':False,'new_artworks':arts,
    'artwork_tool':'image_gen.imagegen','model_version':'not_exposed_by_tool',
    'deterministic_proofs':'preserved byte-for-byte from R1081; hashes checked',
    'profile_execution':{'agent_id':'romance-psicologico-molambudos',
        'activation_task':'task-16e5a510','core_task':'task-0c4481f8',
        'executor':'codex','mode':'cli-read-only-windows-interop',
        'editorial_task_executed':True,'own_file_reading':False,
        'evidence':'verified excerpts supplied by primary',
        'image_generation_by_profile':False},
    'printing':{'binding':'paperback','trim_mm':[160,230],
        'paper':'premium color / white KDP','bleed_mm':3.175,
        'vector_swatch_max_nominal_tac_percent':152.905,
        'global_icc_tac_measured':False,'pdf_x_claim':False},
    'files':files}
(OUT/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(files),'new_artworks':arts},ensure_ascii=False,indent=2))
