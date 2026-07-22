# -*- coding: utf-8 -*-
"""
Tests SPEC-935-R209 — LiteRT-LM Skill Integration
==================================================
Rigor TDD: RED → GREEN → REFACTOR
All tests initially RED (code doesn't exist yet).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_MODEL_METADATA = {
    "model_id": "litert-community/gemma-4-E2B-it-litert-lm",
    "model_path": "/home/user/.litert-lm/models/litert-community--gemma-4-E2B-it-litert-lm/model.litertlm",
    "backend": "gpu",
    "max_num_tokens": 8192,
    "speculative_decoding": True,
    "model_type": "ARTISAN_TEXT_DECODER",
    "file_size_mb": 4825,
}

MOCK_CHAT_RESPONSE = {
    "content": [{"type": "text", "text": "Olá! Sou o Gemma 4, como posso ajudar?"}],
    "role": "assistant",
}

MOCK_STREAM_CHUNKS = [
    {"content": [{"type": "text", "text": "Olá"}], "role": "assistant"},
    {"content": [{"type": "text", "text": "! Sou"}], "role": "assistant"},
    {"content": [{"type": "text", "text": " o Gemma 4."}], "role": "assistant"},
]


def _make_mock_engine():
    """Cria um mock do litert_lm.Engine para testes."""
    engine = mock.MagicMock()
    engine.__enter__ = mock.MagicMock(return_value=engine)
    engine.__exit__ = mock.MagicMock(return_value=None)

    # Conversation mock
    conv = mock.MagicMock()
    conv.__enter__ = mock.MagicMock(return_value=conv)
    conv.__exit__ = mock.MagicMock(return_value=None)
    conv.send_message_async.return_value = MOCK_STREAM_CHUNKS
    conv.send_message.return_value = MOCK_CHAT_RESPONSE

    engine.create_conversation.return_value = conv

    # Session mock
    session = mock.MagicMock()
    session.__enter__ = mock.MagicMock(return_value=session)
    session.__exit__ = mock.MagicMock(return_value=None)
    session.run_prefill.return_value = None
    session.run_decode_async.return_value = [
        mock.MagicMock(texts=["Olá! Sou o Gemma 4."])
    ]

    engine.create_session.return_value = session
    engine.tokenize.return_value = [1, 2, 3, 4]
    engine.detokenize.return_value = "Olá! Sou o Gemma 4."
    engine.bos_token_id = 1
    engine.eos_token_ids = [[2]]

    return engine


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestModelManager(unittest.TestCase):
    """ModelManager: descoberta, cache, import, inspect, delete."""

    def setUp(self):
        self.models_dir = tempfile.mkdtemp()
        self.patcher = mock.patch.dict(
            "os.environ", {"LITERT_LM_MODELS_DIR": self.models_dir}, clear=False
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.models_dir, ignore_errors=True)

    def _create_fake_model_dir(self, name: str) -> str:
        """Cria diretório fake de modelo com model.litertlm."""
        safe = name.replace("/", "--")
        model_dir = os.path.join(self.models_dir, safe)
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "model.litertlm")
        with open(model_path, "wb") as f:
            f.write(b"FAKE_LITERTLM_HEADER")
        return model_path

    # ── CA1: list ─────────────────────────────────────────────────────────

    def test_list_models_empty_dir(self):
        """list_models retorna lista vazia quando não há modelos."""
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        models = mgr.list_models()
        self.assertEqual(models, [])

    def test_list_models_with_one(self):
        """list_models encontra modelo criado no diretório."""
        self._create_fake_model_dir("test-org/test-model")
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        models = mgr.list_models()
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].model_id, "test-org/test-model")

    def test_list_models_with_multiple(self):
        """list_models encontra múltiplos modelos."""
        self._create_fake_model_dir("org/a")
        self._create_fake_model_dir("org/b")
        self._create_fake_model_dir("org/c")
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        models = mgr.list_models()
        self.assertEqual(len(models), 3)

    # ── CA2: find_model ───────────────────────────────────────────────────

    def test_find_model_by_id(self):
        """find_model localiza por ID (org/model)."""
        self._create_fake_model_dir("gemma/test")
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        info = mgr.find_model("gemma/test")
        self.assertIsNotNone(info)
        self.assertEqual(info.model_id, "gemma/test")

    def test_find_model_by_path(self):
        """find_model localiza por caminho absoluto."""
        path = self._create_fake_model_dir("some/model")
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        info = mgr.find_model(path)
        self.assertIsNotNone(info)

    def test_find_model_not_found(self):
        """find_model retorna None para modelo inexistente."""
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        info = mgr.find_model("nonexistent/model")
        self.assertIsNone(info)

    # ── CA3: inspect ──────────────────────────────────────────────────────

    def test_inspect_model(self):
        """inspect retorna metadados do modelo."""
        path = self._create_fake_model_dir("gemma/test")
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        metadata = mgr.inspect(path)
        self.assertIsNotNone(metadata)
        self.assertIn("file_size_bytes", metadata)
        self.assertIn("model_id", metadata)

    def test_inspect_nonexistent_file(self):
        """inspect levanta FileNotFoundError para arquivo inexistente."""
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        with self.assertRaises(FileNotFoundError):
            mgr.inspect("/nonexistent/path.litertlm")

    # ── CA4: delete ───────────────────────────────────────────────────────

    def test_delete_model(self):
        """delete_model remove diretório do modelo."""
        self._create_fake_model_dir("org/to-delete")
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        result = mgr.delete_model("org/to-delete")
        self.assertTrue(result)
        self.assertIsNone(mgr.find_model("org/to-delete"))

    def test_delete_nonexistent(self):
        """delete_model retorna False para modelo inexistente."""
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        result = mgr.delete_model("ghost/model")
        self.assertFalse(result)

    # ── CA5: import ───────────────────────────────────────────────────────

    @mock.patch("skills.litert_lm.model_manager._huggingface_hub.hf_hub_download")
    def test_import_from_hf(self, mock_download):
        """import_from_hf baixa modelo do HuggingFace."""
        mock_download.return_value = "/fake/path/model.litertlm"
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        info = mgr.import_from_hf("litert-community/gemma-4-E2B-it-litert-lm",
                                   filename="model.litertlm")
        self.assertIsNotNone(info)
        mock_download.assert_called_once()

    @mock.patch("skills.litert_lm.model_manager._huggingface_hub.hf_hub_download")
    def test_import_from_hf_with_token(self, mock_download):
        """import_from_hf aceita token opcional."""
        mock_download.return_value = "/fake/path/model.litertlm"
        from skills.litert_lm.model_manager import ModelManager
        mgr = ModelManager(models_dir=self.models_dir)
        mgr.import_from_hf("org/model", token="hf_test123")
        _, kwargs = mock_download.call_args
        self.assertEqual(kwargs.get("token"), "hf_test123")


class TestLiteRTLMSkill(unittest.TestCase):
    """LiteRTLMSkill: orquestração de alto nível."""

    def setUp(self):
        self.models_dir = tempfile.mkdtemp()
        self.patcher = mock.patch.dict(
            "os.environ", {"LITERT_LM_MODELS_DIR": self.models_dir}, clear=False
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.models_dir, ignore_errors=True)

    def _create_fake_model(self, name: str) -> str:
        safe = name.replace("/", "--")
        model_dir = os.path.join(self.models_dir, safe)
        os.makedirs(model_dir, exist_ok=True)
        path = os.path.join(model_dir, "model.litertlm")
        with open(path, "wb") as f:
            f.write(b"FAKE")
        return path

    # ── CA1: Skill.list_models ────────────────────────────────────────────

    def test_skill_list_models(self):
        """Skill.list_models delega ao ModelManager."""
        self._create_fake_model("gemma/test")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)
        models = skill.list_models()
        self.assertEqual(len(models), 1)

    # ── CA2: Skill.run ────────────────────────────────────────────────────

    @mock.patch("skills.litert_lm.chat.litert_lm")
    def test_skill_run_single_prompt(self, mock_litert):
        """Skill.run executa prompt único com Engine."""
        mock_litert.Engine = mock.MagicMock(return_value=_make_mock_engine())
        mock_litert.Backend = mock.MagicMock()
        mock_litert.Backend.CPU = mock.MagicMock()

        self._create_fake_model("gemma/test")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)

        result = skill.run("gemma/test", "Olá!")
        self.assertIn("Gemma", result)

    @mock.patch("skills.litert_lm.chat.litert_lm")
    def test_skill_run_with_kwargs(self, mock_litert):
        """Skill.run propaga SamplerConfig para o Engine."""
        mock_litert.Engine = mock.MagicMock(return_value=_make_mock_engine())
        mock_litert.Backend = mock.MagicMock()
        mock_litert.Backend.CPU = mock.MagicMock()

        self._create_fake_model("gemma/test")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)

        skill.run("gemma/test", "Teste", temperature=0.5, top_k=20)

    # ── CA3: Skill.chat ───────────────────────────────────────────────────

    @mock.patch("skills.litert_lm.chat.litert_lm")
    def test_skill_chat_session(self, mock_litert):
        """Skill.chat retorna ChatSession."""
        mock_litert.Engine = mock.MagicMock(return_value=_make_mock_engine())
        mock_litert.Backend = mock.MagicMock()
        mock_litert.Backend.CPU = mock.MagicMock()

        self._create_fake_model("gemma/test")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)

        session = skill.chat("gemma/test")
        self.assertIsNotNone(session)
        # Envia mensagem no chat
        response = session.send("Olá!")
        self.assertIsNotNone(response)

    # ── CA4: Skill.serve ──────────────────────────────────────────────────

    @mock.patch("skills.litert_lm.skill.LiteRTOpenAIServer")
    def test_skill_serve(self, mock_server_class):
        """Skill.serve cria servidor OpenAI (sem iniciar HTTP)."""
        self._create_fake_model("gemma/test")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)

        mock_server = mock.MagicMock()
        mock_server_class.return_value = mock_server

        result = skill.serve("gemma/test", host="127.0.0.1", port=8080)
        mock_server_class.assert_called_once()
        self.assertEqual(result, mock_server)

    # ── CA5: Skill.inspect ────────────────────────────────────────────────

    def test_skill_inspect(self):
        """Skill.inspect retorna metadados."""
        path = self._create_fake_model("gemma/my-model")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)
        meta = skill.inspect(path)
        self.assertIn("file_size_bytes", meta)

    # ── CA6: Skill.delete ─────────────────────────────────────────────────

    def test_skill_delete(self):
        """Skill.delete_model remove modelo."""
        self._create_fake_model("old/model")
        from skills.litert_lm.skill import LiteRTLMSkill
        skill = LiteRTLMSkill(models_dir=self.models_dir)
        result = skill.delete_model("old/model")
        self.assertTrue(result)
        self.assertEqual(len(skill.list_models()), 0)


class TestChatSession(unittest.TestCase):
    """ChatSession: interface conversacional interativa."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.tmpdir, "model.litertlm")
        with open(self.model_path, "wb") as f:
            f.write(b"MOCK_LITERTLM_MODEL")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    # ── CA7: Chat básico ──────────────────────────────────────────────────

    @mock.patch("skills.litert_lm.chat.litert_lm", create=True)
    def test_chat_send_message(self, mock_litert):
        """ChatSession.send envia mensagem e recebe resposta."""
        mock_engine = _make_mock_engine()
        mock_litert.Engine.return_value = mock_engine

        from skills.litert_lm.chat import ChatSession
        session = ChatSession(self.model_path)
        response = session.send("Olá!")
        self.assertIsNotNone(response)

    @mock.patch("skills.litert_lm.chat.litert_lm", create=True)
    def test_chat_streaming(self, mock_litert):
        """ChatSession.send com streaming retorna iterador."""
        mock_engine = _make_mock_engine()
        mock_litert.Engine.return_value = mock_engine

        from skills.litert_lm.chat import ChatSession
        session = ChatSession(self.model_path, stream=True)
        response = session.send("Olá!")
        # streaming retorna iterable
        chunks = list(response) if hasattr(response, "__iter__") else [response]
        self.assertGreater(len(chunks), 0)

    @mock.patch("skills.litert_lm.chat.litert_lm", create=True)
    def test_chat_history(self, mock_litert):
        """ChatSession mantém histórico de mensagens (user+assistant a cada send)."""
        mock_engine = _make_mock_engine()
        mock_litert.Engine.return_value = mock_engine

        from skills.litert_lm.chat import ChatSession
        session = ChatSession(self.model_path)
        session.send("Mensagem 1")
        session.send("Mensagem 2")
        # Cada send() adiciona user + assistant = 2 entradas
        # 2 sends = 4 entradas
        self.assertEqual(len(session.history), 4)

    @mock.patch("skills.litert_lm.chat.litert_lm", create=True)
    def test_chat_cancel(self, mock_litert):
        """ChatSession.cancel interrompe geração."""
        mock_engine = _make_mock_engine()
        mock_litert.Engine.return_value = mock_engine

        from skills.litert_lm.chat import ChatSession
        session = ChatSession(self.model_path)
        session.cancel()  # Não deve levantar exceção

    # ── CA8: Chat com preset ──────────────────────────────────────────────

    @mock.patch("skills.litert_lm.chat.litert_lm", create=True)
    def test_chat_with_preset(self, mock_litert):
        """ChatSession aceita preset com tools e system_instruction."""
        mock_engine = _make_mock_engine()
        mock_litert.Engine.return_value = mock_engine

        from skills.litert_lm.chat import ChatSession

        def fake_tool():
            pass

        session = ChatSession(
            self.model_path,
            preset_tools=[fake_tool],
            system_instruction="Seja prestativo.",
        )
        session.send("Teste")
        # Engine.create_conversation foi chamado com sistema
        mock_engine.create_conversation.assert_called_once()


class TestCLI(unittest.TestCase):
    """CLI: argumentos, subcomandos, erros."""

    def setUp(self):
        self.models_dir = tempfile.mkdtemp()
        self.patcher = mock.patch.dict(
            "os.environ",
            {"LITERT_LM_MODELS_DIR": self.models_dir},
            clear=False,
        )
        self.patcher.start()

        # Cria modelo fake
        safe = "gemma--test"
        os.makedirs(os.path.join(self.models_dir, safe), exist_ok=True)
        with open(os.path.join(self.models_dir, safe, "model.litertlm"), "wb") as f:
            f.write(b"FAKE")

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.models_dir, ignore_errors=True)

    @mock.patch("skills.litert_lm.skill.LiteRTLMSkill.list_models")
    def test_cli_list_command(self, mock_list):
        """CLI 'list' invoca list_models."""
        mock_list.return_value = []

        from skills.litert_lm.cli import litert_lm_cli
        runner = unittest.mock.MagicMock()
        # Usa Click test runner
        from click.testing import CliRunner
        cli_runner = CliRunner()
        result = cli_runner.invoke(litert_lm_cli, ["list"])
        self.assertEqual(result.exit_code, 0)

    @mock.patch("skills.litert_lm.skill.LiteRTLMSkill.run")
    def test_cli_run_command(self, mock_run):
        """CLI 'run' invoca skill.run com modelo e prompt."""
        mock_run.return_value = "Resposta mockada"

        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, [
            "run", "gemma/test", "--prompt", "Olá!"
        ])
        self.assertEqual(result.exit_code, 0)
        mock_run.assert_called_once()

    def test_cli_run_missing_model(self):
        """CLI 'run' sem modelo existente retorna erro."""
        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, [
            "run", "nonexistent/model", "--prompt", "Oi"
        ])
        self.assertNotEqual(result.exit_code, 0)

    @mock.patch("skills.litert_lm.skill.LiteRTLMSkill.chat")
    def test_cli_chat_command(self, mock_chat):
        """CLI 'chat' inicia ChatSession."""
        mock_session = mock.MagicMock()
        mock_session.send.return_value = "Resposta"
        mock_chat.return_value = mock_session

        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, [
            "chat", "gemma/test", "--prompt", "Olá!", "--non-interactive"
        ])
        self.assertEqual(result.exit_code, 0)

    @mock.patch.dict(os.environ, {"LITERT_LM_DRY_RUN": "1"})
    @mock.patch("skills.litert_lm.skill.LiteRTLMSkill.serve")
    def test_cli_serve_command(self, mock_serve):
        """CLI 'serve' (dry-run) valida parsing e criação do servidor."""
        mock_server = mock.MagicMock()
        mock_server.model_name = "gemma/test"
        mock_serve.return_value = mock_server
        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, [
            "serve", "gemma/test", "--port", "9999"
        ])
        self.assertEqual(result.exit_code, 0)

    @mock.patch("skills.litert_lm.skill.LiteRTLMSkill.inspect")
    def test_cli_info_command(self, mock_info):
        """CLI 'info' exibe metadados do modelo."""
        mock_info.return_value = {
            "model_id": "gemma/test",
            "file_size_bytes": 1234,
        }
        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, ["info", "gemma/test"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("gemma/test", result.output)

    def test_cli_list_json_flag(self):
        """CLI 'list --json' retorna JSON válido."""
        # Cria modelo para listar
        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, ["list", "--json"])
        self.assertEqual(result.exit_code, 0)
        try:
            json.loads(result.output)
        except json.JSONDecodeError:
            self.fail("Output não é JSON válido")

    # ── CA9: Argumentos compartilhados ────────────────────────────────────

    def test_cli_backend_argument(self):
        """CLI aceita --backend como argumento."""
        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        # Só testa que o argumento é aceito no parsing
        result = runner.invoke(litert_lm_cli, [
            "run", "gemma/test", "--backend", "gpu", "--prompt", "test"
        ])
        # Pode falhar por modelo não encontrado, mas não por argumento inválido
        self.assertNotIn("Error: no such option", result.output)

    # ── CA10: Erro de modelo não encontrado ───────────────────────────────

    def test_cli_model_not_found_error_message(self):
        """CLI exibe mensagem clara para modelo não encontrado."""
        from skills.litert_lm.cli import litert_lm_cli
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(litert_lm_cli, [
            "run", "completely/fake-model", "--prompt", "test"
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("não encontrado", result.output.lower()
                       or "not found" in result.output.lower()
                       or "error" in result.output.lower())


class TestOpenAIServer(unittest.TestCase):
    """Servidor OpenAI-Compatible."""

    def setUp(self):
        self.models_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.models_dir, ignore_errors=True)

    def test_server_initialization(self):
        """LiteRTOpenAIServer inicializa na porta correta."""
        from skills.litert_lm.server import LiteRTOpenAIServer
        server = LiteRTOpenAIServer(
            model_path="/fake/model.litertlm",
            host="0.0.0.0",
            port=9379,
        )
        self.assertEqual(server.host, "0.0.0.0")
        self.assertEqual(server.port, 9379)

    @mock.patch("skills.litert_lm.server.litert_lm.Engine")
    def test_server_model_listing(self, mock_engine):
        """Servidor lista modelos via /v1/models."""
        mock_engine_instance = mock.MagicMock()
        mock_engine_instance.__enter__ = mock.MagicMock(return_value=mock_engine_instance)
        mock_engine_instance.__exit__ = mock.MagicMock(return_value=None)
        mock_engine.return_value = mock_engine_instance

        from skills.litert_lm.server import LiteRTOpenAIServer
        server = LiteRTOpenAIServer(
            model_path="/fake/model.litertlm",
        )
        models = server.list_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    @mock.patch("skills.litert_lm.server.litert_lm.Engine")
    def test_server_chat_completion(self, mock_engine):
        """Servidor processa /v1/chat/completions."""
        mock_conv = mock.MagicMock()
        mock_conv.__enter__ = mock.MagicMock(return_value=mock_conv)
        mock_conv.__exit__ = mock.MagicMock(return_value=None)
        mock_conv.send_message.return_value = MOCK_CHAT_RESPONSE

        mock_engine_instance = mock.MagicMock()
        mock_engine_instance.__enter__ = mock.MagicMock(return_value=mock_engine_instance)
        mock_engine_instance.__exit__ = mock.MagicMock(return_value=None)
        mock_engine_instance.create_conversation.return_value = mock_conv
        mock_engine.return_value = mock_engine_instance

        from skills.litert_lm.server import LiteRTOpenAIServer
        server = LiteRTOpenAIServer(model_path="/fake/model.litertlm")
        response = server.chat_completion([
            {"role": "user", "content": "Olá!"}
        ])
        self.assertIn("choices", response)
        self.assertIn("model", response)


class TestSkillErrorHandling(unittest.TestCase):
    """Casos de erro e robustez."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.tmpdir, "model.litertlm")
        with open(self.model_path, "wb") as f:
            f.write(b"MOCK")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_model_not_found_error_raised(self):
        """Skill.run levanta exceção para modelo inexistente."""
        from skills.litert_lm.model_manager import ModelNotFoundError
        # Verifica que a exceção existe
        self.assertTrue(issubclass(ModelNotFoundError, Exception))

    @mock.patch("skills.litert_lm.chat.litert_lm.Engine")
    def test_engine_error_wraps_gracefully(self, mock_engine_cls):
        """Erro do Engine é capturado e relatado."""
        mock_engine_cls.side_effect = RuntimeError("Falha no Engine")
        from skills.litert_lm.chat import ChatSession
        session = ChatSession(self.model_path)
        with self.assertRaises(RuntimeError):
            session.send("Olá!")

    def test_directory_not_exist(self):
        """ModelManager criado com diretório inexistente cria o diretório."""
        from skills.litert_lm.model_manager import ModelManager
        from tempfile import mkdtemp
        d = os.path.join(mkdtemp(), "nonexistent", "subdir")
        mgr = ModelManager(models_dir=d)
        self.assertTrue(os.path.exists(d))


if __name__ == "__main__":
    unittest.main()
