# -*- coding: utf-8 -*-
"""Testes da integração Haystack (SPEC-935-R604) — padrão M7.

Haystack é framework Python (não CLI). Estes testes validam o wrapper
integrations/haystack_cli.py SEM exigir `pip install haystack-ai`:

- disponibilidade/versão (importlib.util.find_spec / metadata)
- build_rag_pipeline falha graciosamente sem o pacote (nunca lança)
- run_retrieval valida entradas e propaga erros sem lançar
- doctor_check warn (nunca fail) quando ausente
- CLI: status/doctor/install sem instalação real

Quando haystack_ai estiver instalado, os mesmos testes rodam contra o
pacote real (smoke) — sem depender disso para passarem.
"""

import json
import sys

import pytest

# Reseta caches entre testes (importlib/metadata)
import integrations.haystack_cli as h


@pytest.fixture(autouse=True)
def _reset_caches():
    h._AVAILABLE_CACHE = None
    h._VERSION_CACHE = None
    yield
    h._AVAILABLE_CACHE = None
    h._VERSION_CACHE = None


class TestDisponibilidade:
    def test_haystack_available_false_sem_pacote(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: False)
        assert h.haystack_available() is False

    def test_haystack_available_true_se_instalado(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: True)
        assert h.haystack_available() is True

    def test_versao_none_sem_pacote(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: False)
        assert h.haystack_version() is None

    def test_versao_metadata_quando_instalado(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: True)
        monkeypatch.setattr(
            "importlib.metadata.version",
            lambda dist: "3.2.0"
            if dist == "haystack-ai"
            else (_ for _ in ()).throw(ValueError(dist)),
        )
        assert h.haystack_version() == "3.2.0"
        # cache de versão respeitado
        assert h.haystack_version() == "3.2.0"

    def test_versao_tolerante_metadata_quebra(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: True)

        def boom(dist):
            raise Exception("metadata corrupta")

        monkeypatch.setattr("importlib.metadata.version", boom)
        assert h.haystack_version() is None


class TestBuildRagPipeline:
    def test_build_sem_pacote_ok_false_sem_excecao(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: False)
        resultado = h.build_rag_pipeline(
            [{"content": "docs", "meta": {"a": 1}}]
        )
        assert resultado["ok"] is False
        assert resultado["pipeline"] is None
        assert "haystack_ai não instalado" in resultado["error"]
        assert "pip install haystack-ai" in resultado["install"]

    def test_build_com_pacote_mockado_indexa_docs(self, monkeypatch):
        # Simula um ambiente com haystack_ai: componentes mock no nível certo
        monkeypatch.setattr(h, "_installed", lambda: True)

        class FakeDoc:
            def __init__(self, content="", meta=None):
                self.content = content
                self.meta = meta or {}

        class FakeDocEmbedder:
            def __init__(self, model=None):
                self.model = model

            def run(self, data):
                return {"documents": data["documents"]}

        class FakeStore:
            _written = []

            def write_documents(self, docs):
                FakeStore._written = docs

        class FakeRetriever:
            def __init__(self, document_store=None, top_k=3):
                self.document_store = document_store
                self.top_k = top_k

        class FakeTextEmbedder:
            def __init__(self, model=None):
                self.model = model

        class FakePipeline:
            def __init__(self):
                self.added = {}

            def add_component(self, name, comp):
                self.added[name] = comp

            def connect(self, a, b):
                pass

        monkeypatch.setattr(
            h, "_import_haystack",
            lambda: (FakePipeline, FakeDoc),
        )
        monkeypatch.setattr(
            h, "_import_components",
            lambda: {
                "store": FakeStore,
                "retriever": FakeRetriever,
                "doc_embedder": FakeDocEmbedder,
                "text_embedder": FakeTextEmbedder,
            },
        )

        resultado = h.build_rag_pipeline(
            [{"content": "conteudo valido", "meta": {"origem": "x"}}]
        )
        assert resultado["ok"] is True
        assert resultado["documents_indexed"] == 1
        assert resultado["top_k"] == 3
        assert FakeStore._written  # docs escritos no store

    def test_build_filtra_docs_vazios_e_protege_erro(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: True)

        def boom(*a, **k):
            raise RuntimeError("componente quebrou")

        monkeypatch.setattr(h, "_import_haystack", boom)
        resultado = h.build_rag_pipeline([{"content": "x"}])
        assert resultado["ok"] is False
        assert "componente quebrou" in resultado["error"]

    def test_docs_vazios_nao_quebram(self, monkeypatch):
        # Sem haystack, mas entrada vazia não deve lançar (retorna ids de doc 0)
        monkeypatch.setattr(h, "_installed", lambda: False)
        resultado = h.build_rag_pipeline([])
        assert resultado["ok"] is False


class TestRunRetrieval:
    def test_run_sem_pipeline_ok_false(self):
        resultado = h.run_retrieval(None, "consulta")
        assert resultado["ok"] is False
        assert "pipeline ausente" in resultado["error"]

    def test_run_com_query_vazia(self):
        resultado = h.run_retrieval(object(), "   ")
        assert resultado["ok"] is False
        assert "query vazia" in resultado["error"]

    def test_run_com_pipeline_mock(self, monkeypatch):
        class FakeDoc:
            def __init__(self, content, score, meta):
                self.content = content
                self.score = score
                self.meta = meta

        class FakePipeline:
            def run(self, dados):
                return {
                    "retriever": {
                        "documents": [
                            FakeDoc("achado A", 0.98, {"org": "y"}),
                            FakeDoc("achado B", 0.77, {}),
                        ]
                    }
                }

        resultado = h.run_retrieval(FakePipeline(), "consulta")
        assert resultado["ok"] is True
        assert resultado["count"] == 2
        assert resultado["documents"][0]["content"] == "achado A"
        assert resultado["documents"][0]["score"] == 0.98

    def test_run_protege_excecao(self, monkeypatch):
        class Ruim:
            def run(self, dados):
                raise ValueError("query malformada")

        resultado = h.run_retrieval(Ruim(), "consulta")
        assert resultado["ok"] is False
        assert "query malformada" in resultado["error"]


class TestDoctorCheck:
    def test_doctor_warn_sem_pacote(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: False)
        check = h.doctor_check()
        assert check["name"] == "haystack"
        assert check["status"] == "warn"  # nunca fail
        assert "não instalado" in check["detail"]

    def test_doctor_pass_com_pacote_mock(self, monkeypatch):
        monkeypatch.setattr(h, "_installed", lambda: True)
        monkeypatch.setattr(h, "haystack_version", lambda: "3.2.0")

        class FakePipeline:
            def __init__(self):
                pass

        monkeypatch.setattr(h, "_import_haystack", lambda: (FakePipeline, object))
        check = h.doctor_check()
        assert check["status"] == "pass"
        assert "v3.2.0" in check["detail"]


class TestCLI:
    def test_help(self, capsys):
        assert h.main(["--help"]) == 0
        out = capsys.readouterr().out
        assert "status" in out and "doctor" in out and "install" in out

    def test_status_sem_pacote_exit_1(self, monkeypatch, capsys):
        monkeypatch.setattr(h, "_installed", lambda: False)
        assert h.main(["status"]) == 1
        out = capsys.readouterr().out
        assert "NÃO INSTALADO" in out

    def test_status_com_pacote_exit_0(self, monkeypatch, capsys):
        monkeypatch.setattr(h, "_installed", lambda: True)
        monkeypatch.setattr(h, "haystack_version", lambda: "3.2.0")
        assert h.main(["status"]) == 0
        out = capsys.readouterr().out
        assert "v3.2.0" in out.replace("versão      ", "v")

    def test_install(self, capsys):
        assert h.main(["install"]) == 0
        out = capsys.readouterr().out
        assert "pip install haystack-ai" in out

    def test_doctor_warn_exit_1(self, monkeypatch, capsys):
        monkeypatch.setattr(h, "_installed", lambda: False)
        assert h.main(["doctor"]) == 1
        out = capsys.readouterr().out
        assert "warn" in out

    def test_subcomando_desconhecido_exit_2(self, monkeypatch, capsys):
        monkeypatch.setattr(h, "_installed", lambda: False)
        assert h.main(["inexistente"]) == 2

    def test_sem_argumentos_mostra_uso(self, capsys):
        assert h.main([]) == 0


class TestIntegracaoInstalada:
    """Smoke opcional: roda APENAS se haystack-ai estiver instalado."""

    def test_health_real_se_instalado(self):
        if not h._installed():
            pytest.skip("haystack-ai não instalado; smoke opcional")
        assert h.haystack_available() is True
        versao = h.haystack_version()
        assert versao and versao.count(".") >= 1
        check = h.doctor_check()
        assert check["status"] in ("pass", "warn")