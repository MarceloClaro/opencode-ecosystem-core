# -*- coding: utf-8 -*-
"""
LiteRT-LM Provider — Integração com modelos on-device via LiteRT-LM
===================================================================
Expõe os modelos locais executados pelo LiteRT-LM (Google AI Edge)
como um provider nativo do ecossistema OpenCode.

Modelos disponíveis (via litert-lm list):
  - litert-community/gemma-4-E2B-it-litert-lm (2B)
  - litert-community/gemma-4-E4B-it-litert-lm (4B)
  - litert-community/gemma-4-12B-it-litert-lm (12B)
  - litert-community/Qwen3-0.6B (586MB)

Funcionamento:
  - Inicia automaticamente o servidor litert-lm serve em background
    na porta 9379 se ele não estiver rodando
  - Comunica via API OpenAI-compatible (http://127.0.0.1:9379/v1)
  - Suporta /v1/models e /v1/chat/completions

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import logging
import os
import re
import signal
import subprocess
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from ipaddress import ip_address
from typing import Any, Dict, List, Optional
from urllib import request as urllib_request
from urllib.error import URLError
from urllib.parse import urlsplit, urlunsplit

from integrations.litert_lm_supervisor import (
    LITERT_HOST as SUPERVISOR_HOST,
    LITERT_PORT as SUPERVISOR_PORT,
    LiteRTSupervisor,
    SupervisorConfig,
    SupervisorState,
)

logger = logging.getLogger("litert-lm-provider")

# ── Constantes ──────────────────────────────────────────────────────────────

PROVIDER_ID = "litert-lm"
DEFAULT_MODEL = "litert-community/gemma-4-E2B-it-litert-lm"
LITERT_SERVE_PORT = 9379
SERVER_START_TIMEOUT = 120  # segundos máximos para inicialização do modelo

HOST_ENV = "LITERT_LM_HOST"
BASE_URL_ENV = "LITERT_LM_BASE_URL"
CORS_ORIGIN_ENV = "LITERT_LM_CORS_ORIGIN"
CORS_ORIGINS_ENV = "LITERT_LM_CORS_ORIGINS"
ALLOW_INSECURE_CORS_ENV = "LITERT_LM_ALLOW_INSECURE_CORS"
DEFAULT_LOCAL_HOST = "127.0.0.1"
CONTEXT_TOKENS_ENV = "LITERT_LM_CONTEXT_TOKENS"
LEGACY_CONTEXT_TOKENS_ENV = "LITERT_LM_MAX_TOKENS"
DEFAULT_CONTEXT_TOKENS = 20_480


def _is_loopback_url(value: str) -> bool:
    """Retorna se ``value`` aponta para um endpoint HTTP de loopback."""
    try:
        parsed = urlsplit(value.strip())
        hostname = parsed.hostname
        if parsed.scheme not in {"http", "https"} or not hostname:
            return False
        if hostname.lower() == "localhost":
            return True
        return ip_address(hostname).is_loopback
    except (TypeError, ValueError):
        return False


def _validated_local_host(
    configured: Optional[str],
    default: str = DEFAULT_LOCAL_HOST,
) -> str:
    """Aceita somente hosts de loopback para o daemon local."""
    if configured is None or not configured.strip():
        return default

    host = configured.strip()
    if host.lower() == "localhost":
        return "localhost"
    try:
        if ip_address(host).is_loopback:
            return host
    except ValueError:
        pass
    raise ValueError(
        f"Host LiteRT-LM inseguro: {host!r}; use um endereço de loopback."
    )


try:
    LITERT_SERVE_HOST = _validated_local_host(os.environ.get(HOST_ENV))
except ValueError:
    # Um override inseguro não pode tornar o módulo importável com bind global.
    LITERT_SERVE_HOST = DEFAULT_LOCAL_HOST


def _local_base_url(host: str, port: int = LITERT_SERVE_PORT) -> str:
    """Formata corretamente hosts IPv4, nomes locais e IPv6."""
    normalized_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    return f"http://{normalized_host}:{port}/v1"


_DEFAULT_BASE_URL = _local_base_url(LITERT_SERVE_HOST)


def _environment_base_url(default: str = _DEFAULT_BASE_URL) -> str:
    """Lê ``LITERT_LM_BASE_URL`` somente quando ele permanece local.

    A variável de ambiente é uma configuração implícita e, portanto, não
    concede opt-in para rede. Uma URL remota passada diretamente à API continua
    sendo possível para doubles e integrações explicitamente revisadas.
    """
    safe_default = default.rstrip("/")
    if not _is_loopback_url(safe_default):
        safe_default = _DEFAULT_BASE_URL

    configured = os.environ.get(BASE_URL_ENV)
    if configured and configured.strip():
        candidate = configured.strip().rstrip("/")
        if _is_loopback_url(candidate):
            return candidate
        logger.warning(
            "%s remoto ignorado por padrão; usando endpoint de loopback",
            BASE_URL_ENV,
        )
    return safe_default


BASE_URL = _environment_base_url()

_READINESS_BASE_URL: ContextVar[Optional[str]] = ContextVar(
    "litert_lm_readiness_base_url",
    default=None,
)


def _configured_base_url(
    base_url: Optional[str] = None,
    default: Optional[str] = None,
) -> str:
    """Resolve a URL explícita ou a configuração implícita segura.

    ``base_url`` não é validada contra loopback quando fornecida diretamente:
    isso preserva a injeção de endpoints remotos em mocks/testes. O ambiente,
    por outro lado, sempre passa pela política de loopback.
    """
    if base_url is not None:
        explicit = str(base_url).strip()
        if explicit:
            return explicit.rstrip("/")

    local_default = (default or BASE_URL).rstrip("/")
    if not _is_loopback_url(local_default):
        local_default = _DEFAULT_BASE_URL
    if local_default == BASE_URL and os.environ.get(HOST_ENV):
        return _local_base_url(_configured_host())
    return _environment_base_url(local_default)


def _configured_host(default: str = LITERT_SERVE_HOST) -> str:
    """Obtém o host de bind; o fallback permanece restrito ao loopback."""
    return _validated_local_host(os.environ.get(HOST_ENV), default)


def _configured_cors_origins() -> List[str]:
    """Retorna origens CORS explicitamente permitidas.

    Nenhuma origem é enviada por padrão. O curinga exige uma segunda opção
    explícita para evitar que uma variável de ambiente acidental reabra o
    servidor para qualquer origem.
    """
    configured = os.environ.get(CORS_ORIGINS_ENV) or os.environ.get(CORS_ORIGIN_ENV)
    if not configured:
        return []

    allow_insecure = os.environ.get(ALLOW_INSECURE_CORS_ENV) == "1"
    origins = []
    for origin in configured.split(","):
        normalized = origin.strip()
        if not normalized:
            continue
        if normalized == "*" and not allow_insecure:
            logger.warning(
                "CORS curinga ignorado; defina %s=1 somente em uma configuração "
                "explicitamente revisada.",
                ALLOW_INSECURE_CORS_ENV,
            )
            continue
        origins.append(normalized)
    return origins


def _configured_context_tokens() -> int:
    """Resolve o contexto total compartilhado com os wrappers LiteRT-LM."""
    raw_value = os.environ.get(CONTEXT_TOKENS_ENV)
    if raw_value is None:
        raw_value = os.environ.get(LEGACY_CONTEXT_TOKENS_ENV)
    try:
        configured = int(raw_value) if raw_value is not None else DEFAULT_CONTEXT_TOKENS
    except (TypeError, ValueError):
        return DEFAULT_CONTEXT_TOKENS
    return configured if configured > 0 else DEFAULT_CONTEXT_TOKENS


def _models_endpoint(base_url: Optional[str], port: int) -> str:
    """Monta o endpoint de readiness sem descartar uma URL configurada."""
    if base_url:
        return f"{base_url.rstrip('/')}/models"
    return f"{_local_base_url(_configured_host(), port)}/models"

# ── Catálogo de modelos locais curado ──────────────────────────────────────

MODELS: Dict[str, Dict[str, Any]] = {
    "litert-community/gemma-4-E2B-it-litert-lm": {
        "name": "Gemma 4 E2B (2B)",
        "provider": PROVIDER_ID,
        "description": "Gemma 4 2B parâmetros, instrução-tuned, MTP",
        "size_gb": 2.4,
        "backend": "cpu",
        "tier": "fast",
        "context": 20480,
        "task_types": ["fast", "local", "writing"],
    },
    "litert-community/gemma-4-E4B-it-litert-lm": {
        "name": "Gemma 4 E4B (4B)",
        "provider": PROVIDER_ID,
        "description": "Gemma 4 4B parâmetros, instrução-tuned",
        "size_gb": 3.4,
        "backend": "cpu",
        "tier": "standard",
        "context": 20480,
        "task_types": ["fast", "local", "writing", "reasoning"],
    },
    "litert-community/gemma-4-12B-it-litert-lm": {
        "name": "Gemma 4 12B IT",
        "provider": PROVIDER_ID,
        "description": "Gemma 4 12B parâmetros, instrução-tuned",
        "size_gb": 6.1,
        "backend": "cpu",
        "tier": "premium",
        "context": 20480,
        "task_types": ["local", "reasoning", "coding", "writing"],
    },
    "litert-community/Qwen3-0.6B": {
        "name": "Qwen3 0.6B",
        "provider": PROVIDER_ID,
        "description": "Qwen3 0.6B parâmetros — modelo leve para testes",
        "size_gb": 0.58,
        "backend": "cpu",
        "tier": "fast",
        "context": 20480,
        "task_types": ["fast", "local"],
    },
}

# IDs publicados por ``opencode.json`` e por este catálogo. O roteador pode
# manter compatibilidade com nomes históricos, mas nunca deve devolvê-los como
# modelo selecionado.
CANONICAL_MODEL_IDS = frozenset(MODELS)

# Compatibilidade com as fachadas anteriores do ecossistema. Todos os valores
# precisam permanecer no catálogo acima; aliases não são uma segunda fonte de
# modelos anunciados.
MODEL_ALIASES: Dict[str, str] = {
    # IDs usados pela integração legada ``integrations.litert_lm``.
    "gemma-4-E2B-it": "litert-community/gemma-4-E2B-it-litert-lm",
    "gemma-4-E4B-it": "litert-community/gemma-4-E4B-it-litert-lm",
    "gemma-4-9B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "gemma-4-12B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "gemma-3-1B-it": "litert-community/Qwen3-0.6B",
    "gemma-3-4B-it": "litert-community/gemma-4-E4B-it-litert-lm",
    "gemma-3-12B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "gemma-3-27B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "gemma-2-2B-it": "litert-community/gemma-4-E2B-it-litert-lm",
    "gemma-2-9B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "gemma-2-27B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "llama-4-17B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "llama-3-8B-it": "litert-community/gemma-4-E4B-it-litert-lm",
    "llama-3-70B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "phi-4-14B-it": "litert-community/gemma-4-12B-it-litert-lm",
    "qwen-2.5-7B-it": "litert-community/Qwen3-0.6B",
    "qwen-2.5-32B-it": "litert-community/Qwen3-0.6B",
    "qwen-3-4B-it": "litert-community/Qwen3-0.6B",
    "qwen-3-8B-it": "litert-community/Qwen3-0.6B",
    "qwen-3-30B-it": "litert-community/Qwen3-0.6B",
    "Qwen3-0.6B": "litert-community/Qwen3-0.6B",
    "qwen-3-0.6B": "litert-community/Qwen3-0.6B",
    "qwen3-0.6b": "litert-community/Qwen3-0.6B",
    # Formas curtas e com prefixo usadas por servidores/fachadas anteriores.
    "gemma-4-E2B-it-litert-lm": "litert-community/gemma-4-E2B-it-litert-lm",
    "gemma-4-E4B-it-litert-lm": "litert-community/gemma-4-E4B-it-litert-lm",
    "gemma-4-12B-it-litert-lm": "litert-community/gemma-4-12B-it-litert-lm",
    "litert-community/gemma-4-E2B-it": "litert-community/gemma-4-E2B-it-litert-lm",
    "litert-community/gemma-4-E4B-it": "litert-community/gemma-4-E4B-it-litert-lm",
    "litert-community/gemma-4-12B-it": "litert-community/gemma-4-12B-it-litert-lm",
}


def canonical_model_id(model_id: str) -> str:
    """Normaliza um ID LiteRT para um ID canônico anunciado.

    IDs desconhecidos são devolvidos sem alteração (exceto pelo prefixo de
    provider), permitindo que a camada chamadora produza seu erro de validação
    sem transformar um typo em um modelo válido arbitrário.
    """
    if not isinstance(model_id, str):
        raise TypeError("model_id deve ser uma string")

    normalized = model_id.strip()
    provider_prefix = f"{PROVIDER_ID}/"
    if normalized.startswith(provider_prefix):
        normalized = normalized[len(provider_prefix):]
    if normalized in CANONICAL_MODEL_IDS:
        return normalized
    return MODEL_ALIASES.get(normalized, normalized)


def is_canonical_model_id(model_id: str) -> bool:
    """Indica se ``model_id`` é um dos quatro IDs publicados pelo provider."""
    return canonical_model_id(model_id) in CANONICAL_MODEL_IDS


_BEARER_RE = re.compile(
    r"(?i)(\bauthorization\b\s*:?\s*bearer\s+)([^\s,;]+)"
)
_SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)(\b(?:authorization|api[_-]?key|access[_-]?token|client[_-]?secret|token|password|passwd|secret)\b\s*[=:]\s*)([^\s,;\"']+)"
)
_URL_SENSITIVE_QUERY_RE = re.compile(
    r"(?i)(\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd|secret|token)\b\s*=\s*)([^&#\s]+)"
)
_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def redact_url(value: str) -> str:
    """Redige usuário/senha e parâmetros sensíveis de uma URL."""
    try:
        raw_value = str(value)
        parsed = urlsplit(raw_value)
        if not parsed.scheme or not parsed.netloc:
            return _SENSITIVE_ASSIGNMENT_RE.sub(
                r"\1***REDACTED***",
                _URL_SENSITIVE_QUERY_RE.sub(r"\1***REDACTED***", raw_value),
            )

        hostname = parsed.hostname or ""
        if ":" in hostname and not hostname.startswith("["):
            host = f"[{hostname}]"
        else:
            host = hostname
        try:
            port = f":{parsed.port}" if parsed.port is not None else ""
        except ValueError:
            port = ""
        # O usuário também é omitido: em endpoints de API ele pode ser um
        # identificador de cliente ou parte da própria credencial.
        credentials = ""
        query = _URL_SENSITIVE_QUERY_RE.sub(
            r"\1***REDACTED***", parsed.query
        )
        fragment = _URL_SENSITIVE_QUERY_RE.sub(
            r"\1***REDACTED***", parsed.fragment
        )
        return urlunsplit(
            (parsed.scheme, f"{credentials}{host}{port}", parsed.path, query, fragment)
        )
    except (TypeError, ValueError):
        return "<REDACTED_URL>"


def redact_exception(value: object) -> str:
    """Redige credenciais de mensagens de erro antes de serializá-las."""
    text = str(value)
    text = _URL_RE.sub(lambda match: redact_url(match.group(0)), text)
    text = _BEARER_RE.sub(r"\1***REDACTED***", text)
    return _SENSITIVE_ASSIGNMENT_RE.sub(r"\1***REDACTED***", text)

# ── Estado do servidor ──────────────────────────────────────────────────────

_server_process: Optional[subprocess.Popen] = None
_server_ready: bool = False
_current_model: Optional[str] = None


# ── LiteRTLMProvider ───────────────────────────────────────────────────────


class LiteRTLMProvider:
    """Provider de inferência on-device via LiteRT-LM.

    Gerencia o ciclo de vida do servidor litert-lm e expõe
    interface compatível com o ModelRouter do ecossistema.
    """

    def __init__(self, base_url: Optional[str] = None, auto_start: bool = True):
        self.base_url = _configured_base_url(base_url)
        self.auto_start = auto_start
        if auto_start:
            self._ensure_server()

    # ── Gestão do servidor ──────────────────────────────────────────────────

    @staticmethod
    def is_server_running(
        base_url: Optional[str] = None,
        port: int = LITERT_SERVE_PORT,
    ) -> bool:
        """Verifica readiness usando ``base_url`` quando fornecido."""
        try:
            readiness_base_url = base_url or _READINESS_BASE_URL.get()
            req = urllib_request.Request(
                _models_endpoint(readiness_base_url, port)
            )
            with urllib_request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                return "data" in data
        except (URLError, ConnectionRefusedError, OSError, json.JSONDecodeError):
            return False

    @staticmethod
    def start_server(port: int = LITERT_SERVE_PORT,
                     host: str = LITERT_SERVE_HOST,
                     timeout: int = SERVER_START_TIMEOUT,
                     base_url: Optional[str] = None) -> bool:
        """Solicita o daemon ao supervisor canônico da SPEC-935-R212."""
        global _server_process, _server_ready

        if _server_ready:
            return True

        readiness_base_url = base_url or _READINESS_BASE_URL.get()
        if LiteRTLMProvider.is_server_running(
            base_url=readiness_base_url,
            port=port,
        ):
            _server_ready = True
            logger.info("Servidor litert-lm já está rodando em :%d", port)
            return True

        serve_host = _configured_host() if host == LITERT_SERVE_HOST else _validated_local_host(host)
        if serve_host not in {SUPERVISOR_HOST, "localhost"} or port != SUPERVISOR_PORT:
            raise ValueError(
                "O supervisor LiteRT-LM aceita somente 127.0.0.1:9379."
            )

        # Uma URL remota explicitamente injetada é responsabilidade do chamador;
        # o supervisor nunca abre um daemon para representar outro endpoint.
        if readiness_base_url and not _is_loopback_url(readiness_base_url):
            return LiteRTLMProvider.is_server_running(
                base_url=readiness_base_url,
                port=port,
            )

        logger.info("Solicitando LiteRT-LM ao supervisor em %s:%d...", SUPERVISOR_HOST, SUPERVISOR_PORT)
        try:
            configured_timeout = max(float(timeout), 0.001)
            supervisor = LiteRTSupervisor(
                SupervisorConfig(startup_timeout_seconds=configured_timeout),
                process_factory=subprocess.Popen,
                readiness_probe=lambda: LiteRTLMProvider.is_server_running(
                    base_url=readiness_base_url,
                    port=SUPERVISOR_PORT,
                ),
            )
            status = supervisor.ensure(non_blocking=timeout <= 0)
            _server_process = None
            _server_ready = bool(status.ready)
            if status.state is SupervisorState.CIRCUIT_OPEN:
                logger.warning("Circuit breaker LiteRT-LM aberto; start suprimido.")
            return _server_ready
        except Exception as exc:
            logger.error("Supervisor LiteRT-LM indisponível: %s", exc)
            return False

    @staticmethod
    def stop_server() -> None:
        """Solicita parada segura do PID conhecido pelo supervisor."""
        global _server_process, _server_ready
        try:
            LiteRTSupervisor().stop()
        except Exception as exc:
            logger.warning("Não foi possível parar LiteRT-LM pelo supervisor: %s", exc)
        _server_process = None
        _server_ready = False
        logger.info("Servidor litert-lm parado.")

    def _ensure_server(self) -> None:
        """Garante que o servidor está rodando."""
        if not self.auto_start:
            return

        # Mantém a chamada sem argumentos para preservar a API observável e
        # fornece a URL da instância ao readiness real por contexto local.
        token = _READINESS_BASE_URL.set(self.base_url)
        try:
            started = self.start_server()
        finally:
            _READINESS_BASE_URL.reset(token)

        if not started:
            logger.warning(
                "Servidor litert-lm não disponível. "
                "Modelos on-device ficarão indisponíveis."
            )

    # ── Listagem de modelos ────────────────────────────────────────────────

    def list_models(self) -> List[Dict[str, Any]]:
        """Retorna a lista de modelos disponíveis (do servidor + catálogo)."""
        models = []
        try:
            req = urllib_request.Request(f"{self.base_url}/models")
            with urllib_request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                for m in data.get("data", []):
                    model_id = canonical_model_id(m["id"])
                    info = MODELS.get(model_id, {})
                    models.append({
                        "id": model_id,
                        "name": info.get("name", model_id),
                        "provider": PROVIDER_ID,
                        "tier": info.get("tier", "standard"),
                        "size_gb": info.get("size_gb", "?"),
                    })
        except Exception as e:
            logger.debug("Erro ao listar modelos do servidor: %s", e)
            # Fallback: catálogo estático
            for mid, info in MODELS.items():
                models.append({
                    "id": mid,
                    "name": info["name"],
                    "provider": PROVIDER_ID,
                    "tier": info["tier"],
                    "size_gb": info["size_gb"],
                })
        return models

    def server_status(self) -> Dict[str, Any]:
        """Consulta o status sem iniciar o servidor implicitamente."""
        api_key = str(getattr(self, "_api_key", "") or "")
        safe_base_url = redact_url(self.base_url)
        if api_key:
            safe_base_url = safe_base_url.replace(api_key, "***REDACTED***")
        try:
            req = urllib_request.Request(f"{self.base_url}/models")
            with urllib_request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
            models = data.get("data", [])
            model_names = [
                canonical_model_id(model.get("id") or "")
                for model in models
            ]
            if api_key:
                model_names = [
                    name.replace(api_key, "***REDACTED***")
                    for name in model_names
                ]
            return {
                "online": True,
                "base_url": safe_base_url,
                "models_served": len(models),
                "model_names": model_names,
            }
        except Exception as exc:
            safe_error = redact_exception(exc)
            if api_key:
                safe_error = safe_error.replace(api_key, "***REDACTED***")
            return {
                "online": False,
                "base_url": safe_base_url,
                "error": safe_error,
            }

    def status(self) -> Dict[str, Any]:
        """Alias compatível para ``server_status``."""
        return self.server_status()

    # ── Inferência ─────────────────────────────────────────────────────────

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Envia uma requisição de chat para o modelo on-device.

        Args:
            messages: Lista de mensagens no formato {"role": ..., "content": ...}
            model: ID do modelo (default: gemma-4-E2B-it-litert-lm)
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura de amostragem
            stream: Se True, retorna generator (não implementado nesta versão)

        Returns:
            Dict com a resposta no formato OpenAI ChatCompletion
        """
        if self.auto_start:
            self._ensure_server()

        model_id = canonical_model_id(model or DEFAULT_MODEL)
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }

        req = urllib_request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib_request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read())
                return result
        except URLError as e:
            logger.error("Erro na requisição ao litert-lm: %s", e)
            return {
                "error": f"Falha ao contactar servidor litert-lm: {e.reason}",
                "model": model_id,
            }


# ── Helpers para uso externo ────────────────────────────────────────────────

def get_provider() -> LiteRTLMProvider:
    """Retorna uma instância singleton do provider."""
    return LiteRTLMProvider()


def list_available_models() -> List[Dict[str, Any]]:
    """Retorna a lista de modelos disponíveis."""
    return get_provider().list_models()


# ── CLI de diagnóstico ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    provider = LiteRTLMProvider(auto_start=True)

    if "--stop" in sys.argv:
        provider.stop_server()
        print("Servidor litert-lm parado.")
        sys.exit(0)

    models = provider.list_models()
    print(f"Modelos LiteRT-LM disponíveis ({len(models)}):")
    for m in models:
        print(f"  {m['id']} — {m['name']} ({m['size_gb']}GB, {m['tier']})")

    if len(sys.argv) > 1 and sys.argv[1] not in ("--stop",):
        prompt = " ".join(sys.argv[1:])
        print(f"\nPrompt: {prompt}")
        result = provider.complete(
            messages=[{"role": "user", "content": prompt}],
            model=DEFAULT_MODEL,
            max_tokens=256,
        )
        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            content = result["choices"][0]["message"]["content"]
            print(f"Resposta: {content}")
