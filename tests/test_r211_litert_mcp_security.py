# -*- coding: utf-8 -*-
"""Testes RED de segurança da SPEC-935-R211.

Os contratos deste arquivo são deliberadamente executados antes da correção de
produção. O RED esperado cobre: bind somente em loopback, resposta de
``status``/``models`` sem chamar o bootstrap do daemon e comando de start do
provider sem bind global nem CORS curinga.

Os testes importam o servidor MCP por caminho, mas substituem todos os pontos
de HTTP e subprocesso por doubles determinísticos. Nenhum servidor real é
iniciado.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest import mock
from urllib.parse import urlsplit

import httpx
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = PROJECT_ROOT / ".opencode" / "mcp" / "litert_lm_server.py"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

# Permite importar a skill pelo pacote local sem depender do PYTHONPATH externo.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def litert_mcp_server() -> ModuleType:
    """Importa o servidor MCP sem executá-lo como processo ou servidor HTTP."""

    # Arrange: carrega somente o módulo versionado, sem executar ``main``.
    module_name = "_r211_litert_lm_mcp_server_under_test"
    spec = importlib.util.spec_from_file_location(module_name, SERVER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível importar {SERVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    # Act: a importação registra handlers, mas não deve abrir rede nem processo.
    spec.loader.exec_module(module)

    # Assert: o fixture entrega o módulo importado para os testes de contrato.
    return module


def _server_host(module: ModuleType) -> str:
    """Obtém o host efetivamente publicado pela configuração importada."""

    configured_host = getattr(module, "LITERT_HOST", None)
    if configured_host:
        return str(configured_host)
    base_url = str(getattr(module, "LITERT_BASE"))
    hostname = urlsplit(base_url).hostname
    if hostname is None:
        raise AssertionError(f"URL LiteRT inválida: {base_url!r}")
    return hostname


class _FakeResponse:
    """Resposta HTTP mínima usada por clientes assíncronos e síncronos fake."""

    def __init__(self, payload: dict[str, Any]):
        self._payload = payload

    def json(self) -> dict[str, Any]:
        return self._payload

    def read(self) -> bytes:
        import json

        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None


class _OnlineAsyncClient:
    """Cliente HTTP assíncrono local, sem qualquer socket real."""

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    async def __aenter__(self) -> "_OnlineAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def get(self, path: str) -> _FakeResponse:
        return _FakeResponse(self.payload)


class _OfflineAsyncClient:
    """Cliente que simula daemon ausente sem tentar conexão de rede."""

    async def __aenter__(self) -> "_OfflineAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def get(self, path: str) -> _FakeResponse:
        raise OSError("daemon LiteRT deliberadamente ausente no teste")


class _FailingAsyncClient:
    """Cliente assíncrono que falha com o erro offline indicado pelo teste."""

    def __init__(self, error: Exception):
        self.error = error

    async def __aenter__(self) -> "_FailingAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def get(self, path: str) -> _FakeResponse:
        raise self.error


def test_servidor_importado_usa_somente_host_loopback(
    litert_mcp_server: ModuleType,
):
    """O endpoint padrão do MCP deve permanecer explicitamente local."""

    # Arrange: lê a configuração efetiva após a importação do servidor.
    host = _server_host(litert_mcp_server)

    # Act: classifica o host sem iniciar o daemon LiteRT-LM.
    is_loopback = host in LOOPBACK_HOSTS

    # Assert: bind curinga não é aceitável para o servidor local.
    assert is_loopback, f"Host LiteRT não é loopback: {host!r}"
    assert host not in {"0.0.0.0", "::"}


@pytest.mark.parametrize("unsafe_host", ["0.0.0.0", "::"])
def test_servidor_nao_aceita_override_de_host_nao_local(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    unsafe_host: str,
):
    """Uma variável de ambiente não pode reabrir o bind do servidor."""

    # Arrange: fornece explicitamente um host que publica em todas as interfaces.
    monkeypatch.setenv(litert_mcp_server.HOST_ENV, unsafe_host)

    # Act: avalia a configuração sem iniciar HTTP ou subprocesso.
    try:
        configured_host = litert_mcp_server._configured_host()
    except (ValueError, RuntimeError):
        # Assert: rejeitar a configuração insegura também satisfaz o contrato.
        return

    # Assert: quando aceita a variável, o resultado ainda deve ser loopback.
    assert configured_host in LOOPBACK_HOSTS


def test_status_e_models_respondem_com_http_mockado_sem_subprocesso(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """As ferramentas devem responder ao daemon já disponível sem bootstrap."""

    # Arrange: HTTP e subprocesso são doubles; o daemon nunca será real.
    payload = {"data": [{"id": "gemma-test"}]}
    ensure_server = mock.AsyncMock(
        side_effect=AssertionError("status/models não devem iniciar o daemon")
    )
    popen = mock.Mock(name="Popen")
    monkeypatch.setattr(litert_mcp_server, "_ensure_server", ensure_server)
    monkeypatch.setattr(
        litert_mcp_server.httpx,
        "AsyncClient",
        lambda *args, **kwargs: _OnlineAsyncClient(payload),
    )
    monkeypatch.setattr(
        litert_mcp_server.urllib_request,
        "urlopen",
        mock.Mock(return_value=_FakeResponse(payload)),
    )
    monkeypatch.setattr(litert_mcp_server.subprocess, "Popen", popen)

    # Act: consulta cada ferramenta diretamente, sem transporte MCP real.
    responses = [
        asyncio.run(litert_mcp_server.call_tool("litert_lm_status", {})),
        asyncio.run(litert_mcp_server.call_tool("litert_lm_models", {})),
    ]

    # Assert: ambas respondem e nenhuma rota solicita o daemon.
    assert all(responses)
    assert '"models_count"' in responses[0][0].text
    assert "gemma-test" in responses[1][0].text
    ensure_server.assert_not_awaited()
    popen.assert_not_called()


@pytest.mark.parametrize("tool_name", ["litert_lm_status", "litert_lm_models"])
def test_status_e_models_reportam_offline_sem_tentar_iniciar_daemon(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tool_name: str,
):
    """Daemon ausente não pode transformar health check em spawn implícito."""

    # Arrange: falhas HTTP são simuladas; Popen é apenas uma sentinela.
    ensure_server = mock.AsyncMock(
        side_effect=AssertionError("health check não deve fazer auto-start")
    )
    popen = mock.Mock(name="Popen")
    monkeypatch.setattr(litert_mcp_server, "_ensure_server", ensure_server)
    monkeypatch.setattr(
        litert_mcp_server.httpx,
        "AsyncClient",
        lambda *args, **kwargs: _OfflineAsyncClient(),
    )
    monkeypatch.setattr(
        litert_mcp_server.urllib_request,
        "urlopen",
        mock.Mock(side_effect=OSError("daemon ausente")),
    )
    monkeypatch.setattr(litert_mcp_server.subprocess, "Popen", popen)

    # Act: consulta o estado mesmo com o backend indisponível.
    response = asyncio.run(litert_mcp_server.call_tool(tool_name, {}))

    # Assert: existe resposta estruturada e nenhum processo foi criado.
    assert response
    content = getattr(response, "content", response)
    assert getattr(content[0], "text", "")
    assert getattr(response, "isError", False) is True
    ensure_server.assert_not_awaited()
    popen.assert_not_called()


@pytest.mark.parametrize("tool_name", ["litert_lm_status", "litert_lm_models"])
@pytest.mark.parametrize(
    ("error_type", "error_message"),
    [
        pytest.param(httpx.RequestError, "falha HTTP do daemon", id="request-error"),
        pytest.param(OSError, "daemon offline", id="daemon-offline"),
    ],
)
def test_r211_new_status_e_models_offline_retorna_is_error(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tool_name: str,
    error_type: type[Exception],
    error_message: str,
):
    """CA14: falha HTTP/offline em health checks deve ser erro MCP real."""

    # Arrange: o cliente HTTP falha de forma determinística, sem rede real.
    offline_error = error_type(error_message)
    monkeypatch.setattr(
        litert_mcp_server.httpx,
        "AsyncClient",
        lambda *args, **kwargs: _FailingAsyncClient(offline_error),
    )

    # Act: chama a ferramenta diretamente, sem iniciar transporte MCP ou daemon.
    response = asyncio.run(litert_mcp_server.call_tool(tool_name, {}))

    # Assert: a falha operacional precisa chegar ao cliente com isError=true.
    assert getattr(response, "isError", False) is True
    assert response.content[0].text


def test_provider_default_host_e_loopback():
    """O host padrão do provider não pode escutar em todas as interfaces."""

    # Arrange: importa somente constantes e métodos do provider.
    provider_module = importlib.import_module("integrations.litert_lm_provider")

    # Act: lê o host usado pelo argumento padrão de ``start_server``.
    host = provider_module.LITERT_SERVE_HOST

    # Assert: o bind padrão deve ser explicitamente local.
    assert host in LOOPBACK_HOSTS
    assert host not in {"0.0.0.0", "::"}


@pytest.mark.parametrize("unsafe_host", ["0.0.0.0", "::"])
def test_provider_nao_aceita_host_de_ambiente_nao_local(
    monkeypatch: pytest.MonkeyPatch,
    unsafe_host: str,
):
    """O override de host do provider também deve permanecer em loopback."""

    # Arrange: injeta um override inseguro, sem criar provider ou servidor.
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    monkeypatch.setenv(provider_module.HOST_ENV, unsafe_host)

    # Act: avalia a variável de ambiente explicitamente.
    try:
        configured_host = provider_module._configured_host()
    except (ValueError, RuntimeError):
        # Assert: rejeição explícita da configuração também é segura.
        return

    # Assert: nenhuma variável pode converter o fallback em bind global.
    assert configured_host in LOOPBACK_HOSTS


def test_provider_start_padrao_nao_usa_bind_global_nem_cors_curinga(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
):
    """O comando padrão de start deve evitar wildcard de rede e CORS global."""

    # Arrange: readiness, HTTP implícito e processo são totalmente simulados.
    # XDG_RUNTIME_DIR isolado: o supervisor persiste estado de circuit breaker
    # em disco (~/.../opencode/litert-lm/state.json); sem isolar o diretório,
    # falhas reais acumuladas de outras execuções (daemon indisponível neste
    # ambiente) deixam o circuito aberto e suprimem o start_server() deste teste.
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    popen = mock.Mock(name="Popen")
    monkeypatch.setattr(provider_module, "_server_ready", False)
    monkeypatch.setattr(
        provider_module.LiteRTLMProvider,
        "is_server_running",
        staticmethod(lambda **kwargs: False),
    )
    monkeypatch.setattr(provider_module.subprocess, "Popen", popen)
    monkeypatch.setattr(
        provider_module.urllib_request,
        "urlopen",
        mock.Mock(side_effect=OSError("HTTP deliberadamente mockado")),
    )

    # Act: monta o comando padrão sem aguardar readiness real.
    provider_module.LiteRTLMProvider.start_server(timeout=0)

    # Assert: nenhum argumento pode publicar o daemon ou liberar CORS global.
    popen.assert_called_once()
    command = [str(argument) for argument in popen.call_args.args[0]]
    assert "0.0.0.0" not in command
    assert "*" not in command
    if "--cors-origin" in command:
        cors_index = command.index("--cors-origin")
        assert command[cors_index + 1] != "*"


def test_provider_start_padrao_envia_limites_ca10_ao_subprocesso(
    monkeypatch: pytest.MonkeyPatch, tmp_path,
):
    """CA10: o subprocesso recebe contexto e saída padrão de 20480 tokens."""

    # Arrange: readiness, processo, globals e ambiente são isolados pelo teste.
    # XDG_RUNTIME_DIR isolado (mesmo motivo do teste acima: circuit breaker
    # persistido em disco não deve vazar entre testes/execuções).
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    readiness = mock.Mock(name="is_server_running", return_value=False)
    popen = mock.Mock(name="Popen")
    monkeypatch.setattr(provider_module, "_server_ready", False)
    monkeypatch.setattr(provider_module, "_server_process", None)
    monkeypatch.delenv("LITERT_LM_CONTEXT_TOKENS", raising=False)
    monkeypatch.delenv("LITERT_LM_MAX_TOKENS", raising=False)
    monkeypatch.setattr(
        provider_module.LiteRTLMProvider,
        "is_server_running",
        staticmethod(readiness),
    )
    monkeypatch.setattr(provider_module.subprocess, "Popen", popen)

    # Act: inicia o servidor sem esperar readiness real ou abrir subprocesso real.
    provider_module.LiteRTLMProvider.start_server(timeout=0)

    # Assert: os defaults de contexto e saída devem ser explícitos no ambiente.
    popen.assert_called_once()
    environment = popen.call_args.kwargs["env"]
    assert environment["LITERT_LM_CONTEXT_TOKENS"] == "20480"
    assert environment["LITERT_LM_MAX_TOKENS"] == "20480"


def test_r211_remaining_skill_serve_usa_host_padrao_loopback_sem_servidor_real(
    monkeypatch: pytest.MonkeyPatch,
):
    """O ``serve`` da skill deve encaminhar um bind local por padrão."""

    # Arrange: resolve o modelo e construtor HTTP são doubles locais.
    skill_module = importlib.import_module("skills.litert_lm.skill")
    skill = object.__new__(skill_module.LiteRTLMSkill)
    model_info = SimpleNamespace(
        model_id="modelo-teste",
        model_path="/tmp/modelo-teste.litertlm",
    )
    resolver = mock.Mock(return_value=model_info)
    server_constructor = mock.Mock(name="LiteRTOpenAIServer")
    monkeypatch.setattr(skill, "_resolve_model", resolver)
    monkeypatch.setattr(skill_module, "LiteRTOpenAIServer", server_constructor)

    # Act: monta a configuração padrão sem abrir uma porta ou iniciar daemon.
    result = skill.serve("modelo-teste")

    # Assert: o host efetivo é loopback e nunca o wildcard de rede.
    resolver.assert_called_once_with("modelo-teste")
    server_constructor.assert_called_once()
    assert result is server_constructor.return_value
    configured_host = server_constructor.call_args.kwargs["host"]
    assert configured_host in LOOPBACK_HOSTS
    assert configured_host not in {"0.0.0.0", "::"}


def test_r211_new_agent_action_serve_usa_loopback_sem_host_no_contexto():
    """CA15: ``_action_serve`` deve usar loopback quando host é omitido."""

    # Arrange: a skill e o servidor são doubles; nenhum servidor real é aberto.
    agent_module = importlib.import_module("skills.litert_lm.agent")
    skill = mock.Mock(name="LiteRTLMSkill")
    skill.serve.return_value = SimpleNamespace(host="127.0.0.1", port=9379)
    agent = agent_module.LiteRTLMAgent(skill=skill)
    context = {"model_ref": "modelo-teste"}

    # Act: executa serve sem fornecer a chave ``host`` no contexto.
    result = agent._action_serve(context)

    # Assert: o default encaminhado à skill deve ser estritamente loopback.
    assert result["ok"] is True
    configured_host = skill.serve.call_args.kwargs["host"]
    assert configured_host in LOOPBACK_HOSTS
    assert configured_host not in {"0.0.0.0", "::"}
