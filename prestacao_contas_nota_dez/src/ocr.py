# -*- coding: utf-8 -*-
"""
OCR de PDFs escaneados (Epson Scan 2) com cache por página
===========================================================
Converte cada página de um PDF-imagem em texto via pdftoppm + tesseract,
com cache em JSON para não repetir trabalho entre execuções.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

_LANG = "por"
_PSM = "6"
_DPI = 200


def _tem_pdftoppm() -> bool:
    return shutil.which("pdftoppm") is not None


def _tem_tesseract() -> bool:
    return shutil.which("tesseract") is not None


def _paginas_pdf(pdf_path: Path) -> int:
    """Número de páginas via pdfinfo (fallback: conta via pdftoppm)."""
    info = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True, timeout=60
    )
    for linha in info.stdout.splitlines():
        if linha.lower().startswith("pages"):
            try:
                return int(linha.split(":")[1].strip())
            except (IndexError, ValueError):
                break
    return 0


def _ocr_pagina(png: Path) -> str:
    out = Path(str(png) + ".txt")
    subprocess.run(
        ["tesseract", str(png), str(out), "-l", _LANG, "--psm", _PSM],
        capture_output=True,
        timeout=180,
    )
    return out.read_text(encoding="utf-8", errors="ignore") if out.exists() else ""


def ocr_pdf(pdf_path: Path, cache_dir: Path | None = None, workers: int = 4) -> Dict[int, str]:
    """OCR completo de um PDF-imagem, com cache opcional.

    Returns: {num_pagina (1-based): texto}. Requer ``pdftoppm`` e ``tesseract``
    (com o idioma instalado). Lança ``RuntimeError`` com mensagem clara se uma
    ferramenta faltar.
    """
    if not _tem_pdftoppm():
        raise RuntimeError("pdftoppm não encontrado (poppler-utils).")
    if not _tem_tesseract():
        raise RuntimeError("tesseract não encontrado.")
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    n_paginas = _paginas_pdf(pdf_path)
    cache: Dict[str, str] = {}
    chave_global = f"ocr_{hashlib.sha1(str(pdf_path.resolve()).encode()).hexdigest()[:10]}"
    if cache_dir:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        arquivo_cache = cache_dir / f"{chave_global}.json"
        if arquivo_cache.exists():
            try:
                cache = json.loads(arquivo_cache.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                cache = {}

    faltantes = [i for i in range(1, n_paginas + 1) if str(i) not in cache or not cache[str(i)].strip()]
    if faltantes:
        with tempfile.TemporaryDirectory(prefix="pcn_ocr_") as tmp:
            pagina = 1
            while pagina <= n_paginas:
                # pdftoppm por página é caro; conversão em lote é melhor:
                break
            output_prefix = Path(tmp) / "pg"
            conv = subprocess.run(
                ["pdftoppm", "-r", str(_DPI), "-png", str(pdf_path), str(output_prefix)],
                capture_output=True,
                timeout=600,
            )
            if conv.returncode != 0:
                raise RuntimeError(f"pdftoppm falhou: {conv.stderr.decode(errors='ignore')[:200]}")
            pngs = sorted(Path(tmp).glob("pg-*.png"))
            if len(pngs) != n_paginas:
                # pdfinfo contou N; pdftoppm gerou M; usamos o que existir
                n_paginas = len(pngs)

            def tarefa(i: int, png: Path):
                texto = ""
                try:
                    texto = _ocr_pagina(png)
                except Exception:
                    texto = ""
                return i, texto

            with ThreadPoolExecutor(max_workers=workers) as ex:
                for i, texto in ex.map(tarefa, range(1, len(pngs) + 1), pngs):
                    if texto.strip():
                        cache[str(i)] = texto

    if cache_dir:
        (cache_dir / f"{chave_global}.json").write_text(
            json.dumps(cache, ensure_ascii=False), encoding="utf-8"
        )
    return {int(k): v for k, v in sorted(cache.items(), key=lambda kv: int(kv[0]))}


def texto_por_pagina(ocr: Dict[int, str]) -> List[str]:
    return [ocr.get(i, "") for i in range(1, max(ocr) + 1)] if ocr else []