"""
Módulo spec — Decorador e ferramentas para Specification-Driven Development.

O SDD (Specification-Driven Development) estabelece que nenhuma
implementação deve ser entregue sem uma especificação formal prévia.

Funções:
    spec         : Decorador que adiciona especificação a uma função
    get_spec     : Recupera a especificação de uma função
    validate_spec : Valida formalmente a especificação
    list_specs    : Lista todas as funções especificadas
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Optional

# Registro global de especificações
_SPEC_REGISTRY: Dict[str, dict] = {}


def spec(
    problem: str,
    input: str,
    output: str,
    criteria: List[str],
    category: str = "geral",
) -> Callable:
    """Decorador que anexa uma especificação formal a uma função.

    A especificação define, de forma contratual, o problema, entradas,
    saídas e critérios de aceitação. Segue o princípio SDD: nada
    implementado sem antes ser especificado.

    Args:
        problem: Descrição do problema odontológico
        input: Descrição da entrada esperada
        output: Descrição da saída produzida
        criteria: Lista de critérios de aceitação verificáveis
        category: Categoria da especificação (ex: 'classificacao',
                  'segmentacao', 'preprocessamento', 'geral')

    Returns:
        Decorador que registra a especificação no registro global

    Example:
        >>> @spec(
        ...     problem="Classificar lesões bucais em radiografias",
        ...     input="ndarray (H, W) uint8 radiografia",
        ...     output="int classe predita + ndarray heatmap",
        ...     criteria=["accuracy > 0.85", "sensitivity > 0.80"]
        ... )
        ... def detect_lesion(img):
        ...     return model.predict(img)
        ...
        >>> spec_data = get_spec(detect_lesion)
        >>> print(spec_data['problem'])
    """
    def decorator(func: Callable) -> Callable:
        spec_data = {
            "function": func.__name__,
            "module": func.__module__,
            "problem": problem,
            "input": input,
            "output": output,
            "criteria": criteria,
            "category": category,
        }

        # Registra no registro global
        qualified_name = f"{func.__module__}.{func.__name__}"
        _SPEC_REGISTRY[qualified_name] = spec_data

        # Anexa ao objeto função como atributo
        func.__spec__ = spec_data

        return func

    return decorator


def get_spec(func: Callable) -> Optional[dict]:
    """Recupera a especificação de uma função decorada com @spec.

    Args:
        func: Função decorada com @spec

    Returns:
        Dicionário com a especificação, ou None se não especificada

    Example:
        >>> spec_data = get_spec(classify_lesion)
        >>> if spec_data:
        ...     print(f"Problema: {spec_data['problem']}")
    """
    return getattr(func, "__spec__", None)


def validate_spec(func: Callable) -> dict:
    """Valida a especificação de uma função decorada com @spec.

    Verifica se:
        - A especificação existe
        - Todos os campos obrigatórios estão preenchidos
        - Os critérios são strings não vazias
        - A função possui docstring (recomendado)

    Args:
        func: Função decorada com @spec

    Returns:
        Dicionário com status da validação:
            - valid: bool
            - errors: list[str]
            - warnings: list[str]

    Example:
        >>> result = validate_spec(classify_lesion)
        >>> print(f"Válida: {result['valid']}")
    """
    spec_data = get_spec(func)
    errors = []
    warnings = []

    if spec_data is None:
        return {"valid": False, "errors": ["Função não possui especificação"], "warnings": []}

    # Campos obrigatórios
    required_fields = ["problem", "input", "output", "criteria"]
    for field in required_fields:
        value = spec_data.get(field)
        if not value:
            errors.append(f"Campo obrigatório '{field}' está vazio")
        elif isinstance(value, list) and len(value) == 0:
            errors.append(f"Lista '{field}' está vazia")

    # Critérios devem ser strings
    for i, criterion in enumerate(spec_data.get("criteria", [])):
        if not isinstance(criterion, str) or not criterion.strip():
            errors.append(f"Criterio {i} inválido: deve ser string não vazia")

    # Warnings
    doc = inspect.getdoc(func)
    if not doc:
        warnings.append("Função não possui docstring")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "spec": spec_data,
    }


def list_specs(category: Optional[str] = None) -> Dict[str, dict]:
    """Lista todas as funções especificadas no registro global.

    Args:
        category: Se fornecida, filtra por categoria

    Returns:
        Dicionário {função_qualificada: spec_data}

    Example:
        >>> all_specs = list_specs()
        >>> for name, data in all_specs.items():
        ...     print(f"{name}: {data['problem'][:50]}")
    """
    if category is None:
        return dict(_SPEC_REGISTRY)
    return {
        name: data
        for name, data in _SPEC_REGISTRY.items()
        if data.get("category") == category
    }