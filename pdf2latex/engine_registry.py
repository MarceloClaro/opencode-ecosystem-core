"""
Registro central de engines de conversão PDF→LaTeX.

Separado do __init__.py para evitar imports circulares.
Usa forward reference (string) para o tipo BaseEngine.
"""

from typing import Any, Dict, List, Optional


class _EngineRegistry:
    """Registro singleton de engines."""

    def __init__(self):
        self._engines: Dict[str, Any] = {}

    def register(self, engine) -> None:
        """Registra um engine."""
        self._engines[engine.name] = engine

    def get(self, name: str):
        """Retorna um engine pelo nome."""
        return self._engines.get(name)

    def list(self) -> List[Dict]:
        """Lista todos os engines com metadados."""
        return [
            {
                "name": e.name,
                "description": getattr(e, 'description', ''),
                "available": e.is_available(),
                "requires_gpu": getattr(e, 'requires_gpu', False),
            }
            for e in self._engines.values()
        ]

    def best(self, preferred_order=None):
        """Retorna o melhor engine disponível."""
        if preferred_order is None:
            preferred_order = ["docling", "mineru", "builtin"]
        for name in preferred_order:
            engine = self._engines.get(name)
            if engine and engine.is_available():
                return engine
        # Fallback
        for name, engine in self._engines.items():
            if engine.is_available():
                return engine
        return None


# Singleton
_registry = _EngineRegistry()

# API pública
register_engine = _registry.register
get_engine = _registry.get
list_engines = _registry.list


def convert_with_best(pdf_path, **kwargs):
    """Auto-seleciona o melhor engine disponível e converte."""
    engine = _registry.best()
    if not engine:
        raise RuntimeError("Nenhum engine de conversão disponível!")
    result = engine.convert(pdf_path, **kwargs)
    result.engine_used = engine.name
    return result
