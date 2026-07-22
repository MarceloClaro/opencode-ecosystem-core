"""CrossValidator — Validação Cruzada do Manuscrito Completo.

Verificações:
1. Transições entre todos os pares consecutivos
2. Consistência terminológica global
3. Detecção de contradições
4. Integridade estrutural
5. Score de coesão geral
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Optional

from . import (
    COHERENCE_SCORE_TARGET, NanoBlock, NanoPlan, ValidationReport,
)


logger = logging.getLogger(__name__)

# Termos acadêmicos centrais (exemplo — podem ser customizados)
DEFAULT_TERMS = [
    "análise", "método", "teoria", "dados", "resultado",
    "hipótese", "variável", "amostra", "correlação", "significância",
    "metodologia", "abordagem", "paradigma", "fenômeno", "contexto",
]


class CrossValidator:
    """Valida a consistência global do manuscrito.

    Características:
    - Validação de transições entre blocos consecutivos
    - Consistência terminológica (mesmo termo, mesmo significado)
    - Detecção de contradições lógicas
    - Score de coesão geral (0-10)
    """

    def __init__(self, terms: Optional[list[str]] = None):
        self.terms = terms or DEFAULT_TERMS
        self._term_occurrences: dict[str, list[int]] = {}

    def validate_transitions(self, plan: NanoPlan) -> list[dict]:
        """Valida transições entre todos os pares consecutivos.

        Para cada par (i, i+1):
        - Verifica se há conectivo no início do segundo
        - Verifica continuidade temática
        - Verifica se não há salto lógico

        Returns:
            Lista de relatórios por par.
        """
        reports = []
        blocks = plan.blocks

        for i in range(len(blocks) - 1):
            curr = blocks[i]
            nxt = blocks[i + 1]

            if not curr.content or not nxt.content:
                reports.append({
                    "pair": (i, i + 1),
                    "status": "incomplete",
                    "issues": ["Um ou ambos os blocos não têm conteúdo"],
                })
                continue

            curr_end = curr.content.strip()[-200:].lower()
            nxt_start = nxt.content.strip()[:200].lower()
            issues = []

            # 1. Conectivo no início do segundo bloco
            has_connector = any(
                nxt_start.startswith(device)
                for cat in COHESIVE_DEVICES.values()
                for device in cat
            )

            # 2. Continuidade temática: palavras do fim do curr no início do nxt
            curr_end_words = set(re.findall(r'\b\w{4,}\b', curr_end))
            nxt_start_words = set(re.findall(r'\b\w{4,}\b', nxt_start))
            overlap = len(curr_end_words & nxt_start_words)
            thematic_continuity = overlap >= 2 if curr_end_words and nxt_start_words else True

            # 3. Verifica se o nxt não contradiz o curr
            contradiction = self._detect_contradiction(curr_end, nxt_start)

            if contradiction:
                issues.append(f"Possível contradição detectada: {contradiction}")

            reports.append({
                "pair": (i, i + 1),
                "curr_title": curr.title,
                "next_title": nxt.title,
                "has_connector": has_connector,
                "thematic_overlap": overlap,
                "thematic_continuity": thematic_continuity,
                "contradiction": contradiction,
                "issues": issues,
                "status": "ok" if not issues else "warning",
            })

        return reports

    def validate_term_consistency(self, plan: NanoPlan) -> dict:
        """Verifica consistência terminológica global.

        Para cada termo chave:
        - Conta ocorrências em cada bloco
        - Verifica se o termo é usado consistentemente
        - Detecta termos que aparecem apenas uma vez

        Returns:
            Dict com métricas de consistência.
        """
        self._term_occurrences = {}
        total_blocks_with_terms = 0
        term_issues = []

        for block in plan.blocks:
            if not block.content:
                continue

            content_lower = block.content.lower()
            for term in self.terms:
                count = content_lower.count(term)
                if count > 0:
                    if term not in self._term_occurrences:
                        self._term_occurrences[term] = []
                    self._term_occurrences[term].append(block.index)

        for term, blocks_found in self._term_occurrences.items():
            n = len(blocks_found)
            if n == 1:
                term_issues.append(f"Termo '{term}' aparece em apenas 1 bloco")
            elif n < 3 and len(plan.blocks) > 10:
                term_issues.append(f"Termo '{term}' aparece em apenas {n} blocos")

        n_terms = len(self.terms)
        n_terms_found = len(self._term_occurrences)
        consistency = n_terms_found / max(n_terms, 1)

        return {
            "total_terms": n_terms,
            "terms_found": n_terms_found,
            "consistency_ratio": round(consistency, 3),
            "term_occurrences": {
                k: len(v) for k, v in self._term_occurrences.items()
            },
            "issues": term_issues,
            "score": round(consistency * 10, 2),
        }

    def _detect_contradiction(self, text_a: str, text_b: str) -> Optional[str]:
        """Detecta possíveis contradições entre dois textos.

        Procura padrões como:
        - "X é Y" vs "X não é Y"
        - Afirmação vs negação do mesmo conceito
        """
        # Padrões simples de contradição
        negations_b = re.findall(r'\b(não|nenhum|jamais|nunca|sem)\s+(\w+)', text_b)
        for neg, word in negations_b:
            if word in text_a:
                return f"'{word}' negado em B após uso em A"
        return None

    def validate_integrity(self, plan: NanoPlan) -> list[str]:
        """Valida integridade estrutural do manuscrito.

        Returns:
            Lista de issues de integridade.
        """
        issues = []

        # Todos os blocos têm conteúdo?
        empty_blocks = [b for b in plan.blocks if not b.content]
        if empty_blocks:
            issues.append(f"{len(empty_blocks)} blocos vazios")

        # Blocos em ordem crescente?
        indices = [b.index for b in plan.blocks]
        if indices != sorted(indices):
            issues.append("Blocos fora de ordem")

        # Todas as seções estão representadas?
        sections_with_blocks = set(b.section for b in plan.blocks)
        missing_sections = set(plan.sections) - sections_with_blocks
        if missing_sections:
            issues.append(f"Seções sem blocos: {missing_sections}")

        # Tamanhos dos blocos
        for b in plan.blocks:
            if b.content and len(b.content) < 200:
                issues.append(f"Bloco {b.index} muito curto ({len(b.content)} chars)")

        return issues

    def calculate_cohesion_score(self, plan: NanoPlan) -> float:
        """Calcula score de coesão geral do manuscrito.

        Fatores:
        - Conectivos por bloco (média)
        - Consistência terminológica
        - Transições suaves
        - Ausência de contradições

        Returns:
            Score 0-10.
        """
        if not plan.blocks:
            return 0.0

        # 1. Conectivos
        total_connectors = 0
        for block in plan.blocks:
            if block.content:
                for cat, devices in COHESIVE_DEVICES.items():
                    for device in devices:
                        total_connectors += block.content.lower().count(device)

        avg_connectors = total_connectors / max(len(plan.blocks), 1)
        connector_score = min(10.0, avg_connectors * 2)

        # 2. Terminologia
        term_consistency = self.validate_term_consistency(plan)
        term_score = term_consistency["score"]

        # 3. Transições
        transitions = self.validate_transitions(plan)
        ok_transitions = sum(1 for t in transitions if t["status"] == "ok")
        transition_ratio = ok_transitions / max(len(transitions), 1)
        transition_score = transition_ratio * 10

        # 4. Integridade
        integrity_issues = self.validate_integrity(plan)
        integrity_score = max(0, 10 - len(integrity_issues) * 2)

        # Média ponderada
        cohesion = (
            connector_score * 0.2
            + term_score * 0.25
            + transition_score * 0.35
            + integrity_score * 0.2
        )

        return round(min(10.0, cohesion), 2)

    def validate_all(self, plan: NanoPlan) -> ValidationReport:
        """Executa todas as validações e gera relatório completo.

        Returns:
            ValidationReport consolidado.
        """
        transitions = self.validate_transitions(plan)
        term_consistency = self.validate_term_consistency(plan)
        integrity_issues = self.validate_integrity(plan)
        cohesion = self.calculate_cohesion_score(plan)

        n_pairs = len(transitions)
        smooth = sum(1 for t in transitions if t["status"] == "ok")
        contradictions = sum(1 for t in transitions if t.get("contradiction"))

        report = ValidationReport(
            total_blocks=len(plan.blocks),
            validated_pairs=n_pairs,
            smooth_transitions=smooth,
            contradictions=contradictions,
            term_consistency=term_consistency["consistency_ratio"],
            cohesion_score=cohesion,
            passed=cohesion >= COHERENCE_SCORE_TARGET,
            details={
                "transitions": transitions,
                "term_consistency": term_consistency,
                "integrity_issues": integrity_issues,
            },
        )

        logger.info(
            f"Validação cruzada: {smooth}/{n_pairs} transições suaves, "
            f"{contradictions} contradições, "
            f"coesão {cohesion}/10"
        )

        return report


# Necessário para referência no validate_transitions
COHESIVE_DEVICES = {
    "adição": ["além disso", "ademais", "outrossim", "também", "ainda", "da mesma forma"],
    "contraste": ["contudo", "entretanto", "todavia", "por outro lado", "no entanto", "não obstante"],
    "causa": ["porque", "pois", "visto que", "já que", "uma vez que", "em virtude de"],
    "consequência": ["portanto", "assim", "dessa forma", "consequentemente", "por conseguinte", "logo"],
    "conclusão": ["em síntese", "em suma", "concluindo", "por fim", "finalmente", "para concluir"],
    "exemplificação": ["por exemplo", "como", "tais como", "a exemplo de", "nomeadamente"],
    "ordenação": ["primeiramente", "em primeiro lugar", "em segundo lugar", "por último"],
}
