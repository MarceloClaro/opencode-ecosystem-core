"""R1053-B — pacote de submissão a partir do manuscrito validado.

Gera Markdown, LaTeX e DOCX quando as ferramentas existem, um `.bib`
auxiliar, template ABNT genérico, checklist de periódico, declarações
pendentes de humano e manifesto com hashes.

O módulo não declara conformidade ABNT, aceite editorial ou publicação. Um
template genérico não substitui as regras do periódico-alvo.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from scientific_lab import journal_profiles
from scientific_lab.native.common import dump, load, now, sha256_file

SCHEMA_VERSION = "1.0"
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".svg", ".csv", ".tex"}
MAX_ASSET_BYTES = 50_000_000

ABNT_TEMPLATE = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{mathptmx}
\usepackage{setspace}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\usepackage{graphicx}
\usepackage{array}
\usepackage{calc}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{hyperref}
\onehalfspacing
\setlength{\parindent}{1.25cm}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\begin{document}
$body$
\end{document}
"""

DECLARATION_FIELDS = (
    "ethics", "consent", "conflicts", "funding", "data_availability",
    "author_contributions", "ai_use", "orcid",
)

CHECKLIST_ITEMS = (
    ("title", "Título"),
    ("abstract", "Resumo/abstract"),
    ("keywords", "Palavras-chave"),
    ("main_text", "Texto principal"),
    ("references", "Referências"),
    ("figures", "Figuras"),
    ("tables", "Tabelas"),
    ("ethics", "Ética e consentimento"),
    ("conflicts", "Conflitos de interesse"),
    ("funding", "Financiamento"),
    ("data_availability", "Disponibilidade de dados"),
    ("author_contributions", "Contribuição dos autores"),
    ("orcid", "ORCID"),
    ("ai_use", "Uso de IA"),
    ("cover_letter", "Carta de submissão"),
    ("supplementary", "Material suplementar"),
    ("word_count", "Contagem de palavras"),
    ("formatting", "Formatação do periódico"),
    ("submission_system", "Sistema de submissão"),
)


def _latex_escape(value: object) -> str:
    text = str(value or "")
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def build_bib(references: dict) -> str:
    entries = []
    for index, record in enumerate(references.get("records") or [], start=1):
        authors = record.get("authors") or []
        author_text = " and ".join(str(item) for item in authors) if authors else "Autoria não informada"
        title = record.get("title") or "Título não informado"
        year = record.get("year") or "s.d."
        venue = record.get("venue") or "Veículo não informado"
        doi = record.get("doi")
        url = record.get("url")
        lines = [
            f"@article{{ref{index:03d},",
            f"  author = {{{_latex_escape(author_text)}}},",
            f"  title = {{{{{_latex_escape(title)}}}}},",
            f"  year = {{{_latex_escape(year)}}},",
            f"  journal = {{{_latex_escape(venue)}}},",
        ]
        if doi:
            lines.append(f"  doi = {{{_latex_escape(doi)}}},")
        if url:
            lines.append(f"  url = {{{_latex_escape(url)}}},")
        lines.append("}")
        entries.append("\n".join(lines))
    return "\n\n".join(entries) + ("\n" if entries else "")


def journal_checklist(journal: str | None) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "journal": journal or "não informado",
        "generated_at": now(),
        "status": "pending_human",
        "items": [
            {
                "id": item_id,
                "label": label,
                "status": "pending_human",
                "evidence": None,
                "reason": "regra do periódico não inferida pelo pipeline",
            }
            for item_id, label in CHECKLIST_ITEMS
        ],
        "policy": "journal_rules_not_inferred",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "O checklist é genérico e não substitui as instruções do periódico.",
            "Nenhum item foi marcado como cumprido sem decisão humana.",
        ],
    }


def declarations() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pending_human",
        "fields": {
            field: {"status": "pending_human", "value": None}
            for field in DECLARATION_FIELDS
        },
        "truth_claim": False,
        "human_review_required": True,
        "limitations": [
            "Declarações éticas, de conflito, financiamento e IA devem ser preenchidas por humano.",
            "O pipeline não inventa aprovação ética, consentimento ou contribuição autoral.",
        ],
    }


def _declarations_markdown(data: dict) -> str:
    lines = [
        "# Declarações — PENDENTE_HUMANO",
        "",
        "Preencha cada campo antes da submissão. Nenhum valor foi inferido.",
        "",
        "| Campo | Estado | Valor |",
        "|---|---|---|",
    ]
    for field, item in data["fields"].items():
        lines.append(f"| {field} | {item['status']} | não preenchido |")
    lines.append("")
    return "\n".join(lines)


def _cover_letter(journal: str | None, title: str) -> str:
    return "\n".join([
        "# Carta de submissão — PENDENTE_HUMANO",
        "",
        f"**Periódico:** {journal or 'não informado'}",
        f"**Manuscrito:** {title}",
        "",
        "Preencher:",
        "",
        "- nome e afiliação do autor correspondente;",
        "- contribuição dos autores;",
        "- declaração de originalidade e não submissão simultânea;",
        "- conflitos de interesse;",
        "- financiamento;",
        "- aprovação ética e consentimento, quando aplicável;",
        "- uso de IA, quando aplicável.",
        "",
        "Esta carta é um template; não contém declaração factual inventada.",
        "",
    ])


def _copy_assets(source: str | Path | None, dest: Path) -> list[dict]:
    if source is None:
        return []
    root = Path(source).expanduser().resolve()
    if not root.exists():
        return []
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ASSET_SUFFIXES:
            continue
        size = path.stat().st_size
        if total + size > MAX_ASSET_BYTES:
            copied.append({
                "source": str(path),
                "copied": False,
                "reason": "limite de 50 MB excedido",
            })
            continue
        target = dest / path.name
        shutil.copy2(path, target)
        total += size
        copied.append({
            "source": str(path),
            "copied": True,
            "path": target.relative_to(dest.parent).as_posix(),
            "sha256": sha256_file(target),
            "bytes": size,
        })
    return copied


def _run_tool(command: list[str], cwd: Path, timeout: int = 180) -> dict:
    try:
        completed = subprocess.run(
            command, cwd=str(cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }
    if completed.returncode != 0:
        return {
            "status": "failed",
            "returncode": completed.returncode,
            "stderr": (completed.stderr or "")[-1500:],
            "stdout": (completed.stdout or "")[-500:],
        }
    return {"status": "generated", "returncode": 0}


def _clean_latex_aux(root: Path, *, keep_log: bool) -> None:
    for suffix in (".aux", ".fdb_latexmk", ".fls", ".out", ".toc", ".bbl", ".blg", ".synctex.gz"):
        for path in root.glob(f"*{suffix}"):
            path.unlink()
    if not keep_log:
        for path in root.glob("*.log"):
            path.unlink()


def _collect_files(root: Path) -> list[dict]:
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "submission-manifest.json":
            continue
        files.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })
    return files


def build(
    out: str | Path,
    *,
    journal: str | None = None,
    journal_profile_id: str | None = None,
    figures_dir: str | Path | None = None,
    tables_dir: str | Path | None = None,
    compile_pdf: bool = True,
) -> dict:
    out = Path(out).resolve()
    manuscript = out / "06_manuscript/manuscript.md"
    if not manuscript.exists():
        raise ValueError("manuscrito ausente; rode o pipeline antes da submissão")
    sub = out / "10_submission"
    sub.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manuscript, sub / "manuscript.md")

    profile = (
        journal_profiles.load_profile(journal_profile_id)
        if journal_profile_id else None
    )
    if profile is not None:
        journal = profile["name"]
    compliance = (
        journal_profiles.validate_manuscript(manuscript, profile)
        if profile is not None else None
    )
    if compliance is not None:
        dump(sub / "journal-compliance.json", compliance)
        checklist = journal_profiles.checklist(profile, compliance)
    else:
        checklist = journal_checklist(journal)
    dump(sub / "journal-checklist.json", checklist)

    references_path = out / "06_manuscript/references.json"
    references = load(references_path) if references_path.exists() else {"records": []}
    (sub / "references.bib").write_text(build_bib(references), encoding="utf-8")
    decl = declarations()
    dump(sub / "declarations.json", decl)
    (sub / "declarations.md").write_text(
        _declarations_markdown(decl), encoding="utf-8",
    )
    title = next(
        (
            line.lstrip("# ").strip()
            for line in manuscript.read_text(encoding="utf-8").splitlines()
            if line.startswith("# ")
        ),
        "Título não informado",
    )
    (sub / "cover-letter.md").write_text(
        _cover_letter(journal, title), encoding="utf-8",
    )
    (sub / "abnt-template.tex").write_text(ABNT_TEMPLATE, encoding="utf-8")

    figures = _copy_assets(figures_dir, sub / "figures")
    figures += _copy_assets(out / "06_manuscript/figures", sub / "figures")
    tables = _copy_assets(tables_dir, sub / "tables")
    tables += _copy_assets(out / "06_manuscript/tables", sub / "tables")

    pandoc = shutil.which("pandoc")
    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")
    latex_status = {"status": "unavailable", "reason": "pandoc ausente"}
    docx_status = {"status": "unavailable", "reason": "pandoc ausente"}
    if pandoc:
        latex_status = _run_tool(
            [
                pandoc, "manuscript.md", "-o", "manuscript.tex",
                "--standalone", "--template=abnt-template.tex",
            ],
            sub,
        )
        docx_status = _run_tool(
            [pandoc, "manuscript.md", "-o", "manuscript.docx"],
            sub,
        )
    pdf_status = {"status": "unavailable", "reason": "manuscrito.tex ausente"}
    if compile_pdf and (sub / "manuscript.tex").exists():
        if latexmk:
            pdf_status = _run_tool(
                [
                    latexmk, "-pdf", "-interaction=nonstopmode",
                    "-halt-on-error", "manuscript.tex",
                ],
                sub,
            )
        elif pdflatex:
            pdf_status = _run_tool(
                [
                    pdflatex, "-interaction=nonstopmode",
                    "-halt-on-error", "manuscript.tex",
                ],
                sub,
            )
        else:
            pdf_status = {
                "status": "unavailable",
                "reason": "latexmk/pdflatex ausentes",
            }
    elif not compile_pdf:
        pdf_status = {"status": "skipped", "reason": "compile_pdf=false"}

    _clean_latex_aux(sub, keep_log=pdf_status.get("status") == "failed")

    readme = "\n".join([
        "# Pacote de submissão",
        "",
        f"**Periódico:** {journal or 'não informado'}",
        "",
        "| Item | Estado |",
        "|---|---|",
        f"| Markdown | copiado |",
        f"| LaTeX | `{latex_status['status']}` |",
        f"| DOCX | `{docx_status['status']}` |",
        f"| PDF | `{pdf_status['status']}` |",
        f"| Perfil | `{journal_profile_id or 'genérico'}` |",
        f"| Conformidade | `{compliance['status'] if compliance else 'não avaliada'}` |",
        f"| Checklist | `{checklist['status']}` |",
        f"| Declarações | `{decl['status']}` |",
        "",
        "O template ABNT é genérico e não certifica conformidade com norma ou",
        "periódico. O checklist e as declarações exigem preenchimento humano.",
        "Um perfil real transcreve regras públicas, mas não garante aceite.",
        "",
    ])
    (sub / "README.md").write_text(readme, encoding="utf-8")

    files = _collect_files(sub)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "journal": journal or "não informado",
        "journal_profile_id": journal_profile_id,
        "journal_compliance": compliance["status"] if compliance else None,
        "status": (
            "partial" if pdf_status["status"] == "failed"
            else "completed" if latex_status["status"] == "generated"
            or docx_status["status"] == "generated"
            else "partial"
        ),
        "tools": {
            "pandoc": bool(pandoc),
            "latexmk": bool(latexmk),
            "pdflatex": bool(pdflatex),
        },
        "latex": latex_status,
        "docx": docx_status,
        "pdf": pdf_status,
        "figures": figures,
        "tables": tables,
        "files": files,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Template ABNT genérico; não substitui a norma do periódico.",
            "Checklist e declarações permanecem pending_human.",
            "Conversão para LaTeX/DOCX/PDF depende das ferramentas locais.",
            "Nada foi submetido ou publicado.",
        ],
    }
    dump(sub / "submission-manifest.json", manifest)
    return {
        "status": manifest["status"],
        "out": str(sub),
        "journal": manifest["journal"],
        "latex": latex_status["status"],
        "docx": docx_status["status"],
        "pdf": pdf_status["status"],
        "files": len(files),
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
    }


def run(out: str | Path, **kwargs) -> dict:
    return build(out, **kwargs)
