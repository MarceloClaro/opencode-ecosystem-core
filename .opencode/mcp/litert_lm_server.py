#!/usr/bin/env python3
"""
MCP Server — LiteRT-LM (Gemma 4 on-device)
============================================
Expõe modelos on-device do LiteRT-LM como ferramentas MCP
para uso dentro do OpenCode, Claude Code e qualquer cliente MCP.

Ferramentas:
  - litert_lm_chat:    Envia mensagem para um modelo on-device
  - litert_lm_models:  Lista modelos disponíveis
  - litert_lm_status:  Status do servidor e recursos

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import subprocess
import sys
import time
from collections.abc import Mapping
from ipaddress import ip_address
from pathlib import Path
from typing import Any, Optional

from urllib import request as urllib_request
from urllib.parse import urlsplit

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

try:
    from mcp.types import CallToolResult
except ImportError:
    class CallToolResult(list[TextContent]):
        """Fallback mínimo para versões antigas do SDK MCP.

        O SDK atual fornece ``CallToolResult`` e preserva ``isError`` no
        transporte. A classe local mantém o mesmo contrato observável para
        ambientes que ainda não expõem esse tipo, sem substituir o SDK
        instalado.
        """

        def __init__(
            self,
            *,
            content: list[TextContent],
            isError: bool = False,
            **extra_data: Any,
        ) -> None:
            super().__init__(content)
            self.content = list(content)
            self.isError = isError
            for key, value in extra_data.items():
                setattr(self, key, value)

# ── Configuração ────────────────────────────────────────────────────────────

LITERT_PORT = 9379
SERVER_START_TIMEOUT = 120
HOST_ENV = "LITERT_LM_HOST"
BASE_URL_ENV = "LITERT_LM_BASE_URL"
ALLOW_REMOTE_ENV = "LITERT_LM_ALLOW_REMOTE"
CONTEXT_TOKENS_ENV = "LITERT_LM_CONTEXT_TOKENS"
LEGACY_CONTEXT_TOKENS_ENV = "LITERT_LM_MAX_TOKENS"
CORS_ORIGIN_ENV = "LITERT_LM_CORS_ORIGIN"
CORS_ORIGINS_ENV = "LITERT_LM_CORS_ORIGINS"
ALLOW_INSECURE_CORS_ENV = "LITERT_LM_ALLOW_INSECURE_CORS"
READ_ONLY_TIMEOUT = 1.0
DEFAULT_LOCAL_HOST = "127.0.0.1"
DEFAULT_CONTEXT_TOKENS = 20_480
CANONICAL_MODEL_IDS = (
    "litert-community/gemma-4-E2B-it-litert-lm",
    "litert-community/gemma-4-E4B-it-litert-lm",
    "litert-community/gemma-4-12B-it-litert-lm",
    "litert-community/Qwen3-0.6B",
)
DEFAULT_MODEL_ID = CANONICAL_MODEL_IDS[0]
MAX_CHAT_MESSAGES = 64
MAX_MESSAGE_CONTENT_BYTES = 64 * 1024
MAX_COMPLETION_TOKENS = 2048
DEFAULT_COMPLETION_TOKENS = MAX_COMPLETION_TOKENS
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR_PATH = PROJECT_ROOT / "integrations" / "litert_lm_supervisor.py"
SUPERVISOR_COMMAND = (
    sys.executable or "python3",
    str(SUPERVISOR_PATH),
    "ensure",
    "--non-blocking",
)


class _McpHttpError(RuntimeError):
    """Indica resposta HTTP que não representa sucesso operacional."""


class _McpPayloadError(ValueError):
    """Indica JSON ausente, inválido ou incompatível com o contrato."""


def _validated_local_host(configured: Optional[str]) -> str:
    """Aceita somente hosts de loopback para o daemon local."""
    if configured is None or not configured.strip():
        return DEFAULT_LOCAL_HOST

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
    LITERT_HOST = _validated_local_host(os.environ.get(HOST_ENV))
except ValueError:
    # Um override inseguro não pode tornar o módulo importável com bind global.
    LITERT_HOST = DEFAULT_LOCAL_HOST
LITERT_BASE = f"http://{LITERT_HOST}:{LITERT_PORT}/v1"

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("litert-lm-mcp")


def _configured_host() -> str:
    """Obtém o host de bind, mantendo o loopback como fallback seguro."""
    return _validated_local_host(os.environ.get(HOST_ENV))


def _is_loopback_url(value: str) -> bool:
    """Verifica se uma URL HTTP(S) aponta para um host de loopback."""
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


def _configured_base_url() -> str:
    """Obtém a URL do backend sem aceitar remoto por configuração implícita."""
    configured = os.environ.get(BASE_URL_ENV)
    if configured and configured.strip():
        candidate = configured.strip().rstrip("/")
        if _is_loopback_url(candidate) or os.environ.get(ALLOW_REMOTE_ENV) == "1":
            return candidate
        logger.warning(
            "%s remoto ignorado por padrão; usando endpoint de loopback",
            BASE_URL_ENV,
        )
    if os.environ.get(HOST_ENV):
        return f"http://{_configured_host()}:{LITERT_PORT}/v1"
    return LITERT_BASE.rstrip("/")


def _configured_context_tokens() -> int:
    """Resolve o contexto total, preservando o nome legado do CLI nativo."""
    raw_value = os.environ.get(CONTEXT_TOKENS_ENV)
    if raw_value is None:
        raw_value = os.environ.get(LEGACY_CONTEXT_TOKENS_ENV)
    if raw_value is None:
        return DEFAULT_CONTEXT_TOKENS
    try:
        configured = int(raw_value)
    except (TypeError, ValueError):
        return DEFAULT_CONTEXT_TOKENS
    return configured if configured > 0 else DEFAULT_CONTEXT_TOKENS


def _configured_cors_origins() -> list[str]:
    """Retorna somente origens CORS explicitamente configuradas."""
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
                "CORS curinga ignorado; defina %s=1 somente após revisão.",
                ALLOW_INSECURE_CORS_ENV,
            )
            continue
        origins.append(normalized)
    return origins


# ── Helpers de resultado e validação ─────────────────────────────────────────


def _text_content(text: str) -> list[TextContent]:
    """Cria conteúdo textual no formato aceito pelo SDK MCP."""
    return [TextContent(type="text", text=text)]


def _mcp_error(message: str) -> CallToolResult:
    """Retorna um erro de ferramenta real, preservando ``isError=true``."""
    return CallToolResult(content=_text_content(message), isError=True)


def _offline_text(tool: str, error: Exception) -> CallToolResult:
    """Sinaliza indisponibilidade do backend como erro MCP real."""
    logger.debug("%s offline: %s", tool, error, exc_info=True)
    return CallToolResult(
        content=_text_content(json.dumps({
            "server": "offline",
            "port": LITERT_PORT,
            "error": "Servidor LiteRT-LM indisponível.",
        }, ensure_ascii=False)),
        isError=True,
    )


def _response_status_code(response: Any) -> Optional[int]:
    """Obtém um status HTTP sem exigir esse atributo nos doubles dos testes."""
    status_code = getattr(response, "status_code", None)
    if isinstance(status_code, bool) or not isinstance(status_code, int):
        return None
    return status_code


def _decode_http_json(response: Any, operation: str) -> dict[str, Any]:
    """Valida status HTTP e materializa um objeto JSON de resposta."""
    status_code = _response_status_code(response)
    if status_code is not None and not 200 <= status_code < 300:
        raise _McpHttpError(f"{operation} retornou HTTP {status_code}.")

    raise_for_status = getattr(response, "raise_for_status", None)
    if callable(raise_for_status):
        try:
            raise_for_status()
        except Exception as exc:
            raise _McpHttpError(
                f"{operation} retornou uma resposta HTTP inválida."
            ) from exc

    try:
        payload = response.json()
    except Exception as exc:
        raise _McpPayloadError(f"{operation} retornou JSON inválido.") from exc

    if not isinstance(payload, Mapping):
        raise _McpPayloadError(
            f"{operation} retornou um payload JSON incompatível."
        )
    return dict(payload)


def _model_ids(payload: Mapping[str, Any], operation: str) -> list[str]:
    """Valida o envelope ``/models`` e retorna somente IDs textuais."""
    raw_models = payload.get("data")
    if not isinstance(raw_models, list):
        raise _McpPayloadError(
            f"{operation} retornou um campo 'data' inválido."
        )

    model_ids: list[str] = []
    for index, model in enumerate(raw_models):
        if not isinstance(model, Mapping):
            raise _McpPayloadError(
                f"{operation} retornou o modelo {index} em formato inválido."
            )
        model_id = model.get("id")
        if not isinstance(model_id, str) or not model_id.strip():
            raise _McpPayloadError(
                f"{operation} retornou um modelo sem ID textual."
            )
        model_ids.append(model_id)
    return model_ids


def _validate_chat_arguments(
    arguments: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], str, int, float | int]:
    """Valida argumentos quando o handler é chamado diretamente ou via SDK."""
    messages = arguments.get("messages")
    if not isinstance(messages, list) or not messages:
        raise _McpPayloadError(
            "Payload inválido: 'messages' deve ser uma lista não vazia."
        )
    if len(messages) > MAX_CHAT_MESSAGES:
        raise _McpPayloadError(
            f"Payload inválido: 'messages' aceita no máximo {MAX_CHAT_MESSAGES} itens."
        )

    normalized_messages: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        if not isinstance(message, Mapping):
            raise _McpPayloadError(
                f"Payload inválido: mensagem {index} deve ser um objeto."
            )
        role = message.get("role")
        content = message.get("content")
        if not isinstance(role, str) or role not in {
            "system",
            "user",
            "assistant",
        }:
            raise _McpPayloadError(
                f"Payload inválido: role ausente ou inválido na mensagem {index}."
            )
        if not isinstance(content, str):
            raise _McpPayloadError(
                f"Payload inválido: content inválido na mensagem {index}."
            )
        try:
            content_size = len(content.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise _McpPayloadError(
                f"Payload inválido: content da mensagem {index} não é UTF-8 válido."
            ) from exc
        if content_size > MAX_MESSAGE_CONTENT_BYTES:
            raise _McpPayloadError(
                "Payload inválido: content da mensagem "
                f"{index} excede {MAX_MESSAGE_CONTENT_BYTES} bytes UTF-8."
            )
        normalized_messages.append(dict(message))

    model = arguments.get("model", DEFAULT_MODEL_ID)
    if not isinstance(model, str) or model not in CANONICAL_MODEL_IDS:
        raise _McpPayloadError(
            "Payload inválido: 'model' deve ser um dos quatro IDs canônicos."
        )

    for token_field in ("max_tokens", "max_completion_tokens"):
        if token_field not in arguments:
            continue
        token_value = arguments[token_field]
        if (
            isinstance(token_value, bool)
            or not isinstance(token_value, int)
            or not 1 <= token_value <= MAX_COMPLETION_TOKENS
        ):
            raise _McpPayloadError(
                f"Payload inválido: '{token_field}' deve ser inteiro entre "
                f"1 e {MAX_COMPLETION_TOKENS}."
            )

    if "max_completion_tokens" in arguments:
        max_completion_tokens = arguments["max_completion_tokens"]
    elif "max_tokens" in arguments:
        max_completion_tokens = arguments["max_tokens"]
    else:
        max_completion_tokens = DEFAULT_COMPLETION_TOKENS

    temperature = arguments.get("temperature", 0.7)
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise _McpPayloadError(
            "Payload inválido: 'temperature' deve ser um número finito."
        )
    try:
        numeric_temperature = float(temperature)
        if not math.isfinite(numeric_temperature):
            raise _McpPayloadError(
                "Payload inválido: 'temperature' deve ser um número finito."
            )
    except (OverflowError, ValueError) as exc:
        raise _McpPayloadError(
            "Payload inválido: 'temperature' deve ser um número finito."
        ) from exc
    if not MIN_TEMPERATURE <= numeric_temperature <= MAX_TEMPERATURE:
        raise _McpPayloadError(
            "Payload inválido: 'temperature' deve estar entre 0 e 2."
        )

    return normalized_messages, model, max_completion_tokens, temperature


def _chat_content(payload: Mapping[str, Any]) -> tuple[str, Mapping[str, Any]]:
    """Valida a resposta OpenAI-compatible antes de extrair seu conteúdo."""
    if "error" in payload:
        raise _McpPayloadError("Backend LiteRT-LM retornou um erro.")

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise _McpPayloadError(
            "Resposta inválida: 'choices' deve conter uma completion."
        )
    first_choice = choices[0]
    if not isinstance(first_choice, Mapping):
        raise _McpPayloadError("Resposta inválida: choice não é um objeto.")
    message = first_choice.get("message")
    if not isinstance(message, Mapping):
        raise _McpPayloadError("Resposta inválida: message ausente na completion.")
    content = message.get("content")
    if not isinstance(content, str):
        raise _McpPayloadError("Resposta inválida: content não é texto.")

    usage = payload.get("usage") or {}
    if not isinstance(usage, Mapping):
        raise _McpPayloadError("Resposta inválida: usage não é um objeto.")
    return content, usage


# ── Helpers síncronos para verificação rápida (evitam thread overhead) ─────


def _check_server_sync() -> bool:
    """Verificação rápida síncrona se o servidor responde."""
    try:
        req = urllib_request.Request(f"{_configured_base_url()}/models")
        with urllib_request.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read())
            if not isinstance(payload, Mapping):
                return False
            _model_ids(payload, "Verificação de readiness")
            return True
    except Exception:
        return False


async def _ensure_server() -> bool:
    """Solicita o supervisor canônico e aguarda somente quando o chat exige."""
    base_url = _configured_base_url()
    # Tenta conectar diretamente com httpx (async)
    try:
        async with httpx.AsyncClient(
            base_url=base_url, timeout=httpx.Timeout(3.0)
        ) as client:
            resp = await client.get("/models")
            payload = _decode_http_json(resp, "Verificação de readiness")
            _model_ids(payload, "Verificação de readiness")
            if "data" in payload:
                return True
    except Exception:
        pass

    logger.info("Solicitando bootstrap supervisionado na porta %d...", LITERT_PORT)
    if not await _request_supervisor_bootstrap():
        return False

    started_at = time.monotonic()
    while time.monotonic() - started_at < SERVER_START_TIMEOUT:
        await asyncio.sleep(2)
        try:
            async with httpx.AsyncClient(
                base_url=base_url, timeout=httpx.Timeout(2.0)
            ) as client:
                resp = await client.get("/models")
                payload = _decode_http_json(resp, "Verificação de readiness")
                _model_ids(payload, "Verificação de readiness")
                if "data" in payload:
                    logger.info("Servidor litert-lm pronto.")
                    return True
        except Exception:
            pass
    logger.error("Servidor litert-lm não iniciou em %ds", SERVER_START_TIMEOUT)
    return False


def _supervisor_environment() -> dict[str, str]:
    """Cria o contexto mínimo necessário para executar a CLI do supervisor."""

    allowed_names = {
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "PATH",
        "TMPDIR",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_RUNTIME_DIR",
        "LITERT_LM_MODELS_DIR",
        "LITERT_LM_CONTEXT_TOKENS",
        "LITERT_LM_MAX_TOKENS",
    }
    environment = {
        name: value
        for name in allowed_names
        if (value := os.environ.get(name)) is not None
    }
    environment.setdefault("PATH", os.defpath)
    return environment


def _observe_background_task(task: asyncio.Task[Any]) -> None:
    """Consome falhas de tarefas fire-and-forget sem escrever no stdout MCP."""

    if task.cancelled():
        return
    try:
        task.exception()
    except (asyncio.CancelledError, Exception):
        logger.debug("Falha na tarefa de bootstrap LiteRT-LM", exc_info=True)


async def _reap_supervisor_request(process: asyncio.subprocess.Process) -> None:
    """Coleta somente a CLI curta; o daemon permanece sob o supervisor."""

    await process.wait()


async def _request_supervisor_bootstrap() -> bool:
    """Dispara ``ensure --non-blocking`` sem aguardar readiness do daemon."""

    try:
        process = await asyncio.create_subprocess_exec(
            *SUPERVISOR_COMMAND,
            cwd=str(PROJECT_ROOT),
            env=_supervisor_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except (OSError, RuntimeError):
        logger.debug("Supervisor LiteRT-LM indisponível", exc_info=True)
        return False

    reap_task = asyncio.create_task(_reap_supervisor_request(process))
    reap_task.add_done_callback(_observe_background_task)
    return True


# ── MCP Server ──────────────────────────────────────────────────────────────

app = Server("litert-lm")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Registra as ferramentas MCP disponíveis."""
    return [
        Tool(
            name="litert_lm_chat",
            description=(
                "Envia mensagem para modelo on-device "
                "(Gemma 4 / Qwen3) via LiteRT-LM"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": MAX_CHAT_MESSAGES,
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["system", "user", "assistant"],
                                },
                                "content": {
                                    "type": "string",
                                    "maxLength": MAX_MESSAGE_CONTENT_BYTES,
                                    "description": (
                                        "Conteúdo limitado a 64 KiB em UTF-8"
                                    ),
                                },
                            },
                            "required": ["role", "content"],
                        },
                        "description": "Lista de mensagens no formato chat",
                    },
                    "model": {
                        "type": "string",
                        "enum": list(CANONICAL_MODEL_IDS),
                        "default": DEFAULT_MODEL_ID,
                        "description": "ID canônico do modelo LiteRT-LM",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": MAX_COMPLETION_TOKENS,
                        "description": "Campo legado para o limite de saída",
                    },
                    "max_completion_tokens": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": MAX_COMPLETION_TOKENS,
                        "default": DEFAULT_COMPLETION_TOKENS,
                        "description": "Maximo de tokens na resposta",
                    },
                    "temperature": {
                        "type": "number",
                        "minimum": MIN_TEMPERATURE,
                        "maximum": MAX_TEMPERATURE,
                        "default": 0.7,
                        "description": "Temperatura de amostragem",
                    },
                },
                "required": ["messages"],
            },
        ),
        Tool(
            name="litert_lm_models",
            description="Lista modelos disponiveis no servidor LiteRT-LM",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="litert_lm_status",
            description="Status do servidor LiteRT-LM e modelos carregados",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict,
) -> CallToolResult | list[TextContent]:
    """Executa a ferramenta MCP solicitada."""
    supported_tools = {
        "litert_lm_status",
        "litert_lm_models",
        "litert_lm_chat",
    }
    if not isinstance(name, str) or name not in supported_tools:
        return _mcp_error(f"Ferramenta desconhecida: {name}")
    if not isinstance(arguments, Mapping):
        return _mcp_error("Payload inválido: argumentos devem ser um objeto.")

    # ── litert_lm_status ────────────────────────────────────────────────
    if name == "litert_lm_status":
        try:
            async with httpx.AsyncClient(
                base_url=_configured_base_url(),
                timeout=httpx.Timeout(READ_ONLY_TIMEOUT),
            ) as client:
                resp = await client.get("/models")
                data = _decode_http_json(resp, "Consulta de status")
                models = _model_ids(data, "Consulta de status")
                return _text_content(json.dumps({
                    "server": "online",
                    "port": LITERT_PORT,
                    "models_count": len(models),
                    "models": models,
                }, indent=2))
        except (httpx.RequestError, OSError, TimeoutError) as exc:
            return _offline_text("litert_lm_status", exc)
        except (_McpHttpError, _McpPayloadError) as exc:
            logger.debug("Falha de status: %s", exc, exc_info=True)
            return _mcp_error(str(exc))
        except Exception as exc:
            logger.debug("Falha inesperada de status: %s", exc, exc_info=True)
            return _mcp_error(
                f"Falha na consulta de status: {type(exc).__name__}."
            )

    # ── litert_lm_models ────────────────────────────────────────────────
    if name == "litert_lm_models":
        try:
            async with httpx.AsyncClient(
                base_url=_configured_base_url(),
                timeout=httpx.Timeout(READ_ONLY_TIMEOUT),
            ) as client:
                resp = await client.get("/models")
                data = _decode_http_json(resp, "Consulta de modelos")
                models = _model_ids(data, "Consulta de modelos")
                if not models:
                    return _text_content("Nenhum modelo encontrado.")
                lines = ["**Modelos LiteRT-LM disponiveis:**"]
                for model_id in models:
                    lines.append(f"- {model_id}")
                return _text_content("\n".join(lines))
        except (httpx.RequestError, OSError, TimeoutError) as exc:
            return _offline_text("litert_lm_models", exc)
        except (_McpHttpError, _McpPayloadError) as exc:
            logger.debug("Falha de modelos: %s", exc, exc_info=True)
            return _mcp_error(str(exc))
        except Exception as exc:
            logger.debug("Falha inesperada de modelos: %s", exc, exc_info=True)
            return _mcp_error(
                f"Falha na consulta de modelos: {type(exc).__name__}."
            )

    # ── litert_lm_chat ──────────────────────────────────────────────────
    if name == "litert_lm_chat":
        try:
            messages, model, max_completion_tokens, temperature = (
                _validate_chat_arguments(arguments)
            )
        except _McpPayloadError as exc:
            return _mcp_error(str(exc))

        # Somente chat pode iniciar o daemon e aguardar o cold start do modelo.
        try:
            if not await _ensure_server():
                return _mcp_error(
                    "Servidor LiteRT-LM indisponível após a verificação de readiness."
                )
        except Exception as exc:
            logger.debug("Falha de readiness: %s", exc, exc_info=True)
            return _mcp_error(
                "Falha na verificação de readiness do servidor LiteRT-LM."
            )

        payload = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
            "temperature": temperature,
        }
        try:
            async with httpx.AsyncClient(
                base_url=_configured_base_url(),
                timeout=httpx.Timeout(300.0, connect=5.0),
            ) as client:
                resp = await client.post("/chat/completions", json=payload)
                result = _decode_http_json(resp, "Chat LiteRT-LM")

            content, usage = _chat_content(result)
            meta = ""
            if usage:
                try:
                    usage_json = json.dumps(usage)
                except (TypeError, ValueError) as exc:
                    raise _McpPayloadError(
                        "Resposta inválida: usage não é serializável."
                    ) from exc
                meta = f"\n\n---\nModelo: {model} | Tokens: {usage_json}"
            return _text_content(content + meta)

        except (_McpHttpError, _McpPayloadError) as exc:
            logger.debug("Falha de payload do chat: %s", exc, exc_info=True)
            return _mcp_error(str(exc))
        except (httpx.RequestError, OSError, TimeoutError) as exc:
            logger.debug("Falha HTTP do chat: %s", exc, exc_info=True)
            return _mcp_error(
                f"Falha HTTP no chat LiteRT-LM: {type(exc).__name__}."
            )
        except Exception as exc:
            logger.debug("Falha inesperada do chat: %s", exc, exc_info=True)
            return _mcp_error(
                f"Falha no chat LiteRT-LM: {type(exc).__name__}."
            )

    return _mcp_error(f"Ferramenta desconhecida: {name}")


# ── Entrypoint ──────────────────────────────────────────────────────────────


async def main():
    logger.info("Iniciando MCP Server LiteRT-LM...")
    bootstrap_task = asyncio.create_task(_request_supervisor_bootstrap())
    bootstrap_task.add_done_callback(_observe_background_task)
    # Entrega um turno ao bootstrap, mas nunca aguarda cold start ou readiness.
    await asyncio.sleep(0)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
