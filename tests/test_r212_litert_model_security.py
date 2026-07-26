# -*- coding: utf-8 -*-
"""Testes RED herméticos da CA26 da SPEC-935-R212 v1.1.

Os contratos abaixo exigem validação fail-closed de IDs antes de qualquer
consulta, importação ou exclusão. Todo filesystem mutável reside em
``tmp_path`` e a integração com HuggingFace é sempre substituída por doubles.
"""

from __future__ import annotations

import http.client
import importlib
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest import mock
from urllib import request as urllib_request

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


CANONICAL_MODEL_ID = "litert-community/gemma-4-E2B-it-litert-lm"
ESCAPING_MODEL_ID = "local/escaping-model"

_INVALID_ID_CASES = (
    "empty",
    "dot",
    "dot-dot",
    "absolute",
    "traversal",
    "backslash",
    "nul",
)

_INVALID_ID_LABELS = (
    "vazio",
    "ponto",
    "ponto-ponto",
    "absoluto",
    "travessia",
    "barra-invertida",
    "nul",
)


@dataclass(frozen=True)
class _ManagerHarness:
    module: ModuleType
    manager: Any
    cache_dir: Path


@pytest.fixture(autouse=True)
def no_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha imediatamente diante de rede, subprocesso ou espera real."""

    def blocked(*args: Any, **kwargs: Any) -> Any:
        del args, kwargs
        raise AssertionError(
            "Testes R212 CA26 não permitem rede, subprocesso ou espera real"
        )

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(http.client.HTTPConnection, "connect", blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", blocked)
    monkeypatch.setattr(urllib_request, "urlopen", blocked)
    monkeypatch.setattr(subprocess, "Popen", blocked)
    monkeypatch.setattr(time, "sleep", blocked)


@pytest.fixture
def manager_harness(tmp_path: Path) -> _ManagerHarness:
    """Cria um ModelManager cujo cache está integralmente em ``tmp_path``."""

    module = importlib.import_module("skills.litert_lm.model_manager")
    cache_dir = tmp_path / "sandbox" / "models"
    manager = module.ModelManager(models_dir=str(cache_dir))
    return _ManagerHarness(module=module, manager=manager, cache_dir=cache_dir)


@pytest.fixture(params=_INVALID_ID_CASES, ids=_INVALID_ID_LABELS)
def invalid_model_id(request: pytest.FixtureRequest, tmp_path: Path) -> str:
    """Materializa cada classe de ID proibida pela CA26."""

    values = {
        "empty": "",
        "dot": ".",
        "dot-dot": "..",
        "traversal": "../outside-model",
        "backslash": r"organization\model",
        "nul": "organization/model\x00",
    }
    if request.param == "absolute":
        return str(tmp_path / "outside-cache" / "absolute-model")
    return values[request.param]


def _capture_exception(operation: Callable[[], object]) -> Exception | None:
    """Captura a falha sem impedir a verificação posterior dos spies."""

    try:
        operation()
    except Exception as error:  # noqa: BLE001 - o tipo é verificado no teste
        return error
    return None


def _create_cached_model(
    harness: _ManagerHarness,
    model_id: str = CANONICAL_MODEL_ID,
    *,
    filename: str = "model.litertlm",
    payload: bytes = b"LOCAL-LITERT-MODEL",
) -> Path:
    model_dir = harness.cache_dir / model_id.replace("/", "--")
    model_dir.mkdir(parents=True, exist_ok=True)
    model_file = model_dir / filename
    model_file.parent.mkdir(parents=True, exist_ok=True)
    model_file.write_bytes(payload)
    return model_file


def _create_escaping_symlink(
    harness: _ManagerHarness,
    tmp_path: Path,
) -> tuple[Path, Path]:
    outside_dir = tmp_path / "outside-cache"
    outside_model = outside_dir / "nested" / "weights.litertlm"
    outside_model.parent.mkdir(parents=True, exist_ok=True)
    outside_model.write_bytes(b"OUTSIDE-CACHE-SENTINEL")

    model_link = harness.cache_dir / ESCAPING_MODEL_ID.replace("/", "--")
    model_link.symlink_to(outside_dir, target_is_directory=True)
    return model_link, outside_model


def _install_fake_hub(
    monkeypatch: pytest.MonkeyPatch,
    module: ModuleType,
    *,
    download_side_effect: Callable[..., str] | None = None,
) -> tuple[mock.Mock, mock.Mock]:
    list_repo_files = mock.Mock(
        name="list_repo_files",
        return_value=["model.litertlm"],
    )
    hf_hub_download = mock.Mock(
        name="hf_hub_download",
        side_effect=download_side_effect,
    )
    fake_hub = SimpleNamespace(
        list_repo_files=list_repo_files,
        hf_hub_download=hf_hub_download,
    )
    monkeypatch.setattr(module, "_huggingface_hub", fake_hub)
    monkeypatch.setattr(module, "_HF_AVAILABLE", True)
    return list_repo_files, hf_hub_download


def test_find_model_rejeita_id_invalido_antes_de_consultar_filesystem(
    manager_harness: _ManagerHarness,
    invalid_model_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA26 negativo: find falha antes de qualquer localização no cache."""

    # Arrange: substitui todas as sondagens alcançadas pelo fluxo legado.
    file_probe = mock.Mock(name="isfile", return_value=False)
    recursive_finder = mock.Mock(name="_find_litertlm_file", return_value=None)
    monkeypatch.setattr(manager_harness.module.os.path, "isfile", file_probe)
    monkeypatch.setattr(
        manager_harness.manager,
        "_find_litertlm_file",
        recursive_finder,
    )

    # Act: tenta localizar uma referência que não pertence à gramática canônica.
    error = _capture_exception(
        lambda: manager_harness.manager.find_model(invalid_model_id)
    )

    # Assert: a validação antecede toda consulta e falha de forma explícita.
    assert tuple(manager_harness.cache_dir.iterdir()) == ()
    file_probe.assert_not_called()
    recursive_finder.assert_not_called()
    assert isinstance(error, ValueError)


def test_import_from_hf_rejeita_id_invalido_antes_de_hub_ou_mutacao(
    manager_harness: _ManagerHarness,
    invalid_model_id: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CA26 negativo: import valida o ID antes do Hub e do diretório destino."""

    # Arrange: todas as integrações e mutações potenciais são spies locais.
    list_repo_files, hf_hub_download = _install_fake_hub(
        monkeypatch,
        manager_harness.module,
    )
    hf_hub_download.return_value = str(tmp_path / "unused-download.litertlm")
    require_hub = mock.Mock(name="_require_hub_method")
    make_dirs = mock.Mock(name="makedirs")
    monkeypatch.setattr(manager_harness.module, "_require_hub_method", require_hub)
    monkeypatch.setattr(manager_harness.module.os, "makedirs", make_dirs)
    entries_before = tuple(manager_harness.cache_dir.iterdir())

    # Act: tenta importar sem permitir acesso ao HuggingFace ou escrita adicional.
    error = _capture_exception(
        lambda: manager_harness.manager.import_from_hf(
            invalid_model_id,
            filename="model.litertlm",
        )
    )

    # Assert: nenhuma etapa de importação começa antes da rejeição do ID.
    assert tuple(manager_harness.cache_dir.iterdir()) == entries_before
    require_hub.assert_not_called()
    make_dirs.assert_not_called()
    list_repo_files.assert_not_called()
    hf_hub_download.assert_not_called()
    assert isinstance(error, ValueError)


def test_delete_model_rejeita_id_invalido_antes_de_sondar_ou_excluir(
    manager_harness: _ManagerHarness,
    invalid_model_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA26 negativo: delete falha antes de sondar ou remover qualquer árvore."""

    # Arrange: bloqueia tanto a sondagem quanto a primitiva destrutiva.
    directory_probe = mock.Mock(name="isdir", return_value=False)
    remove_tree = mock.Mock(name="rmtree")
    monkeypatch.setattr(manager_harness.module.os.path, "isdir", directory_probe)
    monkeypatch.setattr(manager_harness.module.shutil, "rmtree", remove_tree)
    entries_before = tuple(manager_harness.cache_dir.iterdir())

    # Act: solicita exclusão com um ID proibido pela CA26.
    error = _capture_exception(
        lambda: manager_harness.manager.delete_model(invalid_model_id)
    )

    # Assert: nenhuma consulta ou exclusão ocorre e o erro é de validação.
    assert tuple(manager_harness.cache_dir.iterdir()) == entries_before
    directory_probe.assert_not_called()
    remove_tree.assert_not_called()
    assert isinstance(error, ValueError)


def test_find_model_rejeita_symlink_que_escapa_do_cache_antes_da_busca(
    manager_harness: _ManagerHarness,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CA26 negativo: find não segue o diretório de modelo para fora do cache."""

    # Arrange: o nome é canônico, mas sua entrada aponta para uma árvore externa.
    model_link, outside_model = _create_escaping_symlink(
        manager_harness,
        tmp_path,
    )
    original_isfile = manager_harness.module.os.path.isfile
    file_probe = mock.Mock(name="isfile", wraps=original_isfile)
    recursive_finder = mock.Mock(
        name="_find_litertlm_file",
        wraps=manager_harness.manager._find_litertlm_file,
    )
    monkeypatch.setattr(manager_harness.module.os.path, "isfile", file_probe)
    monkeypatch.setattr(
        manager_harness.manager,
        "_find_litertlm_file",
        recursive_finder,
    )

    # Act: tenta resolver o ID cuja entrada rompe a contenção do cache.
    error = _capture_exception(
        lambda: manager_harness.manager.find_model(ESCAPING_MODEL_ID)
    )

    # Assert: o alvo externo permanece intacto e nenhuma busca o alcança.
    assert model_link.is_symlink()
    assert outside_model.read_bytes() == b"OUTSIDE-CACHE-SENTINEL"
    file_probe.assert_not_called()
    recursive_finder.assert_not_called()
    assert isinstance(error, ValueError)


def test_import_from_hf_rejeita_symlink_que_escapa_antes_do_download(
    manager_harness: _ManagerHarness,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CA26 negativo: import não usa symlink externo como diretório destino."""

    # Arrange: instala o symlink malicioso e doubles observáveis do Hub/filesystem.
    model_link, outside_model = _create_escaping_symlink(
        manager_harness,
        tmp_path,
    )
    list_repo_files, hf_hub_download = _install_fake_hub(
        monkeypatch,
        manager_harness.module,
    )
    hf_hub_download.return_value = str(outside_model)
    require_hub = mock.Mock(name="_require_hub_method")
    original_makedirs = manager_harness.module.os.makedirs
    make_dirs = mock.Mock(name="makedirs", wraps=original_makedirs)
    monkeypatch.setattr(manager_harness.module, "_require_hub_method", require_hub)
    monkeypatch.setattr(manager_harness.module.os, "makedirs", make_dirs)

    # Act: tenta importar para a entrada que resolve fora do cache.
    error = _capture_exception(
        lambda: manager_harness.manager.import_from_hf(
            ESCAPING_MODEL_ID,
            filename="model.litertlm",
        )
    )

    # Assert: nenhuma integração começa e o arquivo externo não é modificado.
    assert model_link.is_symlink()
    assert outside_model.read_bytes() == b"OUTSIDE-CACHE-SENTINEL"
    require_hub.assert_not_called()
    make_dirs.assert_not_called()
    list_repo_files.assert_not_called()
    hf_hub_download.assert_not_called()
    assert isinstance(error, ValueError)


def test_delete_model_rejeita_symlink_que_escapa_antes_de_remover(
    manager_harness: _ManagerHarness,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CA26 negativo: delete nunca entrega symlink externo ao ``rmtree``."""

    # Arrange: a primitiva destrutiva é um mock e o alvo externo é um sentinela.
    model_link, outside_model = _create_escaping_symlink(
        manager_harness,
        tmp_path,
    )
    remove_tree = mock.Mock(name="rmtree")
    monkeypatch.setattr(manager_harness.module.shutil, "rmtree", remove_tree)

    # Act: tenta excluir o ID cuja entrada escapa da raiz confiável.
    error = _capture_exception(
        lambda: manager_harness.manager.delete_model(ESCAPING_MODEL_ID)
    )

    # Assert: nem o link nem o alvo são removidos e rmtree jamais é chamado.
    assert model_link.is_symlink()
    assert outside_model.read_bytes() == b"OUTSIDE-CACHE-SENTINEL"
    remove_tree.assert_not_called()
    assert isinstance(error, ValueError)


def test_find_model_preserva_id_canonico_dentro_do_cache(
    manager_harness: _ManagerHarness,
) -> None:
    """CA26 positivo: a contenção não bloqueia localização canônica válida."""

    # Arrange: cria um modelo regular exclusivamente dentro do cache temporário.
    model_file = _create_cached_model(manager_harness)

    # Act: localiza o modelo por seu ID canônico.
    info = manager_harness.manager.find_model(CANONICAL_MODEL_ID)

    # Assert: o contrato positivo e o caminho contido permanecem funcionais.
    assert info is not None
    assert info.model_id == CANONICAL_MODEL_ID
    assert Path(info.model_path) == model_file.resolve()
    assert Path(info.model_path).is_relative_to(manager_harness.cache_dir.resolve())


def test_import_from_hf_preserva_id_canonico_com_download_mockado(
    manager_harness: _ManagerHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA26 positivo: ID canônico ainda pode ser importado de forma contida."""

    # Arrange: o download fake grava somente no ``local_dir`` fornecido.
    payload = b"IMPORTED-LITERT-MODEL"

    def fake_download(**kwargs: Any) -> str:
        target = Path(kwargs["local_dir"]) / kwargs["filename"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return str(target)

    list_repo_files, hf_hub_download = _install_fake_hub(
        monkeypatch,
        manager_harness.module,
        download_side_effect=fake_download,
    )

    # Act: importa um nome canônico sem realizar rede real.
    info = manager_harness.manager.import_from_hf(
        CANONICAL_MODEL_ID,
        filename="model.litertlm",
    )

    # Assert: o Hub fake recebe destino contido e o modelo fica utilizável.
    list_repo_files.assert_not_called()
    hf_hub_download.assert_called_once()
    call = hf_hub_download.call_args.kwargs
    expected_dir = manager_harness.cache_dir / CANONICAL_MODEL_ID.replace("/", "--")
    assert call["repo_id"] == CANONICAL_MODEL_ID
    assert Path(call["local_dir"]) == expected_dir
    assert call["local_dir_use_symlinks"] is False
    assert Path(call["local_dir"]).resolve().is_relative_to(
        manager_harness.cache_dir.resolve()
    )
    assert info.model_id == CANONICAL_MODEL_ID
    assert Path(info.model_path).read_bytes() == payload
    assert manager_harness.manager.find_model(CANONICAL_MODEL_ID) is not None


def test_delete_model_preserva_id_canonico_dentro_do_cache(
    manager_harness: _ManagerHarness,
) -> None:
    """CA26 positivo: exclusão de modelo canônico contido continua válida."""

    # Arrange: cria uma árvore regular de modelo no cache temporário.
    model_file = _create_cached_model(manager_harness)
    model_dir = model_file.parent

    # Act: exclui pelo ID canônico.
    removed = manager_harness.manager.delete_model(CANONICAL_MODEL_ID)

    # Assert: somente a árvore do modelo é removida; a raiz do cache permanece.
    assert removed is True
    assert not model_dir.exists()
    assert manager_harness.cache_dir.is_dir()


@pytest.mark.parametrize(
    "confirmation_fields",
    [
        pytest.param({}, id="confirm-omitido"),
        pytest.param({"confirm": False}, id="confirm-false"),
        pytest.param({"confirm": None}, id="confirm-none"),
        pytest.param({"confirm": "true"}, id="confirm-textual"),
        pytest.param({"confirm": 1}, id="confirm-inteiro"),
    ],
)
def test_agent_delete_sem_confirm_true_falha_sem_chamar_skill(
    confirmation_fields: dict[str, object],
) -> None:
    """CA26 negativo: somente o booleano literal ``confirm=True`` autoriza."""

    # Arrange: a skill é um double que tornaria qualquer delegação observável.
    agent_module = importlib.import_module("skills.litert_lm.agent")
    skill = mock.Mock(name="LiteRTLMSkill")
    skill.delete_model.return_value = True
    agent = agent_module.LiteRTLMAgent(skill=skill)
    context = {
        "action": "delete",
        "model_ref": CANONICAL_MODEL_ID,
        **confirmation_fields,
    }

    # Act: solicita delete sem confirmação booleana explícita.
    result = agent.execute(context)

    # Assert: a operação falha fechada antes de alcançar a skill destrutiva.
    skill.delete_model.assert_not_called()
    assert result["ok"] is False
    assert "confirm" in result["error"].casefold()


def test_agent_delete_com_confirm_true_chama_skill_uma_vez() -> None:
    """CA26 positivo: confirmação explícita permite a exclusão solicitada."""

    # Arrange: configura uma skill local com retorno determinístico.
    agent_module = importlib.import_module("skills.litert_lm.agent")
    skill = mock.Mock(name="LiteRTLMSkill")
    skill.delete_model.return_value = True
    agent = agent_module.LiteRTLMAgent(skill=skill)
    context = {
        "action": "delete",
        "model_ref": CANONICAL_MODEL_ID,
        "confirm": True,
    }

    # Act: executa o delete com confirmação booleana explícita.
    result = agent.execute(context)

    # Assert: a delegação ocorre uma única vez e preserva o envelope público.
    skill.delete_model.assert_called_once_with(CANONICAL_MODEL_ID)
    assert result == {
        "ok": True,
        "removed": True,
        "model": CANONICAL_MODEL_ID,
    }
