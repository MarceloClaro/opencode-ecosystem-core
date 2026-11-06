"""Preserva a composição escolhida e incorpora as duas artes em gravura brasileira."""
from pathlib import Path
import hashlib
import json
import fitz
from PIL import Image

HERE=Path(__file__).resolve().parent
OUT=HERE.parent
BASE=OUT.parent/'edicao_2026-11-05'
MM=72/25.4
BLEED=3.175

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def render(name,pages):
    source=BASE/f'molambudos_capa_completa_{name}_300dpi.pdf'
    doc=fitz.open(source)
    page=doc[0]
    images=page.get_image_info(xrefs=True)
    assert len(images)==2
    # Ordem de desenho da composição já escolhida: contracapa, capa frontal.
    page.replace_image(images[0]['xref'],filename=str(HERE/'arte_contracapa_original.png'))
    page.replace_image(images[1]['xref'],filename=str(HERE/'arte_frontal_original.png'))
    metadata=doc.metadata
    metadata['title']=f'Molambudos — capa completa — {pages} páginas — gravura brasileira'
    metadata['subject']='Capa preta e ouro envelhecido; traço Piranesi/Pencz; reconstituição ficcional por IA'
    doc.set_metadata(metadata)
    target=OUT/f'molambudos_capa_completa_{name}_300dpi.pdf'
    doc.save(target,garbage=4,deflate=True)
    doc.close()
    doc=fitz.open(target)
    p=doc[0]
    spine=pages*.002347*25.4
    width=326.35+spine
    assert len(doc)==1 and not doc.is_encrypted
    assert abs(p.rect.width/MM-width)<.02
    assert abs(p.rect.height/MM-236.35)<.02
    assert p.bleedbox==p.mediabox
    assert abs(p.trimbox.x0/MM-BLEED)<.02
    for phrase in ['MOLAMBUDOS','O Diário do Paciente 1.260','Marcelo Dias de Carvalho Filho','Marcelo Claro']:
        assert phrase in p.get_text()
    assert 'ISBN' not in p.get_text()
    for f in p.get_fonts(full=True):
        assert doc.extract_font(f[0])[3]
    raster=[]
    for im in p.get_image_info():
        b=fitz.Rect(im['bbox'])
        dpi=[im['width']/b.width*72,im['height']/b.height*72]
        assert min(dpi)>=300
        raster.append({'pixels':[im['width'],im['height']],'effective_dpi':dpi})
    assert len(raster)==2
    pngdir=OUT/name
    pngdir.mkdir(exist_ok=True)
    fx=BLEED+160+spine
    panels={
        'capa_frontal_160x230mm':(fx,BLEED,160,230),
        'contracapa_160x230mm':(BLEED,BLEED,160,230),
        'lombada':(BLEED+160,BLEED,spine,230),
        'capa_aberta_com_sangria':(0,0,width,236.35)}
    exported=[]
    for label,(x,y,w,h) in panels.items():
        panel=fitz.open()
        pp=panel.new_page(width=w*MM,height=h*MM)
        pp.show_pdf_page(pp.rect,doc,0,clip=fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM))
        pix=pp.get_pixmap(dpi=300,alpha=False)
        pix.set_dpi(300,300)
        png=pngdir/(label+'_300dpi.png')
        pix.save(png)
        with Image.open(png) as im:
            exported.append({'path':str(png.relative_to(OUT)),'pixels':list(im.size),'size_mm':[w,h]})
            assert abs(im.info['dpi'][0]-300)<.1
            if label.startswith(('capa_frontal','contracapa')):
                assert im.size==(1890,2717)
        panel.close()
    p.get_pixmap(dpi=110,alpha=False).save(OUT/f'previa_{name}.png')
    doc.close()
    return {'variant':name,'pages':pages,'spine_mm':spine,'cover_mm':[width,236.35],
            'trim_mm':[160,230],'bleed_mm':BLEED,'artwork':raster,'pngs':exported,
            'fonts_embedded':True,'status':'PASS_LOCAL','external_print_approval':False}

if __name__=='__main__':
    data=[render('422p_print',422),render('436p_canonica',436)]
    (OUT/'preflight_local.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
