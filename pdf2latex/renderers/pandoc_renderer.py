"""
Renderer Pandoc — converte dados extraídos para LaTeX via Pandoc + templates.

Fluxo:
  Dados Extraídos → Markdown Estruturado → Split por capítulos →
  Pandoc (fragmento) em cada capítulo → main.tex com \\include{} dos capítulos

Para livros com 500+ páginas, cada capítulo vira um .tex separado em capitulos/.
"""

import logging
import re
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import date

from .base import BaseRenderer, RenderInput
from ..template_integrator import TemplateIntegrator

logger = logging.getLogger("pdf2latex")

# CSL embutidos (minificado) para fallback
EMBEDDED_CSL = {
    "abnt.csl": """<?xml version="1.0" encoding="utf-8"?><style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0"><info><title>ABNT (alfabética)</title><id>http://www.zotero.org/styles/abnt</id><link href="http://www.zotero.org/styles/abnt" rel="self"/><author><name>ABNT</name></author><category field="generic-base"/><updated>2024-01-01T00:00:00+00:00</updated></info><macro name="author"><names variable="author"><name sort-separator="; " name-form="short" name-as-sort-order="all"/></names></macro><macro name="year"><date variable="issued"><date-part name="year"/></date></macro><citation><layout><text macro="author"/><text macro="year" prefix=", "/></layout></citation><bibliography><sort><key macro="author"/><key macro="year"/></sort><layout><text macro="author"/><text macro="year" prefix=". "/><text variable="title" prefix=". " suffix="."/><text variable="publisher" prefix=". "/></layout></bibliography></style>""",
    "ieee.csl": """<?xml version="1.0" encoding="utf-8"?><style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0"><info><title>IEEE</title><id>http://www.zotero.org/styles/ieee</id><link href="http://www.zotero.org/styles/ieee" rel="self"/><author><name>IEEE</name></author><category field="engineering"/><updated>2024-01-01T00:00:00+00:00</updated></info><citation><layout><text variable="citation-number"/></layout></citation><bibliography><layout><text variable="citation-number" prefix="[" suffix="]"/><text macro="author" prefix=". " suffix="."/><text variable="title" prefix=" " suffix="."/><text variable="publisher" prefix=" "/></layout></bibliography></style>""",
    "acm-sig-proceedings.csl": """<?xml version="1.0" encoding="utf-8"?><style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0"><info><title>ACM SIG Proceedings</title><id>http://www.zotero.org/styles/acm-sig-proceedings</id><link href="http://www.zotero.org/styles/acm-sig-proceedings" rel="self"/><author><name>ACM</name></author><category field="computer-science"/><updated>2024-01-01T00:00:00+00:00</updated></info><citation><layout><text variable="citation-number"/></layout></citation><bibliography><layout><text variable="citation-number" prefix="[" suffix="]"/><text macro="author" prefix=". " suffix="."/><text variable="title" prefix=" " suffix="."/><text variable="publisher" prefix=" "/></layout></bibliography></style>""",
}


class PandocRenderer(BaseRenderer):
    """
    Renderizador usando Pandoc + templates.
    Produz LaTeX de altíssima qualidade com capítulos separados.

    Para livros com 500+ páginas, cada capítulo vira um .tex separado
    em capitulos/, e o main.tex usa \\include{} para montar o documento.

    Requer: pandoc (>= 3.0)
    """

    name = "pandoc"
    description = "Renderer Pandoc: Markdown → LaTeX com capítulos separados. Qualidade tipográfica superior."

    def __init__(self):
        self._csl_dir = Path(__file__).parent.parent / "pandoc-templates"

    def render(self, data: RenderInput) -> Path:
        """Renderiza dados extraídos em LaTeX via Pandoc."""
        output_dir = data.output_dir or Path(f"./{data.pdf_name}_latex")
        output_dir.mkdir(parents=True, exist_ok=True)

        chapters_dir = output_dir / "capitulos"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        # 1. Gerar Markdown completo
        md_path = output_dir / "documento.md"
        self._generate_markdown(md_path, data)

        # 2. Parsear Markdown e dividir em capítulos por # Heading
        chapters = self._split_markdown_by_chapters(md_path)

        if not chapters:
            logger.warning("   ⚠️  Nenhum capítulo detectado. Usando fallback.")
            tex_path = output_dir / "main.tex"
            tex_path.write_text(self._fallback_latex(data), encoding="utf-8")
            self._copy_images(data, output_dir)
            return output_dir

        logger.info(f"   → {len(chapters)} capítulos detectados")

        # 3. Renderizar cada capítulo com Pandoc (fragmento, sem standalone)
        for i, (title, md_content) in enumerate(chapters):
            chap_num = i + 1
            slug = self._slugify(title)
            chap_md_path = chapters_dir / f"capitulo_{chap_num:02d}_{slug}.md"
            chap_tex_path = chapters_dir / f"capitulo_{chap_num:02d}_{slug}.tex"

            # Escrever arquivo .md do capítulo
            chap_md_path.write_text(md_content, encoding="utf-8")

            # Converter via Pandoc (fragmento: sem -s, apenas body)
            self._pandoc_md_to_tex(chap_md_path, chap_tex_path, data)

            if not chap_tex_path.exists() or chap_tex_path.stat().st_size < 10:
                logger.warning(f"   ⚠️  Capítulo {chap_num} vazio após Pandoc, usando template")
                clean_title = self._clean_for_latex(title)
                chap_tex_path.write_text(
                    f"\\chapter{{{clean_title}}}\n\nConteúdo extraído automaticamente.\n",
                    encoding="utf-8"
                )

            logger.info(f"   ✓ Capítulo {chap_num:02d}: {title} → capitulos/{chap_tex_path.name}")

        # 4. Gerar main.tex com \include{} para cada capítulo
        self._generate_main_tex(output_dir, chapters, data)

        # 5. Copiar imagens
        self._copy_images(data, output_dir)

        # 6. Aplicar template (copia .cls, .sty, .bst, .bib, fontes)
        if data.template:
            try:
                integrator = TemplateIntegrator(
                    project_dir=output_dir,
                    template_name=data.template,
                )
                integrator.apply()
                logger.info(f"   → Template '{data.template}' aplicado (arquivos copiados)")
            except Exception as e:
                logger.warning(f"   ⚠️  Erro ao aplicar template: {e}")

        return output_dir

    # ------------------------------------------------------------------ #
    #  Divisão de capítulos
    # ------------------------------------------------------------------ #

    def _split_markdown_by_chapters(self, md_path: Path) -> List[Tuple[str, str]]:
        """
        Divide o Markdown em capítulos baseado em # Heading (top-level).

        Retorna lista de (título, conteúdo_markdown).
        """
        text = md_path.read_text(encoding="utf-8")

        # Remove YAML front matter
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
        text = text.strip()

        # Encontra todos os headings top-level (# )
        # Captura: o título e o conteúdo até o próximo # ou fim
        pattern = r'^# (.+)$'
        lines = text.split('\n')

        chapters = []
        current_title = None
        current_lines = []

        for line in lines:
            m = re.match(r'^# (.+)$', line)
            if m:
                # Salva capítulo anterior
                if current_title is not None and current_lines:
                    chapters.append((current_title, '\n'.join(current_lines)))
                # Inicia novo capítulo
                current_title = m.group(1).strip()
                current_lines = [line]
            else:
                if current_title is not None:
                    current_lines.append(line)

        # Último capítulo
        if current_title is not None and current_lines:
            chapters.append((current_title, '\n'.join(current_lines)))

        return chapters

    def _slugify(self, title: str) -> str:
        """Converte título para slug seguro para nome de arquivo."""
        slug = title.lower().strip()
        slug = re.sub(r'[áàâãä]', 'a', slug)
        slug = re.sub(r'[éèêë]', 'e', slug)
        slug = re.sub(r'[íìîï]', 'i', slug)
        slug = re.sub(r'[óòôõö]', 'o', slug)
        slug = re.sub(r'[úùûü]', 'u', slug)
        slug = re.sub(r'[ç]', 'c', slug)
        slug = re.sub(r'[^a-z0-9]+', '_', slug)
        slug = slug.strip('_')
        return slug[:60] or "capitulo"

    def _clean_for_latex(self, text: str) -> str:
        """Escapa caracteres especiais do LaTeX."""
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('$', '\\$'),
            ('#', '\\#'),
            ('_', '\\_'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('~', '\\textasciitilde{}'),
            ('^', '\\textasciicircum{}'),
            ('<', '\\textless{}'),
            ('>', '\\textgreater{}'),
        ]
        for old, new in replacements:
            text = text.replace(old, new)
        return text

    # ------------------------------------------------------------------ #
    #  Conversão Pandoc
    # ------------------------------------------------------------------ #

    def _pandoc_md_to_tex(self, md_path: Path, tex_path: Path, data: RenderInput):
        """Converte um arquivo Markdown para LaTeX via Pandoc (fragmento)."""
        cmd = [
            "pandoc",
            str(md_path),
            "-f", "markdown",
            "-t", "latex",
            "-o", str(tex_path),
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                logger.warning(f"   ⚠️  Pandoc erro no capítulo {md_path.name}: {result.returncode}")
                if result.stderr:
                    for line in result.stderr.strip().split('\n')[-3:]:
                        logger.warning(f"      {line}")
        except subprocess.TimeoutExpired:
            logger.warning(f"   ⚠️  Pandoc timeout no capítulo {md_path.name}")
        except FileNotFoundError:
            logger.error("   ❌ Pandoc não encontrado. Instale: sudo apt install pandoc")
            raise

    # ------------------------------------------------------------------ #
    #  Geração do main.tex
    # ------------------------------------------------------------------ #

    def _generate_main_tex(self, output_dir: Path, chapters: List[Tuple[str, str]], data: RenderInput):
        """Gera main.tex com preâmbulo do template + \\include{} dos capítulos + posâmbulo."""
        chapters_dir = output_dir / "capitulos"
        template = data.template or "article"

        # Preâmbulo
        preamble = self._generate_preamble(template, data)

        # Corpo: \include{} para cada capítulo
        body_parts = []
        for i, (title, _) in enumerate(chapters):
            slug = self._slugify(title)
            chap_filename = f"capitulo_{i+1:02d}_{slug}"
            body_parts.append(f"\\include{{capitulos/{chap_filename}}}")

        # Posâmbulo
        postamble = self._generate_postamble(template, data)

        # Montar main.tex
        main_tex = preamble + "\n\\begin{document}\n\n"
        main_tex += "\\maketitle\n\\tableofcontents\n\\newpage\n\n"
        main_tex += "\n".join(body_parts) + "\n\n"
        main_tex += postamble
        main_tex += "\n\\end{document}\n"

        tex_path = output_dir / "main.tex"
        tex_path.write_text(main_tex, encoding="utf-8")
        logger.info(f"   → main.tex gerado com {len(chapters)} capítulos ({tex_path.stat().st_size} bytes)")

    def _generate_preamble(self, template: str, data: RenderInput) -> str:
        """Gera o preâmbulo LaTeX baseado no template."""
        # Tenta usar template .template do Pandoc para o preâmbulo
        template_file = self._get_template_file(template)
        if template_file:
            content = template_file.read_text(encoding="utf-8")
            # Extrair só o preâmbulo (tudo antes de \begin{document})
            m = re.search(r'^(.*?)\\begin\{document\}', content, re.DOTALL)
            if m:
                preamble = m.group(1).strip()
                # Substituir variáveis do template Pandoc por valores reais
                today = date.today().isoformat()
                preamble = preamble.replace('$title$', self._clean_for_latex(data.pdf_name))
                preamble = preamble.replace('$author$', '')
                preamble = preamble.replace('$date$', today)
                return preamble

        # Fallback: preâmbulo genérico
        return self._default_preamble(template, data)

    def _generate_postamble(self, template: str, data: RenderInput) -> str:
        """Gera o posâmbulo LaTeX (bibliografia, etc.)."""
        bib_style = self._get_bibstyle(template)
        parts = []

        if data.references:
            parts.append(f"\\bibliographystyle{{{bib_style}}}")
            parts.append("\\bibliography{referencias}")

        return "\n".join(parts)

    def _default_preamble(self, template: str, data: RenderInput) -> str:
        """Preâmbulo LaTeX padrão para cada template."""
        preambles = {
            "abntex2": r"""\documentclass[12pt,a4paper]{abntex2}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{graphicx}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{a4paper, margin=2.5cm}
\usepackage{indentfirst}
\usepackage{setspace}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{xcolor}

\usepackage[alf]{abntex2cite}

\onehalfspacing
\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}

\title{""" + self._clean_for_latex(data.pdf_name) + r"""}
\author{}
\date{\today}""",
            "ieee": r"""\documentclass[conference]{IEEEtran}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{cite}

\title{""" + self._clean_for_latex(data.pdf_name) + r"""}
\author{}""",
        }

        if template in preambles:
            return preambles[template]

        # Genérico
        return r"""\documentclass[12pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{a4paper, margin=2.5cm}
\usepackage{setspace}
\usepackage{caption}
\usepackage{xcolor}

\onehalfspacing
\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}

\title{""" + self._clean_for_latex(data.pdf_name) + r"""}
\author{}
\date{\today}"""

    def _get_bibstyle(self, template: str) -> str:
        """Retorna o estilo bibliográfico para o template."""
        styles = {
            "abntex2": "abntex2-alf",
            "abnt": "abntex2-alf",
            "ieee": "IEEEtran",
            "acm": "ACM-Reference-Format",
            "article": "plain",
            "book": "plain",
        }
        return styles.get(template, "plain")

    def _get_template_file(self, template_name: str) -> Optional[Path]:
        """Localiza arquivo de template .template no diretório pandoc-templates."""
        for ext in [".template", ".latex", ".tex"]:
            tpl = self._csl_dir / (template_name + ext)
            if tpl.exists():
                return tpl
        return None

    # ------------------------------------------------------------------ #
    #  Geração de Markdown
    # ------------------------------------------------------------------ #

    def _generate_markdown(self, md_path: Path, data: RenderInput):
        """Converte dados extraídos para Markdown estruturado com capítulos."""
        lines = []
        lines.append("---")
        lines.append(f"title: '{data.pdf_name}'")
        lines.append(f"date: '2026-07-09'")
        lines.append("lang: pt-BR")
        lines.append("...")
        lines.append("")

        # Capítulos da estrutura
        chapters = data.structure.get('chapters', [])
        sections = data.structure.get('sections', [])
        paragraphs = data.structure.get('paragraphs', [])
        text = data.text_content

        if chapters:
            for title, content in chapters:
                lines.append(f"# {title}")
                lines.append("")
                body = self._extract_body(title, text)
                lines.append(body)
                lines.append("")
        elif sections:
            for title, content in sections:
                lines.append(f"# {title}")
                lines.append("")
                body = self._extract_body(title, text)
                lines.append(body)
                lines.append("")
        else:
            # Texto corrido — divide em parágrafos como capítulos
            paragraphs_text = re.split(r'\n\n+', text)
            for i, para in enumerate(paragraphs_text[:100]):
                para = para.strip()
                if len(para) > 100:
                    lines.append(f"# Seção {i+1}")
                    lines.append("")
                    lines.append(para[:2000])
                    lines.append("")

        # Figuras
        if data.images:
            lines.append("# Figuras")
            lines.append("")
            for img_path, page, caption in data.images[:5]:
                rel_path = f"figures/{img_path.name}"
                cap = caption or f"Figura extraída"
                lines.append(f"![{cap}]({rel_path})")
                lines.append("")

        # Referências
        if data.references:
            lines.append("# Referências")
            lines.append("")
            for cite_key, bib_entry in data.references[:30]:
                lines.append(f"  - {cite_key}: extraída automaticamente")
            lines.append("")

        md_path.write_text('\n'.join(lines), encoding="utf-8")

    def _extract_body(self, title: str, full_text: str) -> str:
        """Extrai corpo do texto após um título."""
        idx = full_text.find(title)
        if idx < 0:
            return "Conteúdo extraído automaticamente."
        start = idx + len(title)
        end = min(start + 3000, len(full_text))
        content = full_text[start:end].strip()
        # Limitar no próximo título numérico
        next_title = re.search(r'\n\d+\s+[A-Z]', content)
        if next_title:
            content = content[:next_title.start()]
        return content[:2500]

    # ------------------------------------------------------------------ #
    #  Utilidades
    # ------------------------------------------------------------------ #

    def _copy_images(self, data: RenderInput, output_dir: Path):
        """Copia imagens para o diretório de saída."""
        figures_dir = output_dir / "figures"
        figures_dir.mkdir(exist_ok=True)
        for img_path, page, caption in data.images:
            if img_path.exists():
                try:
                    shutil.copy2(img_path, figures_dir / img_path.name)
                except Exception:
                    pass

    def _fallback_latex(self, data: RenderInput) -> str:
        """Gera LaTeX de fallback simples sem Pandoc."""
        lines = []
        lines.append(r"\documentclass[12pt,a4paper]{article}")
        lines.append(r"\usepackage[utf8]{inputenc}")
        lines.append(r"\usepackage[T1]{fontenc}")
        lines.append(r"\usepackage[brazil]{babel}")
        lines.append(r"\usepackage{graphicx}")
        lines.append(r"\usepackage{hyperref}")
        lines.append(r"\begin{document}")
        lines.append(f"\\title{{{self._clean_for_latex(data.pdf_name)}}}")
        lines.append(r"\maketitle")
        lines.append(r"\tableofcontents")
        lines.append(r"\newpage")

        chapters = data.structure.get('chapters', [])
        for i, (title, content) in enumerate(chapters[:30]):
            clean = self._clean_for_latex(title)
            lines.append(f"\\chapter{{{clean}}}")
            lines.append("Conteúdo extraído automaticamente.")
            lines.append("")

        if data.references:
            lines.append(r"\bibliographystyle{plain}")
            lines.append(r"\bibliography{referencias}")

        lines.append(r"\end{document}")
        return '\n'.join(lines)

    def is_available(self) -> bool:
        """Verifica se Pandoc está disponível."""
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
