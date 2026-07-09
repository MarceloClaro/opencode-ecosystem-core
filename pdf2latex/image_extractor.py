"""
Extração de figuras e imagens de PDFs.
Usa PyMuPDF (fitz) e pdfimages (poppler).
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

import fitz  # PyMuPDF


class ImageExtractor:
    """Extrai imagens de arquivos PDF."""

    def __init__(self, pdf_path: Path, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract(self) -> List[Tuple[Path, int, str]]:
        """
        Extrai todas as imagens do PDF.
        Retorna: [(caminho_imagem, numero_pagina, legenda_sugerida), ...]
        """
        images = []

        # Método 1: pdfimages (poppler) — extrai todas as imagens nativas
        images += self._extract_with_pdfimages()

        # Método 2: PyMuPDF — captura páginas como imagem (fallback)
        if not images:
            images += self._capture_pages_as_images()

        return images

    def _extract_with_pdfimages(self) -> List[Tuple]:
        """Usa pdfimages para extrair imagens nativas do PDF."""
        images = []
        try:
            prefix = str(self.output_dir / "img")
            subprocess.run(
                ["pdfimages", "-png", "-j", str(self.pdf_path), prefix],
                capture_output=True, timeout=120
            )

            # Listar imagens extraídas
            img_files = sorted(self.output_dir.glob("img-*.png"))
            img_files += sorted(self.output_dir.glob("img-*.jpg"))

            for i, img_path in enumerate(img_files):
                pagina = self._guess_page_from_filename(str(img_path))
                images.append((img_path, pagina, f"figura_{i+1}"))

        except Exception as e:
            pass

        return images

    def _capture_pages_as_images(self) -> List[Tuple]:
        """Captura páginas do PDF como imagens usando PyMuPDF."""
        images = []
        try:
            doc = fitz.open(str(self.pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Verificar se a página tem imagens
                image_list = page.get_images(full=True)
                for img_idx, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    img_filename = f"fig_p{page_num+1}_{img_idx+1}.{ext}"
                    img_path = self.output_dir / img_filename
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                    images.append((img_path, page_num + 1, f"figura_p{page_num+1}"))

                # Se não encontrou imagens embutidas, capturar página inteira
                if not image_list and page_num < 5:  # só primeiras páginas
                    pix = page.get_pixmap(dpi=200)
                    img_path = self.output_dir / f"page_{page_num+1}.png"
                    pix.save(str(img_path))
                    images.append((img_path, page_num + 1, f"pagina_{page_num+1}"))

            doc.close()
        except Exception as e:
            pass

        return images

    def _guess_page_from_filename(self, filename: str) -> int:
        """Tenta adivinhar o número da página a partir do nome do arquivo."""
        match = re.search(r'-(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0
