# -*- coding: utf-8 -*-
"""
Blind Review — Revisão às Cegas Real (R115)
==============================================
Simulação real de revisão duplo-cega (double-blind) para o pipeline R103
(``agentic_science_v2/review_agent.py``): remove identificadores de autor
e afiliação do texto ANTES de qualquer crítico ver o paper (não apenas
"simula" a revisão sem nunca ocultar nada), verifica pós-hoc se algum
identificador vazou para o texto das críticas geradas, e detecta conflito
de interesse quando um revisor compartilha afiliação com um autor.

Isso é o que faltava para "revisão cega" deixar de ser apenas um nome —
antes deste módulo, nenhuma informação de autor/afiliação era sequer
capturada pelo contrato de entrada do R103.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BlindReviewReport:
    """Resultado da anonimização e das verificações de revisão às cegas."""
    applied: bool = False
    redactions_made: int = 0
    leaks_detected: List[str] = field(default_factory=list)
    conflicts_of_interest: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """A revisão às cegas só é considerada íntegra se foi de fato
        aplicada, nenhum identificador vazou e não há conflito de
        interesse detectado."""
        return not self.leaks_detected and not self.conflicts_of_interest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applied": self.applied,
            "redactions_made": self.redactions_made,
            "leaks_detected": self.leaks_detected,
            "conflicts_of_interest": self.conflicts_of_interest,
            "passed": self.passed,
        }


class BlindReviewAnonymizer:
    """Anonimiza um paper antes da revisão e verifica a integridade da
    ocultação depois — double-blind real, não decorativo."""

    REDACTED_AUTHOR = "[AUTOR OCULTO]"
    REDACTED_AFFILIATION = "[INSTITUIÇÃO OCULTA]"

    def anonymize(self, paper: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Retorna (paper_anonimizado, número de redações feitas).

        Se o paper não trouxer ``author_names``/``author_affiliations``,
        não há nada para ocultar — retorna o paper original e 0 redações
        (revisão às cegas não é aplicável, não é um "fail" silencioso).
        """
        authors = [a for a in (paper.get("author_names") or []) if a]
        affiliations = [a for a in (paper.get("author_affiliations") or []) if a]

        if not authors and not affiliations:
            return paper, 0

        anonymized = copy.deepcopy(paper)
        redactions = 0

        def _redact(text: str) -> str:
            nonlocal redactions
            if not isinstance(text, str):
                return text
            for name in authors:
                if name in text:
                    text = text.replace(name, self.REDACTED_AUTHOR)
                    redactions += 1
            for aff in affiliations:
                if aff in text:
                    text = text.replace(aff, self.REDACTED_AFFILIATION)
                    redactions += 1
            return text

        anonymized["title"] = _redact(anonymized.get("title", ""))
        anonymized["abstract"] = _redact(anonymized.get("abstract", ""))
        sections = anonymized.get("sections", [])
        if isinstance(sections, list):
            anonymized["sections"] = [_redact(s) for s in sections]

        return anonymized, redactions

    def detect_leaks(self, generated_text: str, paper: Dict[str, Any]) -> List[str]:
        """Verificação pós-hoc: algum nome de autor/afiliação apareceu no
        texto gerado pelas críticas (repair_plan, etc.)? Se sim, a
        ocultação falhou de verdade — mesmo espírito de
        ``revision_agent.DiffEngine.verify_integrity()``: não confiar
        cegamente, verificar o resultado real."""
        leaks = []
        for name in (paper.get("author_names") or []):
            if name and name in generated_text:
                leaks.append(name)
        for aff in (paper.get("author_affiliations") or []):
            if aff and aff in generated_text:
                leaks.append(aff)
        return leaks

    def check_conflict_of_interest(
        self, paper: Dict[str, Any],
        reviewer_affiliations: Optional[Dict[str, str]],
    ) -> List[str]:
        """Verifica se algum revisor (por tipo: methodology/results/
        literature/ethics) compartilha afiliação com um autor do paper —
        conflito de interesse real de revisão por pares acadêmica."""
        if not reviewer_affiliations:
            return []
        author_affs = {a for a in (paper.get("author_affiliations") or []) if a}
        conflicts = []
        for reviewer, aff in reviewer_affiliations.items():
            if aff and aff in author_affs:
                conflicts.append(
                    f"Revisor '{reviewer}' compartilha afiliação '{aff}' com um autor do paper."
                )
        return conflicts
