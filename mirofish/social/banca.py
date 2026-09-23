"""
MiroFish Social — Banca Editorial ampliada (MIT, SPEC-976 R-976.11..R-976.14).

Simula a opinião de uma banca de publicação composta por revisores
especialistas (PhD por critério). R-976.12 adiciona PESO DO TEXTO nas
decisões: sinais textuais por critério modulam os biases dos revisores.
R-976.13 amplia a banca: 12 critérios, revisores por critério, instituições
de publicação de referência (rótulos de simulação) e veredito ponderado.
R-976.14 integra PERFIS EDITORIAIS de periódicos reais (normas públicas):
ao escolher um periódico-alvo, a avaliação usa os pesos/critérios do perfil
editorial daquele veículo (escopo, prioridade, gates especiais, fonte).

ANTI-OVERCLAIM (R110): isto é uma SIMULAÇÃO de banca, não revisão por pares
real. Não substitui submissão a periódico nem validação externa por humanos.
Os nomes de instituições/revistas são RÓTULOS de simulação para calibração
de perfil — não indicam afiliação, parecer real ou promessa editorial.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .contracts import OasisAgentProfile
from .editorial_profiles import (
    EDITORIAL_PROFILES,
    EditorialProfile,
    JOURNAL_KEYS,
    get_profile,
    merge_weights,
    profile_summary,
)

# ─────────────────────────────────────────────────────────────
# Critérios ampliados (R-976.13): 12 dimensões de avaliação
# ─────────────────────────────────────────────────────────────
CRITERIA = [
    "metodologia",
    "estatística",
    "ética",
    "originalidade",
    "clareza",
    "relevância",
    "teoria",
    "reprodutibilidade",
    "evidências",
    "redação",
    "coerência",
    "impacto",
]

POSITIONS = ["rigoroso", "equilibrado", "entusiasta", "cético"]

# Instituições de referência (rótulos de simulação — R-976.13/14).
# R-976.14: derivadas dos perfis editoriais reais (JOURNAL_KEYS) para que a
# banca rode sobre periódicos pesquisados, mantendo o aviso anti-overclaim.
_INSTITUTIONS = [f"{name} (Qualis A1 — simulação)" for name in JOURNAL_KEYS]


def resolve_institution_name(target_institution: Optional[str]) -> Optional[str]:
    """Resolve o rótulo de simulação a partir do nome do periódico."""
    if not target_institution:
        return None
    profile = get_profile(target_institution)
    if not profile:
        return None
    return f"{profile.journal} (Qualis A1 — simulação)"

# Sinais textuais por critério (R-976.12): termos que evidenciam solidez
# do manuscrito em cada dimensão. Frequência de acertos em 0..1.
_CRITERION_SIGNALS: Dict[str, List[str]] = {
    "metodologia": [
        r"método", r"metodologia", r"protocolo", r"PRISMA", r"JBI",
        r"triagem", r"critérios de inclusão", r"critérios de exclusão",
        r"extração", r"síntese", r"revisão de escopo", r"Joanna Briggs",
    ],
    "estatística": [
        r"kappa", r"κ", r"Po\s*=", r"Pe\s*=", r"concordância", r"n\s*=\s*\d+",
        r"95%", r"IC95", r"intervalo", r"frequência", r"porcentagem", r"%",
    ],
    "ética": [
        r"ética", r"integri", r"declaração", r"conflito de interesse",
        r"consentimento", r"comitê", r"CEP\b", r"anti-overclaim", r"plágio",
        r"integridade acadêmica", r"supervisão humana",
    ],
    "originalidade": [
        r"contribuição", r"original", r"lacuna", r"\bgap\b", r"ineditismo",
        r"avanço", r"diferencial", r"inovação", r"novidade",
        r"perspectiva comparada", r"Brasil-comparado",
    ],
    "clareza": [
        r"resumo", r"abstract", r"palavras-chave", r"keywords",
        r"tabela", r"figura", r"anexo", r"apêndice", r"seções", r"diagram",
    ],
    "relevância": [
        r"relevância", r"agenda", r"prioritária", r"impacto", r"formação",
        r"educação jurídica", r"política pública", r"urgente",
        r"aplicação prática", r"sala de aula",
    ],
    "teoria": [
        r"referencial", r"teórico", r"framework", r"quadro conceitual",
        r"teoria", r"fundamentação", r"marco", r"conceitual",
    ],
    "reprodutibilidade": [
        r"reprodut", r"dados", r"código", r"repositório", r"seed",
        r"OpenAlex", r"DOAJ", r"material suplementar", r"Zenodo", r"OSF",
        r"DOI",
    ],
    "evidências": [
        r"estudos incluídos", r"corpus", r"n\s*=\s*21", r"literatura",
        r"referências", r"2020", r"2026", r"triagem independente",
        r"consenso documentado",
    ],
    "redação": [
        r"ABNT", r"normas", r"formatação", r"citações", r"citação",
        r"NBR", r"referências", r"português", r"inglês",
    ],
    "coerência": [
        r"objetivo", r"método", r"resultados", r"discussão", r"conclusão",
        r"alinhamento", r"coerente", r"síntese",
    ],
    "impacto": [
        r"contribuição", r"implicações", r"política", r"ensino",
        r"aplicação", r"futuras", r"agenda", r"prioritária",
    ],
}

# Peso de cada critério na nota final ponderada (R-976.13).
CRITERION_WEIGHTS: Dict[str, float] = {
    "metodologia": 1.4,
    "estatística": 1.2,
    "ética": 1.2,
    "originalidade": 1.0,
    "clareza": 0.9,
    "relevância": 1.1,
    "teoria": 0.9,
    "reprodutibilidade": 1.2,
    "evidências": 1.3,
    "redação": 0.7,
    "coerência": 0.9,
    "impacto": 0.7,
}

# Decisão editorial por valor médio de sentimento (escala −1..1)
VERDICTS = [
    (0.6, "ACEITAR"),
    (0.2, "REVISÕES MENORES"),
    (-0.2, "REVISÕES MAIORES"),
    (-1.01, "REJEITAR"),
]


@dataclass
class BancaMember:
    """Revisor especialista da banca."""

    profile: OasisAgentProfile
    criterion: str
    institution: str
    position: str  # rigoroso | equilibrado | entusiasta | cético
    text_signal: float = 0.5   # 0..1 — força textual no critério (R-976.12)
    base_bias: float = 0.0     # bias puro da postura
    adjusted_bias: float = 0.0  # bias modulado pelo texto

    def to_dict(self) -> Dict[str, Any]:
        return {
            "criterion": self.criterion,
            "institution": self.institution,
            "position": self.position,
            "text_signal": round(self.text_signal, 4),
            "base_bias": round(self.base_bias, 4),
            "adjusted_bias": round(self.adjusted_bias, 4),
            "profile": self.profile.to_dict(),
        }


def _stance_from_position(position: str) -> str:
    return {
        "rigoroso": "opposing",      # cético, exige mais evidência
        "equilibrado": "neutral",
        "entusiasta": "supportive",
        "cético": "opposing",
    }[position]


def _bias_from_position(position: str) -> float:
    return {
        "rigoroso": -0.25,
        "equilibrado": 0.0,
        "entusiasta": 0.5,
        "cético": -0.5,
    }[position]


# ─────────────────────────────────────────────────────────────
# Sinais textuais (R-976.12)
# ─────────────────────────────────────────────────────────────
def text_signals(doc_text: str, criteria: Optional[List[str]] = None) -> Dict[str, float]:
    """Detecta solidez textual por critério: proporção de sinais encontrados.

    Cada critério tem uma lista de regex; `signal ∈ [0,1]` = acertos / total.
    Determinístico e stdlib-only.
    """
    criteria = criteria or CRITERIA
    text = (doc_text or "").lower()
    signals: Dict[str, float] = {}
    for criterion in criteria:
        patterns = _CRITERION_SIGNALS.get(criterion, [])
        if not patterns:
            signals[criterion] = 0.5  # sem sinais definidos → neutro
            continue
        # Padrões e texto em minúsculas para casar siglas (PRISMA, JBI,
        # OpenAlex, DOAJ, Zenodo, OSF, DOI, ABNT...) de forma determinística.
        hits = sum(1 for pattern in patterns if re.search(pattern.lower(), text))
        signals[criterion] = hits / len(patterns)
    return signals


def adjust_bias_by_signal(base_bias: float, signal: float, strength: float = 0.5) -> float:
    """Modula o bias-base pela força do sinal textual no critério.

    signal=0.5 → mantém postura; signal>0.5 (texto forte) → suaviza;
    signal<0.5 (texto fraco) → endurece. Limitado a [−1,1].
    """
    delta = (signal - 0.5) * 2.0 * strength  # ∈ [−strength, +strength]
    return max(-1.0, min(1.0, base_bias + delta))


# ─────────────────────────────────────────────────────────────
class BancaProfileGenerator:
    """Gera banca ampliada de revisores especialistas (R-976.12/13/14).

    Com n_members=12 revê cada critério com um PhD; com n_members>12
    repete critérios com posturas distintas. Os biases são modulados
    pelos sinais textuais do próprio manuscrito.

    R-976.14: `target_institution` escolhe o perfil editorial de um periódico
    real (normas públicas). Quando definido, todos os membros são afiliados ao
    rótulo do periódico-alvo e a nota ponderada usa os pesos do perfil
    editorial (merge com CRITERION_WEIGHTS).
    """

    def __init__(
        self,
        doc_text: str,
        n_members: int = 12,
        seed: int = 42,
        criteria: Optional[List[str]] = None,
        include_signal_adjust: bool = True,
        target_institution: Optional[str] = None,
    ):
        self.doc_text = doc_text or ""
        self.n_members = max(2, n_members)
        self.seed = seed
        self.criteria = criteria or CRITERIA
        self.include_signal_adjust = include_signal_adjust
        self.target_institution = target_institution
        self.editorial_profile: Optional[EditorialProfile] = (
            get_profile(target_institution) if target_institution else None
        )
        self._rng = random.Random(seed)
        self._signals: Optional[Dict[str, float]] = None
        self._effective_weights: Dict[str, float] = (
            merge_weights(CRITERION_WEIGHTS, self.editorial_profile.weights)
            if self.editorial_profile is not None
            else dict(CRITERION_WEIGHTS)
        )

    @property
    def effective_weights(self) -> Dict[str, float]:
        """Pesos usados na nota ponderada (perfil editorial ou default)."""
        return dict(self._effective_weights)

    def generate(self) -> List[BancaMember]:
        """Um revisor por critério, cíclico até n_members."""
        if self.include_signal_adjust:
            self._signals = text_signals(self.doc_text, self.criteria)

        members: List[BancaMember] = []
        # Se periódico-alvo definido, todos os membros são do rótulo dele;
        # senão, rotaciona pelas instituições de referência (R-976.13).
        target_label = resolve_institution_name(self.target_institution)
        for i in range(self.n_members):
            criterion = self.criteria[i % len(self.criteria)]
            position = POSITIONS[(i + i // len(self.criteria)) % len(POSITIONS)]
            first = self._rng.choice(self._names_first())
            last = self._rng.choice(self._names_last())
            institution = (
                target_label
                if target_label
                else _INSTITUTIONS[i % len(_INSTITUTIONS)]
            )

            base_bias = _bias_from_position(position)
            signal = (
                self._signals.get(criterion, 0.5)
                if self._signals is not None
                else 0.5
            )
            adjusted = adjust_bias_by_signal(base_bias, signal) if self.include_signal_adjust else base_bias

            profile = OasisAgentProfile(
                user_id=i + 1,
                user_name=f"reviewer_{i + 1:03d}",
                name=f"Prof. Dr. {first} {last}",
                bio=f"PhD em {criterion.capitalize()}, revisor(a) de {institution}.",
                persona=self._persona(criterion, position, signal),
                karma=0,
                follower_count=self._rng.randint(1000, 50000),
                statuses_count=self._rng.randint(100, 2000),
                age=self._rng.randint(35, 70),
                profession=f"Pesquisador(a) — {criterion}",
                interested_topics=[criterion],
                sentiment_bias=adjusted,
                stance=_stance_from_position(position),
                influence_weight=round(
                    self._rng.uniform(1.0, 4.0) * (0.8 + 0.4 * signal), 3
                ),
                activity_level=0.9,
            )
            members.append(
                BancaMember(
                    profile=profile,
                    criterion=criterion,
                    institution=institution,
                    position=position,
                    text_signal=signal,
                    base_bias=base_bias,
                    adjusted_bias=adjusted,
                )
            )
        return members

    def signals(self) -> Dict[str, float]:
        """Sinais textuais calculados (R-976.12) — dispara geração se preciso."""
        if self._signals is None:
            self._signals = text_signals(self.doc_text, self.criteria)
        return dict(self._signals)

    @staticmethod
    def _names_first() -> List[str]:
        return ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fábio", "Giovana",
                "Heitor", "Isabela", "João", "Karen", "Lucas", "Marina", "Nuno",
                "Olívia", "Paulo", "Rafael", "Sofia", "Thiago", "Vera"]

    @staticmethod
    def _names_last() -> List[str]:
        return ["Silva", "Santos", "Oliveira", "Pereira", "Costa", "Rodrigues",
                "Martins", "Souza", "Almeida", "Nunes"]

    def _persona(self, criterion: str, position: str, signal: float) -> str:
        base = f"Avalia rigorosamente o critério '{criterion}' da submissão."
        extra = {
            "rigoroso": "exige reprodutibilidade e limites claros; penaliza overclaim.",
            "equilibrado": "pondera mérito e limitações; vê potencial de revisão.",
            "entusiasta": "valoriza a contribuição e a inovação; sugere melhorias leves.",
            "cético": "questiona premissas e ameaças à validade; exige contraprovas.",
        }[position]
        sinal = "sinal textual fraco" if signal < 0.4 else (
            "sinal textual forte" if signal > 0.6 else "sinal textual mediano")
        return f"{base} ({sinal}). {extra}"


def banca_verdict(final_sentiment: float) -> Tuple[str, float]:
    """Converte sentimento médio (∈[−1,1]) em decisão editorial."""
    for threshold, verdict in VERDICTS:
        if final_sentiment >= threshold:
            return verdict, final_sentiment
    return "REJEITAR", final_sentiment


def banca_weighted_score(
    final_sentiment: float,
    by_criterion: Dict[str, Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Nota ponderada 0..100 por critério (R-976.13).

    Cada média de critério (∈[−1,1]) é mapeada para 0..100 e ponderada;
    o sentimento final entra com peso 1.0 como âncora global.
    """
    w = weights or CRITERION_WEIGHTS
    total_weight = 0.0
    weighted_sum = 0.0
    for crit, info in by_criterion.items():
        weight = w.get(crit, 1.0)
        total_weight += weight
        weighted_sum += (info["avg"] + 1) / 2 * 100 * weight
    if total_weight <= 0:
        return 50.0
    score = weighted_sum / total_weight
    # âncora global de sentimento
    global_anchor = (final_sentiment + 1) / 2 * 100
    return round(0.85 * score + 0.15 * global_anchor, 1)


def recommendation_from_score(score: float) -> str:
    if score >= 80:
        return "Aceitar com poucas sugestões (ensaio de submissão forte)."
    if score >= 65:
        return "Aceitar após revisões menores."
    if score >= 45:
        return "Revisões maiores antes de nova submissão."
    return "Rejeitar ou reformular substancialmente."


def summarize_banca(
    members: List[BancaMember],
    opinions: Dict[int, float],
    weights: Optional[Dict[str, float]] = None,
    signals: Optional[Dict[str, float]] = None,
    editorial_profile: Optional[EditorialProfile] = None,
) -> Dict[str, Any]:
    """Resumo por critério + sinais + decisão editorial ponderada.

    `editorial_profile` (R-976.14) anexa ao relatório o perfil do periódico
    alvo (escopo, prioridade, gates, fonte) com aviso anti-overclaim.
    """
    by_criterion: Dict[str, Dict[str, Any]] = {}
    for member in members:
        criterion = member.criterion
        entry = by_criterion.setdefault(criterion, {"count": 0, "sum": 0.0, "names": []})
        entry["count"] += 1
        entry["sum"] += opinions.get(member.profile.user_id, member.adjusted_bias)
        entry["names"].append(member.profile.name)

    per_criterion = {}
    for criterion, entry in by_criterion.items():
        per_criterion[criterion] = {
            "avg": round(entry["sum"] / entry["count"], 4),
            "reviewers": entry["names"],
        }

    final = (
        sum(opinions.values()) / len(opinions) if opinions else 0.0
    )
    verdict, _ = banca_verdict(final)
    score = banca_weighted_score(final, per_criterion, weights=weights)
    recommendation = recommendation_from_score(score)

    # Sinais textuais (R-976.12)
    text_sig = {
        crit: round(sig, 4)
        for crit, sig in (signals or {}).items()
    }

    # Fortalezas/fragilidades por critério
    strengths = [
        crit for crit, info in per_criterion.items() if info["avg"] >= 0.3
    ]
    weaknesses = [
        crit for crit, info in per_criterion.items() if info["avg"] <= -0.3
    ]

    result: Dict[str, Any] = {
        "final_sentiment": round(final, 4),
        "verdict": verdict,
        "weighted_score": score,
        "recommendation": recommendation,
        "by_criterion": per_criterion,
        "text_signals": text_sig,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "members": [m.to_dict() for m in members],
        "disclaimer": (
            "SIMULAÇÃO de banca editorial (SPEC-976 R-976.11–14). Não substitui "
            "revisão por pares real, não constitui validação externa e não "
            "representa parecer das instituições citadas. Instituições são "
            "rótulos de simulação para calibração de perfil. Perfis editoriais "
            "baseados em normas públicas das revistas, com finalidade de ensaio "
            "de submissão orientado."
        ),
    }
    if editorial_profile is not None:
        result["editorial_profile"] = {
            "journal": editorial_profile.journal,
            "scope": editorial_profile.scope,
            "priority": editorial_profile.priority,
            "reference_style": editorial_profile.reference_style,
            "length_limit": editorial_profile.length_limit,
            "review_flow": editorial_profile.review_flow,
            "special_gates": editorial_profile.special_gates,
            "source": editorial_profile.source,
        }
    return result