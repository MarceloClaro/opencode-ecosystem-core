"""Check manuscript and research deliverables for the OdontoCA handoff."""

import json
from PIL import Image
import re
from pathlib import Path

import fitz
from docx import Document


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "manuscript_assets"
references = json.loads((ASSETS / "references_crossref_verified.json").read_text())
article = (ROOT / "Journal_of_Dentistry_Example_OdontoCA.md").read_text()
docx = Document(ROOT / "Journal_of_Dentistry_Example_OdontoCA.docx")
docx_text = "\n".join(paragraph.text for paragraph in docx.paragraphs)
docx_tables_text = "\n".join(cell.text for table in docx.tables for row in table.rows for cell in row.cells)
pdf = fitz.open(ROOT / "Journal_of_Dentistry_Example_OdontoCA.pdf")
pdf_text = "\n".join(page.get_text() for page in pdf)
notebook = json.loads((ROOT / "OdontoCA_v1_3_4_CALIBRACAO_AGRUPADA.ipynb").read_text())
calibration = json.loads((ASSETS / "calibrated_clinical_internal_validation_corrected_sklearn190.json").read_text())

assert len(references) >= 24
assert all(ref["crossref_status"] == 200 and ref["doi_http_status"] in {301, 302, 303, 307, 308} for ref in references)
assert all(ref["doi"] in article and ref["doi"] in docx_text for ref in references)
body = article.split("## References", 1)[0]
assert all(re.search(rf"(?<!\d){i}(?!\d)", body) for i in range(1, len(references) + 1))
assert len(docx.tables) == 6 and len(docx.inline_shapes) == 5
# Section 3.4 and its figures must survive the DOCX conversion, not only exist in Markdown.
docx_paras = "\n".join(p.text for p in docx.paragraphs)
for marker in ("Distribution of outcome events across tooth positions",
               "Figure 4. Training distribution", "Figure S1. Reconstruction",
               "181 anterior-tooth transitions"):
    assert marker in docx_paras, f"docx lost manuscript content: {marker}"
assert len(pdf) >= 7
assert "0.0745" in article and "0.0745" in docx_tables_text and "0.0745" in pdf_text
assert "−0.00610" in article and "−0.00067" in article
assert "Figure_2_discrimination_corrected_sklearn190.png" in article
assert "Figure_3_calibration_corrected_sklearn190.png" in article
assert abs(calibration["metrics"]["clinical_minimal"]["intercept_and_slope"]["brier"] - 0.07450806997038699) < 1e-12
assert calibration["calibration_minus_uncalibrated"]["clinical_minimal"]["intercept_and_slope"]["brier"]["ci95"][1] < 0
assert len(notebook["cells"]) == 51
assert "Adendo clínico v1.3.3" in "".join(notebook["cells"][-4]["source"])
assert "SOURCE_SHA256" in "".join(notebook["cells"][-3]["source"])
assert "Recalibração aninhada por criança" in "".join(notebook["cells"][-2]["source"])
assert "corrected_group_splits" in "".join(notebook["cells"][-1]["source"])
assert (ASSETS / "Supplementary_Architecture_v2_1.mmd").exists()

# --- figure export contract -----------------------------------------------------
# MDPI asks for >=600 dpi. Three figures were still exported at 300/400 dpi and
# one of them also had a tick label colliding with its neighbour, so the dpi and
# the presence of every embedded figure are now asserted rather than assumed.
# Overlap itself is checked by the audit scripts, which need the live Figure
# objects and are therefore too slow to run inside this gate:
#     python3 manuscript_assets/figure_overlap_strict.py   # cohort flow + teeth
#     python3 manuscript_assets/figure_overlap_rest.py    # Figures 1, 2 and 3
EMBEDDED_FIGURES = [
    "Figure_1_pipeline_v2_compact.png",
    "Figure_2_discrimination_corrected_sklearn190.png",
    "Figure_3_calibration_corrected_sklearn190.png",
    "Figure_cohort_flow.png",
    "Figure_teeth_training_propagation.png",
]
for _name in EMBEDDED_FIGURES:
    _path = ASSETS / _name
    assert _path.exists(), f"missing embedded figure: {_name}"
    with Image.open(_path) as _im:
        _dpi = _im.info.get("dpi", (0, 0))[0]
    assert _dpi >= 599, f"{_name} exported at {_dpi:.0f} dpi, MDPI asks for >=600"
assert "Figure_cohort_flow.png" in article
assert "Figure_teeth_training_propagation.png" in article

# --- v1.4.0 clinical-prediction deliverable -------------------------------------
# The gate above audits the historical v1.3.4 calibration notebook. The current
# thesis deliverable is v1.4.0, so its existence, provenance block and error-free
# execution are asserted explicitly to prevent a silent regression.
v140 = ROOT / "OdontoCA_v1_4_0_CLINICAL_PREDICTION.ipynb"
assert v140.exists(), f"missing clinical-prediction deliverable: {v140.name}"
nb140 = json.loads(v140.read_text())
sources_140 = "".join("".join(c["source"]) for c in nb140["cells"])
for marker in ("resolve_source", "neighbor_caries_count", "Riley",
               "LOCK_DIR", "predict_tooth_risk", "MOLARS"):
    assert marker in sources_140, f"v1.4.0 missing block: {marker}"
errored = [i for i, c in enumerate(nb140["cells"])
           if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
assert not errored, f"v1.4.0 executed with errors in cells: {errored}"
def _stream_text(cell):
    """Concatenate stream outputs; nbformat may store `text` as str or list."""
    parts = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            t = o.get("text", "")
            parts.append("".join(t) if isinstance(t, list) else str(t))
    return "".join(parts)


outs_140 = "".join(_stream_text(c) for c in nb140["cells"])
for fact in ('"required_outcome_events": 240', '"anterior_events": 0', '"molar_events": 83',
             '"sha256_matches_manuscript": true'):
    assert fact in outs_140, f"v1.4.0 output missing expected fact: {fact}"

# New manuscript figures must exist on disk, not only be referenced in prose.
for fig in ("Figure_teeth_training_propagation.png", "Figure_cohort_flow.png"):
    assert (ASSETS / fig).exists(), f"referenced figure missing on disk: {fig}"
    assert fig in article, f"figure referenced nowhere in the article: {fig}"
    assert f"manuscript_assets/{fig})" in article, f"figure not embedded: {fig}"

embedded = re.findall(r"manuscript_assets/([^)\s]+\.png)", article)
for path in embedded:
    assert (ASSETS / path).exists(), f"embedded figure missing on disk: {path}"
assert len(embedded) == 5, f"unexpected embedded figure count: {len(embedded)} -> {embedded}"

# The PT-BR control translation must not silently reuse English-labelled
# figures; the repository convention is a `_pt` suffix for every figure.
pt_article = (ROOT / "Journal_of_Dentistry_Example_OdontoCA_PT.md").read_text()
embedded_pt = re.findall(r"manuscript_assets/([^)\s]+\.png)", pt_article)
assert len(embedded_pt) == 5, f"PT figure count: {len(embedded_pt)} -> {embedded_pt}"
for path in embedded_pt:
    assert (ASSETS / path).exists(), f"PT figure missing on disk: {path}"
    assert path.endswith("_pt.png"), f"PT manuscript reuses an English-labelled figure: {path}"

print(f"FINAL_QUALITY_GATE_PASS: {len(references)} DOI; {len(pdf)} PDF pages; "
      f"{len(embedded)} figures embedded (Figures 1-4 + S1), all localised for PT; "
      f"51 legacy cells; {len(nb140['cells'])} cells in v1.4.0 deliverable, 0 errors")
