# -*- coding: utf-8 -*-
"""
LiteRTLMSkill — Orquestrador Central da Skill LiteRT-LM
========================================================
Expõe todas as operações de alto nível: listar, executar, conversar,
importar, servir, inspecionar e remover modelos LiteRT-LM.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional, Union

from .chat import ChatSession
from .model_manager import ModelInfo, ModelManager, ModelNotFoundError
from .server import LiteRTOpenAIServer


# ── Tenta importar litert_lm ──────────────────────────────────────────────────

try:
    import litert_lm as _litert_lm

    _LITERT_AVAILABLE = True
except ImportError:
    _LITERT_AVAILABLE = False


# ── LiteRTLMSkill ─────────────────────────────────────────────────────────────


class LiteRTLMSkill:
    """Orquestrador da skill LiteRT-LM.

    Encapsula ModelManager, ChatSession e LiteRTOpenAIServer em uma
    interface unificada.

    Uso:
        skill = LiteRTLMSkill()
        skill.list_models()
        skill.run("gemma-4-E2B-it", "Qual a capital da França?")
    """

    def __init__(
        self,
        models_dir: Optional[str] = None,
        verbose: bool = False,
    ):
        """Inicializa o orquestrador.

        Args:
            models_dir: Diretório de modelos. Default: ~/.litert-lm/models.
            verbose: Logs detalhados.
        """
        self.verbose = verbose
        self._model_manager = ModelManager(models_dir=models_dir)

    # ─── Gerenciamento de Modelos ─────────────────────────────────────────

    @property
    def model_manager(self) -> ModelManager:
        """Acessa o gerenciador de modelos subjacente."""
        return self._model_manager

    def list_models(self) -> List[ModelInfo]:
        """Lista modelos disponíveis localmente.

        Returns:
            Lista de ModelInfo.
        """
        return self._model_manager.list_models()

    def inspect(self, model_ref: str) -> Dict[str, Any]:
        """Inspeciona metadados de um modelo.

        Args:
            model_ref: ID do modelo ou caminho para .litertlm.

        Returns:
            Dicionário com metadados.
        """
        # Tenta encontrar o caminho
        info = self._model_manager.find_model(model_ref)
        if info:
            return self._model_manager.inspect(info.model_path)
        if os.path.isfile(model_ref) and model_ref.endswith(".litertlm"):
            return self._model_manager.inspect(model_ref)
        raise ModelNotFoundError(
            f"Modelo não encontrado: {model_ref}. "
            "Use 'litert-lm list' para ver os disponíveis."
        )

    def delete_model(self, model_ref: str) -> bool:
        """Remove um modelo do cache.

        Args:
            model_ref: ID do modelo.

        Returns:
            True se removido, False se não existia.
        """
        return self._model_manager.delete_model(model_ref)

    def import_model(
        self,
        repo_id: str,
        filename: str = "model.litertlm",
        token: Optional[str] = None,
    ) -> ModelInfo:
        """Importa modelo do HuggingFace.

        Args:
            repo_id: Repositório HF (ex.: "litert-community/...").
            filename: Nome do arquivo no repo.
            token: Token de acesso (opcional).

        Returns:
            ModelInfo do modelo importado.
        """
        return self._model_manager.import_from_hf(
            repo_id=repo_id,
            filename=filename,
            token=token,
        )

    # ─── Execução ─────────────────────────────────────────────────────────

    def run(
        self,
        model_ref: str,
        prompt: str,
        *,
        backend: str = "cpu",
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        max_tokens: Optional[int] = None,
        cache: str = "disk",
        no_template: bool = False,
        chat_template: Optional[str] = None,
        speculative_decoding: Optional[bool] = None,
    ) -> str:
        """Executa um prompt único em um modelo e retorna a resposta.

        Args:
            model_ref: ID ou caminho do modelo.
            prompt: Texto do prompt.
            backend: Backend de inferência.
            temperature: Temperatura.
            top_k: Top-K.
            top_p: Top-P.
            seed: Seed aleatória.
            max_tokens: Máximo de tokens de saída.
            cache: Modo de cache.
            no_template: Ignorar template de prompt.
            chat_template: Template Jinja personalizado.
            speculative_decoding: Decodificação especulativa.

        Returns:
            Texto da resposta do modelo.
        """
        # Resolve o modelo
        info = self._resolve_model(model_ref)

        # Cria sessão de chat com uma única troca
        with ChatSession(
            info.model_path,
            stream=False,
            backend=backend,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            seed=seed,
            max_tokens=max_tokens,
            cache=cache,
            no_template=no_template,
            chat_template=chat_template,
            verbose=self.verbose,
        ) as session:
            return session.send(prompt)

    def chat(
        self,
        model_ref: str,
        *,
        backend: str = "cpu",
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        max_tokens: Optional[int] = None,
        cache: str = "disk",
        preset_tools: Optional[List[Callable]] = None,
        system_instruction: Optional[str] = None,
        chat_template: Optional[str] = None,
        no_template: bool = False,
        stream: bool = True,
    ) -> ChatSession:
        """Inicia uma sessão de chat interativa.

        Args:
            model_ref: ID ou caminho do modelo.
            backend: Backend de inferência.
            temperature: Temperatura.
            top_k: Top-K.
            top_p: Top-P.
            seed: Seed aleatória.
            max_tokens: Máximo de tokens.
            cache: Modo de cache.
            preset_tools: Ferramentas para tool use.
            system_instruction: Instrução de sistema.
            chat_template: Template Jinja personalizado.
            no_template: Ignorar template.
            stream: Se True, streaming habilitado.

        Returns:
            ChatSession pronta para uso.
        """
        info = self._resolve_model(model_ref)

        return ChatSession(
            info.model_path,
            stream=stream,
            backend=backend,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            seed=seed,
            max_tokens=max_tokens,
            cache=cache,
            preset_tools=preset_tools,
            system_instruction=system_instruction,
            chat_template=chat_template,
            no_template=no_template,
            verbose=self.verbose,
        )

    def serve(
        self,
        model_ref: str,
        host: str = "0.0.0.0",
        port: int = 9379,
        backend: str = "cpu",
        cors_origins: Optional[List[str]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LiteRTOpenAIServer:
        """Inicia um servidor OpenAI-compatible.

        Args:
            model_ref: ID ou caminho do modelo.
            host: Host do servidor.
            port: Porta do servidor.
            backend: Backend de inferência.
            cors_origins: Origens CORS.
            max_tokens: Máximo de tokens.
            temperature: Temperatura padrão.

        Returns:
            Instância do servidor.
        """
        info = self._resolve_model(model_ref)

        return LiteRTOpenAIServer(
            info.model_path,
            model_name=info.model_id,
            host=host,
            port=port,
            backend=backend,
            cors_origins=cors_origins,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    # ─── Helpers Internos ─────────────────────────────────────────────────

    def _resolve_model(self, model_ref: str) -> ModelInfo:
        """Resolve uma referência de modelo para ModelInfo.

        Args:
            model_ref: ID, caminho, ou string de referência.

        Returns:
            ModelInfo do modelo encontrado.

        Raises:
            ModelNotFoundError: Se o modelo não for encontrado.
        """
        info = self._model_manager.find_model(model_ref)
        if info is None:
            # Tenta como caminho direto
            if os.path.isfile(model_ref) and model_ref.endswith(".litertlm"):
                return ModelInfo(
                    model_id=os.path.basename(os.path.dirname(model_ref)),
                    model_path=os.path.abspath(model_ref),
                )
            raise ModelNotFoundError(
                f"Modelo '{model_ref}' não encontrado.\n"
                f"  • Verifique se o nome está correto.\n"
                f"  • Use 'litert-lm list' para listar modelos disponíveis.\n"
                f"  • Use 'litert-lm import <repo>' para baixar do HuggingFace."
            )
        return info
