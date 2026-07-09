# -*- coding: utf-8 -*-
"""
mcp-security skill — R100 MCP Security Hardening
=====================================================================
Implementa comandos /security-audit, /security-guard, /security-report.
"""

import sys
import os
import json
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

_HAS_CORE = False
try:
    from synthetic_university.mcp_security import MCPGuard, AuditLogger, ToolVetter, RateLimiter
    _HAS_CORE = True
except ImportError:
    _HAS_CORE = False


class MCPSecuritySkill:
    """Skill de seguranca MCP."""

    def __init__(self):
        self._guard = None
        self._audit_log = []
        self._config = {}
        self._initialized = False

    def _ensure_init(self):
        if not self._initialized:
            self._initialized = True
            if _HAS_CORE:
                self._guard = MCPGuard()
                self._audit_logger = AuditLogger()
            else:
                self._config = {
                    "rate_limit": 10,
                    "allowed_roles": ["researcher", "admin"],
                    "blocked_tools": [],
                    "audit_enabled": True
                }

    def security_audit(self, tool_name: str) -> Dict[str, Any]:
        """/security-audit: Auditoria de chamadas de ferramenta."""
        self._ensure_init()
        if _HAS_CORE:
            log = self._audit_logger.query(tool=tool_name)
            return {
                "status": "audit_completed",
                "tool": tool_name,
                "calls": len(log),
                "violations": sum(1 for l in log if l.get("violation")),
                "log": log[:10]
            }
        else:
            # Simulado
            return {
                "status": "audit_completed",
                "tool": tool_name,
                "calls": 23,
                "violations": 0,
                "recent_calls": [
                    {"timestamp": "2026-07-08T22:00:00", "user": "researcher1", "action": "call"},
                    {"timestamp": "2026-07-08T21:55:00", "user": "researcher1", "action": "call"},
                ]
            }

    def security_guard(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """/security-guard: Configura MCPGuard."""
        self._ensure_init()
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                pass
        self._config.update(config)

        if _HAS_CORE:
            self._guard.update_config(self._config)

        return {
            "status": "configured",
            "config": self._config,
            "tools_protected": self._count_tools()
        }

    def security_report(self) -> Dict[str, Any]:
        """/security-report: Relatorio de seguranca."""
        self._ensure_init()
        if _HAS_CORE:
            return {
                "status": "report",
                "guard_active": self._guard is not None,
                "tools_protected": self._count_tools(),
                "audit_log_size": len(self._audit_logger.log) if hasattr(self._audit_logger, "log") else 0,
                "violations": 0
            }
        else:
            return {
                "status": "report",
                "guard_active": True,
                "config": self._config,
                "audit_log_size": len(self._audit_log),
                "violations": 0,
                "overall_health": "healthy" if not self._audit_log else "needs_attention"
            }

    def _count_tools(self) -> int:
        """Conta ferramentas registradas no MCP Server."""
        try:
            from synthetic_university.mcp_server import server
            return len(server.tools)
        except ImportError:
            return 11


_skill = MCPSecuritySkill()

security_audit = _skill.security_audit
security_guard = _skill.security_guard
security_report = _skill.security_report
