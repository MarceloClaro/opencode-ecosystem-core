# -*- coding: utf-8 -*-
"""
ModelManager — Descoberta, Cache e Gerenciamento de Modelos LiteRT-LM
=====================================================================
Gerencia o diretório ~/.litert-lm/models/ com operações CRUD para modelos
.litertlm baixados do HuggingFace ou convertidos localmente.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Tenta importar huggingface_hub (falha silenciosa) ─────────────────────────

try:
    import huggingface_hub as _huggingface_hub
    _HF_AVAILABLE = True
except ImportError:
    _huggingface_hub = None
    _HF_AVAILABLE = False


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

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _model_id_to_dirname(model_id: str) -> str:
        """Converte 'org/model' → 'org--model'."""
        return model_id.replace("/", "--")

    @staticmethod
    def _dirname_to_model_id(dirname: str) -> str:
        """Converte 'org--model' → 'org/model'."""
        return dirname.replace("--", "/", 1) if "--" in dirname else dirname

    def _model_dir(self, model_id: str) -> str:
        """Retorna o caminho do diretório de um modelo."""
        return os.path.join(self.models_dir, self._model_id_to_dirname(model_id))

    def _find_litertlm_file(self, directory: str) -> Optional[str]:
        """Procura recursivamente por um arquivo .litertlm em ``directory``.

        Retorna o caminho completo do primeiro arquivo .litertlm encontrado,
        ou None se nenhum existir.
        """
        if not os.path.isdir(directory):
            return None
        # Varredura recursiva limitada (máx 4 níveis)
        for root, dirs, files in os.walk(directory, topdown=True):
            for f in sorted(files):
                if f.endswith(".litertlm"):
                    return os.path.join(root, f)
            # Limita profundidade para não percorrer .cache
            depth = root.replace(directory, "").count(os.sep)
            if depth >= 3:
                dirs.clear()
        return None

    def _model_path(self, model_id: str) -> str:
        """Retorna o caminho para o arquivo .litertlm no diretório do modelo.

        Tenta 'model.litertlm' primeiro; se não existir, busca recursivamente
        por qualquer arquivo .litertlm dentro do diretório.
        """
        model_dir = self._model_dir(model_id)
        expected = os.path.join(model_dir, "model.litertlm")
        if os.path.isfile(expected):
            return expected
        found = self._find_litertlm_file(model_dir)
        return found if found else expected  # fallback (vai falhar com FileNotFound)

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

        for entry in sorted(os.listdir(self.models_dir)):
            entry_path = os.path.join(self.models_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            found = self._find_litertlm_file(entry_path)
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
        # Tenta como caminho absoluto primeiro
        if os.path.isfile(ref) and ref.endswith(".litertlm"):
            # Extrai model_id do caminho
            parent = os.path.basename(os.path.dirname(ref))
            model_id = self._dirname_to_model_id(parent)
            return ModelInfo(
                model_id=model_id,
                model_path=os.path.abspath(ref),
                file_size_bytes=os.path.getsize(ref),
            )

        # Tenta como model_id
        model_path = self._model_path(ref)
        if os.path.isfile(model_path):
            return ModelInfo(
                model_id=ref,
                model_path=os.path.abspath(model_path),
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
        model_dir = self._model_dir(model_id)
        if os.path.isdir(model_dir):
            shutil.rmtree(model_dir)
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
        global _huggingface_hub, _HF_AVAILABLE
        if not _HF_AVAILABLE:
            raise ImportError(
                "huggingface_hub não está instalado. "
                "Execute: pip install huggingface-hub"
            )

        # Descobre filename se não informado
        if filename is None:
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

        # Garante que o diretório de destino existe
        dest_dir = self._model_dir(repo_id)
        os.makedirs(dest_dir, exist_ok=True)

        # Download para o diretório local
        local_path = _huggingface_hub.hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=token,
            local_dir=dest_dir,
            local_dir_use_symlinks=False,
        )

        file_size = os.path.getsize(local_path) if os.path.isfile(local_path) else 0
        return ModelInfo(
            model_id=repo_id,
            model_path=os.path.abspath(local_path),
            file_size_bytes=file_size,
        )
