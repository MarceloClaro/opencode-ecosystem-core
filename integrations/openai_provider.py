# -*- coding: utf-8 -*-
"""
OpenAI Provider — Integração com a API oficial da OpenAI
=========================================================
Expõe modelos GPT da OpenAI via API compatível com OpenAI:

  - GPT-4o (multimodal, raciocínio)
  - GPT-4o Mini (rápido e econômico)
  - GPT-4.1 (coding, reasoning)
  - o3 (raciocínio profundo)
  - o4-mini (raciocínio rápido e leve)

Uso:
    from integrations.openai_provider import OpenAIProvider
    provider = OpenAIProvider()
    result = provider.complete("Explique conceito", model="gpt-4o")

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger("openai-provider")

# ── Constantes ──────────────────────────────────────────────────────────────

PROVIDER_ID = "openai"
BASE_URL = "https://api.openai.com/v1"
ENV_KEY = "OPENAI_API_KEY"

# Catálogo de modelos OpenAI
MODELS: Dict[str, Dict[str, Any]] = {
    "gpt-4o": {
        "name": "GPT-4o",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["coding", "reasoning", "writing", "multimodal", "academic"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["coding", "fast", "writing"],
        "context_window": 128_000,
        "thinking": False,
        "tier": "fast",
    },
    "gpt-4.1": {
        "name": "GPT-4.1",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["coding", "reasoning"],
        "context_window": 1_000_000,
        "thinking": True,
        "tier": "premium",
    },
    "o3": {
        "name": "o3",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["reasoning", "math", "science", "academic"],
        "context_window": 200_000,
        "thinking": True,
        "tier": "premium",
    },
    "o4-mini": {
        "name": "o4-mini",
        "provider": PROVIDER_ID,
        "family": "openai",
        "strengths": ["reasoning", "math", "coding", "fast"],
        "context_window": 200_000,
        "thinking": True,
        "tier": "standard",
    },
}

DEFAULT_MODEL = "gpt-4o"


# ── Exceções ─────────────────────────────────────────────────────────────────

class OpenAIError(Exception):
    """Erro base do provider OpenAI."""


class ProviderAuthError(OpenAIError):
    """Chave de API ausente ou inválida."""


class ModelNotFoundError(OpenAIError):
    """Modelo solicitado não existe no catálogo."""


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CompletionRequest:
    prompt: str
    model: str = DEFAULT_MODEL
    system: str = ""
    thinking: bool = False
    thinking_effort: str = "medium"
    temperature: float = 0.0
    max_tokens: int = 4096
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

class OpenAIProvider:
    """
    Provider para OpenAI — modelos GPT.

    Autenticação: lê OPENAI_API_KEY do ambiente.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or self._load_api_key()
        logger.info(
            "OpenAIProvider inicializado — %d modelos, base_url=%s, auth=%s",
            len(MODELS), self.base_url, "sim" if self._api_key else "não",
        )

    # ── API Key ──────────────────────────────────────────────────────────────

    def _load_api_key(self) -> str:
        """Carrega a chave de API da variável de ambiente."""
        key = os.environ.get(ENV_KEY, "")
        if key:
            return key
        logger.warning(
            "Chave OpenAI não encontrada. Configure OPENAI_API_KEY no .env"
        )
        return ""

    # ── Modelos ───────────────────────────────────────────────────────────────

    def list_models(self) -> List[Dict[str, Any]]:
        """Retorna o catálogo de modelos disponíveis."""
        return [{"model_id": mid, **meta} for mid, meta in MODELS.items()]

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Retorna metadados de um modelo específico."""
        if model_id not in MODELS:
            raise ModelNotFoundError(
                f"Modelo '{model_id}' não encontrado no catálogo OpenAI. "
                f"Disponíveis: {list(MODELS.keys())}"
            )
        return {"model_id": model_id, **MODELS[model_id]}

    def best_model_for(self, task_type: str, tier: str = "any") -> str:
        """Retorna o ID do melhor modelo para um tipo de tarefa."""
        candidates = [
            (mid, meta) for mid, meta in MODELS.items()
            if task_type in meta.get("strengths", [])
            and (tier == "any" or meta.get("tier") == tier)
        ]
        if not candidates:
            return DEFAULT_MODEL
        candidates.sort(
            key=lambda x: (x[1].get("tier") == "premium", x[1].get("thinking", False)),
            reverse=True,
        )
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
        """Executa uma requisição de completion via API OpenAI."""
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
            raise ModelNotFoundError(f"Modelo desconhecido: '{req.model}'")

        raw_response = self._call_api(req)

        return CompletionResponse(
            model=req.model,
            provider=PROVIDER_ID,
            content=raw_response.get("content", ""),
            thinking=raw_response.get("thinking", ""),
            spec_id=req.spec_id,
            spec_verified=False,
            usage=raw_response.get("usage", {}),
            raw=raw_response,
        )

    def _call_api(self, req: CompletionRequest) -> Dict[str, Any]:
        """Executa a chamada HTTP ao endpoint da OpenAI."""
        if not self._api_key:
            logger.debug("Modo mock ativo (sem chave de API)")
            return self._mock_response(req)

        try:
            import urllib.request
            import urllib.error

            payload = {
                "model": req.model,
                "messages": [],
                "max_tokens": req.max_tokens,
                "temperature": req.temperature,
            }
            if req.system:
                payload["messages"].append({"role": "system", "content": req.system})
            payload["messages"].append({"role": "user", "content": req.prompt})

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
                    "thinking": message.get("reasoning_content", ""),
                    "usage": body.get("usage", {}),
                    "_raw": body,
                }
        except Exception as exc:
            logger.error("Erro na chamada à OpenAI: %s", exc)
            return {"content": f"[ERRO] {exc}", "thinking": "", "usage": {}, "_error": str(exc)}

    def _mock_response(self, req: CompletionRequest) -> Dict[str, Any]:
        """Resposta simulada para testes sem chave de API."""
        return {
            "content": (
                f"[MOCK OpenAI — {req.model}] "
                f"Resposta simulada para: {req.prompt[:100]}..."
            ),
            "thinking": "[MOCK] Raciocínio simulado.",
            "usage": {"prompt_tokens": 50, "completion_tokens": 80, "total_tokens": 130},
            "_mock": True,
        }

    def provider_info(self) -> Dict[str, Any]:
        """Retorna metadados completos do provider."""
        return {
            "provider_id": PROVIDER_ID,
            "base_url": self.base_url,
            "total_models": len(MODELS),
            "authenticated": bool(self._api_key),
            "default_model": DEFAULT_MODEL,
            "tiers": list({m["tier"] for m in MODELS.values()}),
        }


# ── Singleton global ──────────────────────────────────────────────────────────

openai_provider = OpenAIProvider()
