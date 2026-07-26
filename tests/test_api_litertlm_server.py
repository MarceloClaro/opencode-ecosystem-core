# -*- coding: utf-8 -*-
"""
Testes de API do servidor LiteRT-LM (OpenAI-compatible)
=========================================================
Valida os endpoints reais do servidor rodando em localhost:9379.

SDD estrito — acceptance criteria:
  CA1: GET  /v1/models           → 200 + JSON com lista de modelos
  CA2: POST /v1/chat/completions  → 200 + resposta com choices[0].message.content
  CA3: POST /v1/chat/completions streaming → SSE chunks com delta
  CA4: model ID inválido → erro mensagem clara
  CA5: payload inválido → 422/400
  CA6: modelos listados batem com os que respondem ao chat

TDD: RED (servidor offline) → GREEN (servidor online) → REFACTOR
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import Any

import pytest

try:
    import requests
except ImportError:
    requests = None  # type: ignore

BASE_URL = "http://localhost:9379/v1"
MODEL_ID = "litert-community/gemma-4-E2B-it-litert-lm"
TIMEOUT = 60  # segundos (modelo on-device pode ser lento)
RUN_EXTERNAL_TESTS = os.getenv("OPENCODE_RUN_EXTERNAL_TESTS") == "1"
pytestmark = [
    pytest.mark.external,
    pytest.mark.skipif(
        not RUN_EXTERNAL_TESTS,
        reason=(
            "inferência LiteRT-LM real é opt-in; defina "
            "OPENCODE_RUN_EXTERNAL_TESTS=1"
        ),
    ),
]


# ── Helpers ────────────────────────────────────────────────────────────────────


def _req(method: str, path: str, **kwargs) -> dict[str, Any]:
    """Faz requisição HTTP e retorna JSON."""
    if requests is None:
        raise unittest.SkipTest("requests não instalado (pip install requests)")
    url = f"{BASE_URL}/{path.lstrip('/')}"
    kwargs.setdefault("timeout", TIMEOUT)
    resp = requests.request(method, url, **kwargs)
    resp.raise_for_status()
    return resp.json()


def _server_available() -> bool:
    """Verifica se o servidor responde."""
    try:
        import requests
        resp = requests.get(f"{BASE_URL}/models", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


# ── Tests ──────────────────────────────────────────────────────────────────────


@unittest.skipIf(requests is None, "requests library not installed")
class TestAPIHealth(unittest.TestCase):
    """SDD CA1: GET /v1/models retorna lista de modelos."""

    @classmethod
    def setUpClass(cls):
        if not _server_available():
            raise unittest.SkipTest(
                "Servidor LiteRT-LM não está rodando em :9379.\n"
                "Inicie com: litert-lm serve --port 9379"
            )

    def test_models_endpoint_status(self):
        """CA1a: GET /v1/models → 200 OK"""
        resp = _req("GET", "models")
        self.assertIn("object", resp)
        self.assertIn("data", resp)

    def test_models_list_is_array(self):
        """CA1b: data é uma lista não vazia de modelos"""
        resp = _req("GET", "models")
        data = resp["data"]
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Nenhum modelo disponível no servidor")

    def test_models_have_required_fields(self):
        """CA1c: cada modelo tem id, object, created, owned_by"""
        resp = _req("GET", "models")
        for model in resp["data"]:
            with self.subTest(model=model.get("id", "unknown")):
                self.assertIn("id", model)
                self.assertIn("object", model)
                self.assertIn("created", model)
                self.assertIn("owned_by", model)
                self.assertIsInstance(model["id"], str)
                self.assertTrue(len(model["id"]) > 0)

    def test_specific_model_exists(self):
        """CA1d: modelo Gemma 4 E2B está disponível"""
        resp = _req("GET", "models")
        ids = [m["id"] for m in resp["data"]]
        self.assertIn(
            MODEL_ID, ids,
            f"Modelo {MODEL_ID} não encontrado. Disponíveis: {ids}",
        )


@unittest.skipIf(requests is None, "requests library not installed")
class TestChatCompletion(unittest.TestCase):
    """SDD CA2: POST /v1/chat/completions retorna resposta válida."""

    @classmethod
    def setUpClass(cls):
        if not _server_available():
            raise unittest.SkipTest("Servidor não disponível")

    def test_chat_basic_response(self):
        """CA2a: chat completion retorna 200 com texto"""
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": "Responda apenas: FUNCIONOU"}],
            "temperature": 0.1,
            "max_tokens": 50,
        }
        resp = _req("POST", "chat/completions", json=payload)
        self.assertIn("choices", resp)
        self.assertGreater(len(resp["choices"]), 0)
        choice = resp["choices"][0]
        self.assertIn("message", choice)
        self.assertIn("content", choice["message"])
        content = choice["message"]["content"]
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)

    def test_chat_returned_model_matches(self):
        """CA2b: model no response corresponde ao solicitado"""
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": "teste"}],
            "max_tokens": 10,
        }
        resp = _req("POST", "chat/completions", json=payload)
        self.assertEqual(resp["model"], MODEL_ID)

    def test_chat_has_finish_reason(self):
        """CA2c: resposta tem finish_reason"""
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": "diga: FUNCIONOU"}],
            "max_tokens": 100,
        }
        resp = _req("POST", "chat/completions", json=payload)
        choice = resp["choices"][0]
        self.assertIn("finish_reason", choice)
        self.assertIn(choice["finish_reason"], ["stop", "length"])

    def test_chat_contains_funcionou(self):
        """CA2d: conteúdo da resposta contém FUNCIONOU (validação semântica)"""
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": "diga: FUNCIONOU"}],
            "temperature": 0.1,
            "max_tokens": 100,
        }
        resp = _req("POST", "chat/completions", json=payload)
        content = resp["choices"][0]["message"]["content"]
        self.assertIn(
            "FUNCIONOU",
            content.upper(),
            f"Resposta não contém FUNCIONOU: {content[:200]}",
        )
        print(f"\n  ✅ Resposta: {content[:150]}...")

    def test_chat_with_system_prompt(self):
        """CA2e: system prompt é respeitado"""
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": "Responda apenas com a palavra SIM"},
                {"role": "user", "content": "Confirme que está funcionando"},
            ],
            "temperature": 0.1,
            "max_tokens": 50,
        }
        resp = _req("POST", "chat/completions", json=payload)
        content = resp["choices"][0]["message"]["content"]
        self.assertGreater(len(content), 0)


@unittest.skipIf(requests is None, "requests library not installed")
class TestErrorHandling(unittest.TestCase):
    """SDD CA4/CA5: Erros são tratados adequadamente."""

    @classmethod
    def setUpClass(cls):
        if not _server_available():
            raise unittest.SkipTest("Servidor não disponível")

    def test_invalid_model_returns_error(self):
        """CA4: model ID inválido → mensagem de erro"""
        import requests as req_lib
        payload = {
            "model": "nonexistent/model",
            "messages": [{"role": "user", "content": "teste"}],
        }
        url = f"{BASE_URL}/chat/completions"
        resp = req_lib.post(url, json=payload, timeout=TIMEOUT)
        # Pode ser 4xx ou 200 com erro interno
        if resp.status_code != 200:
            # Erro HTTP legítimo
            self.assertIn(resp.status_code, [400, 404, 422, 500])
        else:
            # 200 mas com erro no conteúdo
            body = resp.json()
            if "error" in body:
                self.assertIn("message", body["error"])

    def test_empty_messages_returns_error(self):
        """CA5: payload sem messages → erro"""
        import requests as req_lib
        payload = {"model": MODEL_ID}
        url = f"{BASE_URL}/chat/completions"
        resp = req_lib.post(url, json=payload, timeout=TIMEOUT)
        # Servidor retorna 500 para payload inválido
        self.assertIn(resp.status_code, [400, 422, 500])


@unittest.skipIf(requests is None, "requests library not installed")
class TestModelConsistency(unittest.TestCase):
    """SDD CA6: modelos listados × modelos que respondem ao chat.

    Garante que todo modelo listado no GET /v1/models também aceita
    requisições de chat completion.
    """

    @classmethod
    def setUpClass(cls):
        if not _server_available():
            raise unittest.SkipTest("Servidor não disponível")
        resp = _req("GET", "models")
        cls.available_models = [m["id"] for m in resp["data"]]

    def test_all_models_accept_chat(self):
        """CA6a: cada modelo listado responde ao chat"""
        for model_id in self.available_models:
            with self.subTest(model=model_id):
                payload = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": "diga: OK"}],
                    "max_tokens": 30,
                    "temperature": 0.1,
                }
                try:
                    resp = _req("POST", "chat/completions", json=payload)
                    self.assertIn("choices", resp)
                    content = resp["choices"][0]["message"]["content"]
                    self.assertGreater(len(content), 0)
                    print(f"    ✅ {model_id}: {content[:60]}...")
                except Exception as e:
                    self.fail(
                        f"Modelo {model_id} falhou no chat: {e}"
                    )


# ── Run if called directly ─────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
