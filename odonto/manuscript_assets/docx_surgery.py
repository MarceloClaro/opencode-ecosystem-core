#!/usr/bin/env python3
"""In-place, template-preserving edits to the MDPI DOCX deliverable.

Why this exists
---------------
`submission_package/Manuscript_MDPI_Dentistry_Revised_marginfix.docx` was
produced by LibreOffice from the MDPI `dentistry-template.dotx`, not from a
Markdown source. Rebuilding it through the Markdown -> pandoc path would discard
the journal template styling, the section numbering, and the table layout, so the
document is edited directly in its OOXML part instead. Only `word/document.xml` is
touched; every other zip entry is copied through byte for byte.

Text replacement is run-aware: a target phrase may straddle several `<w:t>`
elements, so the replacement is applied positionally across the runs that cover
it, and runs outside the target are left byte-identical. Formatting is therefore
preserved rather than flattened.

Usage:
    python3 manuscript_assets/docx_surgery.py <docx> [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

DOC_PART = "word/document.xml"
# `<w:t[^>]*>` would also match <w:tbl>, <w:tc> and <w:tr>, letting the non-greedy
# body swallow whole tables and get escaped into literal text. The tag name must
# therefore be followed by whitespace or the closing angle bracket.
W_T = re.compile(r"(<w:t(?:\s[^>]*)?>)(.*?)(</w:t>)", re.S)
PARA = re.compile(r"<w:p[ >].*?</w:p>", re.S)

# Structural elements that must survive the edit untouched. Their counts are
# compared before and after, so a regex that starts eating tables is caught
# before anything is written.
STRUCTURAL = (
    "<w:tbl>", "</w:tbl>", "<w:tc>", "<w:tr>", "<w:drawing>",
    "<wp:extent", "<w:hyperlink", "<w:bookmarkStart",
)


def unescape(text: str) -> str:
    return (
        text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&amp;", "&")
    )


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def para_text(p_xml: str) -> str:
    return "".join(unescape(m.group(2)) for m in W_T.finditer(p_xml))


def replace_in_paragraph(p_xml: str, old: str, new: str) -> tuple[str, bool]:
    """Replace `old` with `new` inside one paragraph, spanning run boundaries.

    Runs that the target does not touch are re-emitted with their original raw
    text, so existing entity escaping (`&amp;` in "Cell Host &amp; Microbe") is
    preserved verbatim instead of being decoded and re-encoded.
    """
    matches = list(W_T.finditer(p_xml))
    raw = [m.group(2) for m in matches]
    full = "".join(unescape(r) for r in raw)
    idx = full.find(old)
    if idx < 0:
        return p_xml, False
    end = idx + len(old)

    out: list[str] = []
    cursor = 0
    for m, r in zip(matches, raw):
        text = unescape(r)
        start, stop = cursor, cursor + len(text)
        cursor = stop
        if stop <= idx or start >= end:
            out.append(m.group(1) + r + m.group(3))
            continue
        head = text[: idx - start] if start < idx else ""
        tail = text[end - start :] if stop > end else ""
        out.append(m.group(1) + escape(head + new + tail) + m.group(3))

    rebuilt, last = [], 0
    for m, piece in zip(matches, out):
        rebuilt.append(p_xml[last : m.start()])
        rebuilt.append(piece)
        last = m.end()
    rebuilt.append(p_xml[last:])
    return "".join(rebuilt), True


def prefix_paragraph(p_xml: str, prefix: str) -> str:
    """Insert `prefix` at the very start of a paragraph's text.

    The existing run text is kept raw: decoding it here previously emitted a bare
    `&` for references such as "Cell Host & Microbe" and produced invalid XML.
    """
    m = W_T.search(p_xml)
    if not m:
        return p_xml
    return p_xml[: m.start(2)] + escape(prefix) + m.group(2) + p_xml[m.end(2) :]


def edit_document(xml: str, *, dry_run: bool) -> tuple[str, list[str]]:
    log: list[str] = []

    # -- 1. "version-locked" -> "version-frozen", and the conservative reframe ----
    # The freeze is retrospective: the hyperparameter and the recalibration form
    # were both chosen on the development cohort. Saying only "locked" invites a
    # reviewer to read a prospective prespecification that did not happen.
    wordwise = [
        ("Version-Locked", "Version-Frozen"),
        ("version-locked", "version-frozen"),
        ("Locking procedure", "Freezing procedure"),
        ("Locking an artifact", "Freezing an artifact"),
        ("Locking the final model", "Freezing the final model"),
        ("before locking", "before freezing"),
        # "lock" is correct when it describes a *prospective* next step; naming it
        # explicitly keeps it from reading as another retrospective freeze.
        (
            "should lock the clinical-spatial",
            "should prospectively lock the clinical-spatial",
        ),
        ("lock timestamp", "freeze timestamp"),
        ("Locked", "Frozen"),
        ("locked", "frozen"),
    ]
    for old, new in wordwise:
        n = xml.count(old)
        if n:
            xml = xml.replace(old, new)
            log.append(f"wordwise {old!r} -> {new!r}: {n} occurrence(s)")

    targeted = [
        (
            "The frozen primary model is the clinical-minimal set.",
            "The designated primary model for external evaluation is the clinical-minimal set.",
        ),
        (
            "was therefore frozen as a secondary exploratory candidate",
            "was therefore designated as a secondary exploratory candidate",
        ),
    ]
    for old, new in targeted:
        if old in xml:
            xml = xml.replace(old, new)
            log.append(f"targeted: {old[:52]}...")
        else:
            log.append(f"TARGETED NOT FOUND: {old[:52]}...")

    # -- 2. state explicitly what the freeze does and does not establish ---------
    caveat = (
        " The freeze was retrospective: it followed inspection of the development "
        "results and did not constitute prospective model prespecification. "
        "Throughout this manuscript, version-frozen means only that the artifact, "
        "its recorded hash, and its inference settings will not change before "
        "external scoring; it does not mean that the model was selected without "
        "reference to the development data. Because both the regularisation value "
        "and the recalibration form were selected using the development cohort, the "
        "artifact is an exploratory model frozen for reproducibility and audit, and "
        "its apparent performance must not be reported as independent performance."
    )
    anchor = (
        "Freezing an artifact does not constitute validation and does not justify "
        "clinical deployment."
    )
    if caveat.strip() not in xml:
        if anchor in xml:
            xml = xml.replace(anchor, anchor + caveat, 1)
            log.append("inserted retrospective-freeze caveat in section 2.5")
        else:
            log.append("CAVEAT ANCHOR NOT FOUND")

    # -- 3. number the reference list -------------------------------------------
    # MDPI numbers references in order of appearance and matches them to the
    # in-text brackets. The in-text citations already run [1]-[30] in first-
    # appearance order, but the list paragraphs carried no numbers at all.
    paras = PARA.findall(xml)
    ref_start = None
    for i, p in enumerate(paras):
        if para_text(p).strip() == "References":
            ref_start = i
            break
    if ref_start is None:
        log.append("REFERENCES HEADING NOT FOUND")
        return xml, log

    numbered = 0
    rebuilt_paras = list(paras)
    n = 0
    for i in range(ref_start + 1, len(paras)):
        text = para_text(paras[i]).strip()
        if not text:
            continue
        if re.match(r"^\[\d+\]", text):
            continue
        n += 1
        rebuilt_paras[i] = prefix_paragraph(paras[i], f"[{n}] ")
        numbered += 1
    log.append(f"numbered {numbered} reference entries as [1]-[{n}]")

    xml = PARA.sub(lambda m: rebuilt_paras.pop(0) if rebuilt_paras else m.group(0), xml)
    if dry_run:
        log.append("(dry run: nothing written)")
    return xml, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.docx.exists():
        print(f"not found: {args.docx}", file=sys.stderr)
        return 1

    with zipfile.ZipFile(args.docx) as zf:
        entries = [(i, zf.read(i.filename)) for i in zf.infolist()]

    document = next(d for i, d in entries if i.filename == DOC_PART)
    before = document.decode("utf-8")
    new_xml, log = edit_document(before, dry_run=args.dry_run)
    print(f"== {args.docx.name} ==")
    for line in log:
        print("  -", line)

    if args.dry_run:
        return 0

    # --- fail-closed guards --------------------------------------------------
    # A DOCX that does not parse, or that lost a table, is worse than no edit.
    from xml.dom import minidom

    try:
        minidom.parseString(new_xml)
    except Exception as exc:  # noqa: BLE001
        print(f"ABORT: edited XML is not well-formed: {exc}", file=sys.stderr)
        return 2
    lost = [t for t in STRUCTURAL if before.count(t) != new_xml.count(t)]
    if lost:
        print(f"ABORT: structural elements changed: {lost}", file=sys.stderr)
        return 3
    print("  guards: XML well-formed, structure preserved")

    backup = args.docx.with_suffix(".pre-surgery.docx")
    if not backup.exists():
        shutil.copy2(args.docx, backup)
        print(f"  backup -> {backup.name}")

    tmp = args.docx.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for info, data in entries:
            out.writestr(
                info,
                new_xml.encode("utf-8") if info.filename == DOC_PART else data,
            )
    tmp.replace(args.docx)
    print("  written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())