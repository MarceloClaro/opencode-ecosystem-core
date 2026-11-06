"""R1060 — desktop-operator do Core.

Wrapper local sobre o agent-desktop (Apache-2.0) com allowlist, aprovação
humana e redação. Não instala o binário e não expõe o MCP completo.
"""

__all__ = ["approvals", "policy", "runtime"]
__version__ = "1.0.0"
