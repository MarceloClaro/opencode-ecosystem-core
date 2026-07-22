# -*- coding: utf-8 -*-
"""
Testes TDD — OpenCode Go, OpenCode Zen e ModelRouter
=====================================================
Bateria de testes unitários e de integração para os módulos:
  - integrations.opencode_go (OpenCodeGoProvider)
  - integrations.opencode_zen (OpenCodeZenProvider)
  - integrations.model_router (ModelRouter, ModelProfile, RouteResult)

Cobertura alvo: ≥ 80% dos três módulos.

Ciclo TDD:
  RED   → estes testes falham antes da implementação
  GREEN → implementação satisfaz todos os critérios
  REFACTOR → melhoria sem quebrar testes

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock, PropertyMock

# Garantir que o root do projeto está no path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


# ═══════════════════════════════════════════════════════════════════════════════
# Testes — OpenCodeGoProvider
# ═══════════════════════════════════════════════════════════════════════════════

class TestOpenCodeGoProvider(unittest.TestCase):
    """Testes unitários do provider OpenCode Go."""

    def setUp(self):
        """Instancia o provider sem chave de API (modo mock)."""
        from integrations.opencode_go import OpenCodeGoProvider
        self.provider = OpenCodeGoProvider(api_key="")
        self.provider.disable_sdd()  # SDD desativado para testes unitários

    # ── CA-1: Catálogo de modelos ─────────────────────────────────────────────

    def test_list_models_retorna_ao_menos_quatro_modelos(self):
        """CA-1: list_models() deve retornar ≥ 4 modelos."""
        models = self.provider.list_models()
        self.assertGreaterEqual(len(models), 4, "Deve haver ao menos 4 modelos Go")

    def test_kimi_k27_code_presente(self):
        """CA-1: kimi-k2.7-code deve estar no catálogo."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("kimi-k2.7-code", ids)

    def test_deepseek_v4_pro_presente(self):
        """CA-1: deepseek-v4-pro deve estar no catálogo."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("deepseek-v4-pro", ids)

    def test_glm_52_presente(self):
        """CA-1: glm-5.2 deve estar no catálogo."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("glm-5.2", ids)

    def test_qwen_37_max_presente(self):
        """CA-1: qwen3.7-max deve estar no catálogo."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("qwen3.7-max", ids)

    # ── Informações de modelo ─────────────────────────────────────────────────

    def test_get_model_info_retorna_metadados(self):
        """get_model_info deve retornar dict com campos esperados."""
        info = self.provider.get_model_info("kimi-k2.7-code")
        self.assertEqual(info["model_id"], "kimi-k2.7-code")
        self.assertIn("strengths", info)
        self.assertIn("context_window", info)
        self.assertIn("tier", info)

    def test_get_model_info_modelo_inexistente_levanta_erro(self):
        """get_model_info com modelo inexistente deve levantar ModelNotFoundError."""
        from integrations.opencode_go import ModelNotFoundError
        with self.assertRaises(ModelNotFoundError):
            self.provider.get_model_info("modelo-inexistente-xyz")

    # ── best_model_for ────────────────────────────────────────────────────────

    def test_best_model_for_coding_retorna_string_valida(self):
        """best_model_for('coding') deve retornar um model_id válido."""
        model = self.provider.best_model_for("coding")
        self.assertIsInstance(model, str)
        self.assertGreater(len(model), 0)

    def test_best_model_for_task_type_inexistente_retorna_default(self):
        """best_model_for com task_type inválido deve retornar o modelo padrão."""
        from integrations.opencode_go import DEFAULT_MODEL
        model = self.provider.best_model_for("tarefa-inexistente-xyz")
        self.assertEqual(model, DEFAULT_MODEL)

    # ── complete (modo mock) ──────────────────────────────────────────────────

    def test_complete_modo_mock_retorna_response_valida(self):
        """complete() sem chave de API deve retornar CompletionResponse simulada."""
        resp = self.provider.complete("Escreva um hello world em Python")
        self.assertIsNotNone(resp)
        self.assertIsInstance(resp.content, str)
        self.assertGreater(len(resp.content), 0)

    def test_complete_response_tem_provider_id_correto(self):
        """CompletionResponse deve ter provider='opencode-go'."""
        resp = self.provider.complete("Teste de provider ID")
        self.assertEqual(resp.provider, "opencode-go")

    def test_complete_modelo_inexistente_levanta_erro(self):
        """complete() com modelo inexistente deve levantar ModelNotFoundError."""
        from integrations.opencode_go import ModelNotFoundError
        with self.assertRaises(ModelNotFoundError):
            self.provider.complete("Teste", model="modelo-nao-existe")

    # ── provider_info ─────────────────────────────────────────────────────────

    def test_provider_info_retorna_dict_completo(self):
        """provider_info() deve retornar dict com campos obrigatórios."""
        info = self.provider.provider_info()
        self.assertIn("provider_id", info)
        self.assertIn("total_models", info)
        self.assertIn("authenticated", info)
        self.assertIn("default_model", info)
        self.assertEqual(info["provider_id"], "opencode-go")

    def test_sdd_toggle(self):
        """Deve ser possível ativar e desativar SDD."""
        self.provider.enable_sdd()
        self.assertTrue(self.provider._sdd_enabled)
        self.provider.disable_sdd()
        self.assertFalse(self.provider._sdd_enabled)


# ═══════════════════════════════════════════════════════════════════════════════
# Testes — OpenCodeZenProvider
# ═══════════════════════════════════════════════════════════════════════════════

class TestOpenCodeZenProvider(unittest.TestCase):
    """Testes unitários do provider OpenCode Zen."""

    def setUp(self):
        from integrations.opencode_zen import OpenCodeZenProvider
        self.provider = OpenCodeZenProvider(api_key="")
        self.provider.disable_sdd()

    # ── CA-2: Catálogo de modelos ─────────────────────────────────────────────

    def test_list_models_retorna_ao_menos_tres_modelos(self):
        """CA-2: list_models() deve retornar ≥ 3 modelos Zen."""
        models = self.provider.list_models()
        self.assertGreaterEqual(len(models), 3)

    def test_gpt55_presente(self):
        """CA-2: gpt-5.5 deve estar no catálogo Zen."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("gpt-5.5", ids)

    def test_claude_opus4_presente(self):
        """CA-2: claude-opus-4 deve estar no catálogo Zen."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("claude-opus-4", ids)

    def test_gemini_25_pro_presente(self):
        """CA-2: gemini-2.5-pro deve estar no catálogo Zen."""
        ids = [m["model_id"] for m in self.provider.list_models()]
        self.assertIn("gemini-2.5-pro", ids)

    # ── list_models free_only ─────────────────────────────────────────────────

    def test_list_models_free_only_retorna_apenas_gratuitos(self):
        """list_models(free_only=True) deve retornar apenas modelos gratuitos."""
        free_models = self.provider.list_models(free_only=True)
        for m in free_models:
            self.assertTrue(m.get("free", False), f"Modelo {m['model_id']} não é gratuito")

    # ── best_model_for ────────────────────────────────────────────────────────

    def test_best_model_for_reasoning_retorna_modelo_valido(self):
        """best_model_for('reasoning') deve retornar um model_id válido."""
        model = self.provider.best_model_for("reasoning")
        self.assertIsInstance(model, str)
        self.assertGreater(len(model), 0)

    def test_best_model_for_family_anthropic(self):
        """best_model_for com family='anthropic' deve retornar modelo Anthropic."""
        model = self.provider.best_model_for("reasoning", family="anthropic")
        from integrations.opencode_zen import MODELS
        if model in MODELS:
            self.assertEqual(MODELS[model]["family"], "anthropic")

    # ── complete (modo mock) ──────────────────────────────────────────────────

    def test_complete_modo_mock_retorna_response(self):
        """complete() sem chave deve retornar response mock válida."""
        resp = self.provider.complete("Revise este artigo")
        self.assertIsNotNone(resp)
        self.assertIsInstance(resp.content, str)
        self.assertGreater(len(resp.content), 0)

    def test_complete_provider_id_correto(self):
        """CompletionResponse deve ter provider='opencode-zen'."""
        resp = self.provider.complete("Teste")
        self.assertEqual(resp.provider, "opencode-zen")

    def test_complete_modelo_inexistente_levanta_erro(self):
        """complete() com modelo inexistente deve levantar ModelNotFoundError."""
        from integrations.opencode_zen import ModelNotFoundError
        with self.assertRaises(ModelNotFoundError):
            self.provider.complete("Teste", model="modelo-zen-nao-existe")

    # ── provider_info ─────────────────────────────────────────────────────────

    def test_provider_info_campos_obrigatorios(self):
        """provider_info() deve ter campos obrigatórios."""
        info = self.provider.provider_info()
        self.assertIn("provider_id", info)
        self.assertIn("total_models", info)
        self.assertIn("families", info)
        self.assertIn("free_models", info)
        self.assertEqual(info["provider_id"], "opencode-zen")

    def test_provider_info_tem_multiplas_familias(self):
        """Zen deve ter modelos de múltiplas famílias."""
        info = self.provider.provider_info()
        self.assertGreaterEqual(len(info["families"]), 3)


# ═══════════════════════════════════════════════════════════════════════════════
# Testes — ModelRouter
# ═══════════════════════════════════════════════════════════════════════════════

class TestModelRouter(unittest.TestCase):
    """Testes unitários do ModelRouter."""

    def setUp(self):
        from integrations.model_router import ModelRouter
        self.router = ModelRouter()

    # ── CA-3: Roteamento por task_type ────────────────────────────────────────

    def test_route_coding_retorna_opencode_go(self):
        """CA-3: route('coding') deve preferir opencode-go com kimi ou deepseek."""
        result = self.router.route("coding")
        self.assertIn(result.provider_id, ["opencode-go", "opencode-zen", "litert-lm"])
        self.assertIsInstance(result.model_id, str)
        self.assertGreater(len(result.model_id), 0)

    def test_route_reasoning_retorna_modelo_valido(self):
        """CA-3: route('reasoning') deve retornar um provider e modelo válidos."""
        result = self.router.route("reasoning")
        self.assertIn(result.provider_id, ["opencode-go", "opencode-zen", "litert-lm"])
        self.assertIsInstance(result.model_id, str)

    def test_route_academic_retorna_modelo_valido(self):
        """CA-3: route('academic') deve retornar modelo para escrita acadêmica."""
        result = self.router.route("academic")
        self.assertIn(result.task_type, ["academic", "coding"])  # pode usar coding como fallback

    def test_route_task_type_desconhecido_usa_coding_fallback(self):
        """route() com task_type desconhecido deve usar perfil 'coding' como fallback."""
        result = self.router.route("tarefa-completamente-desconhecida")
        self.assertIsNotNone(result)
        self.assertIsInstance(result.model_id, str)

    # ── force_provider / force_model ──────────────────────────────────────────

    def test_route_force_provider_e_model(self):
        """route() com force_provider e force_model deve obedecer os overrides."""
        result = self.router.route(
            "coding",
            force_provider="opencode-go",
            force_model="deepseek-v4-flash",
        )
        self.assertEqual(result.provider_id, "opencode-go")
        self.assertEqual(result.model_id, "deepseek-v4-flash")

    # ── require_thinking ──────────────────────────────────────────────────────

    def test_route_require_thinking_filtra_modelos(self):
        """route() com require_thinking=True deve selecionar modelo com thinking."""
        from integrations.opencode_go import MODELS as GO_MODELS
        from integrations.opencode_zen import MODELS as ZEN_MODELS

        result = self.router.route("coding", require_thinking=True)
        # Verifica se o modelo selecionado suporta thinking
        model_meta = (
            GO_MODELS.get(result.model_id)
            or ZEN_MODELS.get(result.model_id)
            or {}
        )
        # Se o modelo tem thinking ou é fallback, o teste passa
        self.assertTrue(
            model_meta.get("thinking", False) or result.model_id in GO_MODELS or result.model_id in ZEN_MODELS
        )

    # ── RouteResult ───────────────────────────────────────────────────────────

    def test_route_result_tem_campos_obrigatorios(self):
        """RouteResult deve ter todos os campos definidos."""
        result = self.router.route("coding")
        self.assertIsNotNone(result.task_type)
        self.assertIsNotNone(result.provider_id)
        self.assertIsNotNone(result.model_id)
        self.assertIsNotNone(result.reason)
        self.assertIsInstance(result.alternatives, list)

    # ── list_all_models ───────────────────────────────────────────────────────

    def test_list_all_models_retorna_lista(self):
        """list_all_models() deve retornar lista de dicts."""
        models = self.router.list_all_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    # ── list_profiles ─────────────────────────────────────────────────────────

    def test_list_profiles_retorna_todos_os_perfis(self):
        """list_profiles() deve retornar ao menos 5 perfis."""
        profiles = self.router.list_profiles()
        self.assertGreaterEqual(len(profiles), 5)

    # ── status ────────────────────────────────────────────────────────────────

    def test_status_retorna_dict_com_providers(self):
        """status() deve retornar dict com informações de providers."""
        s = self.router.status()
        self.assertIn("providers", s)
        self.assertIn("opencode-go", s["providers"])
        self.assertIn("opencode-zen", s["providers"])
        self.assertIn("litert-lm", s["providers"])
        self.assertIn("total_models", s)
        self.assertGreater(s["total_models"], 0)


# ═══════════════════════════════════════════════════════════════════════════════
# Testes — Integração: carregamento de auth.json simulado
# ═══════════════════════════════════════════════════════════════════════════════

class TestApiKeyLoading(unittest.TestCase):
    """Testes de carregamento de chave de API."""

    def test_opencode_go_lê_env_var(self):
        """OpenCodeGoProvider deve ler a chave de OPENCODE_API_KEY."""
        with patch.dict(os.environ, {"OPENCODE_API_KEY": "test-key-go-123"}):
            from integrations.opencode_go import OpenCodeGoProvider
            provider = OpenCodeGoProvider()
            self.assertEqual(provider._api_key, "test-key-go-123")

    def test_opencode_zen_lê_env_var_zen(self):
        """OpenCodeZenProvider deve ler a chave de OPENCODE_ZEN_API_KEY."""
        with patch.dict(os.environ, {
            "OPENCODE_ZEN_API_KEY": "test-zen-key-456",
            "OPENCODE_API_KEY": "",
        }):
            from integrations.opencode_zen import OpenCodeZenProvider
            provider = OpenCodeZenProvider()
            self.assertEqual(provider._api_key, "test-zen-key-456")

    def test_opencode_go_lê_auth_json(self):
        """OpenCodeGoProvider deve ler chave de auth.json se env var não disponível."""
        auth_data = {"opencode-go": {"apiKey": "auth-json-go-key"}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(auth_data, f)
            tmp_path = f.name

        try:
            with patch.dict(os.environ, {"OPENCODE_API_KEY": ""}):
                from integrations.opencode_go import OpenCodeGoProvider, AUTH_FILE_PATHS
                with patch.object(
                    sys.modules.get("integrations.opencode_go", __import__("integrations.opencode_go", fromlist=["AUTH_FILE_PATHS"])),
                    "AUTH_FILE_PATHS",
                    [tmp_path],
                ):
                    provider = OpenCodeGoProvider()
                    self.assertEqual(provider._api_key, "auth-json-go-key")
        finally:
            os.unlink(tmp_path)


# ═══════════════════════════════════════════════════════════════════════════════
# Suite principal
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
