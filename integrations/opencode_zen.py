# -*- coding: utf-8 -*-
"""
OpenCode Zen Provider — Integração com o provider opencode-zen
==============================================================
Expõe os modelos curados e testados pelo gateway OpenCode Zen:
  - GPT (OpenAI): gpt-5.5, gpt-5, gpt-4.5
  - Claude (Anthropic): claude-opus-4, claude-sonnet-4.6, claude-haiku-4
  - Gemini (Google): gemini-2.5-pro, gemini-2.5-flash
  - DeepSeek (via Zen): deepseek-r2, deepseek-v3
  - MiniMax (via Zen): minimax-m3-ultra
  - Outros curados: grok-4, mistral-large-3

Pay-as-you-go com rotação de modelos gratuitos.
Integração completa com protocolo SDD/TDD do ecossistema.

Uso:
    from integrations.opencode_zen import OpenCodeZenProvider
    provider = OpenCodeZenProvider()
    result = provider.complete("Revise este artigo científico", model="claude-opus-4")

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger("opencode-zen-provider")

# ── Constantes ──────────────────────────────────────────────────────────────

PROVIDER_ID = "opencode-zen"
BASE_URL = "https://opencode.ai/zen/v1"
ENV_KEY = "OPENCODE_ZEN_API_KEY"
ENV_KEY_FALLBACK = "OPENCODE_API_KEY"
AUTH_FILE_PATHS = [
    os.path.expanduser("~/.local/share/opencode/auth.json"),
    os.path.expanduser("~/.config/opencode/auth.json"),
]

# Catálogo de modelos curados (pay-as-you-go)
MODELS: Dict[str, Dict[str, Any]] = {
    # GPT / OpenAI
    "gpt-5.5": {
        "name": "GPT-5.5",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["reasoning", "coding", "academic", "multimodal"],
        "context_window": 256_000,
        "thinking": True,
        "tier": "frontier",
        "free": False,
    },
    "gpt-5": {
        "name": "GPT-5",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["reasoning", "coding", "academic"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
        "free": False,
    },
    "gpt-4.5": {
        "name": "GPT-4.5",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["coding", "academic"],
        "context_window": 128_000,
        "thinking": False,
        "tier": "standard",
        "free": False,
    },
    # Claude / Anthropic
    "claude-opus-4": {
        "name": "Claude Opus 4",
        "provider": PROVIDER_ID,
        "family": "anthropic",
        "strengths": ["reasoning", "academic", "writing", "coding"],
        "context_window": 200_000,
        "thinking": True,
        "tier": "frontier",
        "free": False,
    },
    "claude-sonnet-4.6": {
        "name": "Claude Sonnet 4.6",
        "provider": PROVIDER_ID,
        "family": "anthropic",
        "strengths": ["coding", "reasoning", "academic"],
        "context_window": 200_000,
        "thinking": True,
        "tier": "premium",
        "free": False,
    },
    "claude-haiku-4": {
        "name": "Claude Haiku 4",
        "provider": PROVIDER_ID,
        "family": "anthropic",
        "strengths": ["coding", "fast"],
        "context_window": 200_000,
        "thinking": False,
        "tier": "fast",
        "free": False,
    },
    # Gemini / Google
    "gemini-2.5-pro": {
        "name": "Gemini 2.5 Pro",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["reasoning", "coding", "academic", "multimodal"],
        "context_window": 2_000_000,
        "thinking": True,
        "tier": "frontier",
        "free": False,
    },
    "gemini-2.5-flash": {
        "name": "Gemini 2.5 Flash",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "fast", "multimodal"],
        "context_window": 1_000_000,
        "thinking": True,
        "tier": "fast",
        "free": False,
    },
    # DeepSeek via Zen
    "deepseek-r2": {
        "name": "DeepSeek R2",
        "provider": PROVIDER_ID,
        "family": "deepseek",
        "strengths": ["reasoning", "math", "coding"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
        "free": True,
    },
    "deepseek-v3": {
        "name": "DeepSeek V3",
        "provider": PROVIDER_ID,
        "family": "deepseek",
        "strengths": ["coding", "reasoning"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "standard",
        "free": True,
    },
    # MiniMax via Zen
    "minimax-m3-ultra": {
        "name": "MiniMax M3 Ultra",
        "provider": PROVIDER_ID,
        "family": "minimax",
        "strengths": ["coding", "multimodal", "agentic"],
        "context_window": 256_000,
        "thinking": True,
        "tier": "premium",
        "free": False,
    },
    # Grok / xAI
    "grok-4": {
        "name": "Grok 4",
        "provider": PROVIDER_ID,
        "family": "xai",
        "strengths": ["reasoning", "coding", "real-time"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "frontier",
        "free": False,
    },
    # Mistral
    "mistral-large-3": {
        "name": "Mistral Large 3",
        "provider": PROVIDER_ID,
        "family": "mistral",
        "strengths": ["coding", "reasoning", "european"],
        "context_window": 128_000,
        "thinking": False,
        "tier": "premium",
        "free": False,
    },
}

DEFAULT_MODEL = "claude-sonnet-4.6"


# ── Exceções ─────────────────────────────────────────────────────────────────

class OpenCodeZenError(Exception):
    """Erro base do provider OpenCode Zen."""


class ProviderAuthError(OpenCodeZenError):
    """Chave de API ausente ou inválida."""


class ModelNotFoundError(OpenCodeZenError):
    """Modelo solicitado não existe no catálogo Zen."""


class SpecVerificationError(OpenCodeZenError):
    """A resposta do modelo não passou na verificação SDD."""


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CompletionRequest:
    prompt: str
    model: str = DEFAULT_MODEL
    system: str = ""
    thinking: bool = False
    thinking_effort: str = "medium"
    temperature: float = 0.0
    max_tokens: int = 8192
    spec_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    model: str
    provider: str
    content: str
    thinking: str = ""
    spec_id: Optional[str] = None
    spec_verified: bool = False
    usage: Dict[str, int] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)


# ── Provider ──────────────────────────────────────────────────────────────────

class OpenCodeZenProvider:
    """
    Provider para OpenCode Zen — gateway curado pay-as-you-go.

    Suporta GPT, Claude, Gemini, DeepSeek, MiniMax, Grok e Mistral
    via um único endpoint e chave de API.

    Integra com SDD/TDD: toda requisição pode vincular uma
    Specification no SpecRegistry e verificar a resposta.

    Autenticação: lê OPENCODE_ZEN_API_KEY (ou OPENCODE_API_KEY) do
    ambiente ou de ~/.local/share/opencode/auth.json.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or self._load_api_key()
        self._sdd_enabled = True
        logger.info(
            "OpenCodeZenProvider inicializado — %d modelos curados, base_url=%s",
            len(MODELS), self.base_url,
        )

    # ── API Key ──────────────────────────────────────────────────────────────

    def _load_api_key(self) -> str:
        """Carrega chave de OPENCODE_ZEN_API_KEY, OPENCODE_API_KEY ou auth.json."""
        key = os.environ.get(ENV_KEY, "") or os.environ.get(ENV_KEY_FALLBACK, "")
        if key:
            return key
        for path in AUTH_FILE_PATHS:
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    key = (
                        data.get("opencode-zen", {}).get("apiKey", "")
                        or data.get("opencode", {}).get("apiKey", "")
                        or data.get("apiKey", "")
                    )
                    if key:
                        return key
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Falha ao ler %s: %s", path, exc)
        logger.warning(
            "Chave OpenCode Zen não encontrada. Configure OPENCODE_ZEN_API_KEY ou use /connect."
        )
        return ""

    # ── Modelos ───────────────────────────────────────────────────────────────

    def list_models(self, free_only: bool = False) -> List[Dict[str, Any]]:
        """Retorna catálogo de modelos. Se free_only=True, filtra por gratuitos."""
        models = [{"model_id": mid, **meta} for mid, meta in MODELS.items()]
        if free_only:
            models = [m for m in models if m.get("free", False)]
        return models

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        if model_id not in MODELS:
            raise ModelNotFoundError(
                f"Modelo '{model_id}' não encontrado no catálogo OpenCode Zen. "
                f"Modelos disponíveis: {list(MODELS.keys())}"
            )
        return {"model_id": model_id, **MODELS[model_id]}

    def best_model_for(
        self,
        task_type: str,
        family: Optional[str] = None,
        tier: str = "any",
        prefer_free: bool = False,
    ) -> str:
        """
        Seleciona o melhor modelo Zen para a tarefa.

        Args:
            task_type: "coding" | "reasoning" | "academic" | "writing" | "fast"
            family: "openai" | "anthropic" | "google" | None (qualquer)
            tier: "frontier" | "premium" | "fast" | "standard" | "any"
            prefer_free: se True, prefere modelos gratuitos
        """
        candidates = [
            (mid, meta) for mid, meta in MODELS.items()
            if task_type in meta.get("strengths", [])
            and (family is None or meta.get("family") == family)
            and (tier == "any" or meta.get("tier") == tier)
        ]
        if not candidates:
            return DEFAULT_MODEL

        def score(item):
            _, meta = item
            tier_score = {"frontier": 4, "premium": 3, "standard": 2, "fast": 1}.get(
                meta.get("tier", "standard"), 0
            )
            return (
                int(prefer_free and meta.get("free", False)) * 10,
                int(meta.get("thinking", False)),
                tier_score,
            )

        candidates.sort(key=score, reverse=True)
        return candidates[0][0]

    # ── Completion ────────────────────────────────────────────────────────────

    def complete(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        system: str = "",
        thinking: bool = False,
        thinking_effort: str = "medium",
        spec_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CompletionResponse:
        """
        Completion com ciclo SDD/TDD integrado.

        Fluxo:
          1. Valida modelo no catálogo Zen
          2. Cria spec dinâmica se necessário
          3. Chama API (ou mock)
          4. Verifica spec
          5. Publica no MetaBus
        """
        req = CompletionRequest(
            prompt=prompt,
            model=model,
            system=system,
            thinking=thinking,
            thinking_effort=thinking_effort,
            spec_id=spec_id,
            metadata=metadata or {},
        )
        return self._execute(req)

    def _execute(self, req: CompletionRequest) -> CompletionResponse:
        if req.model not in MODELS:
            raise ModelNotFoundError(f"Modelo desconhecido no Zen: '{req.model}'")

        active_spec_id = req.spec_id
        if self._sdd_enabled:
            active_spec_id = self._ensure_spec(req)

        raw_response = self._call_api(req)

        verified = False
        if self._sdd_enabled and active_spec_id:
            verified = self._verify_spec(active_spec_id, raw_response)

        self._publish_metabus_event(req, raw_response, verified)

        return CompletionResponse(
            model=req.model,
            provider=PROVIDER_ID,
            content=raw_response.get("content", ""),
            thinking=raw_response.get("thinking", ""),
            spec_id=active_spec_id,
            spec_verified=verified,
            usage=raw_response.get("usage", {}),
            raw=raw_response,
        )

    def _ensure_spec(self, req: CompletionRequest) -> str:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from sdd.spec_engine import spec_registry

            if req.spec_id and spec_registry.get(req.spec_id):
                return req.spec_id

            family = MODELS.get(req.model, {}).get("family", "unknown")
            spec = spec_registry.create_task_spec(
                title=f"Completion via OpenCode Zen [{req.model} / {family}]",
                objective=req.prompt[:200],
                criteria_descriptions=[
                    "A resposta não deve ser vazia",
                    "A resposta deve conter texto coerente",
                    f"O modelo '{req.model}' deve ser utilizado",
                ],
            )
            return spec.spec_id
        except ImportError:
            return ""

    def _verify_spec(self, spec_id: str, response: Dict[str, Any]) -> bool:
        try:
            from sdd.spec_engine import spec_verifier
            result = spec_verifier.verify(spec_id, response.get("content", ""))
            if not result["verified"]:
                logger.warning(
                    "Spec %s não verificada: %d/%d critérios",
                    spec_id, result["passed_count"], result["total_count"],
                )
            return result["verified"]
        except ImportError:
            return False

    def _call_api(self, req: CompletionRequest) -> Dict[str, Any]:
        if not self._api_key:
            return self._mock_response(req)

        try:
            import urllib.request

            payload = {
                "model": req.model,
                "messages": [],
                "max_tokens": req.max_tokens,
                "temperature": req.temperature,
            }
            if req.system:
                payload["messages"].append({"role": "system", "content": req.system})
            payload["messages"].append({"role": "user", "content": req.prompt})

            if req.thinking and MODELS.get(req.model, {}).get("thinking", False):
                payload["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": {
                        "low": 1024, "medium": 4096, "high": 16384
                    }.get(req.thinking_effort, 4096),
                }

            data = json.dumps(payload).encode("utf-8")
            http_req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "opencode-ecosystem-core/3.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(http_req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                choice = body.get("choices", [{}])[0]
                message = choice.get("message", {})
                return {
                    "content": message.get("content", ""),
                    "thinking": message.get("thinking", ""),
                    "usage": body.get("usage", {}),
                    "_raw": body,
                }
        except Exception as exc:
            logger.error("Erro na chamada ao OpenCode Zen: %s", exc)
            return {"content": f"[ERRO] {exc}", "thinking": "", "usage": {}, "_error": str(exc)}

    def _mock_response(self, req: CompletionRequest) -> Dict[str, Any]:
        family = MODELS.get(req.model, {}).get("family", "unknown")
        return {
            "content": (
                f"[MOCK OpenCode Zen — {req.model} ({family})] "
                f"Resposta simulada para: {req.prompt[:100]}..."
            ),
            "thinking": f"[MOCK Thinking — {req.model}] Raciocínio simulado.",
            "usage": {"prompt_tokens": 60, "completion_tokens": 100, "total_tokens": 160},
            "_mock": True,
        }

    def _publish_metabus_event(
        self, req: CompletionRequest, response: Dict[str, Any], verified: bool
    ) -> None:
        try:
            from mci.metabus import metabus
            metabus.publish_subsystem_event(
                "opencode-zen",
                "completion.done",
                {
                    "model": req.model,
                    "family": MODELS.get(req.model, {}).get("family", "unknown"),
                    "spec_id": req.spec_id,
                    "verified": verified,
                    "tokens": response.get("usage", {}).get("total_tokens", 0),
                    "mock": response.get("_mock", False),
                },
                source_agent="opencode_zen_provider",
            )
        except Exception:
            pass

    # ── Utilidades ────────────────────────────────────────────────────────────

    def disable_sdd(self) -> None:
        self._sdd_enabled = False

    def enable_sdd(self) -> None:
        self._sdd_enabled = True

    def provider_info(self) -> Dict[str, Any]:
        return {
            "provider_id": PROVIDER_ID,
            "base_url": self.base_url,
            "total_models": len(MODELS),
            "free_models": sum(1 for m in MODELS.values() if m.get("free")),
            "families": list({m["family"] for m in MODELS.values()}),
            "authenticated": bool(self._api_key),
            "sdd_enabled": self._sdd_enabled,
            "default_model": DEFAULT_MODEL,
        }


# ── Singleton global ──────────────────────────────────────────────────────────

opencode_zen = OpenCodeZenProvider()
