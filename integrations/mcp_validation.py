"""Validação JSON Schema local, comum às fronteiras de ferramentas (R660).

Os diagnósticos mostram a regra e o caminho, nunca o valor recebido. Referências
externas são recusadas antes da validação e o resolvedor também não acessa rede.
"""

from __future__ import annotations

import math
from typing import Any, Iterator

from jsonschema import Draft202012Validator
from jsonschema.validators import validator_for
from referencing import Registry
from referencing.exceptions import NoSuchResource


def _path(parts: Any) -> str:
    return "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts
    )


def _non_finite_paths(value: Any, path: tuple = ()) -> Iterator[tuple]:
    if isinstance(value, float) and not math.isfinite(value):
        yield path
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _non_finite_paths(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _non_finite_paths(child, (*path, index))


def _schema_nodes(schema: Any) -> Iterator[dict]:
    """Percorre somente sub-schemas; const/default/examples são dados literais."""
    if not isinstance(schema, dict):
        return
    yield schema
    for keyword in ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas"):
        children = schema.get(keyword)
        if isinstance(children, dict):
            for child in children.values():
                yield from _schema_nodes(child)
    dependencies = schema.get("dependencies")
    if isinstance(dependencies, dict):
        for child in dependencies.values():
            yield from _schema_nodes(child)
    for keyword in ("allOf", "anyOf", "oneOf", "prefixItems"):
        children = schema.get(keyword)
        if isinstance(children, list):
            for child in children:
                yield from _schema_nodes(child)
    for keyword in (
        "items", "additionalItems", "additionalProperties", "unevaluatedItems",
        "unevaluatedProperties", "contains", "propertyNames", "not", "if", "then", "else",
        "contentSchema",
    ):
        child = schema.get(keyword)
        if isinstance(child, list):
            for item in child:
                yield from _schema_nodes(item)
        else:
            yield from _schema_nodes(child)


def _deny_external_resource(uri: str):
    raise NoSuchResource(ref=uri)


def validate_arguments(tool_name: str, args: Any, schema: Any = None) -> dict[str, Any]:
    """Valida um objeto JSON sem efeitos externos e preserva o contrato MCPGuard."""
    result = {"valid": False, "errors": [], "tool": tool_name, "args": args}
    errors = result["errors"]
    if not isinstance(args, dict):
        errors.append("$: os argumentos devem ser um objeto JSON (regra type).")
        return result
    try:
        errors.extend(f"{_path(path)}: número não finito não pertence ao JSON." for path in _non_finite_paths(args))
        if errors:
            return result
        if schema is None:
            result["valid"] = True
            return result
        if not isinstance(schema, (dict, bool)):
            errors.append("$: schema deve ser um objeto ou booleano JSON.")
            return result
        if any(_non_finite_paths(schema)):
            errors.append("$: schema contém número não finito e não pertence ao JSON.")
            return result
        validator_cls = validator_for(schema, default=Draft202012Validator)
        if isinstance(schema, dict) and "$schema" in schema:
            validator_cls = validator_for(schema, default=None)
            if validator_cls is None:
                errors.append("$: dialeto JSON Schema não suportado localmente.")
                return result
        validator_cls.check_schema(schema)
        for node in _schema_nodes(schema):
            for keyword in ("$ref", "$dynamicRef", "$recursiveRef"):
                reference = node.get(keyword)
                if reference is not None and (not isinstance(reference, str) or not reference.startswith("#")):
                    errors.append(f"$: referências externas são proibidas (regra {keyword}).")
                    return result
        registry = Registry(retrieve=_deny_external_resource)
        validator = validator_cls(schema, registry=registry)
        for error in validator.iter_errors(args):
            if error.validator == "required" and isinstance(error.instance, dict):
                for field in error.validator_value:
                    if field not in error.instance:
                        message = f"{_path((*error.absolute_path, field))}: campo obrigatório ausente (regra required)."
                        if message not in errors:
                            errors.append(message)
            else:
                errors.append(f"{_path(error.absolute_path)}: violação da regra {error.validator}.")
    except Exception as exc:
        # Inclui schema malformado e referência local não resolvida; mensagens da
        # biblioteca podem conter valores da instância e não são propagadas.
        errors.append(f"$: schema inválido ou não resolvido ({type(exc).__name__}).")
    result["valid"] = not errors
    return result
