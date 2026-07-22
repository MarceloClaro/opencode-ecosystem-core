# -*- coding: utf-8 -*-
"""
LiteRT-LM Provider — Integração com modelos on-device via LiteRT-LM
===================================================================
Expõe os modelos locais executados pelo LiteRT-LM (Google AI Edge)
como um provider nativo do ecossistema OpenCode.

Modelos disponíveis (via litert-lm list):
  - litert-community/gemma-4-E2B-it-litert-lm (2B)
  - litert-community/gemma-4-E4B-it-litert-lm (4B)
  - litert-community/gemma-4-12B-it-litert-lm (12B)
  - litert-community/Qwen3-0.6B (586MB)

Funcionamento:
  - Inicia automaticamente o servidor litert-lm serve em background
    na porta 9379 se ele não estiver rodando
  - Comunica via API OpenAI-compatible (http://localhost:9379/v1)
  - Suporta /v1/models e /v1/chat/completions

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib import request as urllib_request
from urllib.error import URLError

logger = logging.getLogger("litert-lm-provider")

# ── Constantes ──────────────────────────────────────────────────────────────

PROVIDER_ID = "litert-lm"
BASE_URL = "http://localhost:9379/v1"
DEFAULT_MODEL = "litert-community/gemma-4-E2B-it-litert-lm"
LITERT_SERVE_PORT = 9379
LITERT_SERVE_HOST = "0.0.0.0"
SERVER_START_TIMEOUT = 120  # segundos máximos para inicialização do modelo

# ── Catálogo de modelos locais curado ──────────────────────────────────────

MODELS: Dict[str, Dict[str, Any]] = {
    "litert-community/gemma-4-E2B-it-litert-lm": {
        "name": "Gemma 4 E2B (2B)",
        "provider": PROVIDER_ID,
        "description": "Gemma 4 2B parâmetros, instrução-tuned, MTP",
        "size_gb": 2.4,
        "backend": "cpu",
        "tier": "fast",
        "context": 8192,
        "task_types": ["fast", "local", "writing"],
    },
    "litert-community/gemma-4-E4B-it-litert-lm": {
        "name": "Gemma 4 E4B (4B)",
        "provider": PROVIDER_ID,
        "description": "Gemma 4 4B parâmetros, instrução-tuned",
        "size_gb": 3.4,
        "backend": "cpu",
        "tier": "standard",
        "context": 8192,
        "task_types": ["fast", "local", "writing", "reasoning"],
    },
    "litert-community/gemma-4-12B-it-litert-lm": {
        "name": "Gemma 4 12B IT",
        "provider": PROVIDER_ID,
        "description": "Gemma 4 12B parâmetros, instrução-tuned",
        "size_gb": 6.1,
        "backend": "cpu",
        "tier": "premium",
        "context": 8192,
        "task_types": ["local", "reasoning", "coding", "writing"],
    },
    "litert-community/Qwen3-0.6B": {
        "name": "Qwen3 0.6B",
        "provider": PROVIDER_ID,
        "description": "Qwen3 0.6B parâmetros — modelo leve para testes",
        "size_gb": 0.58,
        "backend": "cpu",
        "tier": "fast",
        "context": 4096,
        "task_types": ["fast", "local"],
    },
}

# ── Estado do servidor ──────────────────────────────────────────────────────

_server_process: Optional[subprocess.Popen] = None
_server_ready: bool = False
_current_model: Optional[str] = None


# ── LiteRTLMProvider ───────────────────────────────────────────────────────


class LiteRTLMProvider:
    """Provider de inferência on-device via LiteRT-LM.

    Gerencia o ciclo de vida do servidor litert-lm e expõe
    interface compatível com o ModelRouter do ecossistema.
    """

    def __init__(self, base_url: str = BASE_URL, auto_start: bool = True):
        self.base_url = base_url.rstrip("/")
        if auto_start:
            self._ensure_server()

    # ── Gestão do servidor ──────────────────────────────────────────────────

    @staticmethod
    def is_server_running() -> bool:
        """Verifica se o servidor litert-lm está rodando na porta 9379."""
        try:
            req = urllib_request.Request(f"http://localhost:{LITERT_SERVE_PORT}/v1/models")
            with urllib_request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                return "data" in data
        except (URLError, ConnectionRefusedError, OSError, json.JSONDecodeError):
            return False

    @staticmethod
    def start_server(port: int = LITERT_SERVE_PORT,
                     host: str = LITERT_SERVE_HOST,
                     timeout: int = SERVER_START_TIMEOUT) -> bool:
        """Inicia o servidor litert-lm serve em background.

        Retorna True se o servidor iniciou com sucesso dentro do timeout.
        """
        global _server_process, _server_ready

        if _server_ready:
            return True

        if LiteRTLMProvider.is_server_running():
            _server_ready = True
            logger.info("Servidor litert-lm já está rodando em :%d", port)
            return True

        logger.info("Iniciando servidor litert-lm na porta %d...", port)
        try:
            _server_process = subprocess.Popen(
                ["litert-lm", "serve", "--port", str(port),
                 "--cors-origin", "*"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )

            # Aguarda o servidor ficar pronto (modelo carrega sob demanda)
            inicio = time.time()
            while time.time() - inicio < timeout:
                if LiteRTLMProvider.is_server_running():
                    _server_ready = True
                    elapsed = time.time() - inicio
                    logger.info("Servidor litert-lm pronto em %.1fs", elapsed)
                    return True
                time.sleep(2)

            logger.error("Servidor litert-lm não respondeu em %ds", timeout)
            return False

        except FileNotFoundError:
            logger.error("litert-lm não encontrado no PATH. Instale com: pip3 install litert-lm")
            return False
        except Exception as e:
            logger.error("Erro ao iniciar servidor litert-lm: %s", e)
            return False

    @staticmethod
    def stop_server() -> None:
        """Para o servidor litert-lm."""
        global _server_process, _server_ready
        if _server_process:
            _server_process.terminate()
            try:
                _server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                _server_process.kill()
            _server_process = None
        _server_ready = False
        logger.info("Servidor litert-lm parado.")

    def _ensure_server(self) -> None:
        """Garante que o servidor está rodando."""
        if not self.start_server():
            logger.warning(
                "Servidor litert-lm não disponível. "
                "Modelos on-device ficarão indisponíveis."
            )

    # ── Listagem de modelos ────────────────────────────────────────────────

    def list_models(self) -> List[Dict[str, Any]]:
        """Retorna a lista de modelos disponíveis (do servidor + catálogo)."""
        models = []
        try:
            req = urllib_request.Request(f"{self.base_url}/models")
            with urllib_request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                for m in data.get("data", []):
                    model_id = m["id"]
                    info = MODELS.get(model_id, {})
                    models.append({
                        "id": model_id,
                        "name": info.get("name", model_id),
                        "provider": PROVIDER_ID,
                        "tier": info.get("tier", "standard"),
                        "size_gb": info.get("size_gb", "?"),
                    })
        except Exception as e:
            logger.debug("Erro ao listar modelos do servidor: %s", e)
            # Fallback: catálogo estático
            for mid, info in MODELS.items():
                models.append({
                    "id": mid,
                    "name": info["name"],
                    "provider": PROVIDER_ID,
                    "tier": info["tier"],
                    "size_gb": info["size_gb"],
                })
        return models

    # ── Inferência ─────────────────────────────────────────────────────────

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Envia uma requisição de chat para o modelo on-device.

        Args:
            messages: Lista de mensagens no formato {"role": ..., "content": ...}
            model: ID do modelo (default: gemma-4-E2B-it-litert-lm)
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura de amostragem
            stream: Se True, retorna generator (não implementado nesta versão)

        Returns:
            Dict com a resposta no formato OpenAI ChatCompletion
        """
        self._ensure_server()

        model_id = model or DEFAULT_MODEL
        payload = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }

        req = urllib_request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib_request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read())
                return result
        except URLError as e:
            logger.error("Erro na requisição ao litert-lm: %s", e)
            return {
                "error": f"Falha ao contactar servidor litert-lm: {e.reason}",
                "model": model_id,
            }


# ── Helpers para uso externo ────────────────────────────────────────────────

def get_provider() -> LiteRTLMProvider:
    """Retorna uma instância singleton do provider."""
    return LiteRTLMProvider()


def list_available_models() -> List[Dict[str, Any]]:
    """Retorna a lista de modelos disponíveis."""
    return get_provider().list_models()


# ── CLI de diagnóstico ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    provider = LiteRTLMProvider(auto_start=True)

    if "--stop" in sys.argv:
        provider.stop_server()
        print("Servidor litert-lm parado.")
        sys.exit(0)

    models = provider.list_models()
    print(f"Modelos LiteRT-LM disponíveis ({len(models)}):")
    for m in models:
        print(f"  {m['id']} — {m['name']} ({m['size_gb']}GB, {m['tier']})")

    if len(sys.argv) > 1 and sys.argv[1] not in ("--stop",):
        prompt = " ".join(sys.argv[1:])
        print(f"\nPrompt: {prompt}")
        result = provider.complete(
            messages=[{"role": "user", "content": prompt}],
            model=DEFAULT_MODEL,
            max_tokens=256,
        )
        if "error" in result:
            print(f"Erro: {result['error']}")
        else:
            content = result["choices"][0]["message"]["content"]
            print(f"Resposta: {content}")
