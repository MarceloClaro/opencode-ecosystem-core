# -*- coding: utf-8 -*-
"""
Testes do cliente LLM unificado (Ollama local + OpenAI-compatível).
Todos os testes rodam offline: o servidor Ollama é simulado com um
HTTPServer local em thread, garantindo determinismo total.
"""
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.llm_client import LLMClient  # noqa: E402


class _FakeOllamaHandler(BaseHTTPRequestHandler):
    """Servidor mínimo que emula /api/tags e /api/generate do Ollama."""

    def log_message(self, *args):  # silencia logs
        pass

    def do_GET(self):
        if self.path == "/api/tags":
            body = json.dumps({"models": [{"name": "llama3.2"},
                                          {"name": "qwen2.5"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/generate":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length).decode())
            body = json.dumps({
                "model": payload.get("model"),
                "response": f"Análise crítica gerada localmente pelo "
                            f"modelo {payload.get('model')}.",
                "done": True,
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


class LLMClientOllamaTest(unittest.TestCase):
    """Testa o caminho Ollama com servidor local simulado."""

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _FakeOllamaHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls._old_host = os.environ.get("OLLAMA_HOST")
        os.environ["OLLAMA_HOST"] = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        if cls._old_host is None:
            os.environ.pop("OLLAMA_HOST", None)
        else:
            os.environ["OLLAMA_HOST"] = cls._old_host

    def test_ollama_available(self):
        self.assertTrue(LLMClient.ollama_available())

    def test_ollama_models_listed(self):
        models = LLMClient.ollama_models()
        self.assertIn("llama3.2", models)
        self.assertIn("qwen2.5", models)

    def test_auto_resolves_to_ollama(self):
        client = LLMClient(provider="auto")
        self.assertEqual(client.provider, "ollama")
        self.assertTrue(client.available())

    def test_generate_via_ollama(self):
        client = LLMClient(provider="ollama", model="llama3.2")
        text = client.generate("Resuma o artigo X.")
        self.assertIsNotNone(text)
        self.assertIn("llama3.2", text)
        self.assertIn("localmente", text)

    def test_describe_reports_local_provider(self):
        client = LLMClient(provider="ollama", model="llama3.2")
        meta = client.describe()
        self.assertEqual(meta["provider"], "ollama")
        self.assertTrue(meta["local"])
        self.assertEqual(meta["model"], "llama3.2")

    def test_custom_model_via_env(self):
        os.environ["OLLAMA_MODEL"] = "qwen2.5"
        try:
            client = LLMClient(provider="ollama")
            self.assertEqual(client.model, "qwen2.5")
        finally:
            os.environ.pop("OLLAMA_MODEL", None)


class LLMClientFallbackTest(unittest.TestCase):
    """Testa resolução de provedor sem Ollama e sem chave de API."""

    def setUp(self):
        self._old = {k: os.environ.pop(k, None)
                     for k in ("OLLAMA_HOST", "OPENAI_API_KEY",
                               "RESEARCH_LLM")}
        # host inexistente para simular Ollama offline
        os.environ["OLLAMA_HOST"] = "http://127.0.0.1:1"

    def tearDown(self):
        for k, v in self._old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_no_provider_resolves_none(self):
        client = LLMClient(provider="auto")
        self.assertIsNone(client.provider)
        self.assertFalse(client.available())
        self.assertIsNone(client.generate("teste"))

    def test_describe_deterministic_when_unavailable(self):
        client = LLMClient(provider="none")
        meta = client.describe()
        self.assertEqual(meta["provider"], "deterministic")
        self.assertFalse(meta["local"])

    def test_forced_openai_without_key_generates_none(self):
        client = LLMClient(provider="openai")
        self.assertIsNone(client.generate("teste"))

    def test_env_research_llm_none(self):
        os.environ["RESEARCH_LLM"] = "none"
        client = LLMClient(provider="auto")
        self.assertIsNone(client.provider)


class FichamentoOllamaIntegrationTest(unittest.TestCase):
    """Integração: enrich_with_llm usando o Ollama simulado."""

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _FakeOllamaHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls._old_host = os.environ.get("OLLAMA_HOST")
        os.environ["OLLAMA_HOST"] = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        if cls._old_host is None:
            os.environ.pop("OLLAMA_HOST", None)
        else:
            os.environ["OLLAMA_HOST"] = cls._old_host

    def test_resenha_enriched_with_local_model(self):
        import tempfile
        from research.fichamento import FichamentoWriter
        from research.searchers import PaperRecord

        tmp = tempfile.mkdtemp(prefix="fich_")
        writer = FichamentoWriter(tmp, tmp, "aprendizado quântico")
        rec = PaperRecord(
            title="Quantum Noise as Regularizer",
            authors=["Silva, Ana"], year=2025,
            abstract="Noise can help variational classifiers.",
            url="https://example.org/paper", source="arxiv")
        resenha = writer.resenha(rec, "Texto integral do artigo.")
        ok = writer.enrich_with_llm(rec, "Texto integral do artigo.",
                                    resenha, provider="ollama",
                                    model="llama3.2")
        self.assertTrue(ok)
        content = open(resenha, encoding="utf-8").read()
        self.assertIn("Análise aprofundada", content)
        self.assertIn("modelo local `llama3.2` via Ollama", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
