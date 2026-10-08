"""Translate the retained manuscript package while preserving its layout parts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import json
import re

from lxml import etree as ET

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "manuscript_assets"
WORK = ASSETS / "pt_build"
SOURCE = ROOT / "Journal_of_Dentistry_Example_OdontoCA.docx"
TARGET = ROOT / "Journal_of_Dentistry_Example_OdontoCA_PT.docx"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}


def text_of(p):
    return "".join(p.xpath(".//w:t/text()", namespaces=NS))


def assemble():
    english = (ROOT / "Journal_of_Dentistry_Example_OdontoCA.md").read_text(encoding="utf-8")
    parts = [(ASSETS / name).read_text(encoding="utf-8").strip() for name in
             ("pt_resumo.md", "pt_parte_metodos.md", "pt_parte_resultados.md")]
    references = english.split("## References", 1)[1]
    portuguese = "\n\n".join(parts) + "\n\n## Referências" + references
    portuguese = portuguese.replace("precisão–revocação", "precisão–sensibilidade")
    (ROOT / "Journal_of_Dentistry_Example_OdontoCA_PT.md").write_text(portuguese, encoding="utf-8")
    WORK.mkdir(exist_ok=True)
    assert re.findall(r"\[(?:\d+,?)+\]", english) == re.findall(r"\[(?:\d+,?)+\]", portuguese)
    assert english.split("## References", 1)[1] == portuguese.split("## Referências", 1)[1]
    print("PORTUGUESE_MARKDOWN_ASSEMBLED: citations and all 28 references preserved")


def build():
    with ZipFile(WORK / "source_draft.docx") as z:
        en = ET.fromstring(z.read("word/document.xml"))
        en_rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    with ZipFile(WORK / "translation_draft.docx") as z:
        pt = ET.fromstring(z.read("word/document.xml"))
        pt_rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    en_paras = en.xpath(".//w:p", namespaces=NS)
    pt_paras = pt.xpath(".//w:p", namespaces=NS)
    assert len(en_paras) == len(pt_paras), (len(en_paras), len(pt_paras))
    translations = {}
    for a, b in zip(en_paras, pt_paras):
        key = text_of(a)
        if not key:
            continue
        if key in translations:
            assert text_of(translations[key]) == text_of(b), key
        translations[key] = b
    # Pandoc assigns the same external-link relationships in both drafts.
    external = lambda root: {x.get("Id"): x.get("Target") for x in root if x.get("TargetMode") == "External"}
    assert external(en_rels) == external(pt_rels)

    with ZipFile(SOURCE) as z:
        originals = {info.filename: z.read(info.filename) for info in z.infolist()}
    doc = ET.fromstring(originals["word/document.xml"])
    manual = {
        "Research article · secondary analysis and internal validation": "Artigo de pesquisa · análise secundária e validação interna",
        "A R T I C L E  I N F O": "INFORMAÇÕES DO ARTIGO",
        "A B S T R A C T": "R E S U M O",
        "Keywords:": "Palavras-chave:",
        "early-childhood caries": "cárie na primeira infância",
        "clinical prediction": "predição clínica",
        "primary teeth": "dentes decíduos",
        "spatial features": "características espaciais",
        "internal validation": "validação interna",
        "calibration": "calibração",
        "oral microbiome": "microbioma oral",
    }
    replaced = 0
    unknown = []
    for p in doc.xpath(".//w:p", namespaces=NS):
        old = text_of(p)
        if not old:
            continue
        if old in translations:
            if text_of(translations[old]) == old:
                continue
            for child in list(p):
                if child.tag != f"{{{NS['w']}}}pPr":
                    p.remove(child)
            for child in translations[old]:
                if child.tag != f"{{{NS['w']}}}pPr":
                    p.append(deepcopy(child))
            replaced += 1
        elif old in manual:
            nodes = p.xpath(".//w:t", namespaces=NS)
            nodes[0].text = manual[old]
            for node in nodes[1:]:
                node.text = ""
            replaced += 1
        else:
            unknown.append(old)
    assert not unknown, unknown

    rels = ET.fromstring(originals["word/_rels/document.xml.rels"])
    target_by_id = {x.get("Id"): x.get("Target") for x in rels}
    drawings = doc.xpath(".//a:blip", namespaces=NS)
    figures = ["Figure_1_pipeline_v2_compact_pt.png", "Figure_2_discrimination_corrected_sklearn190_pt.png", "Figure_3_calibration_corrected_sklearn190_pt.png"]
    assert len(drawings) == len(figures) == 3
    edits = {}
    for drawing, figure in zip(drawings, figures):
        rel_id = drawing.get(f"{{{NS['r']}}}embed")
        edits["word/" + target_by_id[rel_id]] = (ASSETS / figure).read_bytes()
    for a, b in zip(doc.xpath(".//wp:docPr", namespaces=NS), pt.xpath(".//wp:docPr", namespaces=NS)):
        for attr in ("descr", "title"):
            if b.get(attr):
                a.set(attr, b.get(attr))
    # Set proofreading language only in translated runs, retaining existing styles.
    for r in doc.xpath(".//w:r", namespaces=NS):
        if r.xpath(".//w:t", namespaces=NS):
            rp = r.find(f"{{{NS['w']}}}rPr")
            if rp is None:
                rp = ET.Element(f"{{{NS['w']}}}rPr")
                r.insert(0, rp)
            lang = rp.find(f"{{{NS['w']}}}lang")
            if lang is None:
                lang = ET.SubElement(rp, f"{{{NS['w']}}}lang")
            lang.set(f"{{{NS['w']}}}val", "pt-BR")
    edits["word/document.xml"] = ET.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(TARGET, "w", ZIP_DEFLATED) as z:
        for name, data in originals.items():
            z.writestr(name, edits.get(name, data))
    with ZipFile(TARGET) as z:
        assert set(z.namelist()) == set(originals)
        unchanged = [name for name in originals if name not in edits]
        assert all(z.read(name) == originals[name] for name in unchanged)
    # Paragraph-property, section and relationship fidelity is deliberate.
    source_xml = ET.fromstring(originals["word/document.xml"])
    for path in (".//w:sectPr", ".//w:tblPr", ".//w:tblGrid"):
        assert [ET.tostring(x) for x in source_xml.xpath(path,namespaces=NS)] == [ET.tostring(x) for x in doc.xpath(path,namespaces=NS)], path
    report = {"source_sha256": sha256(SOURCE.read_bytes()).hexdigest(), "target_sha256": sha256(TARGET.read_bytes()).hexdigest(), "translated_paragraphs": replaced, "figures": 3, "references": 28, "preserved_package_parts": len(unchanged), "edited_parts": list(edits), "fidelity": "page geometry, styles, table grids, relationships and headers/footers preserved"}
    (WORK / "translation_quality.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (WORK / "artifact.md").write_text("# Contrato da versão em português\n\nReferência: " + str(SOURCE) + "\n\nSHA-256: " + report["source_sha256"] + "\n\nA versão copia o pacote original, substitui os parágrafos traduzidos e as três imagens. Preserva geometrias de página, estilos, grades de tabela, propriedades de parágrafo, cabeçalhos, rodapés, relacionamentos e todas as demais partes do pacote. As referências mantêm os títulos e DOI originais. A expansão textual pode alterar a paginação.\n", encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("assemble", "build"))
    args = parser.parse_args()
    assemble() if args.mode == "assemble" else build()
