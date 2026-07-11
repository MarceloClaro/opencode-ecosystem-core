"""
Interface abstrata para renderizadores LaTeX.
Cada renderizador converte dados extraídos (texto + estrutura) em projeto LaTeX.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class RenderInput:
    """Dados de entrada padronizados para qualquer renderizador."""
    pdf_name: str
    text_content: str
    structure: Dict = field(default_factory=dict)
    images: List[Tuple] = field(default_factory=list)
    tables: List[Tuple] = field(default_factory=list)
    equations: List[Tuple] = field(default_factory=list)
    references: List[Tuple] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    template: Optional[str] = None
    output_dir: Optional[Path] = None


class BaseRenderer(ABC):
    """Classe base para renderizadores."""

    name = "base"
    description = "Renderer base abstrato"

    @abstractmethod
    def render(self, data: RenderInput) -> Path:
        """Renderiza dados de entrada em projeto LaTeX.
        Retorna o caminho do diretório do projeto gerado.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o renderizador está disponível."""
        ...

    def get_metadata(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "available": self.is_available(),
        }
