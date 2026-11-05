"""R1071: Book Studio — manifesto, builds e QA técnico."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import zipfile

import pytest

from marceloclaro import book_studio as studio


def _write_book(root: Path, *, engine: str = "typst", source: str | None = None,
                chapters: tuple[str, ...] = ("chapters/01.md", "chapters/02.md")) -> None:
    manifest = studio.BookManifest(
        title="Livro de Teste", author="Autora Teste", language="pt-BR",
        trim="6x9in", engine=engine, source=source, chapters=chapters,
        output_formats=("pdf", "epub"),
    )
    studio.save_manifest(root, manifest)
    if chapters:
        (root / "chapters").mkdir(exist_ok=True)
        (root / "chapters/01.md").write_text(
            "# Capítulo 1\n\nMarcador-alfa do livro de teste.\n", encoding="utf-8")
        (root / "chapters/02.md").write_text(
            "# Capítulo 2\n\nMarcador-beta do livro de teste.\n", encoding="utf-8")


def test_init_creates_manifest_and_sample(tmp_path):
    result = studio.init(tmp_path, title="Livro", author="Autor",
                         language="pt-BR", trim="6x9in", engine="typst")
    assert result["status"] == "completed"
    assert (tmp_path / "book.json").is_file()
    assert (tmp_path / "chapters/01.md").is_file()
    manifest = studio.load_manifest(tmp_path)
    assert manifest.title == "Livro"
    assert manifest.engine == "typst"


def test_typst_build_and_qa(tmp_path):
    if not studio._binary("typst") or not shutil.which("pandoc"):
        pytest.skip("typst/pandoc ausentes")
    _write_book(tmp_path)
    result = studio.build(tmp_path, engine="typst")
    assert result["status"] == "completed"
    pdf = Path(result["output"])
    assert pdf.is_file() and pdf.stat().st_size > 0
    qa = result["qa"]
    assert qa["pages"] >= 1
    assert qa["text_chars"] > 0
    assert qa["title"] == "Livro de Teste"
    assert qa["author"] == "Autora Teste"
    assert qa["fonts"]["not_embedded"] == []
    assert qa["issues"] == []
    assert abs(qa["page_size_inches"][0] - 6) < 0.02
    assert abs(qa["page_size_inches"][1] - 9) < 0.02


def test_epub_build(tmp_path):
    if not shutil.which("pandoc"):
        pytest.skip("pandoc ausente")
    _write_book(tmp_path)
    result = studio.build(tmp_path, engine="typst", output_format="epub")
    assert result["status"] == "completed"
    epub = Path(result["output"])
    assert epub.is_file() and epub.stat().st_size > 0
    with zipfile.ZipFile(epub) as archive:
        assert "mimetype" in archive.namelist()
        assert archive.read("mimetype").decode("ascii") == "application/epub+zip"


def test_latex_engine_builds_pdf(tmp_path):
    if not studio._binary("latex"):
        pytest.skip("latexmk/pdflatex ausentes")
    root = tmp_path
    (root / "main.tex").write_text(
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{hyperref}\n"
        "\\hypersetup{pdftitle={Livro LaTeX},pdfauthor={Autora LaTeX}}\n"
        "\\begin{document}\nMarcador-gama.\\newpage\nSegunda página.\\end{document}\n",
        encoding="utf-8",
    )
    manifest = studio.BookManifest(
        title="Livro LaTeX", author="Autora LaTeX", language="pt-BR",
        trim="8.5x11in", engine="latex", source="main.tex", chapters=(),
        output_formats=("pdf",),
    )
    studio.save_manifest(root, manifest)
    result = studio.build(root, engine="latex", timeout=60)
    assert result["status"] == "completed"
    qa = result["qa"]
    assert qa["pages"] >= 1
    assert qa["title"] == "Livro LaTeX"
    assert qa["author"] == "Autora LaTeX"
    assert qa["fonts"]["not_embedded"] == []


def test_chapter_path_traversal_is_rejected(tmp_path):
    _write_book(tmp_path)
    manifest = studio.BookManifest(
        title="Livro", author="Autor", engine="typst",
        chapters=("../escape.md",), output_formats=("pdf",),
    )
    with pytest.raises(studio.BookError):
        studio.chapter_paths(tmp_path, manifest)


def test_status_lists_engines():
    current = studio.status()
    assert current["status"] == "ready"
    assert "typst" in current["engines"]
    assert "latex" in current["engines"]
    assert current["external_validation"] is False
