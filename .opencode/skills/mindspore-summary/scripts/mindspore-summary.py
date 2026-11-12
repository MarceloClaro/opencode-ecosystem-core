#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mindspore-summary — Gera resumos de configurações MindSpore"""

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
                "additionalProperties": False,
            }
        },
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
        "additionalProperties": True,
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
    """Valida dados JSON contra um schema simples."""
    errors: List[str] = []
    for req in schema.get("required", []):
        if req not in data:
            errors.append(f"Campo obrigatório ausente: '{req}'")
    known_props = schema.get("properties", {})
    additional_allowed = schema.get("additionalProperties", True)
    for key, value in data.items():
        if key in known_props:
            prop_schema = known_props[key]
            expected_type = prop_schema.get("type")
            if expected_type and not _check_type(value, expected_type):
                errors.append(f"Campo '{key}': esperado {expected_type}, got {type(value).__name__}")
        elif additional_allowed is not False:
            pass
        else:
            errors.append(f"Propriedade desconhecida: '{key}'")
    for prop_name, prop_schema in known_props.items():
        if prop_name in data:
            value = data[prop_name]
            expected_type = prop_schema.get("type")
            if expected_type and not _check_type(value, expected_type):
                existing = any(err.startswith(f"Campo '{prop_name}") for err in errors)
                if not existing:
                    errors.append(f"Campo '{prop_name}': esperado {expected_type}, got {type(value).__name__}")
    return errors


def _check_type(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    elif expected_type == "array":
        return isinstance(value, list)
    elif expected_type == "object":
        return isinstance(value, dict)
    return True


def detect_pattern(filename: str) -> Optional[str]:
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
    result["pattern"] = detect_pattern(filepath)
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
    if isinstance(data, dict):
        result["info"] = {
            "campos_total": len(data),
            "campos_conhecidos": len([k for k in data if k in str(KNOWN_PATTERNS)]),
            "has_nested": any(isinstance(v, dict) for v in data.values()),
        }
    return result


def generate_summary(filepaths: List[str]) -> Dict[str, Any]:
    summary = {
        "total_files": len(filepaths),
        "patterns": {},
        "common_fields": {},
        "errors": [],
        "valid_count": 0,
        "invalid_count": 0,
    }
    for filepath in filepaths:
        result = validate_file(filepath)
        pattern = result["pattern"] or "desconhecido"
        summary["patterns"][pattern] = summary["patterns"].get(pattern, 0) + 1
        if result["valid"]:
            summary["valid_count"] += 1
        else:
            summary["invalid_count"] += 1
            summary["errors"].extend(result["errors"])
        if isinstance(result.get("info"), dict):
            for key, value in result["info"].items():
                if key not in summary["common_fields"]:
                    summary["common_fields"][key] = {"count": 0, "values": set()}
                summary["common_fields"][key]["count"] += 1
                if isinstance(value, (str, int, float, bool)):
                    summary["common_fields"][key]["values"].add(str(value))
                elif isinstance(value, list):
                    summary["common_fields"][key]["values"].add(f"list({len(value)})")
    for key in summary["common_fields"]:
        summary["common_fields"][key]["values"] = list(summary["common_fields"][key]["values"])
    return summary


def format_summary(summary: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 56)
    lines.append(" mindspore-config — Resumo de Análise ")
    lines.append("=" * 56)
    lines.append("")
    lines.append(f"Arquivos total: {summary['total_files']}")
    lines.append(f"  Válidos: {summary['valid_count']}")
    lines.append(f"  Inválidos: {summary['invalid_count']}")
    lines.append("")
    if summary["patterns"]:
        lines.append("Distribuição de padrões:")
        for pattern, count in sorted(summary["patterns"].items(), key=lambda item: -item[1]):
            lines.append(f"  - {pattern}: {count}")
        lines.append("")
    if summary["common_fields"]:
        lines.append("Campos mais comuns:")
        # Ordena por count descending
        sorted_fields = sorted(summary["common_fields"].items(), key=lambda item: -item[1]["count"])
        for key, info in sorted_fields:
            lines.append(f"  - {key}: aparece em {info['count']} arquivo(s)")
            if info.get("values"):
                lines.append(f"    valores amostra: {', '.join(info['values'][:3])}")
        lines.append("")
    if summary["errors"]:
        lines.append("Erros encontrados:")
        for error in summary["errors"][:10]:
            lines.append(f"  ❌ {error}")
        if len(summary["errors"]) > 10:
            lines.append(f"  ... e mais {len(summary['errors']) - 10} erros")
        lines.append("")
    lines.append("=" * 56)
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="mindspore-summary",
        description="Gera resumos de configurações MindSpore",
    )
    parser.add_argument("filepaths", nargs="+", help="Caminhos dos arquivos JSON a analisar")
    args = parser.parse_args()
    summary = generate_summary(args.filepaths)
    output = format_summary(summary)
    print(output)
    if summary["invalid_count"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()