# -*- coding: utf-8 -*-
"""
Testes de regressão da SPEC-935-R211 — reconciliação LiteRT-LM.

Os testes são deliberadamente determinísticos: dependências opcionais, engine,
backends, HTTP e servidor de inferência são substituídos por mocks. O arquivo
registra o contrato esperado antes da correção de produção (RED → GREEN).
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest


ROOT = Path(__file__).resolve().parent.parent
MODEL_MANAGER_MODULE = "skills.litert_lm.model_manager"
PLUGIN_PATH = ROOT / ".opencode" / "plugins" / "litert-lm-provider.ts"
EXPECTED_CONTEXT_TOKENS = 20_480

# Mantém os imports dos módulos locais independentes do diretório de coleta.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _plugin_published_models(source: str) -> dict[str, dict[str, object]]:
    """Extrai a projeção pública dos modelos sem executar TypeScript.

    O plugin é deliberadamente tratado como fonte textual: o teste não depende
    de Bun, Node, compilador TypeScript ou rede. As chaves com oito espaços são
    as entradas de modelo do objeto retornado pelo hook ``models``.
    """

    model_matches = list(
        re.finditer(
            r'(?m)^[ \t]{8}"(?P<model>[^"]+)":\s*\{',
            source,
        )
    )
    assert model_matches, "O plugin não publicou nenhum modelo LiteRT-LM"

    published: dict[str, dict[str, object]] = {}
    for index, model_match in enumerate(model_matches):
        block_start = model_match.end()
        block_end = (
            model_matches[index + 1].start()
            if index + 1 < len(model_matches)
            else source.find("\n      }),", block_start)
        )
        if block_end < 0:
            block_end = len(source)
        block = source[block_start:block_end]

        declared_id = re.search(r'\bid:\s*"([^"]+)"', block)
        limit = re.search(
            r"limit:\s*\{\s*context:\s*(\d+)\s*,\s*output:\s*(\d+)\s*\}",
            block,
        )
        assert declared_id, f"Modelo sem id explícito no plugin: {model_match.group('model')}"
        assert limit, f"Modelo sem limit no plugin: {model_match.group('model')}"
        published[model_match.group("model")] = {
            "id": declared_id.group(1),
            "limit": {
                "context": int(limit.group(1)),
                "output": int(limit.group(2)),
            },
        }
    return published


def _canonical_ids_from_config() -> set[str]:
    """Obtém os IDs anunciados pela configuração OpenCode atual."""
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    return set(config["provider"]["litert-lm"]["models"])


@contextmanager
def _model_manager_without_huggingface():
    """Recarrega model_manager simulando ausência de huggingface_hub.

    O estado global do módulo é restaurado ao final para não contaminar outros
    testes eventualmente executados no mesmo processo.
    """
    module = importlib.import_module(MODEL_MANAGER_MODULE)
    previous_hub = module._huggingface_hub
    previous_available = module._HF_AVAILABLE

    try:
        with mock.patch.dict(sys.modules, {"huggingface_hub": None}):
            importlib.reload(module)
            yield module
    finally:
        module._huggingface_hub = previous_hub
        module._HF_AVAILABLE = previous_available


def _fake_engine():
    """Cria engine/conversation sem carregar um modelo real."""
    engine = mock.MagicMock(name="engine")
    engine.__enter__.return_value = engine
    engine.__exit__.return_value = None

    conversation = mock.MagicMock(name="conversation")
    conversation.__enter__.return_value = conversation
    conversation.__exit__.return_value = None
    engine.create_conversation.return_value = conversation
    return engine, conversation


def _fake_litert_backend(backend_factories, engine):
    """Monta o namespace mínimo da API LiteRT-LM para testes unitários."""
    return SimpleNamespace(
        Backend=SimpleNamespace(**backend_factories),
        Engine=mock.Mock(return_value=engine),
    )


class _JsonResponse:
    """Resposta HTTP mínima para impedir qualquer conexão de rede real."""

    def __init__(self, payload: dict):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None

    def read(self):
        return self._body


# ── CA8: import opcional e pontos de integração mockáveis ──────────────────────


def test_model_manager_importa_sem_huggingface_hub(tmp_path):
    """A ausência do pacote opcional não impede importar ModelManager."""
    # Arrange: o helper recarrega o módulo com o import opcional indisponível.
    with _model_manager_without_huggingface() as module:
        # Act: importa/instancia a classe sem tocar na rede ou no Hub.
        manager = module.ModelManager(models_dir=str(tmp_path / "models"))

        # Assert: o módulo está utilizável e sinaliza corretamente a ausência.
        assert manager.models_dir == str(tmp_path / "models")
        assert module._HF_AVAILABLE is False
        assert module._huggingface_hub is None


def test_model_manager_sem_huggingface_exibe_erro_de_instalacao(tmp_path):
    """O método real falha claramente, em vez de produzir AttributeError."""
    # Arrange: carrega ModelManager com a dependência opcional ausente.
    with _model_manager_without_huggingface() as module:
        manager = module.ModelManager(models_dir=str(tmp_path / "models"))

        # Act + Assert: importar pelo Hub exige uma instalação explícita.
        with pytest.raises(ImportError, match=r"huggingface_hub.*pip install"):
            manager.import_from_hf("org/model", filename="model.litertlm")


def test_metodos_opcionais_do_huggingface_sao_patchaveis(tmp_path):
    """list_repo_files e hf_hub_download podem ser substituídos por mocks."""
    # Arrange: cria um Hub falso e um download que grava somente um fixture local.
    module = importlib.import_module(MODEL_MANAGER_MODULE)
    list_repo_files = mock.Mock(return_value=["README.md", "model.litertlm"])

    def fake_download(**kwargs):
        destination = Path(kwargs["local_dir"]) / kwargs["filename"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"modelo-falso")
        return str(destination)

    download = mock.Mock(side_effect=fake_download)
    fake_hub = SimpleNamespace(
        list_repo_files=list_repo_files,
        hf_hub_download=download,
    )

    with mock.patch.object(module, "_HF_AVAILABLE", True), mock.patch.object(
        module, "_huggingface_hub", fake_hub
    ):
        manager = module.ModelManager(models_dir=str(tmp_path / "models"))

        # Act: executa a auto-descoberta e o download usando somente os mocks.
        info = manager.import_from_hf("org/model", token="hf-test-token")

        # Assert: os dois pontos de integração receberam os argumentos corretos.
        list_repo_files.assert_called_once_with("org/model", token="hf-test-token")
        download.assert_called_once()
        assert download.call_args.kwargs["repo_id"] == "org/model"
        assert download.call_args.kwargs["filename"] == "model.litertlm"
        assert info.model_id == "org/model"
        assert Path(info.model_path).is_file()


def test_auto_descoberta_sem_arquivo_litertlm_e_rejeitada(tmp_path):
    """Um Hub mockado sem artefato .litertlm produz erro explícito."""
    # Arrange: o método opcional anuncia somente arquivos que não são modelos.
    module = importlib.import_module(MODEL_MANAGER_MODULE)
    fake_hub = SimpleNamespace(
        list_repo_files=mock.Mock(return_value=["README.md"]),
        hf_hub_download=mock.Mock(),
    )
    with mock.patch.object(module, "_HF_AVAILABLE", True), mock.patch.object(
        module, "_huggingface_hub", fake_hub
    ):
        manager = module.ModelManager(models_dir=str(tmp_path / "models"))

        # Act + Assert: não tenta baixar um arquivo inexistente.
        with pytest.raises(ValueError, match=r"Nenhum arquivo \.litertlm"):
            manager.import_from_hf("org/model")
        fake_hub.hf_hub_download.assert_not_called()


# ── CA9: ciclo de vida e auto_start ───────────────────────────────────────────


def test_provider_auto_start_false_nao_inicia_servidor_na_construcao():
    """auto_start=False não chama start_server durante a construção."""
    # Arrange: intercepta o método que poderia iniciar subprocesso.
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    with mock.patch.object(
        provider_module.LiteRTLMProvider, "start_server", return_value=True
    ) as start_server:
        # Act: cria o provider sem inicialização automática.
        provider_module.LiteRTLMProvider(
            base_url="http://test.invalid/v1", auto_start=False
        )

        # Assert: nenhum início foi solicitado.
        start_server.assert_not_called()


def test_provider_auto_start_true_inicia_servidor():
    """O caminho positivo mantém a inicialização automática configurada."""
    # Arrange: substitui start_server para evitar subprocesso e HTTP.
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    with mock.patch.object(
        provider_module.LiteRTLMProvider, "start_server", return_value=True
    ) as start_server:
        # Act: usa o comportamento padrão.
        provider_module.LiteRTLMProvider(base_url="http://test.invalid/v1")

        # Assert: o início automático foi solicitado exatamente uma vez.
        start_server.assert_called_once_with()


def test_provider_auto_start_false_nao_inicia_servidor_ao_completar():
    """complete não reativa start_server quando auto_start=False."""
    # Arrange: HTTP e start_server são mocks; não há servidor local envolvido.
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    response = _JsonResponse(
        {
            "id": "chatcmpl-test",
            "choices": [{"message": {"role": "assistant", "content": "ok"}}],
        }
    )
    with mock.patch.object(
        provider_module.LiteRTLMProvider, "start_server", return_value=True
    ) as start_server, mock.patch.object(
        provider_module.urllib_request, "urlopen", return_value=response
    ):
        provider = provider_module.LiteRTLMProvider(
            base_url="http://test.invalid/v1", auto_start=False
        )

        # Act: completa uma requisição contra a resposta HTTP simulada.
        result = provider.complete(
            messages=[{"role": "user", "content": "teste"}],
            model=provider_module.DEFAULT_MODEL,
            max_tokens=8,
        )

        # Assert: a requisição foi concluída sem iniciar o daemon.
        assert result["choices"][0]["message"]["content"] == "ok"
        start_server.assert_not_called()


# ── CA9: seleção de backend e falha explícita ─────────────────────────────────


def _ensure_litert_attr(module):
    """Ensure a skills.litert_lm.* module has a 'litert_lm' attribute."""
    import types as _t
    if "litert_lm" not in module.__dict__:
        _m = _t.ModuleType("litert_lm")
        _m.Engine = mock.MagicMock()
        _m.Backend = mock.MagicMock()
        _m.Backend.CPU = mock.MagicMock()
        _m.SamplerConfig = mock.MagicMock()
        module.__dict__["litert_lm"] = _m
        module.__dict__["_LITERT_AVAILABLE"] = True

def test_chat_instancia_apenas_o_backend_solicitado(tmp_path, monkeypatch):
    """Selecionar GPU não deve construir CPU nem NPU como efeito colateral."""
    # Arrange: ensure chat module has litert_lm attribute first
    from skills.litert_lm import chat as chat_module
    _ensure_litert_attr(chat_module)

    model_path = tmp_path / "model.litertlm"
    model_path.write_bytes(b"modelo-falso")
    engine, _conversation = _fake_engine()
    cpu = mock.Mock(name="CPU", return_value=object())
    gpu = mock.Mock(name="GPU", return_value=object())
    npu = mock.Mock(name="NPU", return_value=object())
    fake_litert = _fake_litert_backend(
        {"CPU": cpu, "GPU": gpu, "NPU": npu}, engine
    )
    monkeypatch.setattr(chat_module, "litert_lm", fake_litert)
    monkeypatch.setattr(chat_module, "_LITERT_AVAILABLE", True)

    session = chat_module.ChatSession(
        str(model_path), backend="gpu", cache="none", max_tokens=128
    )

    # Act: inicializa sob demanda.
    session._ensure_initialized()

    # Assert: somente a factory do backend escolhido foi chamada.
    gpu.assert_called_once_with()
    cpu.assert_not_called()
    npu.assert_not_called()
    assert fake_litert.Engine.call_args.kwargs["backend"] is gpu.return_value


def test_chat_backend_indisponivel_nao_faz_downgrade_para_cpu(tmp_path, monkeypatch):
    """RuntimeError do backend solicitado deve chegar ao chamador."""
    # Arrange: GPU explicitamente indisponível; CPU/NPU são sentinelas.
    from skills.litert_lm import chat as chat_module
    _ensure_litert_attr(chat_module)

    model_path = tmp_path / "model.litertlm"
    model_path.write_bytes(b"modelo-falso")
    engine, _conversation = _fake_engine()
    cpu = mock.Mock(name="CPU", return_value=object())
    gpu = mock.Mock(name="GPU", side_effect=RuntimeError("GPU indisponível"))
    npu = mock.Mock(name="NPU", return_value=object())
    fake_litert = _fake_litert_backend(
        {"CPU": cpu, "GPU": gpu, "NPU": npu}, engine
    )
    monkeypatch.setattr(chat_module, "litert_lm", fake_litert)
    monkeypatch.setattr(chat_module, "_LITERT_AVAILABLE", True)
    session = chat_module.ChatSession(
        str(model_path), backend="gpu", cache="none", max_tokens=128
    )

    # Act + Assert: indisponibilidade não é convertida silenciosamente em CPU.
    with pytest.raises(RuntimeError, match="GPU indisponível"):
        session._ensure_initialized()
    cpu.assert_not_called()
    npu.assert_not_called()
    fake_litert.Engine.assert_not_called()


def test_server_instancia_apenas_o_backend_solicitado(monkeypatch):
    """O wrapper HTTP aplica a mesma seleção lazy de backend da sessão."""
    # Arrange: servidor e API LiteRT-LM totalmente simulados.
    from skills.litert_lm import server as server_module
    _ensure_litert_attr(server_module)

    engine, _conversation = _fake_engine()
    cpu = mock.Mock(name="CPU", return_value=object())
    gpu = mock.Mock(name="GPU", return_value=object())
    npu = mock.Mock(name="NPU", return_value=object())
    fake_litert = _fake_litert_backend(
        {"CPU": cpu, "GPU": gpu, "NPU": npu}, engine
    )
    monkeypatch.setattr(server_module, "litert_lm", fake_litert)

    server = server_module.LiteRTOpenAIServer(
        "model.litertlm", backend="gpu"
    )

    # Act: inicializa o engine sem abrir porta HTTP.
    server._init_engine()

    # Assert: CPU e NPU não foram instanciados.
    gpu.assert_called_once_with()
    cpu.assert_not_called()
    npu.assert_not_called()
    assert fake_litert.Engine.call_args.kwargs["backend"] is gpu.return_value


def test_server_backend_indisponivel_nao_faz_downgrade_para_cpu(monkeypatch):
    """O servidor também propaga indisponibilidade explícita do backend."""
    # Arrange: factory GPU falha e nenhuma inferência real é permitida.
    from skills.litert_lm import server as server_module
    _ensure_litert_attr(server_module)

    engine, _conversation = _fake_engine()
    cpu = mock.Mock(name="CPU", return_value=object())
    gpu = mock.Mock(name="GPU", side_effect=RuntimeError("GPU indisponível"))
    npu = mock.Mock(name="NPU", return_value=object())
    fake_litert = _fake_litert_backend(
        {"CPU": cpu, "GPU": gpu, "NPU": npu}, engine
    )
    monkeypatch.setattr(server_module, "litert_lm", fake_litert)
    server = server_module.LiteRTOpenAIServer(
        "model.litertlm", backend="gpu"
    )

    # Act + Assert: a falha explícita não aciona o fallback CPU.
    with pytest.raises(RuntimeError, match="GPU indisponível"):
        server._init_engine()
    cpu.assert_not_called()
    npu.assert_not_called()
    fake_litert.Engine.assert_not_called()


# ── CA10: política de contexto separada do limite de saída ────────────────────


def test_chat_contexto_e_saida_usam_limites_separados(tmp_path, monkeypatch):
    """max_tokens limita a saída, enquanto o contexto segue política própria.

    A implementação pode expor ``context_tokens``/``context_window`` ou usar a
    política configurável ``LITERT_LM_CONTEXT_TOKENS``. O contrato observável é
    o mesmo: max_num_tokens do Engine não pode ser reduzido ao limite de saída.
    """
    # Arrange: usa output pequeno e contexto deliberadamente maior.
    from skills.litert_lm import chat as chat_module
    _ensure_litert_attr(chat_module)

    model_path = tmp_path / "model.litertlm"
    model_path.write_bytes(b"modelo-falso")
    engine, conversation = _fake_engine()
    backend = {
        "CPU": mock.Mock(name="CPU", return_value=object()),
        "GPU": mock.Mock(name="GPU", return_value=object()),
        "NPU": mock.Mock(name="NPU", return_value=object()),
    }
    fake_litert = _fake_litert_backend(backend, engine)
    monkeypatch.setattr(chat_module, "litert_lm", fake_litert)
    monkeypatch.setattr(chat_module, "_LITERT_AVAILABLE", True)

    output_limit = 128
    context_limit = 8192
    constructor_kwargs = {
        "stream": False,
        "backend": "cpu",
        "cache": "none",
        "max_tokens": output_limit,
    }
    parameters = inspect.signature(chat_module.ChatSession).parameters
    if "context_tokens" in parameters:
        constructor_kwargs["context_tokens"] = context_limit
    elif "context_window" in parameters:
        constructor_kwargs["context_window"] = context_limit
    else:
        # Rota de política configurável aceita pelo contrato R211.
        monkeypatch.setenv("LITERT_LM_CONTEXT_TOKENS", str(context_limit))

    session = chat_module.ChatSession(str(model_path), **constructor_kwargs)

    # Act: constrói o engine/conversation com os limites configurados.
    session._ensure_initialized()

    # Assert: contexto e saída permanecem distintos e explícitos.
    assert fake_litert.Engine.call_args.kwargs["max_num_tokens"] == context_limit
    conversation_kwargs = engine.create_conversation.call_args.kwargs
    assert conversation_kwargs["max_output_tokens"] == output_limit
    assert fake_litert.Engine.call_args.kwargs["max_num_tokens"] != output_limit


def test_configuracao_litert_anuncia_contexto_e_saida_separados():
    """A configuração atual não deve colapsar context e output em um limite."""
    # Arrange: lê somente o JSON versionado, sem iniciar provider ou servidor.
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    models = config["provider"]["litert-lm"]["models"]

    # Act: coleta os limites publicados para cada modelo.
    limits = [model_info["limit"] for model_info in models.values()]

    # Assert: ambos os limites existem e o contexto é maior que a saída.
    assert limits
    for limit in limits:
        assert isinstance(limit["context"], int)
        assert isinstance(limit["output"], int)
        assert limit["context"] > limit["output"]


def test_r211_remaining_politica_contexto_20480_e_consistente_em_todas_as_fontes():
    """O default de contexto deve ser o mesmo em cada superfície LiteRT-LM."""

    # Arrange: importa somente constantes/catálogos e lê JSON/plugin locais.
    chat_module = importlib.import_module("skills.litert_lm.chat")
    server_module = importlib.import_module("skills.litert_lm.server")
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    config_models = config["provider"]["litert-lm"]["models"]
    plugin_models = _plugin_published_models(
        PLUGIN_PATH.read_text(encoding="utf-8")
    )

    # Act: reúne os valores publicados por runtime, catálogo, JSON e plugin.
    context_values = {
        "skills.litert_lm.chat": {chat_module.DEFAULT_CONTEXT_TOKENS},
        "skills.litert_lm.server": {server_module.DEFAULT_CONTEXT_TOKENS},
        "integrations.litert_lm_provider.MODELS": {
            model["context"] for model in provider_module.MODELS.values()
        },
        "opencode.json": {
            model["limit"]["context"] for model in config_models.values()
        },
        ".opencode/plugins/litert-lm-provider.ts": {
            model["limit"]["context"] for model in plugin_models.values()
        },
    }

    # Assert: cada superfície possui exatamente a política contratada.
    assert context_values
    for source, values in context_values.items():
        assert values == {EXPECTED_CONTEXT_TOKENS}, (
            f"Política de contexto divergente em {source}: {sorted(values)}"
        )


def test_r211_remaining_plugin_publicado_nao_diverge_do_opencode_json():
    """IDs e limites publicados pelo plugin devem coincidir com o JSON."""

    # Arrange: normaliza as duas fontes locais para a mesma projeção pública.
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    config_models = config["provider"]["litert-lm"]["models"]
    plugin_models = _plugin_published_models(
        PLUGIN_PATH.read_text(encoding="utf-8")
    )
    expected = {
        model_id: {
            "id": model_id,
            "limit": {
                "context": model_info["limit"]["context"],
                "output": model_info["limit"]["output"],
            },
        }
        for model_id, model_info in config_models.items()
    }

    # Act: compara a publicação textual do plugin com a configuração canônica.
    published = {
        model_id: {
            "id": model_info["id"],
            "limit": model_info["limit"],
        }
        for model_id, model_info in plugin_models.items()
    }

    # Assert: nenhuma entrada, ID ou limite pode divergir entre as fontes.
    assert set(published) == set(expected)
    assert published == expected


# ── CA7/CA10: IDs canônicos e aliases anunciados ──────────────────────────────


def test_provider_lista_ids_canonicos_anunciados_sem_servidor_real():
    """Os IDs canônicos da API/configuração são preservados pelo catálogo."""
    # Arrange: força o caminho de fallback sem rede.
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    provider = provider_module.LiteRTLMProvider(
        base_url="http://test.invalid/v1", auto_start=False
    )
    with mock.patch.object(
        provider_module.urllib_request,
        "urlopen",
        side_effect=OSError("servidor deliberadamente ausente"),
    ):
        # Act: lista modelos exclusivamente do catálogo local.
        models = provider.list_models()

    # Assert: cada ID configurado continua anunciado literalmente.
    announced = {model["id"] for model in models}
    assert _canonical_ids_from_config() <= announced


def test_aliases_anunciados_apontam_para_ids_canonicos():
    """Se a API expuser aliases, cada um deve declarar seu canônico.

    O catálogo atual pode anunciar somente IDs canônicos; nesse caso o teste é
    pulado com motivo explícito, sem inventar aliases que o servidor não expõe.
    """
    # Arrange: procura os nomes convencionais de mapa de aliases na API atual.
    provider_module = importlib.import_module("integrations.litert_lm_provider")
    aliases = getattr(provider_module, "MODEL_ALIASES", None)
    if aliases is None:
        aliases = getattr(provider_module, "ALIASES", None)
    if not aliases:
        pytest.skip("A API atual anuncia somente IDs canônicos; nenhum alias")

    canonical_ids = _canonical_ids_from_config()

    # Act: normaliza o mapa anunciado pelo provider.
    normalized = dict(aliases)

    # Assert: aliases não podem apontar para IDs não publicados.
    assert set(normalized.values()) <= canonical_ids
    assert set(normalized) - set(normalized.values())
