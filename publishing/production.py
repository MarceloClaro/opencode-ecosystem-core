"""
Scientific Production Pipeline — Pasta única de produção científica.

Reproduz o padrão do OpenCode_Ecosystem original: toda produção acadêmica
(artigo, dissertação ou livro) gera UMA pasta única e autocontida com:

    producao_cientifica/<slug>-<timestamp>/
    ├── latex/            fonte LaTeX (a partir do template escolhido)
    │   ├── main.tex      esqueleto que inclui as seções
    │   └── sections/     subpasta com cada seção/capítulo em .tex separado
    ├── manuscrito.md     fonte Markdown canônica
    ├── manuscrito.pdf    compilado PDF
    ├── manuscrito.docx   compilado Word
    ├── manuscrito.odt    compilado OpenDocument (extensão aceita no Amazon KDP)
    └── MANIFEST.json     manifesto com metadados, template e checksums

Conversões: usa `pandoc` quando disponível (md → docx/odt/pdf e md → tex);
compila LaTeX com `latexmk`/`pdflatex` quando disponível; sempre degrada
graciosamente registrando no manifesto o que foi ou não gerado.

Templates suportados (publishing/templates/):
- artigo       → artigo_modelo_qualis_a1.tex (Qualis A1, ABNT)
- dissertacao  → dissertacao_modelo_abnt.tex (abnTeX2)
- abntex2      → abntex2-modelo-trabalho-academico.tex
- livro        → victoria_regia | book (Amazon KDP-ready)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
TEMPLATES_DIR = os.path.join(_HERE, "templates")
DEFAULT_OUTPUT_ROOT = os.path.join(_ROOT, "producao_cientifica")

TEMPLATE_MAIN = {
    "artigo": os.path.join("artigo", "artigo_modelo_qualis_a1.tex"),
    "dissertacao": os.path.join("dissertacao", "dissertacao_modelo_abnt.tex"),
    "abntex2": os.path.join("abntex2", "abntex2-modelo-trabalho-academico.tex"),
    "livro": os.path.join("livro", "victoria_regia"),
    "livro-book": os.path.join("livro", "book"),
}

FORMATS = ["pdf", "docx", "md", "odt"]


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "producao"


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class ScientificProduction:
    """
    Pipeline de pasta única de produção científica.

    Uso:
        prod = ScientificProduction(title="Meu Artigo", template="artigo")
        prod.write_markdown(conteudo_md)
        manifest = prod.build()   # gera latex/, pdf, docx, md, odt + MANIFEST
    """

    def __init__(self, title: str, template: str = "artigo",
                 author: str = "Prof. Marcelo Claro",
                 output_root: Optional[str] = None):
        if template not in TEMPLATE_MAIN:
            raise ValueError(
                f"Template desconhecido: {template}. "
                f"Opções: {sorted(TEMPLATE_MAIN)}"
            )
        self.title = title
        self.author = author
        self.template = template
        stamp = time.strftime("%Y%m%d-%H%M%S")
        self.slug = f"{_slugify(title)}-{stamp}"
        root = output_root or DEFAULT_OUTPUT_ROOT
        self.folder = os.path.join(root, self.slug)
        self.latex_dir = os.path.join(self.folder, "latex")
        self.sections_dir = os.path.join(self.latex_dir, "sections")
        self.md_path = os.path.join(self.folder, "manuscrito.md")
        os.makedirs(self.latex_dir, exist_ok=True)
        os.makedirs(self.sections_dir, exist_ok=True)
        self._log: List[str] = []

    # ── Etapa 1: fonte Markdown canônica ──
    def write_markdown(self, content: str) -> str:
        header = f"# {self.title}\n\n**Autor:** {self.author}\n\n"
        body = content if content.lstrip().startswith("#") else header + content
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write(body if body.endswith("\n") else body + "\n")
        self._log.append("markdown: fonte canônica gravada")
        return self.md_path

    # ── Etapa 2: fonte LaTeX modularizada ──
    def _split_markdown(self, content: str) -> Dict[str, str]:
        """Divide o Markdown em seções baseadas em headers H1/H2."""
        sections = {}
        current_section = "preamble"
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('# ') or line.startswith('## '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                title = line.replace('#', '').strip().lower()
                title = ''.join(c if c.isalnum() else '_' for c in title)
                current_section = title or "section"
                current_content = [line]
            else:
                current_content.append(line)
                
        if current_content:
            sections[current_section] = '\n'.join(current_content)
            
        return sections

    def prepare_latex(self) -> str:
        src = os.path.join(TEMPLATES_DIR, TEMPLATE_MAIN[self.template])
        if os.path.isdir(src):
            # template de livro: copia a árvore inteira
            for item in os.listdir(src):
                s, d = os.path.join(src, item), os.path.join(self.latex_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            self._log.append(f"latex: template de livro '{self.template}' copiado")
        else:
            # template de artigo/dissertação: copia diretório do template
            tpl_dir = os.path.dirname(src)
            for item in os.listdir(tpl_dir):
                s = os.path.join(tpl_dir, item)
                if os.path.isfile(s):
                    shutil.copy2(s, os.path.join(self.latex_dir, item))
            self._log.append(f"latex: template '{self.template}' copiado")

        # Lê o markdown para dividir
        with open(self.md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        sections = self._split_markdown(md_content)
        section_files = []
        pandoc = _which("pandoc")

        # Converte cada seção para .tex
        for sec_name, content in sections.items():
            tmp_md = os.path.join(self.sections_dir, f"{sec_name}.md")
            out_tex = os.path.join(self.sections_dir, f"{sec_name}.tex")
            
            with open(tmp_md, "w", encoding="utf-8") as f:
                f.write(content)
                
            if pandoc:
                try:
                    subprocess.run(
                        [pandoc, tmp_md, "-f", "markdown", "-t", "latex", "-o", out_tex],
                        check=True, capture_output=True, timeout=60
                    )
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    # Fallback
                    with open(out_tex, "w", encoding="utf-8") as f:
                        f.write(content)
            else:
                with open(out_tex, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            os.remove(tmp_md)
            section_files.append(f"sections/{sec_name}")

        self._log.append(f"latex: {len(section_files)} seções modularizadas geradas")

        # Gera main.tex
        main_tex = os.path.join(self.latex_dir, "main.tex")
        
        tex_lines = [
            "\\documentclass[12pt,a4paper]{article}",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage[T1]{fontenc}",
            "\\usepackage[brazil]{babel}",
            "\\usepackage{amsmath,amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{hyperref}",
            "",
            f"\\title{{{self.title}}}",
            f"\\author{{{self.author}}}",
            "\\date{\\today}",
            "",
            "\\begin{document}",
            "\\maketitle",
            "\\tableofcontents",
            "\\newpage",
            ""
        ]
        
        for sec in section_files:
            tex_lines.append(f"\\input{{{sec}}}")
            
        tex_lines.append("")
        tex_lines.append("\\end{document}")
        
        with open(main_tex, "w", encoding="utf-8") as f:
            f.write("\n".join(tex_lines))
            
        self._log.append("latex: main.tex gerado com \\input{} modulares")
        return main_tex

    # ── Etapa 3: compilados PDF/DOCX/ODT ──
    def compile_outputs(self) -> Dict[str, Optional[str]]:
        outputs: Dict[str, Optional[str]] = {"md": self.md_path}
        pandoc = _which("pandoc")
        for fmt in ("docx", "odt"):
            out = os.path.join(self.folder, f"manuscrito.{fmt}")
            if pandoc:
                try:
                    subprocess.run(
                        [pandoc, self.md_path, "-o", out],
                        check=True, capture_output=True, timeout=180,
                    )
                    outputs[fmt] = out
                    self._log.append(f"{fmt}: gerado via pandoc")
                    continue
                except (subprocess.CalledProcessError,
                        subprocess.TimeoutExpired) as exc:
                    self._log.append(f"{fmt}: pandoc falhou ({exc})")
            outputs[fmt] = None
            if not pandoc:
                self._log.append(f"{fmt}: pandoc indisponível — pulado")

        outputs["pdf"] = self._compile_pdf(pandoc)
        return outputs

    def _compile_pdf(self, pandoc: Optional[str]) -> Optional[str]:
        out = os.path.join(self.folder, "manuscrito.pdf")
        main_tex = os.path.join(self.latex_dir, "main.tex")
        # 1ª tentativa: latexmk/pdflatex sobre o main.tex
        for engine in ("latexmk", "pdflatex"):
            binpath = _which(engine)
            if binpath and os.path.exists(main_tex):
                cmd = ([binpath, "-pdf", "-interaction=nonstopmode",
                        "-output-directory", self.latex_dir, main_tex]
                       if engine == "latexmk" else
                       [binpath, "-interaction=nonstopmode",
                        "-output-directory", self.latex_dir, main_tex])
                try:
                    subprocess.run(cmd, check=True, capture_output=True,
                                   timeout=300, cwd=self.latex_dir)
                    produced = os.path.join(self.latex_dir, "main.pdf")
                    if os.path.exists(produced):
                        shutil.copy2(produced, out)
                        self._log.append(f"pdf: compilado via {engine}")
                        return out
                except (subprocess.CalledProcessError,
                        subprocess.TimeoutExpired):
                    self._log.append(f"pdf: {engine} falhou; tentando próximo")
        # 2ª tentativa: pandoc md → pdf
        if pandoc:
            for pdf_engine in ("pdflatex", "weasyprint", "wkhtmltopdf"):
                try:
                    subprocess.run(
                        [pandoc, self.md_path, "-o", out,
                         f"--pdf-engine={pdf_engine}"],
                        check=True, capture_output=True, timeout=300,
                    )
                    self._log.append(f"pdf: gerado via pandoc/{pdf_engine}")
                    return out
                except (subprocess.CalledProcessError,
                        subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        # 3ª tentativa: manus-md-to-pdf (disponível no sandbox Manus)
        md2pdf = _which("manus-md-to-pdf")
        if md2pdf:
            try:
                subprocess.run([md2pdf, self.md_path, out],
                               check=True, capture_output=True, timeout=300)
                self._log.append("pdf: gerado via manus-md-to-pdf")
                return out
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass
        self._log.append("pdf: nenhum compilador disponível — pulado")
        return None

    # ── Etapa 4: manifesto ──
    def build(self, markdown_content: Optional[str] = None) -> Dict[str, Any]:
        if markdown_content is not None:
            self.write_markdown(markdown_content)
        if not os.path.exists(self.md_path):
            raise RuntimeError("Chame write_markdown() antes de build().")
        self.prepare_latex()
        
        # Se for um livro, gera a capa, contracapa e ilustrações internas
        cover_report = None
        if self.template.startswith("livro"):
            from .cover_designer import CoverDesigner
            designer = CoverDesigner(os.path.join(self.latex_dir, "cover"))
            with open(self.md_path, "r", encoding="utf-8") as f:
                full_md = f.read()
            cover_report = designer.design_cover(self.title, self.author,
                                                 full_md[:1000])
            self._log.append(f"cover: design gerado (estilo {cover_report['style']})")

            # Internal Illustrator: injeta prompts de ilustração didática
            # nos parágrafos complexos e grava a versão ilustrada
            illustrated = designer.illustrate_internals(full_md,
                                                        cover_report["style"])
            n_prompts = illustrated.count("[ILUSTRAÇÃO DIDÁTICA SUGERIDA]")
            if n_prompts > 0:
                illustrated_path = os.path.join(self.folder,
                                                "manuscrito_ilustrado.md")
                with open(illustrated_path, "w", encoding="utf-8") as f:
                    f.write(illustrated if illustrated.endswith("\n")
                            else illustrated + "\n")
                cover_report["illustrated_manuscript"] = illustrated_path
                cover_report["internal_prompts"] = n_prompts
                self._log.append(
                    f"illustrations: {n_prompts} prompts didáticos internos "
                    f"injetados em manuscrito_ilustrado.md")
            else:
                cover_report["internal_prompts"] = 0
                self._log.append("illustrations: nenhum parágrafo complexo "
                                 "detectado para ilustração interna")
            
        outputs = self.compile_outputs()

        manifest: Dict[str, Any] = {
            "title": self.title,
            "author": self.author,
            "template": self.template,
            "slug": self.slug,
            "folder": self.folder,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "formats": {},
            "kdp_ready": outputs.get("odt") is not None,
            "cover_design": cover_report,
            "log": self._log,
        }
        for fmt in FORMATS:
            path = outputs.get(fmt)
            if path and os.path.exists(path):
                manifest["formats"][fmt] = {
                    "path": os.path.relpath(path, self.folder),
                    "bytes": os.path.getsize(path),
                    "sha256": _sha256(path),
                }
            else:
                manifest["formats"][fmt] = None
        manifest_path = os.path.join(self.folder, "MANIFEST.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        manifest["manifest_path"] = manifest_path
        return manifest


def list_templates() -> Dict[str, str]:
    """Lista os templates LaTeX disponíveis e seus caminhos."""
    return {
        name: os.path.join(TEMPLATES_DIR, rel)
        for name, rel in TEMPLATE_MAIN.items()
    }
