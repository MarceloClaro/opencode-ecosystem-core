"""
Gerador de projeto LaTeX completo a partir do conteúdo extraído do PDF.
Cria main.tex com preâmbulo, capítulos separados, figuras, tabelas, equações e .bib.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class LaTeXGenerator:
    """Gera um projeto LaTeX completo e compilável."""

    def __init__(
        self,
        output_dir: Path,
        pdf_name: str,
        text_content: str,
        structure: Dict,
        images: List[Tuple],
        tables: List[Tuple],
        equations: List[Tuple],
        references: List[Tuple],
    ):
        self.output_dir = output_dir
        self.pdf_name = pdf_name
        self.text_content = text_content
        self.structure = structure
        self.images = images
        self.tables = tables
        self.equations = equations
        self.references = references

        # Diretórios do projeto
        self.chapters_dir = output_dir / "capitulos"
        self.figures_dir = output_dir / "figures"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def generate(self):
        """Gera todo o projeto LaTeX."""
        self._copy_images()
        self._generate_chapters()
        self._generate_main_tex()
        self._generate_bibliography()
        self._generate_makefile()
        self._generate_readme()

    def _copy_images(self):
        """Copia imagens extraídas para o diretório figures/."""
        import shutil
        for img_path, page, caption in self.images:
            if img_path.exists():
                dest = self.figures_dir / img_path.name
                # Evitar copiar para si mesmo
                if str(img_path.resolve()) != str(dest.resolve()):
                    shutil.copy2(img_path, dest)
                else:
                    pass  # Já está no lugar correto

    def _generate_chapters(self):
        """Gera arquivos .tex para cada capítulo/seção."""
        chapters = self.structure.get('chapters', [])
        sections = self.structure.get('sections', [])
        special = self.structure.get('special', [])

        # Capítulo de preâmbulo (resumo, abstract, introdução não numerada)
        preliminar = [
            sec for sec in special
            if any(kw in sec[0].upper() for kw in ['RESUMO', 'ABSTRACT', 'AGRADECIMENTO'])
        ]

        # Processar seções especiais como capítulos
        for i, (title, line) in enumerate(preliminar):
            latex = self._section_to_latex(title, line)
            filename = f"00_{i+1}_{self._slugify(title)}.tex"
            (self.chapters_dir / filename).write_text(latex, encoding="utf-8")

        # Processar capítulos numerados
        for i, (title, line) in enumerate(chapters):
            latex = self._section_to_latex(title, line, nivel="chapter")
            filename = f"capitulo_{i+1:02d}_{self._slugify(title)}.tex"
            (self.chapters_dir / filename).write_text(latex, encoding="utf-8")

        # Se não detectou capítulos, criar a partir de parágrafos
        if not chapters and not preliminar:
            self._generate_from_paragraphs()

    def _generate_from_paragraphs(self):
        """Gera capítulos a partir de parágrafos quando não há estrutura detectada."""
        paragraphs = self.structure.get('paragraphs', [])
        if not paragraphs:
            # Fallback: pegar o texto completo e dividir
            lines = self.text_content.split('\n')
            chunks = []
            current = []
            for line in lines:
                current.append(line)
                if len('\n'.join(current)) > 5000:  # ~5KB por capítulo
                    chunks.append('\n'.join(current))
                    current = []
            if current:
                chunks.append('\n'.join(current))

            for i, chunk in enumerate(chunks):
                latex = self._text_to_chapter(chunk, f"Seção {i+1}")
                filename = f"capitulo_{i+1:02d}_texto_extraido.tex"
                (self.chapters_dir / filename).write_text(latex, encoding="utf-8")
        else:
            # Agrupar parágrafos em capítulos (~10 parágrafos por capítulo)
            chunk_size = 10
            for i in range(0, len(paragraphs), chunk_size):
                chunk = paragraphs[i:i + chunk_size]
                text = '\n\n'.join(p[1] for p in chunk)
                latex = self._text_to_chapter(text, f"Capítulo {i//chunk_size + 1}")
                filename = f"capitulo_{(i//chunk_size)+1:02d}_detectado.tex"
                (self.chapters_dir / filename).write_text(latex, encoding="utf-8")

    def _section_to_latex(self, title: str, line: str, nivel: str = "chapter") -> str:
        """Converte uma seção detectada para LaTeX."""
        lines = []
        # Limpar título
        clean_title = re.sub(r'^\d+\s+', '', title).strip()
        clean_title = re.sub(r'^\d+\.\d+\s+', '', clean_title).strip()

        # Inserir comando de capítulo/seção
        if nivel == "chapter":
            lines.append(f"\\chapter{{{clean_title}}}")
        elif nivel == "section":
            lines.append(f"\\section{{{clean_title}}}")
        else:
            lines.append(f"\\subsection{{{clean_title}}}")

        lines.append("")
        lines.append(self._extract_content_after(line))
        lines.append("")

        # Inserir figuras encontradas para esta página
        lines.extend(self._get_figures_for_section(title))

        # Inserir tabelas encontradas
        lines.extend(self._get_tables_for_section(title))

        # Inserir equações encontradas
        lines.extend(self._get_equations_for_section(title))

        return '\n'.join(lines)

    def _text_to_chapter(self, text: str, title: str) -> str:
        """Converte texto bruto em capítulo LaTeX."""
        lines = []
        lines.append(f"\\chapter{{{title}}}")
        lines.append("")

        # Processar parágrafos
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            # Verificar se é equação
            is_eq = any(eq[0] in para for eq in self.equations)
            if is_eq:
                lines.append(para)
            elif len(para) > 100:
                lines.append(para)
                lines.append("")

        return '\n'.join(lines)

    def _extract_content_after(self, line: str) -> str:
        """Extrai o conteúdo textual que segue um título de seção."""
        # Buscar no texto completo o parágrafo após esta linha
        idx = self.text_content.find(line)
        if idx < 0:
            return "Conteúdo extraído automaticamente do PDF original."

        # Pegar até 2000 caracteres após
        start = idx + len(line)
        end = min(start + 2000, len(self.text_content))
        content = self.text_content[start:end].strip()

        # Limitar ao próximo título de seção usando padrões inline
        section_breaks = [
            r'^\d+\s+[A-ZÀ-Ú][A-ZÀ-Ú\s]+$',
            r'^\d+\.\d+\s+[A-ZÀ-Ú][A-ZÀ-Úa-zà-ú\s]+$',
            r'^#{2,3}\s+.+$',
            r'^Chapter\s+\d+',
        ]
        for pattern in section_breaks:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                content = content[:match.start()].strip()
                break

        # Limpar excesso de whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Escapar caracteres especiais LaTeX
        content = self._escape_latex(content)

        return content

    def _get_figures_for_section(self, title: str) -> List[str]:
        """Retorna comandos \\includegraphics para figuras próximas a esta seção."""
        fig_cmds = []
        img_idx = 1
        for img_path, page, caption in self.images:
            if img_path.exists():
                rel_path = f"figures/{img_path.name}"
                fig_cmds.append("")
                fig_cmds.append(r"\begin{figure}[h]")
                fig_cmds.append(r"\centering")
                fig_cmds.append(f"\\includegraphics[width=0.8\\textwidth]{{{rel_path}}}")
                fig_cmds.append(f"\\caption{{{caption}}}")
                fig_cmds.append(r"\label{fig:extraida_" + str(img_idx) + "}")
                fig_cmds.append(r"\end{figure}")
                fig_cmds.append("")
                img_idx += 1
                if img_idx > 3:  # Máximo 3 figuras por seção
                    break
        return fig_cmds

    def _get_tables_for_section(self, title: str) -> List[str]:
        """Retorna código de tabelas para esta seção."""
        table_cmds = []
        for latex_code, caption, page in self.tables[:2]:
            table_cmds.append("")
            table_cmds.append(latex_code)
            table_cmds.append("")
        return table_cmds

    def _get_equations_for_section(self, title: str) -> List[str]:
        """Retorna equações para esta seção."""
        eq_cmds = []
        for eq, page in self.equations[:3]:
            eq_cmds.append("")
            eq_cmds.append(eq)
            eq_cmds.append("")
        return eq_cmds

    def _generate_main_tex(self):
        """Gera o arquivo main.tex principal."""
        # Coletar capítulos gerados
        chapter_files = sorted(self.chapters_dir.glob("*.tex"))

        main = []
        main.append(r"% ============================================")
        main.append(r"% Projeto LaTeX gerado automaticamente via pdf2latex")
        main.append(f"% Fonte: {self.pdf_name}.pdf")
        main.append(r"% Data: 2026-07-09")
        main.append(r"% Ferramenta: OpenCode Ecosystem Core -- SPEC-962")
        main.append(r"% ============================================")
        main.append("")
        main.append(r"\documentclass[12pt,a4paper]{article}")
        main.append("")

        # Pacotes essenciais
        main.append(r"% ---- PACOTES ESSENCIAIS ----")
        main.append(r"\usepackage[utf8]{inputenc}")
        main.append(r"\usepackage[T1]{fontenc}")
        main.append(r"\usepackage[brazil]{babel}")
        main.append(r"\usepackage{graphicx}")
        main.append(r"\usepackage{amsmath,amssymb,amsfonts}")
        main.append(r"\usepackage{booktabs}")
        main.append(r"\usepackage{hyperref}")
        main.append(r"\usepackage{geometry}")
        main.append(r"\geometry{a4paper, margin=2.5cm}")
        main.append(r"\usepackage{indentfirst}")
        main.append(r"\usepackage{setspace}")
        main.append(r"\usepackage{tabularx}")
        main.append(r"\usepackage{longtable}")
        main.append(r"\usepackage{caption}")
        main.append(r"\usepackage{subcaption}")
        main.append(r"\usepackage{xcolor}")
        main.append("")

        # Configurações
        main.append(r"% ---- CONFIGURAÇÕES ----")
        main.append(r"\onehalfspacing")
        main.append(r"\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}")
        main.append("")

        # Metadados
        clean_name = self._clean_title(self.pdf_name)
        main.append(r"\title{" + clean_name + "}")
        main.append(r"\author{Extraído automaticamente via pdf2latex}")
        main.append(r"\date{\today}")
        main.append("")

        main.append(r"\begin{document}")
        main.append("")
        main.append(r"\maketitle")
        main.append(r"\tableofcontents")
        main.append(r"\newpage")
        main.append("")

        # Incluir capítulos
        for ch_file in chapter_files:
            rel_path = f"capitulos/{ch_file.name}"
            main.append(f"\\include{{{rel_path.replace('.tex', '')}}}")
            main.append("")

        main.append("")
        # Incluir bibliografia (se houver)
        if self.references:
            main.append(r"\bibliographystyle{abntex2-num}")
            main.append(r"\bibliography{referencias}")
            main.append("")

        main.append(r"\end{document}")
        main.append("")

        (self.output_dir / "main.tex").write_text(
            '\n'.join(main), encoding="utf-8"
        )

    def _generate_bibliography(self):
        """Gera arquivo .bib com as referências extraídas."""
        if not self.references:
            return

        bib_lines = []
        bib_lines.append(r"% Referências extraídas automaticamente via pdf2latex")
        bib_lines.append(r"% Fonte: " + self.pdf_name + ".pdf")
        bib_lines.append("")

        for cite_key, bib_entry in self.references:
            bib_lines.append(bib_entry)

        # Também adicionar em formato abntex2
        bib_lines.append("")
        bib_lines.append(r"% ============================================")
        bib_lines.append(r"% Referências no formato ABNT (extraídas do PDF)")
        bib_lines.append(r"% ============================================")
        for cite_key, bib_entry in self.references:
            bib_lines.append(bib_entry)

        (self.output_dir / "referencias.bib").write_text(
            '\n'.join(bib_lines), encoding="utf-8"
        )

    def _generate_makefile(self):
        """Gera Makefile para compilação."""
        makefile = f"""# Makefile para compilação do projeto LaTeX
# Gerado automaticamente via pdf2latex — OpenCode Ecosystem Core

TEX = main.tex
AUX = main.aux
PDF = main.pdf

all: pdf

pdf:
\tlatexmk -pdf -interaction=nonstopmode $(TEX)

quick:
\tpdflatex -interaction=nonstopmode $(TEX)

clean:
\tlatexmk -c
\trm -f *.bbl *.blg *.run.xml *.synctex.gz

purge: clean
\trm -f $(PDF)

view: pdf
\topen $(PDF) 2>/dev/null || xdg-open $(PDF) 2>/dev/null || echo "Abra: $(PDF)"

# Compilação manual passo a passo
manual:
\tpdflatex -interaction=nonstopmode $(TEX)
\tbibtex $(AUX) 2>/dev/null || true
\tpdflatex -interaction=nonstopmode $(TEX)
\tpdflatex -interaction=nonstopmode $(TEX)

.PHONY: all pdf quick clean purge view manual
"""
        (self.output_dir / "Makefile").write_text(makefile, encoding="utf-8")

    def _generate_readme(self):
        """Gera README do projeto."""
        readme = f"""# Projeto LaTeX: {self._clean_title(self.pdf_name)}

> Gerado automaticamente por **pdf2latex** — OpenCode Ecosystem Core
> Fonte: `{self.pdf_name}.pdf`
> SPEC-962

## Estrutura do Projeto

```
.
├── main.tex              # Arquivo principal
├── Makefile              # Comandos de compilação
├── referencias.bib       # Referências extraídas
├── README.md             # Este arquivo
├── capitulos/            # Capítulos em arquivos separados
│   ├── 00_*.tex
│   ├── capitulo_01_*.tex
│   └── ...
└── figures/              # Figuras extraídas
    ├── fig_*.png
    └── ...
```

## Compilar

```bash
make          # Compilar completo
make quick    # Apenas pdflatex
make clean    # Limpar arquivos auxiliares
make view     # Abrir PDF gerado
```

## Estatísticas

- Total de capítulos: {len(list(self.chapters_dir.glob("*.tex")))}
- Total de figuras: {len(self.images)}
- Total de tabelas: {len(self.tables)}
- Total de equações: {len(self.equations)}
- Total de referências: {len(self.references)}

## Template

Para aplicar um template LaTeX do ecossistema:
```bash
python3 -m pdf2latex.template_integrator --project . --template abntex2
```

Templates disponíveis: `abntex2`, `abnt2025`, `acm`, `ieee`, `nature`, etc.
Veja `templates/README.md` para o catálogo completo.
"""
        (self.output_dir / "README.md").write_text(readme, encoding="utf-8")

    @staticmethod
    def _escape_latex(text: str) -> str:
        """Escapa caracteres especiais LaTeX."""
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    @staticmethod
    def _slugify(text: str) -> str:
        """Converte texto para slug de arquivo."""
        text = text.lower().strip()
        text = re.sub(r'[áàâãä]', 'a', text)
        text = re.sub(r'[éèêë]', 'e', text)
        text = re.sub(r'[íìîï]', 'i', text)
        text = re.sub(r'[óòôõö]', 'o', text)
        text = re.sub(r'[úùûü]', 'u', text)
        text = re.sub(r'[ç]', 'c', text)
        text = re.sub(r'[^a-z0-9]', '_', text)
        text = re.sub(r'_+', '_', text)
        text = text.strip('_')
        return text[:50]  # Limitar tamanho

    @staticmethod
    def _clean_title(name: str) -> str:
        """Limpa nome do PDF para usar como título."""
        name = Path(name).stem
        name = re.sub(r'[_-]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name.title()
