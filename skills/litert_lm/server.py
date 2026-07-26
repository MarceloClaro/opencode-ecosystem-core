# -*- coding: utf-8 -*-
"""
LiteRTOpenAIServer — Servidor OpenAI-Compatible para LiteRT-LM
==============================================================
Implementa endpoints compatíveis com a API OpenAI:
- GET  /v1/models
- POST /v1/chat/completions (streaming opcional)

Pode operar como wrapper do servidor nativo litert-lm serve ou como
implementação própria via http.server.
"""

from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional


# ── Tenta importar litert_lm ──────────────────────────────────────────────────

try:
    import litert_lm

    _LITERT_AVAILABLE = True
except ImportError:
    _LITERT_AVAILABLE = False


DEFAULT_CONTEXT_TOKENS = 20_480
CONTEXT_TOKENS_ENV = "LITERT_LM_CONTEXT_TOKENS"


def _resolve_context_tokens(context_tokens: Optional[int]) -> int:
    """Resolve o contexto total do Engine, separado do output máximo."""
    if context_tokens is not None:
        if context_tokens <= 0:
            raise ValueError("context_tokens deve ser um inteiro positivo")
        return context_tokens

    raw_value = os.environ.get(CONTEXT_TOKENS_ENV)
    if raw_value is None:
        return DEFAULT_CONTEXT_TOKENS

    try:
        configured = int(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_CONTEXT_TOKENS
    return configured if configured > 0 else DEFAULT_CONTEXT_TOKENS


def _create_backend(litert_module: Any, backend: str) -> Any:
    """Cria somente o backend escolhido, sem fallback implícito."""
    normalized = backend.lower()
    if normalized == "cpu":
        return litert_module.Backend.CPU()
    if normalized == "gpu":
        return litert_module.Backend.GPU()
    if normalized == "npu":
        return litert_module.Backend.NPU()
    raise ValueError(
        f"Backend LiteRT-LM inválido: {backend!r}. "
        "Use 'cpu', 'gpu' ou 'npu'."
    )


# ── LiteRTOpenAIServer ────────────────────────────────────────────────────────


class LiteRTOpenAIServer:
    """Servidor HTTP compatível com API OpenAI para modelos LiteRT-LM.

    Fornece uma interface programática para os endpoints /v1/models e
    /v1/chat/completions, podendo ser montada em um servidor HTTP real
    (http.server, FastAPI, etc.).

    Attributes:
        model_path: Caminho para o arquivo .litertlm.
        model_name: Nome do modelo para exibição nas respostas da API.
        host: Host do servidor.
        port: Porta do servidor.
        cors_origins: Origens CORS permitidas.
    """

    def __init__(
        self,
        model_path: str,
        model_name: Optional[str] = None,
        host: str = "127.0.0.1",
        port: int = 9379,
        backend: str = "cpu",
        cors_origins: Optional[List[str]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        context_tokens: Optional[int] = None,
    ):
        """Inicializa o servidor.

        Args:
            model_path: Caminho para o arquivo .litertlm.
            model_name: Nome do modelo (default: extraído do path).
            host: Host para escutar.
            port: Porta para escutar.
            backend: Backend de inferência.
            cors_origins: Origens CORS permitidas.
            max_tokens: Máximo de tokens na resposta (output).
            temperature: Temperatura padrão.
            context_tokens: Tamanho total do contexto do Engine. Se None,
                usa ``LITERT_LM_CONTEXT_TOKENS`` ou 20480.
        """
        self.model_path = model_path
        self.model_name = model_name or os.path.basename(
            os.path.dirname(model_path)
        ) or "litert-lm-model"
        self.host = host
        self.port = port
        self.backend = backend
        # CORS permanece desabilitado por padrão; uma origem só é liberada
        # quando foi fornecida explicitamente pelo chamador.
        self.cors_origins = [
            origin.strip()
            for origin in (cors_origins or [])
            if isinstance(origin, str) and origin.strip()
        ]
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.context_tokens = _resolve_context_tokens(context_tokens)

        self._engine = None
        self._lock = threading.Lock()

    # ── Endpoints ─────────────────────────────────────────────────────────

    def list_models(self) -> List[Dict[str, Any]]:
        """GET /v1/models — Lista modelos disponíveis.

        Returns:
            Lista de dicionários no formato OpenAI API.
        """
        return [
            {
                "id": self.model_name,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "litert-lm",
                "permission": [],
            }
        ]

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        *,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """POST /v1/chat/completions — Gera resposta do modelo.

        Args:
            messages: Lista de mensagens no formato OpenAI.
            stream: Se True, retorna resposta para streaming (ainda não implementado).
            temperature: Temperatura para esta requisição (opcional).
            max_tokens: Campo legado para o máximo de tokens (opcional).
            max_completion_tokens: Campo OpenAI para o máximo de tokens de
                saída (opcional). Tem precedência sobre ``max_tokens``.

        Returns:
            Dicionário no formato OpenAI ChatCompletion response.

        Raises:
            RuntimeError: Se litert_lm não estiver disponível.
        """
        if not _LITERT_AVAILABLE:
            return self._make_mock_response(messages)

        temp = temperature if temperature is not None else self.temperature
        # ``max_completion_tokens`` é o campo atual da API OpenAI-compatible;
        # ``max_tokens`` permanece como fallback para clientes antigos.
        max_out = (
            max_completion_tokens
            if max_completion_tokens is not None
            else max_tokens if max_tokens is not None else self.max_tokens
        )

        with self._lock:
            if self._engine is None:
                self._init_engine()

            # Extrai o último user message para enviar
            user_msg = self._extract_last_user_message(messages)
            if not user_msg:
                return self._error_response("No user message found")

            sampler_config = litert_lm.SamplerConfig(temperature=temp)

            # Prepara mensagens incluindo system se houver
            conv_messages = list(messages)

            with self._engine.create_conversation(
                sampler_config=sampler_config,
                max_output_tokens=max_out,
                messages=conv_messages,
            ) as conv:
                stream_result = conv.send_message_async(user_msg)
                text = ""
                for chunk in stream_result:
                    content_list = chunk.get("content", [])
                    for item in content_list:
                        if item.get("type") == "text":
                            text += item.get("text", "")

        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

    # ── Inicialização do Engine ───────────────────────────────────────────

    def _init_engine(self):
        """Inicializa o LiteRT-LM Engine (thread-safe)."""
        # A fábrica do backend é chamada somente depois da seleção. Qualquer
        # RuntimeError do hardware solicitado deve ser observável pelo usuário.
        backend_obj = _create_backend(litert_lm, self.backend)

        self._engine = litert_lm.Engine(
            self.model_path,
            backend=backend_obj,
            max_num_tokens=self.context_tokens,
        )
        self._engine.__enter__()

    def close(self):
        """Fecha o engine e libera recursos."""
        with self._lock:
            if self._engine is not None:
                try:
                    self._engine.__exit__(None, None, None)
                except Exception:
                    pass
                self._engine = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _extract_last_user_message(
        messages: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Extrai o texto da última mensagem com role='user'."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    texts = [
                        item.get("text", "")
                        for item in content
                        if item.get("type") == "text"
                    ]
                    return "\n".join(texts)
                return str(content)
        return None

    @staticmethod
    def _extract_system_message(
        messages: List[Dict[str, Any]],
    ) -> Optional[str]:
        """Extrai a mensagem de sistema se presente."""
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                return str(content) if not isinstance(content, list) else ""
        return None

    def _make_mock_response(
        self,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Gera resposta mock quando litert_lm não está disponível."""
        user_msg = self._extract_last_user_message(messages) or ""
        return {
            "id": f"chatcmpl-mock-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"[MOCK] Resposta simulada para: {user_msg[:50]}...",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    @staticmethod
    def _error_response(message: str) -> Dict[str, Any]:
        """Gera resposta de erro no formato OpenAI."""
        return {
            "error": {
                "message": message,
                "type": "invalid_request_error",
                "code": 400,
            }
        }
