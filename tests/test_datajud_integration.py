# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-922: Integração Datajud + Raciocínio Jurídico
=================================================================
RED → GREEN → REFACTOR:

Cobertura:
  1. DatajudClient — busca mockada em tribunal específico, busca em tribunal inválido
  2. DatajudClient — busca todos os tribunais, get_process
  3. Conversores — process_to_precedent, process_to_legal_fact, process_to_legal_argument
  4. Integração — LegalDatajudIntegration.load_processes, analyze_process
  5. Modo offline — funciona sem API key
  6. Tribunais — list_tribunals retorna 27 tribunais
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════════════════
# 1. DatajudClient — Operações básicas
# ═══════════════════════════════════════════════════════════════════════════


class TestDatajudClientBasics:
    """Testes básicos do cliente Datajud em modo offline."""

    def test_search_returns_processos(self):
        """CT1: search() retorna lista de DatajudProcess para tribunal válido."""
        from legal import DatajudClient

        client = DatajudClient(offline=True)
        results = client.search("tjsp")

        assert len(results) > 0
        for proc in results:
            assert isinstance(proc.id, str)
            assert proc.tribunal == "tjsp"
            assert proc.numero_processo != ""

    def test_search_invalid_tribunal_raises(self):
        """CT2: search() levanta ValueError para tribunal inexistente."""
        from legal import DatajudClient

        client = DatajudClient(offline=True)
        try:
            client.search("tjj")
            assert False, "Deveria ter levantado ValueError"
        except ValueError as e:
            assert "não reconhecido" in str(e).lower()

    def test_search_all_returns_dict(self):
        """CT3: search_all() retorna dict com tribunais como chaves."""
        from legal import DatajudClient

        client = DatajudClient(offline=True)
        results = client.search_all(tribunais=["tjsp", "tjrj"])

        assert "tjsp" in results
        assert "tjrj" in results
        assert len(results["tjsp"]) > 0
        assert len(results["tjrj"]) > 0

    def test_get_process_found(self):
        """CT4: get_process() retorna processo específico."""
        from legal import DatajudClient

        client = DatajudClient(offline=True)
        proc = client.get_process("1000001-12.2020.8.26.0001", "tjsp")

        assert proc is not None
        assert proc.numero_processo == "1000001-12.2020.8.26.0001"

    def test_get_process_not_found(self):
        """CT5: get_process() retorna None para processo inexistente."""
        from legal import DatajudClient

        client = DatajudClient(offline=True)
        proc = client.get_process("INEXISTENTE-999", "tjsp")

        assert proc is None

    def test_list_tribunals_27(self):
        """CT6: list_tribunals() retorna os 27 tribunais estaduais."""
        from legal import DatajudClient

        client = DatajudClient(offline=True)
        tribunais = client.list_tribunals()

        assert len(tribunais) == 27
        siglas = {t["sigla"] for t in tribunais}
        assert "tjsp" in siglas
        assert "tjrj" in siglas
        assert "tjmg" in siglas
        assert "tjrs" in siglas


# ═══════════════════════════════════════════════════════════════════════════
# 2. DatajudProcess — Propriedades e conversão
# ═══════════════════════════════════════════════════════════════════════════


class TestDatajudProcess:
    """Testes do modelo DatajudProcess."""

    def test_process_properties(self):
        """CT7: Propriedades derivadas do processo."""
        from legal.datajud_client import DatajudProcess

        proc = DatajudProcess(
            id="test-001",
            tribunal="tjsp",
            numero_processo="1000001-12.2020.8.26.0001",
            classe={"codigo": 7, "nome": "Procedimento Comum Cível"},
            assuntos=[{"codigo": 1234, "nome": "Obrigação de Fazer / Não Fazer"}],
            movimentos=[{"codigo": 51, "nome": "Sentença", "dataHora": "2020-06-10T09:00:00Z",
                        "complementosTabelados": [{"codigo": 1, "descricao": "Procedente", "valor": 1}]}],
        )

        assert proc.tribunal_nome == "São Paulo"
        assert proc.assunto_principal == "Obrigação de Fazer / Não Fazer"
        assert proc.classe_nome == "Procedimento Comum Cível"
        assert "Procedente" in (proc.resultado or "")

    def test_ementa_texto_generated(self):
        """CT8: ementa_texto gera string descritiva."""
        from legal.datajud_client import DatajudProcess

        proc = DatajudProcess(
            id="test-002",
            tribunal="tjrj",
            numero_processo="0000001-12.2021.8.19.0001",
            classe={"codigo": 198, "nome": "Apelação Cível"},
            assuntos=[{"codigo": 7890, "nome": "Responsabilidade Civil do Estado"}],
        )

        ementa = proc.ementa_texto
        assert "tjrj" in ementa.lower() or "Rio de Janeiro" in ementa
        assert "Apelação" in ementa
        assert "Responsabilidade" in ementa

    def test_from_api_conversion(self):
        """CT9: from_api converte JSON da API corretamente."""
        from legal.datajud_client import DatajudProcess

        raw = {
            "id": "api-001",
            "tribunal": "TJSP",
            "numeroProcesso": "1000001-12.2020.8.26.0001",
            "dataAjuizamento": "2020-01-15T10:00:00Z",
            "grau": "primeiro",
            "nivelSigilo": 0,
            "classe": {"codigo": 7, "nome": "Procedimento Comum Cível"},
            "assuntos": [{"codigo": 1234, "nome": "Teste"}],
            "movimentos": [],
        }

        proc = DatajudProcess.from_api(raw)
        assert proc.id == "api-001"
        assert proc.tribunal == "tjsp"  # lowercased
        assert proc.data_ajuizamento is not None
        assert proc.grau == "primeiro"


# ═══════════════════════════════════════════════════════════════════════════
# 3. Conversores — DatajudProcess → Tipos do módulo legal/
# ═══════════════════════════════════════════════════════════════════════════


class TestDatajudConverters:
    """Testes dos conversores entre DatajudProcess e tipos legais."""

    def test_process_to_precedent(self):
        """CT10: process_to_precedent() produz Precedent válido."""
        from legal.datajud_client import DatajudProcess
        from legal.integration import process_to_precedent
        from legal import PrecedentType

        proc = DatajudProcess(
            id="conv-001", tribunal="tjsp",
            numero_processo="1000001-12.2020.8.26.0001",
            classe={"codigo": 7, "nome": "Procedimento Comum Cível"},
            assuntos=[{"codigo": 1234, "nome": "Obrigação de Fazer"}],
            movimentos=[{"codigo": 51, "nome": "Sentença", "dataHora": "2020-06-10T09:00:00Z"}],
        )

        precedent = process_to_precedent(proc)
        assert precedent.id.startswith("tjsp_")
        assert precedent.tribunal == "São Paulo"
        assert precedent.tese != ""
        assert len(precedent.fundamentos) > 0
        assert precedent.tipo == PrecedentType.ORDINARIO  # primeiro grau

    def test_process_to_legal_fact(self):
        """CT11: process_to_legal_fact() produz LegalFact válido."""
        from legal.datajud_client import DatajudProcess
        from legal.integration import process_to_legal_fact
        from legal import Competence

        proc = DatajudProcess(
            id="conv-002", tribunal="tjrj",
            numero_processo="0000001-12.2021.8.19.0001",
            classe={"codigo": 198, "nome": "Apelação Cível"},
        )

        fact = process_to_legal_fact(proc)
        assert fact.descricao != ""
        assert "Apelação" in fact.descricao
        assert fact.competencia == Competence.ESTADO

    def test_process_to_legal_argument(self):
        """CT12: process_to_legal_argument() produz LegalArgument válido."""
        from legal.datajud_client import DatajudProcess
        from legal.integration import process_to_legal_argument

        proc = DatajudProcess(
            id="conv-003", tribunal="tjmg",
            numero_processo="1000001-12.2020.8.13.0001",
            classe={"codigo": 7, "nome": "Procedimento Comum Cível"},
            assuntos=[{"codigo": 1234, "nome": "Contratos Bancários"}],
        )

        arg = process_to_legal_argument(proc)
        assert arg.id.startswith("tjmg_")
        assert arg.tese != ""
        assert arg.fundamento_normativo != ""
        assert len(arg.premissas) >= 1

    def test_process_to_precedent_segundo_grau(self):
        """CT13: Processo de segundo grau vira PRECEDENTE_INTERPRETATIVO."""
        from legal.datajud_client import DatajudProcess
        from legal.integration import process_to_precedent
        from legal import PrecedentType

        proc = DatajudProcess(
            id="conv-004", tribunal="tjrs",
            numero_processo="2000001-12.2021.8.21.0001",
            grau="segundo",
            classe={"codigo": 198, "nome": "Apelação Cível"},
            movimentos=[{"codigo": 131, "nome": "Acórdão", "dataHora": "2021-12-01T10:00:00Z"}],
        )

        precedent = process_to_precedent(proc)
        assert precedent.tipo == PrecedentType.PRECEDENTE_INTERPRETATIVO


# ═══════════════════════════════════════════════════════════════════════════
# 4. LegalDatajudIntegration — Pipeline completa
# ═══════════════════════════════════════════════════════════════════════════


class TestLegalDatajudIntegration:
    """Testes da integração completa Datajud → motores de raciocínio."""

    def test_load_processes_returns_list(self):
        """CT14: load_processes() carrega processos e alimenta motores."""
        from legal import LegalDatajudIntegration

        integration = LegalDatajudIntegration(offline=True)
        processos = integration.load_processes("tjsp")

        assert len(processos) > 0
        assert integration.get_stats()["processos_carregados"] > 0

    def test_load_processes_registers_precedents(self):
        """CT15: load_processes() registra precedentes no PrecedentAnalyzer."""
        from legal import LegalDatajudIntegration

        integration = LegalDatajudIntegration(offline=True)
        integration.load_processes("tjsp")

        assert integration.get_stats()["precedentes_registrados"] > 0

        # Verificar que o precedente está acessível
        precedentes = integration.precedents.precedents
        assert len(precedentes) > 0
        # Todos devem ter prefixo tjsp_
        assert all(k.startswith("tjsp_") for k in precedentes.keys())

    def test_analyze_process_runs_all_engines(self):
        """CT16: analyze_process() aplica pipeline completa de raciocínio."""
        from legal import LegalDatajudIntegration
        from legal.datajud_client import DatajudProcess

        integration = LegalDatajudIntegration(offline=True)

        proc = DatajudProcess(
            id="ana-001", tribunal="tjsp",
            numero_processo="1000001-12.2020.8.26.0001",
            classe={"codigo": 7, "nome": "Procedimento Comum Cível"},
            assuntos=[{"codigo": 1234, "nome": "Obrigação de Fazer / Não Fazer"}],
            movimentos=[{"codigo": 51, "nome": "Sentença", "dataHora": "2020-06-10T09:00:00Z"}],
        )

        resultado = integration.analyze_process(proc)

        assert "processo" in resultado
        assert "tribunal" in resultado
        assert "subsuncao" in resultado
        assert "precedente" in resultado
        assert "scoring" in resultado

    def test_analyze_process_scoring_valid(self):
        """CT17: analyze_process() retorna score 0-1."""
        from legal import LegalDatajudIntegration
        from legal.datajud_client import DatajudProcess

        integration = LegalDatajudIntegration(offline=True)

        proc = DatajudProcess(
            id="ana-002", tribunal="tjrj",
            numero_processo="0000001-12.2021.8.19.0001",
            classe={"codigo": 198, "nome": "Apelação Cível"},
            assuntos=[{"codigo": 7890, "nome": "Responsabilidade Civil do Estado"}],
            movimentos=[{"codigo": 131, "nome": "Acórdão", "dataHora": "2021-05-15T14:00:00Z"}],
        )

        resultado = integration.analyze_process(proc)
        score_total = resultado["scoring"]["score_total"]

        assert 0.0 <= score_total <= 1.0

    def test_offline_mode_works_without_api_key(self):
        """CT18: Modo offline funciona sem DATAJUD_API_KEY."""
        from legal import LegalDatajudIntegration

        # Remover variável de ambiente se presente
        old_key = os.environ.pop("DATAJUD_API_KEY", None)
        try:
            integration = LegalDatajudIntegration(offline=True)
            processos = integration.load_processes("tjsp")
            assert len(processos) > 0
        finally:
            if old_key:
                os.environ["DATAJUD_API_KEY"] = old_key

    def test_load_all_tribunals_mock(self):
        """CT19: load_all_tribunals() funciona em modo offline."""
        from legal import LegalDatajudIntegration

        integration = LegalDatajudIntegration(offline=True)
        resultados = integration.load_all_tribunals()

        assert isinstance(resultados, dict)
        # Deve ter pelo menos os tribunais com dados mock
        assert "tjsp" in resultados or "tjrj" in resultados

    def test_reset_stats(self):
        """CT20: reset_stats() zera contadores."""
        from legal import LegalDatajudIntegration

        integration = LegalDatajudIntegration(offline=True)
        integration.load_processes("tjsp")
        assert integration.get_stats()["processos_carregados"] > 0

        integration.reset_stats()
        assert integration.get_stats()["processos_carregados"] == 0
        assert integration.get_stats()["precedentes_registrados"] == 0

    def test_integration_syllogism_loaded(self):
        """CT21: O LegalSyllogism da integração tem normas registradas."""
        from legal import LegalDatajudIntegration

        integration = LegalDatajudIntegration(offline=True)
        integration.load_processes("tjsp", register_norms=True)

        assert len(integration.syllogism.norm_registry) > 0
        # As normas devem ter prefixo norm_tjsp
        assert any(k.startswith("norm_tjsp") for k in integration.syllogism.norm_registry)

    def test_datajud_client_reads_env_key(self):
        """CT22: DatajudClient lê DATAJUD_API_KEY do ambiente."""
        import os
        from legal import DatajudClient

        os.environ["DATAJUD_API_KEY"] = "test-key-123"
        try:
            client = DatajudClient(offline=True)
            # Em modo offline, a chave não é usada, mas deve ser lida
            assert client.api_key == "test-key-123"
        finally:
            os.environ.pop("DATAJUD_API_KEY", None)

    def test_tribunais_constant_completeness(self):
        """CT23: TRIBUNAIS contém todos os 27 estados + DF."""
        from legal import TRIBUNAIS

        assert len(TRIBUNAIS) == 27
        # Verificar alguns obrigatórios
        obrigatorios = {"tjac", "tjal", "tjam", "tjap", "tjba", "tjce", "tjdf",
                        "tjes", "tjgo", "tjma", "tjmg", "tjms", "tjmt", "tjpa",
                        "tjpb", "tjpe", "tjpi", "tjpr", "tjrj", "tjrn", "tjro",
                        "tjrr", "tjrs", "tjsc", "tjse", "tjsp", "tjto"}
        assert set(TRIBUNAIS.keys()) == obrigatorios
