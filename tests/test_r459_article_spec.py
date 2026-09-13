"""Teste de sanidade do artefato de publicação SPEC-935-R459 (R475).

Hermético: lê apenas arquivos locais do artigo LaTeX; sem rede, sem compilação.
Garante que o artefato submissível permaneça íntegro (documento, bibliografia,
figuras e gerador) — o test_file vinculado no frontmatter da spec R459.
"""
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
ARTIFACT = REPO_ROOT / "publications" / "r459_article"


def test_main_tex_existe_e_e_documento_latex():
    main_tex = ARTIFACT / "main.tex"
    assert main_tex.is_file()
    content = main_tex.read_text(encoding="utf-8", errors="replace")
    assert "\\documentclass" in content
    assert "\\begin{document}" in content
    assert "\\end{document}" in content


def test_bibliografia_compilada_existe():
    # O artefato mantém apenas a bibliografia resolvida (main.bbl); a fonte
    # (.bib) pode ser gerada pelo fluxo editorial e não precisa residir no repo.
    assert (ARTIFACT / "main.bbl").is_file()


def test_figuras_e_gerador_presentes():
    figures = ARTIFACT / "figures"
    assert figures.is_dir()
    assert (ARTIFACT / "make_figures.py").is_file()


def test_spec_frontmatter_vinculara_test_file():
    spec = REPO_ROOT / "specs" / "SPEC-935-R459-artigo-publicacao.md"
    content = spec.read_text(encoding="utf-8")
    assert "test_file: tests/test_r459_article_spec.py" in content
    assert "title: Artigo científico" in content


def test_artigo_menciona_diversificacao_e_recaman():
    main_tex = (ARTIFACT / "main.tex").read_text(encoding="utf-8", errors="replace")
    assert "diversifica" in main_tex.lower()
    assert "recam" in main_tex.lower()