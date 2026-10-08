"""Build the author-facing PT-BR manuscript from the canonical PT-BR Markdown.

    python3 manuscript_assets/build_ptbr.py

This is deliberately a separate chain from build_submission.py: the English
package is the journal submission and must never gain, lose or reorder a file
because someone regenerated the translation. The only shared code is the
Markdown -> DOCX and DOCX -> PDF helpers, which are imported rather than
copied, and the formatter, which takes a `lang` argument.

The translation itself is not derived from the English Markdown: it is authored
and gated by test_ptbr_parity.py, which fails if any number, DOI, reference,
section or anti-overclaim hedge drifts from the English source.
"""

import subprocess
import sys
from pathlib import Path

from build_submission import ROOT, ASSETS, docx_to_pdf, md_to_docx
from finalize_docx import DEFAULT_EXAMPLE, finalize


PT_MD = ROOT / "Journal_of_Dentistry_Example_OdontoCA_PT.md"
PT_DRAFT = ASSETS / ".build_ptbr_draft.docx"
PT_DOCX = ROOT / "Journal_of_Dentistry_Example_OdontoCA_PT.docx"
PT_PDF = ROOT / "Journal_of_Dentistry_Example_OdontoCA_PT.pdf"

EN_PACKAGE = ROOT / "submission_package"

# The journal submission is English-only and must stay exactly these 13 files.
EN_PACKAGE_MANIFEST = {
    "Manuscript_Anonymised.docx",
    "Highlights.pdf",
    "Cover_Letter_Journal_of_Dentistry.pdf",
    "Journal_of_Dentistry_Title_Page.pdf",
    "Figure_1.png",
    "Figure_2.png",
    "Figure_3.png",
    "Graphical_Abstract.png",
    "Graphical_Abstract.pdf",
    "Supplementary_File_S1_Architecture.pdf",
    "Supplementary_File_S2_Technical_Audit.pdf",
    "Supplementary_File_S3_TRIPOD_AI_Checklist.pdf",
    "Supplementary_File_S4_PROBAST_AI_Assessment.pdf",
    # Clinical-prediction track (SPEC-935-R645): the locked model, its provenance
    # card, and the pre-specified external validation protocol are part of the
    # submission because the manuscript now claims a testable prediction model.
    "odontoca_clinical_model.joblib",
    "odontoca_clinical_model_card.json",
    "external_validation_protocol.md",
}


def run(cmd, **kw):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kw)


def main() -> int:
    if not PT_MD.exists():
        raise SystemExit(f"missing PT-BR source: {PT_MD}")

    figures = [
        "Figure_1_pipeline_v2_compact_pt.png",
        "Figure_2_discrimination_corrected_sklearn190_pt.png",
        "Figure_3_calibration_corrected_sklearn190_pt.png",
    ]
    missing = [f for f in figures if not (ASSETS / f).exists()]
    if missing:
        raise SystemExit(
            "missing PT-BR figures (regenerate with render_pipeline_v2_compact_pt.py "
            f"and render_corrected_figures_pt.py): {missing}"
        )

    print("[1/4] Parity gate (PT-BR vs EN)")
    run([sys.executable, str(ASSETS / "test_ptbr_parity.py")])

    print("[2/4] PT-BR Markdown -> draft DOCX")
    md_to_docx(PT_MD, PT_DRAFT)

    print("[3/4] Draft -> journal-formatted PT-BR DOCX")
    finalize(PT_DRAFT, DEFAULT_EXAMPLE, PT_DOCX, "pt")
    print(PT_DOCX)

    print("[4/4] PT-BR DOCX -> PDF")
    docx_to_pdf(PT_DOCX, PT_PDF)
    PT_DRAFT.unlink(missing_ok=True)

    for path in (PT_DOCX, PT_PDF):
        print(f"  {path.name:52s} {path.stat().st_size / 1024:8.1f} KB")

    if EN_PACKAGE.exists():
        # Substring matching on "PT" is wrong: "ManuSCRIPT" contains "PT".
        # Compare against the exact expected journal manifest instead, which
        # also catches an unrelated file silently entering or leaving the
        # package.
        actual = {p.name for p in EN_PACKAGE.iterdir() if p.is_file()}
        if actual != EN_PACKAGE_MANIFEST:
            raise SystemExit(
                "English submission package drifted.\n"
                f"  unexpected: {sorted(actual - EN_PACKAGE_MANIFEST)}\n"
                f"  missing:    {sorted(EN_PACKAGE_MANIFEST - actual)}"
            )
        print(
            f"\nEnglish submission package intact "
            f"({len(actual)} files, exact manifest match)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
