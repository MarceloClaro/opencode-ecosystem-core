# -*- coding: utf-8 -*-
"""Workbench de supervisão DeepSeekGUI (M4 — SPEC-935-R479/R471).

Conector opt-in que documenta e valida o fluxo de "apontar" o workbench
DeepSeekGUI para um workspace do Core (pesquisa, academic, publications)
usando o harness já presente em ``integrations.deepseek_harness``.

Licença (CA5): camada de produto DeepSeekGUI é PolyForm Perimeter 1.0.1
(uso interno de pesquisa/estudo permitido; redistribuição competitiva vedada);
o upstream DeepSeek Harness é MIT. Nenhuma GUI é executada por este módulo;
a configuração é um recibo auditável e determinístico, sem credenciais.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

HARNESS_MODULE = "integrations.deepseek_harness"

DEFAULT_CORE_WORKSPACES: tuple = ("pesquisa", "academic", "publications")

_LICENSE_PRODUCT = "PolyForm Perimeter 1.0.1"
_LICENSE_UPSTREAM = "MIT"
_LIMITATION = (
    "Uso interno de pesquisa e estudo permitido; redistribuição competitiva "
    "vedada sem licença (PolyForm Perimeter 1.0.1)."
)


class DeepSeekGUIWorkbench:
    """Conector de supervisão desktop (opt-in via ambiente)."""

    def __init__(self, repo_root: str, enabled_by_env: bool = False) -> None:
        self.repo_root = Path(repo_root).resolve()
        self._enabled_flag = enabled_by_env or os.environ.get("DEEPSEEK_GUI_ENABLED") == "1"
        self.workspace = os.environ.get("DEEPSEEK_GUI_WORKSPACE", "")

    def active(self) -> bool:
        return self._enabled_flag and self.validate_workspace(self.workspace)

    def validate_workspace(self, name: str) -> bool:
        """Workspace deve ser um dos diretórios canônicos do Core."""
        if not name:
            return False
        if name not in DEFAULT_CORE_WORKSPACES:
            return False
        try:
            candidate = (self.repo_root / name).resolve()
        except OSError:
            return False
        return candidate.is_relative_to(self.repo_root) and candidate.is_dir()

    def launch_config(self) -> Dict[str, Any]:
        """Recibo de configuração do workbench (sem executar GUI)."""
        if not self.validate_workspace(self.workspace):
            raise ValueError(f"Workspace inválido: {self.workspace!r} (fora da allowlist do Core).")
        return {
            "workspace": self.workspace,
            "harness_module": HARNESS_MODULE,
            "command": f"python3 -m {HARNESS_MODULE}.bridge",
            "license_product": _LICENSE_PRODUCT,
            "license_upstream": _LICENSE_UPSTREAM,
            "limitation": _LIMITATION,
        }

    def harness_importable(self) -> bool:
        try:
            __import__(HARNESS_MODULE, fromlist=["bridge"])
            return True
        except Exception:
            return False


default_workbench = DeepSeekGUIWorkbench(repo_root=str(Path(__file__).resolve().parent.parent))