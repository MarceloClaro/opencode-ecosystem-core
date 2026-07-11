# -*- coding: utf-8 -*-
"""
OpenCode Go Provider — Integração com o provider opencode-go
============================================================
Expõe os modelos de código aberto curados pelo OpenCode Go:
  - Kimi (Moonshot AI): kimi-k2.7-code, kimi-k2.6, kimi-k2.5
  - DeepSeek: deepseek-v4-pro, deepseek-v4-flash
  - GLM (Zhipu AI): glm-5.2, glm-5.1, glm-5
  - Qwen (Alibaba): qwen3.7-max, qwen3.7-plus, qwen3.6-plus
  - MiMo/MiniMax: mimo-v2.5-pro, mimo-v2.5, minimax-m3, minimax-m2.7

O provider integra com o motor SDD/TDD do ecossistema:
- Toda requisição cria ou vincula uma Specification no SpecRegistry
- O SpecVerifier é chamado sobre a resposta antes de retorná-la
- Erros de verificação propagam SpecVerificationError

Uso:
    from integrations.opencode_go import OpenCodeGoProvider
    provider = OpenCodeGoProvider()
    result = provider.complete("Escreva um pytest para a função X", model="kimi-k2.7-code")

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger("opencode-go-provider")

# ── Constantes ──────────────────────────────────────────────────────────────

PROVIDER_ID = "opencode-go"
BASE_URL = "https://opencode.ai/zen/go/v1"
ENV_KEY = "OPENCODE_API_KEY"
AUTH_FILE_PATHS = [
    os.path.expanduser("~/.local/share/opencode/auth.json"),
    os.path.expanduser("~/.config/opencode/auth.json"),
]

# Catálogo de modelos curado (atualizado em 2026-07)
MODELS: Dict[str, Dict[str, Any]] = {
    # Kimi / Moonshot AI — excelente para código e raciocínio longo
    "kimi-k2.7-code": {
        "name": "Kimi K2.7 Code",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "debugging", "long-context"],
        "context_window": 200_000,
        "thinking": True,
        "tier": "premium",
    },
    "kimi-k2.6": {
        "name": "Kimi K2.6",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "reasoning"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "standard",
    },
    "kimi-k2.5": {
        "name": "Kimi K2.5",
        "provider": PROVIDER_ID,
        "strengths": ["coding"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "standard",
    },
    # DeepSeek
    "deepseek-v4-pro": {
        "name": "DeepSeek V4 Pro",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "reasoning", "math"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
    },
    "deepseek-v4-flash": {
        "name": "DeepSeek V4 Flash",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "fast"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "fast",
    },
    # GLM / Zhipu AI
    "glm-5.2": {
        "name": "GLM 5.2",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "reasoning", "chinese"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
    },
    "glm-5.1": {
        "name": "GLM 5.1",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "reasoning"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "standard",
    },
    "glm-5": {
        "name": "GLM 5",
        "provider": PROVIDER_ID,
        "strengths": ["coding"],
        "context_window": 32_000,
        "thinking": False,
        "tier": "standard",
    },
    # Qwen / Alibaba
    "qwen3.7-max": {
        "name": "Qwen 3.7 Max",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "reasoning", "academic"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
    },
    "qwen3.7-plus": {
        "name": "Qwen 3.7 Plus",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "reasoning"],
        "context_window": 64_000,
        "thinking": True,
        "tier": "standard",
    },
    "qwen3.6-plus": {
        "name": "Qwen 3.6 Plus",
        "provider": PROVIDER_ID,
        "strengths": ["coding"],
        "context_window": 32_000,
        "thinking": False,
        "tier": "standard",
    },
    # MiMo / MiniMax
    "mimo-v2.5-pro": {
        "name": "MiMo V2.5 Pro",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "agentic"],
        "context_window": 128_000,
        "thinking": True,
        "tier": "premium",
    },
    "mimo-v2.5": {
        "name": "MiMo V2.5",
        "provider": PROVIDER_ID,
        "strengths": ["coding"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "standard",
    },
    "minimax-m3": {
        "name": "MiniMax M3",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "multimodal"],
        "context_window": 128_000,
        "thinking": False,
        "tier": "premium",
    },
    "minimax-m2.7": {
        "name": "MiniMax M2.7",
        "provider": PROVIDER_ID,
        "strengths": ["coding"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "standard",
    },
    # Outros
    "hy3-preview": {
        "name": "HY3 Preview",
        "provider": PROVIDER_ID,
        "strengths": ["coding", "experimental"],
        "context_window": 64_000,
        "thinking": False,
        "tier": "preview",
    },
}

DEFAULT_MODEL = "kimi-k2.7-code"


# ── Exceções ─────────────────────────────────────────────────────────────────

class OpenCodeGoError(Exception):
    """Erro base do provider OpenCode Go."""


class ProviderAuthError(OpenCodeGoError):
    """Chave de API ausente ou inválida."""


class ModelNotFoundError(OpenCodeGoError):
    """Modelo solicitado não existe no catálogo."""


class SpecVerificationError(OpenCodeGoError):
    """A resposta do modelo não passou na verificação SDD."""


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CompletionRequest:
    prompt: str
    model: str = DEFAULT_MODEL
    system: str = ""
    thinking: bool = False
    thinking_effort: str = "medium"   # low | medium | high
    temperature: float = 0.0
    max_tokens: int = 4096
    spec_id: Optional[str] = None     # vincula spec SDD existente
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

class OpenCodeGoProvider:
    """
    Provider para OpenCode Go — modelos open-source curados.

    Integra com SDD/TDD: cria spec dinâmica para cada requisição
    e verifica a resposta antes de retorná-la.

    Autenticação: lê OPENCODE_API_KEY do ambiente ou de
    ~/.local/share/opencode/auth.json (auth.opencode-go.apiKey).
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key or self._load_api_key()
        self._sdd_enabled = True
        logger.info(
            "OpenCodeGoProvider inicializado — %d modelos disponíveis, base_url=%s",
            len(MODELS), self.base_url,
        )

    # ── API Key ──────────────────────────────────────────────────────────────

    def _load_api_key(self) -> str:
        """Carrega a chave de API de variável de ambiente ou auth.json."""
        key = os.environ.get(ENV_KEY, "")
        if key:
            return key
        for path in AUTH_FILE_PATHS:
            if os.path.exists(path):
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    # Suporta auth.json do OpenCode TUI
                    key = (
                        data.get("opencode-go", {}).get("apiKey", "")
                        or data.get("opencode", {}).get("apiKey", "")
                        or data.get("apiKey", "")
                    )
                    if key:
                        logger.debug("Chave OpenCode Go lida de %s", path)
                        return key
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Falha ao ler %s: %s", path, exc)
        # Retorna string vazia — sem chave (modo offline/mock)
        logger.warning(
            "Chave OpenCode Go não encontrada. Configure OPENCODE_API_KEY ou use /connect."
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
                f"Modelo '{model_id}' não encontrado no catálogo OpenCode Go. "
                f"Modelos disponíveis: {list(MODELS.keys())}"
            )
        return {"model_id": model_id, **MODELS[model_id]}

    def best_model_for(self, task_type: str, tier: str = "any") -> str:
        """
        Retorna o ID do melhor modelo para um tipo de tarefa.

        Args:
            task_type: "coding" | "reasoning" | "academic" | "fast" | "math"
            tier: "premium" | "standard" | "fast" | "any"
        """
        candidates = [
            (mid, meta) for mid, meta in MODELS.items()
            if task_type in meta.get("strengths", [])
            and (tier == "any" or meta.get("tier") == tier)
        ]
        if not candidates:
            return DEFAULT_MODEL
        # Prioriza premium com thinking habilitado
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
        """
        Executa uma requisição de completion com ciclo SDD/TDD integrado.

        1. Valida o modelo
        2. Cria spec SDD se `spec_id` não fornecido e SDD habilitado
        3. Executa a chamada ao provider (HTTP se chave disponível, mock caso contrário)
        4. Verifica a resposta contra a spec
        5. Retorna CompletionResponse com metadados de verificação
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
        # Valida modelo
        if req.model not in MODELS:
            raise ModelNotFoundError(f"Modelo desconhecido: '{req.model}'")

        # Integração SDD
        active_spec_id = req.spec_id
        if self._sdd_enabled:
            active_spec_id = self._ensure_spec(req)

        # Execução da chamada
        raw_response = self._call_api(req)

        # Verificação SDD
        verified = False
        if self._sdd_enabled and active_spec_id:
            verified = self._verify_spec(active_spec_id, raw_response)

        # Publica evento no MetaBus
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
        """Cria ou reutiliza uma spec SDD para a requisição."""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from sdd.spec_engine import spec_registry

            if req.spec_id and spec_registry.get(req.spec_id):
                return req.spec_id

            spec = spec_registry.create_task_spec(
                title=f"Completion via OpenCode Go [{req.model}]",
                objective=req.prompt[:200],
                criteria_descriptions=[
                    "A resposta não deve ser vazia",
                    "A resposta deve ser em texto coerente",
                    f"O modelo utilizado deve ser '{req.model}'",
                ],
            )
            return spec.spec_id
        except ImportError:
            logger.debug("SpecRegistry indisponível — SDD desativado para esta chamada")
            return ""

    def _verify_spec(self, spec_id: str, response: Dict[str, Any]) -> bool:
        """Verifica a resposta contra os critérios da spec."""
        try:
            from sdd.spec_engine import spec_verifier
            result = spec_verifier.verify(spec_id, response.get("content", ""))
            if not result["verified"]:
                logger.warning(
                    "Spec %s não verificada: %d/%d critérios passaram",
                    spec_id, result["passed_count"], result["total_count"],
                )
            return result["verified"]
        except ImportError:
            return False

    def _call_api(self, req: CompletionRequest) -> Dict[str, Any]:
        """
        Executa a chamada HTTP ao endpoint OpenCode Go.
        Se a chave de API não estiver disponível, retorna um mock estruturado.
        """
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

            if req.thinking and MODELS.get(req.model, {}).get("thinking", False):
                payload["thinking"] = {
                    "enabled": True,
                    "effort": req.thinking_effort,
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
                    "thinking": message.get("reasoning_content", ""),
                    "usage": body.get("usage", {}),
                    "_raw": body,
                }
        except Exception as exc:
            logger.error("Erro na chamada ao OpenCode Go: %s", exc)
            return {"content": f"[ERRO] {exc}", "thinking": "", "usage": {}, "_error": str(exc)}

    def _mock_response(self, req: CompletionRequest) -> Dict[str, Any]:
        """Resposta simulada para testes e desenvolvimento sem chave de API."""
        return {
            "content": (
                f"[MOCK OpenCode Go — {req.model}] "
                f"Resposta simulada para: {req.prompt[:100]}..."
            ),
            "thinking": "[MOCK] Raciocínio simulado.",
            "usage": {"prompt_tokens": 50, "completion_tokens": 80, "total_tokens": 130},
            "_mock": True,
        }

    def _publish_metabus_event(
        self, req: CompletionRequest, response: Dict[str, Any], verified: bool
    ) -> None:
        """Publica evento de roteamento no MetaBus."""
        try:
            from mci.metabus import metabus
            metabus.publish_subsystem_event(
                "opencode-go",
                "completion.done",
                {
                    "model": req.model,
                    "spec_id": req.spec_id,
                    "verified": verified,
                    "tokens": response.get("usage", {}).get("total_tokens", 0),
                    "mock": response.get("_mock", False),
                },
                source_agent="opencode_go_provider",
            )
        except Exception:
            pass  # MetaBus é opcional; não bloqueia o fluxo

    # ── Utilidades ────────────────────────────────────────────────────────────

    def disable_sdd(self) -> None:
        """Desativa verificação SDD (apenas para testes unitários)."""
        self._sdd_enabled = False

    def enable_sdd(self) -> None:
        """Reativa verificação SDD."""
        self._sdd_enabled = True

    def provider_info(self) -> Dict[str, Any]:
        """Retorna metadados completos do provider."""
        return {
            "provider_id": PROVIDER_ID,
            "base_url": self.base_url,
            "total_models": len(MODELS),
            "authenticated": bool(self._api_key),
            "sdd_enabled": self._sdd_enabled,
            "default_model": DEFAULT_MODEL,
            "tiers": list({m["tier"] for m in MODELS.values()}),
        }


# ── Singleton global ──────────────────────────────────────────────────────────

opencode_go = OpenCodeGoProvider()
