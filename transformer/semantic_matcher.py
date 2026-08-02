# -*- coding: utf-8 -*-
"""
SemanticMatcher — Matching Semântico de Capacidades (Melhoria #2)
=================================================================
Substitui o string-matching do catalog_loader por embeddings semânticos
gerados por LiteRT-LM (Gemma 4 / Qwen3) ou Colibri (OLMoE), com fallback
para feature hashing determinístico.

Baseado em:
  - Federation of Agents (FoA) — arXiv 2509.20175 (Giusti et al., 2025)
    Versioned Capability Vectors com embeddings semânticos + índice HNSW
  - IoA Discovery Framework — IEEE 2026 (Guo et al.)
    Two-stage: profiling semântico via LM + indexação escalável
  - SkillOrchestra — arXiv 2602.19672 (Wang et al., 2026)
    Skill Handbook com perfis de competência por skill

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

D_MODEL = 128  # dimensão do espaço semântico (vs 64 do embedder legado)

# Camada epistêmica (SPEC-935-R363) — fail-open se indisponível
try:
    from transformer.episteme import (
        episteme_affinity,
        infer_agent_episteme,
        infer_task_episteme,
    )
    _HAS_EPISTEME = True
except Exception:  # pragma: no cover - fail-open
    _HAS_EPISTEME = False

# Peso brando da afinidade epistêmica no score (±10% no máximo)
EPISTEME_WEIGHT = 0.20


# ═══════════════════════════════════════════════════════════════════════════
# 1. CAPABILITY VECTOR (Versão 1.0 — Versioned Capability Vector)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CapabilityVector:
    """Vetor de capacidades versionado (inspirado em VCVs do FoA).

    Cada skill de um agente vira um vetor no espaço semântico.
    O versionamento permite evolução sem quebrar referências.
    """
    agent_id: str
    skill_id: str
    vector: List[float]          # embedding d=128
    version: int = 1
    tags: List[str] = field(default_factory=list)
    text_source: str = ""        # texto usado para gerar o embedding
    created_at: float = field(default_factory=time.time)


# ═══════════════════════════════════════════════════════════════════════════
# 2. EMBEDDING ENGINE (com fallback hierárquico)
# ═══════════════════════════════════════════════════════════════════════════

def _tokenize(text: str) -> List[str]:
    """Tokenização multilingue com quebra de snake_case e camelCase.

    Antes: 'cloudsql_postgres_ad' → ['cloudsql_postgres_ad'] (1 token)
    Depois: → ['cloudsql', 'postgres', 'ad'] (3 tokens)

    Também quebra camelCase: 'cloudSqlPostgres' → ['cloud', 'sql', 'postgres']
    """
    # Quebra snake_case: cloudsql_postgres_ad → cloudsql postgres ad
    text = text.replace("_", " ")
    # Quebra camelCase: cloudSqlPostgres → cloud Sql Postgres → cloud sql postgres
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return re.findall(r"[a-zA-Zà-úÀ-Ú0-9]+", text.lower())


def _hash_embed(text: str, dim: int = D_MODEL) -> List[float]:
    """Feature hashing determinístico — fallback quando não há LLM disponível.

    Usa SHA-256 com pares de bytes para índice e sinal (stdlib pura).
    """
    vec = [0.0] * dim
    tokens = _tokenize(text)
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(0, min(16, len(digest) - 1), 2):
            idx = (digest[i] * 256 + digest[i + 1]) % dim
            sign = 1.0 if digest[i] % 2 == 0 else -1.0
            vec[idx] += sign
    return _normalize(vec)


def _normalize(vec: List[float]) -> List[float]:
    """Normalização L2."""
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Similaridade cosseno no intervalo [0, 1]."""
    dot = math.fsum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(math.fsum(x * x for x in a))
    norm_b = math.sqrt(math.fsum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    cos = dot / (norm_a * norm_b)
    return max(0.0, min(1.0, (cos + 1.0) / 2.0))


class EmbeddingEngine:
    """Motor de embeddings com fallback hierárquico.

    Hierarquia:
      1. LiteRT-LM (Gemma 4 / Qwen3 on-device) — melhor qualidade
      2. Colibri (OLMoE 1B/7B) — qualidade média, mais rápido
      3. Feature hashing (SHA-256) — fallback stdlib
    """

    def __init__(self, dim: int = D_MODEL):
        self.dim = dim
        self._provider: Optional[str] = None
        self._cache: Dict[str, List[float]] = {}
        self._stats = {"calls": 0, "cache_hits": 0, "provider": "hash"}
        self._probe_providers()

    def _probe_providers(self) -> None:
        """Testa provedores de embedding em ordem de qualidade."""
        # Tenta LiteRT-LM primeiro
        try:
            import sys
            sys.path.insert(0, "/home/marceloclaro/opencode-ecosystem-core")
            from litert_lm import LiteRTClient
            client = LiteRTClient()
            if client.health().get("status") == "ok":
                self._provider = "litert"
                self._stats["provider"] = "litert"
                return
        except Exception:
            pass

        # Tenta Colibri
        try:
            from colibri_mcp import ColibriClient
            client = ColibriClient()
            status = client.status()
            if status.get("ready"):
                self._provider = "colibri"
                self._stats["provider"] = "colibri"
                return
        except Exception:
            pass

        # Fallback: feature hashing
        self._provider = "hash"
        self._stats["provider"] = "hash"

    @property
    def provider(self) -> str:
        return self._provider or "hash"

    def embed(self, text: str, use_cache: bool = True) -> List[float]:
        """Gera embedding para um texto.

        Args:
            text: texto a ser embedado
            use_cache: se True, usa cache LRU simples

        Returns:
            Vetor normalizado d=128
        """
        cache_key = hashlib.sha256(text.encode()).hexdigest()[:32]
        if use_cache and cache_key in self._cache:
            self._stats["cache_hits"] += 1
            return self._cache[cache_key]

        self._stats["calls"] += 1

        if self._provider == "litert":
            vec = self._embed_litert(text)
        elif self._provider == "colibri":
            vec = self._embed_colibri(text)
        else:
            vec = _hash_embed(text, self.dim)

        # Cache LRU simples (máx 500)
        self._cache[cache_key] = vec
        if len(self._cache) > 500:
            # Remove primeiro item (aproximação LRU)
            self._cache.pop(next(iter(self._cache)))

        return vec

    def _embed_litert(self, text: str) -> List[float]:
        """Embedding via LiteRT-LM (Gemma 4 / Qwen3)."""
        try:
            from litert_lm import LiteRTClient
            client = LiteRTClient()
            # Usa o modelo para gerar embedding via hidden states
            # Ou usa a própria representação interna do modelo
            result = client.embed(text=text, model="litert-community/gemma-4-E2B-it-litert-lm")
            if result and "embedding" in result:
                vec = result["embedding"]
                if len(vec) == self.dim:
                    return _normalize(vec)
                # Se dimensão diferente, faz padding/truncation
                if len(vec) < self.dim:
                    vec = vec + [0.0] * (self.dim - len(vec))
                else:
                    vec = vec[:self.dim]
                return _normalize(vec)
        except Exception:
            pass
        # Fallback para hash se LLM falhar
        return _hash_embed(text, self.dim)

    def _embed_colibri(self, text: str) -> List[float]:
        """Embedding via Colibri (OLMoE 1B/7B)."""
        try:
            from colibri_mcp import ColibriClient
            client = ColibriClient()
            result = client.embed(text=text, max_tokens=128)
            if result and "embedding" in result:
                vec = result["embedding"]
                if len(vec) == self.dim:
                    return _normalize(vec)
                if len(vec) < self.dim:
                    vec = vec + [0.0] * (self.dim - len(vec))
                else:
                    vec = vec[:self.dim]
                return _normalize(vec)
        except Exception:
            pass
        return _hash_embed(text, self.dim)

    def get_stats(self) -> Dict[str, Any]:
        return dict(self._stats)


# ═══════════════════════════════════════════════════════════════════════════
# 3. SKILL HANDBOOK (SkillOrchestra — arXiv 2602.19672)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SkillProfile:
    """Perfil de uma skill de agente no Skill Handbook."""
    agent_id: str
    skill_id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.5       # trust per-skill (aprendido)
    executions: int = 0
    successes: int = 0
    avg_cost: float = 0.0          # custo médio por execução
    vector: Optional[List[float]] = None  # embedding cache
    episteme: Optional[str] = None  # regime epistemológico (SPEC-935-R363)


class SkillHandbook:
    """Skill Handbook — substituto do string-matching.

    Baseado em SkillOrchestra (arXiv 2602.19672):
    Em vez de aprender uma política de roteamento end-to-end,
    aprendemos perfis de competência por skill e selecionamos
    o agente que melhor atende às skills requeridas.

    Características:
    - Confiança por skill (não por agente)
    - Aprendizado contínuo (cada execução atualiza o perfil)
    - Custo médio por skill para trade-off performance/custo
    - Versionamento de vetores para evolução sem quebra
    """

    def __init__(self, engine: Optional[EmbeddingEngine] = None):
        self.engine = engine or EmbeddingEngine()
        self._profiles: Dict[Tuple[str, str], SkillProfile] = {}  # (agent_id, skill_id) -> profile
        self._agent_skills: Dict[str, List[str]] = {}  # agent_id -> [skill_ids]

    def _expand_tags(self, tags: Optional[List[str]]) -> List[str]:
        """Expande tags compostas em tokens individuais para matching flexível.

        'cloudsql-postgres-ad' → {'cloudsql-postgres-ad', 'cloudsql', 'postgres', 'ad'}
        'nanoplanner'          → {'nanoplanner'}  (sem separador, mantém original)

        Isso permite que required_tag='postgres' encontre a tag 'cloudsql-postgres-ad'.
        """
        if not tags:
            return []
        expanded: List[str] = []
        seen: set = set()
        for tag in tags:
            tag_str = str(tag)
            if tag_str not in seen:
                seen.add(tag_str)
                expanded.append(tag_str)
            # Quebra por hífen, underscore ou espaço
            for sep in ('-', '_', ' '):
                if sep in tag_str:
                    for part in tag_str.split(sep):
                        part = part.strip()
                        if part and part not in seen:
                            seen.add(part)
                            expanded.append(part)
        return expanded

    def register_skill(self, agent_id: str, skill_id: str, name: str,
                       description: str, tags: Optional[List[str]] = None,
                       initial_confidence: float = 0.5,
                       episteme: Optional[str] = None,
                       category: str = "",
                       agent_type: str = "") -> SkillProfile:
        """Registra uma skill no handbook.

        Args:
            agent_id: ID do agente
            skill_id: ID da skill (ex.: 'hypnotic-prose-analysis')
            name: Nome legível da skill
            description: Descrição detalhada
            tags: Lista de tags para matching semântico
            initial_confidence: Confiança inicial (0-1)
            episteme: Regime epistemológico explícito (override manual;
                vence a inferência heurística — SPEC-935-R363)
            category: Categoria do agente (insumo da inferência epistêmica)
            agent_type: Tipo do agente (insumo da inferência epistêmica)

        Returns:
            SkillProfile criado
        """
        key = (agent_id, skill_id)
        if key in self._profiles:
            return self._profiles[key]

        # Expande tags: 'cloudsql-postgres-ad' → subtokens para matching flexível
        expanded_tags = self._expand_tags(tags)

        # Enriquece tags com tokens do agent_id:
        # 'Cloud SQL PostgreSQL Specialist' → tags 'cloud', 'sql', 'postgresql', 'specialist'
        agent_id_tokens = self._expand_tags([agent_id])
        all_tags = list(dict.fromkeys(expanded_tags + agent_id_tokens))

        # Gera embedding da descrição + tags expandidas para matching semântico
        text = f"{name}. {description}. Agent: {agent_id}. Tags: {', '.join(all_tags)}"
        vector = self.engine.embed(text)

        # Episteme: override explícito vence; senão inferência heurística
        # determinística; qualquer falha resulta em None (fail-open)
        skill_episteme: Optional[str] = None
        if episteme:
            skill_episteme = str(episteme).strip().lower()
        elif _HAS_EPISTEME:
            try:
                inferred = infer_agent_episteme(
                    category=category,
                    agent_type=agent_type,
                    tags=all_tags,
                    name=f"{agent_id} {name}",
                    description=description,
                )
                skill_episteme = inferred.episteme if inferred else None
            except Exception:
                skill_episteme = None

        profile = SkillProfile(
            agent_id=agent_id,
            skill_id=skill_id,
            name=name,
            description=description,
            tags=all_tags,
            confidence=initial_confidence,
            vector=vector,
            episteme=skill_episteme,
        )
        self._profiles[key] = profile
        self._agent_skills.setdefault(agent_id, []).append(skill_id)
        return profile

    def record_execution(self, agent_id: str, skill_id: str,
                         success: bool, cost: float = 0.0) -> None:
        """Atualiza o perfil após uma execução.

        Args:
            agent_id: ID do agente
            skill_id: ID da skill executada
            success: True se bem-sucedido
            cost: Custo da execução (em tokens ou unidades arbitrárias)
        """
        key = (agent_id, skill_id)
        profile = self._profiles.get(key)
        if not profile:
            return

        profile.executions += 1
        if success:
            profile.successes += 1

        # Atualiza confiança: weighted moving average
        recent_rate = profile.successes / max(1, profile.executions)
        profile.confidence = 0.7 * recent_rate + 0.3 * profile.confidence

        # Atualiza custo médio (EMA)
        if cost > 0:
            profile.avg_cost = 0.9 * profile.avg_cost + 0.1 * cost

    def match(self, task_description: str, required_tags: Optional[List[str]] = None,
              min_confidence: float = 0.3, top_k: int = 5) -> List[Dict[str, Any]]:
        """Encontra os melhores (agente, skill) para uma tarefa.

        Usa similaridade cosseno entre o embedding da tarefa e os
        embeddings das skills, filtrado por confiança mínima.

        Args:
            task_description: Descrição da tarefa
            required_tags: Tags requeridas (filtro adicional)
            min_confidence: Confiança mínima por skill
            top_k: Número de resultados

        Returns:
            Lista de dicts com agent_id, skill_id, confidence, similarity
        """
        if not self._profiles:
            return []

        # Embed da tarefa
        task_vec = self.engine.embed(task_description)
        if required_tags:
            required_set = set(t.lower() for t in required_tags)

        # Episteme da tarefa (uma única inferência por chamada; fail-open)
        task_episteme: Optional[str] = None
        if _HAS_EPISTEME:
            try:
                task_profile = infer_task_episteme(task_description)
                task_episteme = task_profile.episteme if task_profile else None
            except Exception:
                task_episteme = None

        scored: List[Dict[str, Any]] = []
        for (agent_id, skill_id), profile in self._profiles.items():
            # Filtro de confiança
            if profile.confidence < min_confidence:
                continue

            # Filtro de tags
            if required_tags:
                profile_tags = set(t.lower() for t in profile.tags)
                if not required_set.intersection(profile_tags):
                    continue

            # Similaridade semântica
            if profile.vector and task_vec:
                similarity = _cosine_similarity(task_vec, profile.vector)
            else:
                similarity = 0.0

            # Score composto: 60% similaridade semântica + 40% confiança
            score = 0.6 * similarity + 0.4 * profile.confidence

            # Peso brando epistêmico (±10% máx.) — só quando tarefa E skill
            # têm episteme identificada; caso contrário score inalterado
            affinity: Optional[float] = None
            if task_episteme and profile.episteme and _HAS_EPISTEME:
                affinity = episteme_affinity(task_episteme, profile.episteme)
                score = score * (1 + EPISTEME_WEIGHT * (affinity - 0.5))

            scored.append({
                "agent_id": agent_id,
                "skill_id": skill_id,
                "skill_name": profile.name,
                "confidence": profile.confidence,
                "similarity": round(similarity, 4),
                "score": round(score, 4),
                "executions": profile.executions,
                "episteme": profile.episteme,
                "episteme_affinity": (
                    round(affinity, 4) if affinity is not None else None
                ),
            })

        # Ordena por score
        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k]

    def get_agent_profile(self, agent_id: str) -> Dict[str, Any]:
        """Retorna o perfil completo de um agente no handbook."""
        skill_ids = self._agent_skills.get(agent_id, [])
        skills = []
        for sid in skill_ids:
            profile = self._profiles.get((agent_id, sid))
            if profile:
                skills.append({
                    "skill_id": profile.skill_id,
                    "name": profile.name,
                    "confidence": profile.confidence,
                    "executions": profile.executions,
                    "avg_cost": profile.avg_cost,
                })
        return {
            "agent_id": agent_id,
            "skills": skills,
            "avg_confidence": (sum(s["confidence"] for s in skills) / len(skills)
                               if skills else 0.0),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas do handbook."""
        total_profiles = len(self._profiles)
        if total_profiles == 0:
            return {"total_skills": 0, "total_agents": 0, "avg_confidence": 0.0}
        avg_conf = sum(p.confidence for p in self._profiles.values()) / total_profiles
        return {
            "total_skills": total_profiles,
            "total_agents": len(self._agent_skills),
            "avg_confidence": round(avg_conf, 4),
            "engine_provider": self.engine.provider,
            "engine_calls": self.engine._stats["calls"],
            "engine_cache_hits": self.engine._stats["cache_hits"],
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialização para persistência."""
        return {
            "profiles": {
                f"{aid}::{sid}": {
                    "agent_id": profile.agent_id,
                    "skill_id": profile.skill_id,
                    "name": profile.name,
                    "description": profile.description,
                    "tags": profile.tags,
                    "confidence": profile.confidence,
                    "executions": profile.executions,
                    "successes": profile.successes,
                    "avg_cost": profile.avg_cost,
                }
                for (aid, sid), profile in self._profiles.items()
            },
            "agent_skills": dict(self._agent_skills),
        }


# ═══════════════════════════════════════════════════════════════════════════
# 4. SEMANTIC MATCHER (Orquestrador)
# ═══════════════════════════════════════════════════════════════════════════

class SemanticMatcher:
    """Orquestrador de matching semântico.

    Integra EmbeddingEngine + SkillHandbook para substituir
    o string-matching do catalog_loader.
    """

    def __init__(self):
        self.engine = EmbeddingEngine()
        self.handbook = SkillHandbook(engine=self.engine)

    def register_agent_skills(self, agent_id: str, skills: List[Dict[str, Any]],
                              initial_confidence: float = 0.5,
                              episteme: Optional[str] = None,
                              category: str = "",
                              agent_type: str = "") -> int:
        """Registra as skills de um agente no handbook.

        Args:
            agent_id: ID do agente
            skills: Lista de dicts com id, name, description, tags
            initial_confidence: Confiança inicial
            episteme: Episteme explícita do agente (frontmatter, opcional);
                skills individuais podem sobrescrever via chave 'episteme'
            category: Categoria do agente (insumo da inferência epistêmica)
            agent_type: Tipo do agente (insumo da inferência epistêmica)

        Returns:
            Número de skills registradas
        """
        count = 0
        for skill in skills:
            skill_id = skill.get("id", skill.get("skill_id", "unknown"))
            self.handbook.register_skill(
                agent_id=agent_id,
                skill_id=skill_id,
                name=skill.get("name", skill_id),
                description=skill.get("description", ""),
                tags=skill.get("tags", []),
                initial_confidence=initial_confidence,
                episteme=skill.get("episteme") or episteme,
                category=category,
                agent_type=agent_type,
            )
            count += 1
        return count

    def match_capabilities(self, task_description: str,
                           required_capabilities: Optional[List[str]] = None,
                           top_k: int = 5) -> List[Dict[str, Any]]:
        """Matching semântico: descrição da tarefa vs skills dos agentes.

        Esta é a função principal usada pelo AttentionRouter.
        Substitui o matching por substring do catalog_loader.

        Args:
            task_description: Descrição da tarefa
            required_capabilities: Lista de capacidades requeridas (tags)
            top_k: Número de resultados

        Returns:
            Lista de (agent_id, skill_id, score) ordenada por score
        """
        return self.handbook.match(
            task_description=task_description,
            required_tags=required_capabilities,
            top_k=top_k,
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "engine": self.engine.get_stats(),
            "handbook": self.handbook.get_stats(),
        }


# Singleton
semantic_matcher = SemanticMatcher()
