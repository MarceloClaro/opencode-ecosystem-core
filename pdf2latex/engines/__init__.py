"""
Engine Adapter System — múltiplos backends para conversão PDF→LaTeX.

Uso:
    from pdf2latex.engines import get_engine, list_engines

    print(list_engines())
    result = get_engine("builtin").convert("documento.pdf")
"""

# Importar engines para auto-registro
# (engine_registry já está totalmente carregado neste ponto)
from . import builtin  # noqa: F401

try:
    from . import docling_engine  # noqa: F401
except ImportError:
    pass

# ocr-vision: import guardado (só stdlib no topo; deps pesadas são lazy).
try:
    from . import ocr_vision  # noqa: F401
except ImportError:
    pass

# Re-exportar funções do registry
from ..engine_registry import get_engine, list_engines, convert_with_best  # noqa: F401
