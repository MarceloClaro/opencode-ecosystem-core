# -*- coding: utf-8 -*-
"""
Testes R128 — Encanamento seguro de chaves LLM (OpenAI) via ambiente
=====================================================================
Escritos ANTES da implementação (TDD). Garantem que:
  - `.env` é ignorado pelo git e `.env.example` permanece versionável;
  - `.env.example` não contém nenhum segredo;
  - o `doctor` reporta a disponibilidade de provedor LLM SEM jamais
    expor o valor da chave.

Princípio: segredo nunca entra no repositório nem em log/saída.

Requisitos: SPEC-935-R128.
"""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# ── CA-1: .gitignore protege .env, mantém .env.example ────────────
def test_env_e_ignorado_pelo_git():
    r = subprocess.run(["git", "check-ignore", ".env"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, ".env deveria estar no .gitignore"


def test_env_example_nao_e_ignorado():
    r = subprocess.run(["git", "check-ignore", ".env.example"], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode != 0, ".env.example deveria permanecer versionável"


# ── CA-2: .env.example é modelo sem segredo ───────────────────────
def test_env_example_existe_e_nomeia_openai():
    ex = ROOT / ".env.example"
    assert ex.exists(), ".env.example ausente"
    conteudo = ex.read_text(encoding="utf-8")
    assert "OPENAI_API_KEY" in conteudo


def test_env_example_nao_contem_segredo():
    conteudo = (ROOT / ".env.example").read_text(encoding="utf-8")
    # nenhum valor de chave real (OpenAI usa prefixo sk-)
    assert "sk-" not in conteudo, ".env.example NÃO pode conter chave real"
    # a linha da chave deve estar vazia (só o nome + '=')
    for line in conteudo.splitlines():
        if line.strip().startswith("OPENAI_API_KEY"):
            assert line.split("=", 1)[1].strip() == "", \
                "OPENAI_API_KEY deve vir vazia no modelo"


# ── CA-3/CA-4: doctor reporta provedor sem vazar a chave ──────────
class TestDoctorLLMCheck:
    def test_pass_quando_openai_key_definida(self, monkeypatch):
        from marceloclaro import doctor as d
        monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-somente-para-teste-XYZ")
        # sem Ollama, mas com a chave → pass
        monkeypatch.setattr(d, "_ollama_available", lambda: False, raising=False)
        check = d._check_llm_providers()
        assert check.status == "pass"

    def test_warn_quando_nenhum_provedor(self, monkeypatch):
        from marceloclaro import doctor as d
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr(d, "_ollama_available", lambda: False, raising=False)
        check = d._check_llm_providers()
        assert check.status == "warn"

    def test_nunca_fail(self, monkeypatch):
        from marceloclaro import doctor as d
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr(d, "_ollama_available", lambda: False, raising=False)
        assert d._check_llm_providers().status != "fail"

    def test_detail_nunca_vaza_o_valor_da_chave(self, monkeypatch):
        from marceloclaro import doctor as d
        segredo = "sk-super-secreto-nao-deve-aparecer-1234567890"
        monkeypatch.setenv("OPENAI_API_KEY", segredo)
        check = d._check_llm_providers()
        assert segredo not in check.detail
        # também não pode vazar via dict serializado
        assert segredo not in str(check.to_dict())


# ── CA-5: run_doctor inclui o check ───────────────────────────────
def test_run_doctor_inclui_llm_providers(monkeypatch):
    from marceloclaro import doctor as d
    report = d.run_doctor()
    nomes = [c["name"] for c in report["checks"]]
    assert "llm_providers" in nomes


# ── loader de .env (acessibilidade: sem exportação manual) ────────
class TestEnvLoader:
    def test_carrega_variaveis_do_arquivo(self, tmp_path, monkeypatch):
        from marceloclaro.env_loader import load_dotenv
        env = tmp_path / ".env"
        env.write_text("FOO_R128=bar\nexport BAZ_R128=\"qux\"\n", encoding="utf-8")
        monkeypatch.delenv("FOO_R128", raising=False)
        monkeypatch.delenv("BAZ_R128", raising=False)
        n = load_dotenv(str(env))
        assert n == 2
        assert os.environ["FOO_R128"] == "bar"
        assert os.environ["BAZ_R128"] == "qux"  # aspas e 'export ' tratados

    def test_nao_sobrescreve_ambiente_existente(self, tmp_path, monkeypatch):
        from marceloclaro.env_loader import load_dotenv
        env = tmp_path / ".env"
        env.write_text("JA_R128=novo\n", encoding="utf-8")
        monkeypatch.setenv("JA_R128", "original")
        load_dotenv(str(env), override=False)
        assert os.environ["JA_R128"] == "original"  # shell tem prioridade

    def test_arquivo_ausente_nao_quebra(self, tmp_path):
        from marceloclaro.env_loader import load_dotenv
        assert load_dotenv(str(tmp_path / "nao-existe.env")) == 0

    def test_ignora_linha_vazia_do_modelo(self, tmp_path, monkeypatch):
        from marceloclaro.env_loader import load_dotenv
        env = tmp_path / ".env"
        env.write_text("VAZIA_R128=\n# comentario\n", encoding="utf-8")
        monkeypatch.delenv("VAZIA_R128", raising=False)
        load_dotenv(str(env))
        assert "VAZIA_R128" not in os.environ  # não define com vazio
