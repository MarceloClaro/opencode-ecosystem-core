"""Book Studio TeX — design de livro, projeto LaTeX, build e QA nativo.

R1111: o Core não embute TeX Live. Ele gera o projeto, invoca `latexmk`
externo e valida o PDF com `pypdf` (fallback) ou poppler quando existir.
Nenhum relatório aqui aprova estética, voz ou qualidade editorial.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

TRIM_RE = re.compile(r"^\s*([0-9.]+)\s*x\s*([0-9.]+)\s*(mm|cm|in)\s*$", re.I)
LANG_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9_-]{1,60}$")


class TexError(ValueError):
    """Erro de projeto, build ou QA TeX."""


def _positive(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TexError(f"{name} deve ser numérico")
    number = float(value)
    if number <= 0:
        raise TexError(f"{name} deve ser positivo")
    return number


def parse_trim(value: str) -> Tuple[float, float]:
    """Retorna (largura_mm, altura_mm). Aceita mm, cm e in."""
    match = TRIM_RE.match(str(value))
    if not match:
        raise TexError(f"trim inválido: {value!r}")
    width, height, unit = float(match.group(1)), float(match.group(2)), match.group(3).lower()
    factor = {"mm": 1.0, "cm": 10.0, "in": 25.4}[unit]
    width, height = width * factor, height * factor
    if not (70 <= width <= 400 and 100 <= height <= 500):
        raise TexError("trim fora da faixa editorial (70..400 x 100..500 mm)")
    return width, height


def format_trim(width_mm: float, height_mm: float) -> str:
    return f"{width_mm:g}x{height_mm:g}mm"


def escape_latex(text: str) -> str:
    """Escapa texto para uso em metadados/campos LaTeX (não em corpo)."""
    if not isinstance(text, str):
        raise TexError("texto deve ser string")
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


@dataclass(frozen=True)
class BookDesign:
    """Tokens de página e tipografia que alimentam o template TeX."""

    trim_width_mm: float = 160.0
    trim_height_mm: float = 230.0
    bleed_mm: float = 3.0
    margin_top_mm: float = 20.0
    margin_bottom_mm: float = 25.0
    margin_inner_mm: float = 22.0
    margin_outer_mm: float = 18.0
    body_font: str = "Libertinus Serif"
    sans_font: str = "Libertinus Sans"
    mono_font: str = "Libertinus Mono"
    body_pt: float = 11.0
    leading_pt: float = 14.5
    chapter_pt: float = 24.0
    section_pt: float = 14.0
    caption_pt: float = 9.0
    par_indent_em: float = 1.2
    language: str = "pt-BR"
    oldstyle_figures: bool = True
    microtype: bool = True
    two_sided: bool = True
    open_right: bool = True
    chapter_style: str = "veelo"
    toc: bool = True
    title_page: bool = True
    bibliography: bool = True
    index: bool = True
    numbered_sections: bool = False
    plots: bool = False
    keywords: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for name in ("trim_width_mm", "trim_height_mm", "bleed_mm", "margin_top_mm",
                     "margin_bottom_mm", "margin_inner_mm", "margin_outer_mm",
                     "body_pt", "leading_pt", "chapter_pt", "section_pt",
                     "caption_pt", "par_indent_em"):
            object.__setattr__(self, name, _positive(getattr(self, name), name))
        if not (70 <= self.trim_width_mm <= 400 and 100 <= self.trim_height_mm <= 500):
            raise TexError("trim fora da faixa editorial")
        if self.margin_inner_mm + self.margin_outer_mm >= self.trim_width_mm - 40:
            raise TexError("margens laterais deixam typeblock estreito demais")
        if self.margin_top_mm + self.margin_bottom_mm >= self.trim_height_mm - 60:
            raise TexError("margens verticais deixam typeblock baixo demais")
        if self.leading_pt < self.body_pt * 1.1:
            raise TexError("entrelinha deve ser ao menos 10% maior que o corpo")
        if self.chapter_pt <= self.body_pt or self.section_pt <= self.body_pt:
            raise TexError("títulos devem ser maiores que o corpo")
        if not LANG_RE.fullmatch(self.language):
            raise TexError("language inválida")
        for name in ("body_font", "sans_font", "mono_font"):
            if not getattr(self, name).strip():
                raise TexError(f"{name} não pode ser vazio")
        if not re.fullmatch(r"[a-z0-9-]{2,30}", self.chapter_style):
            raise TexError("chapter_style inválido")
        if any(not str(k).strip() for k in self.keywords):
            raise TexError("keywords não pode conter item vazio")

    @property
    def trim(self) -> str:
        return format_trim(self.trim_width_mm, self.trim_height_mm)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["keywords"] = list(self.keywords)
        data["trim"] = self.trim
        data["schema"] = "book-design/1"
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookDesign":
        if not isinstance(data, dict):
            raise TexError("design deve ser objeto")
        clean = {k: v for k, v in data.items()
                 if k in cls.__dataclass_fields__ and k != "keywords"}
        keywords = data.get("keywords") or ()
        if not isinstance(keywords, (list, tuple)):
            raise TexError("keywords deve ser lista")
        clean["keywords"] = tuple(str(k) for k in keywords)
        return cls(**clean)

    def latex_preamble(self) -> str:
        """Preâmbulo LaTeX (memoir + LuaLaTeX) derivado dos tokens."""
        width = self.trim_width_mm
        height = self.trim_height_mm
        # memoir aceita 10.5pt com extrafontsizes; 11pt é o padrão seguro.
        size_opt = "11pt"
        lines = [
            "% Gerado por MarceloClaro Book Studio (R1111). Não editar à mão.",
            f"\\documentclass[{size_opt},twoside{' ,openright' if self.open_right else ''}]{{memoir}}",
            f"\\setstocksize{{{height:g}mm}}{{{width:g}mm}}",
            f"\\settrimmedsize{{{height:g}mm}}{{{width:g}mm}}{{*}}",
            f"\\setlrmarginsandblock{{{self.margin_inner_mm:g}mm}}{{{self.margin_outer_mm:g}mm}}{{*}}",
            f"\\setulmarginsandblock{{{self.margin_top_mm:g}mm}}{{{self.margin_bottom_mm:g}mm}}{{*}}",
            "\\setheadfoot{14pt}{28pt}",
            "\\checkandfixthelayout",
            f"\\setlength{{\\parindent}}{{{self.par_indent_em:g}em}}",
            "\\setlength{\\parskip}{0pt}",
            "\\frenchspacing",
            "\\flushbottom",
            "\\widowpenalty=10000",
            "\\clubpenalty=10000",
            "\\displaywidowpenalty=10000",
            "\\brokenpenalty=10000",
            "\\usepackage{fontspec}",
        ]
        main_opts = ["Ligatures=TeX"]
        if self.oldstyle_figures:
            main_opts.append("Numbers=OldStyle")
        lines.append(f"\\setmainfont{{{self.body_font}}}[{', '.join(main_opts)}]")
        lines.append(f"\\setsansfont{{{self.sans_font}}}[Scale=MatchLowercase, Ligatures=TeX]")
        lines.append(f"\\setmonofont{{{self.mono_font}}}[Scale=MatchLowercase]")
        lines += [
            "\\usepackage[brazilian]{babel}",
            "\\selectlanguage{brazilian}",
        ]
        if self.microtype:
            lines.append("\\usepackage{microtype}")
        lines += [
            "\\usepackage[autostyle=true]{csquotes}",
            "\\usepackage{booktabs}",
            "\\usepackage{graphicx}",
            "\\usepackage{caption}",
            f"\\captionsetup{{font=small,labelfont=small}}",
            "\\usepackage{enumitem}",
            "\\usepackage{bookmark}",
        ]
        if self.plots:
            lines += ["\\usepackage{tikz}", "\\usepackage{pgfplots}"]
        if self.index:
            lines += ["\\usepackage{makeidx}", "\\makeindex"]
        lines += [
            f"\\chapterstyle{{{self.chapter_style}}}",
            "\\makepagestyle{book}",
            "\\makeevenhead{book}{\\small\\itshape\\leftmark}{}{\\small\\thepage}",
            "\\makeoddhead{book}{\\small\\thepage}{}{\\small\\itshape\\rightmark}",
            "\\makeevenfoot{book}{}{}{}",
            "\\makeoddfoot{book}{}{}{}",
            "\\pagestyle{book}",
        ]
        if not self.numbered_sections:
            lines.append("\\setsecnumdepth{none}")
        keywords = ", ".join(escape_latex(k) for k in self.keywords)
        hyper = [
            "hidelinks",
            f"pdflang={{{self.language}}}",
        ]
        lines.append("\\usepackage[" + ",".join(hyper) + "]{hyperref}")
        if keywords:
            lines.append(f"\\hypersetup{{pdfkeywords={{{keywords}}}}}")
        if self.bibliography:
            lines += [
                "\\usepackage[backend=biber,style=authoryear]{biblatex}",
                "\\IfFileExists{references.bib}{\\addbibresource{references.bib}}{}",
            ]
        return "\n".join(lines)


def render_main_tex(design: BookDesign, *, title: str, author: str,
                    publisher: str = "", edition: str = "1",
                    chapters: Sequence[str] = (),
                    subject: str = "") -> str:
    """Gera `main.tex` completo a partir dos tokens e do manifesto."""
    if not isinstance(title, str) or not title.strip():
        raise TexError("title obrigatório")
    if not isinstance(author, str) or not author.strip():
        raise TexError("author obrigatório")
    chapter_files = [c for c in chapters if c]
    for chapter in chapter_files:
        if not SAFE_NAME.fullmatch(chapter):
            raise TexError(f"nome de capítulo inseguro: {chapter!r}")
    lines = [design.latex_preamble(), ""]
    title_tex = escape_latex(title.strip())
    author_tex = escape_latex(author.strip())
    lines.append("\\hypersetup{")
    lines.append(f"  pdftitle={{{title_tex}}},")
    lines.append(f"  pdfauthor={{{author_tex}}},")
    if subject:
        lines.append(f"  pdfsubject={{{escape_latex(subject)}}},")
    lines.append("}")
    lines += ["", "\\begin{document}", "\\frontmatter"]
    if design.title_page:
        lines += [
            "\\begin{titlingpage}",
            "\\centering",
            "\\vspace*{30mm}",
            f"{{\\Huge\\bfseries {title_tex}\\par}}",
            "\\vspace{14mm}",
            f"{{\\Large {author_tex}\\par}}",
            "\\vfill",
        ]
        if publisher:
            lines.append(f"{{\\large {escape_latex(publisher)}\\par}}")
        if edition:
            lines.append(f"{{\\small {escape_latex(edition)}ª edição\\par}}")
        lines += ["\\end{titlingpage}"]
    if design.toc:
        lines += ["\\tableofcontents", "\\clearpage"]
    lines.append("\\mainmatter")
    for chapter in chapter_files:
        lines.append(f"\\input{{chapters/{chapter}}}")
    lines += ["\\backmatter"]
    if design.bibliography:
        lines += ["\\printbibliography[heading=bibintoc,title={Referências}]"]
    if design.index:
        lines += ["\\printindex"]
    lines += ["", "\\end{document}", ""]
    return "\n".join(lines)


def write_project(root: str | Path, design: BookDesign, *,
                  title: str, author: str, publisher: str = "",
                  edition: str = "1", chapters: Optional[Dict[str, str]] = None,
                  subject: str = "") -> Dict[str, Any]:
    """Cria um projeto LaTeX mínimo e retorna os caminhos escritos."""
    base = Path(root).expanduser().resolve()
    base.mkdir(parents=True, exist_ok=True)
    chapter_dir = base / "chapters"
    chapter_dir.mkdir(exist_ok=True)
    chapter_map = dict(chapters or {})
    if not chapter_map:
        chapter_map = {"01": "\\chapter{Capítulo de exemplo}\n\nTexto de exemplo.\n"}
    names = []
    for index, (name, body) in enumerate(chapter_map.items(), start=1):
        if not SAFE_NAME.fullmatch(str(name)):
            raise TexError(f"nome de capítulo inseguro: {name!r}")
        if not isinstance(body, str) or not body.strip():
            raise TexError(f"capítulo {name} vazio")
        (chapter_dir / f"{name}.tex").write_text(body.rstrip() + "\n", encoding="utf-8")
        names.append(str(name))
    main_tex = render_main_tex(design, title=title, author=author, publisher=publisher,
                               edition=edition, chapters=names, subject=subject)
    (base / "main.tex").write_text(main_tex, encoding="utf-8")
    if design.bibliography:
        bib = base / "references.bib"
        if not bib.exists():
            bib.write_text("% Referências do projeto (biblatex/biber).\n", encoding="utf-8")
    manifest = {
        "title": title, "author": author, "language": design.language,
        "edition": edition, "publisher": publisher, "trim": design.trim,
        "engine": "latex", "source": "main.tex",
        "chapters": [f"chapters/{name}.tex" for name in names],
        "output_formats": ["pdf"], "css": None,
    }
    (base / "book.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    design_path = base / "book-design.json"
    design_path.write_text(
        json.dumps(design.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"root": str(base), "main_tex": str(base / "main.tex"),
            "book_json": str(base / "book.json"),
            "design_json": str(design_path),
            "chapters": [str(chapter_dir / f"{name}.tex") for name in names]}


def compile_project(root: str | Path, *, timeout: int = 600,
                    jobname: str = "book") -> Dict[str, Any]:
    """Compila com latexmk/LuaLaTeX. Não instala nada e não usa shell."""
    base = Path(root).expanduser().resolve()
    main_tex = base / "main.tex"
    if not main_tex.is_file():
        raise TexError("main.tex ausente")
    latexmk = shutil.which("latexmk")
    if not latexmk:
        raise TexError(
            "latexmk ausente; instale TinyTeX (veja docs) ou use --engine typst")
    build = base / "build"
    build.mkdir(exist_ok=True)
    command = [
        latexmk, "-lualatex", "-interaction=nonstopmode", "-halt-on-error",
        "-file-line-error", f"-jobname={jobname}", f"-outdir={build}", "main.tex",
    ]
    try:
        result = subprocess.run(command, cwd=base, capture_output=True,
                                text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise TexError(f"latexmk excedeu {timeout}s") from exc
    pdf = build / f"{jobname}.pdf"
    log = build / f"{jobname}.log"
    return {
        "status": "completed" if result.returncode == 0 and pdf.is_file() else "failed",
        "returncode": result.returncode,
        "pdf": str(pdf) if pdf.is_file() else None,
        "log": str(log) if log.is_file() else None,
        "stdout_tail": (result.stdout or "")[-2000:],
        "stderr_tail": (result.stderr or "")[-2000:],
        "command": command,
    }


def parse_tex_log(path: str | Path, *, limit: int = 200) -> List[Dict[str, Any]]:
    """Extrai avisos acionáveis do .log do TeX."""
    log_path = Path(path)
    if not log_path.is_file():
        return [{"rule": "log_missing", "severity": "error", "line": None,
                 "detail": "arquivo .log ausente"}]
    text = log_path.read_text(encoding="utf-8", errors="replace")
    findings: List[Dict[str, Any]] = []

    def add(rule: str, severity: str, line: Optional[int], detail: str) -> None:
        if len(findings) < limit:
            findings.append({"rule": rule, "severity": severity,
                             "line": line, "detail": detail[:300]})

    over = re.compile(r"Overfull \\hbox \(([0-9.]+)pt too wide\).*?lines? (\d+)")
    under = re.compile(r"Underfull \\hbox.*?lines? (\d+)")
    for match in over.finditer(text):
        add("overfull_hbox", "warning", int(match.group(2)),
            f"{match.group(1)}pt além da caixa")
    for match in under.finditer(text):
        add("underfull_hbox", "warning", int(match.group(1)), "caixa subpreenchida")
    patterns = [
        ("undefined_reference", "error", re.compile(r"LaTeX Warning: Reference `([^']+)' .*?undefined")),
        ("undefined_citation", "error", re.compile(r"LaTeX Warning: Citation `([^']+)' .*?undefined")),
        ("missing_font", "error", re.compile(r"Font .*? not found")),
        ("biblatex_warning", "warning", re.compile(r"Package biblatex Warning: (.+)")),
        ("latex_error", "error", re.compile(r"^! (.+)$", re.M)),
    ]
    for rule, severity, pattern in patterns:
        for match in pattern.finditer(text):
            detail = match.group(1) if match.groups() else match.group(0)
            add(rule, severity, None, detail.strip())
    return findings


def _pdf_trim_mm(trim: str | None) -> Optional[Tuple[float, float]]:
    if not trim:
        return None
    try:
        return parse_trim(trim)
    except TexError:
        return None


def qa_pdf_native(path: str | Path, *, trim: str | None = None) -> Dict[str, Any]:
    """QA de PDF sem poppler: pypdf para páginas, trim, metadados, fontes e texto."""
    pdf_path = Path(path)
    if not pdf_path.is_file() or pdf_path.stat().st_size <= 0:
        raise TexError("PDF ausente ou vazio")
    try:
        from pypdf import PdfReader
    except Exception as exc:  # pragma: no cover - dependência opcional
        raise TexError("pypdf ausente; instale pypdf ou use poppler") from exc
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        return {"status": "error", "pdf": str(pdf_path), "issues": ["pdf_unreadable"],
                "detail": str(exc)[:200], "human_review_required": True,
                "external_validation": False}
    issues: List[str] = []
    pages = len(reader.pages)
    if pages <= 0:
        issues.append("no_pages")
    if reader.is_encrypted:
        issues.append("encrypted")
    width_mm = height_mm = None
    if pages:
        box = reader.pages[0].mediabox
        width_mm = float(box.width) * 25.4 / 72.0
        height_mm = float(box.height) * 25.4 / 72.0
        expected = _pdf_trim_mm(trim)
        if expected:
            exp_w, exp_h = expected
            if abs(width_mm - exp_w) > 0.6 or abs(height_mm - exp_h) > 0.6:
                issues.append("page_size_mismatch")
    metadata = reader.metadata or {}
    title = metadata.get("/Title") if hasattr(metadata, "get") else None
    author = metadata.get("/Author") if hasattr(metadata, "get") else None
    subject = metadata.get("/Subject") if hasattr(metadata, "get") else None
    if not title:
        issues.append("metadata_missing_title")
    if not author:
        issues.append("metadata_missing_author")
    fonts: Dict[str, Dict[str, Any]] = {}
    text_chars = 0
    for page in reader.pages:
        try:
            text_chars += len((page.extract_text() or "").strip())
        except Exception:
            pass
        resources = page.get("/Resources")
        if not resources:
            continue
        try:
            font_dict = resources.get("/Font") or {}
        except Exception:
            continue
        for _, font_ref in font_dict.items():
            try:
                font = font_ref.get_object()
                base = str(font.get("/BaseFont", "?"))
                descriptor = font.get("/FontDescriptor")
                embedded = False
                if descriptor:
                    descriptor = descriptor.get_object()
                    embedded = any(key in descriptor for key in
                                   ("/FontFile", "/FontFile2", "/FontFile3"))
                fonts.setdefault(base, {"embedded": embedded, "subtype": str(font.get("/Subtype", "?"))})
            except Exception:
                continue
    not_embedded = sorted(name for name, data in fonts.items() if not data["embedded"])
    if not_embedded:
        issues.append("fonts_not_embedded")
    if text_chars == 0:
        issues.append("empty_text")
    return {
        "status": "completed", "pdf": str(pdf_path), "pages": pages,
        "page_size_mm": [round(width_mm, 2), round(height_mm, 2)] if width_mm else None,
        "title": str(title) if title else None,
        "author": str(author) if author else None,
        "subject": str(subject) if subject else None,
        "fonts": {"total": len(fonts), "not_embedded": not_embedded,
                  "names": sorted(fonts)[:40]},
        "text_chars": text_chars, "issues": issues,
        "human_review_required": True, "external_validation": False,
        "engine": "pypdf",
        "limitations": [
            "QA técnico não avalia estética, tipografia ou voz.",
            "Fontes embutidas não provam licença de uso.",
            "PDF/UA, PDF/X, sangria e TAC exigem validação externa.",
        ],
    }
