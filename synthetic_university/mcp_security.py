# -*- coding: utf-8 -*-
"""
MCP Security Hardening — R100
==============================
Camadas de seguranca para o MCP Server:

  - MCPGuard: validacao de argumentos contra JSON Schema
  - AuditLogger: registro estruturado de chamadas
  - ToolVetter: deteccao de tool poisoning
  - RateLimiter: token bucket por caller

Uso:
    from synthetic_university.mcp_security import MCPGuard, AuditLogger, ToolVetter, RateLimiter

    guard = MCPGuard()
    wrapped_handler = guard.wrap("tool_name", handler, schema)

SPEC-935-R100.
"""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Campos sensiveis que devem ser sanitizados nos logs
SENSITIVE_FIELDS = {
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "passwords", "tokens", "access_token", "client_secret",
    "key", "auth", "authorization", "credential", "private",
}

# Marcador interno para que o servidor MCP não serialize uma falha de
# validação como se fosse o resultado bem-sucedido de uma ferramenta.
MCP_ERROR_MARKER = "_mcp_error"


# ============================================================
# C1 — MCPGuard
# ============================================================

class MCPGuard:
    """Valida argumentos de ferramentas MCP contra schemas JSON."""

    @staticmethod
    def validate(
        tool_name: str,
        args: Dict[str, Any],
        schema: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Valida argumentos contra schema JSON.

        Args:
            tool_name: Nome da ferramenta.
            args: Argumentos a validar.
            schema: JSON Schema da ferramenta (None = skip).

        Returns:
            Dict com valid (bool), errors (list), tool, args.
        """
        if not isinstance(args, dict):
            return {
                "valid": False,
                "errors": ["Arguments must be a JSON object"],
                "tool": tool_name,
                "args": args,
            }

        if schema is None:
            return {"valid": True, "errors": [], "tool": tool_name, "args": args}

        errors = []

        # Valida required
        required = schema.get("required", [])
        for field in required:
            if field not in args or args[field] is None:
                errors.append(f"Missing required field: '{field}'")

        # Valida tipos das properties
        properties = schema.get("properties", {})
        for field, value in args.items():
            if field not in properties and field not in required:
                continue  # campos extras sao permitidos
            prop_schema = properties.get(field, {})
            expected_type = prop_schema.get("type")

            if expected_type and value is not None:
                type_ok = False
                if expected_type == "string":
                    type_ok = isinstance(value, str)
                elif expected_type == "integer":
                    type_ok = isinstance(value, int) and not isinstance(value, bool)
                elif expected_type == "number":
                    type_ok = isinstance(value, (int, float)) and not isinstance(value, bool)
                elif expected_type == "boolean":
                    type_ok = isinstance(value, bool)
                elif expected_type == "array":
                    type_ok = isinstance(value, list)
                elif expected_type == "object":
                    type_ok = isinstance(value, dict)

                if not type_ok:
                    errors.append(
                        f"Field '{field}' expected {expected_type}, got {type(value).__name__}"
                    )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "tool": tool_name,
            "args": args,
        }

    def wrap(
        self,
        tool_name: str,
        handler: Callable,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        """Envolve um handler MCP com validacao de argumentos.

        Args:
            tool_name: Nome da ferramenta.
            handler: Funcao handler original.
            schema: JSON Schema para validacao.

        Returns:
            Funcao wrapped que valida antes de chamar o handler.
        """
        def wrapped(args: Dict[str, Any]) -> Dict[str, Any]:
            validation = self.validate(tool_name, args, schema)
            if not validation["valid"]:
                return {
                    MCP_ERROR_MARKER: True,
                    "error": True,
                    "message": f"Validation failed for '{tool_name}': {'; '.join(validation['errors'])}",
                    "validation_errors": validation["errors"],
                }
            return handler(args)

        return wrapped


# ============================================================
# C2 — AuditLogger
# ============================================================

@dataclass
class AuditEntry:
    timestamp: float
    tool: str
    args_sanitized: Dict[str, Any]
    result_summary: str
    duration_seconds: float
    caller: str = "unknown"
    entry_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "datetime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.timestamp)),
            "tool": self.tool,
            "args_sanitized": self.args_sanitized,
            "result_summary": self.result_summary[:200],
            "duration_seconds": round(self.duration_seconds, 4),
            "caller": self.caller,
        }


class AuditLogger:
    """Registro estruturado de chamadas MCP."""

    def __init__(self, max_entries: int = 1000):
        self.entries: List[AuditEntry] = []
        self.max_entries = max_entries

    def log(
        self,
        tool: str,
        args: Dict[str, Any],
        result: Dict[str, Any],
        duration: float,
        caller: str = "unknown",
    ) -> str:
        """Registra uma chamada de ferramenta.

        Args:
            tool: Nome da ferramenta.
            args: Argumentos (serao sanitizados).
            result: Resultado da chamada.
            duration: Duracao em segundos.
            caller: Identificador do caller.

        Returns:
            entry_id.
        """
        entry_id = uuid.uuid4().hex[:12]
        sanitized = self._sanitize(args)
        result_summary = json.dumps(
            self._sanitize(result), ensure_ascii=False, default=str
        )[:200]

        entry = AuditEntry(
            timestamp=time.time(),
            tool=tool,
            args_sanitized=sanitized,
            result_summary=result_summary,
            duration_seconds=duration,
            caller=caller,
            entry_id=entry_id,
        )

        self.entries.append(entry)

        # Mantem limite
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]

        return entry_id

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna entradas mais recentes.

        Args:
            limit: Maximo de entradas.

        Returns:
            Lista de dicts.
        """
        recent = self.entries[-limit:]
        return [e.to_dict() for e in recent]

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do auditor.

        Returns:
            Dict com total_calls, unique_tools, unique_callers, timespan.
        """
        if not self.entries:
            return {
                "total_calls": 0,
                "unique_tools": 0,
                "unique_callers": 0,
                "timespan_seconds": 0,
            }

        tools = {e.tool for e in self.entries}
        callers = {e.caller for e in self.entries}
        timespan = self.entries[-1].timestamp - self.entries[0].timestamp

        return {
            "total_calls": len(self.entries),
            "unique_tools": len(tools),
            "unique_callers": len(callers),
            "timespan_seconds": round(timespan, 2),
        }

    @staticmethod
    def _is_sensitive_field(name: Any) -> bool:
        """Retorna se um nome de campo identifica uma credencial."""
        normalized = str(name).strip().lower().replace("-", "_")
        compact = normalized.replace("_", "")
        sensitive_compact = {field.replace("_", "") for field in SENSITIVE_FIELDS}
        return normalized in SENSITIVE_FIELDS or compact in sensitive_compact

    def _sanitize(self, value: Any) -> Any:
        """Sanitiza recursivamente dicts/listas sem destruir dados públicos."""
        if isinstance(value, dict):
            return {
                key: (
                    "***REDACTED***"
                    if self._is_sensitive_field(key)
                    else self._sanitize(nested_value)
                )
                for key, nested_value in value.items()
            }

        if isinstance(value, list):
            return [self._sanitize(item) for item in value]

        if isinstance(value, str) and len(value) > 200:
            return value[:200] + "..."

        return value


# ============================================================
# C3 — ToolVetter
# ============================================================

class ToolVetter:
    """Detecta padroes suspeitos em argumentos de ferramentas."""

    # Padroes de prompt injection
    PROMPT_INJECTION_PATTERNS = [
        r'\bignore\s+(all\s+)?(previous|prior|above|the)?\s*(instructions|commands|rules|directions|guidelines)\b',
        r'\bforget\s+(all\s+)?(previous|prior)\b',
        r'\bdisregard\s+(all\s+)?(previous|prior)\b',
        r'\byou\s+are\s+(not\s+)?(required\s+to|free\s+to|now)\b',
        r'\bpretend\s+(that\s+)?(you\s+are|to\s+be)\b',
        r'\bdisclose\s+(your\s+)?(system\s+)?(prompt|instructions|rules)\b',
        r'\breveal\s+(your\s+)?(system\s+)?(prompt|instructions|rules)\b',
        r'\boutput\s+(your\s+)?(system\s+)?prompt\b',
        r'\bprint\s+(your\s+)?instructions\b',
        r'\bshow\s+(me\s+)?(your\s+)?(system\s+)?prompt\b',
        r'\bdisclose\s+(system\s+)?prompt\b',
    ]

    # Padroes de command injection
    COMMAND_INJECTION_PATTERNS = [
        r'[;|`]\s*(rm|del|shutdown|reboot|format|mkfs|dd|:wq!|:q!)',
        r'\b(rm\s+-rf|rmdir\s+/|del\s+/[fqs])\b',
        r'(?<!\w)(\|\s*(bash|sh|cmd|powershell|python)\b)',
        r'\b(exec|eval|system|popen|subprocess)\s*\(',
        r'\b(__import__|__builtins__|__globals__)\b',
        r'\b(os\.system|os\.popen|subprocess\.call|subprocess\.Popen)\b',
    ]

    # Padroes de path traversal
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',
        r'\.\.\\',
        r'\.\.%2f',
        r'\.\.%5c',
        r'/etc/passwd',
        r'/etc/shadow',
        r'/etc/hosts',
        r'/windows/system32',
        r'\\windows\\system32',
        r'\.env',
        r'\\$',
    ]

    def check(self, text: Any) -> Dict[str, Any]:
        """Verifica se um texto contem padroes suspeitos.

        Args:
            text: Texto a verificar.

        Returns:
            Dict com suspicious (bool), flags (list), score (int).
        """
        if not isinstance(text, str) or not text.strip():
            return {"suspicious": False, "flags": [], "score": 0}

        flags = []
        text_lower = text.lower()

        # Prompt injection
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                flags.append("prompt_injection")
                break

        # Command injection
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                flags.append("command_injection")
                break

        # Path traversal
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, text_lower):
                flags.append("path_traversal")
                break

        # SQL injection basico
        if re.search(r"('|--|/\*|DROP\s+TABLE|UNION\s+SELECT)", text, re.IGNORECASE):
            flags.append("sql_injection")

        score = len(flags) * 25  # 25 pontos por flag

        return {
            "suspicious": len(flags) > 0,
            "flags": flags,
            "score": min(100, score),
            "length": len(text),
        }

    def scan_args(self, args: Any) -> Dict[str, Any]:
        """Escaneia recursivamente strings em dicts e listas de argumentos.

        Args:
            args: Dict ou lista de argumentos.

        Returns:
            Dict com suspicious (bool), flagged_fields (list),
            total_score (int), details (dict) e flags (list) agregadas.
        """
        empty_result = {
            "suspicious": False,
            "flagged_fields": [],
            "total_score": 0,
            "details": {},
            "flags": [],
        }
        if not isinstance(args, (dict, list)):
            return empty_result

        flagged_fields = []
        flags = []
        total_score = 0
        details = {}

        def scan_value(value: Any, path: str) -> None:
            nonlocal total_score

            if isinstance(value, str):
                result = self.check(value)
                if not result["suspicious"]:
                    return

                flagged_fields.append(path)
                total_score += result["score"]
                details[path] = {
                    "flags": list(result["flags"]),
                    "score": result["score"],
                    "preview": value[:80],
                }
                for flag in result["flags"]:
                    if flag not in flags:
                        flags.append(flag)
                return

            if isinstance(value, dict):
                for key, nested_value in value.items():
                    nested_path = f"{path}.{key}" if path else str(key)
                    scan_value(nested_value, nested_path)
                return

            if isinstance(value, list):
                for index, nested_value in enumerate(value):
                    nested_path = f"{path}[{index}]" if path else f"[{index}]"
                    scan_value(nested_value, nested_path)

        scan_value(args, "")

        return {
            "suspicious": len(flagged_fields) > 0,
            "flagged_fields": flagged_fields,
            "total_score": min(100, total_score),
            "details": details,
            "flags": flags,
        }


# ============================================================
# C4 — RateLimiter
# ============================================================

class RateLimiter:
    """Token bucket simples para rate limiting por caller.

    Attributes:
        max_calls: Maximo de chamadas permitidas na janela.
        window_seconds: Duracao da janela em segundos.
    """

    def __init__(self, max_calls: int = 10, window_seconds: float = 60.0):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._buckets: Dict[str, List[float]] = {}

    def allow(self, caller_id: str) -> bool:
        """Verifica se uma chamada e permitida.

        Args:
            caller_id: Identificador do caller.

        Returns:
            True se permitido, False se rate limit excedido.
        """
        now = time.time()
        if caller_id not in self._buckets:
            self._buckets[caller_id] = []

        # Remove timestamps expirados
        self._buckets[caller_id] = [
            t for t in self._buckets[caller_id]
            if now - t < self.window_seconds
        ]

        if len(self._buckets[caller_id]) >= self.max_calls:
            return False

        self._buckets[caller_id].append(now)
        return True

    def reset(self, caller_id: str) -> None:
        """Reseta o contador de um caller.

        Args:
            caller_id: Identificador do caller.
        """
        self._buckets[caller_id] = []

    def get_remaining(self, caller_id: str) -> int:
        """Retorna quantas chamadas ainda pode fazer.

        Args:
            caller_id: Identificador do caller.

        Returns:
            Numero de chamadas restantes na janela.
        """
        now = time.time()
        if caller_id not in self._buckets:
            return self.max_calls

        active = [t for t in self._buckets[caller_id] if now - t < self.window_seconds]
        return max(0, self.max_calls - len(active))
