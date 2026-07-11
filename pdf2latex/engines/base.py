"""
Engine adapter — interface abstrata para backends de conversão PDF→LaTeX.

Permite usar diferentes motores (builtin, Docling, MinerU, GPT-PDF)
com a mesma interface, selecionáveis via CLI ou config.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ConversionResult:
    """Resultado padronizado da conversão PDF→LaTeX."""
    text_content: str                           # Texto extraído completo
    structure: Dict = field(default_factory=dict)  # {
    #   'chapters': [(title, content), ...],
    #   'sections': [(title, content), ...],
    #   'paragraphs': [(idx, text), ...],
    #   'special': [(title, content), ...],
    # }
    images: List[Tuple] = field(default_factory=list)       # [(path, page, caption), ...]
    tables: List[Tuple] = field(default_factory=list)       # [(latex_code, caption, page), ...]
    equations: List[Tuple] = field(default_factory=list)    # [(latex_eq, page), ...]
    references: List[Tuple] = field(default_factory=list)   # [(cite_key, bib_entry), ...]
    metadata: Dict = field(default_factory=dict)            # metadados do PDF
    engine_used: str = "builtin"                            # nome do engine usado
    confidence: float = 0.0                                 # 0.0 a 1.0


class BaseEngine(ABC):
    """Classe base para todos os engines de conversão."""

    name = "base"
    description = "Engine base abstrata"
    requires_gpu = False
    requires_api_key = False
    min_ram_mb = 0

    @abstractmethod
    def convert(self, pdf_path: Path, **kwargs) -> ConversionResult:
        """Converte um PDF para ConversionResult."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o engine está disponível no ambiente."""
        ...

    def get_metadata(self) -> Dict:
        """Retorna metadados do engine."""
        return {
            "name": self.name,
            "description": self.description,
            "requires_gpu": self.requires_gpu,
            "requires_api_key": self.requires_api_key,
            "min_ram_mb": self.min_ram_mb,
            "available": self.is_available(),
        }
