"""R1111 — Book Studio TeX, QA nativo e gate literário."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from marceloclaro.bookstudio.tex import (
    BookDesign,
    TexError,
    compile_project,
    escape_latex,
    parse_tex_log,
    parse_trim,
    qa_pdf_native,
    write_project,
)
from marceloclaro.bookstudio.review import (
    ReviewError,
    check_languagetool,
    native_review,
    review_file,
    review_text,
)

CHAPTERS = {
    "01": "\\chapter{Primeiro capítulo}\n\nEste é um texto de prova com aspas “tipográficas” e travessão — para testar a diagramação.\n",
    "02": "\\chapter{Segundo capítulo}\n\nOutro parágrafo de prova, com uma frase suficientemente longa para ocupar a linha e verificar a justificação e a hifenização do português brasileiro.\n",
    "03": "\\chapter{Terceiro capítulo}\n\nFim do livro de prova.\n",
}


def test_design_defaults_and_roundtrip():
    design = BookDesign()
    assert design.trim == "160x230mm"
    data = design.to_dict()
    assert data["schema"] == "book-design/1"
    restored = BookDesign.from_dict(data)
    assert restored.trim == design.trim
    assert restored.body_font == design.body_font


def test_design_rejects_bad_leading():
    with pytest.raises(TexError, match="entrelinha"):
        BookDesign(leading_pt=10.0)


def test_parse_trim_units():
    width, height = parse_trim("6x9in")
    assert round(width, 1) == 152.4
    assert round(height, 1) == 228.6
    with pytest.raises(TexError):
        parse_trim("0x0mm")


def test_escape_latex_special_characters():
    escaped = escape_latex("100% & #1_2 {x} ~ ^")
    for token in ("\\%", "\\&", "\\#", "\\_", "\\{", "\\}", "\\textasciitilde{}", "\\textasciicircum{}"):
        assert token in escaped


def test_write_project_generates_manifest_and_template(tmp_path):
    design = BookDesign()
    paths = write_project(tmp_path / "livro", design, title="Livro de Prova",
                          author="Marcelo Claro", publisher="Core",
                          chapters={"01": "\\chapter{Um}\n\nTexto.\n"})
    main_tex = Path(paths["main_tex"]).read_text(encoding="utf-8")
    assert "\\documentclass" in main_tex and "memoir" in main_tex
    assert "\\setstocksize{230mm}{160mm}" in main_tex
    assert "\\setmainfont{Libertinus Serif}" in main_tex
    assert "\\input{chapters/01}" in main_tex
    manifest = json.loads(Path(paths["book_json"]).read_text(encoding="utf-8"))
    assert manifest["engine"] == "latex"
    assert manifest["trim"] == "160x230mm"
    assert manifest["chapters"] == ["chapters/01.tex"]
    assert Path(paths["design_json"]).is_file()


def test_write_project_multiple_chapters(tmp_path):
    paths = write_project(tmp_path / "multi", BookDesign(), title="T", author="A",
                          chapters={"01": "\\chapter{Um}\n\nTexto.\n",
                                    "02": "\\chapter{Dois}\n\nTexto.\n"})
    main_tex = Path(paths["main_tex"]).read_text(encoding="utf-8")
    assert "\\input{chapters/01}" in main_tex
    assert "\\input{chapters/02}" in main_tex
    manifest = json.loads(Path(paths["book_json"]).read_text(encoding="utf-8"))
    assert manifest["chapters"] == ["chapters/01.tex", "chapters/02.tex"]


def test_write_project_rejects_unsafe_chapter(tmp_path):
    with pytest.raises(TexError, match="inseguro"):
        write_project(tmp_path / "x", BookDesign(), title="T", author="A",
                      chapters={"../escape": "\\chapter{X}\n"})


@pytest.fixture(scope="module")
def compiled_book(tmp_path_factory):
    if not shutil.which("latexmk") or not shutil.which("lualatex"):
        pytest.skip("latexmk/lualatex ausentes; instale TinyTeX para o teste de integração")
    root = tmp_path_factory.mktemp("book-r1111")
    design = BookDesign()
    write_project(root, design, title="Livro de Prova", author="Marcelo Claro",
                  publisher="Core", chapters=CHAPTERS)
    result = compile_project(root, timeout=300, clean=True)
    return design, result


def test_compile_demo(compiled_book):
    design, result = compiled_book
    assert result["status"] == "completed", result.get("stdout_tail")
    assert result["returncode"] == 0
    pdf = Path(result["pdf"])
    assert pdf.is_file() and pdf.stat().st_size > 0


def test_qa_demo_native(compiled_book):
    design, result = compiled_book
    qa = qa_pdf_native(result["pdf"], trim=design.trim)
    assert qa["pages"] >= 3
    assert qa["page_size_mm"] == pytest.approx([160.0, 230.0], abs=0.6)
    assert qa["text_chars"] > 0
    assert "fonts_not_embedded" not in qa["issues"]
    assert qa["title"] == "Livro de Prova"
    assert qa["author"] == "Marcelo Claro"
    assert qa["human_review_required"] is True
    assert qa["external_validation"] is False


def test_qa_detects_trim_mismatch(compiled_book):
    _, result = compiled_book
    qa = qa_pdf_native(result["pdf"], trim="170x240mm")
    assert "page_size_mismatch" in qa["issues"]


def test_tex_log_has_no_errors(compiled_book):
    _, result = compiled_book
    findings = parse_tex_log(result["log"])
    assert not [f for f in findings if f["severity"] == "error"]


def test_native_review_rules():
    text = ('Ele disse "olá"... basicamente, foi -- muito bom , com  duplo espaço. '
            'coração disparou. ' +
            "Esta frase é deliberadamente longa para testar a regra de comprimento e "
            "continua com muitas palavras para ultrapassar o limite configurado no "
            "gate nativo de revisão literária do Core, sem qualquer julgamento de mérito; "
            "e mesmo assim segue adiante com novas orações subordinadas, adjetivos e "
            "complementos que só existem para garantir que o limite seja realmente "
            "ultrapassado nesta verificação automática do relatório.")
    rules = {finding.rule for finding in native_review(text)}
    for expected in ("aspas_retas", "reticencias", "muleta", "travessao_duplo",
                     "espaco_antes_pontuacao", "duplo_espaco", "frase_longa", "cliche"):
        assert expected in rules


def test_native_review_detects_unbalanced_quotes():
    rules = {finding.rule for finding in native_review("Ele disse “olá.”")}
    assert "aspas_desbalanceadas" not in rules
    rules = {finding.rule for finding in native_review("Ele disse “olá.")}
    assert "aspas_desbalanceadas" in rules


def test_languagetool_unavailable_is_declared():
    result = check_languagetool("Texto de prova.", endpoint="http://127.0.0.1:9/v2/check",
                                timeout=1.0)
    assert result["available"] is False
    assert result["findings"] == []


def test_review_text_never_approves():
    report = review_text('Ele disse "olá"...', use_languagetool=False)
    assert report["human_review_required"] is True
    assert report["external_validation"] is False
    assert report["metrics"]["words"] > 0
    assert len(report["limitations"]) >= 3
    assert set(report["counts"]) == {"error", "warning", "info"}
    assert "approved" not in report


def test_review_file_reads_and_rejects_missing(tmp_path):
    path = tmp_path / "texto.txt"
    path.write_text("Um texto curto, sem problemas graves.", encoding="utf-8")
    report = review_file(path)
    assert report["file"] == str(path)
    assert report["status"] == "completed"
    with pytest.raises(ReviewError, match="ausente"):
        review_file(tmp_path / "nao-existe.txt")
