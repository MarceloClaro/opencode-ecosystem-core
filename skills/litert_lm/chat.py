# -*- coding: utf-8 -*-
"""
ChatSession — Interface Conversacional Interativa para LiteRT-LM
=================================================================
Gerencia uma sessão de chat com streaming, tool use, multimodalidade e
histórico de mensagens.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from .model_manager import ModelNotFoundError


# ── Tenta importar litert_lm com fallback ─────────────────────────────────────

try:
    import litert_lm

    _LITERT_AVAILABLE = True
except ImportError:
    _LITERT_AVAILABLE = False


# ── ChatSession ───────────────────────────────────────────────────────────────


class ChatSession:
    """Sessão de chat conversacional com modelo LiteRT-LM.

    Uso:
        session = ChatSession("modelo.litertlm")
        resposta = session.send("Olá!")
        print(resposta)

        # Streaming
        session = ChatSession("modelo.litertlm", stream=True)
        for chunk in session.send("Olá!"):
            print(chunk)
    """

    def __init__(
        self,
        model_path: str,
        *,
        stream: bool = False,
        backend: str = "cpu",
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = None,
        max_tokens: Optional[int] = None,
        max_num_images: int = 0,
        vision_backend: Optional[str] = None,
        cache: str = "disk",
        preset_tools: Optional[List[Callable]] = None,
        system_instruction: Optional[str] = None,
        no_template: bool = False,
        verbose: bool = False,
    ):
        """Inicializa sessão de chat.

        Args:
            model_path: Caminho para o arquivo .litertlm.
            stream: Se True, send() retorna iterador de chunks.
            backend: Backend de inferência ("cpu", "gpu", "npu").
            temperature: Temperatura de amostragem (None = padrão do modelo).
            top_k: Top-K para amostragem.
            top_p: Top-P para nucleus sampling.
            seed: Seed para reprodutibilidade.
            max_tokens: Máximo de tokens de saída.
            max_num_images: Nº máx de imagens por mensagem (0 = desligado).
            vision_backend: Backend para encoder de visão ("cpu", "gpu", None=auto).
            cache: Modo de cache ("none", "memory", "disk").
            preset_tools: Lista de funções para tool use.
            system_instruction: Instrução de sistema para o chat.
            no_template: Se True, interage sem template de prompt.
            verbose: Logs detalhados.
        """
        self.model_path = model_path
        self.stream = stream
        self.backend = backend
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.seed = seed
        self.max_tokens = max_tokens
        self.max_num_images = max_num_images
        self.vision_backend = vision_backend
        self.cache = cache
        self.preset_tools = preset_tools or []
        self.system_instruction = system_instruction
        self.no_template = no_template
        self.verbose = verbose

        self._engine = None
        self._conversation = None
        self._session = None
        self._history: List[Dict[str, Any]] = []
        self._initialized = False

    # ── Propriedades ─────────────────────────────────────────────────────

    @property
    def history(self) -> List[Dict[str, Any]]:
        """Histórico de mensagens da sessão."""
        return list(self._history)

    # ── Inicialização ─────────────────────────────────────────────────────

    def _ensure_initialized(self):
        """Inicializa Engine e Conversation sob demanda."""
        if self._initialized:
            return

        if not _LITERT_AVAILABLE:
            raise RuntimeError(
                "litert_lm não está instalado. Execute: pip install litert-lm"
            )

        if not os.path.isfile(self.model_path):
            raise ModelNotFoundError(
                f"Modelo não encontrado: {self.model_path}"
            )

        # Configura sampler
        sampler_config = None
        if any(x is not None for x in [self.top_k, self.top_p, self.temperature, self.seed]):
            sampler_config = litert_lm.SamplerConfig(
                top_k=self.top_k,
                top_p=self.top_p,
                temperature=self.temperature,
                seed=self.seed,
            )

        # Resolve backend (com fallback para CPU se NPU não for suportado)
        try:
            backend_map = {
                "cpu": litert_lm.Backend.CPU(),
                "gpu": litert_lm.Backend.GPU(),
                "npu": litert_lm.Backend.NPU(),
            }
            backend_obj = backend_map.get(self.backend.lower(), litert_lm.Backend.CPU())
        except RuntimeError:
            if self.backend.lower() == "npu":
                import logging
                logging.warning("NPU não suportado nesta plataforma. Usando CPU.")
            backend_obj = litert_lm.Backend.CPU()

        # Define contexto do Engine (total: input + output)
        # Se o usuário não especificou max_tokens, usa 4096 (padrão LiteRT-LM)
        engine_context = self.max_tokens if self.max_tokens is not None else 4096
        # Garante que o contexto mínimo é 2048 (modelos pequenos podem ter menos,
        # mas precisamos de espaço para o input)
        if engine_context < 2048:
            engine_context = 2048

        # Resolve vision_backend
        # Se imagens foram solicitadas, ativa visão mesmo sem backend explícito
        vision_backend_obj = None
        if self.max_num_images > 0:
            vb_spec = self.vision_backend or "cpu"
            try:
                vb_map = {
                    "cpu": litert_lm.Backend.CPU(),
                    "gpu": litert_lm.Backend.GPU(),
                    "npu": litert_lm.Backend.NPU(),
                }
                vision_backend_obj = vb_map.get(
                    vb_spec.lower(), litert_lm.Backend.CPU()
                )
            except RuntimeError:
                if vb_spec.lower() == "npu":
                    import logging
                    logging.warning(
                        "NPU não suportado para vision_backend. Usando CPU."
                    )
                vision_backend_obj = litert_lm.Backend.CPU()

        # Cria Engine
        cache_dir = ""
        if self.cache == "disk":
            cache_dir = os.path.expanduser("~/.litert-lm/cache")
            os.makedirs(cache_dir, exist_ok=True)

        self._engine = litert_lm.Engine(
            self.model_path,
            backend=backend_obj,
            max_num_tokens=engine_context,
            max_num_images=self.max_num_images,
            vision_backend=vision_backend_obj,
            cache_dir=cache_dir,
        )
        self._engine.__enter__()

        # Cria Conversation ou Session
        if self.no_template:
            self._session = self._engine.create_session(
                apply_prompt_template=False,
                sampler_config=sampler_config,
                max_output_tokens=self.max_tokens,  # output limit
            )
            self._session.__enter__()
        else:
            tools = self.preset_tools if self.preset_tools else None
            messages = None
            if self.system_instruction:
                messages = [{
                    "role": "system",
                    "content": [{"type": "text", "text": self.system_instruction}],
                }]

            self._conversation = self._engine.create_conversation(
                tools=tools,
                messages=messages,
                sampler_config=sampler_config,
                max_output_tokens=self.max_tokens,  # output limit
            )
            self._conversation.__enter__()

        self._initialized = True

    # ── Envio de Mensagens ────────────────────────────────────────────────

    def send(
        self,
        message: str,
        attachments: Optional[List[str]] = None,
    ) -> Union[str, Iterator[Dict[str, Any]]]:
        """Envia uma mensagem e retorna a resposta.

        Args:
            message: Texto da mensagem.
            attachments: Lista de caminhos para attachments (imagem/áudio).

        Returns:
            Se stream=False: string com a resposta completa.
            Se stream=True: iterador de chunks.
        """
        self._ensure_initialized()

        attachments = attachments or []

        if self._session:
            # Modo raw session (no_template)
            self._session.run_prefill([message])
            stream = self._session.run_decode_async()

            if self.stream:
                return stream

            text = ""
            for chunk in stream:
                if hasattr(chunk, "texts") and chunk.texts:
                    text += chunk.texts[0]
            self._history.append({"role": "user", "content": message})
            self._history.append({"role": "assistant", "content": text})
            return text

        else:
            # Modo conversation
            if attachments:
                content = []
                for path in attachments:
                    abs_path = os.path.abspath(path)
                    content.append({
                        "type": self._get_attachment_type(abs_path),
                        "path": abs_path,
                    })
                if message:
                    content.append({"type": "text", "text": message})
                msg = {"role": "user", "content": content}
            else:
                msg = message

            if self.stream:
                return self._conversation.send_message_async(msg)

            # Síncrono: send_message retorna dict completo
            response = self._conversation.send_message(msg)
            text = self._extract_text(response)

            self._history.append({"role": "user", "content": message})
            self._history.append({"role": "assistant", "content": text})
            return text

    def cancel(self):
        """Cancela a geração em andamento."""
        if self._conversation is not None:
            try:
                self._conversation.cancel_process()
            except Exception:
                pass

    def close(self):
        """Fecha a sessão e libera recursos."""
        try:
            if self._conversation is not None:
                self._conversation.__exit__(None, None, None)
                self._conversation = None
            if self._session is not None:
                self._session.__exit__(None, None, None)
                self._session = None
            if self._engine is not None:
                self._engine.__exit__(None, None, None)
                self._engine = None
        except Exception:
            pass
        self._initialized = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(response: Mapping[str, Any]) -> str:
        """Extrai texto de uma resposta da Conversation."""
        content_list = response.get("content", [])
        if isinstance(content_list, list):
            parts = []
            for item in content_list:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "".join(parts)
        return str(content_list)

    @staticmethod
    def _get_attachment_type(path: str) -> str:
        """Detecta tipo de attachment por extensão."""
        ext = os.path.splitext(path)[1].lower()
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
        audio_exts = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
        if ext in image_exts:
            return "image"
        if ext in audio_exts:
            return "audio"
        return "text"
