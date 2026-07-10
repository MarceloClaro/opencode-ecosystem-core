# -*- coding: utf-8 -*-
"""
FallacyDetector — Detecção de Falácias Lógicas e Vieses Cognitivos (R113)
==========================================================================
Detector heurístico (por frases-gatilho, PT-BR + EN) de 15 falácias lógicas
clássicas e 4 vieses cognitivos comuns em argumentos textuais.

Não é um classificador semântico/LLM — é pattern-matching determinístico
sobre frases-gatilho conhecidas, no mesmo espírito de outros detectores
heurísticos já existentes no ecossistema (ex.:
``agentic_science_v2.review_agent.ReviewLedger.extract_claim``, que
classifica risco de claims por palavras-chave). Detecta o USO EXPLÍCITO
de padrões retóricos de falácia no texto, não a validade lógica profunda
do argumento subjacente — falso-negativos são esperados quando a falácia
não usa nenhuma das frases-gatilho catalogadas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class FallacyMatch:
    """Uma ocorrência detectada de falácia/viés no texto analisado."""
    fallacy_id: str
    name: str
    category: str          # "fallacy" | "cognitive_bias"
    matched_cues: List[str] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fallacy_id": self.fallacy_id,
            "name": self.name,
            "category": self.category,
            "matched_cues": self.matched_cues,
            "confidence": self.confidence,
            "explanation": self.explanation,
        }


# ============================================================
# Catálogo: 15 falácias lógicas clássicas
# ============================================================

FALLACY_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "ad_hominem": {
        "name": "Ad Hominem",
        "explanation": "Ataca a pessoa que argumenta em vez do argumento em si.",
        "cues": [
            "você é burro", "voce e burro", "só um idiota diria isso",
            "so um idiota diria isso", "você não tem credibilidade",
            "voce nao tem credibilidade", "ele é um mentiroso, então",
            "ela é hipócrita, então", "typical of someone like you",
            "que ridículo vindo de você", "que ridiculo vindo de voce",
        ],
    },
    "straw_man": {
        "name": "Espantalho (Straw Man)",
        "explanation": "Distorce o argumento do oponente para depois refutar a versão distorcida.",
        "cues": [
            "então você está dizendo que", "entao voce esta dizendo que",
            "ou seja, você quer que", "isso é basicamente dizer que",
            "isso e basicamente dizer que", "so what you're saying is",
            "in other words you want",
        ],
    },
    "false_dilemma": {
        "name": "Falso Dilema",
        "explanation": "Apresenta apenas duas opções quando existem mais alternativas.",
        "cues": [
            "ou você está comigo ou", "ou voce esta comigo ou",
            "só existem duas opções", "so existem duas opcoes",
            "ou isso ou aquilo, não há meio termo",
            "either you're with us or", "there are only two options",
            "é uma questão de preto no branco", "e uma questao de preto no branco",
        ],
    },
    "slippery_slope": {
        "name": "Declive Escorregadio (Slippery Slope)",
        "explanation": "Assume que um evento levará inevitavelmente a uma cadeia de consequências extremas.",
        "cues": [
            "se isso acontecer, então vai levar a", "isso vai abrir um precedente perigoso",
            "vai dar errado inevitavelmente", "if we allow this then",
            "next thing you know", "vai acabar destruindo tudo",
        ],
    },
    "appeal_to_authority": {
        "name": "Apelo à Autoridade",
        "explanation": "Usa a autoridade de alguém como prova, sem avaliar o argumento em si.",
        "cues": [
            "um especialista disse que", "segundo um cientista famoso",
            "porque fulano disse", "because an expert said",
            "authorities agree that", "e assim porque um phd afirmou",
            "e assim porque um especialista afirmou",
        ],
    },
    "bandwagon": {
        "name": "Apelo à Popularidade (Bandwagon)",
        "explanation": "Argumenta que algo é verdadeiro/correto só porque muitos acreditam nisso.",
        "cues": [
            "todo mundo concorda que", "a maioria das pessoas pensa assim",
            "é senso comum que", "e senso comum que",
            "everyone agrees that", "most people believe",
            "é óbvio pra todo mundo", "e obvio pra todo mundo",
        ],
    },
    "appeal_to_emotion": {
        "name": "Apelo à Emoção",
        "explanation": "Manipula emoções (medo, pena, indignação) no lugar de evidência lógica.",
        "cues": [
            "pense nas crianças", "pense nas criancas", "imagine o sofrimento",
            "isso vai deixar todos tristes", "think of the children",
            "imagine how sad", "é desumano não concordar", "e desumano nao concordar",
        ],
    },
    "circular_reasoning": {
        "name": "Raciocínio Circular (Petição de Princípio)",
        "explanation": "A conclusão é usada como premissa — o argumento pressupõe o que deveria provar.",
        "cues": [
            "é verdade porque é verdade", "e verdade porque e verdade",
            "isso prova que, porque isso prova que", "porque sim",
            "because it just is", "it's true because it's true",
        ],
    },
    "hasty_generalization": {
        "name": "Generalização Apressada",
        "explanation": "Generaliza a partir de uma amostra pequena ou não representativa.",
        "cues": [
            "um caso já prova que sempre", "um caso ja prova que sempre",
            "vi isso uma vez, então sempre", "vi isso uma vez, entao sempre",
            "todo mundo desse grupo é assim", "todo mundo desse grupo e assim",
            "one example proves that all", "based on this single case",
        ],
    },
    "post_hoc": {
        "name": "Falácia da Causa Falsa (Post Hoc)",
        "explanation": "Assume causalidade apenas porque um evento seguiu outro no tempo.",
        "cues": [
            "depois disso, então foi causado por", "depois disso, entao foi causado por",
            "aconteceu logo após, então deve ter sido causa",
            "correlação prova causalidade", "correlacao prova causalidade",
            "after this therefore because of this", "since it happened right after",
        ],
    },
    "red_herring": {
        "name": "Distração (Red Herring)",
        "explanation": "Introduz um assunto irrelevante para desviar da questão original.",
        "cues": [
            "mas e sobre", "isso não importa, o que importa é",
            "isso nao importa, o que importa e", "muda de assunto para",
            "let's talk about something else", "that's not the real issue, the real issue is",
        ],
    },
    "tu_quoque": {
        "name": "Apelo à Hipocrisia (Tu Quoque)",
        "explanation": "Rejeita uma crítica apontando que o crítico também age assim, sem refutar o argumento.",
        "cues": [
            "você também faz isso, então", "voce tambem faz isso, entao",
            "quem é você para falar", "quem e voce para falar",
            "você não tem moral para dizer isso", "voce nao tem moral para dizer isso",
            "you do it too so", "look who's talking",
        ],
    },
    "false_equivalence": {
        "name": "Falsa Equivalência",
        "explanation": "Trata duas coisas como equivalentes quando as diferenças relevantes são ignoradas.",
        "cues": [
            "é a mesma coisa que", "e a mesma coisa que", "isso é idêntico a",
            "isso e identico a", "é igualzinho a quando", "e igualzinho a quando",
            "that's the same as", "it's just like when",
        ],
    },
    "appeal_to_ignorance": {
        "name": "Apelo à Ignorância",
        "explanation": "Assume que algo é verdadeiro só porque não foi provado falso (ou vice-versa).",
        "cues": [
            "ninguém provou que é falso, então", "ninguem provou que e falso, entao",
            "não há evidência contra, então deve ser verdade",
            "nao ha evidencia contra, entao deve ser verdade",
            "no one has proven it false so", "there's no evidence against it so it must be true",
        ],
    },
    "anecdotal_evidence": {
        "name": "Evidência Anedótica",
        "explanation": "Usa uma experiência pessoal isolada como prova geral, ignorando dados sistemáticos.",
        "cues": [
            "conheço uma pessoa que", "conheco uma pessoa que",
            "minha experiência pessoal mostra que", "minha experiencia pessoal mostra que",
            "um amigo meu disse que", "i know someone who", "in my personal experience",
        ],
    },
}


# ============================================================
# Catálogo: 4 vieses cognitivos comuns
# ============================================================

BIAS_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "confirmation_bias": {
        "name": "Viés de Confirmação",
        "explanation": "Busca ou valoriza apenas evidências que confirmam uma crença pré-existente.",
        "cues": [
            "só considero as evidências que confirmam", "so considero as evidencias que confirmam",
            "ignorei os dados contrários", "ignorei os dados contrarios",
            "só aceito o que já acreditava", "so aceito o que ja acreditava",
        ],
    },
    "anchoring_bias": {
        "name": "Viés de Ancoragem",
        "explanation": "Depende excessivamente da primeira informação recebida (a âncora) para decisões subsequentes.",
        "cues": [
            "o primeiro número que vi foi", "o primeiro numero que vi foi",
            "fiquei preso na primeira estimativa", "ancorado no valor inicial",
        ],
    },
    "availability_heuristic": {
        "name": "Heurística da Disponibilidade",
        "explanation": "Superestima a frequência/probabilidade de algo por ser fácil de lembrar, não por dados reais.",
        "cues": [
            "é a primeira coisa que me vem à mente, então deve ser comum",
            "e a primeira coisa que me vem a mente, entao deve ser comum",
            "lembro de um caso recente, então acho que é frequente",
            "lembro de um caso recente, entao acho que e frequente",
        ],
    },
    "overconfidence_bias": {
        "name": "Viés de Excesso de Confiança",
        "explanation": "Confiança subjetiva na própria opinião muito maior do que a acurácia objetiva justificaria.",
        "cues": [
            "tenho certeza absoluta que", "é impossível eu estar errado",
            "e impossivel eu estar errado", "100% certo disso sem dúvida",
            "100% certo disso sem duvida",
        ],
    },
}


class FallacyDetector:
    """Detector heurístico de falácias lógicas e vieses cognitivos por
    frases-gatilho (PT-BR + EN), case-insensitive."""

    def __init__(self):
        self.fallacies = FALLACY_DEFINITIONS
        self.biases = BIAS_DEFINITIONS

    def _scan(self, text: str, catalog: Dict[str, Dict[str, Any]], category: str) -> List[FallacyMatch]:
        text_lower = text.lower()
        matches: List[FallacyMatch] = []
        for fid, definition in catalog.items():
            hits = [cue for cue in definition["cues"] if cue in text_lower]
            if hits:
                confidence = min(1.0, 0.5 + 0.15 * len(hits))
                matches.append(FallacyMatch(
                    fallacy_id=fid,
                    name=definition["name"],
                    category=category,
                    matched_cues=hits,
                    confidence=round(confidence, 2),
                    explanation=definition["explanation"],
                ))
        return matches

    def detect_fallacies(self, text: str) -> List[FallacyMatch]:
        """Escaneia o texto contra as 15 falácias lógicas catalogadas."""
        return self._scan(text, self.fallacies, "fallacy")

    def detect_biases(self, text: str) -> List[FallacyMatch]:
        """Escaneia o texto contra os 4 vieses cognitivos catalogados."""
        return self._scan(text, self.biases, "cognitive_bias")

    def analyze(self, text: str) -> Dict[str, Any]:
        """Análise crítica completa: falácias + vieses + sumário."""
        fallacy_matches = self.detect_fallacies(text)
        bias_matches = self.detect_biases(text)
        all_matches = fallacy_matches + bias_matches
        return {
            "fallacies_found": [m.to_dict() for m in fallacy_matches],
            "biases_found": [m.to_dict() for m in bias_matches],
            "total_issues": len(all_matches),
            "fallacy_catalog_size": len(self.fallacies),
            "bias_catalog_size": len(self.biases),
            "clean": len(all_matches) == 0,
        }


# Singleton de conveniência
fallacy_detector = FallacyDetector()
