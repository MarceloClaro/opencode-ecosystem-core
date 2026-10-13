"""Recibos REA para contexto finito; Evidence integral permanece em arquivo."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


def _bounded(value: Any, depth: int = 0) -> Any:
    if isinstance(value, str):
        return value if len(value) <= 600 else value[:600] + " [resumo; consulte Evidence]"
    if isinstance(value, dict):
        if depth >= 3:
            return {"fields": len(value)}
        return {str(key): _bounded(child, depth + 1) for key, child in list(value.items())[:20]}
    if isinstance(value, list):
        if len(value) > 12:
            return {"count": len(value), "sample": [_bounded(child, depth + 1) for child in value[:3]]}
        return [_bounded(child, depth + 1) for child in value]
    return value


def _list_count(value: Any) -> int | None:
    return len(value) if isinstance(value, list) else None


def compact_rea_report(report: dict[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    """Guarda bytes completos por hash e devolve resumo explicitamente delimitado."""
    result = {key: value for key, value in report.items() if key not in {"response", "stderr"}}
    if report.get("stderr"):
        result["stderr_excerpt"] = str(report["stderr"])[:2000]
    if report.get("operation") == "layers":
        rows = report.get("layers")
        if isinstance(rows, list):
            result["layers"] = [
                {"id": row.get("id"), "title": row.get("title"), "kind": row.get("kind"),
                 "engine": row.get("engine"), "ready": row.get("ready"),
                 "requirement": row.get("requirement"), "inspection_tool": row.get("inspection_tool"),
                 "reason": row.get("reason"),
                 "env": [{"name": state.get("name"), "ok": state.get("ok"),
                          "source": state.get("source"), "resolved": state.get("resolved"),
                          "reason": state.get("reason")}
                         for state in row.get("env", []) if isinstance(state, dict)]}
                for row in rows if isinstance(row, dict)
            ]
        result["response_delivery"] = "readiness_summary_without_transport"
        return result
    response = report.get("response")
    if response is None:
        return result
    payload = json.dumps(response, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    digest = hashlib.sha256(payload).hexdigest()
    base = Path(root or Path(__file__).resolve().parents[1]).resolve()
    directory = base / ".opencode" / "rea" / "evidence"
    temporary = None
    try:
        expected = report.get("provenance", {}).get("response_sha256")
        if expected is not None and expected != digest:
            raise ValueError("Hash da resposta REA diverge da proveniência")
        if not directory.resolve().is_relative_to(base):
            raise ValueError("Diretório de Evidence REA fora do workspace")
        directory.mkdir(parents=True, exist_ok=True)
        artifact = directory / (digest + ".json")
        if artifact.is_symlink():
            raise ValueError("Destino de Evidence REA contém link simbólico")
        with tempfile.NamedTemporaryFile(dir=directory, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, artifact)
        temporary = None
        result["evidence_artifact"] = {
            "path": str(artifact), "sha256": digest, "bytes": len(payload), "complete": True,
        }
    except (OSError, ValueError) as exc:
        result.update(status="failed", success=False, error_code="evidence_export_failed",
                      error=str(exc), evidence_preserved=False)
        return result
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    result["response_delivery"] = "summary_with_complete_local_artifact"
    if report.get("operation") == "catalog":
        result["tools"] = [tool["name"] for tool in response.get("tools", [])]
        result["schema_delivery"] = "complete_schemas_in_evidence_artifact"
        return result
    native = report.get("operation") == "analyze_binary"
    analysis = response.get("analysis", {}) if native else response
    evidence = analysis.get("structuredContent")
    if evidence is None:
        for block in analysis.get("content", []):
            if block.get("type") == "text":
                try:
                    evidence = json.loads(block["text"])
                    break
                except (ValueError, TypeError):
                    continue
    if isinstance(evidence, dict) and "evidence_id" in evidence:
        normalized = evidence.get("normalized_result", {})
        if not isinstance(normalized, dict):
            result.update(status="failed", success=False, error_code="invalid_evidence",
                          error="REA entregou normalized_result inválido; resposta completa preservada.",
                          session_or_error_summary=_bounded(evidence))
            return result
        graph = normalized.get("graph", {})
        semantic = normalized.get("semantic_graph", {})
        graph = graph if isinstance(graph, dict) else {}
        semantic = semantic if isinstance(semantic, dict) else {}
        result["evidence"] = _bounded({
            "evidence_id": evidence.get("evidence_id"), "operation": evidence.get("operation"),
            "confidence": evidence.get("confidence"), "authority": evidence.get("authority"),
            "provider": evidence.get("provider"), "subject": evidence.get("subject"),
            "procedure": normalized.get("procedure") if native else None,
            "limitations": evidence.get("limitations", []),
            "input_path": normalized.get("input_path"),
            "root_artifact_sha256": normalized.get("root_artifact_sha256"),
            "statistics": normalized.get("statistics", {}),
            "artifact_graph": {"nodes": _list_count(graph.get("nodes")),
                               "edges": _list_count(graph.get("edges")), "coverage": graph.get("coverage")},
            "semantic_graph": {"nodes": _list_count(semantic.get("nodes")),
                               "relations": _list_count(semantic.get("relations")),
                               "unknowns": _list_count(semantic.get("unknowns")), "coverage": semantic.get("coverage")},
        })
    elif (
        report.get("operation") == "session" and report.get("success") is True
        and not response.get("isError") and isinstance(evidence, dict)
        and isinstance(evidence.get("result"), dict)
        and isinstance(evidence["result"].get("server_identity"), dict)
        and evidence["result"]["server_identity"]
    ):
        session = evidence.get("result", evidence)
        session = session if isinstance(session, dict) else {}
        identity = session.get("server_identity", {})
        identity = identity if isinstance(identity, dict) else {}
        catalog = identity.get("catalog", {})
        catalog = catalog if isinstance(catalog, dict) else {}
        providers = session.get("analysis_provider_candidates", [])
        providers = providers if isinstance(providers, list) else []
        availability = session.get("tool_availability", [])
        availability = availability if isinstance(availability, list) else []
        result["session"] = {
            "server_identity": {key: _bounded(value) for key, value in identity.items() if key != "catalog"},
            "catalog": {key: _bounded(catalog.get(key)) for key in ("counts", "digests")},
            "providers": [{key: _bounded(row.get(key)) for key in ("provider", "availability", "target_support")}
                          for row in providers[:12] if isinstance(row, dict)],
            "tool_availability": [{key: _bounded(row.get(key)) for key in ("name", "available", "reason", "remediation")}
                                  for row in availability if isinstance(row, dict) and
                                  row.get("name") in {"binary_session", "analyze_javascript_application"}],
            "open": session.get("open"),
        }
    else:
        result["session_or_error_summary"] = _bounded(evidence)
    return result
