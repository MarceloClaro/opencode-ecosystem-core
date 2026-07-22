"""ContextWindowManager — Gerencia a janela de contexto mínima para cada nanobloco.

Para que modelos LiteRT-LM (20K tokens) escrevam blocos coesos,
cada bloco recebe:
  - O próprio nanobloco (target) ~300 tokens
  - Vizinhos imediatos (anterior e próximo) ~600 tokens
  - Citações/guidelines globais ~200 tokens
  - Mini-SDD com critérios ~200 tokens
Total: ~1300 tokens — folga ampla dentro de 20K.
"""

from __future__ import annotations

from typing import Optional

from . import (
    LINE_RANGE, TOKEN_LIMIT_PER_BLOCK, NanoBlock, NanoPlan,
)


class ContextWindowManager:
    """Gerencia a montagem de contexto para cada nanobloco.

    Estratégia:
    1. Contexto mínimo: 300 tokens (o bloco em si)
    2. Contexto expandido: bloco + vizinhos imediatos
    3. Contexto completo: bloco + vizinhos + guidelines globais + mini-SDD
    """

    MAX_CONTEXT_TOKENS = 1500  # limite seguro para o prompt completo

    def build_context(self, block: NanoBlock, plan: NanoPlan,
                      mode: str = "write") -> dict:
        """Monta o contexto para um nanobloco.

        Args:
            block: O nanobloco alvo.
            plan: Plano completo.
            mode: "write", "verify", ou "coherence".

        Returns:
            Dict com o contexto estruturado.
        """
        idx = block.index

        # Vizinhos
        prev_block = plan.blocks[idx - 1] if idx > 0 else None
        next_block = plan.blocks[idx + 1] if idx < len(plan.blocks) - 1 else None

        context = {
            "target": {
                "index": block.index,
                "title": block.title,
                "section": block.section,
                "block_type": block.block_type.value,
            },
            "neighbors": {},
            "guidelines": {},
            "criteria": [c.description for c in block.criteria],
        }

        # Contexto de vizinhança
        if prev_block:
            context["neighbors"]["previous"] = {
                "index": prev_block.index,
                "title": prev_block.title,
                "content_snippet": prev_block.content[:300] if prev_block.content else "",
                "block_type": prev_block.block_type.value,
            }
        if next_block:
            context["neighbors"]["next"] = {
                "index": next_block.index,
                "title": next_block.title,
                "block_type": next_block.block_type.value,
            }

        # Guidelines globais (extraídas do plano)
        context["guidelines"] = {
            "total_blocks": plan.total_blocks,
            "total_pages": plan.total_pages,
            "section": block.section,
            "section_index": plan.sections.index(block.section) if block.section in plan.sections else -1,
            "total_sections": len(plan.sections),
            "lines_range": list(LINE_RANGE),
        }

        # Modo verify: inclui conteúdo a ser verificado
        if mode == "verify" and block.content:
            context["content_to_verify"] = block.content[:1500]

        # Modo coherence: inclui blocos de referência expandidos
        if mode == "coherence":
            context["coherence_scope"] = self._build_coherence_context(block, plan)

        return context

    def _build_coherence_context(self, block: NanoBlock, plan: NanoPlan) -> dict:
        """Constrói contexto de coerência expandido.

        Inclui até 5 blocos antes e 5 depois para análise de coerência local.
        """
        idx = block.index
        start = max(0, idx - 5)
        end = min(len(plan.blocks), idx + 6)

        surrounding = []
        for i in range(start, end):
            b = plan.blocks[i]
            surrounding.append({
                "index": b.index,
                "title": b.title,
                "content_snippet": b.content[:200] if b.content else "",
                "block_type": b.block_type.value,
            })

        return {
            "window_start": start,
            "window_end": end,
            "window_size": end - start,
            "blocks": surrounding,
        }

    def estimate_context_tokens(self, block: NanoBlock, plan: NanoPlan,
                                 mode: str = "write") -> int:
        """Estima o total de tokens no contexto.

        Usa aproximação: 1 token ≈ 4 caracteres em português.
        """
        context = self.build_context(block, plan, mode)
        # Estimativa grosseira baseada no JSON
        json_str = str(context)
        estimated = len(json_str) // 4
        return min(estimated, self.MAX_CONTEXT_TOKENS)

    def validate_context_budget(self, block: NanoBlock, plan: NanoPlan) -> dict:
        """Valida se o contexto cabe no limite do modelo.

        Returns:
            Dict com status da validação.
        """
        estimated = self.estimate_context_tokens(block, plan)

        return {
            "valid": estimated <= TOKEN_LIMIT_PER_BLOCK,
            "estimated_tokens": estimated,
            "limit": TOKEN_LIMIT_PER_BLOCK,
            "utilization": round(estimated / TOKEN_LIMIT_PER_BLOCK * 100, 1),
            "block_id": block.id,
        }
