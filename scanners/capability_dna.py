"""R664: normalização de capacidades declaradas e referências informadas.

Nenhuma referência é executada ou autenticada neste módulo. Os níveis indicam
o suporte dos registros fornecidos, e não uma auditoria do sistema em operação.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
import re
from typing import Any


STATES = ("declared", "available", "executed", "externally_validated")
CATEGORIES = ("conceitos", "metodos", "bases", "ferramentas", "dominios",
              "validacoes", "recursos")
MAX_CAPABILITIES = 256
MAX_MODULES = 128
MAX_ITEMS = 64
_SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")


def bounded_int(value: Any, name: str, maximum: int) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError(f"{name} deve ser inteiro entre 1 e {maximum}.")
    return value


def text(value: Any, name: str, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{name} deve ser texto não vazio de até {maximum} caracteres.")
    try:
        value.encode("utf-8")
    except UnicodeError as exc:
        raise ValueError(f"{name} deve conter texto Unicode válido.") from exc
    return value.strip()


def texts(value: Any, name: str, maximum: int = MAX_ITEMS) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f"{name} deve ser uma lista com até {maximum} itens.")
    return list(dict.fromkeys(text(item, name) for item in value))


def _provenance_json(value: Any, name: str) -> Any:
    """Preserva metadados JSON pequenos, sem importar ou abrir artefatos."""
    count = 0

    def visit(item: Any, depth: int):
        nonlocal count
        count += 1
        if depth > 6 or count > 512:
            raise ValueError(f"{name} excede limites de profundidade ou quantidade de metadados.")
        kind = type(item)
        if item is None or kind is bool:
            return
        if kind is int:
            if item.bit_length() > 4096:
                raise ValueError(f"{name} contém inteiro excessivamente grande.")
            return
        if kind is float:
            if not math.isfinite(item):
                raise ValueError(f"{name} contém número não finito.")
            return
        if kind is str:
            if len(item) > 2000:
                raise ValueError(f"{name} contém texto acima de 2000 caracteres.")
            try:
                item.encode("utf-8")
            except UnicodeError as exc:
                raise ValueError(f"{name} contém texto Unicode inválido.") from exc
            return
        if kind is list:
            if len(item) > 32:
                raise ValueError(f"{name} contém lista com mais de 32 itens.")
            for child in item:
                visit(child, depth + 1)
            return
        if kind is dict:
            if len(item) > 32:
                raise ValueError(f"{name} contém objeto com mais de 32 campos.")
            for key, child in item.items():
                if type(key) is not str or len(key) > 500:
                    raise ValueError(f"{name} contém chave JSON inválida.")
                visit(key, depth + 1)
                visit(child, depth + 1)
            return
        raise ValueError(f"{name} deve conter somente valores JSON.")

    visit(value, 0)
    serialized = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    if len(serialized.encode("utf-8")) > 8192:
        raise ValueError(f"{name} excede o limite de 8 KiB de metadados JSON.")
    return deepcopy(value)


def evidence_records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_ITEMS:
        raise ValueError("evidence deve ser lista com até 64 referências.")
    result = []
    for item in value:
        if isinstance(item, str):
            result.append({"kind": "note", "ref": text(item, "ref", 2000),
                           "success": False})
            continue
        if not isinstance(item, dict):
            raise ValueError("Cada evidência deve ser uma referência ou objeto.")
        record = {"kind": text(item.get("kind", "note"), "kind"),
                  "ref": text(item.get("ref"), "ref", 2000),
                  "success": item.get("success") is True}
        if item.get("validator") is not None:
            record["validator"] = text(item["validator"], "validator")
        if "sha256" in item:
            digest = item["sha256"]
            if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
                raise ValueError("evidence.sha256 deve conter 64 caracteres hexadecimais.")
            record["sha256"] = digest
        if "scope" in item:
            text(item["scope"], "evidence.scope")
            record["scope"] = item["scope"]
        for name in ("runtime", "artifact"):
            if name in item:
                record[name] = _provenance_json(item[name], f"evidence.{name}")
        result.append(record)
    return result


def supported_state(requested: str, evidence: list[dict[str, Any]]) -> str:
    if requested not in STATES:
        raise ValueError(f"state deve pertencer a {STATES}.")
    level = 0
    for record in evidence:
        if record["success"] is not True:
            continue
        if record["kind"] == "availability":
            level = max(level, 1)
        elif record["kind"] == "execution":
            level = max(level, 2)
        elif record["kind"] == "external_validation" and record.get("validator"):
            level = max(level, 3)
    return STATES[min(STATES.index(requested), level)]


def normalize_modules(modules: Any) -> tuple[dict[str, list[str]], dict[str, dict[str, Any]]]:
    if not isinstance(modules, dict) or len(modules) > MAX_MODULES:
        raise ValueError("modules deve mapear até 128 módulos para listas de capacidades.")
    if any(not isinstance(name, str) for name in modules):
        raise ValueError("Nomes de módulos devem ser strings explícitas.")
    normalized: dict[str, list[str]] = {}
    capabilities: dict[str, dict[str, Any]] = {}
    for name in sorted(modules):
        module = text(name, "module")
        entries = modules[name]
        if not isinstance(entries, list) or len(entries) > MAX_CAPABILITIES:
            raise ValueError("Cada módulo deve declarar uma lista de até 256 capacidades.")
        normalized[module] = []
        for entry in entries:
            if isinstance(entry, str):
                entry = {"id": entry}
            if not isinstance(entry, dict):
                raise ValueError("Capacidades devem ser IDs ou descritores explícitos.")
            capability = text(entry.get("id"), "capability.id")
            evidence = evidence_records(entry.get("evidence", []))
            requested = entry.get("state", "declared")
            state = supported_state(requested, evidence)
            composition = entry.get("composition", {})
            if not isinstance(composition, dict):
                raise ValueError("composition deve ser um mapa de classes de insumos.")
            provider = {"module": module, "state": state, "declared_state": requested,
                        "evidence": evidence, "origin": f"module:{module}:{capability}",
                        "requires": texts(entry.get("requires", []), "requires"),
                        "inputs": texts(entry.get("inputs", []), "inputs"),
                        "outputs": texts(entry.get("outputs", []), "outputs"),
                        "tags": texts(entry.get("tags", []), "tags"),
                        "composition": {category: texts(composition.get(category, []), category)
                                        for category in CATEGORIES},
                        "validation_criteria": texts(entry.get("validation_criteria", []),
                                                     "validation_criteria")}
            if capability not in normalized[module]:
                normalized[module].append(capability)
            if capability not in capabilities:
                if len(capabilities) >= MAX_CAPABILITIES:
                    raise ValueError("DNA excede o limite de 256 capacidades distintas.")
                capabilities[capability] = {
                    "id": capability, "state": "declared", "providers": [],
                    "evidence": [], "requires": [], "inputs": [], "outputs": [], "tags": [],
                    "composition": {category: [] for category in CATEGORIES},
                    "validation_criteria": [], "origins": [],
                }
            record = capabilities[capability]
            record["providers"].append(provider)
            record["origins"] = sorted(set(record["origins"]) | {provider["origin"]})
            if STATES.index(state) > STATES.index(record["state"]):
                record["state"] = state
            record["evidence"].extend({**proof, "module": module, "capability": capability}
                                      for proof in evidence)
            for field in ("requires", "inputs", "outputs", "tags", "validation_criteria"):
                record[field] = sorted(set(record[field]) | set(provider[field]))
            for category in CATEGORIES:
                record["composition"][category] = sorted(
                    set(record["composition"][category]) | set(provider["composition"][category]))
    return normalized, dict(sorted(capabilities.items()))


def capability_map(dna: Any) -> dict[str, dict[str, Any]]:
    """Aceita o snapshot do scanner, seu objeto DNA ou um catálogo de módulos."""
    if dna is None:
        return {}
    if hasattr(dna, "to_dict"):
        dna = dna.to_dict()
    if not isinstance(dna, dict):
        raise ValueError("dna deve ser objeto DNA ou dicionário de capacidades.")
    if "capability_map" in dna:
        records = dna["capability_map"]
        if not isinstance(records, dict) or len(records) > MAX_CAPABILITIES:
            raise ValueError("capability_map inválido ou excede 256 capacidades.")
        # Reaplica o gate: um snapshot manual não pode promover uma declaração
        # apenas alterando a string state. Não há importação ou leitura de refs.
        modules = {}
        for capability, record in records.items():
            if not isinstance(record, dict):
                raise ValueError("Cada capability_map deve conter um descritor.")
            providers = record.get("providers", [])
            if not isinstance(providers, list) or len(providers) > MAX_MODULES:
                raise ValueError("providers deve listar até 128 módulos.")
            if not providers:
                modules.setdefault("provided_dna", []).append({**record, "id": capability})
            for provider in providers:
                if not isinstance(provider, dict):
                    raise ValueError("Cada provider deve conter um descritor.")
                module = text(provider.get("module"), "provider.module")
                modules.setdefault(module, []).append({**provider, "id": capability,
                                                       "state": provider.get("declared_state", provider.get("state", "declared"))})
        return normalize_modules(modules)[1]
    if "capabilities" in dna:
        return normalize_modules({"legacy_dna": dna["capabilities"]})[1]
    return normalize_modules(dna)[1]


def reference_copy(value: Any) -> Any:
    return deepcopy(value)
