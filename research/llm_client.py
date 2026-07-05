# -*- coding: utf-8 -*-
"""
Cliente LLM Unificado — Ollama (local) e OpenAI-compatível (nuvem)
==================================================================
Camada de abstração para enriquecimento de fichamentos e resenhas com
modelos de linguagem, com preferência configurável por **modelos locais
via Ollama** (privacidade total, custo zero) e fallback para provedores
OpenAI-compatíveis quando disponíveis.

Ordem de resolução do provedor (modo ``auto``):
    1. Ollama local (``http://localhost:11434`` ou ``OLLAMA_HOST``)
    2. API OpenAI-compatível (``OPENAI_API_KEY``/``OPENAI_API_BASE``)
    3. ``None`` — o pipeline segue 100% determinístico (stdlib), sem erro.

Variáveis de ambiente:
    OLLAMA_HOST     URL do servidor Ollama (padrão http://localhost:11434)
    OLLAMA_MODEL    Modelo local preferido (padrão llama3.2)
    RESEARCH_LLM    Força o provedor: "ollama", "openai" ou "none"
    OPENAI_API_KEY  Chave para provedores OpenAI-compatíveis

Implementado apenas com stdlib (urllib) — nenhuma dependência extra.
"""

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Optional

logger = logging.getLogger("research.llm_client")

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OPENAI_MODEL = "gemini-2.5-flash"


class LLMClient:
    """Cliente unificado para geração de texto com LLMs locais ou em nuvem.

    Exemplo::

        client = LLMClient()             # auto-detecta Ollama → OpenAI
        client = LLMClient("ollama")     # força Ollama local
        texto = client.generate("Resuma este artigo...")
    """

    def __init__(self, provider: str = "auto",
                 model: Optional[str] = None,
                 timeout: int = 120):
        self.timeout = timeout
        env_provider = os.environ.get("RESEARCH_LLM", "").strip().lower()
        if provider == "auto" and env_provider in ("ollama", "openai", "none"):
            provider = env_provider
        self.provider = self._resolve_provider(provider)
        self.model = model or self._default_model()

    # ------------------------------------------------------------------
    def _resolve_provider(self, provider: str) -> Optional[str]:
        if provider == "none":
            return None
        if provider in ("ollama", "openai"):
            return provider
        # auto: prioriza Ollama local, depois OpenAI-compatível
        if self.ollama_available():
            return "ollama"
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        return None

    def _default_model(self) -> str:
        if self.provider == "ollama":
            return os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        return os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

    # ------------------------------------------------------------------
    @staticmethod
    def ollama_host() -> str:
        return os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST).rstrip("/")

    @classmethod
    def ollama_available(cls, timeout: int = 3) -> bool:
        """Verifica se um servidor Ollama está acessível localmente."""
        try:
            req = urllib.request.Request(cls.ollama_host() + "/api/tags")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except (urllib.error.URLError, OSError, ValueError):
            return False

    @classmethod
    def ollama_models(cls, timeout: int = 5) -> list:
        """Lista os modelos instalados no servidor Ollama local."""
        try:
            req = urllib.request.Request(cls.ollama_host() + "/api/tags")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return [m.get("name", "") for m in data.get("models", [])]
        except (urllib.error.URLError, OSError, ValueError,
                json.JSONDecodeError):
            return []

    # ------------------------------------------------------------------
    def available(self) -> bool:
        return self.provider is not None

    def generate(self, prompt: str, system: str = "",
                 max_tokens: int = 1200) -> Optional[str]:
        """Gera texto com o provedor resolvido; None se indisponível."""
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system, max_tokens)
        if self.provider == "openai":
            return self._generate_openai(prompt, system, max_tokens)
        return None

    # ------------------------------------------------------------------
    def _generate_ollama(self, prompt: str, system: str,
                         max_tokens: int) -> Optional[str]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "Você é um pesquisador acadêmico PhD.",
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.4},
        }
        try:
            req = urllib.request.Request(
                self.ollama_host() + "/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = (data.get("response") or "").strip()
            return text or None
        except (urllib.error.URLError, OSError, ValueError,
                json.JSONDecodeError) as exc:
            logger.debug(f"Ollama indisponível: {exc}")
            return None

    def _generate_openai(self, prompt: str, system: str,
                         max_tokens: int) -> Optional[str]:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return None
        base = os.environ.get(
            "OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": messages,
                   "max_tokens": max_tokens}
        try:
            req = urllib.request.Request(
                base + "/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json",
                         "Authorization": f"Bearer {api_key}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices") or []
            if choices:
                return (choices[0].get("message", {})
                        .get("content") or "").strip() or None
        except (urllib.error.URLError, OSError, ValueError,
                json.JSONDecodeError) as exc:
            logger.debug(f"API OpenAI-compatível indisponível: {exc}")
        return None

    # ------------------------------------------------------------------
    def describe(self) -> dict:
        """Metadados do provedor ativo, para auditoria/manifest."""
        return {
            "provider": self.provider or "deterministic",
            "model": self.model if self.provider else None,
            "local": self.provider == "ollama",
            "ollama_host": self.ollama_host()
            if self.provider == "ollama" else None,
        }
