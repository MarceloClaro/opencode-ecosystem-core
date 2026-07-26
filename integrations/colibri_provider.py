# -*- coding: utf-8 -*-
"""
Colibri Provider — Integração com o Motor de Inferência MoE Colibri
====================================================================
Expõe os modelos executados localmente pelo engine Colibri (ex.: OLMoE 1B/7B,
GLM-5.2) via API HTTP compatível com OpenAI.

Configuração de Porta:
  Utiliza a porta 8090 por padrão (configurável via env COLIBRI_PORT),
  evitando conflitos com a porta 8080 do opencode-ecosystem-core.

Uso:
    from integrations.colibri_provider import ColibriProvider
    provider = ColibriProvider(port=8090)
    if provider.is_available():
        res = provider.complete("Explique aprendizado por reforço")

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import os
import json
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger("colibri-provider")

PROVIDER_ID = "colibri"
DEFAULT_PORT = int(os.environ.get("COLIBRI_PORT", "8090"))
DEFAULT_HOST = os.environ.get("COLIBRI_HOST", "127.0.0.1")

MODELS: Dict[str, Dict[str, Any]] = {
    "olmoe-1b-7b": {
        "name": "OLMoE 1B/7B (Colibri MoE)",
        "provider": PROVIDER_ID,
        "family": "colibri",
        "strengths": ["fast", "moe", "local", "low-ram"],
        "context_window": 4096,
        "thinking": False,
        "tier": "fast",
    },
    "glm-5.2-colibri": {
        "name": "GLM-5.2 (Colibri 744B MoE)",
        "provider": PROVIDER_ID,
        "family": "colibri",
        "strengths": ["reasoning", "moe", "frontier", "local"],
        "context_window": 4096,
        "thinking": True,
        "tier": "premium",
    },
}


@dataclass
class ColibriProvider:
    """Provedor para comunicação com o servidor HTTP local do Colibri."""
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    timeout: float = 30.0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}/v1"

    def is_available(self) -> bool:
        """Verifica se o servidor Colibri está ativo na porta configurada."""
        try:
            req = urllib.request.Request(f"{self.base_url}/models", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def health_check(self) -> Dict[str, Any]:
        """Retorna o estado de saúde e conectividade do provedor."""
        available = self.is_available()
        return {
            "provider": PROVIDER_ID,
            "available": available,
            "host": self.host,
            "port": self.port,
            "base_url": self.base_url,
            "supported_models": list(MODELS.keys()),
        }

    def ensure_server_running(self) -> bool:
        """Inicia o servidor Colibri em segundo plano caso não esteja rodando."""
        if self.is_available():
            return True
        
        try:
            import subprocess
            import time
            logger.info("Iniciando servidor Colibri na porta %d...", self.port)
            cmd = [
                "./.venv/bin/python3",
                "colibri/c/openai_server.py",
                "--engine", "./colibri/c/olmoe",
                "--model", "/home/marceloclaro/models/olmoe_merged",
                "--port", str(self.port)
            ]
            subprocess.Popen(cmd, cwd="/home/marceloclaro/opencode-ecosystem-core")
            for _ in range(15):
                time.sleep(1.0)
                if self.is_available():
                    return True
        except Exception as exc:
            logger.error("Falha ao autoiniciar o servidor Colibri: %s", exc)
        return self.is_available()

    def complete(
        self,
        prompt: str,
        model: str = "olmoe-1b-7b",
        max_tokens: int = 512,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        auto_start: bool = True,
    ) -> Dict[str, Any]:
        """Envia uma requisição de completude para o servidor Colibri."""
        if not self.is_available():
            if auto_start:
                self.ensure_server_running()
            if not self.is_available():
                return {
                    "success": False,
                    "error": f"Servidor Colibri inacessível em {self.base_url}. Inicie o servidor via 'coli serve --port {self.port}'.",
                    "content": "",
                }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "success": True,
                    "content": content,
                    "raw": result,
                    "model": model,
                    "provider": PROVIDER_ID,
                }
        except Exception as exc:
            logger.error("Erro na completude do Colibri: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "content": "",
            }


colibri_provider = ColibriProvider()
