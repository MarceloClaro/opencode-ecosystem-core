"""
pdf2latex — Conversão Inteligente de PDF para Projeto LaTeX
=============================================================

Orquestrador principal do pipeline de conversão.
Parte do OpenCode Ecosystem Core — SPEC-962.

Uso:
    from pdf2latex import PDF2LaTeX
    conv = PDF2LaTeX("documento.pdf")
    conv.convert(output_dir="./projeto", template="abntex2")
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

from .extractor import TextExtractor
from .image_extractor import ImageExtractor
from .table_detector import TableDetector
from .equation_detector import EquationDetector
from .reference_parser import ReferenceParser
from .latex_generator import LaTeXGenerator
from .template_integrator import TemplateIntegrator

logger = logging.getLogger("pdf2latex")


class PDF2LaTeX:
    """Orquestrador principal do pipeline PDF → LaTeX."""

    def __init__(
        self,
        pdf_path: str,
        output_dir: str = "./projeto-latex",
        template: Optional[str] = None,
        ocr: bool = False,
        ocr_lang: str = "por+eng",
        extract_tables: bool = True,
        extract_equations: bool = True,
        extract_references: bool = True,
        extract_images: bool = True,
        verbose: bool = False,
    ):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.template = template
        self.ocr = ocr
        self.ocr_lang = ocr_lang
        self.extract_tables = extract_tables
        self.extract_equations = extract_equations
        self.extract_references = extract_references
        self.extract_images_flag = extract_images

        # Configurar logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="[pdf2latex] %(levelname)s: %(message)s",
        )

        # Validações
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

        # Estado interno
        self.text_content = ""
        self.structure = {}       # {tipo: [(titulo, nivel, texto), ...]}
        self.images = []          # [(caminho, pagina, legenda), ...]
        self.tables = []          # [(latex_tabular, legenda, pagina), ...]
        self.equations = []       # [(latex_equation, pagina), ...]
        self.references = []      # [(cite_key, entry_bibtex), ...]

        logger.info(f"PDF2LaTeX inicializado: {pdf_path}")

    def convert(self, output_dir: Optional[str] = None, template: Optional[str] = None):
        """Executa o pipeline completo de conversão."""
        if output_dir:
            self.output_dir = Path(output_dir)
        if template:
            self.template = template

        logger.info("=" * 60)
        logger.info("INICIANDO PIPELINE PDF → LATEX")
        logger.info("=" * 60)

        # Etapa 1: Extrair texto e estrutura
        self.extract_text()

        # Etapa 2: Extrair imagens
        if self.extract_images_flag:
            self.extract_images_from_pdf()

        # Etapa 3: Detectar tabelas
        if self.extract_tables:
            self.detect_tables()

        # Etapa 4: Detectar equações
        if self.extract_equations:
            self.detect_equations()

        # Etapa 5: Extrair referências
        if self.extract_references:
            self.extract_references_from_text()

        # Etapa 6: Gerar projeto LaTeX
        self.generate_latex_project()

        # Etapa 7: Aplicar template
        if self.template:
            self.apply_template()

        logger.info("=" * 60)
        logger.info(f"✅ CONVERSÃO CONCLUÍDA: {self.output_dir}")
        logger.info("=" * 60)

        return self.output_dir

    def extract_text(self):
        """Etapa 1: Extrair texto com estrutura."""
        logger.info("📄 Etapa 1/7: Extraindo texto e estrutura...")
        extractor = TextExtractor(self.pdf_path, ocr=self.ocr, ocr_lang=self.ocr_lang)
        self.text_content = extractor.extract()
        self.structure = extractor.get_structure()
        logger.info(f"   → {len(self.text_content)} caracteres extraídos")
        logger.info(f"   → {sum(len(v) for v in self.structure.values())} blocos estruturais detectados")

    def extract_images_from_pdf(self):
        """Etapa 2: Extrair figuras/imagens."""
        logger.info("🖼️  Etapa 2/7: Extraindo imagens...")
        extractor = ImageExtractor(self.pdf_path, self.output_dir / "figures")
        self.images = extractor.extract()
        logger.info(f"   → {len(self.images)} imagens extraídas")

    def detect_tables(self):
        """Etapa 3: Detectar tabelas."""
        logger.info("📊 Etapa 3/7: Detectando tabelas...")
        detector = TableDetector(self.pdf_path)
        self.tables = detector.detect()
        logger.info(f"   → {len(self.tables)} tabelas detectadas")

    def detect_equations(self):
        """Etapa 4: Detectar equações."""
        logger.info("∑ Etapa 4/7: Detectando equações...")
        detector = EquationDetector(self.text_content)
        self.equations = detector.detect()
        logger.info(f"   → {len(self.equations)} equações detectadas")

    def extract_references_from_text(self):
        """Etapa 5: Extrair referências."""
        logger.info("📚 Etapa 5/7: Extraindo referências...")
        parser = ReferenceParser(self.text_content)
        self.references = parser.parse()
        logger.info(f"   → {len(self.references)} referências extraídas")

    def generate_latex_project(self):
        """Etapa 6: Gerar projeto LaTeX completo."""
        logger.info("📝 Etapa 6/7: Gerando projeto LaTeX...")
        generator = LaTeXGenerator(
            output_dir=self.output_dir,
            pdf_name=self.pdf_path.stem,
            text_content=self.text_content,
            structure=self.structure,
            images=self.images,
            tables=self.tables,
            equations=self.equations,
            references=self.references,
        )
        generator.generate()
        logger.info(f"   → Projeto gerado em: {self.output_dir}")

    def apply_template(self):
        """Etapa 7: Aplicar template LaTeX."""
        logger.info(f"🎨 Etapa 7/7: Aplicando template '{self.template}'...")
        integrator = TemplateIntegrator(
            project_dir=self.output_dir,
            template_name=self.template,
        )
        integrator.apply()
        logger.info(f"   → Template '{self.template}' aplicado com sucesso")

    def compile(self):
        """Compila o projeto LaTeX gerado."""
        logger.info("🔧 Compilando projeto LaTeX...")
        import subprocess
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"],
            cwd=self.output_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info("✅ Compilação bem-sucedida!")
            return True
        else:
            logger.warning("⚠️  Compilação com avisos (ver .log)")
            return False
