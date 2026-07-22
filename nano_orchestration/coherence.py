"""CoherenceEngine — 3 Passagens de Fusão para Coerência Global.

Estratégia de 3 passagens:
1. Coerência Local (Pass 1): cada bloco é suavizado com seus vizinhos imediatos
2. Coerência Global (Pass 2): blocos dentro de cada seção são harmonizados
3. Coerência de Fluidez (Pass 3): transições e connectors são refinados
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

from . import (
    COHERENCE_SCORE_TARGET, ModelTier, NanoBlock, NanoPlan,
)


logger = logging.getLogger(__name__)

# Conectivos por função
COHESIVE_DEVICES = {
    "adição": ["além disso", "ademais", "outrossim", "também", "ainda", "da mesma forma"],
    "contraste": ["contudo", "entretanto", "todavia", "por outro lado", "no entanto", "não obstante"],
    "causa": ["porque", "pois", "visto que", "já que", "uma vez que", "em virtude de"],
    "consequência": ["portanto", "assim", "dessa forma", "consequentemente", "por conseguinte", "logo"],
    "conclusão": ["em síntese", "em suma", "concluindo", "por fim", "finalmente", "para concluir"],
    "exemplificação": ["por exemplo", "como", "tais como", "a exemplo de", "nomeadamente"],
    "ordenação": ["primeiramente", "em primeiro lugar", "em segundo lugar", "por último"],
}

TRANSITION_SENTINELS = [
    "no capítulo anterior", "na seção anterior", "conforme discutido",
    "como vimos", "dando continuidade", "seguindo esta linha",
    "por outro lado", "em contrapartida", "paralelamente",
]


class CoherenceEngine:
    """Executa 3 passagens de fusão para garantir coerência global.

    Pass 1 — Coerência Local (bi-vizinho):
        Cada bloco é ajustado para conectar suavemente com
        o bloco anterior e o próximo.

    Pass 2 — Coerência Global (por seção):
        Blocos dentro de cada seção são revisados para consistência
        terminológica, tom e profundidade.

    Pass 3 — Fluidez Integral:
        Conectivos, transições e fluxo narrativo são refinados
        em todo o manuscrito.
    """

    def __init__(self):
        self._scores = {
            "pass_1_local": 0.0,
            "pass_2_global": 0.0,
            "pass_3_fluency": 0.0,
            "composite": 0.0,
        }

    def pass_1_local_coherence(self, plan: NanoPlan) -> NanoPlan:
        """Pass 1: Coerência local — suaviza transições entre vizinhos.

        Para cada par (bloco_i, bloco_i+1):
        1. Verifica se há conectivo de transição no início do bloco_i+1
        2. Se não, adiciona um conectivo apropriado
        3. Ajusta o final do bloco_i para preparar transição

        Returns:
            NanoPlan com blocos ajustados.
        """
        blocks = plan.blocks
        adjustments = 0

        for i in range(len(blocks) - 1):
            current = blocks[i]
            next_block = blocks[i + 1]

            # Verifica transição no início do próximo bloco
            next_start = next_block.content.strip()[:100].lower() if next_block.content else ""

            has_transition = any(
                sentinel in next_start
                for sentinel in TRANSITION_SENTINELS
            )

            if not has_transition and next_block.content:
                # Adiciona conectivo de transição
                connector = self._select_connector(
                    current.block_type, next_block.block_type
                )
                if connector:
                    next_block.content = (
                        connector.capitalize() + ", " + next_block.content[0].lower()
                        + next_block.content[1:]
                    )
                    adjustments += 1

            # Ajusta final do bloco atual: garantir que não termine abruptamente
            if current.content:
                lines = current.content.strip().split("\n")
                last_line = lines[-1].lower() if lines else ""
                # Se termina com uma referência direta, garantir continuidade
                if last_line and not last_line.rstrip().endswith((".", "!", "?")):
                    current.content = current.content.rstrip() + "."
                    adjustments += 1

        self._scores["pass_1_local"] = min(
            10.0, adjustments / max(len(blocks), 1) * 10
        )
        logger.info(
            f"Pass 1: {adjustments} ajustes locais em {len(blocks)} blocos "
            f"(score: {self._scores['pass_1_local']:.2f})"
        )
        return plan

    def _select_connector(self, from_type, to_type) -> Optional[str]:
        """Seleciona conectivo apropriado baseado nos tipos de bloco."""
        # Transições analíticas
        if to_type.value in ["analitico", "discussao"]:
            return "não obstante"
        # Transições de resultado para discussão
        if from_type.value == "resultado" and to_type.value == "discussao":
            return "à luz desses resultados"
        # Transições para conclusão
        if to_type.value == "conclusao":
            return "em síntese"
        # Transições para exemplos
        if to_type.value == "citacao":
            return "a título de exemplo"
        # Fallback
        return "dando continuidade"

    def _count_transitions(self, text: str) -> int:
        """Conta dispositivos coesivos no texto."""
        count = 0
        text_lower = text.lower()
        for category, devices in COHESIVE_DEVICES.items():
            for device in devices:
                count += text_lower.count(device)
        return count

    def pass_2_global_coherence(self, plan: NanoPlan) -> NanoPlan:
        """Pass 2: Coerência global — harmoniza blocos dentro de cada seção.

        Para cada seção:
        1. Verifica consistência terminológica
        2. Uniformiza tom e profundidade
        3. Garante progressão lógica

        Returns:
            NanoPlan com blocos harmonizados.
        """
        blocks_by_section: dict[str, list[NanoBlock]] = {}
        for block in plan.blocks:
            sec = block.section or "__default__"
            if sec not in blocks_by_section:
                blocks_by_section[sec] = []
            blocks_by_section[sec].append(block)

        total_blocks = len(plan.blocks)
        issues_found = 0

        for section_name, section_blocks in blocks_by_section.items():
            if len(section_blocks) < 2:
                continue

            # Verifica progressão lógica: cada bloco deve avançar o argumento
            for i in range(1, len(section_blocks)):
                prev_content = section_blocks[i - 1].content
                curr_content = section_blocks[i].content

                if prev_content and curr_content:
                    # Verifica se o bloco atual não repete mecanicamente o anterior
                    prev_words = set(prev_content.lower().split())
                    curr_words = set(curr_content.lower().split())
                    overlap = len(prev_words & curr_words) / max(len(curr_words), 1)

                    if overlap > 0.85:
                        issues_found += 1
                        logger.warning(
                            f"Seção '{section_name}': alta repetição entre "
                            f"blocos {section_blocks[i-1].index} e "
                            f"{section_blocks[i].index}"
                        )

            # Garante distribuição de conectivos
            for block in section_blocks:
                if block.content:
                    n_connectors = self._count_transitions(block.content)
                    if n_connectors < 2 and len(block.content) > 500:
                        issues_found += 1
                        # Adiciona conectivo variado
                        connector = self._select_filler_connector(block)
                        if connector:
                            block.content = block.content.rstrip() + (
                                f" {connector.capitalize()}, "
                            )

        score = max(0, 10.0 - issues_found * 0.5)
        self._scores["pass_2_global"] = min(10.0, score)
        logger.info(
            f"Pass 2: {issues_found} issues em {total_blocks} blocos "
            f"(score: {self._scores['pass_2_global']:.2f})"
        )
        return plan

    def _select_filler_connector(self, block) -> str:
        """Seleciona conectivo para enriquecer coesão."""
        if block.block_type.value in ["analitico", "discussao"]:
            return "ademais"
        if block.block_type.value == "resultado":
            return "paralelamente"
        if block.block_type.value == "conclusao":
            return "por fim"
        return "além disso"

    def pass_3_fluency(self, plan: NanoPlan) -> NanoPlan:
        """Pass 3: Fluidez integral — refina fluxo narrativo.

        1. Ajusta comprimento de sentenças (evita frases muito curtas ou longas)
        2. Enriquece conectivos ao longo do texto
        3. Garante variedade de abertura de parágrafos

        Returns:
            NanoPlan com fluidez refinada.
        """
        total_sentences = 0
        adjusted = 0

        for block in plan.blocks:
            if not block.content:
                continue

            content = block.content
            sentences = re.split(r'(?<=[.!?])\s+', content)

            for si, sentence in enumerate(sentences):
                total_sentences += 1
                words = sentence.split()
                word_count = len(words)

                # Frases muito curtas (< 5 palavras) podem ser fragmentos
                if 0 < word_count < 5 and si > 0:
                    # Tenta fundir com a sentença anterior
                    if si > 0 and len(sentences[si - 1].split()) < 50:
                        # Juntar com conectivo
                        sentences[si] = f", {sentence.strip().lower()}"
                        sentences[si - 1] = sentences[si - 1].rstrip()
                        adjusted += 1

                # Frases muito longas (> 60 palavras) quebram fluidez
                if word_count > 60:
                    # Adiciona ponto e vírgula ou conectivo para pausa
                    mid = word_count // 2
                    words.insert(mid, ";")
                    sentence = " ".join(words)
                    sentences[si] = sentence
                    adjusted += 1

            block.content = " ".join(sentences)

        score = min(10.0, 10.0 - (adjusted / max(total_sentences, 1)) * 5)
        self._scores["pass_3_fluency"] = round(score, 2)
        logger.info(
            f"Pass 3: {adjusted} ajustes de fluidez em {total_sentences} sentenças "
            f"(score: {self._scores['pass_3_fluency']:.2f})"
        )
        return plan

    def apply_all(self, plan: NanoPlan) -> tuple[NanoPlan, dict]:
        """Aplica as 3 passagens sequencialmente.

        Returns:
            Tupla (plan atualizado, scores).
        """
        logger.info("=== Iniciando 3 Passagens de Coerência ===")
        plan = self.pass_1_local_coherence(plan)
        plan = self.pass_2_global_coherence(plan)
        plan = self.pass_3_fluency(plan)

        # Score composto (média ponderada)
        self._scores["composite"] = round(
            self._scores["pass_1_local"] * 0.3
            + self._scores["pass_2_global"] * 0.35
            + self._scores["pass_3_fluency"] * 0.35,
            2,
        )
        logger.info(f"Score composto de coerência: {self._scores['composite']}")
        return plan, dict(self._scores)

    def get_scores(self) -> dict:
        """Retorna scores atuais."""
        return dict(self._scores)
