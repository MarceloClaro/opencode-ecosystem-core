"""
Subpacote 'sdd' — Specification-Driven Development para odontologia.

Fornece o decorador @spec e o validador de especificações, permitindo
que modelos odontológicos sejam formalmente especificados e verificados.

Componentes:
    spec        : Decorador @spec para especificar formalmente funções
    validator   : Validador de especificações

Exemplo:
    >>> from odontoia.sdd import spec
    >>> @spec(problem="classificação de lesões bucais",
    ...       input="imagem radiográfica 256x256",
    ...       output="classe (saudável, cárie, lesão)",
    ...       criteria=["acuracia > 0.90", "sensibilidade > 0.85"])
    ... def classify_lesion(img):
    ...     return model.predict(img)
"""

from odontoia.sdd.spec import spec, get_spec, validate_spec, list_specs
from odontoia.sdd.validator import SpecVerifier, SpecError, verify_all_specs

__all__ = [
    "spec",
    "get_spec",
    "validate_spec",
    "list_specs",
    "SpecVerifier",
    "SpecError",
    "verify_all_specs",
]