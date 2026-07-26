# -*- coding: utf-8 -*-
"""
ModelManager — Descoberta, Cache e Gerenciamento de Modelos LiteRT-LM
=====================================================================
Gerencia o diretório ~/.litert-lm/models/ com operações CRUD para modelos
.litertlm baixados do HuggingFace ou convertidos localmente.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, List, Optional


# ── Tenta importar huggingface_hub (dependência opcional) ─────────────────────

_HUGGINGFACE_INSTALL_MESSAGE = (
    "huggingface_hub não está instalado. "
    "Execute: pip install huggingface-hub"
)


def _missing_huggingface_method(*args: Any, **kwargs: Any) -> None:
    """Expõe um ponto de integração patchável sem instalar o Hub.

    O marcador na função permite distinguir o placeholder de um método que foi
    substituído por ``unittest.mock.patch``. Assim, os testes e integrações que
    não acessam a rede continuam podendo injetar somente os métodos usados.
    """
    raise ImportError(_HUGGINGFACE_INSTALL_MESSAGE)


_missing_huggingface_method._litert_missing_dependency = True  # type: ignore[attr-defined]


class _UnavailableHuggingFaceHub:
    """Superfície mínima mockável para uma dependência ausente."""

    list_repo_files = _missing_huggingface_method
    hf_hub_download = _missing_huggingface_method


_HUGGINGFACE_MODULE_BLOCKED = (
    "huggingface_hub" in sys.modules
    and sys.modules["huggingface_hub"] is None
)

try:
    import huggingface_hub as _huggingface_hub
    _HF_AVAILABLE = True
except ImportError:
    _HF_AVAILABLE = False
    # Quando o import é explicitamente bloqueado (como em ambientes que
    # simulam a ausência do pacote), preserva-se ``None`` para diagnóstico.
    # Em uma importação normal, o proxy mantém os atributos necessários para
    # que ``unittest.mock.patch`` possa injetar os métodos do Hub.
    _huggingface_hub = (
        None
        if _HUGGINGFACE_MODULE_BLOCKED
        else _UnavailableHuggingFaceHub()
    )


def _hub_method_is_usable(name: str) -> bool:
    """Retorna se um método do Hub é real ou foi substituído por um mock."""
    if _huggingface_hub is None:
        return False
    if _HF_AVAILABLE:
        return True

    method = getattr(_huggingface_hub, name, None)
    if method is None:
        return False

    # Métodos ligados expõem o marcador em ``__func__``; mocks instalados no
    # objeto expõem diretamente o atributo substituído.
    if getattr(method, "_litert_missing_dependency", False) is True:
        return False
    function = getattr(method, "__func__", None)
    return getattr(function, "_litert_missing_dependency", False) is not True


def _require_hub_method(name: str) -> None:
    """Garante uma integração real ou explicitamente mockada com o Hub."""
    if not _hub_method_is_usable(name):
        raise ImportError(_HUGGINGFACE_INSTALL_MESSAGE)


_MODEL_ID_MAX_LENGTH = 96
_MODEL_ID_COMPONENT = re.compile(r"[A-Za-z0-9._-]+")


# ── Exceções ──────────────────────────────────────────────────────────────────


class ModelNotFoundError(FileNotFoundError):
    """Levantado quando um modelo solicitado não é encontrado no cache local."""
    pass


# ── Dataclasses ───────────────────────────────────────────────────────────────


@dataclass
class ModelInfo:
    """Informações resumidas de um modelo LiteRT-LM.

    Attributes:
        model_id: Identificador único (ex.: "litert-community/gemma-4-E2B-it").
        model_path: Caminho absoluto para o arquivo .litertlm.
        file_size_bytes: Tamanho do arquivo em bytes (0 se indisponível).
        backend_sugerido: Backend recomendado pelo modelo ("cpu", "gpu", "npu").
    """
    model_id: str
    model_path: str
    file_size_bytes: int = 0
    backend_sugerido: str = "cpu"


# ── ModelManager ──────────────────────────────────────────────────────────────


class ModelManager:
    """Gerencia o diretório de modelos LiteRT-LM.

    O diretório padrão é ~/.litert-lm/models/. Cada modelo reside em uma
    subpasta nomeada pelo model_id com "/" substituído por "--", contendo
    um arquivo model.litertlm.
    """

    def __init__(self, models_dir: Optional[str] = None):
        """Inicializa o gerenciador.

        Args:
            models_dir: Caminho para o diretório de modelos. Se None, usa
                a variável de ambiente LITERT_LM_MODELS_DIR ou ~/.litert-lm/models.
        """
        self.models_dir = models_dir or os.environ.get(
            "LITERT_LM_MODELS_DIR",
            os.path.expanduser("~/.litert-lm/models"),
        )
        os.makedirs(self.models_dir, exist_ok=True)
        self._models_root = Path(self.models_dir).resolve()

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _is_absolute_reference(value: str) -> bool:
        """Reconhece caminhos absolutos POSIX e Windows sem acessar o disco."""
        return (
            PurePosixPath(value).is_absolute()
            or PureWindowsPath(value).is_absolute()
        )

    @staticmethod
    def _validate_model_id(model_id: str) -> str:
        """Valida a gramática canônica e não ambígua de um ID de modelo.

        A validação é puramente léxica para que entradas inválidas sejam
        rejeitadas antes de qualquer consulta ao filesystem ou ao Hub.
        """
        if not isinstance(model_id, str):
            raise ValueError("ID de modelo inválido: esperado texto")
        if not model_id or model_id != model_id.strip():
            raise ValueError("ID de modelo inválido: valor vazio ou não canônico")
        if "\x00" in model_id or "\\" in model_id:
            raise ValueError("ID de modelo inválido: caractere proibido")
        if ModelManager._is_absolute_reference(model_id):
            raise ValueError("ID de modelo inválido: caminho absoluto não é permitido")
        if len(model_id) > _MODEL_ID_MAX_LENGTH:
            raise ValueError("ID de modelo inválido: comprimento excede 96 caracteres")

        components = model_id.split("/")
        if len(components) > 2 or any(
            not component or component in {".", ".."}
            for component in components
        ):
            raise ValueError("ID de modelo inválido: estrutura não canônica")
        if ".." in model_id or "--" in model_id:
            raise ValueError("ID de modelo inválido: sequência ambígua")
        if any(
            _MODEL_ID_COMPONENT.fullmatch(component) is None
            or component[0] in ".-"
            or component[-1] in ".-"
            for component in components
        ):
            raise ValueError("ID de modelo inválido: componente não canônico")
        return model_id

    def _resolve_contained_path(
        self,
        path: Path,
        *,
        boundary: Optional[Path] = None,
    ) -> Path:
        """Resolve ``path`` e garante contenção, sem aceitar symlink final."""
        candidate = Path(path)
        try:
            resolved = candidate.resolve()
            is_symlink = candidate.is_symlink()
            safe_boundary = (
                Path(boundary).resolve()
                if boundary is not None
                else self._models_root
            )
        except (OSError, RuntimeError) as error:
            raise ValueError(f"Caminho de modelo inválido: {path}") from error

        if not safe_boundary.is_relative_to(self._models_root):
            raise ValueError("Limite de modelo escapa do cache configurado")
        if is_symlink:
            raise ValueError(f"Link simbólico de modelo não permitido: {path}")
        if not resolved.is_relative_to(safe_boundary):
            raise ValueError(f"Caminho de modelo escapa do cache: {path}")
        return resolved

    def _validated_model_dir(self, model_id: str) -> Path:
        """Converte um ID validado em diretório resolvido dentro do cache."""
        canonical_id = self._validate_model_id(model_id)
        candidate = self._models_root / canonical_id.replace("/", "--")
        return self._resolve_contained_path(candidate)

    def _validated_download_path(self, model_dir: Path, filename: str) -> Path:
        """Garante que o nome remoto permaneça dentro do diretório do modelo."""
        if not isinstance(filename, str) or not filename:
            raise ValueError("Nome de arquivo de modelo inválido")
        if "\x00" in filename or "\\" in filename:
            raise ValueError("Nome de arquivo de modelo contém caractere proibido")
        if self._is_absolute_reference(filename):
            raise ValueError("Nome de arquivo de modelo não pode ser absoluto")

        components = filename.split("/")
        if any(component in {"", ".", ".."} for component in components):
            raise ValueError("Nome de arquivo de modelo contém travessia")
        return self._resolve_contained_path(
            model_dir.joinpath(*components),
            boundary=model_dir,
        )

    @staticmethod
    def _model_id_to_dirname(model_id: str) -> str:
        """Converte 'org/model' → 'org--model'."""
        return ModelManager._validate_model_id(model_id).replace("/", "--")

    @staticmethod
    def _dirname_to_model_id(dirname: str) -> str:
        """Converte 'org--model' → 'org/model'."""
        return dirname.replace("--", "/", 1) if "--" in dirname else dirname

    def _model_dir(self, model_id: str) -> str:
        """Retorna o caminho do diretório de um modelo."""
        return str(self._validated_model_dir(model_id))

    def _find_litertlm_file(self, directory: str) -> Optional[str]:
        """Procura recursivamente por um arquivo .litertlm em ``directory``.

        Retorna o caminho completo do primeiro arquivo .litertlm encontrado,
        ou None se nenhum existir.
        """
        safe_directory = self._resolve_contained_path(Path(directory))
        if not os.path.isdir(safe_directory):
            return None
        # Varredura recursiva limitada (máx 4 níveis)
        for root, dirs, files in os.walk(safe_directory, topdown=True):
            root_path = self._resolve_contained_path(
                Path(root),
                boundary=safe_directory,
            )
            # ``os.walk`` não segue links por padrão, mas removê-los
            # explicitamente evita que uma mudança futura reabra esse vetor.
            dirs[:] = sorted(
                directory_name
                for directory_name in dirs
                if not (root_path / directory_name).is_symlink()
            )
            for f in sorted(files):
                if f.endswith(".litertlm"):
                    return str(
                        self._resolve_contained_path(
                            root_path / f,
                            boundary=safe_directory,
                        )
                    )
            # Limita profundidade para não percorrer .cache
            depth = len(root_path.relative_to(safe_directory).parts)
            if depth >= 3:
                dirs.clear()
        return None

    def _model_path(self, model_id: str) -> str:
        """Retorna o caminho para o arquivo .litertlm no diretório do modelo.

        Tenta 'model.litertlm' primeiro; se não existir, busca recursivamente
        por qualquer arquivo .litertlm dentro do diretório.
        """
        model_dir = Path(self._model_dir(model_id))
        expected = self._resolve_contained_path(
            model_dir / "model.litertlm",
            boundary=model_dir,
        )
        if os.path.isfile(expected):
            return str(expected)
        found = self._find_litertlm_file(str(model_dir))
        return found if found else str(expected)  # fallback (vai falhar com FileNotFound)

    # ── CRUD ─────────────────────────────────────────────────────────────

    def list_models(self) -> List[ModelInfo]:
        """Lista todos os modelos disponíveis localmente.

        Percorre o diretório models_dir procurando subpastas que contenham
        um arquivo .litertlm (busca recursiva).

        Returns:
            Lista de ModelInfo com os modelos encontrados.
        """
        models: List[ModelInfo] = []
        if not os.path.isdir(self.models_dir):
            return models

        for entry in sorted(os.listdir(self._models_root)):
            try:
                entry_path = self._resolve_contained_path(self._models_root / entry)
            except ValueError:
                continue
            if not os.path.isdir(entry_path):
                continue
            found = self._find_litertlm_file(str(entry_path))
            if found is None:
                continue
            model_id = self._dirname_to_model_id(entry)
            file_size = os.path.getsize(found)
            models.append(ModelInfo(
                model_id=model_id,
                model_path=os.path.abspath(found),
                file_size_bytes=file_size,
            ))
        return models

    def find_model(self, ref: str) -> Optional[ModelInfo]:
        """Localiza um modelo por ID ou caminho.

        Args:
            ref: Model ID ("org/model") ou caminho absoluto para .litertlm.

        Returns:
            ModelInfo se encontrado, None caso contrário.
        """
        if not isinstance(ref, str) or "\x00" in ref or "\\" in ref:
            raise ValueError("Referência de modelo inválida")

        # Caminhos legados só são aceitos para artefatos contidos no cache.
        if self._is_absolute_reference(ref):
            if not ref.endswith(".litertlm"):
                raise ValueError(
                    "Referência absoluta deve apontar para arquivo .litertlm"
                )
            model_path = self._resolve_contained_path(Path(ref))
            if not os.path.isfile(model_path):
                return None
            # Extrai model_id do caminho
            parent = model_path.parent.name
            model_id = self._dirname_to_model_id(parent)
            return ModelInfo(
                model_id=model_id,
                model_path=str(model_path),
                file_size_bytes=os.path.getsize(model_path),
            )

        # Tenta como model_id
        model_id = self._validate_model_id(ref)
        model_path = self._model_path(model_id)
        if os.path.isfile(model_path):
            return ModelInfo(
                model_id=model_id,
                model_path=str(Path(model_path).resolve()),
                file_size_bytes=os.path.getsize(model_path),
            )

        return None

    def inspect(self, model_path: str) -> Dict[str, Any]:
        """Inspeciona metadados de um arquivo .litertlm.

        Args:
            model_path: Caminho para o arquivo .litertlm.

        Returns:
            Dicionário com metadados básicos (file_size_bytes, model_id extraído).

        Raises:
            FileNotFoundError: Se o arquivo não existir.
        """
        if not os.path.isfile(model_path):
            raise FileNotFoundError(
                f"Arquivo de modelo não encontrado: {model_path}"
            )

        file_size = os.path.getsize(model_path)
        parent = os.path.basename(os.path.dirname(model_path))
        model_id = self._dirname_to_model_id(parent)

        return {
            "model_id": model_id,
            "model_path": os.path.abspath(model_path),
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "directory": os.path.dirname(os.path.abspath(model_path)),
        }

    def delete_model(self, model_id: str) -> bool:
        """Remove um modelo do cache local.

        Args:
            model_id: ID do modelo a remover.

        Returns:
            True se removido com sucesso, False se não existia.
        """
        model_dir = Path(self._model_dir(model_id))
        if os.path.isdir(model_dir):
            # Revalida imediatamente antes da primitiva destrutiva.
            safe_model_dir = self._resolve_contained_path(model_dir)
            shutil.rmtree(safe_model_dir)
            return True
        return False

    def import_from_hf(
        self,
        repo_id: str,
        filename: Optional[str] = None,
        token: Optional[str] = None,
    ) -> ModelInfo:
        """Importa um modelo do HuggingFace Hub.

        Usa huggingface_hub.hf_hub_download para baixar o arquivo .litertlm
        para o diretório de modelos local. Se ``filename`` não for informado,
        descobre automaticamente o primeiro arquivo .litertlm no repositório.

        Args:
            repo_id: ID do repositório no HuggingFace (ex.: "litert-community/...").
            filename: Nome do arquivo no repositório (opcional — auto-descoberta).
            token: Token de acesso opcional (para modelos privados/gated).

        Returns:
            ModelInfo do modelo baixado.

        Raises:
            ImportError: Se huggingface_hub não estiver instalado.
            ValueError: Se nenhum arquivo .litertlm for encontrado no repositório.
            Exception: Erros do download.
        """
        # ID e destino são validados antes de qualquer integração com o Hub.
        dest_dir = Path(self._model_dir(repo_id))

        # Descobre filename se não informado
        if filename is None:
            _require_hub_method("list_repo_files")
            try:
                files = _huggingface_hub.list_repo_files(repo_id, token=token)
            except Exception:
                files = []
            litert_files = [f for f in files if f.endswith(".litertlm")]
            if not litert_files:
                raise ValueError(
                    f"Nenhum arquivo .litertlm encontrado no repositório {repo_id}. "
                    f"Arquivos disponíveis: {files[:10]}"
                )
            filename = litert_files[0]
            print(f"Arquivo detectado: {filename}")

        download_path = self._validated_download_path(dest_dir, filename)
        _require_hub_method("hf_hub_download")

        # Garante que o diretório de destino existe
        os.makedirs(dest_dir, exist_ok=True)
        dest_dir = Path(self._model_dir(repo_id))
        download_path = self._validated_download_path(dest_dir, filename)

        # Download para o diretório local
        _huggingface_hub.hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=token,
            local_dir=str(dest_dir),
            local_dir_use_symlinks=False,
        )

        # Não confia no caminho retornado pela integração: deriva novamente o
        # artefato do destino validado e detecta symlink criado no download.
        download_path = self._validated_download_path(dest_dir, filename)
        file_size = (
            os.path.getsize(download_path)
            if os.path.isfile(download_path)
            else 0
        )
        return ModelInfo(
            model_id=repo_id,
            model_path=str(download_path),
            file_size_bytes=file_size,
        )
