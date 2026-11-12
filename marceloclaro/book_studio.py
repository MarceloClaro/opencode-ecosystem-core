"""R1071 — Book Studio: manifesto, build e QA de livros.

Motores internos: Typst (padrão), Pandoc/LaTeX e WeasyPrint. Scribus,
Vivliostyle e CaSILE são motores externos: o Studio verifica presença e devolve
handoff, sem copiar código GPL/AGPL para o Core.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
TYPST_BIN = Path.home() / ".local/share/opencode-core/typst/typst"
BOOK_FILE = "book.json"
ENGINES = ("typst", "pandoc", "weasyprint", "latex", "scribus", "vivliostyle", "casile")
FORMATS = ("pdf", "epub")
TRIM_RE = re.compile(r"^(?P<w>\d+(?:\.\d+)?)x(?P<h>\d+(?:\.\d+)?)(?P<unit>in|mm)$")
LANG_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


class BookError(ValueError):
    pass


def _text(value: Any, name: str, limit: int = 500) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise BookError(f"{name} deve conter 1..{limit} caracteres")
    return value.strip()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug[:80] or "livro"


def _typst_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _typst_text(value: str) -> str:
    """Escapa markup Typst básico em títulos e nomes."""
    return re.sub(r"([\\#\[\]$*_`<>@])", r"\\\1", value)


def _trim(value: str) -> tuple[float, float]:
    match = TRIM_RE.fullmatch(value)
    if not match:
        raise BookError("trim deve ser LARGURAxALTURA em in ou mm (ex.: 6x9in)")
    width, height = float(match.group("w")), float(match.group("h"))
    if match.group("unit") == "mm":
        width, height = width / 25.4, height / 25.4
    if not 3 <= width <= 15 or not 4 <= height <= 18:
        raise BookError("trim fora da faixa editorial de 3..15 x 4..18 polegadas")
    return width, height


@dataclass(frozen=True)
class BookManifest:
    title: str
    author: str
    language: str = "pt-BR"
    edition: str = "1"
    publisher: str = ""
    trim: str = "6x9in"
    engine: str = "typst"
    source: str | None = None
    chapters: tuple[str, ...] = ()
    output_formats: tuple[str, ...] = ("pdf",)
    css: str | None = None

    def __post_init__(self) -> None:
        _text(self.title, "title", 300)
        _text(self.author, "author", 200)
        if not LANG_RE.fullmatch(self.language):
            raise BookError("language inválida")
        _text(self.edition, "edition", 40)
        if self.publisher:
            _text(self.publisher, "publisher", 200)
        _trim(self.trim)
        if self.engine not in ENGINES:
            raise BookError(f"engine deve ser uma de {ENGINES}")
        if self.source is not None:
            _text(self.source, "source", 300)
            if not self.source.casefold().endswith(".tex"):
                raise BookError("source deve apontar para um .tex")
        if self.engine == "latex" and not self.source:
            raise BookError("engine latex exige source")
        minimum = 0 if self.engine == "latex" else 1
        if not isinstance(self.chapters, tuple) or not minimum <= len(self.chapters) <= 200:
            raise BookError(f"chapters deve ter {minimum}..200 entradas")
        for chapter in self.chapters:
            _text(chapter, "chapter", 300)
        if not isinstance(self.output_formats, tuple) or not self.output_formats:
            raise BookError("output_formats não pode ser vazio")
        if any(item not in FORMATS for item in self.output_formats):
            raise BookError("output_formats aceita pdf e/ou epub")
        if self.css is not None:
            _text(self.css, "css", 300)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title, "author": self.author, "language": self.language,
            "edition": self.edition, "publisher": self.publisher, "trim": self.trim,
            "engine": self.engine, "source": self.source,
            "chapters": list(self.chapters),
            "output_formats": list(self.output_formats), "css": self.css,
        }


def load_manifest(root: str | Path) -> BookManifest:
    root = Path(root).expanduser().resolve()
    target = root / BOOK_FILE
    if not target.is_file():
        raise BookError("book.json ausente")
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BookError("book.json ilegível") from exc
    if not isinstance(data, dict):
        raise BookError("book.json deve ser objeto")
    allowed = {"title", "author", "language", "edition", "publisher", "trim",
               "engine", "source", "chapters", "output_formats", "css"}
    if set(data) - allowed:
        raise BookError("book.json contém chaves desconhecidas")
    if not isinstance(data.get("chapters"), list) or not isinstance(
            data.get("output_formats", ["pdf"]), list):
        raise BookError("chapters/output_formats devem ser listas")
    return BookManifest(
        title=data.get("title", ""), author=data.get("author", ""),
        language=data.get("language", "pt-BR"),
        edition=data.get("edition", "1"), publisher=data.get("publisher", ""),
        trim=data.get("trim", "6x9in"), engine=data.get("engine", "typst"),
        source=data.get("source"), chapters=tuple(data.get("chapters", [])),
        output_formats=tuple(data.get("output_formats", ["pdf"])),
        css=data.get("css"),
    )


def save_manifest(root: str | Path, manifest: BookManifest) -> Path:
    root = Path(root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / BOOK_FILE
    target.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return target


def chapter_paths(root: str | Path, manifest: BookManifest) -> List[Path]:
    root = Path(root).expanduser().resolve()
    rows = []
    for relative in manifest.chapters:
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise BookError(f"capítulo fora da raiz: {relative}")
        target = (root / relative).resolve()
        if not str(target).startswith(str(root) + os.sep):
            raise BookError(f"capítulo fora da raiz: {relative}")
        if target.is_symlink() or not target.is_file():
            raise BookError(f"capítulo ausente ou symlink: {relative}")
        if target.suffix.casefold() not in {".md", ".markdown", ".txt"}:
            raise BookError(f"extensão de capítulo não suportada: {relative}")
        rows.append(target)
    return rows


def _binary(name: str) -> str | None:
    if name == "typst":
        if TYPST_BIN.is_file() and os.access(TYPST_BIN, os.X_OK):
            return str(TYPST_BIN)
        return shutil.which("typst")
    if name == "latex":
        return shutil.which("latexmk") or shutil.which("pdflatex")
    return shutil.which(name)


def _version(path: str) -> str | None:
    for flag in ("--version", "-version"):
        try:
            result = subprocess.run([path, flag], capture_output=True, text=True,
                                    timeout=10, shell=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0:
            return (result.stdout or result.stderr).strip().splitlines()[0][:160]
    return None


def status(root: str | Path | None = None) -> Dict[str, Any]:
    engines = {}
    for name in ENGINES:
        path = _binary(name)
        engines[name] = {"available": bool(path), "path": path,
                         "version": _version(path) if path else None}
    qa_tools = {name: bool(shutil.which(name)) for name in
                ("pdfinfo", "pdffonts", "pdftotext")}
    build_capable = [name for name in ("typst", "pandoc", "weasyprint", "latex")
                     if engines[name]["available"]]
    payload: Dict[str, Any] = {
        "status": "ready" if build_capable else "blocked",
        "engines": engines, "qa_tools": qa_tools,
        "default_engine": build_capable[0] if build_capable else "typst",
        "external_engines": ["scribus", "vivliostyle", "casile"],
        "policy": "motores GPL/AGPL permanecem externos; sem cópia para o Core",
        "external_validation": False,
    }
    if root is not None:
        try:
            manifest = load_manifest(root)
            payload["project"] = {"root": str(Path(root).expanduser().resolve()),
                                  "manifest": manifest.to_dict(),
                                  "chapters": len(manifest.chapters)}
        except BookError as exc:
            payload["project"] = {"error": str(exc)}
    return payload


def _run(argv: List[str], timeout: int, cwd: Path | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(argv, capture_output=True, timeout=timeout,
                            shell=False, cwd=str(cwd) if cwd else None)
    stdout = (result.stdout or b"").decode("utf-8", "replace")
    stderr = (result.stderr or b"").decode("utf-8", "replace")
    return subprocess.CompletedProcess(result.args, result.returncode, stdout, stderr)


def _typst_source(root: Path, manifest: BookManifest,
                  chapters: List[Path]) -> str:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise BookError("pandoc é necessário para converter Markdown em Typst")
    width, height = _trim(manifest.trim)
    parts = [
        f"#set document(title: {_typst_str(manifest.title)}, "
        f"author: {_typst_str(manifest.author)})",
        f"#set page(width: {width:.3f}in, height: {height:.3f}in, "
        "margin: (left: 0.9in, right: 0.8in, top: 0.9in, bottom: 0.9in), "
        "numbering: \"1\")",
        f"#set text(lang: {_typst_str(manifest.language.split('-')[0])}, "
        "size: 11pt, font: \"Libertinus Serif\")",
        "#set par(justify: true, leading: 0.65em)",
        "#set heading(numbering: \"1.1\")",
        "#align(center)[",
        f"  #text(size: 24pt, weight: \"bold\")[{_typst_text(manifest.title)}]",
        "  #v(1.2em)",
        f"  #text(size: 14pt)[{_typst_text(manifest.author)}]",
    ]
    if manifest.publisher:
        parts += ["  #v(0.8em)", f"  #text(size: 10pt)[{_typst_text(manifest.publisher)}]"]
    parts += ["  #v(0.4em)",
              f"  #text(size: 10pt)[{_typst_text(manifest.edition)}ª edição]",
              "]", "#pagebreak()", "#outline(title: \"Sumário\")", "#pagebreak()"]
    for chapter in chapters:
        result = _run([pandoc, "-f", "markdown", "-t", "typst", str(chapter)], 60,
                      cwd=root)
        if result.returncode != 0:
            raise BookError(f"pandoc falhou em {chapter.name}: {result.stderr[-300:]}")
        parts.append(result.stdout)
        parts.append("#pagebreak()")
    return "\n\n".join(parts) + "\n"


def _qa_pdf(path: Path, trim: str | None = None) -> Dict[str, Any]:
    if not path.is_file() or path.stat().st_size <= 0:
        raise BookError("PDF ausente ou vazio")
    pdfinfo = shutil.which("pdfinfo")
    pdffonts = shutil.which("pdffonts")
    pdftotext = shutil.which("pdftotext")
    if not pdfinfo:
        from marceloclaro.bookstudio.tex import qa_pdf_native
        try:
            return qa_pdf_native(path, trim=trim)
        except ValueError as exc:
            raise BookError(str(exc)) from exc
    info = _run([pdfinfo, str(path)], 30)
    if info.returncode != 0:
        raise BookError(f"pdfinfo falhou: {info.stderr[-300:]}")
    fields = {}
    for line in (info.stdout or "").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    pages = int(fields.get("Pages", "0") or 0)
    page_size = fields.get("Page size", "")
    width_in = height_in = None
    match = re.search(r"([0-9.]+)\s*x\s*([0-9.]+)\s*pts\s*\(([0-9.]+)\s*x\s*([0-9.]+)\s*inches\)",
                      page_size)
    if match:
        width_in, height_in = float(match.group(3)), float(match.group(4))
    else:
        pt_match = re.search(r"([0-9.]+)\s*x\s*([0-9.]+)\s*pts", page_size)
        if pt_match:
            width_in = float(pt_match.group(1)) / 72.0
            height_in = float(pt_match.group(2)) / 72.0
    fonts = {"total": 0, "not_embedded": []}
    if pdffonts:
        font_result = _run([pdffonts, str(path)], 30)
        font_re = re.compile(
            r"^(.*?)\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$")
        for line in (font_result.stdout or "").splitlines():
            match = font_re.match(line)
            if not match:
                continue
            fonts["total"] += 1
            if match.group(2).casefold() != "yes":
                fonts["not_embedded"].append(match.group(1).strip())
    text = ""
    if pdftotext:
        text_result = _run([pdftotext, str(path), "-"], 30)
        text = text_result.stdout or ""
    issues = []
    if pages <= 0:
        issues.append("no_pages")
    if not text.strip():
        issues.append("empty_text")
    if fonts["not_embedded"]:
        issues.append("fonts_not_embedded")
    if fields.get("Encrypted", "").casefold().startswith("yes"):
        issues.append("encrypted")
    if trim:
        expected_w, expected_h = _trim(trim)
        if width_in is None or height_in is None:
            issues.append("page_size_unknown")
        elif abs(width_in - expected_w) > 0.02 or abs(height_in - expected_h) > 0.02:
            issues.append("page_size_mismatch")
    return {
        "status": "completed", "pdf": str(path), "pages": pages,
        "page_size_inches": [width_in, height_in], "title": fields.get("Title"),
        "author": fields.get("Author"), "producer": fields.get("Producer"),
        "fonts": fonts, "text_chars": len(text.strip()), "issues": issues,
        "human_review_required": True, "external_validation": False,
        "limitations": ["QA técnico não avalia estética, tipografia ou revisão editorial.",
                        "Fontes embutidas não provam licença de uso.",
                        "Imagens, sangria e PDF/X exigem inspeção no editor visual."],
    }


def build(root: str | Path, *, engine: str | None = None,
          output_format: str = "pdf", out: str | Path | None = None,
          timeout: int = 180) -> Dict[str, Any]:
    root = Path(root).expanduser().resolve()
    manifest = load_manifest(root)
    engine = engine or manifest.engine
    if engine not in ENGINES:
        raise BookError(f"engine inválida: {engine}")
    if output_format not in FORMATS:
        raise BookError("output_format deve ser pdf ou epub")
    if engine in {"scribus", "vivliostyle", "casile"}:
        return {"status": "external_required", "engine": engine,
                "available": bool(_binary(engine)),
                "handoff": ("Use o editor/engine externo; o Book Studio não copia "
                            "código GPL/AGPL nem executa o app sem autorização."),
                "executed": False}
    chapters = chapter_paths(root, manifest)
    build_dir = root / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(manifest.title)
    target = Path(out).expanduser().resolve() if out else build_dir / f"{slug}.{output_format}"
    if not str(target).startswith(str(build_dir) + os.sep):
        raise BookError("saída fora de build/")
    target.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "epub":
        pandoc = shutil.which("pandoc")
        if not pandoc:
            raise BookError("pandoc ausente para EPUB")
        argv = [pandoc, *map(str, chapters), "-f", "markdown", "-t", "epub3",
                "--toc", "--metadata", f"title={manifest.title}",
                "--metadata", f"author={manifest.author}",
                "--metadata", f"lang={manifest.language}",
                "-o", str(target)]
        result = _run(argv, timeout, cwd=root)
        if result.returncode != 0:
            raise BookError(f"pandoc EPUB falhou: {result.stderr[-500:]}")
        return {"status": "completed", "engine": "pandoc", "format": "epub",
                "output": str(target), "bytes": target.stat().st_size,
                "executed": True, "external_validation": False}

    if engine == "typst":
        typst = _binary("typst")
        if not typst:
            raise BookError("typst ausente")
        source = _typst_source(root, manifest, chapters)
        source_path = build_dir / f"{slug}.typ"
        source_path.write_text(source, encoding="utf-8")
        argv = [typst, "compile", "--root", str(root), str(source_path), str(target)]
        result = _run(argv, timeout, cwd=root)
        if result.returncode != 0:
            raise BookError(f"typst falhou: {result.stderr[-500:]}")
    elif engine == "pandoc":
        pandoc = shutil.which("pandoc")
        if not pandoc:
            raise BookError("pandoc ausente")
        width, height = _trim(manifest.trim)
        argv = [pandoc, *map(str, chapters), "-f", "markdown", "-t", "pdf",
                "--pdf-engine=xelatex", "--toc", "--number-sections",
                "-V", "documentclass=book", "-V", f"geometry:paperwidth={width:.3f}in",
                "-V", f"geometry:paperheight={height:.3f}in",
                "-V", "geometry:margin=0.9in", "-V", "fontsize=11pt",
                "-V", f"lang={manifest.language}", "--metadata", f"title={manifest.title}",
                "--metadata", f"author={manifest.author}", "-o", str(target)]
        result = _run(argv, timeout, cwd=root)
        if result.returncode != 0:
            raise BookError(f"pandoc PDF falhou: {result.stderr[-500:]}")
    elif engine == "weasyprint":
        pandoc = shutil.which("pandoc")
        weasyprint = shutil.which("weasyprint")
        if not pandoc or not weasyprint:
            raise BookError("pandoc/weasyprint ausente")
        width, height = _trim(manifest.trim)
        css = build_dir / "book.css"
        css.write_text(
            "@page { size: %.3fin %.3fin; margin: 0.9in 0.8in; "
            "@bottom-center { content: counter(page); font-size: 9pt; } }\n"
            "body { font-family: 'Libertinus Serif', serif; font-size: 11pt; "
            "line-height: 1.45; text-align: justify; }\n"
            "h1 { page-break-before: always; }\n" % (width, height),
            encoding="utf-8")
        html = build_dir / f"{slug}.html"
        argv = [pandoc, *map(str, chapters), "-f", "markdown", "-t", "html5",
                "--standalone", "--toc", "--metadata", f"title={manifest.title}",
                "--metadata", f"author={manifest.author}", "--css", str(css),
                "-o", str(html)]
        result = _run(argv, timeout, cwd=root)
        if result.returncode != 0:
            raise BookError(f"pandoc HTML falhou: {result.stderr[-500:]}")
        result = _run([weasyprint, str(html), str(target)], timeout, cwd=root)
        if result.returncode != 0:
            raise BookError(f"weasyprint falhou: {result.stderr[-500:]}")
    elif engine == "latex":
        source_rel = manifest.source or "main.tex"
        if Path(source_rel).is_absolute() or ".." in Path(source_rel).parts:
            raise BookError("source LaTeX fora da raiz")
        source_path = (root / source_rel).resolve()
        if not str(source_path).startswith(str(root) + os.sep) or not source_path.is_file():
            raise BookError("source LaTeX ausente ou fora da raiz")
        latexmk = shutil.which("latexmk")
        pdflatex = shutil.which("pdflatex")
        if not latexmk and not pdflatex:
            raise BookError("latexmk/pdflatex ausente")
        job = f"{slug}-latex"
        source_arg = str(Path(source_rel))
        latex_timeout = max(timeout, 300)
        if latexmk:
            result = _run([latexmk, "-pdf", "-interaction=nonstopmode",
                           "-halt-on-error", f"-jobname={job}",
                           f"-outdir={build_dir}", source_arg],
                          latex_timeout, cwd=root)
        else:
            result = None
            for _ in range(3):
                result = _run([pdflatex, "-interaction=nonstopmode",
                               "-halt-on-error", f"-jobname={job}",
                               f"-output-directory={build_dir}", source_arg],
                              latex_timeout, cwd=root)
                if result.returncode != 0:
                    break
        if result is None or result.returncode != 0:
            detail = (result.stderr or result.stdout or "")[-500:] if result else ""
            raise BookError(f"LaTeX falhou: {detail}")
        produced = build_dir / f"{job}.pdf"
        if not produced.is_file() or produced.stat().st_size <= 0:
            raise BookError("LaTeX não produziu PDF")
        if produced != target:
            shutil.copyfile(produced, target)
    else:
        raise BookError(f"engine não suportada para build: {engine}")

    qa = _qa_pdf(target, manifest.trim)
    return {"status": "completed", "engine": engine, "format": "pdf",
            "output": str(target), "bytes": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "qa": qa, "executed": True, "external_validation": False}


def init(root: str | Path, *, title: str, author: str, language: str = "pt-BR",
         trim: str = "6x9in", engine: str = "typst",
         source: str | None = None) -> Dict[str, Any]:
    root = Path(root).expanduser().resolve()
    chapters = ("chapters/01.md",) if engine != "latex" else ()
    manifest = BookManifest(title=title, author=author, language=language,
                            trim=trim, engine=engine, source=source,
                            chapters=chapters,
                            output_formats=("pdf",) if engine == "latex"
                            else ("pdf", "epub"))
    save_manifest(root, manifest)
    sample = None
    if chapters:
        chapter_dir = root / "chapters"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        sample_path = chapter_dir / "01.md"
        if not sample_path.exists():
            sample_path.write_text("# Capítulo 1\n\nEscreva o texto aqui.\n",
                                   encoding="utf-8")
        sample = str(sample_path)
    return {"status": "completed", "root": str(root), "manifest": manifest.to_dict(),
            "sample": sample, "executed": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="book-studio", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    status_cmd = sub.add_parser("status")
    status_cmd.add_argument("root", nargs="?")
    init_cmd = sub.add_parser("init")
    init_cmd.add_argument("root")
    init_cmd.add_argument("--title", required=True)
    init_cmd.add_argument("--author", required=True)
    init_cmd.add_argument("--language", default="pt-BR")
    init_cmd.add_argument("--trim", default="6x9in")
    init_cmd.add_argument("--engine", choices=ENGINES, default="typst")
    init_cmd.add_argument("--source", help="arquivo .tex para engine latex")
    build_cmd = sub.add_parser("build")
    build_cmd.add_argument("root")
    build_cmd.add_argument("--engine", choices=ENGINES)
    build_cmd.add_argument("--format", choices=FORMATS, default="pdf")
    build_cmd.add_argument("--out")
    build_cmd.add_argument("--timeout", type=int, default=180)
    qa_cmd = sub.add_parser("qa")
    qa_cmd.add_argument("pdf")
    qa_cmd.add_argument("--trim")
    design_cmd = sub.add_parser("design", help="cria projeto LaTeX memoir/LuaLaTeX")
    design_cmd.add_argument("root")
    design_cmd.add_argument("--title", required=True)
    design_cmd.add_argument("--author", required=True)
    design_cmd.add_argument("--trim", default="160x230mm")
    design_cmd.add_argument("--publisher", default="")
    design_cmd.add_argument("--edition", default="1")
    design_cmd.add_argument("--chapter-count", type=int, default=1)
    design_cmd.add_argument("--bibliography", action="store_true")
    design_cmd.add_argument("--index", action="store_true")
    tex_cmd = sub.add_parser("tex", help="compila main.tex com latexmk/LuaLaTeX")
    tex_cmd.add_argument("root")
    tex_cmd.add_argument("--timeout", type=int, default=600)
    tex_cmd.add_argument("--clean", action="store_true")
    review_cmd = sub.add_parser("review", help="gate literário nativo + LanguageTool")
    review_cmd.add_argument("path")
    review_cmd.add_argument("--languagetool", action="store_true")
    review_cmd.add_argument("--endpoint", default="http://127.0.0.1:8081/v2/check")
    review_cmd.add_argument("--language", default="pt-BR")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            payload = status(args.root)
        elif args.command == "init":
            payload = init(args.root, title=args.title, author=args.author,
                           language=args.language, trim=args.trim, engine=args.engine,
                           source=args.source)
        elif args.command == "build":
            payload = build(args.root, engine=args.engine, output_format=args.format,
                            out=args.out, timeout=args.timeout)
        elif args.command == "design":
            from marceloclaro.bookstudio.tex import BookDesign, parse_trim, write_project
            width, height = parse_trim(args.trim)
            design = BookDesign(trim_width_mm=width, trim_height_mm=height,
                                bibliography=args.bibliography, index=args.index)
            count = max(1, min(50, args.chapter_count))
            chapters = {
                f"{index:02d}": f"\\chapter{{Capítulo {index}}}\n\n"
                                f"Texto do capítulo {index}. Substitua pelo manuscrito.\n"
                for index in range(1, count + 1)
            }
            payload = write_project(args.root, design, title=args.title,
                                    author=args.author, publisher=args.publisher,
                                    edition=args.edition, chapters=chapters)
        elif args.command == "tex":
            from marceloclaro.bookstudio.tex import compile_project, parse_tex_log, qa_pdf_native
            payload = compile_project(args.root, timeout=args.timeout, clean=args.clean)
            payload["log_findings"] = parse_tex_log(payload["log"]) if payload.get("log") else []
            if payload.get("pdf"):
                try:
                    trim = load_manifest(args.root).trim
                except BookError:
                    trim = None
                payload["qa"] = qa_pdf_native(payload["pdf"], trim=trim)
            else:
                payload["qa"] = None
        elif args.command == "review":
            from marceloclaro.bookstudio.review import review_file
            payload = review_file(args.path, use_languagetool=args.languagetool,
                                  endpoint=args.endpoint, language=args.language)
        else:
            payload = _qa_pdf(Path(args.pdf).expanduser().resolve(), args.trim)
    except (BookError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        payload = {"status": "blocked", "error": str(exc), "executed": False}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") in {"ready", "completed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
