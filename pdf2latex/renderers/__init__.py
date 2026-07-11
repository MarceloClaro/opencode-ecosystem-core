"""
Sistema de Renderizadores — múltiplos backends para gerar LaTeX.

Fluxo: Engine (extrai PDF) → Dados Estruturados → Renderer → LaTeX

Renderers disponíveis:
  - builtin : LaTeXGenerator (atual, sem dependências)
  - pandoc  : Pandoc + templates Lua (alta qualidade, requer pandoc)
"""

from .builtin_renderer import BuiltinRenderer
from .pandoc_renderer import PandocRenderer
