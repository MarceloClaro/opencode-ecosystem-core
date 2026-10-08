"""Deterministic build of every submission artefact from the canonical Markdown.

The manuscript is authored in Markdown; everything else (anonymised DOCX,
review PDF, and the PDF form of each supplementary file) is derived. Doing this
by hand previously made it possible for the DOCX and the PDF to disagree with
the Markdown, and for the submission package to lag behind the sources. This
script makes the whole chain a single reproducible command:

    python3 manuscript_assets/build_submission.py

Order matters: the Markdown -> DOCX step must precede finalize_docx.py, which
consumes clean_draft.docx, and the package copy must come last so it can never
contain a stale manuscript.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "manuscript_assets"
PACKAGE = ROOT / "submission_package"

MANUSCRIPT_MD = ROOT / "Journal_of_Dentistry_Example_OdontoCA.md"
CLEAN_DRAFT = ASSETS / "clean_draft.docx"
MANUSCRIPT_DOCX = ROOT / "Journal_of_Dentistry_Example_OdontoCA.docx"
MANUSCRIPT_PDF = ROOT / "Journal_of_Dentistry_Example_OdontoCA.pdf"

# Markdown source -> PDF name in the package.
SUPPLEMENTARY = {
    "Supplementary_File_S3_TRIPOD_AI_Checklist.md": "Supplementary_File_S3_TRIPOD_AI_Checklist.pdf",
    "Supplementary_File_S4_PROBAST_AI_Assessment.md": "Supplementary_File_S4_PROBAST_AI_Assessment.pdf",
    "Highlights.md": "Highlights.pdf",
    "Cover_Letter_Journal_of_Dentistry.md": "Cover_Letter_Journal_of_Dentistry.pdf",
    "Journal_of_Dentistry_Title_Page.md": "Journal_of_Dentistry_Title_Page.pdf",
}

# Figures are rendered by their own scripts; the package takes the canonical PNG.
# Destination number = figure number as CITED in the manuscript text, i.e. the
# order the drawings appear in the DOCX. The discrimination curves are Figure 3
# (a cohort flow diagram sits at Figure 2), so mapping them to Figure_2.png
# shipped the wrong image under a plausible-looking name. Keys are ordered so
# the mapping reads in manuscript order; assert_figure_order() enforces it.
FIGURES = {
    "Figure_1_pipeline_v2_compact.png": "Figure_1.png",
    "Figure_cohort_flow.png": "Figure_2.png",
    "Figure_2_discrimination_corrected_sklearn190.png": "Figure_3.png",
    "Figure_3_calibration_corrected_sklearn190.png": "Figure_4.png",
    "Figure_teeth_training_propagation.png": "Figure_5.png",
}
FIGURE_VECTORS = {"Figure_teeth_training_propagation": ("Figure_5.pdf", "Figure_5.svg")}


def assert_figure_order(package, docx=None):
    """Fail closed if Figure_N.png is not the Nth drawing of the manuscript.

    A silently swapped figure is worse than a missing one: the reviewer opens
    "Figure 2" and reads the ROC curves where the text promises the cohort flow.
    Comparing SHA-256 against the drawings embedded in the DOCX, in document
    order, makes that unrepresentable. Figures beyond the drawing count are
    reported and skipped rather than silently accepted.
    """
    docx = docx or MANUSCRIPT_DOCX
    if not Path(docx).exists():
        print(f"  ! {Path(docx).name} absent; figure order not verified")
        return
    import hashlib
    import re
    import zipfile

    with zipfile.ZipFile(docx) as z:
        doc = z.read("word/document.xml").decode("utf-8", "ignore")
        rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="(media/[^"]+)"',
                               z.read("word/_rels/document.xml.rels").decode()))
        embedded = [hashlib.sha256(z.read("word/" + rels[r])).hexdigest()
                    for r in re.findall(r'r:embed="([^"]+)"', doc)]

    if len(embedded) != len(FIGURES):
        print(f"  ! manuscript has {len(embedded)} drawings but FIGURES declares "
              f"{len(FIGURES)}; figure order NOT verified")
        return
    for i, name in enumerate(sorted(FIGURES.values(),
                                    key=lambda n: int(re.search(r"\d+", n).group())), 1):
        pkg = package / name
        if not pkg.exists():
            raise SystemExit(f"figure order FAILED: {name} absent from package")
        got = hashlib.sha256(pkg.read_bytes()).hexdigest()
        if got != embedded[i - 1]:
            raise SystemExit(
                f"figure order FAILED: {name} does not match drawing {i} of "
                f"{Path(docx).name}. The packaged figure and the embedded figure "
                f"have diverged; re-embed the figure before shipping.")
    print(f"  figure order OK: {len(embedded)} figures match the manuscript in order")

GRAPHICAL_ABSTRACT = ("Graphical_Abstract.png", "Graphical_Abstract.pdf")


def run(cmd, **kw):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kw)


def md_to_docx(md: Path, out: Path, reference=None):
    """Markdown -> DOCX.

    Deliberately NOT using --reference-doc: the journal template renames the
    base styles ('normal', no 'First Paragraph'), which finalize_docx.py then
    cannot look up. finalize_docx.py already copies the template's page
    geometry and margins onto the result, which is what the template is
    actually needed for.
    """
    cmd = [
        "pandoc", str(md),
        "--from", "markdown+pipe_tables+implicit_figures",
        "--to", "docx",
        "--output", str(out),
        "--resource-path", str(ROOT),
    ]
    run(cmd)


def md_to_pdf(md: Path, out: Path):
    """Markdown -> PDF for a standalone front-matter/supplementary file.

    These have no finalize step, so Markdown -> DOCX -> PDF is the whole chain.
    """
    tmp = ASSETS / f".build_{out.stem}.docx"
    md_to_docx(md, tmp)
    docx_to_pdf(tmp, out)
    tmp.unlink()


def docx_to_pdf(docx: Path, out: Path):
    """DOCX -> PDF.

    Used for the manuscript review PDF so that it is a rendering of the actual
    submitted DOCX, not of the Markdown. Deriving the PDF from the Markdown
    instead silently skipped finalize_docx.py and inflated the page count.
    """
    run(["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(docx.parent), str(docx)])
    produced = docx.with_suffix(".pdf")
    if not produced.exists():
        raise SystemExit(f"soffice did not produce {produced}")
    if produced != out:
        shutil.move(str(produced), str(out))


def main():
    PACKAGE.mkdir(exist_ok=True)
    print("[1/5] Markdown -> anonymised DOCX")
    md_to_docx(MANUSCRIPT_MD, CLEAN_DRAFT)
    run([sys.executable, str(ASSETS / "finalize_docx.py")])

    print("[2/5] Finalised DOCX -> review PDF")
    docx_to_pdf(MANUSCRIPT_DOCX, MANUSCRIPT_PDF)

    print("[3/5] Supplementary files and front matter -> PDF")
    for src_name, pdf_name in SUPPLEMENTARY.items():
        src = ROOT / src_name
        if not src.exists():
            print(f"  ! missing {src_name}, skipped")
            continue
        md_to_pdf(src, ROOT / pdf_name)

    print("[4/5] Refresh submission package")
    shutil.copy2(MANUSCRIPT_DOCX, PACKAGE / "Manuscript_Anonymised.docx")
    for src_name, pdf_name in SUPPLEMENTARY.items():
        pdf = ROOT / pdf_name
        if pdf.exists():
            shutil.copy2(pdf, PACKAGE / pdf_name)
    for src_name, dst_name in FIGURES.items():
        src = ASSETS / src_name
        if not src.exists():
            print(f"  ! missing {src_name}, skipped")
            continue
        shutil.copy2(src, PACKAGE / dst_name)
    for stem, dst_names in FIGURE_VECTORS.items():
        for dst_name in dst_names:
            src = ASSETS / f"{stem}.{dst_name.rsplit('.', 1)[1]}"
            if not src.exists():
                print(f"  ! missing {src.name}, skipped")
                continue
            shutil.copy2(src, PACKAGE / dst_name)
    assert_figure_order(PACKAGE)

    print("[5/5] Graphical abstract")
    for name in GRAPHICAL_ABSTRACT:
        src = ASSETS / name
        if src.exists():
            shutil.copy2(src, PACKAGE / name)
        else:
            print(f"  ! missing {name}, skipped")

    print("\nPackage contents:")
    for f in sorted(PACKAGE.iterdir()):
        print(f"  {f.name:52s} {f.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
