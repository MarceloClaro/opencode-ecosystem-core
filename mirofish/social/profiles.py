"""
MiroFish Social — gerador determinístico de perfis (MIT, stdlib).

Sem chamadas LLM: extrai tópicos do documento por frequência de termos e gera
N perfis heterogêneos com vieses cíclicos, personalidades e influências.
"""
from __future__ import annotations

import random
import re
import string
from typing import Dict, List, Tuple

from .contracts import OasisAgentProfile

_STANCES = ["supportive", "opposing", "neutral", "observer"]
_MBTI = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
         "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
_PROFESSIONS = ["Professor", "Engenheira", "Advogado", "Médica", "Artista",
                "Pesquisadora", "Empreendedor", "Professora", "Jornalista", "Analista"]
_NAMES_FIRST = ["Ana", "Bruno", "Carla", "Diego", "Elena", "Fábio", "Giovana",
                "Heitor", "Isabela", "João", "Karen", "Lucas", "Marina", "Nuno",
                "Olívia", "Paulo", "Quitéria", "Rafael", "Sofia", "Thiago"]
_NAMES_LAST = ["Silva", "Santos", "Oliveira", "Pereira", "Costa", "Rodrigues",
               "Martins", "Souza", "Almeida", "Nunes", "Ribeiro", "Carvalho",
               "Gomes", "Lima", "Araújo", "Melo"]


class SimulationProfileGenerator:
    """Gera perfis de agentes sociais a partir de um documento (determinístico)."""

    def __init__(self, doc_text: str, n_agents: int = 20, seed: int = 42):
        self.doc_text = doc_text or ""
        self.n_agents = max(1, n_agents)
        self.seed = seed
        self._rng = random.Random(seed)

    # ── util ────────────────────────────────────────────────────────

    def extract_topics(self, top_n: int = 6) -> List[str]:
        """Tópicos quentes: palavras mais frequentes (min 4 letras, sem stopwords PT)."""
        stopwords = {
            "para", "com", "sobre", "como", "mais", "que", "dos", "das", "uma", "sua",
            "pode", "ser", "por", "entre", "também", "esses", "esta", "tem", "muito",
            "estão", "forma", "caso", "segundo", "depois", "antes", "outro", "outra",
            "sobre", "durante", "quando", "onde", "sendo", "foram", "será", "podem",
        }
        words = re.findall(r"[A-Za-zÀ-ú]{4,}", self.doc_text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1
        ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
        return [w for w, _ in ranked[:top_n]]

    # ── geração ─────────────────────────────────────────────────────

    def generate(self) -> List[OasisAgentProfile]:
        topics = self.extract_topics()
        if not topics:
            topics = ["notícia", "evento", "debate"]
        profiles: List[OasisAgentProfile] = []
        for i in range(self.n_agents):
            stance = _STANCES[i % len(_STANCES)]
            # Viés de opinião derivado da postura
            if stance == "supportive":
                bias = round(self._rng.uniform(0.3, 1.0), 3)
            elif stance == "opposing":
                bias = round(self._rng.uniform(-1.0, -0.3), 3)
            elif stance == "observer":
                bias = round(self._rng.uniform(-0.15, 0.15), 3)
            else:
                bias = round(self._rng.uniform(-0.3, 0.3), 3)

            first = self._rng.choice(_NAMES_FIRST)
            last = self._rng.choice(_NAMES_LAST)
            profile = OasisAgentProfile(
                user_id=i + 1,
                user_name=f"user_{i + 1:03d}",
                name=f"{first} {last}",
                bio=f"Morador simulado interessado em {', '.join(topics[:2])}.",
                persona=self._build_persona(first, topics, stance),
                karma=self._rng.randint(100, 5000),
                friend_count=self._rng.randint(20, 800),
                follower_count=self._rng.randint(50, 20000),
                statuses_count=self._rng.randint(50, 2000),
                age=self._rng.randint(18, 70),
                gender=self._rng.choice(["feminino", "masculino", "não-binário"]),
                mbti=self._rng.choice(_MBTI),
                country=self._rng.choice(["Brasil", "Portugal", "Moçambique"]),
                profession=self._rng.choice(_PROFESSIONS),
                interested_topics=self._rng.sample(topics, k=min(3, len(topics))),
                sentiment_bias=bias,
                stance=stance,
                influence_weight=round(self._rng.uniform(0.3, 3.0), 3),
                activity_level=round(self._rng.uniform(0.2, 1.0), 3),
            )
            profiles.append(profile)
        return profiles

    def _build_persona(self, first: str, topics: List[str], stance: str) -> str:
        if stance == "supportive":
            return (f"{first} tende a apoiar mudanças relacionadas a {topics[0]}, "
                    "defendendo com argumentos otimistas.")
        if stance == "opposing":
            return (f"{first} costuma contestar narrativas sobre {topics[0]}, "
                    "sendo cético quanto a promessas.")
        if stance == "observer":
            return (f"{first} observa os debates sobre {topics[0]} com distanciamento "
                    "analítico.")
        return (f"{first} acompanha {', '.join(topics[:2])} com opiniões moderadas e "
                "alternantes.")


def determinist_slug(text: str, limit: int = 40) -> str:
    """Slug simples determinístico a partir de texto (para ids)."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    words = cleaned.split()
    if not words:
        return "documento"
    slug = "_".join(words[:4])
    return slug[:limit].rstrip("_")