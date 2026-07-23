# -*- coding: utf-8 -*-
"""
Model Router — Roteamento Inteligente de Modelos
================================================
Roteia tarefas para o modelo mais adequado entre OpenCode Go,
OpenCode Zen, e outros providers do ecossistema, com base em:

  - Tipo de tarefa (coding, reasoning, academic, writing, fast, math)
  - Provider preferido (opencode-go, opencode-zen, anthropic, google, openai)
  - Tier de qualidade (frontier, premium, standard, fast)
  - Disponibilidade de chave de API
  - Histórico de performance via MetaBus

Integração completa com SDD/TDD:
  - Toda decisão de roteamento cria um evento no MetaBus
  - ModelProfiles mapeiam task_type → modelo ideal
  - TrustEngine pode bloquear modelos com score baixo

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("model-router")

# ── Imports opcionais de providers ────────────────────────────────────────────

def _get_opencode_go():
    try:
        from integrations.opencode_go import opencode_go, MODELS as GO_MODELS
        return opencode_go, GO_MODELS
    except ImportError:
        return None, {}


def _get_opencode_zen():
    try:
        from integrations.opencode_zen import opencode_zen, MODELS as ZEN_MODELS
        return opencode_zen, ZEN_MODELS
    except ImportError:
        return None, {}


def _get_litert_lm():
    try:
        from integrations.litert_lm import litert_lm, MODELS as LT_MODELS
        return litert_lm, LT_MODELS
    except ImportError:
        return None, {}


def _get_openai():
    try:
        from integrations.openai_provider import openai_provider, MODELS as OA_MODELS
        return openai_provider, OA_MODELS
    except ImportError:
        return None, {}


# ── Perfis de modelo por tipo de tarefa ──────────────────────────────────────

@dataclass
class ModelProfile:
    """Perfil de roteamento para um tipo de tarefa."""
    task_type: str
    description: str
    # Lista ordenada de (provider_id, model_id) em ordem de preferência
    preferred: List[Tuple[str, str]] = field(default_factory=list)
    # Modelo fallback se todos os preferidos falharem (free-only)
    fallback: Tuple[str, str] = ("litert-lm", "gemma-4-E2B-it")


# Perfis padrão do ecossistema
DEFAULT_PROFILES: Dict[str, ModelProfile] = {
    # ── CODING ───────────────────────────────────────────────────────────────
    # Token-optimized: gemma-4-E2B-it (2.5GB, standard) é o melhor custo-benefício
    # para código. Fallbacks: qwen-3-4B-it (2.5GB), gemma-4-E4B-it (4.8GB com thinking).
    "coding": ModelProfile(
        task_type="coding",
        description="Geração, revisão e depuração de código [FREE only]",
        preferred=[
            ("litert-lm", "gemma-4-E2B-it"),        # 2.5GB, standard, eficiente
            ("litert-lm", "gemma-3-4B-it"),          # 2.5GB, coding+fast
            ("litert-lm", "qwen-3-4B-it"),           # 2.5GB, standard
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium c/ thinking
            ("litert-lm", "gemma-4-9B-it"),          # 9GB, premium c/ thinking
            ("litert-lm", "llama-3-8B-it"),          # 4.5GB, standard
            ("litert-lm", "gemma-2-9B-it"),          # 5.5GB, standard
            ("opencode-zen", "deepseek-v3"),          # FREE Zen, API-based
        ],
        fallback=("litert-lm", "gemma-4-E2B-it"),
    ),
    # ── REASONING ────────────────────────────────────────────────────────────
    # phi-4 (9GB, premium, thinking) tem a melhor relação qualidade/tokens
    # para raciocínio. Alternativas maiores só se precisar de mais potência.
    "reasoning": ModelProfile(
        task_type="reasoning",
        description="Raciocínio complexo, chain-of-thought [FREE only]",
        preferred=[
            ("litert-lm", "phi-4-14B-it"),           # 9GB, premium, thinking, math+reasoning
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium c/ thinking
            ("litert-lm", "gemma-3-27B-it"),         # 16GB, frontier c/ thinking
            ("litert-lm", "gemma-4-12B-it"),         # 12GB, frontier c/ thinking
            ("litert-lm", "qwen-3-30B-it"),          # 18GB, frontier
            ("opencode-zen", "deepseek-r2"),          # FREE Zen, reasoning premium
        ],
        fallback=("litert-lm", "phi-4-14B-it"),
    ),
    # ── ACADEMIC ─────────────────────────────────────────────────────────────
    # Escrita acadêmica exige contexto longo e precisão. gemma-4-12B-it
    # (frontier, thinking) é o ponto ótimo. deepseek-r2 como fallback cloud.
    "academic": ModelProfile(
        task_type="academic",
        description="Escrita acadêmica, revisão por pares, MASWOS [FREE only]",
        preferred=[
            ("litert-lm", "gemma-4-12B-it"),         # 12GB, frontier, thinking
            ("litert-lm", "qwen-3-30B-it"),          # 18GB, frontier
            ("litert-lm", "gemma-3-27B-it"),         # 16GB, frontier, thinking
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium, thinking
            ("litert-lm", "phi-4-14B-it"),           # 9GB, premium, thinking
            ("opencode-zen", "deepseek-r2"),          # FREE Zen
        ],
        fallback=("litert-lm", "gemma-4-12B-it"),
    ),
    # ── WRITING ──────────────────────────────────────────────────────────────
    # Escrita criativa: modelos pequenos e rápidos são suficientes.
    # Gemma 4 E2B (2.5GB) como padrão token-efficient.
    "writing": ModelProfile(
        task_type="writing",
        description="Escrita criativa, edição e revisão textual [FREE only]",
        preferred=[
            ("litert-lm", "gemma-4-E2B-it"),        # 2.5GB, standard
            ("litert-lm", "qwen-3-4B-it"),           # 2.5GB, standard
            ("litert-lm", "gemma-3-4B-it"),          # 2.5GB, standard
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium (se precisar)
            ("opencode-zen", "deepseek-v3"),          # FREE Zen
        ],
        fallback=("litert-lm", "gemma-4-E2B-it"),
    ),
    # ── FAST ─────────────────────────────────────────────────────────────────
    # Ultra-eficiente: gemma-3-1B-it (0.5GB, 8K ctx) para respostas instantâneas.
    # gemma-2-2B-it (1.5GB) como alternativa. deepseek-v3 via cloud.
    "fast": ModelProfile(
        task_type="fast",
        description="Respostas rápidas, tarefas simples, alta frequência [FREE only]",
        preferred=[
            ("litert-lm", "gemma-3-1B-it"),          # 0.5GB, ultra-rápido
            ("litert-lm", "gemma-2-2B-it"),          # 1.5GB, rápido
            ("litert-lm", "gemma-3-4B-it"),          # 2.5GB, standard
            ("litert-lm", "qwen-3-4B-it"),           # 2.5GB, standard
            ("litert-lm", "gemma-4-E2B-it"),         # 2.5GB (fallback local)
            ("opencode-zen", "deepseek-v3"),          # FREE Zen, API-based
        ],
        fallback=("litert-lm", "gemma-3-1B-it"),
    ),
    # ── LOCAL ────────────────────────────────────────────────────────────────
    # Inferência 100% on-device. Prioridade: modelos que cabem em qualquer hardware.
    "local": ModelProfile(
        task_type="local",
        description="Inferência on-device via LiteRT-LM [FREE only, sem rede]",
        preferred=[
            ("litert-lm", "gemma-4-E2B-it"),         # 2.5GB, standard, universal
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium, multimodal
            ("litert-lm", "gemma-4-12B-it"),         # 12GB, frontier
            ("litert-lm", "gemma-3-1B-it"),          # 0.5GB, ultra-leve
        ],
        fallback=("litert-lm", "gemma-4-E2B-it"),
    ),
    # ── MATH ─────────────────────────────────────────────────────────────────
    # phi-4 (14B) é especializado em math+reasoning, melhor escolha gratuita.
    # deepseek-r2 (FREE Zen) como alternativa cloud de alto nível.
    "math": ModelProfile(
        task_type="math",
        description="Computação matemática, estatística, modelagem formal [FREE only]",
        preferred=[
            ("litert-lm", "phi-4-14B-it"),           # 9GB, premium, thinking, math
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium, thinking
            ("litert-lm", "qwen-3-30B-it"),          # 18GB, frontier
            ("opencode-zen", "deepseek-r2"),          # FREE Zen, math+reasoning
            ("litert-lm", "gemma-3-27B-it"),         # 16GB, frontier, thinking
        ],
        fallback=("litert-lm", "phi-4-14B-it"),
    ),
    # ── MULTIMODAL ───────────────────────────────────────────────────────────
    # gemma-4-E4B-it (4.8GB, multimodal c/ thinking) é o mais eficiente.
    # Alternativas maiores para visão mais complexa.
    "multimodal": ModelProfile(
        task_type="multimodal",
        description="Análise de imagens, gráficos e conteúdo visual [FREE only]",
        preferred=[
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium, multimodal, thinking
            ("litert-lm", "gemma-4-9B-it"),          # 9GB, premium, multimodal, thinking
            ("litert-lm", "llama-4-17B-it"),         # 10GB, premium, multimodal, thinking
            ("litert-lm", "gemma-4-12B-it"),         # 12GB, frontier, multimodal, thinking
        ],
        fallback=("litert-lm", "gemma-4-E4B-it"),
    ),
    # ── LEGAL ────────────────────────────────────────────────────────────────
    # Raciocínio jurídico exige contexto + precisão. deepseek-r2 é forte aqui.
    "legal": ModelProfile(
        task_type="legal",
        description="Raciocínio jurídico, subsunção, SPEC-921/928 [FREE only]",
        preferred=[
            ("litert-lm", "gemma-4-12B-it"),         # 12GB, frontier, thinking
            ("litert-lm", "phi-4-14B-it"),           # 9GB, premium, thinking
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium, thinking
            ("litert-lm", "qwen-3-30B-it"),          # 18GB, frontier
            ("opencode-zen", "deepseek-r2"),          # FREE Zen
        ],
        fallback=("litert-lm", "gemma-4-12B-it"),
    ),
    # ── AGENTIC ──────────────────────────────────────────────────────────────
    # Orquestração multi-agente: planejamento longo, contexto grande.
    # deepseek-r2 como alternativa cloud gratuita de frontieir.
    "agentic": ModelProfile(
        task_type="agentic",
        description="Orquestração multi-agente, planejamento longo [FREE only]",
        preferred=[
            ("litert-lm", "qwen-3-30B-it"),          # 18GB, frontier
            ("litert-lm", "gemma-4-12B-it"),         # 12GB, frontier, thinking
            ("litert-lm", "gemma-3-27B-it"),         # 16GB, frontier, thinking
            ("litert-lm", "phi-4-14B-it"),           # 9GB, premium, thinking
            ("litert-lm", "gemma-4-E4B-it"),         # 4.8GB, premium, thinking
            ("opencode-zen", "deepseek-r2"),          # FREE Zen
        ],
        fallback=("litert-lm", "qwen-3-30B-it"),
    ),
}


# ── Resultado de roteamento ───────────────────────────────────────────────────

@dataclass
class RouteResult:
    """Resultado de uma decisão de roteamento."""
    task_type: str
    provider_id: str
    model_id: str
    profile: ModelProfile
    reason: str
    alternatives: List[Tuple[str, str]] = field(default_factory=list)
    authenticated: bool = False
    mock_mode: bool = False


# ── Router ────────────────────────────────────────────────────────────────────

class ModelRouter:
    """
    Roteador central de modelos do OpenCode Ecosystem.

    Seleciona o modelo mais adequado para cada tipo de tarefa,
    considerando disponibilidade de API keys e perfis configurados.

    Integração com o ecossistema:
      - Publica eventos de roteamento no MetaBus
      - Pode ser chamado pelo orquestrador marceloclaro
      - Suporte a override de perfil por agente
    """

    def __init__(
        self,
        profiles: Optional[Dict[str, ModelProfile]] = None,
        prefer_authenticated: bool = True,
    ):
        self.profiles = profiles or DEFAULT_PROFILES.copy()
        self.prefer_authenticated = prefer_authenticated
        self._go_provider, self._go_models = _get_opencode_go()
        self._zen_provider, self._zen_models = _get_opencode_zen()
        self._lt_provider, self._lt_models = _get_litert_lm()
        self._oa_provider, self._oa_models = _get_openai()
        logger.info(
            "ModelRouter inicializado — %d perfis, Go=%s, Zen=%s, LiteRT=%s, OpenAI=%s",
            len(self.profiles),
            "OK" if self._go_provider else "indisponível",
            "OK" if self._zen_provider else "indisponível",
            "OK" if self._lt_provider else "indisponível",
            "OK" if self._oa_provider else "indisponível",
        )

    def route(
        self,
        task_type: str,
        force_provider: Optional[str] = None,
        force_model: Optional[str] = None,
        require_thinking: bool = False,
        prefer_free: bool = False,
    ) -> RouteResult:
        """
        Seleciona o melhor provider + modelo para a tarefa.

        Args:
            task_type: Tipo da tarefa (ver DEFAULT_PROFILES)
            force_provider: Se fornecido, força o provider (ignora preferências)
            force_model: Se fornecido, força o modelo (ignora perfil)
            require_thinking: Se True, filtra apenas modelos com thinking habilitado
            prefer_free: Se True, prefere modelos gratuitos no Zen

        Returns:
            RouteResult com provider_id, model_id e metadados de decisão
        """
        profile = self.profiles.get(task_type)
        if profile is None:
            # Task type desconhecido → usa perfil "coding" como default
            logger.warning(
                "Task type '%s' sem perfil configurado — usando 'coding' como fallback",
                task_type,
            )
            profile = self.profiles.get("coding", ModelProfile(
                task_type="coding",
                description="Fallback",
                preferred=[("litert-lm", "gemma-4-E2B-it")],
            ))

        # Override forçado
        if force_provider and force_model:
            return RouteResult(
                task_type=task_type,
                provider_id=force_provider,
                model_id=force_model,
                profile=profile,
                reason=f"Override forçado: {force_provider}/{force_model}",
                alternatives=[],
                authenticated=self._is_authenticated(force_provider),
                mock_mode=not self._is_authenticated(force_provider),
            )

        # Seleciona da lista de preferidos
        candidates = self._filter_candidates(
            profile.preferred,
            force_provider=force_provider,
            require_thinking=require_thinking,
            prefer_free=prefer_free,
        )

        if candidates:
            provider_id, model_id = candidates[0]
            alternatives = candidates[1:]
        else:
            # Fallback
            provider_id, model_id = profile.fallback
            alternatives = []

        authenticated = self._is_authenticated(provider_id)
        result = RouteResult(
            task_type=task_type,
            provider_id=provider_id,
            model_id=model_id,
            profile=profile,
            reason=self._build_reason(
                task_type, provider_id, model_id, require_thinking, authenticated
            ),
            alternatives=alternatives[:3],
            authenticated=authenticated,
            mock_mode=not authenticated,
        )

        self._publish_route_event(result)
        return result

    def route_and_complete(
        self,
        prompt: str,
        task_type: str = "coding",
        system: str = "",
        thinking: bool = False,
        spec_id: Optional[str] = None,
        **route_kwargs,
    ) -> Any:
        """
        Roteia e executa a completion em uma única chamada.

        Returns:
            CompletionResponse do provider selecionado.
        """
        route = self.route(task_type, require_thinking=thinking, **route_kwargs)
        provider = self._get_provider(route.provider_id)

        if provider is None:
            raise RuntimeError(
                f"Provider '{route.provider_id}' indisponível. "
                "Verifique as importações em integrations/."
            )

        return provider.complete(
            prompt=prompt,
            model=route.model_id,
            system=system,
            thinking=thinking,
            spec_id=spec_id,
        )

    def list_all_models(self) -> List[Dict[str, Any]]:
        """Lista todos os modelos de todos os providers."""
        models = []
        if self._go_provider:
            models.extend(self._go_provider.list_models())
        if self._zen_provider:
            models.extend(self._zen_provider.list_models())
        if self._lt_provider:
            models.extend(self._lt_provider.list_models(local_only=True))
        if self._oa_provider:
            models.extend(self._oa_provider.list_models())
        return models

    def list_profiles(self) -> List[Dict[str, Any]]:
        """Lista os perfis de roteamento configurados."""
        return [
            {
                "task_type": p.task_type,
                "description": p.description,
                "preferred_count": len(p.preferred),
                "top_model": f"{p.preferred[0][0]}/{p.preferred[0][1]}" if p.preferred else None,
            }
            for p in self.profiles.values()
        ]

    def status(self) -> Dict[str, Any]:
        """Retorna o status completo do router."""
        return {
            "profiles": len(self.profiles),
            "providers": {
                "opencode-go": {
                    "available": self._go_provider is not None,
                    "authenticated": self._is_authenticated("opencode-go"),
                    "models": len(self._go_models),
                },
                "opencode-zen": {
                    "available": self._zen_provider is not None,
                    "authenticated": self._is_authenticated("opencode-zen"),
                    "models": len(self._zen_models),
                },
                "litert-lm": {
                    "available": self._lt_provider is not None,
                    "authenticated": self._is_authenticated("litert-lm"),
                    "models": len(self._lt_models),
                },
                "openai": {
                    "available": self._oa_provider is not None,
                    "authenticated": self._is_authenticated("openai"),
                    "models": len(self._oa_models),
                },
            },
            "total_models": len(self._go_models) + len(self._zen_models) + len(self._lt_models) + len(self._oa_models),
        }

    # ── Privados ─────────────────────────────────────────────────────────────

    def _filter_candidates(
        self,
        preferred: List[Tuple[str, str]],
        force_provider: Optional[str],
        require_thinking: bool,
        prefer_free: bool,
    ) -> List[Tuple[str, str]]:
        """Filtra e ordena candidatos com base nas restrições."""
        result = []
        for provider_id, model_id in preferred:
            if force_provider and provider_id != force_provider:
                continue
            model_meta = self._get_model_meta(provider_id, model_id)
            if require_thinking and not model_meta.get("thinking", False):
                continue
            authenticated = self._is_authenticated(provider_id)
            # Ordena: autenticados primeiro (se prefer_authenticated), depois gratuitos
            priority = (
                int(self.prefer_authenticated and authenticated),
                int(prefer_free and model_meta.get("free", False)),
            )
            result.append((priority, provider_id, model_id))
        result.sort(key=lambda x: x[0], reverse=True)
        return [(pid, mid) for _, pid, mid in result]

    def _get_model_meta(self, provider_id: str, model_id: str) -> Dict[str, Any]:
        """Busca metadados do modelo no provider correto."""
        if provider_id == "opencode-go":
            return self._go_models.get(model_id, {})
        if provider_id == "opencode-zen":
            return self._zen_models.get(model_id, {})
        if provider_id == "openai":
            return self._oa_models.get(model_id, {})
        return {}

    def _is_authenticated(self, provider_id: str) -> bool:
        """Verifica se o provider tem chave de API disponível."""
        if provider_id == "opencode-go" and self._go_provider:
            return bool(self._go_provider._api_key)
        if provider_id == "opencode-zen" and self._zen_provider:
            return bool(self._zen_provider._api_key)
        if provider_id == "litert-lm" and self._lt_provider:
            return True  # servidor local, sempre autenticado
        if provider_id == "openai" and self._oa_provider:
            return bool(self._oa_provider._api_key)
        return False

    def _get_provider(self, provider_id: str):
        """Retorna a instância do provider."""
        if provider_id == "opencode-go":
            return self._go_provider
        if provider_id == "opencode-zen":
            return self._zen_provider
        if provider_id == "litert-lm":
            return self._lt_provider
        if provider_id == "openai":
            return self._oa_provider
        return None

    def _build_reason(
        self,
        task_type: str,
        provider_id: str,
        model_id: str,
        require_thinking: bool,
        authenticated: bool,
    ) -> str:
        parts = [
            f"task_type='{task_type}'",
            f"modelo selecionado: {provider_id}/{model_id}",
        ]
        if require_thinking:
            parts.append("thinking habilitado")
        if not authenticated:
            parts.append("modo mock (sem chave de API)")
        return " | ".join(parts)

    def _publish_route_event(self, result: RouteResult) -> None:
        """Publica evento de roteamento no MetaBus."""
        try:
            from mci.metabus import metabus
            metabus.publish_subsystem_event(
                "model-router",
                "route.selected",
                {
                    "task_type": result.task_type,
                    "provider": result.provider_id,
                    "model": result.model_id,
                    "authenticated": result.authenticated,
                    "mock_mode": result.mock_mode,
                    "reason": result.reason,
                },
                source_agent="model_router",
            )
        except Exception:
            pass


# ── Singleton global ──────────────────────────────────────────────────────────

model_router = ModelRouter()
