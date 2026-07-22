"""NanoSDD Engine — Geração automática de mini-specs para cada nanobloco.

Cada nanobloco recebe 3-5 critérios de aceitação verificáveis,
um template de saída esperada, e contexto mínimo de vizinhança.
"""

from __future__ import annotations

import uuid
from typing import Optional

from . import (
    BlockType, Criterion, NanoBlock, NanoPlan, default_nano_block,
)


CRITERIA_TEMPLATES: dict[BlockType, list[tuple[str, int]]] = {
    BlockType.DESCRITIVO: [
        ("O texto descreve o cenário ou conceito proposto com clareza", 3),
        ("Não contém juízos de valor ou opiniões não fundamentadas", 4),
        ("Vocabulário preciso e adequado ao contexto acadêmico", 3),
        ("Extensão entre 5 e 15 linhas", 3),
        ("Parágrafos com estrutura tópico-desenvolvimento", 3),
    ],
    BlockType.ARGUMENTATIVO: [
        ("Apresenta uma tese clara apoiada por evidências", 5),
        ("Estrutura lógica: premissa → evidência → conclusão", 5),
        ("Cita fontes relevantes quando necessário", 4),
        ("Contra-argumentos são considerados quando pertinente", 3),
        ("Transição suave para o próximo bloco", 3),
    ],
    BlockType.ANALITICO: [
        ("Análise aprofunda o tema com múltiplas perspectivas", 5),
        ("Estabelece relações entre conceitos (causa, analogia, contraste)", 5),
        ("Uso de terminologia técnica consistente", 4),
        ("Referencia autores e obras pertinentes", 4),
        ("Conclusão parcial sintetiza os pontos principais", 4),
    ],
    BlockType.TRANSICAO: [
        ("Conecta o bloco anterior ao próximo de forma fluida", 4),
        ("Retoma conceito-chave do bloco anterior", 3),
        ("Antecipa conceito do próximo bloco sem revelá-lo completamente", 3),
        ("Extensão entre 40 e 80 linhas", 3),
    ],
    BlockType.CITAÇÃO: [
        ("Citação é relevante para o argumento da seção", 4),
        ("Fonte é corretamente identificada (autor, ano, obra)", 5),
        ("Citação é contextualizada antes e comentada depois", 4),
        ("Não excede 30% do bloco em citações diretas", 3),
    ],
    BlockType.METODOLOGIA: [
        ("Descreve o método com precisão e reprodutibilidade", 5),
        ("Justifica a escolha metodológica", 4),
        ("Identifica limitações do método", 3),
        ("Linguagem impessoal e objetiva", 4),
    ],
    BlockType.RESULTADO: [
        ("Apresenta resultados de forma objetiva e imparcial", 5),
        ("Dados são reportados com precisão (valores, estatísticas)", 5),
        ("Resultados são organizados por relevância", 3),
        ("Não interpreta resultados (reservado para Discussão)", 4),
    ],
    BlockType.DISCUSSAO: [
        ("Interpreta resultados à luz da literatura existente", 5),
        ("Identifica concordâncias e divergências com estudos anteriores", 5),
        ("Discute limitações do estudo", 4),
        ("Implicações práticas e teóricas são exploradas", 4),
        ("Não introduz resultados não reportados anteriormente", 4),
    ],
    BlockType.CONCLUSÃO: [
        ("Sintetiza as contribuições principais do trabalho", 5),
        ("Responde à pergunta de pesquisa ou tese inicial", 5),
        ("Aponta direções para trabalhos futuros", 3),
        ("Não introduz argumentos ou dados novos", 4),
        ("Tom conclusivo e assertivo", 3),
    ],
}


class NanoSDDEngine:
    """Gera mini-especificações formais para cada nanobloco.

    Características:
    - 3-5 critérios por bloco, cada um com peso 1-5
    - Critérios verificáveis automaticamente
    - Template de saída esperada
    - Contexto mínimo extraído
    """

    def generate_criteria(self, block: NanoBlock,
                          prev_block: Optional[NanoBlock] = None,
                          next_block: Optional[NanoBlock] = None) -> list[Criterion]:
        """Gera 3-5 critérios de aceitação para um nanobloco.

        Args:
            block: O nanobloco alvo.
            prev_block: Bloco anterior (para contexto de transição).
            next_block: Próximo bloco (para contexto de transição).

        Returns:
            Lista de critérios com pesos.
        """
        templates = CRITERIA_TEMPLATES.get(block.block_type, CRITERIA_TEMPLATES[BlockType.DESCRITIVO])
        criteria = []

        for i, (desc, weight) in enumerate(templates):
            crit = Criterion(
                id=f"{block.id}-c{i+1:02d}",
                description=desc,
                weight=weight,
            )
            criteria.append(crit)

        # Adiciona critério de transição contextual se houver vizinhos
        if prev_block and block.index > 0:
            criteria.append(Criterion(
                id=f"{block.id}-ctx-prev",
                description=f"Preserva continuidade com bloco anterior ({prev_block.title})",
                weight=4,
            ))

        if next_block:
            criteria.append(Criterion(
                id=f"{block.id}-ctx-next",
                description=f"Prepara transição para o próximo bloco ({next_block.title})",
                weight=3,
            ))

        return criteria

    def generate_prompt_template(self, block: NanoBlock) -> str:
        """Gera o template de prompt para escrever este bloco.

        Returns:
            String com o template de prompt.
        """
        type_instructions = {
            BlockType.DESCRITIVO: (
                "Descreva o cenário ou conceito com clareza e objetividade. "
                "Use linguagem acadêmica precisa. Mantenha tom neutro."
            ),
            BlockType.ARGUMENTATIVO: (
                "Construa um argumento lógico: apresente a tese, "
                "forneça evidências, conclua. Considere contra-argumentos."
            ),
            BlockType.ANALITICO: (
                "Analise o tema com profundidade, estabelecendo relações "
                "entre conceitos. Use múltiplas perspectivas. "
                "Terminologia técnica consistente."
            ),
            BlockType.TRANSICAO: (
                "Faça a transição suave entre os blocos anterior e próximo. "
                "Retome o conceito anterior e prepare o terreno para o próximo."
            ),
            BlockType.CITAÇÃO: (
                "Apresente e contextualize a citação. Explique sua relevância "
                "para o argumento. Comente após a citação."
            ),
            BlockType.METODOLOGIA: (
                "Descreva o método de forma precisa e reprodutível. "
                "Justifique a escolha. Identifique limitações. "
                "Linguagem impessoal."
            ),
            BlockType.RESULTADO: (
                "Apresente resultados de forma objetiva. Reporte dados "
                "com precisão. Organize por relevância. "
                "Não interprete (reservado para Discussão)."
            ),
            BlockType.DISCUSSAO: (
                "Interprete os resultados à luz da literatura. Compare com "
                "estudos anteriores. Discuta limitações e implicações."
            ),
            BlockType.CONCLUSÃO: (
                "Sintetize as contribuições principais. Responda à pergunta "
                "de pesquisa. Aponte trabalhos futuros. "
                "Não introduza argumentos novos."
            ),
        }

        instr = type_instructions.get(
            block.block_type,
            "Escreva o conteúdo acadêmico com clareza e precisão."
        )

        return (
            f"Você está escrevendo o bloco \"{block.title}\" "
            f"(seção: {block.section}).\n\n"
            f"Tipo: {block.block_type.value}\n"
            f"Instrução: {instr}\n\n"
            f"Extensão: entre 5 e 15 linhas (nanobloco acadêmico).\n"
            f"Tom: acadêmico formal em português brasileiro.\n\n"
            f"Critérios de qualidade:\n" +
            "\n".join(f"- [{c.weight}/5] {c.description}"
                      for c in block.criteria if c.weight >= 3)
        )

    def apply_criteria_to_plan(self, plan: NanoPlan) -> NanoPlan:
        """Aplica critérios a todos os blocos do plano."""
        for i, block in enumerate(plan.blocks):
            prev = plan.blocks[i - 1] if i > 0 else None
            nxt = plan.blocks[i + 1] if i < len(plan.blocks) - 1 else None
            block.criteria = self.generate_criteria(block, prev, nxt)
        return plan

    def validate_criteria_coverage(self, plan: NanoPlan) -> dict:
        """Valida a cobertura de critérios.

        Returns:
            Dict com métricas de validação.
        """
        blocks_without = [b for b in plan.blocks if not b.criteria]
        total_criteria = sum(len(b.criteria) for b in plan.blocks)
        criteria_per_block = total_criteria / max(1, len(plan.blocks))

        return {
            "valid": len(blocks_without) == 0,
            "total_blocks": len(plan.blocks),
            "total_criteria": total_criteria,
            "avg_criteria_per_block": round(criteria_per_block, 2),
            "blocks_without_criteria": len(blocks_without),
            "min_criteria": min((len(b.criteria) for b in plan.blocks), default=0),
            "max_criteria": max((len(b.criteria) for b in plan.blocks), default=0),
        }
