#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mindspore-validate — Validação de configurações MindSpore"""

import sys
import json
import argparse
from typing import Dict, Any, List, Optional


# Padrões de config conhecidos
KNOWN_PATTERNS = {
    "acl_dump_cfg": {
        "type": "object",
        "required": ["dump"],
        "properties": {
            "dump": {
                "type": "object",
                "required": ["dump_list", "dump_path", "dump_mode", "dump_op_switch"],
                "properties": {
                    "dump_list": {"type": "array", "items": {"type": "object"}},
                    "dump_path": {"type": "string"},
                    "dump_mode": {"enum": ["all", "select", "off"]},
                    "dump_op_switch": {"enum": ["on", "off"], "default": "on"},
                },
            }
        },
        "additionalProperties": False,
    },
    "hccl_single_machine_multi_rank": {
        "type": "object",
        "required": ["board_id", "chip_info", "deploy_mode", "group_count", "group_list"],
        "properties": {
            "board_id": {"type": "string"},
            "chip_info": {"type": "string"},
            "deploy_mode": {"enum": ["lab", "field", "sim"]},
            "group_count": {"type": "string"},
            "group_list": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["device_num", "group_name", "instance_count", "instance_list"],
                    "properties": {
                        "device_num": {"type": "string"},
                        "group_name": {"type": "string"},
                        "instance_count": {"type": "string"},
                        "instance_list": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["devices", "rank_id", "server_id"],
                                "properties": {
                                    "devices": {
                                        "type": "array",
                                        "items": {"type": "object", "required": ["device_id"], "properties": {"device_id": {"type": "string"}}},
                                    },
                                    "rank_id": {"type": "string"},
                                    "server_id": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
        "additionalProperties": True,  # HCCL configs têm campos extras legítimos
    },
    "dataset_schema": {
        "type": "object",
        "required": ["datasetType", "numRows", "columns"],
        "properties": {
            "datasetType": {"type": "string"},
            "numRows": {"type": "integer", "minimum": 1},
            "columns": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["type", "rank", "t_impl"],
                    "properties": {
                        "type": {"type": "string"},
                        "rank": {"type": "integer", "minimum": 1},
                        "t_impl": {"type": "string"},
                    },
                },
            },
        },
        "additionalProperties": False,
    },
}


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Valida dados JSON contra um schema simples, respeitando additionalProperties."""
    errors: List[str] = []

    # Verificar propriedades obrigatórias
    for req in schema.get("required", []):
        if req not in data:
            errors.append(f"Campo obrigatório ausente: '{req}'")

    # Verificar tipo da raiz
    expected_root_type = schema.get("type")
    if expected_root_type and not isinstance(data, eval(expected_root_type)):
        errors.append(f"Tipo raiz esperado: {expected_root_type}, got {type(data).__name__}")

    # Verificar propriedades conhecidas e seus tipos
    known_props = schema.get("properties", {})
    additional_allowed = schema.get("additionalProperties", True)

    for key, value in data.items():
        if key in known_props:
            prop_schema = known_props[key]
            # Validar tipo do campo conhecido
            expected_type = prop_schema.get("type")
            if expected_type and not _check_type(value, expected_type):
                errors.append(f"Campo '{key}': esperado {expected_type}, got {type(value).__name__}")
        elif additional_allowed is not False:
            # Propriedade adicional é permitida
            pass
        else:
            errors.append(f"Propriedade desconhecida: '{key}'")

    # Validar tipos de campos conhecidos (segunda passagem para consistência)
    for prop_name, prop_schema in known_props.items():
        if prop_name in data:
            value = data[prop_name]
            expected_type = prop_schema.get("type")
            if expected_type and not _check_type(value, expected_type):
                # Evitar mensagens duplicadas
                existing = any(err.split(":")[0] == f"Campo '{prop_name}'" for err in errors)
                if not existing:
                    errors.append(f"Campo '{prop_name}': esperado {expected_type}, got {type(value).__name__}")

    return errors


def _check_type(value: Any, expected_type: str) -> bool:
    """Verifica se um valor corresponde ao tipo esperado."""
    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    elif expected_type == "array":
        return isinstance(value, list)
    elif expected_type == "object":
        return isinstance(value, dict)
    elif expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def detect_pattern(filename: str) -> Optional[str]:
    """Detecta o padrão de configuração baseado no nome do arquivo."""
    basename = filename.replace(".json", "").lower()

    if "acl_dump" in basename or "acl" in basename:
        return "acl_dump_cfg"
    elif "hccl" in basename:
        return "hccl_single_machine_multi_rank"
    elif "dataset" in basename and "schema" in basename:
        return "dataset_schema"
    elif basename.endswith("config"):
        return "generic_config"

    return None


def validate_file(filepath: str) -> Dict[str, Any]:
    """Valida um arquivo de configuração MindSpore."""
    result = {
        "filepath": filepath,
        "valid": False,
        "pattern": None,
        "errors": [],
        "warnings": [],
        "info": {},
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        result["errors"].append(f"Erro ao ler JSON: {e}")
        return result
    except FileNotFoundError:
        result["errors"].append(f"Arquivo não encontrado: {filepath}")
        return result
    except Exception as e:
        result["errors"].append(f"Erro inesperado: {e}")
        return result

    # Detectar padrão
    result["pattern"] = detect_pattern(filepath)

    # Validar contra schema conhecido
    pattern = result["pattern"]
    if pattern and pattern in KNOWN_PATTERNS:
        errors = validate_json_schema(data, KNOWN_PATTERNS[pattern])
        result["errors"] = errors
        result["valid"] = len(errors) == 0

        if errors:
            result["warnings"].extend(errors)
    else:
        result["warnings"].append(f"Padrão desconhecido: {result['pattern']}")
        result["valid"] = False

    # Extrair info relevante
    if isinstance(data, dict):
        result["info"] = {
            "campos_total": len(data),
            "campos_conhecidos": len([k for k in data if k in str(KNOWN_PATTERNS)]),
            "has_nested": any(isinstance(v, dict) for v in data.values()),
        }

    return result


def main():
    parser = argparse.ArgumentParser(
        prog="mindspore-validate",
        description="Valida arquivos de configuração MindSpore",
    )
    parser.add_argument("filepath", help="Caminho do arquivo JSON a validar")
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="Listar padrões conhecidos"
    )

    args = parser.parse_args()

    if args.list_patterns:
        print("Padrões conhecidos:")
        for name, schema in KNOWN_PATTERNS.items():
            required = schema.get("required", [])
            props = list(schema.get("properties", {}).keys())
            print(f"  - {name} (obrigatórios: {required})")
        return

    result = validate_file(args.filepath)

    print(f"Arquivo: {result['filepath']}")
    print(f"Padrão detectado: {result['pattern'] or 'desconhecido'}")
    print(f"Válido: {'Sim' if result['valid'] else 'Não'}")

    if result["errors"]:
        print("\nErros:")
        for error in result["errors"]:
            print(f"  ❌ {error}")

    if result["warnings"]:
        print("\nAvisos:")
        for warning in result["warnings"]:
            print(f"  ⚠️  {warning}")

    if result["info"]:
        info = result["info"]
        print(f"\nInformações:")
        print(f"  Total de campos: {info.get('campos_total')}")
        print(f"  Campos conhecidos: {info.get('campos_conhecidos')}")
        print(f"  Tem aninhados: {info.get('has_nested')}")

    # Code de saída
    if result["valid"]:
        print("\n✅ Validação concluída com sucesso")
        sys.exit(0)
    else:
        print("\n❌ Validação falhou")
        sys.exit(1)


if __name__ == "__main__":
    main()
