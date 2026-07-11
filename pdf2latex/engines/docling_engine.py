"""
Engine Docling — conversão PDF→LaTeX usando IBM Docling.

Docling é um motor de análise de documentos de alta precisão da IBM,
que preserva layout, tabelas, fórmulas, figuras e ordem de leitura.

Requer: pip install docling
Documentação: https://github.com/docling-project/docling
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .base import BaseEngine, ConversionResult
from ..engine_registry import register_engine


class DoclingEngine(BaseEngine):
    """
    Engine de conversão usando IBM Docling.
    
    Preserva layout avançado: tabelas complexas, fórmulas LaTeX,
    ordem de leitura multi-coluna, figuras com legendas.
    """

    name = "docling"
    description = (
        "IBM Docling: análise de layout avançado, tabelas, fórmulas, "
        "ordem de leitura multi-coluna. Precisão superior sem GPU."
    )
    requires_gpu = False       # CPU-only funciona
    requires_api_key = False
    min_ram_mb = 1024          # ~1GB RAM mínimo

    def __init__(self):
        self._converter = None

    def _lazy_init(self):
        """Inicialização tardia (import pesado)."""
        if self._converter is not None:
            return
        from docling.document_converter import DocumentConverter
        self._converter = DocumentConverter()

    def convert(self, pdf_path: Path, **kwargs) -> ConversionResult:
        """Converte PDF usando Docling."""
        self._lazy_init()

        # Converter documento
        result = self._converter.convert(str(pdf_path))
        doc = result.document

        # Exportar para markdown (base para LaTeX)
        md_content = doc.export_to_markdown()

        # Extrair texto puro
        text_content = doc.export_to_text() or md_content

        # Extrair estrutura do documento
        structure = self._extract_structure(doc, md_content)

        # Extrair metadados
        metadata = {
            "pages": len(doc.pages) if hasattr(doc, 'pages') else 0,
            "title": Path(pdf_path).stem,
            "producer": "docling",
            "docling_version": getattr(doc, 'version', 'desconhecida'),
        }
        if hasattr(doc, 'name') and doc.name:
            metadata['title'] = doc.name

        return ConversionResult(
            text_content=text_content,
            structure=structure,
            metadata=metadata,
            engine_used=self.name,
            confidence=0.85,  # Docling tem alta precisão
        )

    def is_available(self) -> bool:
        """Verifica se Docling está instalado."""
        try:
            import docling  # noqa
            return True
        except ImportError:
            return False

    def _extract_structure(self, doc, md_content: str) -> Dict:
        """Extrai estrutura hierárquica do Docling."""
        structure = {
            'docling_tables': [],
            'docling_formulas': [],
            'docling_figures': [],
            'chapters': [],
            'sections': [],
            'paragraphs': [],
            'special': [],
        }

        # Extrair tabelas do Docling
        if hasattr(doc, 'tables') and doc.tables:
            for table in doc.tables:
                try:
                    html = table.export_to_html() if hasattr(table, 'export_to_html') else ""
                    caption = table.caption if hasattr(table, 'caption') else ""
                    structure['docling_tables'].append({
                        "html": html,
                        "caption": caption,
                        "page": getattr(table, 'page', 0),
                    })
                except Exception:
                    pass

        # Extrair fórmulas do Docling
        if hasattr(doc, 'formulas') and doc.formulas:
            for formula in doc.formulas:
                try:
                    latex = getattr(formula, 'latex', '')
                    if latex:
                        structure['docling_formulas'].append({
                            "latex": latex,
                            "page": getattr(formula, 'page', 0),
                        })
                except Exception:
                    pass

        # Extrair figuras
        if hasattr(doc, 'pictures') and doc.pictures:
            for pic in doc.pictures:
                try:
                    caption = getattr(pic, 'caption', '') or ''
                    structure['docling_figures'].append({
                        "caption": caption,
                        "page": getattr(pic, 'page', 0),
                        "bbox": str(getattr(pic, 'bbox', '')),
                    })
                except Exception:
                    pass

        return structure


# Auto-registro
register_engine(DoclingEngine())
