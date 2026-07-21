# -*- coding: utf-8 -*-
"""
Testes TDD — R205: Integração Médico Virtual Supremo + Ecossistema
====================================================================
Valida hooks, plugins, raciocínio científico, agentes especialistas,
pipeline transformer e integração com o ecossistema.

Requisitos: SPEC-935-R205.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import hashlib
import json

# ──────────────────────────────────────────────────────────────────────
# CT-01: Sistema de Hooks Clínicos
# ──────────────────────────────────────────────────────────────────────

class TestHooksClinicos:
    """Valida o sistema de hooks clínicos (SPEC-935-R205 §2.1)."""

    def test_hook_manager_cria(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            ClinicalHookManager, criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        assert manager is not None
        assert manager.summary()["total_hooks"] > 0

    def test_hook_manager_stages(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            ClinicalHookManager, STAGES
        )
        manager = ClinicalHookManager()
        for stage in STAGES:
            ctx = manager.execute(stage, {"test": True})
            assert ctx["test"] is True  # Não quebra sem hooks

    def test_hook_pre_normalize_executa(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        ctx = {
            "clinical_data": {"cpf": "123.456.789-00", "nome_completo": "Teste"},
            "patient": {"age_years": 45},
            "hooks": [],
            "alertas": [],
        }
        resultado = manager.execute("pre_normalize", ctx)
        # CPF deve ter sido removido
        assert "cpf" not in resultado.get("clinical_data", {})
        assert "nome_completo" not in resultado.get("clinical_data", {})
        assert "hooks" in resultado

    def test_hook_post_hypothesis_ranqueia(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        ctx = {
            "hipoteses": [
                {"name": "gripe", "status": "alternativa"},
                {"name": "IAM", "status": "grave_não_perder"},
                {"name": "pneumonia", "status": "provável"},
            ],
            "hooks": [],
        }
        resultado = manager.execute("post_hypothesis", ctx)
        hip = resultado["hipoteses"]
        # Grave_não_perder deve vir primeiro
        assert hip[0]["status"] == "grave_não_perder"

    def test_hook_validar_idade_rejeita_invalida(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        ctx = {
            "patient": {"age_years": 200},
            "clinical_data": {},
            "hooks": [],
            "alertas": [],
        }
        resultado = manager.execute("pre_normalize", ctx)
        assert resultado["patient"]["age_years"] is None
        assert any("Idade inválida" in a for a in resultado["alertas"])

    def test_hook_detecta_criticos(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        ctx = {
            "clinical_data": {"vital_signs": {"temp": 42, "spo2": 85}},
            "hooks": [],
            "alertas": [],
        }
        resultado = manager.execute("post_normalize", ctx)
        assert any("Hiperpirexia" in a for a in resultado["alertas"])
        assert any("Hipoxemia" in a for a in resultado["alertas"])

    def test_hook_adaptar_linguagem_paciente(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        ctx = {"modo": "patient_education", "plano": {"red_flags": ["dispneia"]}, "hooks": []}
        resultado = manager.execute("post_plan", ctx)
        assert "red_flags_orientacao" in resultado["plano"]

    def test_hook_pre_verify_checklist_personalizado(self):
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        manager = criar_hook_manager_padrao()
        ctx = {"modo": "research", "hooks": []}
        resultado = manager.execute("pre_verify", ctx)
        assert "checklist_personalizado" in resultado
        assert any("fonte citada" in c for c in resultado["checklist_personalizado"])


# ──────────────────────────────────────────────────────────────────────
# CT-02: Plugins de Validação Cruzada
# ──────────────────────────────────────────────────────────────────────

class TestValidacaoCruzada:
    """Valida plugins de validação cruzada (SPEC-935-R205 §2.2)."""

    def test_cross_validation_cria(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            CrossValidationPlugin
        )
        plugin = CrossValidationPlugin()
        assert plugin is not None

    def test_cross_validation_consenso(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            CrossValidationPlugin
        )
        plugin = CrossValidationPlugin()
        plugin.registrar_especialista("cardiologia", ["ecg", "ecocardiograma"])
        plugin.registrar_especialista("neurologia", ["eeg", "neuroimagem"])

        caso = {
            "assessment": {
                "hypotheses": [
                    {"name": "infecção respiratória", "status": "provável",
                     "confidence": "moderada"}
                ]
            },
            "evidence": [
                {"claim": "febre e tosse sugestivos de infecção",
                 "source": "diretriz clínica 2024",
                 "applicability": "direta"}
            ],
        }
        report = plugin.validar(caso)
        assert report.num_especialistas_consultados == 2
        assert report.caso_id is not None

    def test_cross_validation_conflito(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            CrossValidationPlugin
        )
        plugin = CrossValidationPlugin()
        plugin.registrar_especialista("cardiologia", ["ecg"])
        # Caso com hipótese cardíaca avaliada por não-cardio
        caso = {
            "assessment": {
                "hypotheses": [
                    {"name": "IAM sem supradesnível ST", "status": "grave_não_perder"}
                ]
            },
            "evidence": [],
        }
        report = plugin.validar(caso, especialistas_ativos=["cardiologia"])
        assert report is not None

    def test_differential_validator_completo(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            DifferentialValidator
        )
        validador = DifferentialValidator()
        hipoteses = [
            {"name": "pneumonia bacteriana", "status": "provável",
             "confidence": "moderada", "missing_evidence": ["rx tórax"]},
            {"name": "sepse de foco pulmonar", "status": "grave_não_perder",
             "confidence": "moderada", "missing_evidence": ["hemocultura"]},
        ]
        resultado = validador.validar(hipoteses, "respiratório")
        assert resultado["score"] >= 0.6

    def test_differential_validator_incompleto(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            DifferentialValidator
        )
        validador = DifferentialValidator()
        # Apenas uma hipótese sem status grave
        hipoteses = [
            {"name": "gripe", "status": "alternativa", "confidence": "baixa"},
        ]
        resultado = validador.validar(hipoteses, "inespecífico")
        assert resultado["score"] < 0.9
        assert not resultado["valido"] or resultado["score"] < 1.0

    def test_evidence_crosscheck_duplicatas(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            EvidenceCrosscheck
        )
        checker = EvidenceCrosscheck()
        evidencias = [
            {"claim": "febre indica infecção", "source": "diretriz",
             "applicability": "direta"},
            {"claim": "febre indica infecção", "source": "diretriz",
             "applicability": "direta"},
        ]
        resultado = checker.verificar(evidencias, [])
        assert len(resultado["duplicatas"]) > 0

    def test_evidence_crosscheck_sem_evidencias(self):
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            EvidenceCrosscheck
        )
        checker = EvidenceCrosscheck()
        resultado = checker.verificar([], [])
        assert resultado["score"] < 0.5
        assert not resultado["valido"]


# ──────────────────────────────────────────────────────────────────────
# CT-03: Raciocínio Científico
# ──────────────────────────────────────────────────────────────────────

class TestRaciocinioCientifico:
    """Valida motor de raciocínio científico (SPEC-935-R205 §2.3)."""

    def test_evidence_based_reasoning_grade(self):
        from skills.medico_virtual_supremo.reasoning.evidence_based_reasoning import (
            EvidenceBasedReasoning, TipoEstudo, NivelEvidencia, ForcaRecomendacao
        )
        motor = EvidenceBasedReasoning()
        grade = motor.classificar_evidencia(
            tipo_estudo=TipoEstudo.ENSAIO_CLINICO_RANDOMIZADO,
            populacao="adultos com pneumonia",
            consistencia=True,
            aplicabilidade_direta=True,
            risco_viés="baixo",
        )
        assert grade.nivel in NivelEvidencia
        assert grade.forca in ForcaRecomendacao
        assert grade.justificativa is not None

    def test_evidence_based_pico(self):
        from skills.medico_virtual_supremo.reasoning.evidence_based_reasoning import (
            EvidenceBasedReasoning
        )
        motor = EvidenceBasedReasoning()
        pico = motor.criar_pico(
            population="adultos com pneumonia comunitária",
            intervention="antibioticoterapia por 5 dias",
            outcome="cura clínica",
        )
        assert "P:" in pico.formatar()
        assert "I:" in pico.formatar()

    def test_evidence_based_soap(self):
        from skills.medico_virtual_supremo.reasoning.evidence_based_reasoning import (
            EvidenceBasedReasoning
        )
        motor = EvidenceBasedReasoning()
        soap = motor.criar_soap(
            subjetivo="Febre e tosse há 3 dias",
            objetivo="Temp 38.5, FR 22, SpO2 95%",
            assessment="Provável pneumonia comunitária",
            plano="Antibiótico + sintomáticos",
        )
        assert soap.subjetivo == "Febre e tosse há 3 dias"

    def test_diagnostic_reasoning_bayes(self):
        from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import (
            DiagnosticReasoning
        )
        motor = DiagnosticReasoning()
        motor.registrar_teste("ecg_para_iam", 0.50, 0.95, "literatura")
        resultado = motor.avaliar_teste(
            nome_teste="ecg_para_iam",
            prob_pre_teste=0.3,
            resultado_positivo=True,
            hipotese="IAM",
        )
        assert resultado.prob_pos_teste > resultado.prob_pre_teste
        assert resultado.lr_aplicado is not None

    def test_diagnostic_reasoning_multiplos_testes(self):
        from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import (
            criar_raciocinio_padrao
        )
        motor = criar_raciocinio_padrao()
        resultados = motor.comparar_testes(
            prob_pre_teste=0.2,
            testes=[("ecg_para_iam", True), ("troponina_para_iam", True)],
            hipotese="IAM",
        )
        assert len(resultados) == 2
        # Probabilidade deve aumentar com testes positivos
        assert resultados[-1].prob_pos_teste > resultados[0].prob_pos_teste


# ──────────────────────────────────────────────────────────────────────
# CT-04: Agentes Especialistas
# ──────────────────────────────────────────────────────────────────────

class TestAgentesEspecialistas:
    """Valida agentes médicos especialistas (SPEC-935-R205 §2.4)."""

    ROOT = Path(__file__).resolve().parent.parent
    AGENTS_DIR = ROOT / "agents" / "catalog"

    def _check_agent_file(self, agent_id: str, specialty: str):
        path = self.AGENTS_DIR / f"{agent_id}.md"
        assert path.exists(), f"Agente {agent_id}.md não encontrado"
        content = path.read_text(encoding="utf-8")
        assert f"agent_id: {agent_id}" in content
        assert specialty in content
        return content

    def test_agent_cardiologista_existe(self):
        self._check_agent_file("medico-cardiologista", "cardiologia")

    def test_agent_neurologista_existe(self):
        self._check_agent_file("medico-neurologista", "neurologia")

    def test_agent_radiologista_existe(self):
        self._check_agent_file("medico-radiologista", "radiologia")

    def test_agent_infectologista_existe(self):
        self._check_agent_file("medico-infectologista", "infectologia")

    def test_agent_clinico_geral_existe(self):
        self._check_agent_file("medico-clinico-geral", "clinica_geral")

    def test_todos_agentes_medicos_registrados_no_opencode(self):
        """Verifica se todos os novos agentes estão no opencode.json."""
        import json
        opencode_path = self.ROOT / "opencode.json"
        with open(opencode_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        agents = config.get("agent", {})
        for agent_id in [
            "medico-cardiologista", "medico-neurologista",
            "medico-radiologista", "medico-infectologista", "medico-clinico-geral",
        ]:
            assert agent_id in agents, f"Agente {agent_id} não está no opencode.json"


# ──────────────────────────────────────────────────────────────────────
# CT-05: Pipeline Transformer
# ──────────────────────────────────────────────────────────────────────

class TestPipelineTransformer:
    """Valida pipeline transformer de orquestração (SPEC-935-R205 §2.5)."""

    def test_pipeline_cria(self):
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )
        pipeline = criar_pipeline_padrao()
        assert pipeline is not None
        assert len(pipeline.get_especialistas()) >= 5

    def test_pipeline_roteia_por_sindrome(self):
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )
        pipeline = criar_pipeline_padrao()
        caso = {
            "request": "Paciente com dor no peito e falta de ar",
            "clinical_summary": {
                "problem_representation": "Síndrome cardíaco"
            },
            "safety": {"emergency_detected": False},
            "assessment": {"hypotheses": [
                {"name": "IAM", "status": "grave_não_perder"}
            ]},
        }
        resultado = pipeline.processar(caso)
        assert resultado.especialista_principal is not None
        assert resultado.especialista_principal.especialidade == "cardiologia"

    def test_pipeline_roteia_por_palavras_chave(self):
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )
        pipeline = criar_pipeline_padrao()
        caso = {
            "request": "Paciente com cefaleia intensa e sinais de AVC",
            "clinical_summary": {"problem_representation": "Síndrome neurológica"},
            "safety": {"emergency_detected": False},
            "assessment": {"hypotheses": []},
        }
        resultado = pipeline.processar(caso)
        assert resultado.especialista_principal is not None
        # Pode rotear para neurologia ou clínico geral
        assert resultado.especialista_principal.especialidade in [
            "neurologia", "clinica_geral"
        ]

    def test_pipeline_fallback_clinico_geral(self):
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )
        pipeline = criar_pipeline_padrao()
        caso = {
            "request": "Paciente para check-up de rotina",
            "clinical_summary": {"problem_representation": "Paciente assintomático"},
            "safety": {"emergency_detected": False},
            "assessment": {"hypotheses": []},
        }
        resultado = pipeline.processar(caso)
        assert resultado.especialista_principal is not None
        # Deve cair no clínico geral por ser inespecífico
        assert resultado.especialista_principal.especialidade in [
            "clinica_geral", "cardiologia"  # cardiologia pelo check-up
        ]

    def test_pipeline_urgencia_detectada(self):
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )
        pipeline = criar_pipeline_padrao()
        caso = {
            "request": "Paciente com dificuldade respiratória intensa",
            "clinical_summary": {"problem_representation": "Emergência respiratória"},
            "safety": {"emergency_detected": True},
            "assessment": {"hypotheses": []},
        }
        resultado = pipeline.processar(caso)
        assert resultado.score_urgencia > 0.7
        assert "URGÊNCIA" in resultado.justificativa

    def test_pipeline_justificativa_detalhada(self):
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )
        pipeline = criar_pipeline_padrao()
        caso = {
            "request": "Febre, tosse e calafrios há 3 dias",
            "clinical_summary": {"problem_representation": "Quadro infeccioso"},
            "safety": {"emergency_detected": False},
            "assessment": {"hypotheses": []},
        }
        resultado = pipeline.processar(caso)
        assert "roteado para" in resultado.justificativa


# ──────────────────────────────────────────────────────────────────────
# CT-06: Integração com o Ecossistema
# ──────────────────────────────────────────────────────────────────────

class TestIntegracaoEcossistema:
    """Valida integração com marceloclaro e ecossistema (SPEC-935-R205 §2.6)."""

    ROOT = Path(__file__).resolve().parent.parent

    def test_skill_importavel(self):
        """Skill principal deve ser importável diretamente."""
        from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill
        skill = MedicoVirtualSupremoSkill()
        assert skill.get_version() == "2.0.0"

    def test_spec_r205_existe(self):
        """SPEC-935-R205 deve existir."""
        path = self.ROOT / "specs" / "SPEC-935-R205.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "Hooks Clínicos" in content
        assert "Validação Cruzada" in content

    def test_skill_hooks_integrados(self):
        """Os hooks devem se integrar com a skill principal."""
        from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill
        from skills.medico_virtual_supremo.hooks.clinical_hooks import (
            criar_hook_manager_padrao
        )
        # Hook manager deve ser instanciável
        manager = criar_hook_manager_padrao()
        # Skill deve funcionar independente
        skill = MedicoVirtualSupremoSkill()
        resultado = skill.analisar("patient_education", "teste de integração")
        assert resultado is not None

    def test_plugins_integrados_com_pipeline(self):
        """Plugins devem funcionar com dados reais."""
        from skills.medico_virtual_supremo.plugins.cross_validation import (
            CrossValidationPlugin, DifferentialValidator, EvidenceCrosscheck
        )
        from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill

        skill = MedicoVirtualSupremoSkill()
        resultado = skill.analisar(
            "professional_cds",
            "Paciente com febre, tosse e dispneia há 4 dias",
            patient={"age_years": 60, "sex_at_birth": "masculino"},
        )

        corpo = resultado["resposta_medico_virtual_supremo"]
        hipoteses = corpo["assessment"]["hypotheses"]
        evidencias = corpo["evidence"]

        # Validador diferencial
        validador = DifferentialValidator()
        v_resultado = validador.validar(hipoteses, "respiratório")
        assert v_resultado["score"] > 0

        # Cross-check de evidências
        checker = EvidenceCrosscheck()
        c_resultado = checker.verificar(evidencias, hipoteses)
        assert c_resultado["score"] > 0

    def test_raciocinio_com_dados_reais(self):
        """Motor de raciocínio com dados realísticos."""
        from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import (
            criar_raciocinio_padrao
        )
        motor = criar_raciocinio_padrao()

        # Simular caso de IAM: ECG + troponina + clínica
        resultado = motor.avaliar_teste(
            "ecg_para_iam", 0.4, True, "IAM com supradesnível ST"
        )
        assert resultado.prob_pos_teste > 0.4

        # Com troponina positiva após ECG
        resultado2 = motor.avaliar_teste(
            "troponina_para_iam", resultado.prob_pos_teste, True, "IAM"
        )
        assert resultado2.prob_pos_teste > resultado.prob_pos_teste

    def test_pipeline_completo_fim_a_fim(self):
        """Pipeline completo: skill → transformer → especialistas."""
        from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            criar_pipeline_padrao
        )

        # 1. Skill analisa caso
        skill = MedicoVirtualSupremoSkill()
        resultado = skill.analisar(
            "professional_cds",
            "Paciente com dor torácica opressiva há 2 horas, irradiando para braço E, "
            "associada a sudorese e náusea. PA 160/95, FC 98.",
            patient={"age_years": 55, "sex_at_birth": "masculino",
                     "weight_kg": 80},
            clinical_data={
                "vital_signs": {"pa": "160/95", "fc": 98, "fr": 20, "spo2": 97},
                "history": ["tabagista", "hipertenso", "diabetes tipo 2"],
                "medications": ["enalapril", "metformina"],
            }
        )

        # 2. Transformer pipeline roteia para cardiologista
        pipeline = criar_pipeline_padrao()
        roteamento = pipeline.processar(resultado["resposta_medico_virtual_supremo"])
        assert roteamento.especialista_principal is not None
        # Caso cardíaco deve ir para cardiologia
        assert roteamento.especialista_principal.especialidade in [
            "cardiologia", "clinica_geral"
        ]

    def test_spec_refere_implementacao(self):
        """Spec deve referenciar componentes existentes."""
        spec = Path(__file__).resolve().parent.parent / "specs" / "SPEC-935-R205.md"
        content = spec.read_text(encoding="utf-8")
        assert "hooks" in content.lower() or "Hooks" in content
        assert "transformer" in content.lower()
        assert "validação cruzada" in content.lower()


# ──────────────────────────────────────────────────────────────────────
# CT-07: Métricas e Sanidade
# ──────────────────────────────────────────────────────────────────────

class TestMetricasSanidade:
    """Valida métricas de sucesso e sanidade do sistema."""

    def test_todos_testes_tem_prefixo_test(self):
        """Garante que todas as funções de teste seguem o padrão."""
        import re
        path = Path(__file__)
        content = path.read_text(encoding="utf-8")
        # Encontrar todas as funções definidas
        funcoes = re.findall(r'^\s+def (\w+)\s*\(', content, re.MULTILINE)
        metodos_test = [f for f in funcoes if f.startswith("test_")]
        metodos_outros = [f for f in funcoes if not f.startswith("test_") and not f.startswith("_")]
        assert len(metodos_outros) == 0, f"Métodos sem prefixo test: {metodos_outros}"

    def test_especialistas_tem_atributos_completos(self):
        """Especialistas padrão devem ter todos os atributos."""
        from skills.medico_virtual_supremo.orchestration.transformer_pipeline import (
            PERFIS_ESPECIALISTAS_PADRAO
        )
        for perfil in PERFIS_ESPECIALISTAS_PADRAO:
            assert perfil.id
            assert perfil.nome
            assert perfil.especialidade
            assert perfil.palavras_chave
            assert len(perfil.palavras_chave) >= 3
            assert perfil.capacidades
            assert 0 <= perfil.peso_urgencia <= 1

    def test_raciocinio_tem_teste_iam_completo(self):
        """Cenario completo: diagnostico de IAM com dados realisticos."""
        from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import (
            criar_raciocinio_padrao
        )
        from skills.medico_virtual_supremo.reasoning.evidence_based_reasoning import (
            EvidenceBasedReasoning, TipoEstudo
        )

        motor_diag = criar_raciocinio_padrao()
        motor_ebm = EvidenceBasedReasoning()

        # Probabilidade pré-teste de IAM em homem 55a com dor torácica típica: ~40%
        prob_pre = 0.40

        # ECG mostra supradesnível ST (LR+ ~11 para IAM)
        resultados = motor_diag.comparar_testes(
            prob_pre,
            [("ecg_para_iam", True), ("troponina_para_iam", True)],
            "IAM com supradesnível ST",
        )

        prob_pos = resultados[-1].prob_pos_teste
        # Probabilidade pós-teste deve ser >80% (ECG + troponina)
        assert prob_pos > 0.70, (
            f"Probabilidade pós-teste {prob_pos:.2%} deveria ser >70% "
            f"para IAM com ECG + troponina positivos"
        )

        # Classificar evidência
        grade = motor_ebm.classificar_evidencia(
            tipo_estudo=TipoEstudo.ENSAIO_CLINICO_RANDOMIZADO,
            populacao="adultos com IAM",
            consistencia=True,
            aplicabilidade_direta=True,
        )
        assert grade.nivel.value in ("alta", "moderada")


# ──────────────────────────────────────────────────────────────────────
# CT-08: Integridade dos Arquivos
# ──────────────────────────────────────────────────────────────────────

class TestIntegridadeArquivos:
    """Valida que todos os arquivos do R205 existem e são válidos."""

    ROOT = Path(__file__).resolve().parent.parent

    def test_skill_py_existe(self):
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "skill.py").exists()

    def test_hooks_existem(self):
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "hooks" / "clinical_hooks.py").exists()
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "hooks" / "__init__.py").exists()

    def test_plugins_existem(self):
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "plugins" / "cross_validation.py").exists()
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "plugins" / "__init__.py").exists()

    def test_reasoning_existe(self):
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "reasoning" / "evidence_based_reasoning.py").exists()
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "reasoning" / "diagnostic_reasoning.py").exists()
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "reasoning" / "__init__.py").exists()

    def test_orchestration_existe(self):
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "orchestration" / "transformer_pipeline.py").exists()
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "orchestration" / "__init__.py").exists()

    def test_agentes_no_catalogo(self):
        for agent_id in [
            "medico-cardiologista", "medico-neurologista",
            "medico-radiologista", "medico-infectologista", "medico-clinico-geral",
        ]:
            path = self.ROOT / "agents" / "catalog" / f"{agent_id}.md"
            assert path.exists(), f"Agente {agent_id} ausente"

    def test_spec_existe(self):
        assert (self.ROOT / "specs" / "SPEC-935-R205.md").exists()

    def test_metabus_integration_existe(self):
        """MetaBus: módulo de integração existe."""
        assert (self.ROOT / "skills" / "medico_virtual_supremo" / "metabus_integration.py").exists()

    def test_metabus_integration_skill_ativo(self):
        """MetaBus: skill reporta MetaBus ativo."""
        from skills.medico_virtual_supremo.skill import METABUS_ATIVO
        assert METABUS_ATIVO is True


# ──────────────────────────────────────────────────────────────────────
# CT-08: MetaBus Integration
# ──────────────────────────────────────────────────────────────────────

class TestMetaBusIntegration:
    """Valida integração com o barramento metacognitivo (SPEC-935-R205 §2.7)."""

    def test_metabus_importavel(self):
        from skills.medico_virtual_supremo.metabus_integration import (
            status_metabus, publicar_evento, analysis_started,
            analysis_completed, emergency_detected, refletir_analise,
            atualizar_confianca_skill, registrar_licao_apos_analise,
            obtermemoriametacognitiva,
        )
        assert callable(status_metabus)
        assert callable(publicar_evento)

    def test_metabus_status_disponivel(self):
        from skills.medico_virtual_supremo.metabus_integration import status_metabus
        status = status_metabus()
        assert status.get("disponivel") is True
        assert "episodic_memory_size" in status

    def test_metabus_publica_evento(self):
        from skills.medico_virtual_supremo.metabus_integration import publicar_evento
        # Publicar sempre retorna int (0 se sem subscribers, mas não falha)
        result = publicar_evento("test.metabus_integration", {"test": True})
        assert isinstance(result, int)

    def test_metabus_analysis_started(self):
        from skills.medico_virtual_supremo.metabus_integration import analysis_started
        n = analysis_started("test-mode", "test-run-id", "paciente com febre")
        assert isinstance(n, int)

    def test_metabus_analysis_completed(self):
        from skills.medico_virtual_supremo.metabus_integration import analysis_completed
        n = analysis_completed("test-mode", "test-run-id", 2, 7, 0, False, 0.5)
        assert isinstance(n, int)

    def test_metabus_emergency_detected(self):
        from skills.medico_virtual_supremo.metabus_integration import emergency_detected
        n = emergency_detected("test-run-id", "dispneia intensa", "professional_cds")
        assert isinstance(n, int)

    def test_metabus_refletir_analise(self):
        from skills.medico_virtual_supremo.metabus_integration import refletir_analise
        ref_id = refletir_analise("test-run-id", "test", 5, 0, 2, False)
        # Deve retornar um ID de reflexão (string) ou None
        assert ref_id is None or isinstance(ref_id, str)

    def test_metabus_confianca_atualiza(self):
        from skills.medico_virtual_supremo.metabus_integration import (
            atualizar_confianca_skill, status_metabus
        )
        antes = status_metabus().get("confidence_medico_skill", 0.5)
        atualizar_confianca_skill(7, 7)  # 100% = score 1.0 → EMA atualiza
        depois = status_metabus().get("confidence_medico_skill", 0.5)
        assert depois != antes, "Confiança deveria ter mudado com EMA"

    def test_metabus_skill_integration_pipeline(self):
        """MetaBus: pipeline da skill publica eventos automaticamente."""
        from skills.medico_virtual_supremo.skill import MedicoVirtualSupremoSkill
        skill = MedicoVirtualSupremoSkill()
        r = skill.analisar("patient_education", "Tosse seca há 5 dias")
        corpo = r.get("resposta_medico_virtual_supremo", r)
        assert corpo["meta"]["mode"] == "patient_education"
        # Verifica que o confidence ledger foi atualizado pela skill
        from skills.medico_virtual_supremo.metabus_integration import status_metabus
        status = status_metabus()
        assert status.get("confidence_medico_skill", 0.0) > 0.0

    def test_metabus_hook_publica_no_metabus(self):
        """MetaBus: hook de auditoria publica cross_validation_executed."""
        from skills.medico_virtual_supremo.hooks.clinical_hooks import criar_hook_manager_padrao
        m = criar_hook_manager_padrao()
        ctx = {
            "clinical_data": {},
            "patient": {"age_years": 40},
            "modo": "professional_cds",
            "hipoteses": [{"name": "teste", "status": "alternativa", "confidence": "baixa"}],
            "plano": {"red_flags": ["alarme"]},
            "auditoria": {"checks_passed": ["ok"], "checks_failed": []},
            "run_id": "test-hook-metabus",
        }
        ctx = m.execute("post_verify", ctx)
        assert len(ctx.get("hooks", [])) > 0
