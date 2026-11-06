"""
Módulo validator — Verificador formal de especificações SDD.

Fornece o SpecVerifier para validação programática de especificações
contra implementações reais.

Classes:
    SpecVerifier : Verificador de especificações com suporte a contratos
    SpecError     : Exceção para erro de especificação

Funções:
    verify_all_specs : Verifica todas as especificações registradas
"""

from __future__ import annotations

import inspect
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


class SpecError(Exception):
    """Exceção levantada quando a verificação de especificação falha.

    Attributes:
        message: Descrição do erro
        spec: Especificação que falhou
        detail: Detalhes adicionais
    """

    def __init__(self, message: str, spec: Optional[dict] = None, detail: str = ""):
        self.message = message
        self.spec = spec
        self.detail = detail
        super().__init__(f"{message}\nEspecificação: {spec}\nDetalhe: {detail}")


class SpecVerifier:
    """Verificador de especificações SDD.

    Valida que uma implementação atende aos critérios de aceitação
    definidos na especificação.

    Example:
        >>> from odontoia.sdd import spec
        >>> @spec(problem="soma",
        ...       input="dois inteiros",
        ...       output="inteiro soma",
        ...       criteria=["função deve retornar int"])
        ... def add(a, b):
        ...     return a + b
        >>> verifier = SpecVerifier()
        >>> result = verifier.verify(add, args=(3, 4))
        >>> print(result.valid)

    Attributes:
        strict_mode: Se True, levanta exceção na primeira falha
    """

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self._results: List[dict] = []

    def verify(
        self,
        func: Callable,
        *args,
        test_output: Optional[Any] = None,
        **kwargs,
    ) -> "VerificationResult":
        """Verifica se a implementação atende à especificação.

        Executa a função com os argumentos fornecidos e valida
        o resultado contra a especificação.

        Args:
            func: Função decorada com @spec
            *args: Argumentos posicionais para testar a função
            test_output: Saída esperada (opcional)
            **kwargs: Argumentos nomeados

        Returns:
            VerificationResult com status e detalhes

        Raises:
            SpecError: Se strict_mode=True e houver erro
        """
        from odontoia.sdd.spec import get_spec

        spec_data = get_spec(func)
        errors = []
        warnings = []

        # 1. Verifica se está especificada
        if spec_data is None:
            msg = f"Função '{func.__name__}' não possui especificação @spec"
            errors.append(msg)
            if self.strict_mode:
                raise SpecError(msg)
            return VerificationResult(valid=False, errors=errors)

        # 2. Verifica docstring
        doc = inspect.getdoc(func)
        if not doc:
            warnings.append("Função sem docstring")

        # 3. Executa e verifica tipo de saída
        try:
            result = func(*args, **kwargs)

            # Verifica se o resultado corresponde ao tipo esperado
            output_desc = spec_data.get("output", "").lower()
            if test_output is not None:
                if isinstance(test_output, (int, float)):
                    if not isinstance(result, (int, float)):
                        errors.append(
                            f"Saída esperada tipo numérico, obteve {type(result).__name__}"
                        )
                elif "array" in output_desc and not hasattr(result, "shape"):
                    errors.append("Saída deveria ser array-like")
                elif "classe" in output_desc and not isinstance(result, (int, np.integer)):
                    if isinstance(result, np.ndarray) and result.ndim > 0:
                        pass  # Pode ser one-hot
                    else:
                        errors.append(f"Saída esperada ser classe (int), obteve {type(result).__name__}")

        except Exception as exc:
            errors.append(f"Erro na execução: {exc}")

        # 4. Verifica critérios formais (se parseáveis)
        for criterion in spec_data.get("criteria", []):
            cr = Criterion(criterion)
            if cr.field and not cr.parse():
                warnings.append(f"Criterio não verificável automaticamente: {criterion}")

        result_obj = VerificationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            spec=spec_data,
        )
        self._results.append(result_obj)

        if self.strict_mode and not result_obj.valid:
            raise SpecError(
                "Especificação não validada",
                spec=spec_data,
                detail="; ".join(errors),
            )

        return result_obj

    def summary(self) -> dict:
        """Resumo de todas as verificações realizadas.

        Returns:
            Dicionário com total, aprovados, reprovados
        """
        total = len(self._results)
        passed = sum(1 for r in self._results if r.valid)
        failed = total - passed
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "rate": passed / total if total > 0 else 0.0,
        }


class VerificationResult:
    """Resultado da verificação de especificação.

    Attributes:
        valid : Se a especificação foi validada
        errors : Lista de erros encontrados
        warnings : Lista de avisos
        spec : Dados da especificação
    """

    def __init__(
        self,
        valid: bool,
        errors: List[str],
        warnings: Optional[List[str]] = None,
        spec: Optional[dict] = None,
    ):
        self.valid = valid
        self.errors = errors
        self.warnings = warnings or []
        self.spec = spec


class Criterion:
    """Representa e parsa um critério de especificação.

    Tenta extrair campo, operador e valor de critérios como:
    - "accuracy > 0.85"
    - "sensitivity >= 0.80"
    - "dice > 0.75"
    """

    def __init__(self, text: str):
        self.text = text
        self.field = None
        self.operator = None
        self.value = None
        self._parse_simple()

    def _parse_simple(self):
        """Tenta extrair campo, operador e valor."""
        # Match pattern: field > value ou field >= value etc
        pattern = re.match(
            r"(\w+)\s*(>=|<=|==|!=|>|<)\s*([\d.]+)", self.text
        )
        if pattern:
            self.field = pattern.group(1)
            self.operator = pattern.group(2)
            self.value = float(pattern.group(3))

    def __repr__(self) -> str:
        return f"Criterion({self.field} {self.operator} {self.value})"


def verify_all_specs() -> Dict[str, VerificationResult]:
    """Executa verificação em todas as funções especificadas.

    Para cada função registrada via @spec, tenta importar e verificar.

    Returns:
        Dict {qualified_name: VerificationResult}

    Example:
        >>> results = verify_all_specs()
        >>> for name, result in results.items():
        ...     status = "✓" if result.valid else "✗"
        ...     print(f"{status} {name}")
    """
    from odontoia.sdd.spec import _SPEC_REGISTRY

    verifier = SpecVerifier(strict_mode=False)
    registered_funcs = set()

    # Verifica funções registradas
    for qualified_name, spec_data in _SPEC_REGISTRY.items():
        module_name = spec_data.get("module", "")
        # Tenta importar e encontrar a função
        try:
            parts = qualified_name.split(".")
            func_name = parts[-1]
            module_path = ".".join(parts[:-1])
            import importlib
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            verifier.verify(func)
        except (ImportError, AttributeError) as e:
            verifier._results.append(
                VerificationResult(
                    valid=False,
                    errors=[f"Não foi possível carregar {qualified_name}: {e}"],
                    spec=spec_data,
                )
            )

    return {r.spec.get("function") if r.spec else f"func_{i}": r for i, r in enumerate(verifier._results)}