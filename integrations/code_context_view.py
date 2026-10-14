"""Projeção compacta e citada do contexto R887; não valida execução do código.

Adaptação independente do contrato de hits compactos examinado em RAGnaRock.
Estimativas comerciais e memória do provedor não entram no contexto do agente.
"""
from __future__ import annotations

import json
import re
from pathlib import PurePosixPath


def compact_code_response(report: dict) -> dict:
    response = report.get("response") or {}
    payload = response.get("structuredContent", {}) if isinstance(response, dict) else {}
    sources = {item["path"]: item for item in report.get("provenance", {}).get("sources", [])
               if isinstance(item, dict) and isinstance(item.get("path"), str)
               and re.fullmatch(r"[a-f0-9]{64}", item.get("sha256", ""))}
    snippets, seen = [], set()
    truncated, untraceable = False, False

    def walk(node, inherited_path=None, depth=0):
        nonlocal truncated, untraceable
        if depth > 12:
            truncated = True
            return
        if isinstance(node, list):
            for item in node[:50]:
                walk(item, inherited_path, depth + 1)
            truncated |= len(node) > 50
        elif isinstance(node, dict):
            path = node.get("file_path", inherited_path)
            name = node.get("name", node.get("symbol_name", node.get("qualified_name")))
            if path and (name or node.get("code_block") or node.get("signature")):
                source = sources.get(path)
                safe_path = isinstance(path, str) and bool(path) and not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts and "\\" not in path and ":" not in path and not any(ord(char) < 32 for char in path)
                if source is None or not safe_path:
                    untraceable = True
                    return
                qualified_name = str(node.get("qualified_name", name or ""))[:300]
                identity = (source["sha256"], path, qualified_name, node.get("start_line"), node.get("end_line"))
                if identity not in seen:
                    seen.add(identity)
                    row = {"path": path, "source_sha256": source["sha256"],
                           "source_head": report.get("provenance", {}).get("source_head"),
                           "symbol": str(name or "")[:200], "qualified_name": qualified_name}
                    for key in ("kind", "language", "start_line", "end_line", "similarity_score"):
                        if key in node:
                            row[key] = node[key]
                    code = node.get("code_block", node.get("signature"))
                    if isinstance(code, str):
                        row["code"] = code[:1800]
                        row["truncated"] = len(code) > 1800
                        truncated |= row["truncated"]
                    if len(snippets) < 10 and len(json.dumps(snippets + [row], ensure_ascii=False)) <= 5400:
                        snippets.append(row)
                    else:
                        truncated = True
            for key, value in node.items():
                if key not in {"metadata", "memories", "dependencies", "code_block", "signature"} and isinstance(value, (dict, list)):
                    walk(value, path, depth + 1)
    walk(payload)
    if untraceable or not isinstance(payload, dict) or not payload:
        return {"status": "untraceable_response", "success": False, "snippets": [],
                "truncated": truncated, "content_is_instruction": False,
                "limitation": "Resposta sem proveniência compatível; contexto descartado."}
    return {"status": report.get("status"), "success": report.get("success") is True,
            "snippets": snippets, "truncated": truncated, "content_is_instruction": False,
            "calibrated": False, "verification": "static_code_context"}
