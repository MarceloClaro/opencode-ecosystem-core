"""
pdf2latex — Conversão Inteligente de PDF para Projeto LaTeX
=============================================================

Orquestrador principal do pipeline de conversão.
Parte do OpenCode Ecosystem Core — SPEC-962.

Suporta múltiplos engines de conversão:
  - builtin: pdfminer + pdftotext + Tesseract (padrão, offline)
  - docling: IBM Docling (layout avançado, alta precisão)
  - mineru : MinerU (precisão máxima, requer GPU)

Suporta múltiplos renderizadores LaTeX:
  - builtin: LaTeXGenerator + TemplateIntegrator (sem dependências)
  - pandoc : Pandoc + templates Lua + citeproc (alta qualidade)

Uso:
    from pdf2latex import PDF2LaTeX
    conv = PDF2LaTeX("documento.pdf", engine="builtin", renderer="pandoc")
    conv.convert(output_dir="./projeto", template="abntex2")
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Engine registry (auto-registro acontece ao importar engines)
from . import engines  # noqa: F401
from .engine_registry import get_engine, list_engines, convert_with_best

from .extractor import TextExtractor
from .image_extractor import ImageExtractor
from .table_detector import TableDetector
from .equation_detector import EquationDetector
from .reference_parser import ReferenceParser
from .latex_generator import LaTeXGenerator
from .template_integrator import TemplateIntegrator
from .renderers import BuiltinRenderer, PandocRenderer
from .renderers.base import RenderInput

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
        engine: str = "auto",
        renderer: str = "builtin",
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
        self.engine_name = engine
        self.engine = None
        self.renderer_name = renderer
        self._renderer = self._init_renderer()

        # Configurar logging
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="[pdf2latex] %(levelname)s: %(message)s",
        )

        # Validações
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

        # Inicializar engine
        self._init_engine()

        # Estado interno
        self.text_content = ""
        self.structure = {}       # {tipo: [(titulo, nivel, texto), ...]}
        self.images = []          # [(caminho, pagina, legenda), ...]
        self.tables = []          # [(latex_tabular, legenda, pagina), ...]
        self.equations = []       # [(latex_equation, pagina), ...]
        self.references = []      # [(cite_key, entry_bibtex), ...]

        logger.info(f"PDF2LaTeX inicializado: {pdf_path}")
        logger.info(f"Engine: {self.engine_name} | Renderer: {self.renderer_name}")

    def _init_renderer(self):
        """Inicializa o renderizador LaTeX."""
        if self.renderer_name == "pandoc":
            r = PandocRenderer()
            if r.is_available():
                logger.info("Renderer: Pandoc (alta qualidade)")
                return r
            logger.warning("Pandoc não disponível. Usando builtin.")
        return BuiltinRenderer()

    def _init_engine(self):
        """Inicializa o engine de conversão."""
        if self.engine_name == "auto":
            # Auto-selecionar melhor engine disponível
            available = [e for e in list_engines() if e["available"]]
            if not available:
                logger.warning("Nenhum engine disponível! Usando builtin.")
                self.engine = get_engine("builtin")
                self.engine_name = "builtin"
                return

            # Ordem de preferência
            preferred = ["docling", "mineru", "builtin"]
            for name in preferred:
                engine = get_engine(name)
                if engine and engine.is_available():
                    self.engine = engine
                    self.engine_name = name
                    logger.info(f"Engine auto-selecionado: {name}")
                    return

            # Fallback
            self.engine = get_engine(available[0]["name"])
            self.engine_name = available[0]["name"]
        else:
            self.engine = get_engine(self.engine_name)
            if not self.engine:
                raise ValueError(
                    f"Engine '{self.engine_name}' não encontrado. "
                    f"Disponíveis: {[e['name'] for e in list_engines()]}"
                )
            if not self.engine.is_available():
                logger.warning(
                    f"Engine '{self.engine_name}' não está disponível "
                    "(dependências faltando). Usando builtin como fallback."
                )
                self.engine = get_engine("builtin")
                self.engine_name = "builtin"

    def convert(self, output_dir: Optional[str] = None, template: Optional[str] = None):
        """Executa o pipeline completo de conversão."""
        if output_dir:
            self.output_dir = Path(output_dir)
        if template:
            self.template = template

        logger.info("=" * 60)
        logger.info(f"INICIANDO PIPELINE PDF → LATEX (engine: {self.engine_name})")
        logger.info("=" * 60)

        if self.engine_name != "builtin":
            # Usar engine externo (alta precisão)
            self._convert_with_external_engine()
        else:
            # Usar pipeline builtin completo
            self._convert_with_builtin()

        logger.info("=" * 60)
        logger.info(f"✅ CONVERSÃO CONCLUÍDA: {self.output_dir}")
        logger.info("=" * 60)

        return self.output_dir

    def _convert_with_external_engine(self):
        """Usa engine externo para extração de alta precisão."""
        logger.info(f"🔧 Usando engine: {self.engine_name}")

        try:
            result = self.engine.convert(self.pdf_path, ocr=self.ocr, ocr_lang=self.ocr_lang)
            self.text_content = result.text_content
            self.structure = result.structure
            self.images = result.images
            self.tables = result.tables
            self.equations = result.equations
            self.references = result.references

            # Se o engine não extraiu imagens, usar extrator builtin
            if not self.images and self.extract_images_flag:
                logger.info("→ Engine não extraiu imagens. Usando extrator builtin.")
                extractor = ImageExtractor(self.pdf_path, self.output_dir / "figures")
                self.images = extractor.extract()

            logger.info(f"   → {len(self.text_content)} caracteres extraídos")
            logger.info(f"   → Confiança do engine: {result.confidence:.1%}")

        except Exception as e:
            logger.error(f"Erro no engine '{self.engine_name}': {e}")
            logger.info("→ Fallback para engine builtin...")
            self._convert_with_builtin()
            return

        # Renderizar com o renderizador selecionado
        self._render_project()

    def _convert_with_builtin(self):
        """Pipeline completo usando engine builtin."""
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

        # Renderizar com o renderizador selecionado
        self._render_project()

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

    def _render_project(self):
        """Renderiza o projeto usando o renderizador selecionado."""
        logger.info(f"📝 Renderizando LaTeX (renderer: {self.renderer_name})...")

        render_input = RenderInput(
            pdf_name=self.pdf_path.stem,
            text_content=self.text_content,
            structure=self.structure,
            images=self.images,
            tables=self.tables,
            equations=self.equations,
            references=self.references,
            template=self.template,
            output_dir=self.output_dir,
        )

        output_dir = self._renderer.render(render_input)
        logger.info(f"   → Projeto gerado em: {output_dir}")

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
