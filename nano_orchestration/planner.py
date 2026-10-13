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
    MAX_PLANNED_BLOCKS = 50_000

    def __init__(self, lines_per_page: int = 35, blocks_per_page: int = 10):
        """Inicializa o planner.

        Args:
            lines_per_page: Linhas por lauda.
            blocks_per_page: Nanoblocos por lauda (target ~10 para 5000/500).
        """
        self.lines_per_page = self._positive_integer(lines_per_page, "lines_per_page")
        self.blocks_per_page = self._positive_integer(blocks_per_page, "blocks_per_page")

    @staticmethod
    def _positive_integer(value, label):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{label} deve ser inteiro positivo.")
        return value

    @staticmethod
    def _names(names):
        if not isinstance(names, (list, tuple)) or not names:
            raise ValueError("Informe uma lista não vazia de seções.")
        if any(not isinstance(name, str) or not name.strip() for name in names):
            raise ValueError("Cada seção deve ter nome não vazio.")
        normalized = [name.strip() for name in names]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Os nomes das seções devem ser únicos.")
        return normalized

    @classmethod
    def _sections(cls, sections):
        if (not isinstance(sections, (list, tuple)) or not sections or
                any(not isinstance(item, (list, tuple)) or len(item) != 2 for item in sections)):
            raise ValueError("Informe seções como pares de nome e páginas.")
        names = cls._names([item[0] for item in sections])
        return [(name, cls._positive_integer(item[1], "Páginas da seção"))
                for name, item in zip(names, sections)]

    def _calc_blocks_per_section(self, pages: int) -> int:
        """Calcula quantos nanoblocos para uma seção de N páginas."""
        return self._positive_integer(pages, "Páginas da seção") * self.blocks_per_page

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
        sections = self._sections(sections)
        allocated_pages = sum(p for _, p in sections)
        total_pages = allocated_pages if total_pages is None else self._positive_integer(total_pages, "total_pages")
        if total_pages != allocated_pages:
            raise ValueError("total_pages deve ser igual à soma das páginas das seções.")
        block_count = sum(self._calc_blocks_per_section(pages) for _, pages in sections)
        if block_count > self.MAX_PLANNED_BLOCKS:
            raise ValueError(f"O plano excede o orçamento de {self.MAX_PLANNED_BLOCKS} blocos.")

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
            "section_pages": [[name, pages] for name, pages in sections],
            "blocks_per_page": self.blocks_per_page,
        }

        return plan

    def validate_plan(self, plan: NanoPlan) -> dict:
        """Valida um plano existente contra os critérios de qualidade.

        Returns:
            Dict com métricas de validação.
        """
        errors = []
        warnings = []

        try:
            self._positive_integer(plan.total_pages, "total_pages")
        except ValueError as exc:
            errors.append(str(exc))
        try:
            section_names = self._names(plan.sections)
        except ValueError as exc:
            errors.append(str(exc))
            section_names = []
        if isinstance(plan.total_pages, int) and not isinstance(plan.total_pages, bool) and len(section_names) > plan.total_pages:
            errors.append("Há mais seções que páginas: a alocação inteira positiva é impossível.")
        if (isinstance(plan.total_blocks, bool) or not isinstance(plan.total_blocks, int)
                or plan.total_blocks <= 0 or plan.total_blocks != len(plan.blocks)):
            errors.append("Contador de blocos vazio ou divergente dos blocos do plano.")
        if len(plan.blocks) > self.MAX_PLANNED_BLOCKS:
            errors.append("O plano excede o orçamento de blocos.")
        coverage = {name: 0 for name in section_names}
        for block in plan.blocks:
            if block.section not in coverage:
                errors.append(f"Bloco {block.index}: seção não declarada no plano.")
            else:
                coverage[block.section] += 1
        if any(count == 0 for count in coverage.values()):
            errors.append("Uma ou mais seções declaradas não possuem blocos.")
        allocation_checked = False
        metadata = plan.metadata if isinstance(plan.metadata, dict) else {}
        if not isinstance(plan.metadata, dict):
            errors.append("Metadados de alocação inválidos.")
        if "section_pages" in metadata:
            try:
                allocation = self._sections(metadata["section_pages"])
                if [name for name, _ in allocation] != section_names:
                    raise ValueError("Seções da alocação divergem das seções do plano.")
                if sum(pages for _, pages in allocation) != plan.total_pages:
                    raise ValueError("Soma da alocação diverge de total_pages.")
                allocation_checked = True
                if "blocks_per_page" in metadata:
                    density = self._positive_integer(metadata["blocks_per_page"], "blocks_per_page")
                    if any(coverage[name] != pages * density for name, pages in allocation):
                        errors.append("Contagem de blocos por seção diverge da alocação persistida.")
            except ValueError as exc:
                errors.append(str(exc))
        else:
            warnings.append("Plano legado sem alocação de páginas: somente a estrutura foi examinada.")

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
            try:
                # JSON de checkpoint restaura o Enum str como texto. Aceitar
                # seus valores conhecidos sem alterar o plano carregado.
                block_type = BlockType(b.block_type)
            except (TypeError, ValueError):
                errors.append(f"Bloco {b.index}: tipo não reconhecido.")
                continue
            type_counts[block_type] = type_counts.get(block_type, 0) + 1

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
            "score": round(max(0.0, 10.0 - (len(errors) * 2.0 + len(warnings) * 0.5)), 2),
            "page_allocation_checked": allocation_checked,
            "validation_scope": "pages_and_structure" if allocation_checked else
                                "structure_only_missing_page_allocation" if "section_pages" not in metadata else
                                "structure_with_invalid_page_allocation",
        }

    def estimate_from_pages(self, total_pages: int,
                            section_names: Optional[list[str]] = None) -> dict:
        """Estima o plano sem executá-lo.

        Útil para preview antes de commit.
        """
        total_pages = self._positive_integer(total_pages, "total_pages")
        if section_names is None:
            section_names = [
                "Introdução", "Fundamentação Teórica", "Metodologia",
                "Resultados", "Discussão", "Conclusão"
            ]

        section_names = self._names(section_names)
        if total_pages < len(section_names):
            raise ValueError("O total de páginas deve cobrir as seções com pelo menos uma página cada; informe menos seções explicitamente.")
        # Reserva uma página por seção; distribui o restante por maiores
        # restos inteiros, sem arredondamento que prejudique a última seção.
        weights = [12, 25, 15, 18, 20, 10] if len(section_names) == 6 else [1] * len(section_names)
        denominator = sum(weights)
        remaining = total_pages - len(section_names)
        shares = [divmod(remaining * weight, denominator) for weight in weights]
        pages = [1 + quotient for quotient, _ in shares]
        residual = remaining - sum(quotient for quotient, _ in shares)
        order = sorted(range(len(section_names)), key=lambda index: (-shares[index][1], index))
        for index in order[:residual]:
            pages[index] += 1
        sections = list(zip(section_names, pages))

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
