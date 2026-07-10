# -*- coding: utf-8 -*-
"""
Testes R119 — Templates literários (romance e contos/poesia)
=================================================================
Até o R119, todos os templates de "livro" do catálogo eram acadêmicos ou
técnicos (Victoria Regia, UnB Editora, Springer, book-simple). Este ciclo
adiciona os dois primeiros templates literários/de ficção:

  - `templates/books/romance-literario/` — romance/narrativa longa
  - `templates/books/contos-poesia/`     — coletânea de contos e poemas

E os integra ao pipeline `publishing/production.py` (`TEMPLATE_MAIN`),
via symlinks de compatibilidade em `publishing/templates/livro/`
(seguindo o mesmo padrão já usado por `book`/`victoria_regia`).

Requisitos (SPEC-935-R119):
  - Os dois diretórios de template existem com `main.tex` válido
  - `TEMPLATE_MAIN` inclui `livro-romance` e `livro-contos`
  - `list_templates()` resolve os caminhos corretamente
  - `ScientificProduction.prepare_latex()` copia a árvore inteira do
    template (incluindo `misc/opcoes.sty`) para `latex_dir`
"""

import os
import shutil
import tempfile

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATES_BOOKS = os.path.join(_ROOT, "templates", "books")


class TestTemplateFilesExist:
    @pytest.mark.parametrize("dirname", ["romance-literario", "contos-poesia"])
    def test_template_directory_has_main_tex(self, dirname):
        path = os.path.join(_TEMPLATES_BOOKS, dirname)
        assert os.path.isdir(path)
        assert os.path.isfile(os.path.join(path, "main.tex"))
        assert os.path.isfile(os.path.join(path, "misc", "opcoes.sty"))

    def test_romance_has_frontmatter_and_backmatter(self):
        path = os.path.join(_TEMPLATES_BOOKS, "romance-literario")
        for rel in (
            "frontmatter/folhaderosto.tex",
            "frontmatter/dedicatoria.tex",
            "frontmatter/epigrafe.tex",
            "content/capitulo01.tex",
            "backmatter/sobre-o-autor.tex",
            "backmatter/colofao.tex",
        ):
            assert os.path.isfile(os.path.join(path, rel)), rel

    def test_contos_poesia_has_content(self):
        path = os.path.join(_TEMPLATES_BOOKS, "contos-poesia")
        for rel in (
            "frontmatter/folhaderosto.tex",
            "content/conto-01.tex",
            "content/poema-01.tex",
            "backmatter/sobre-o-autor.tex",
        ):
            assert os.path.isfile(os.path.join(path, rel)), rel


class TestPipelineIntegration:
    def test_template_main_has_literary_entries(self):
        from publishing.production import TEMPLATE_MAIN
        assert TEMPLATE_MAIN["livro-romance"] == os.path.join("livro", "romance")
        assert TEMPLATE_MAIN["livro-contos"] == os.path.join("livro", "contos")

    def test_list_templates_resolves_existing_directories(self):
        from publishing.production import list_templates
        templates = list_templates()
        assert os.path.isdir(templates["livro-romance"])
        assert os.path.isdir(templates["livro-contos"])

    def test_compatibility_symlinks_point_to_new_templates(self):
        symlink_romance = os.path.join(
            _ROOT, "publishing", "templates", "livro", "romance"
        )
        symlink_contos = os.path.join(
            _ROOT, "publishing", "templates", "livro", "contos"
        )
        assert os.path.realpath(symlink_romance) == os.path.join(
            _TEMPLATES_BOOKS, "romance-literario"
        )
        assert os.path.realpath(symlink_contos) == os.path.join(
            _TEMPLATES_BOOKS, "contos-poesia"
        )

    @pytest.mark.parametrize("template_name", ["livro-romance", "livro-contos"])
    def test_prepare_latex_copies_template_tree(self, template_name):
        from publishing.production import ScientificProduction

        tmpdir = tempfile.mkdtemp()
        try:
            prod = ScientificProduction(
                title="Obra de Teste", template=template_name, author="Autor Teste"
            )
            prod.folder = tmpdir
            prod.latex_dir = os.path.join(tmpdir, "latex")
            prod.sections_dir = os.path.join(prod.latex_dir, "sections")
            os.makedirs(prod.sections_dir, exist_ok=True)
            prod.md_path = os.path.join(tmpdir, "manuscrito.md")
            with open(prod.md_path, "w", encoding="utf-8") as f:
                f.write("# Capitulo 1\nEra uma vez.\n")

            main_tex = prod.prepare_latex()

            assert os.path.isfile(main_tex)
            assert os.path.isfile(
                os.path.join(prod.latex_dir, "misc", "opcoes.sty")
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
