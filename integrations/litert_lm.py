# -*- coding: utf-8 -*-
"""
OpenCode LiteRT-LM Provider — Integração com o provider litert-lm
=================================================================
Expõe os modelos on-device servidos localmente via LiteRT-LM (Google AI Edge):

  - Gemma 4: 2B, 9B, 12B (E2B, E4B com MTP)
  - Gemma 3: 1B, 4B, 12B, 27B
  - Gemma 2: 2B, 9B, 27B
  - Llama 4: 17B
  - Llama 3: 8B, 70B
  - Phi-4: 14B
  - Qwen 2.5: 7B, 32B
  - Qwen 3: 4B, 8B, 15B, 30B, 235B

Inferência 100% local com aceleração CPU/GPU/NPU.
Integração completa com protocolo SDD/TDD do ecossistema.

Uso:
    from integrations.litert_lm import LiteRTLMProvider
    provider = LiteRTLMProvider()
    result = provider.complete("Explique conceito", model="gemma-4-E2B-it")

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("litert-lm-provider")

# ── Constantes ──────────────────────────────────────────────────────────────

PROVIDER_ID = "litert-lm"
BASE_URL = "http://localhost:9379/v1"
ENV_KEY = "LITERT_LM_BASE_URL"
ENV_KEY_FALLBACK = "LITERT_LM_API_KEY"

# Catálogo de modelos suportados pelo LiteRT-LM (Google AI Edge)
# Para consultar os modelos atualmente servidos, use o endpoint /v1/models
# do servidor local, ou consulte um destes abaixo.
MODELS: Dict[str, Dict[str, Any]] = {
    # ── Gemma 4 ──────────────────────────────────────────────────────────
    "gemma-4-E2B-it": {
        "name": "Gemma 4 E2B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "reasoning", "academic"],
        "context_window": 32_768,
        "thinking": False,
        "tier": "standard",
        "free": True,
        "size_gb": 2.5,
    },
    "gemma-4-E4B-it": {
        "name": "Gemma 4 E4B IT (MTP)",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "reasoning", "academic", "multimodal"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "premium",
        "free": True,
        "size_gb": 4.8,
    },
    "gemma-4-9B-it": {
        "name": "Gemma 4 9B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "reasoning", "multimodal"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "premium",
        "free": True,
        "size_gb": 9.0,
    },
    "gemma-4-12B-it": {
        "name": "Gemma 4 12B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["reasoning", "coding", "academic", "multimodal"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "frontier",
        "free": True,
        "size_gb": 12.0,
    },
    # ── Gemma 3 ──────────────────────────────────────────────────────────
    "gemma-3-1B-it": {
        "name": "Gemma 3 1B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["fast", "simple"],
        "context_window": 8_192,
        "thinking": False,
        "tier": "fast",
        "free": True,
        "size_gb": 0.5,
    },
    "gemma-3-4B-it": {
        "name": "Gemma 3 4B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "fast"],
        "context_window": 16_384,
        "thinking": False,
        "tier": "standard",
        "free": True,
        "size_gb": 2.5,
    },
    "gemma-3-12B-it": {
        "name": "Gemma 3 12B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "reasoning", "academic"],
        "context_window": 32_768,
        "thinking": False,
        "tier": "premium",
        "free": True,
        "size_gb": 8.0,
    },
    "gemma-3-27B-it": {
        "name": "Gemma 3 27B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["reasoning", "coding", "academic"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "frontier",
        "free": True,
        "size_gb": 16.0,
    },
    # ── Gemma 2 ──────────────────────────────────────────────────────────
    "gemma-2-2B-it": {
        "name": "Gemma 2 2B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["fast", "simple"],
        "context_window": 8_192,
        "thinking": False,
        "tier": "fast",
        "free": True,
        "size_gb": 1.5,
    },
    "gemma-2-9B-it": {
        "name": "Gemma 2 9B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["coding", "reasoning"],
        "context_window": 16_384,
        "thinking": False,
        "tier": "standard",
        "free": True,
        "size_gb": 5.5,
    },
    "gemma-2-27B-it": {
        "name": "Gemma 2 27B IT",
        "provider": PROVIDER_ID,
        "family": "google",
        "strengths": ["reasoning", "academic"],
        "context_window": 32_768,
        "thinking": False,
        "tier": "premium",
        "free": True,
        "size_gb": 16.0,
    },
    # ── Llama ────────────────────────────────────────────────────────────
    "llama-4-17B-it": {
        "name": "Llama 4 17B IT",
        "provider": PROVIDER_ID,
        "family": "meta",
        "strengths": ["reasoning", "coding", "multimodal"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "premium",
        "free": True,
        "size_gb": 10.0,
    },
    "llama-3-8B-it": {
        "name": "Llama 3 8B IT",
        "provider": PROVIDER_ID,
        "family": "meta",
        "strengths": ["coding", "reasoning"],
        "context_window": 16_384,
        "thinking": False,
        "tier": "standard",
        "free": True,
        "size_gb": 4.5,
    },
    "llama-3-70B-it": {
        "name": "Llama 3 70B IT",
        "provider": PROVIDER_ID,
        "family": "meta",
        "strengths": ["reasoning", "academic", "coding"],
        "context_window": 32_768,
        "thinking": False,
        "tier": "frontier",
        "free": True,
        "size_gb": 40.0,
    },
    # ── Phi ──────────────────────────────────────────────────────────────
    "phi-4-14B-it": {
        "name": "Phi-4 14B IT",
        "provider": PROVIDER_ID,
        "family": "microsoft",
        "strengths": ["reasoning", "math", "coding"],
        "context_window": 16_384,
        "thinking": False,
        "tier": "premium",
        "free": True,
        "size_gb": 9.0,
    },
    # ── Qwen ─────────────────────────────────────────────────────────────
    "qwen-2.5-7B-it": {
        "name": "Qwen 2.5 7B IT",
        "provider": PROVIDER_ID,
        "family": "qwen",
        "strengths": ["coding", "reasoning"],
        "context_window": 32_768,
        "thinking": False,
        "tier": "standard",
        "free": True,
        "size_gb": 4.5,
    },
    "qwen-2.5-32B-it": {
        "name": "Qwen 2.5 32B IT",
        "provider": PROVIDER_ID,
        "family": "qwen",
        "strengths": ["reasoning", "coding", "academic"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "frontier",
        "free": True,
        "size_gb": 20.0,
    },
    "qwen-3-4B-it": {
        "name": "Qwen3 4B IT",
        "provider": PROVIDER_ID,
        "family": "qwen",
        "strengths": ["coding", "fast"],
        "context_window": 32_768,
        "thinking": False,
        "tier": "standard",
        "free": True,
        "size_gb": 2.5,
    },
    "qwen-3-8B-it": {
        "name": "Qwen3 8B IT",
        "provider": PROVIDER_ID,
        "family": "qwen",
        "strengths": ["coding", "reasoning"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "premium",
        "free": True,
        "size_gb": 5.0,
    },
    "qwen-3-30B-it": {
        "name": "Qwen3 30B IT",
        "provider": PROVIDER_ID,
        "family": "qwen",
        "strengths": ["reasoning", "coding", "academic"],
        "context_window": 32_768,
        "thinking": True,
        "tier": "frontier",
        "free": True,
        "size_gb": 18.0,
    },
}

DEFAULT_MODEL = "gemma-4-E2B-it"


# ── Exceções ─────────────────────────────────────────────────────────────────

class LiteRTLError(Exception):
    """Erro base do provider LiteRT-LM."""


class ProviderConnectionError(LiteRTLError):
    """Não foi possível conectar ao servidor LiteRT-LM local."""


class ModelNotFoundError(LiteRTLError):
    """Modelo solicitado não existe no catálogo LiteRT-LM."""


class SpecVerificationError(LiteRTLError):
    """A resposta do modelo não passou na verificação SDD."""


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CompletionRequest:
    prompt: str
    model: str = DEFAULT_MODEL
    system: str = ""
    temperature: float = 0.0
    max_tokens: int = 4096
    spec_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    model: str
    provider: str
    content: str
    spec_id: Optional[str] = None
    spec_verified: bool = False
    usage: Dict[str, int] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)


# ── Provider ──────────────────────────────────────────────────────────────────

class LiteRTLMProvider:
    """
    Provider para LiteRT-LM — inferência on-device local.

    Conecta-se a um servidor OpenAI-compatible rodando em localhost:9379
    (ou em outra URL configurada via LITERT_LM_BASE_URL).

    Suporta modelos Gemma, Llama, Phi, Qwen e outros do ecossistema
    Google AI Edge, executados 100% local com aceleração CPU/GPU/NPU.

    Integra com SDD/TDD: toda requisição pode vincular uma
    Specification no SpecRegistry e verificar a resposta.

    Autenticação: não necessária (servidor local).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: str = "sk-no-key-required",
    ):
        self.base_url = (base_url or os.environ.get(ENV_KEY, BASE_URL)).rstrip("/")
        self._api_key = api_key
        self._sdd_enabled = True
        self._cached_remote_models: Optional[List[Dict[str, Any]]] = None
        logger.info(
            "LiteRTLMProvider inicializado — %d modelos no catálogo, base_url=%s",
            len(MODELS), self.base_url,
        )

    # ── Modelos ───────────────────────────────────────────────────────────────

    def list_models(
        self,
        local_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Retorna catálogo de modelos.

        Se local_only=False (padrão), tenta consultar o servidor local
        em /v1/models para obter a lista real de modelos servidos.
        Se falhar ou local_only=True, retorna o catálogo estático.

        Args:
            local_only: Se True, retorna apenas o catálogo estático.

        Returns:
            Lista de dicionários com metadados dos modelos.
        """
        if not local_only:
            remote = self._fetch_remote_models()
            if remote:
                return remote

        return [{"model_id": mid, **meta} for mid, meta in MODELS.items()]

    def _fetch_remote_models(self) -> Optional[List[Dict[str, Any]]]:
        """Consulta /v1/models do servidor OpenAI-compatible local."""
        if self._cached_remote_models is not None:
            return self._cached_remote_models

        try:
            import urllib.request

            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "opencode-ecosystem-core/3.0",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                remote_models = body.get("data", [])

            # Enriquece com metadados do catálogo local
            enriched = []
            for rm in remote_models:
                mid = rm.get("id", "")
                local_meta = MODELS.get(mid, {})
                enriched.append({
                    "model_id": mid,
                    "name": local_meta.get("name", mid),
                    "provider": PROVIDER_ID,
                    "family": local_meta.get("family", "unknown"),
                    "strengths": local_meta.get("strengths", ["general"]),
                    "context_window": local_meta.get("context_window", 32_768),
                    "thinking": local_meta.get("thinking", False),
                    "tier": local_meta.get("tier", "standard"),
                    "free": True,
                    "size_gb": local_meta.get("size_gb", 0),
                    "remote": True,
                    "server_status": "online",
                    **rm,
                })

            # Se o servidor retornou modelos, adiciona também os do catálogo
            # que podem não estar servidos mas são compatíveis
            if enriched:
                served_ids = {m["model_id"] for m in enriched}
                for mid, meta in MODELS.items():
                    if mid not in served_ids:
                        enriched.append({
                            "model_id": mid,
                            **meta,
                            "remote": False,
                            "server_status": "offline",
                        })

                self._cached_remote_models = enriched
                return enriched

        except Exception as exc:
            logger.debug(
                "Servidor LiteRT-LM não acessível em %s: %s",
                self.base_url, exc,
            )

        return None

    def get_model_info(
        self,
        model_id: str,
        refresh_remote: bool = False,
    ) -> Dict[str, Any]:
        """Retorna informações detalhadas de um modelo.

        Args:
            model_id: Identificador do modelo.
            refresh_remote: Se True, consulta o servidor mesmo se
                já tiver cache.

        Returns:
            Dicionário com metadados do modelo.

        Raises:
            ModelNotFoundError: Se o modelo não existir.
        """
        # Tenta remote primeiro se disponível
        if refresh_remote or self._cached_remote_models is None:
            self._fetch_remote_models()

        if self._cached_remote_models:
            for m in self._cached_remote_models:
                if m.get("model_id") == model_id:
                    return m

        # Fallback para catálogo local
        if model_id in MODELS:
            return {"model_id": model_id, **MODELS[model_id]}

        raise ModelNotFoundError(
            f"Modelo '{model_id}' não encontrado no catálogo LiteRT-LM. "
            f"Modelos disponíveis: {list(MODELS.keys())}"
        )

    def best_model_for(
        self,
        task_type: str,
        family: Optional[str] = None,
        tier: str = "any",
        max_size_gb: Optional[float] = None,
    ) -> str:
        """
        Seleciona o melhor modelo LiteRT-LM para a tarefa.

        Args:
            task_type: "coding" | "reasoning" | "academic" | "fast" | "math"
            family: "google" | "meta" | "microsoft" | "qwen" | None (qualquer)
            tier: "frontier" | "premium" | "standard" | "fast" | "any"
            max_size_gb: Tamanho máximo do modelo em GB (ex.: 8.0 para RAM limitada).

        Returns:
            ID do modelo mais adequado.
        """
        candidates = [
            (mid, meta) for mid, meta in MODELS.items()
            if task_type in meta.get("strengths", [])
            and (family is None or meta.get("family") == family)
            and (tier == "any" or meta.get("tier") == tier)
            and (max_size_gb is None or meta.get("size_gb", 0) <= max_size_gb)
        ]
        if not candidates:
            # Fallback progressivo: reduz tier
            if tier != "any":
                return self.best_model_for(task_type, family, "any", max_size_gb)
            return DEFAULT_MODEL

        def score(item):
            _, meta = item
            tier_score = {"frontier": 4, "premium": 3, "standard": 2, "fast": 1}.get(
                meta.get("tier", "standard"), 0
            )
            return (
                int(meta.get("thinking", False)) * 10,
                tier_score,
                -meta.get("size_gb", 0),  # prefere modelos menores
            )

        candidates.sort(key=score, reverse=True)
        return candidates[0][0]

    # ── Completion ────────────────────────────────────────────────────────────

    def complete(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        system: str = "",
        spec_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CompletionResponse:
        """
        Completion com ciclo SDD/TDD integrado.

        Fluxo:
          1. Valida modelo no catálogo LiteRT-LM
          2. Cria spec dinâmica se necessário
          3. Chama servidor local
          4. Verifica spec
          5. Publica no MetaBus

        Args:
            prompt: Texto do prompt.
            model: ID do modelo (ex.: "gemma-4-E2B-it").
            system: Instrução de sistema (opcional).
            spec_id: ID de spec existente (opcional).
            metadata: Metadados adicionais.

        Returns:
            CompletionResponse com o resultado.
        """
        req = CompletionRequest(
            prompt=prompt,
            model=model,
            system=system,
            spec_id=spec_id,
            metadata=metadata or {},
        )
        return self._execute(req)

    def _execute(self, req: CompletionRequest) -> CompletionResponse:
        if req.model not in MODELS:
            raise ModelNotFoundError(
                f"Modelo desconhecido no LiteRT-LM: '{req.model}'. "
                f"Disponíveis: {list(MODELS.keys())}"
            )

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
            spec_id=active_spec_id,
            spec_verified=verified,
            usage=raw_response.get("usage", {}),
            raw=raw_response,
        )

    # ── SDD/TDD Integration ─────────────────────────────────────────────────

    def _ensure_spec(self, req: CompletionRequest) -> str:
        """Cria ou reutiliza uma spec para a requisição.

        Returns:
            spec_id ou string vazia se spec_engine não disponível.
        """
        try:
            from sdd.spec_engine import spec_registry

            if req.spec_id and spec_registry.get(req.spec_id):
                return req.spec_id

            family = MODELS.get(req.model, {}).get("family", "unknown")
            spec = spec_registry.create_task_spec(
                title=f"Completion via LiteRT-LM [{req.model} / {family}]",
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
        """Verifica se a resposta atende aos critérios da spec.

        Returns:
            True se verificada, False caso contrário.
        """
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

    # ── API Call ──────────────────────────────────────────────────────────────

    def _call_api(self, req: CompletionRequest) -> Dict[str, Any]:
        """Chama o servidor OpenAI-compatible /v1/chat/completions.

        Se o servidor não estiver acessível, retorna resposta mock.
        """
        try:
            import urllib.request

            payload = {
                "model": req.model,
                "messages": [],
                "max_tokens": req.max_tokens,
                "temperature": req.temperature,
            }
            if req.system:
                payload["messages"].append({
                    "role": "system",
                    "content": req.system,
                })
            payload["messages"].append({
                "role": "user",
                "content": req.prompt,
            })

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
                    "usage": body.get("usage", {}),
                    "_raw": body,
                }

        except Exception as exc:
            logger.warning(
                "Servidor LiteRT-LM não acessível (%s). Usando mock.", exc
            )
            return self._mock_response(req)

    def _mock_response(self, req: CompletionRequest) -> Dict[str, Any]:
        """Gera resposta mock quando o servidor local não está acessível."""
        meta = MODELS.get(req.model, {})
        return {
            "content": (
                f"[MOCK LiteRT-LM — {req.model} ({meta.get('family', 'unknown')})] "
                f"Resposta simulada. Servidor local não está rodando.\n"
                f"Prompt: {req.prompt[:100]}..."
            ),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "_mock": True,
            "_error": "Servidor LiteRT-LM não acessível. Inicie com: litert-lm serve <model>",
        }

    # ── MetaBus Events ──────────────────────────────────────────────────────

    def _publish_metabus_event(
        self,
        req: CompletionRequest,
        response: Dict[str, Any],
        verified: bool,
    ) -> None:
        """Publica evento de completion no MetaBus."""
        try:
            from mci.metabus import metabus

            metabus.publish_subsystem_event(
                PROVIDER_ID,
                "completion.done",
                {
                    "model": req.model,
                    "family": MODELS.get(req.model, {}).get("family", "unknown"),
                    "spec_id": req.spec_id,
                    "verified": verified,
                    "tokens": response.get("usage", {}).get("total_tokens", 0),
                    "mock": response.get("_mock", False),
                },
                source_agent="litert_lm_provider",
            )
        except Exception:
            pass

    # ── Utilidades ────────────────────────────────────────────────────────────

    def disable_sdd(self) -> None:
        """Desativa verificação SDD."""
        self._sdd_enabled = False

    def enable_sdd(self) -> None:
        """Ativa verificação SDD."""
        self._sdd_enabled = True

    def clear_model_cache(self) -> None:
        """Limpa cache de modelos remotos (força re-consulta)."""
        self._cached_remote_models = None

    def server_status(self) -> Dict[str, Any]:
        """Verifica se o servidor local está respondendo.

        Returns:
            Dicionário com status do servidor.
        """
        try:
            import urllib.request

            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "opencode-ecosystem-core/3.0",
                },
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                models = body.get("data", [])
                return {
                    "online": True,
                    "base_url": self.base_url,
                    "models_served": len(models),
                    "model_names": [m.get("id") for m in models],
                }
        except Exception as exc:
            return {
                "online": False,
                "base_url": self.base_url,
                "error": str(exc),
                "hint": "Inicie o servidor com: litert-lm serve <modelo> --port 9379",
            }

    def provider_info(self) -> Dict[str, Any]:
        """Informações resumidas do provider."""
        return {
            "provider_id": PROVIDER_ID,
            "base_url": self.base_url,
            "total_models": len(MODELS),
            "families": list({m["family"] for m in MODELS.values()}),
            "authenticated": bool(self._api_key),
            "sdd_enabled": self._sdd_enabled,
            "default_model": DEFAULT_MODEL,
            "server": self.server_status(),
        }


# ── Singleton global ──────────────────────────────────────────────────────────

litert_lm = LiteRTLMProvider()
