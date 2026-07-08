# -*- coding: utf-8 -*-
"""
SPEC-924: Legal Impact Scanner
==============================
Avalia pesquisas, produções e artefatos quanto a impacto jurídico,
conformidade e maturidade metacognitiva jurídica.

O scanner mede duas classes de saída:
  1. prontidão jurídica (compliance / defensibilidade / risco)
  2. ganho metacognitivo jurídico (awareness normativa, antecipação de risco,
     detecção de conflito normativo e humildade epistêmica aplicada)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Iterable, Tuple, Optional


@dataclass
class LegalDimensionAssessment:
    name: str
    score: float
    findings: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LegalMetacognitiveAssessment:
    compliance_awareness: float = 0.0
    normative_conflict_detection: float = 0.0
    risk_anticipation: float = 0.0
    epistemic_humility_legal: float = 0.0

    @property
    def overall(self) -> float:
        return round(
            (
                self.compliance_awareness
                + self.normative_conflict_detection
                + self.risk_anticipation
                + self.epistemic_humility_legal
            ) / 4.0,
            2,
        )


@dataclass
class LegalImpactReport:
    title: str
    artifact_type: str
    overall_score: float
    legal_readiness: str
    high_risk_flags: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    dimensions: List[LegalDimensionAssessment] = field(default_factory=list)
    metacognitive: LegalMetacognitiveAssessment = field(
        default_factory=LegalMetacognitiveAssessment
    )

    @property
    def metacognitive_gain_score(self) -> float:
        return self.metacognitive.overall

    def as_dict(self) -> Dict:
        payload = asdict(self)
        payload["metacognitive_gain_score"] = self.metacognitive_gain_score
        return payload


def _normalize(score: float) -> float:
    return max(0.0, min(100.0, round(score, 2)))


class LegalImpactScanner:
    """Scanner jurídico de impacto para pesquisas e produções."""

    SIGNALS: Dict[str, Dict[str, Iterable[str]]] = {
        "data_protection": {
            "positive": [
                "lgpd", "anonimiz", "pseudonimiz", "consentimento",
                "base legal", "minimização", "dados pessoais", "privacidade",
            ],
            "negative": [
                "cpf", "rg", "dados sensíveis", "biometria",
                "vazamento", "reidentificação",
            ],
        },
        "intellectual_property": {
            "positive": [
                "licença", "copyright", "creative commons", "atribuição",
                "propriedade intelectual", "uso autorizado", "fair use",
            ],
            "negative": [
                "pirataria", "sem licença", "uso não autorizado",
                "plágio", "cópia integral",
            ],
        },
        "regulatory_ethics": {
            "positive": [
                "comitê de ética", "cep", "conep", "conformidade",
                "compliance", "regulatório", "aprovação ética",
                "termo de consentimento",
            ],
            "negative": [
                "sem aprovação ética", "não autorizado", "violação ética",
                "irregular", "não consentido",
            ],
        },
        "jurisprudential_grounding": {
            "positive": [
                "stf", "stj", "jurisprud", "súmula", "precedente",
                "ratio decidendi", "repercussão geral", "resp", "adi",
                "adpf", "art.", "lei ", "cf/88", "cpc/2015",
            ],
            "negative": [
                "sem fundamento legal", "opinião pessoal", "achismo",
            ],
        },
        "contractual_liability": {
            "positive": [
                "responsabilidade", "cláusula", "indenização", "obrigação",
                "limitação de responsabilidade", "rescisão", "inadimplemento",
            ],
            "negative": [
                "sem contrato", "sem garantia", "sem responsabilização",
            ],
        },
        "publication_defensibility": {
            "positive": [
                "limitações", "risco", "abstenção", "revisão jurídica",
                "validade externa", "replicabilidade", "fonte", "citação",
            ],
            "negative": [
                "garantido", "sem risco", "100% seguro", "sem revisão",
                "verificado automaticamente",
            ],
        },
    }

    META_SIGNALS = {
        "compliance_awareness": [
            "lgpd", "licença", "compliance", "regulatório", "ética", "consentimento",
        ],
        "normative_conflict_detection": [
            "conflito", "colisão", "ponderação", "trade-off", "tensão",
            "equilíbrio", "distinguishing",
        ],
        "risk_anticipation": [
            "risco", "mitigação", "contingência", "impacto", "litígio",
            "responsabilidade", "exposição",
        ],
        "epistemic_humility_legal": [
            "limitação", "incerteza", "pode exigir revisão", "abstenção",
            "necessita parecer", "não substitui advogado", "cautela",
        ],
    }

    def _count_hits(self, text: str, terms: Iterable[str]) -> int:
        lowered = text.lower()
        return sum(1 for term in terms if term in lowered)

    def _assess_dimension(self, text: str, name: str) -> LegalDimensionAssessment:
        cfg = self.SIGNALS[name]
        pos_hits = self._count_hits(text, cfg["positive"])
        neg_hits = self._count_hits(text, cfg["negative"])
        score = _normalize(50 + pos_hits * 10 - neg_hits * 12)

        findings: List[str] = []
        risks: List[str] = []
        recommendations: List[str] = []

        if pos_hits:
            findings.append(f"Sinais positivos detectados em {name}: {pos_hits}")
        if neg_hits:
            risks.append(f"Sinais de risco detectados em {name}: {neg_hits}")

        if score < 40:
            recommendations.append(
                f"Reforçar a dimensão '{name}' com salvaguardas explícitas, referências normativas e revisão jurídica."
            )
        elif score < 70:
            recommendations.append(
                f"A dimensão '{name}' está parcial; ampliar evidências, disclaimers e controles preventivos."
            )
        else:
            findings.append(f"A dimensão '{name}' apresenta boa prontidão jurídica.")

        return LegalDimensionAssessment(
            name=name,
            score=score,
            findings=findings,
            risks=risks,
            recommendations=recommendations,
        )

    def _assess_metacognition(self, text: str) -> LegalMetacognitiveAssessment:
        def score_for(name: str) -> float:
            hits = self._count_hits(text, self.META_SIGNALS[name])
            return _normalize(min(100.0, hits * 20.0 + (20.0 if hits else 0.0)))

        return LegalMetacognitiveAssessment(
            compliance_awareness=score_for("compliance_awareness"),
            normative_conflict_detection=score_for("normative_conflict_detection"),
            risk_anticipation=score_for("risk_anticipation"),
            epistemic_humility_legal=score_for("epistemic_humility_legal"),
        )

    def _build_report(self, title: str, artifact_type: str, text: str) -> LegalImpactReport:
        dims = [self._assess_dimension(text, name) for name in self.SIGNALS.keys()]
        overall = _normalize(sum(d.score for d in dims) / max(len(dims), 1))
        meta = self._assess_metacognition(text)

        flags: List[str] = []
        strengths: List[str] = []
        improvements: List[str] = []
        for dim in dims:
            if dim.score < 40:
                flags.append(dim.name)
            if dim.score >= 70:
                strengths.append(dim.name)
            improvements.extend(dim.recommendations)

        if overall >= 80:
            readiness = "alta"
        elif overall >= 60:
            readiness = "moderada"
        elif overall >= 40:
            readiness = "inicial"
        else:
            readiness = "crítica"

        return LegalImpactReport(
            title=title,
            artifact_type=artifact_type,
            overall_score=overall,
            legal_readiness=readiness,
            high_risk_flags=flags,
            strengths=strengths,
            improvements=list(dict.fromkeys(improvements)),
            dimensions=dims,
            metacognitive=meta,
        )

    def analyze_research_paper(
        self,
        titulo: str,
        resumo: str,
        metodologia: str,
        resultados: str,
        conclusoes: str,
        palavras_chave: Optional[List[str]] = None,
        area_conhecimento: str = "",
    ) -> LegalImpactReport:
        text = "\n".join(
            [
                titulo,
                area_conhecimento,
                " ".join(palavras_chave or []),
                resumo,
                metodologia,
                resultados,
                conclusoes,
            ]
        )
        return self._build_report(titulo or "Pesquisa", "research_paper", text)

    def analyze_production_artifact(
        self,
        descricao: str,
        corpus: str,
        artifact_type: str = "production_artifact",
    ) -> LegalImpactReport:
        text = f"{descricao}\n{corpus}"
        return self._build_report(descricao or "Produção", artifact_type, text)


__all__ = [
    "LegalDimensionAssessment",
    "LegalMetacognitiveAssessment",
    "LegalImpactReport",
    "LegalImpactScanner",
]
