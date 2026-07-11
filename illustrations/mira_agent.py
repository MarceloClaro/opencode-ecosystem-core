"""
MIRA Presentation Agent — o agente-executor de runtime do método MIRA.
======================================================================

Enquanto `illustrations/mira_deck.py::MiraDeckPipeline` é o *motor* (a
linha de montagem de 6 estágios) e `orchestrator.present()` é a via
*direta* (chamada de biblioteca), este agente é a via *delegada*: um
executor de runtime que **encarna** o pipeline e é registrável no
Blackboard com uma capacidade própria, tornando "gerar uma apresentação"
uma tarefa de primeira classe do runtime multiagente (sujeita a matching
por atenção, Trust Engine e Token Economy).

Ver SPEC-935-R126.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .mira_deck import MiraDeckPipeline

MIRA_AGENT_ID = "mira-presenter"
# `apresentacao-mira` é a capacidade DISTINTIVA — exclusiva deste agente,
# garante elegibilidade determinística no matching do Blackboard.
MIRA_CAPABILITIES = ["apresentacao", "apresentacao-mira", "mira-deck",
                     "slides-animados"]


class MiraPresentationAgent:
    """Agente-executor que realiza o método MIRA a partir de uma produção."""

    agent_id = MIRA_AGENT_ID
    name = "MIRA Presentation Agent"
    description = (
        "Executor de runtime do método MIRA: transforma o manuscrito de "
        "uma produção (manuscrito.md) num deck HTML de cards de vidro "
        "animados (extract → plan → copywrite → build → animate → validate), "
        "com relatório de conformidade."
    )
    capabilities = MIRA_CAPABILITIES

    def __init__(self, pipeline: Optional[MiraDeckPipeline] = None):
        self.pipeline = pipeline or MiraDeckPipeline()

    # ------------------------------------------------------------------
    def register_payload(self) -> Dict[str, Any]:
        """Payload pronto para `metabus.publish('agent.register', ...)`."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": list(self.capabilities),
            "schema": {
                "production_folder": "str — pasta da produção contendo manuscrito.md",
            },
        }

    # ------------------------------------------------------------------
    def execute(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa a tarefa de apresentação a partir do contexto do Blackboard.

        Espera `production_folder` (ou `folder`) no contexto. Retorna um
        resultado padronizado; contexto inválido ou manuscrito ausente
        devolvem `{"ok": False, "error": ...}` sem lançar exceção.
        """
        ctx = context or {}
        folder = ctx.get("production_folder") or ctx.get("folder")
        if not folder:
            return {"ok": False, "error": "contexto sem 'production_folder'"}

        prod = Path(folder)
        manuscrito = prod / "manuscrito.md"
        if not manuscrito.exists():
            return {"ok": False,
                    "error": f"manuscrito.md não encontrado em {folder}"}

        markdown = manuscrito.read_text(encoding="utf-8", errors="ignore")
        out = prod / "apresentacao"
        report = self.pipeline.run(markdown, str(out))
        return {
            "ok": True,
            "passed": report.passed,
            "deck": str(out / "deck.html"),
            "conformidade": str(out / "CONFORMIDADE.md"),
            "violations": report.violations,
        }
