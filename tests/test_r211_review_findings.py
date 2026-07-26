# -*- coding: utf-8 -*-
"""Testes RED para os findings P1 da revisão LiteRT-LM (SPEC-935-R211).

Os contratos deste arquivo documentam as correções ainda pendentes. A suíte não
instala dependências, não abre sockets e não inicia o daemon LiteRT-LM: o
servidor MCP é importado pelo caminho e as integrações HTTP são substituídas por
doubles locais.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from unittest import mock
from urllib import request as urllib_request
from urllib.parse import urlsplit

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MCP_SERVER_PATH = PROJECT_ROOT / ".opencode" / "mcp" / "litert_lm_server.py"
CONFIG_PATH = PROJECT_ROOT / "opencode.json"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

# Permite executar este arquivo tanto com ``python -m pytest`` quanto com o
# executável ``pytest`` sem depender de configuração global de PYTHONPATH.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _install_dependency_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Instala somente stubs de importação quando uma dependência não existe."""

    mcp_module = ModuleType("mcp")
    mcp_server_module = ModuleType("mcp.server")
    mcp_stdio_module = ModuleType("mcp.server.stdio")
    mcp_types_module = ModuleType("mcp.types")

    class _StubServer:
        def __init__(self, name: str):
            self.name = name

        def list_tools(self):
            return lambda function: function

        def call_tool(self):
            return lambda function: function

        def create_initialization_options(self):
            return {}

        async def run(self, *args, **kwargs):
            return None

    class _StubContent:
        def __init__(self, type: str = "text", text: str = "", **kwargs):
            self.type = type
            self.text = text
            for key, value in kwargs.items():
                setattr(self, key, value)

    class _StubTool:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class _StubCallToolResult:
        def __init__(self, content=None, isError: bool = False, **kwargs):
            self.content = content or []
            self.isError = isError
            for key, value in kwargs.items():
                setattr(self, key, value)

    mcp_server_module.Server = _StubServer
    mcp_types_module.Tool = _StubTool
    mcp_types_module.TextContent = _StubContent
    mcp_types_module.CallToolResult = _StubCallToolResult

    class _StubStdioContext:
        async def __aenter__(self):
            return None, None

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

    mcp_stdio_module.stdio_server = lambda: _StubStdioContext()
    mcp_module.server = mcp_server_module
    mcp_module.types = mcp_types_module

    for name, module in {
        "mcp": mcp_module,
        "mcp.server": mcp_server_module,
        "mcp.server.stdio": mcp_stdio_module,
        "mcp.types": mcp_types_module,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)


def _install_httpx_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fornece a superfície mínima de httpx para a importação sem instalação."""

    httpx_module = ModuleType("httpx")

    class _StubRequestError(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)
            self.request = kwargs.get("request")

    class _StubTimeout:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    httpx_module.RequestError = _StubRequestError
    httpx_module.Timeout = _StubTimeout
    httpx_module.AsyncClient = object
    monkeypatch.setitem(sys.modules, "httpx", httpx_module)


@pytest.fixture
def litert_mcp_server(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Importa o servidor MCP versionado sem executar seu entrypoint."""

    # Arrange: torna a importação independente de instalações opcionais locais.
    try:
        importlib.import_module("mcp.server")
        importlib.import_module("mcp.types")
    except ModuleNotFoundError:
        _install_dependency_stubs(monkeypatch)

    try:
        importlib.import_module("httpx")
    except ModuleNotFoundError:
        _install_httpx_stub(monkeypatch)

    module_name = "_r211_review_litert_mcp_server"
    spec = importlib.util.spec_from_file_location(module_name, MCP_SERVER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível importar {MCP_SERVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    # Act: executa somente o módulo; main() não é chamado.
    spec.loader.exec_module(module)

    # Assert: o fixture devolve o módulo isolado para os testes de contrato.
    try:
        yield module
    finally:
        sys.modules.pop(module_name, None)


def _canonical_litert_ids() -> set[str]:
    """Obtém o conjunto comum de IDs do provider e da configuração."""

    provider_module = importlib.import_module("integrations.litert_lm_provider")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    provider_ids = set(provider_module.MODELS)
    config_ids = set(config["provider"]["litert-lm"]["models"])
    canonical_ids = provider_ids & config_ids
    assert canonical_ids, "Provider/configuração não compartilham IDs LiteRT canônicos"
    return canonical_ids


def _normalization_artifacts(module: ModuleType) -> list[tuple[str, object]]:
    """Localiza função ou mapa explícito de aliases/normalização de modelos."""

    artifacts: list[tuple[str, object]] = []
    owners = [module]
    router_class = getattr(module, "ModelRouter", None)
    if router_class is not None:
        owners.append(router_class)

    for owner in owners:
        for name, value in vars(owner).items():
            lowered = name.lower()
            is_model_artifact = "model" in lowered or "litert" in lowered
            has_normalization_marker = any(
                marker in lowered for marker in ("normal", "alias", "canonical")
            )
            if (
                is_model_artifact
                and has_normalization_marker
                and (callable(value) or isinstance(value, Mapping))
            ):
                artifacts.append((name, value))
    return artifacts


def test_catalogo_litert_expoe_funcao_ou_mapa_de_normalizacao():
    """P1.1: aliases não podem ficar implícitos em listas divergentes."""

    # Arrange: carrega os módulos que participam do catálogo/roteamento.
    router_module = importlib.import_module("integrations.model_router")
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    legacy_catalog_module = importlib.import_module("integrations.litert_lm")

    # Act: procura uma API explícita de normalização em cada ponto público.
    artifacts = []
    for module in (router_module, provider_module, legacy_catalog_module):
        artifacts.extend(_normalization_artifacts(module))

    # Assert: o contrato deve ser observável, não apenas inferido de comentários.
    assert artifacts, (
        "O catálogo/roteador LiteRT deve expor função ou mapa de normalização "
        "de IDs canônicos"
    )


def test_route_local_forcado_litert_retorna_id_canonico():
    """P1.1: o roteamento local não pode produzir modelo órfão."""

    # Arrange: usa apenas os catálogos locais e silencia publicação de telemetria.
    router_module = importlib.import_module("integrations.model_router")
    router = router_module.ModelRouter()
    canonical_ids = _canonical_litert_ids()
    with mock.patch.object(router, "_publish_route_event"):
        # Act: força o provider local sem iniciar servidor ou fazer HTTP.
        result = router.route("local", force_provider="litert-lm")

    # Assert: o ID retornado precisa ser anunciado por provider e configuração.
    assert result.provider_id == "litert-lm"
    assert result.model_id in canonical_ids


def test_call_tool_ferramenta_desconhecida_retorna_erro_mcp(
    litert_mcp_server: ModuleType,
):
    """P1.2 positivo/negativo: ferramenta inexistente usa isError=true."""

    # Arrange: nenhum recurso externo é necessário para uma ferramenta inválida.
    unknown_tool = "litert_lm_tool_that_does_not_exist"

    # Act: chama diretamente o handler registrado, sem transporte MCP real.
    result = asyncio.run(litert_mcp_server.call_tool(unknown_tool, {}))

    # Assert: o envelope MCP precisa sinalizar falha, não apenas texto de erro.
    assert _result_is_error(result) is True


class _FailingAsyncClient:
    """Cliente httpx fake que falha somente no POST de chat."""

    def __init__(self, error: Exception):
        self.error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None

    async def post(self, *args, **kwargs):
        raise self.error


class _SuccessfulAsyncClient:
    """Cliente httpx fake que devolve uma completion determinística."""

    def __init__(self, payload: dict):
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None

    async def post(self, *args, **kwargs):
        return mock.Mock(json=lambda: self.payload)


def _result_is_error(result: object) -> object:
    """Lê isError tanto de CallToolResult quanto de um envelope dict."""

    if isinstance(result, Mapping):
        return result.get("isError")
    return getattr(result, "isError", None)


def test_call_tool_falha_de_chat_retorna_erro_mcp(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """P1.2: falha HTTP simulada deve virar CallToolResult com isError=true."""

    # Arrange: readiness e POST são doubles; nenhum daemon ou socket é usado.
    monkeypatch.setattr(
        litert_mcp_server,
        "_ensure_server",
        mock.AsyncMock(return_value=True),
    )
    request_error = litert_mcp_server.httpx.RequestError(
        "falha de chat deliberadamente simulada",
        request=mock.Mock(name="request"),
    )
    monkeypatch.setattr(
        litert_mcp_server.httpx,
        "AsyncClient",
        lambda *args, **kwargs: _FailingAsyncClient(request_error),
    )

    # Act: envia um chat válido para um backend HTTP que falha de propósito.
    result = asyncio.run(
        litert_mcp_server.call_tool(
            "litert_lm_chat",
            {"messages": [{"role": "user", "content": "teste"}]},
        )
    )

    # Assert: falha operacional não pode ser confundida com sucesso MCP.
    assert _result_is_error(result) is True


def test_call_tool_chat_sucesso_nao_e_marcado_como_erro(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """P1.2 positivo: uma completion mockada preserva resultado de sucesso."""

    # Arrange: readiness e resposta OpenAI-compatible são totalmente simuladas.
    monkeypatch.setattr(
        litert_mcp_server,
        "_ensure_server",
        mock.AsyncMock(return_value=True),
    )
    payload = {
        "choices": [{"message": {"content": "resposta local"}}],
        "usage": {"total_tokens": 1},
    }
    monkeypatch.setattr(
        litert_mcp_server.httpx,
        "AsyncClient",
        lambda *args, **kwargs: _SuccessfulAsyncClient(payload),
    )

    # Act: executa chat contra o cliente fake, sem servidor LiteRT real.
    result = asyncio.run(
        litert_mcp_server.call_tool(
            "litert_lm_chat",
            {"messages": [{"role": "user", "content": "teste"}]},
        )
    )

    # Assert: o caminho feliz não deve declarar isError.
    assert _result_is_error(result) is not True


def _assert_local_or_rejected(configured_url: str) -> None:
    """Aceita rejeição explícita ou fallback seguro para loopback."""

    host = urlsplit(configured_url).hostname
    assert host in LOOPBACK_HOSTS, (
        f"URL LiteRT externa aceita sem opt-in: {configured_url!r}"
    )


@pytest.mark.parametrize(
    "module_name",
    ["integrations.litert_lm", "integrations.litert_lm_provider"],
)
def test_provider_nao_aceita_url_externa_do_ambiente_por_padrao(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
):
    """P1.3: BASE_URL_ENV remoto exige rejeição ou opt-in explícito."""

    # Arrange: injeta URL remota sem qualquer opção de segurança adicional.
    provider_module = importlib.import_module(module_name)
    base_url_env = getattr(provider_module, "BASE_URL_ENV", "LITERT_LM_BASE_URL")
    monkeypatch.delenv(base_url_env, raising=False)
    monkeypatch.setenv(
        base_url_env,
        "https://usuario:senha@remote.example/v1",
    )

    # Act: constrói apenas o objeto de configuração, sem auto-start.
    try:
        if module_name == "integrations.litert_lm":
            provider = provider_module.LiteRTLMProvider(
                base_url=None,
                api_key="test-api-key",
            )
        else:
            provider = provider_module.LiteRTLMProvider(auto_start=False)
    except (ValueError, PermissionError):
        # Assert: rejeição explícita atende ao contrato de default seguro.
        return

    # Assert: fallback permissivo também deve permanecer em loopback.
    _assert_local_or_rejected(provider.base_url)


def test_mcp_nao_aceita_url_externa_do_ambiente_por_padrao(
    litert_mcp_server: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
):
    """P1.3: o wrapper MCP não deve confiar em BASE_URL remoto por default."""

    # Arrange: força URL externa no mesmo ambiente consumido pelo wrapper.
    monkeypatch.delenv(litert_mcp_server.BASE_URL_ENV, raising=False)
    monkeypatch.setenv(
        litert_mcp_server.BASE_URL_ENV,
        "https://remote.example/v1",
    )

    # Act: resolve a URL sem abrir o servidor ou fazer uma requisição.
    try:
        configured_url = litert_mcp_server._configured_base_url()
    except (ValueError, PermissionError):
        # Assert: rejeição explícita também é segura.
        return

    # Assert: nenhuma URL externa entra na configuração padrão.
    _assert_local_or_rejected(configured_url)


class _JsonResponse:
    """Resposta urllib mínima para testar server_status sem rede."""

    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def _new_status_provider(module_name: str, base_url: str, api_key: str):
    """Cria qualquer uma das fachadas LiteRT sem iniciar serviços externos."""

    module = importlib.import_module(module_name)
    if module_name == "integrations.litert_lm":
        return module.LiteRTLMProvider(base_url=base_url, api_key=api_key)

    provider = module.LiteRTLMProvider(base_url=base_url, auto_start=False)
    # A fachada hardened atual não recebe a chave no construtor, mas o status
    # deve permanecer seguro mesmo quando a instância possui uma credencial.
    provider._api_key = api_key
    return provider


@pytest.mark.parametrize(
    "module_name",
    ["integrations.litert_lm", "integrations.litert_lm_provider"],
)
def test_server_status_preserva_status_operacional_sem_credencial_em_claro(
    module_name: str,
):
    """P1.3 positivo: status online mantém somente dados operacionais."""

    # Arrange: resposta local mockada e chave que jamais deve ser serializada.
    provider_module = importlib.import_module(module_name)
    provider = _new_status_provider(
        module_name,
        base_url="http://127.0.0.1:9379/v1",
        api_key="status-api-key",
    )
    response = _JsonResponse({"data": [{"id": "modelo-teste"}]})
    with mock.patch.object(
        urllib_request,
        "urlopen",
        return_value=response,
    ):
        # Act: consulta status sem servidor real.
        status = provider.server_status()

    # Assert: campos úteis existem, mas a chave não aparece no payload.
    serialized = json.dumps(status, ensure_ascii=False)
    assert status["online"] is True
    assert status["models_served"] == 1
    assert "status-api-key" not in serialized


@pytest.mark.parametrize(
    "module_name",
    ["integrations.litert_lm", "integrations.litert_lm_provider"],
)
def test_server_status_redige_credenciais_da_url_e_da_excecao(
    module_name: str,
):
    """P1.3 negativo: URL autenticada e erro não podem vazar segredos."""

    # Arrange: injeta credenciais em URL e em exceção HTTP totalmente mockada.
    provider_module = importlib.import_module(module_name)
    secrets = {
        "url_password": "url-password-secret",
        "api_key": "api-key-secret",
        "access_token": "access-token-secret",
        "client_secret": "client-secret-secret",
    }
    provider = _new_status_provider(
        module_name,
        base_url=(
            "https://usuario:"
            f"{secrets['url_password']}@127.0.0.1:9379/v1"
        ),
        api_key=secrets["api_key"],
    )
    failure = RuntimeError(
        "Authorization Bearer "
        f"{secrets['access_token']} "
        f"api_key={secrets['api_key']} "
        f"client_secret={secrets['client_secret']}"
    )
    with mock.patch.object(
        urllib_request,
        "urlopen",
        side_effect=failure,
    ):
        # Act: consulta status offline, ainda sem qualquer rede real.
        status = provider.server_status()

    # Assert: nenhum valor sensível pode aparecer no resumo devolvido.
    serialized = json.dumps(status, ensure_ascii=False)
    for secret in secrets.values():
        assert secret not in serialized


def test_audit_logger_preserva_dados_publicos_aninhados():
    """P1.4 positivo: a redação não deve destruir dados não sensíveis."""

    # Arrange: argumentos e resultado públicos em objetos/listas aninhados.
    security_module = importlib.import_module("synthetic_university.mcp_security")
    audit = security_module.AuditLogger()
    args = {"metadata": {"items": [{"label": "publico", "count": 2}]}}
    result = {"ok": True, "data": [{"message": "resultado publico"}]}

    # Act: registra chamada sem credenciais.
    audit.log("safe_tool", args, result, duration=0.0)

    # Assert: a estrutura pública permanece legível após a auditoria.
    entry = audit.entries[0]
    assert entry.args_sanitized["metadata"]["items"][0]["label"] == "publico"
    assert "resultado publico" in entry.result_summary


def test_audit_logger_redige_credenciais_recursivamente_e_no_resultado():
    """P1.4 negativo: dicts/listas e result_summary devem ser sanitizados."""

    # Arrange: cada segredo aparece em dict e lista, nos argumentos e resultado.
    security_module = importlib.import_module("synthetic_university.mcp_security")
    audit = security_module.AuditLogger()
    secrets = [
        "arg-api-key-secret",
        "arg-access-token-secret",
        "arg-client-secret-secret",
        "result-api-key-secret",
        "result-access-token-secret",
        "result-client-secret-secret",
    ]
    args = {
        "nested": {
            "api_key": secrets[0],
            "items": [
                {"access_token": secrets[1]},
                {"client_secret": secrets[2]},
            ],
        }
    }
    result = {
        "api_key": secrets[3],
        "access_token": secrets[4],
        "client_secret": secrets[5],
        "items": [{"ok": True}],
    }

    # Act: registra a chamada e materializa o resumo público da entrada.
    audit.log("secret_tool", args, result, duration=0.0)
    serialized_entry = json.dumps(audit.get_recent(limit=1)[0], ensure_ascii=False)

    # Assert: nenhum segredo sobrevive em args_sanitized ou result_summary.
    for secret in secrets:
        assert secret not in serialized_entry
    assert "***REDACTED***" in serialized_entry


_REQUIREMENT_SPLIT = re.compile(r"(?:===|==|~=|!=|<=|>=|<|>|;|\[)")


def _declared_requirement_names(path: Path) -> set[str]:
    """Lê nomes de pacotes sem instalar ou resolver requirements."""

    names: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith(("-r", "--requirement", "-e", "--editable")):
            continue
        name = _REQUIREMENT_SPLIT.split(line, maxsplit=1)[0].strip()
        if name:
            names.add(name.lower().replace("-", "_"))
    return names


def test_requirements_declara_runtime_mcp_httpx_click_e_prompt_toolkit():
    """P1.5: o manifesto de runtime declara todas as dependências MCP."""

    # Arrange: lê somente o manifesto versionado, sem importar pacotes externos.
    runtime_names = _declared_requirement_names(PROJECT_ROOT / "requirements.txt")
    required_runtime = {"mcp", "httpx", "click", "prompt_toolkit"}

    # Act: calcula dependências ausentes no manifesto de execução.
    missing = required_runtime - runtime_names

    # Assert: uma instalação limpa deve conseguir preparar o runtime básico.
    assert not missing, f"Dependências de runtime ausentes: {sorted(missing)}"


def test_requirements_dev_declara_frontend_build():
    """P1.5: build permanece no manifesto de desenvolvimento."""

    # Arrange: lê requirements-dev.txt sem executar o frontend de build.
    dev_names = _declared_requirement_names(PROJECT_ROOT / "requirements-dev.txt")

    # Act/Assert: o pacote de empacotamento é uma dependência declarada.
    assert "build" in dev_names
