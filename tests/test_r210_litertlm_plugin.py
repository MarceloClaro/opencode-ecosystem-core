# -*- coding: utf-8 -*-
"""
Tests SPEC-935-R210 — LiteRT-LM TypeScript Plugin Provider
===========================================================
Rigor TDD: RED → GREEN → REFACTOR
All tests initially RED (plugin file doesn't exist yet).
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PLUGIN_PATH = PROJECT_ROOT / ".opencode" / "plugins" / "litert-lm-provider.ts"
OPCODE_CONFIG_PATH = PROJECT_ROOT / "opencode.json"
SPEC_PATH = PROJECT_ROOT / "specs" / "SPEC-935-R210-litertlm-plugin-provider.md"

# Modelos que DEVEM estar registrados (validação empírica via GET /v1/models do servidor)
REQUIRED_MODELS = [
    "litert-community/gemma-4-E4B-it-litert-lm",
    "litert-community/gemma-4-12B-it-litert-lm",
    "litert-community/gemma-4-E2B-it-litert-lm",
    "litert-community/Qwen3-0.6B",
]

# Campos obrigatórios de cada modelo no retorno do provider hook
MODEL_REQUIRED_FIELDS = [
    "id",
    "providerID",
    "name",
    "capabilities",
    "limit",
    "cost",
    "status",
]


class TestR210PluginExists(unittest.TestCase):
    """RED 1: O arquivo do plugin deve existir."""

    def test_plugin_file_exists(self):
        """CA1: Plugin TypeScript existe em .opencode/plugins/"""
        self.assertTrue(
            PLUGIN_PATH.exists(),
            f"Plugin não encontrado em {PLUGIN_PATH}. Crie o arquivo para passar este teste.",
        )

    def test_plugin_file_not_empty(self):
        """CA1: Plugin TypeScript não está vazio"""
        self.assertGreater(PLUGIN_PATH.stat().st_size, 50)


class TestR210PluginSyntax(unittest.TestCase):
    """RED 2: O plugin deve ser TypeScript válido."""

    def test_plugin_exports_provider(self):
        """O arquivo deve exportar LiteRTProvider ou default com hook provider."""
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")
        content = PLUGIN_PATH.read_text(encoding="utf-8")
        # Verifica se há um export com nome contendo "LiteRT" ou "litert"
        has_export = bool(
            re.search(r"export\s+(const|function|default)\s+\w*[Ll]ite\w*", content)
        )
        self.assertTrue(
            has_export,
            "Plugin deve exportar uma função chamada LiteRTProvider ou similar.\n"
            f"Conteúdo atual: {content[:200]}",
        )

    def test_plugin_imports_plugin_type(self):
        """O plugin deve importar de @opencode-ai/plugin."""
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")
        content = PLUGIN_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "@opencode-ai/plugin",
            content,
            "Plugin deve importar tipos de '@opencode-ai/plugin'",
        )

    def test_plugin_has_provider_hook(self):
        """O hook provider deve estar presente no objeto retornado."""
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")
        content = PLUGIN_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "provider:",
            content,
            "O plugin deve retornar um objeto com a chave 'provider'",
        )
        self.assertIn(
            'id: "litert-lm"',
            content,
            "O provider deve ter id: 'litert-lm'",
        )

    def test_plugin_has_models_function(self):
        """O provider deve ter uma função models()."""
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")
        content = PLUGIN_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "models:",
            content,
            "O provider hook deve ter uma função 'models'",
        )


class TestR210ModelsList(unittest.TestCase):
    """RED 3: Modelos obrigatórios devem estar listados no plugin."""

    def test_all_required_models_present(self):
        """Todos os modelos da SPEC-935-R209 devem estar no plugin."""
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")
        content = PLUGIN_PATH.read_text(encoding="utf-8")
        for model_id in REQUIRED_MODELS:
            with self.subTest(model=model_id):
                self.assertIn(
                    model_id,
                    content,
                    f"Modelo {model_id} deve estar definido no plugin",
                )


class TestR210OpencodeConfig(unittest.TestCase):
    """RED 4: opencode.json deve ter a config do provider litert-lm."""

    def setUp(self):
        with open(OPCODE_CONFIG_PATH, encoding="utf-8") as f:
            self.config = json.load(f)

    def test_provider_section_exists(self):
        """opencode.json deve ter provider.litert-lm"""
        self.assertIn(
            "provider", self.config,
            "opencode.json deve ter seção 'provider'",
        )
        self.assertIn(
            "litert-lm", self.config["provider"],
            "provider deve ter entrada 'litert-lm'",
        )

    def test_provider_has_base_url(self):
        """provider.litert-lm deve ter options.baseURL"""
        provider = self.config["provider"]["litert-lm"]
        self.assertIn(
            "options", provider,
            "provider.litert-lm deve ter 'options'",
        )
        self.assertIn(
            "baseURL", provider["options"],
            "options deve ter 'baseURL'",
        )
        base_url = provider["options"]["baseURL"]
        self.assertIn(
            "9379", base_url,
            f"baseURL deve conter porta 9379, mas é: {base_url}",
        )

    def test_provider_has_api_key(self):
        """provider.litert-lm deve ter options.apiKey"""
        provider = self.config["provider"]["litert-lm"]
        self.assertIn("options", provider)
        self.assertIn(
            "apiKey", provider["options"],
            "options deve ter 'apiKey'",
        )

    def test_provider_has_npm(self):
        """provider.litert-lm deve ter npm: @ai-sdk/openai-compatible"""
        provider = self.config["provider"]["litert-lm"]
        self.assertIn(
            "npm", provider,
            "provider.litert-lm deve ter 'npm' para funcionar como provider custom OpenAI-compatível",
        )
        self.assertEqual(
            provider["npm"],
            "@ai-sdk/openai-compatible",
            "npm deve ser @ai-sdk/openai-compatible para compatibilidade com API OpenAI",
        )

    def test_provider_has_models_section(self):
        """provider.litert-lm deve ter seção models com os modelos do servidor"""
        provider = self.config["provider"]["litert-lm"]
        self.assertIn(
            "models", provider,
            "provider.litert-lm deve ter 'models' registrados no config",
        )
        models = provider["models"]
        self.assertIn(
            "litert-community/gemma-4-E2B-it-litert-lm",
            models,
            "Gemma 4 E2B deve estar listado em models",
        )
        self.assertGreaterEqual(
            len(models), 4,
            f"Devem haver pelo menos 4 modelos. Encontrados: {len(models)}",
        )


class TestR210SpecDocument(unittest.TestCase):
    """RED 5: Spec SDD deve existir e estar completa."""

    def test_spec_exists(self):
        """SPEC-935-R210 existe."""
        self.assertTrue(
            SPEC_PATH.exists(),
            f"Spec não encontrada em {SPEC_PATH}",
        )

    def test_spec_has_acceptance_criteria(self):
        """Spec deve listar acceptance criteria numerados."""
        if not SPEC_PATH.exists():
            self.skipTest("Spec ainda não existe")
        content = SPEC_PATH.read_text(encoding="utf-8")
        self.assertIn("Critérios de Aceitação", content)
        # Deve ter pelo menos 5 CAs
        ca_count = len(re.findall(r"\|\s*CA\d+", content))
        self.assertGreaterEqual(
            ca_count, 5,
            f"Spec deve ter pelo menos 5 critérios de aceitação. Encontrados: {ca_count}",
        )


class TestR210PluginLoadable(unittest.TestCase):
    """RED 6: O plugin deve ser carregável pelo runtime TypeScript do OpenCode.

    NOTA: Este teste requer 'bun' ou 'tsc' instalado. Se não estiver disponível,
    o teste é pulado com skip.
    """

    @classmethod
    def setUpClass(cls):
        cls.bun_available = (
            subprocess.run(
                ["which", "bun"], capture_output=True, text=True
            ).returncode
            == 0
        )
        cls.node_available = (
            subprocess.run(
                ["which", "node"], capture_output=True, text=True
            ).returncode
            == 0
        )
        cls.tsc_available = (
            subprocess.run(
                ["which", "tsc"], capture_output=True, text=True
            ).returncode
            == 0
        )

    def _make_temp_package_json(self, tmpdir: Path):
        """Cria um package.json temporário com as dependências necessárias."""
        pkg = {
            "name": "test-litert-plugin",
            "private": True,
            "dependencies": {
                "@opencode-ai/plugin": "latest",
            },
        }
        pkg_path = tmpdir / "package.json"
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(pkg, f)
        return pkg_path

    def test_plugin_compiles_with_bun(self):
        """Se bun estiver disponível, o plugin deve compilar sem erros."""
        if not self.bun_available:
            self.skipTest("bun não está instalado")
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            # Copia plugin para diretório temporário
            plugin_dest = tmp / "litert-lm-provider.ts"
            plugin_dest.write_text(PLUGIN_PATH.read_text(encoding="utf-8"))
            self._make_temp_package_json(tmp)

            # Tenta compilar com bun
            result = subprocess.run(
                ["bun", "build", str(plugin_dest)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmp,
            )
            if result.returncode != 0:
                print(f"STDERR: {result.stderr}", file=sys.stderr)
            self.assertEqual(
                result.returncode,
                0,
                f"Plugin não compila com bun:\n{result.stderr}",
            )

    def test_plugin_syntax_valid_typescript(self):
        """Validação básica de sintaxe TypeScript (sem compilação)."""
        if not PLUGIN_PATH.exists():
            self.skipTest("Plugin ainda não existe")
        content = PLUGIN_PATH.read_text(encoding="utf-8")

        # Verificações básicas de sanidade
        self.assertFalse(
            content.startswith("<<<<<<<"),
            "Plugin contém marcador de conflito git (<<<<<<<)",
        )
        self.assertFalse(
            ">>>>>>>" in content,
            "Plugin contém marcador de conflito git (>>>>>>>)",
        )
        # Chaves devem estar balanceadas aproximadamente
        opens = content.count("{")
        closes = content.count("}")
        self.assertEqual(
            opens, closes,
            f"Chaves desbalanceadas: {opens} abertas, {closes} fechadas",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
