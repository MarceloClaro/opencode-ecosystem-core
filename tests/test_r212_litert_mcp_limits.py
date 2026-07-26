# -*- coding: utf-8 -*-
"""Testes RED herméticos de CA27 da SPEC-935-R212 v1.1.

O MCP LiteRT-LM é importado diretamente de seu caminho versionado. Toda rota
externa é substituída por double: os casos inválidos devem retornar
``isError=true`` antes de readiness, HTTP ou criação de processo.
"""

from __future__ import annotations

import asyncio
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest import mock

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_PATH = PROJECT_ROOT / ".opencode" / "mcp" / "litert_lm_server.py"
CANONICAL_MODEL_IDS = (
    "litert-community/gemma-4-E2B-it-litert-lm",
    "litert-community/gemma-4-E4B-it-litert-lm",
    "litert-community/gemma-4-12B-it-litert-lm",
    "litert-community/Qwen3-0.6B",
)
MAX_MESSAGES = 64
MAX_CONTENT_BYTES = 64 * 1024
MAX_OUTPUT_TOKENS = 2048

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def litert_mcp() -> ModuleType:
    """Importa o MCP por caminho sem executar seu entrypoint stdio."""

    # Arrange: aponta para o artefato exato registrado no opencode.json.
    module_name = "_r212_litert_mcp_limits_under_test"
    module_spec = importlib.util.spec_from_file_location(module_name, MCP_PATH)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module

    # Act: executa apenas a carga do módulo; ``main`` permanece inativo.
    module_spec.loader.exec_module(module)

    # Assert: os testes recebem o handler importado do caminho canônico.
    assert Path(module.__file__).resolve() == MCP_PATH.resolve()
    return module


class _FakeChatResponse:
    """Resposta OpenAI-compatible inteiramente local."""

    status_code = 200

    def json(self) -> dict[str, Any]:
        return {
            "choices": [{"message": {"content": "resposta fake"}}],
            "usage": {},
        }

    def raise_for_status(self) -> None:
        return None


class _RecordingAsyncClient:
    """Cliente HTTP fake que registra o payload sem abrir sockets."""

    def __init__(self, requests: list[dict[str, Any]]) -> None:
        self._requests = requests

    async def __aenter__(self) -> "_RecordingAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def post(self, path: str, *, json: dict[str, Any]) -> _FakeChatResponse:
        self._requests.append({"path": path, "json": json})
        return _FakeChatResponse()


@dataclass
class _ExternalSentinels:
    """Pontos observáveis que jamais podem ser alcançados por payload inválido."""

    ensure_server: mock.AsyncMock
    http_client: mock.Mock
    async_spawn: mock.AsyncMock
    popen: mock.Mock


def _valid_arguments(**overrides: Any) -> dict[str, Any]:
    arguments: dict[str, Any] = {
        "messages": [{"role": "user", "content": "Olá"}],
        "model": CANONICAL_MODEL_IDS[0],
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "temperature": 0.7,
    }
    arguments.update(overrides)
    return arguments


def _call_chat(module: ModuleType, arguments: dict[str, Any]) -> Any:
    return asyncio.run(module.call_tool("litert_lm_chat", arguments))


def _is_error(result: Any) -> bool:
    return getattr(result, "isError", False) is True


def _install_successful_backend(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[list[dict[str, Any]], mock.AsyncMock, mock.AsyncMock, mock.Mock]:
    """Instala readiness e HTTP positivos, mantendo todo spawn proibido."""

    requests: list[dict[str, Any]] = []
    ensure_server = mock.AsyncMock(name="ensure_server", return_value=True)
    async_spawn = mock.AsyncMock(
        name="create_subprocess_exec",
        side_effect=AssertionError("um payload válido não deve criar processo no teste"),
    )
    popen = mock.Mock(
        name="Popen",
        side_effect=AssertionError("um payload válido não deve usar Popen no teste"),
    )
    http_client = mock.Mock(
        name="AsyncClient",
        side_effect=lambda *args, **kwargs: _RecordingAsyncClient(requests),
    )
    monkeypatch.setattr(module, "_ensure_server", ensure_server)
    monkeypatch.setattr(module.httpx, "AsyncClient", http_client)
    monkeypatch.setattr(module.asyncio, "create_subprocess_exec", async_spawn)
    monkeypatch.setattr(module.subprocess, "Popen", popen)
    return requests, ensure_server, async_spawn, popen


def _install_invalid_input_sentinels(
    module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> _ExternalSentinels:
    """Mantém efeitos locais e observáveis para provar a ordem da validação."""

    ensure_server = mock.AsyncMock(
        name="ensure_server",
        return_value=True,
    )
    http_client = mock.Mock(
        name="AsyncClient",
        side_effect=lambda *args, **kwargs: _RecordingAsyncClient([]),
    )
    async_spawn = mock.AsyncMock(
        name="create_subprocess_exec",
        side_effect=AssertionError("validação ocorreu depois de spawn assíncrono"),
    )
    popen = mock.Mock(
        name="Popen",
        side_effect=AssertionError("validação ocorreu depois de Popen"),
    )
    monkeypatch.setattr(module, "_ensure_server", ensure_server)
    monkeypatch.setattr(module.httpx, "AsyncClient", http_client)
    monkeypatch.setattr(module.asyncio, "create_subprocess_exec", async_spawn)
    monkeypatch.setattr(module.subprocess, "Popen", popen)
    return _ExternalSentinels(ensure_server, http_client, async_spawn, popen)


def _assert_successful_request(
    result: Any,
    requests: list[dict[str, Any]],
    async_spawn: mock.AsyncMock,
    popen: mock.Mock,
) -> dict[str, Any]:
    assert not _is_error(result)
    assert len(requests) == 1
    assert requests[0]["path"] == "/chat/completions"
    async_spawn.assert_not_awaited()
    popen.assert_not_called()
    return requests[0]["json"]


def _assert_rejected_before_external_calls(
    result: Any,
    sentinels: _ExternalSentinels,
) -> None:
    sentinels.ensure_server.assert_not_awaited()
    sentinels.http_client.assert_not_called()
    sentinels.async_spawn.assert_not_awaited()
    sentinels.popen.assert_not_called()
    assert _is_error(result), "Entrada inválida deve retornar isError=true"


@pytest.mark.parametrize("model_id", CANONICAL_MODEL_IDS)
def test_chat_aceita_exatamente_cada_id_de_modelo_canonico(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    model_id: str,
):
    """CA27 positivo: cada um dos quatro IDs canônicos alcança o HTTP fake."""

    # Arrange: seleciona um ID canônico e instala somente doubles locais.
    arguments = _valid_arguments(model=model_id)
    requests, ensure_server, async_spawn, popen = _install_successful_backend(
        litert_mcp, monkeypatch
    )

    # Act: chama diretamente o handler importado por caminho.
    result = _call_chat(litert_mcp, arguments)

    # Assert: o modelo é aceito sem spawn e preservado no payload de saída.
    payload = _assert_successful_request(result, requests, async_spawn, popen)
    assert payload["model"] == model_id
    ensure_server.assert_awaited_once()


@pytest.mark.parametrize(
    "model_id",
    [
        "gemma-4-E2B-it-litert-lm",
        "litert-community/gemma-4-E2B-it-litert-lm/variante",
        "litert-community/modelo-nao-canonico",
    ],
)
def test_chat_rejeita_id_de_modelo_fora_dos_quatro_canonicos_antes_de_efeitos(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    model_id: str,
):
    """CA27 negativo: alias, sufixo e modelo desconhecido falham fechados."""

    # Arrange: fornece um ID não canônico e arma sentinelas de efeitos externos.
    arguments = _valid_arguments(model=model_id)
    sentinels = _install_invalid_input_sentinels(litert_mcp, monkeypatch)

    # Act: submete a entrada inválida diretamente ao handler.
    result = _call_chat(litert_mcp, arguments)

    # Assert: a rejeição MCP antecede readiness, HTTP e spawn.
    _assert_rejected_before_external_calls(result, sentinels)


def test_chat_aceita_exatamente_sessenta_e_quatro_mensagens(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA27 positivo: o limite inclusivo de mensagens é 64."""

    # Arrange: cria exatamente a fronteira permitida e um backend fake.
    messages = [
        {"role": "user", "content": f"mensagem-{index}"}
        for index in range(MAX_MESSAGES)
    ]
    arguments = _valid_arguments(messages=messages)
    requests, _, async_spawn, popen = _install_successful_backend(
        litert_mcp, monkeypatch
    )

    # Act: envia as 64 mensagens sem usar rede real.
    result = _call_chat(litert_mcp, arguments)

    # Assert: a fronteira é aceita e chega intacta ao HTTP fake.
    payload = _assert_successful_request(result, requests, async_spawn, popen)
    assert payload["messages"] == messages


def test_chat_rejeita_sessenta_e_cinco_mensagens_antes_de_efeitos(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA27 negativo: uma mensagem acima do limite falha antes do backend."""

    # Arrange: cria 65 mensagens e proíbe qualquer efeito externo.
    messages = [
        {"role": "user", "content": f"mensagem-{index}"}
        for index in range(MAX_MESSAGES + 1)
    ]
    arguments = _valid_arguments(messages=messages)
    sentinels = _install_invalid_input_sentinels(litert_mcp, monkeypatch)

    # Act: submete a coleção uma unidade acima do máximo.
    result = _call_chat(litert_mcp, arguments)

    # Assert: o envelope é erro e nenhum readiness/HTTP/spawn foi alcançado.
    _assert_rejected_before_external_calls(result, sentinels)


def test_chat_aceita_conteudo_com_exatos_sessenta_e_quatro_kib_em_utf8(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA27 positivo: 64 KiB por conteúdo é uma fronteira inclusiva em bytes."""

    # Arrange: usa caractere multibyte para distinguir bytes de code points.
    content = "á" * (MAX_CONTENT_BYTES // len("á".encode("utf-8")))
    assert len(content.encode("utf-8")) == MAX_CONTENT_BYTES
    arguments = _valid_arguments(messages=[{"role": "user", "content": content}])
    requests, _, async_spawn, popen = _install_successful_backend(
        litert_mcp, monkeypatch
    )

    # Act: envia o conteúdo exatamente na fronteira ao backend fake.
    result = _call_chat(litert_mcp, arguments)

    # Assert: o conteúdo permitido é preservado sem processo real.
    payload = _assert_successful_request(result, requests, async_spawn, popen)
    assert payload["messages"][0]["content"] == content


def test_chat_rejeita_conteudo_acima_de_sessenta_e_quatro_kib_antes_de_efeitos(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA27 negativo: o tamanho deve ser medido em UTF-8, não em caracteres."""

    # Arrange: acrescenta um byte ASCII à fronteira UTF-8 permitida.
    at_limit = "á" * (MAX_CONTENT_BYTES // len("á".encode("utf-8")))
    content = at_limit + "a"
    assert len(content.encode("utf-8")) == MAX_CONTENT_BYTES + 1
    arguments = _valid_arguments(messages=[{"role": "user", "content": content}])
    sentinels = _install_invalid_input_sentinels(litert_mcp, monkeypatch)

    # Act: submete conteúdo uma unidade acima do máximo em bytes.
    result = _call_chat(litert_mcp, arguments)

    # Assert: a entrada é erro MCP antes de qualquer interação externa.
    _assert_rejected_before_external_calls(result, sentinels)


@pytest.mark.parametrize("token_field", ["max_tokens", "max_completion_tokens"])
def test_chat_aceita_output_de_exatos_2048_tokens_para_ambos_os_campos(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    token_field: str,
):
    """CA27 positivo: o máximo inclusivo vale para o campo atual e o legado."""

    # Arrange: configura somente um alias de saída por execução.
    arguments = _valid_arguments()
    arguments.pop("max_completion_tokens")
    arguments[token_field] = MAX_OUTPUT_TOKENS
    requests, _, async_spawn, popen = _install_successful_backend(
        litert_mcp, monkeypatch
    )

    # Act: envia o valor exatamente no limite permitido.
    result = _call_chat(litert_mcp, arguments)

    # Assert: ambos os aliases normalizam para saída máxima de 2048.
    payload = _assert_successful_request(result, requests, async_spawn, popen)
    assert payload["max_completion_tokens"] == MAX_OUTPUT_TOKENS


def test_chat_sem_output_explicito_adota_default_seguro_de_2048(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA27 positivo: omitir o campo nunca produz default acima do máximo."""

    # Arrange: remove ambos os aliases e instala backend observável local.
    arguments = _valid_arguments()
    arguments.pop("max_completion_tokens")
    requests, _, async_spawn, popen = _install_successful_backend(
        litert_mcp, monkeypatch
    )

    # Act: chama o chat sem limite de saída fornecido pelo cliente.
    result = _call_chat(litert_mcp, arguments)

    # Assert: o payload normalizado permanece limitado a 2048.
    payload = _assert_successful_request(result, requests, async_spawn, popen)
    assert payload["max_completion_tokens"] == MAX_OUTPUT_TOKENS


@pytest.mark.parametrize("token_field", ["max_tokens", "max_completion_tokens"])
def test_chat_rejeita_output_acima_de_2048_antes_de_efeitos(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    token_field: str,
):
    """CA27 negativo: 2049 é inválido nos dois nomes aceitos pela API."""

    # Arrange: excede um alias por vez e arma todos os sentinelas externos.
    arguments = _valid_arguments()
    arguments.pop("max_completion_tokens")
    arguments[token_field] = MAX_OUTPUT_TOKENS + 1
    sentinels = _install_invalid_input_sentinels(litert_mcp, monkeypatch)

    # Act: submete a saída uma unidade acima do teto.
    result = _call_chat(litert_mcp, arguments)

    # Assert: a validação falha fechada antes de readiness/HTTP/spawn.
    _assert_rejected_before_external_calls(result, sentinels)


@pytest.mark.parametrize("temperature", [0, 2])
def test_chat_aceita_temperaturas_nas_duas_fronteiras(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    temperature: int,
):
    """CA27 positivo: temperatura aceita o intervalo fechado de 0 a 2."""

    # Arrange: seleciona uma fronteira e usa backend totalmente fake.
    arguments = _valid_arguments(temperature=temperature)
    requests, _, async_spawn, popen = _install_successful_backend(
        litert_mcp, monkeypatch
    )

    # Act: envia a temperatura de fronteira ao handler.
    result = _call_chat(litert_mcp, arguments)

    # Assert: 0 e 2 são preservados no único payload HTTP fake.
    payload = _assert_successful_request(result, requests, async_spawn, popen)
    assert payload["temperature"] == temperature


@pytest.mark.parametrize("temperature", [-0.01, 2.01])
def test_chat_rejeita_temperatura_fora_de_zero_a_dois_antes_de_efeitos(
    litert_mcp: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    temperature: float,
):
    """CA27 negativo: valores finitos fora do intervalo também são inválidos."""

    # Arrange: usa um valor abaixo ou acima do intervalo e proíbe efeitos.
    arguments = _valid_arguments(temperature=temperature)
    sentinels = _install_invalid_input_sentinels(litert_mcp, monkeypatch)

    # Act: submete a temperatura inválida diretamente ao MCP.
    result = _call_chat(litert_mcp, arguments)

    # Assert: o MCP sinaliza isError antes de qualquer backend ou processo.
    _assert_rejected_before_external_calls(result, sentinels)
