"""
Engine Built-in — conversão PDF→LaTeX usando pdfminer + pdftotext + OCR Tesseract.
Engine padrão, não requer GPU nem API key, funciona offline.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytesseract

try:
    from pdfminer.high_level import extract_text as pdfminer_extract
except ImportError:
    pdfminer_extract = None

from .base import BaseEngine, ConversionResult
from ..engine_registry import register_engine


# Padrões para detectar estrutura hierárquica
SECTION_PATTERNS = [
    # Formato ABNT: "1 INTRODUÇÃO", "1.1 Fundamentação"
    (re.compile(r'^(\d+)\s+([A-ZÀ-Ú][A-ZÀ-Ú\s]+)$', re.MULTILINE), 'chapter'),
    (re.compile(r'^(\d+\.\d+)\s+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú\s]+)$', re.MULTILINE), 'section'),
    (re.compile(r'^(\d+\.\d+\.\d+)\s+([A-ZÀ-Úa-zà-ú].+)$', re.MULTILINE), 'subsection'),
    # Formato markdown
    (re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE), 'markdown_header'),
    # "Chapter 1", "Chapter 2"
    (re.compile(r'^(Chapter|CHAPTER)\s+(\d+)\s*[.:]?\s*(.+)$', re.MULTILINE), 'chapter'),
    # "1. Introduction", "2.1 Background"
    (re.compile(r'^(\d+)\.\s+([A-Z][A-Za-z\s]+)$', re.MULTILINE), 'chapter'),
    (re.compile(r'^(\d+\.\d+)\.\s+([A-Z][A-Za-z\s]+)$', re.MULTILINE), 'section'),
    # Seções especiais
    (re.compile(r'^(ABSTRACT|RESUMO|INTRODUÇÃO|INTRODUCCION|CONCLUSÃO|CONCLUSION|'
                r'REFERÊNCIAS|REFERENCES|BIBLIOGRAPHY|APÊNDICE|APENDICE|ANNEX|'
                r'AGRADECIMENTOS|ACKNOWLEDGMENTS|DEDICATÓRIA|EPÍGRAFE)\s*$',
                re.MULTILINE | re.IGNORECASE), 'special_section'),
]


class BuiltinEngine(BaseEngine):
    """Engine de conversão usando ferramentas nativas (pdfminer + pdftotext + Tesseract)."""

    name = "builtin"
    description = "Engine nativo: pdfminer + pdftotext + OCR Tesseract. Funciona offline, sem GPU."
    requires_gpu = False
    requires_api_key = False
    min_ram_mb = 256

    def __init__(self, ocr: bool = False, ocr_lang: str = "por+eng"):
        self.ocr = ocr
        self.ocr_lang = ocr_lang

    def convert(self, pdf_path: Path, **kwargs) -> ConversionResult:
        """Converte PDF usando o engine builtin."""
        ocr = kwargs.get("ocr", self.ocr)
        ocr_lang = kwargs.get("ocr_lang", self.ocr_lang)

        # 1. Extrair texto
        text_content = self._extract_text(pdf_path, ocr, ocr_lang)

        # 2. Detectar estrutura
        structure = self._detect_structure(text_content)

        # 3. Extrair metadados
        metadata = self._extract_metadata(pdf_path)

        return ConversionResult(
            text_content=text_content,
            structure=structure,
            metadata=metadata,
            engine_used=self.name,
            confidence=0.6,
        )

    def is_available(self) -> bool:
        """Sempre disponível (dependências básicas)."""
        try:
            import pdfminer  # noqa
            return True
        except ImportError:
            return False

    def _extract_text(self, pdf_path: Path, ocr: bool, ocr_lang: str) -> str:
        """Extrai texto do PDF."""
        if ocr:
            return self._extract_ocr(pdf_path, ocr_lang)
        return self._extract_native(pdf_path)

    def _extract_native(self, pdf_path: Path) -> str:
        """Extrai texto de PDF nativo."""
        texts = []

        # Método 1: pdftotext
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), "-"],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and result.stdout.strip():
                texts.append(result.stdout)
        except Exception:
            pass

        # Método 2: pdfminer
        if pdfminer_extract:
            try:
                text = pdfminer_extract(str(pdf_path))
                if text.strip():
                    texts.append(text)
            except Exception:
                pass

        return max(texts, key=len) if texts else ""

    def _extract_ocr(self, pdf_path: Path, ocr_lang: str) -> str:
        """Extrai texto de PDF escaneado usando OCR."""
        try:
            from pdf2image import convert_from_path
        except ImportError:
            return "[ERRO] pdf2image não instalado. Use: pip install pdf2image"

        images = convert_from_path(str(pdf_path), dpi=300)
        texts = []
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(
                img, lang=ocr_lang, config='--oem 3 --psm 6'
            )
            texts.append(f"--- PÁGINA {i+1} ---\n{text}")

        return "\n\n".join(texts)

    def _detect_structure(self, text: str) -> Dict:
        """Detecta estrutura hierárquica do documento."""
        structure = {
            'chapters': [],
            'sections': [],
            'subsections': [],
            'paragraphs': [],
            'special': [],
        }

        lines = text.split('\n')
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            detected = False
            for pattern, level in SECTION_PATTERNS:
                match = pattern.search(line_stripped)
                if match:
                    if level == 'chapter':
                        title = match.group(2) if match.lastindex >= 2 else match.group(1)
                        structure['chapters'].append((title, line_stripped))
                    elif level == 'section':
                        title = match.group(2) if match.lastindex >= 2 else match.group(1)
                        structure['sections'].append((title, line_stripped))
                    elif level == 'subsection':
                        title = match.group(1)
                        structure['subsections'].append((title, line_stripped))
                    elif level == 'special_section':
                        structure['special'].append((line_stripped, line_stripped))
                    detected = True
                    break

            if not detected and len(line_stripped) > 80:
                structure['paragraphs'].append((len(line_stripped), line_stripped))

        return structure

    def _extract_metadata(self, pdf_path: Path) -> Dict:
        """Extrai metadados do PDF."""
        metadata = {
            "pages": 0,
            "title": pdf_path.stem,
            "producer": "",
        }
        try:
            result = subprocess.run(
                ["pdfinfo", str(pdf_path)],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        key_stripped = key.strip().lower()
                        if 'pages' in key_stripped:
                            metadata['pages'] = int(val.strip())
                        elif 'title' in key_stripped:
                            metadata['title'] = val.strip() or pdf_path.stem
        except Exception:
            pass
        return metadata


# Auto-registro
register_engine(BuiltinEngine())
