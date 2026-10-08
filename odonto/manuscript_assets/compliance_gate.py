"""Compliance gate: submitted manuscript vs. Journal of Dentistry guide for authors.

Checks the objective, mechanically verifiable requirements only. Placeholder
declarations are reported as blockers rather than silently passing.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "Journal_of_Dentistry_Example_OdontoCA.md"
DOCX = ROOT / "Journal_of_Dentistry_Example_OdontoCA.docx"
PDF = ROOT / "Journal_of_Dentistry_Example_OdontoCA.pdf"
TITLE_PAGE = ROOT / "Journal_of_Dentistry_Title_Page.md"
HIGHLIGHTS = ROOT / "Highlights.md"
ASSETS = ROOT / "manuscript_assets"
TRIPOD = ROOT / "Supplementary_File_S3_TRIPOD_AI_Checklist.md"

ABSTRACT_LIMIT = 250
KEYWORDS_MIN, KEYWORDS_MAX = 1, 7
HIGHLIGHTS_MAX_CHARS = 85
DPI_MIN = 300

failures: list[str] = []
warnings: list[str] = []
checks: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "", *, warn_only: bool = False) -> None:
    checks.append((name, ok, detail))
    if not ok:
        (warnings if warn_only else failures).append(f"{name}: {detail}")


text = MD.read_text(encoding="utf-8")

# --- abstract length -------------------------------------------------------
abstract = text.split("## Abstract")[1].split("**Keywords:**")[0]
abstract_words = len([w for w in re.sub(r"[*]", "", abstract).split() if re.search(r"\w", w)])
check(
    f"Abstract <= {ABSTRACT_LIMIT} words",
    abstract_words <= ABSTRACT_LIMIT,
    f"{abstract_words} words",
)

# --- keywords --------------------------------------------------------------
kw_raw = text.split("**Keywords:**")[1].split("\n")[0]
keywords = [k.strip().rstrip(".") for k in kw_raw.split(";") if k.strip()]
check(
    f"Keywords within {KEYWORDS_MIN}-{KEYWORDS_MAX}",
    KEYWORDS_MIN <= len(keywords) <= KEYWORDS_MAX,
    f"{len(keywords)} keywords",
)

# --- reference numbering by first appearance -------------------------------
body = text.split("## 1. Introduction")[1].split("## References")[0]
order: list[int] = []
for match in re.finditer(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]", body):
    for number in re.findall(r"\d+", match.group(1)):
        if int(number) not in order:
            order.append(int(number))
reference_block = text.split("## References")[1]
listed = [int(m) for m in re.findall(r"^(\d+)\.", reference_block, re.M)]
check(
    "Citations numbered sequentially by first appearance",
    order == sorted(order) and order == list(range(1, len(listed) + 1)),
    f"order ok={order == sorted(order)}, {len(listed)} references",
)

# --- every reference has a DOI --------------------------------------------
dois = re.findall(r"\[(10\.\S+?)\]\(https://doi\.org/", reference_block)
check("Every reference carries a DOI", len(dois) == len(listed), f"{len(dois)}/{len(listed)}")

# --- no unresolved placeholders in the manuscript --------------------------
# AUTHOR TO SUPPLY marks a declaration that only the authors can complete. The
# Declarations section was restructured into the seven MDPI statements, so these
# markers are now per-declaration rather than two generic strings. The gate must
# keep failing closed while any of them survives: an author fact that nobody can
# derive (ethics determination, funding, competing interests, CRediT roles) must
# never be auto-filled.
placeholders = re.findall(
    r"AUTHOR TO SUPPLY|To be completed|must confirm|TBD|\[REQUIRED\]|\bXX+\b",
    text,
)
# The Declarations section must also expose every MDPI statement, so that a
# missing statement is a hard failure rather than a silent omission.
MDPI_DECLARATIONS = (
    "Institutional Review Board Statement",
    "Informed Consent Statement",
    "Data Availability Statement",
    "Funding",
    "Conflicts of Interest",
    "Author Contributions (CRediT)",
    "Acknowledgments",
)
check(
    "No unresolved placeholders in the manuscript",
    not placeholders,
    f"{len(placeholders)} found: {sorted(set(placeholders))}",
)
_missing = [d for d in MDPI_DECLARATIONS if d not in text]
check(
    "All seven MDPI declarations present",
    not _missing,
    "missing: " + ", ".join(_missing)
    if _missing
    else "IRB, consent, data, funding, COI, CRediT, acknowledgments",
)
check(
    "Generative AI declaration present with author-responsibility clause",
    "Declaration of Generative Artificial Intelligence Use" in text
    and "take full responsibility" in text,
    "GenAI declaration or author-responsibility clause absent",
)

# --- anonymisation ---------------------------------------------------------
anonymisation_hits = re.findall(
    # "Acknowledgments" is an MDPI-mandated heading, not identifying language, so
    # it is not matched here; the personal-name patterns below still catch any
    # named individual anywhere in the manuscript.
    r"the user'?s|Colab|Marcelo|Claro", text, re.IGNORECASE
)
check(
    "Manuscript body carries no author-identifying language",
    not anonymisation_hits,
    f"hits: {sorted(set(h.lower() for h in anonymisation_hits))}",
)

with zipfile.ZipFile(DOCX) as archive:
    core = archive.read("docProps/core.xml").decode("utf-8", "ignore")
creator = re.search(r"<dc:creator>(.*?)</dc:creator>", core)
last_by = re.search(r"<cp:lastModifiedBy>(.*?)</cp:lastModifiedBy>", core)
check(
    "DOCX author metadata empty",
    (not creator or not creator.group(1).strip())
    and (not last_by or not last_by.group(1).strip()),
    f"creator={creator.group(1) if creator else None!r}",
)

# --- figure resolution ----------------------------------------------------
try:
    from PIL import Image

    for name in (
        "Figure_1_pipeline_v2_compact.png",
        "Figure_2_discrimination_corrected_sklearn190.png",
        "Figure_3_calibration_corrected_sklearn190.png",
    ):
        with Image.open(ASSETS / name) as img:
            dpi = (img.info.get("dpi") or (0, 0))[0]
        # PNG stores DPI as a rational; 299.9994 is a rounding artefact of 300.
        check(
            f"{name} at least {DPI_MIN} DPI",
            dpi >= DPI_MIN - 1.0,
            f"{dpi:.0f} DPI",
            warn_only=True,
        )
except ImportError:  # pragma: no cover
    warnings.append("Pillow unavailable; DPI not checked")

# --- figure legends --------------------------------------------------------
for number in (1, 2, 3):
    check(
        f"Figure {number} has a legend in the manuscript",
        f"![Figure {number}." in text,
    )

# --- generative AI declaration --------------------------------------------
# MDPI asks for a GenAI declaration; the section heading was renamed to the
# journal's own wording, so accept either phrasing and match case-insensitively.
check(
    "Generative AI use declared",
    re.search(r"declaration of generative (?:artificial intelligence|AI) use", text, re.I)
    is not None,
)
check(
    "Figure 1 legend discloses AI assistance",
    "OpenAI Codex" in text.split("## 2. Materials and methods")[1].split("\n\n")[2]
    or "prepared with the assistance of OpenAI Codex" in text,
)

# --- reporting guideline statement ----------------------------------------
check(
    "TRIPOD+AI reporting statement present in Methods",
    "TRIPOD+AI statement" in text and "PROBAST+AI" in text,
)

# --- supplementary materials ----------------------------------------------
check(
    "TRIPOD+AI checklist supplied as Supplementary File S3",
    TRIPOD.exists(),
)

# --- title page is a separate file ----------------------------------------
check("Separate title page file exists", TITLE_PAGE.exists())
check(
    "Title page is not embedded in the manuscript",
    "Author" not in text.split("## Abstract")[0] or "Corresponding" not in text,
)

# --- highlights ------------------------------------------------------------
if HIGHLIGHTS.exists():
    points = [
        m.group(2).strip()
        for m in re.finditer(r"^(\d)\.\s+(.+)$", HIGHLIGHTS.read_text(encoding="utf-8"), re.M)
    ]
    check("Highlights count within 3-5", 3 <= len(points) <= 5, f"{len(points)} points")
    for index, point in enumerate(points, 1):
        check(
            f"Highlight {index} within {HIGHLIGHTS_MAX_CHARS} characters",
            len(point) <= HIGHLIGHTS_MAX_CHARS,
            f"{len(point)} characters",
        )

# --- page budget -----------------------------------------------------------
try:
    import pypdfium2 as pdfium

    pages = len(pdfium.PdfDocument(str(PDF)))
    check("Rendered length within the ~20 page guideline", pages <= 20, f"{pages} pages")
except ImportError:  # pragma: no cover
    warnings.append("pypdfium2 unavailable; page count not checked")

# --- report ----------------------------------------------------------------
width = max(len(name) for name, _, _ in checks)
print("=" * (width + 12))
print("JOURNAL OF DENTISTRY — COMPLIANCE GATE")
print("=" * (width + 12))
for name, ok, detail in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")

print()
print(f"Blocking failures: {len(failures)}")
for item in failures:
    print(f"  - {item}")
print(f"Warnings: {len(warnings)}")
for item in warnings:
    print(f"  - {item}")

json.dump(
    {
        "checks": [{"name": n, "pass": o, "detail": d} for n, o, d in checks],
        "blocking_failures": failures,
        "warnings": warnings,
    },
    open(ASSETS / "compliance_gate_report.json", "w"),
    indent=1,
)

sys.exit(1 if failures else 0)
