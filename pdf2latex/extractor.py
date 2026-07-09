"""
Extração de texto e detecção de estrutura hierárquica de PDF.
Suporta PDFs nativos (pdftotext/pdfminer) e escaneados (OCR Tesseract).
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import pytesseract
from pdfminer.high_level import extract_text as pdfminer_extract


class TextExtractor:
    """Extrai texto estruturado de PDFs."""

    # Padrões para detectar estrutura hierárquica
    SECTION_PATTERNS = [
        # Formato ABNT: "1 INTRODUÇÃO", "1.1 Fundamentação"
        (re.compile(r'^(\d+)\s+([A-ZÀ-Ú][A-ZÀ-Ú\s]+)$', re.MULTILINE), 'chapter'),
        (re.compile(r'^(\d+\.\d+)\s+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú\s]+)$', re.MULTILINE), 'section'),
        (re.compile(r'^(\d+\.\d+\.\d+)\s+([A-ZÀ-Úa-zà-ú].+)$', re.MULTILINE), 'subsection'),
        # Formato artigo: "## Introdução", "### Método"
        (re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE), 'markdown_header'),
        # Formato "Chapter 1", "Chapter 2"
        (re.compile(r'^(Chapter|CHAPTER)\s+(\d+)\s*[.:]?\s*(.+)$', re.MULTILINE), 'chapter'),
        # "1. Introduction", "2.1 Background"
        (re.compile(r'^(\d+)\.\s+([A-Z][A-Za-z\s]+)$', re.MULTILINE), 'chapter'),
        (re.compile(r'^(\d+\.\d+)\.\s+([A-Z][A-Za-z\s]+)$', re.MULTILINE), 'section'),
        # "Abstract", "Resumo", "Introdução", "Conclusão"
        (re.compile(r'^(ABSTRACT|RESUMO|INTRODUÇÃO|INTRODUCCION|CONCLUSÃO|CONCLUSION|'
                    r'REFERÊNCIAS|REFERENCES|BIBLIOGRAPHY|APÊNDICE|APENDICE|ANNEX|'
                    r'AGRADECIMENTOS|ACKNOWLEDGMENTS|DEDICATÓRIA|EPÍGRAFE)\s*$',
                    re.MULTILINE | re.IGNORECASE), 'special_section'),
    ]

    def __init__(self, pdf_path: Path, ocr: bool = False, ocr_lang: str = "por+eng"):
        self.pdf_path = pdf_path
        self.ocr = ocr
        self.ocr_lang = ocr_lang
        self._raw_text = ""
        self._structure: Dict[str, List[Tuple]] = {
            'chapters': [],
            'sections': [],
            'subsections': [],
            'paragraphs': [],
            'special': [],
        }

    def extract(self) -> str:
        """Extrai texto completo do PDF."""
        if self.ocr:
            return self._extract_ocr()
        return self._extract_native()

    def _extract_native(self) -> str:
        """Extrai texto de PDF nativo (não escaneado)."""
        texts = []

        # Método 1: pdftotext (mais rápido, bom para layout)
        try:
            result = subprocess.run(
                ["pdftotext", "-layout", str(self.pdf_path), "-"],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and result.stdout.strip():
                texts.append(result.stdout)
        except Exception as e:
            pass

        # Método 2: pdfminer (mais preciso, melhor para colunas)
        try:
            text = pdfminer_extract(str(self.pdf_path))
            if text.strip():
                texts.append(text)
        except Exception as e:
            pass

        # Usar o texto mais longo (mais completo)
        self._raw_text = max(texts, key=len) if texts else ""
        self._detect_structure()
        return self._raw_text

    def _extract_ocr(self) -> str:
        """Extrai texto de PDF escaneado usando OCR Tesseract."""
        from pdf2image import convert_from_path

        images = convert_from_path(str(self.pdf_path), dpi=300)
        texts = []

        for i, img in enumerate(images):
            text = pytesseract.image_to_string(
                img,
                lang=self.ocr_lang,
                config='--oem 3 --psm 6'
            )
            texts.append(f"--- PÁGINA {i+1} ---\n{text}")

        self._raw_text = "\n\n".join(texts)
        self._detect_structure()
        return self._raw_text

    def _detect_structure(self):
        """Detecta a estrutura hierárquica do documento."""
        lines = self._raw_text.split('\n')
        current_chapter = ""
        current_section = ""

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            detected = False
            for pattern, level in self.SECTION_PATTERNS:
                match = pattern.search(line_stripped)
                if match:
                    if level == 'chapter':
                        title = match.group(2) if match.lastindex >= 2 else match.group(1)
                        current_chapter = title
                        self._structure['chapters'].append((title, line_stripped))
                    elif level == 'section':
                        title = match.group(2) if match.lastindex >= 2 else match.group(1)
                        current_section = title
                        self._structure['sections'].append((title, line_stripped))
                    elif level == 'subsection':
                        title = match.group(1)
                        self._structure['subsections'].append((title, line_stripped))
                    elif level == 'special_section':
                        self._structure['special'].append((line_stripped, line_stripped))
                    detected = True
                    break

            if not detected and len(line_stripped) > 80:
                self._structure['paragraphs'].append((len(line_stripped), line_stripped))

    def get_structure(self) -> Dict:
        """Retorna a estrutura detectada."""
        return self._structure

    def get_clean_text(self) -> str:
        """Retorna texto limpo (sem cabeçalhos/rodapés duplicados)."""
        lines = self._raw_text.split('\n')
        # Filtra cabeçalhos/rodapés repetidos (heurística simples)
        from collections import Counter
        line_counter = Counter(lines)
        # Remove linhas que aparecem mais de 3 vezes (provavelmente header/footer)
        cleaned = [l for l in lines if line_counter[l] < 3]
        return '\n'.join(cleaned)
