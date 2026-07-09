"""
Utilitários para o módulo pdf2latex.
"""

import re
from pathlib import Path


def detect_file_type(filepath: str) -> str:
    """Detecta o tipo de arquivo pela extensão."""
    ext = Path(filepath).suffix.lower()
    types = {
        '.pdf': 'pdf',
        '.ps': 'postscript',
        '.eps': 'eps',
    }
    return types.get(ext, 'unknown')


def safe_filename(text: str, max_len: int = 50) -> str:
    """Converte texto em nome de arquivo seguro."""
    text = text.lower().strip()
    text = re.sub(r'[áàâãä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[íìîï]', 'i', text)
    text = re.sub(r'[óòôõö]', 'o', text)
    text = re.sub(r'[úùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[^a-z0-9_.-]', '_', text)
    text = re.sub(r'_+', '_', text)
    return text[:max_len]


def count_words(text: str) -> int:
    """Conta palavras em um texto."""
    return len(text.split())


def estimate_pages(text: str, words_per_page: int = 350) -> int:
    """Estima número de páginas a partir do texto."""
    word_count = count_words(text)
    return max(1, word_count // words_per_page)
