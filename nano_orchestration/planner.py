"""NanoPlanner — Decomposição top-down de manuscritos em nanoblocos.

Entrada: tema + especificação (estrutura de seções, páginas por seção)
Saída: NanoPlan com ~5000 nanoblocos ordenados topologicamente.
"""

from __future__ import annotations

import itertools
import math
import time
import uuid
from typing import Optional

from . import (
    LINE_RANGE, MODEL_TIER_BY_BLOCK_TYPE, NanoBlock, NanoPlan, BlockType, default_nano_block,
)


class NanoPlanner:
    """Planeja a decomposição de um manuscrito em nanoblocos.

    Características:
    - Decompõe N páginas em blocos de 80-120 linhas
    - Gera grafo de dependência entre blocos
    - Estima tokens por bloco
    - Atribui tipo a cada bloco
    """

    MIN_LINES = 5  # nanoblocos de ~300 tokens (~5 linhas)
    MAX_LINES = 15
    LINES_PER_PAGE = 35  # estimativa: 35 linhas por lauda A4

    def __init__(self, lines_per_page: int = 35, blocks_per_page: int = 10):
        """Inicializa o planner.

        Args:
            lines_per_page: Linhas por lauda.
            blocks_per_page: Nanoblocos por lauda (target ~10 para 5000/500).
        """
        self.lines_per_page = lines_per_page
        self.blocks_per_page = blocks_per_page

    def _calc_blocks_per_section(self, pages: int) -> int:
        """Calcula quantos nanoblocos para uma seção de N páginas."""
        return max(1, round(pages * self.blocks_per_page))

    def _block_type_for_section(self, section_name: str, block_idx: int,
                                 total_blocks: int) -> BlockType:
        """Determina o tipo de bloco baseado na seção e posição."""
        sn = section_name.lower()

        # Mapeamento de seção para tipo dominante
        if any(w in sn for w in ["introdução", "introducao", "introdução"]):
            if block_idx == 0:
                return BlockType.DESCRITIVO
            if block_idx == total_blocks - 1:
                return BlockType.TRANSICAO
            return BlockType.ARGUMENTATIVO

        if any(w in sn for w in ["fundamentação", "fundamentacao", "referencial",
                                  "revisão", "revisao", "literatura", "teórica",
                                  "teorica", "estado da arte"]):
            if block_idx % 5 == 0:
                return BlockType.CITAÇÃO
            return BlockType.ANALITICO

        if any(w in sn for w in ["metodologia", "método", "metodo", "materiais",
                                  "materiais e métodos", "materiais e metodos"]):
            return BlockType.METODOLOGIA

        if any(w in sn for w in ["resultado", "resultados"]):
            return BlockType.RESULTADO

        if any(w in sn for w in ["discussão", "discussao", "discussão dos",
                                  "análise", "analise"]):
            return BlockType.DISCUSSAO

        if any(w in sn for w in ["conclusão", "conclusao", "considerações",
                                  "consideracoes"]):
            return BlockType.CONCLUSÃO

        # Fallback: alterna entre descritivo e argumentativo
        return BlockType.ARGUMENTATIVO if block_idx % 2 == 0 else BlockType.DESCRITIVO

    def _build_dependency_graph(self, blocks: list[NanoBlock]) -> list[NanoBlock]:
        """Constrói grafo de dependências: cada bloco depende do anterior."""
        for i, block in enumerate(blocks):
            deps = []
            if i > 0:
                deps.append(i - 1)
            # Blocos analíticos também dependem do primeiro bloco da seção
            if block.block_type == BlockType.ANALITICO and i > 0:
                # Encontra o primeiro bloco da mesma seção
                for j in range(i - 1, -1, -1):
                    if blocks[j].section == block.section:
                        if j not in deps:
                            deps.append(j)
                        break
            block.dependencies = deps
        return blocks

    def _estimate_tokens(self, block: NanoBlock) -> int:
        """Estima tokens para um nanobloco baseado no tipo.

        Aproximação: 1 linha ≈ 15 tokens em português acadêmico.
        Nanoblocos têm ~5-15 linhas → ~75-225 tokens, mas ajustamos
        pela densidade do tipo de bloco.
        """
        avg_lines = (self.MIN_LINES + self.MAX_LINES) / 2
        tokens_per_line = 15
        base = int(avg_lines * tokens_per_line)

        # Ajuste por tipo
        adjustments = {
            BlockType.ANALITICO: 1.3,
            BlockType.DISCUSSAO: 1.2,
            BlockType.CITAÇÃO: 0.9,
            BlockType.TRANSICAO: 0.7,
            BlockType.CONCLUSÃO: 1.0,
        }
        return round(base * adjustments.get(block.block_type, 1.0))

    def plan(self, title: str, sections: list[tuple[str, int]],
             total_pages: Optional[int] = None) -> NanoPlan:
        """Planeja a decomposição.

        Args:
            title: Título do manuscrito.
            sections: Lista de (nome_da_seção, páginas).
            total_pages: Total de páginas (opcional, calculado se None).

        Returns:
            NanoPlan com todos os blocos planejados.
        """
        if not sections:
            raise ValueError("Pelo menos uma seção é necessária")

        if total_pages is None:
            total_pages = sum(p for _, p in sections)

        plan = NanoPlan(
            id=f"plan-{uuid.uuid4().hex[:12]}",
            title=title,
            total_pages=total_pages,
            created_at=time.time(),
            sections=[s for s, _ in sections],
        )

        blocks: list[NanoBlock] = []
        global_idx = 0

        for section_name, section_pages in sections:
            if section_pages <= 0:
                continue

            num_blocks = self._calc_blocks_per_section(section_pages)

            for bi in range(num_blocks):
                block_type = self._block_type_for_section(
                    section_name, bi, num_blocks
                )
                block = default_nano_block(
                    index=global_idx,
                    block_type=block_type,
                    section=section_name,
                    title=f"{section_name} — bloco {bi + 1}/{num_blocks}",
                )
                block.estimated_tokens = self._estimate_tokens(block)
                blocks.append(block)
                global_idx += 1

        # Constrói grafo de dependência
        blocks = self._build_dependency_graph(blocks)

        plan.blocks = blocks
        plan.total_blocks = len(blocks)
        plan.estimated_total_tokens = sum(b.estimated_tokens for b in blocks)
        plan.metadata = {
            "avg_blocks_per_section": round(len(blocks) / len(sections), 1),
            "total_lines_estimated": len(blocks) * (self.MIN_LINES + self.MAX_LINES) // 2,
        }

        return plan

    def validate_plan(self, plan: NanoPlan) -> dict:
        """Valida um plano existente contra os critérios de qualidade.

        Returns:
            Dict com métricas de validação.
        """
        errors = []
        warnings = []

        # CA-001: Blocos no range de nanoblocos (50-400 tokens)
        for b in plan.blocks:
            if b.estimated_tokens < 50 or b.estimated_tokens > 400:
                warnings.append(f"Bloco {b.index}: tokens estimados ({b.estimated_tokens}) fora do range")

        # CA-002: Grafo de dependência
        blocks_without_deps = [b for b in plan.blocks if not b.dependencies]
        if len(blocks_without_deps) > 1:
            # Primeiro bloco pode não ter dependências; outros devem ter
            extra = [b for b in blocks_without_deps if b.index > 0]
            if extra:
                errors.append(f"{len(extra)} blocos (não-iniciais) sem dependências")

        # CA-004: Tipos atribuídos
        type_counts = {}
        for b in plan.blocks:
            type_counts[b.block_type] = type_counts.get(b.block_type, 0) + 1

        # CA-005: Ordem topológica válida
        indices = [b.index for b in plan.blocks]
        if indices != sorted(indices):
            errors.append("Blocos não estão em ordem crescente de índice")

        # CA-006: Escala (check apenas se > 1000 blocos)
        if plan.total_blocks > 1000:
            # estimativa de tempo de planejamento
            pass

        return {
            "valid": len(errors) == 0,
            "total_blocks": plan.total_blocks,
            "total_sections": len(plan.sections),
            "estimated_tokens": plan.estimated_total_tokens,
            "block_types": {k.value: v for k, v in type_counts.items()},
            "errors": errors,
            "warnings": warnings,
            "score": round(10.0 - (len(errors) * 2.0 + len(warnings) * 0.5), 2),
        }

    def estimate_from_pages(self, total_pages: int,
                            section_names: Optional[list[str]] = None) -> dict:
        """Estima o plano sem executá-lo.

        Útil para preview antes de commit.
        """
        if section_names is None:
            section_names = [
                "Introdução", "Fundamentação Teórica", "Metodologia",
                "Resultados", "Discussão", "Conclusão"
            ]

        # Distribuição típica de páginas
        weights = [0.12, 0.25, 0.15, 0.18, 0.20, 0.10]
        assert len(weights) == len(section_names), "Pesos devem cobrir todas as seções"

        sections = []
        for name, w in zip(section_names, weights):
            pages = max(1, round(total_pages * w))
            sections.append((name, pages))

        # Ajustar para somar exatamente total_pages
        diff = total_pages - sum(p for _, p in sections)
        if diff != 0:
            sections[-1] = (sections[-1][0], sections[-1][1] + diff)

        plan = self.plan(title="Preview", sections=sections)
        val = self.validate_plan(plan)

        return {
            "total_pages": total_pages,
            "total_blocks": plan.total_blocks,
            "estimated_tokens": plan.estimated_total_tokens,
            "sections": sections,
            "blocks_per_section": {
                s: self._calc_blocks_per_section(p)
                for s, p in sections
            },
            "validation": val,
        }
