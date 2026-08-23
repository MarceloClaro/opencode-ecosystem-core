# -*- coding: utf-8 -*-
"""
Ponte e Pipeline Orquestrado de Investigação Clínica
===================================================
Une Anamnese Guiada, Grafos Bayesianos, Teoria dos Jogos (Minimax Regret),
Verificação de Segurança Z3 e Ancoragem em Evidências Reais em um fluxo unificado.
Gera saída estruturada conforme o padrão da Skill Médico Virtual Supremo.
"""

import json
import time
from typing import Any, Dict, List, Optional
import uuid

from integrations.medical.evidence_grounding import ClinicalEvidenceLibrary, VERIFIED_MEDICAL_GUIDELINES
from integrations.medical.clinical_game_theory import (
    DiagnosticHypothesis,
    DiagnosticTest,
    DiagnosticDecisionGraph,
    ShannonEntropyEngine,
    ClinicalGameTheoryEngine,
    ClinicalAnamnesisGenerator,
)
from integrations.medical.clinical_verifier import ClinicalSafetyVerifier


class ClinicalInvestigationPipeline:
    """Pipeline completo de decisão clínica por grafos e teoria dos jogos."""

    def __init__(self) -> None:
        self.evidence_lib = ClinicalEvidenceLibrary()
        self.verifier = ClinicalSafetyVerifier()

    def investigate(self, case_data: Dict[str, Any], mode: str = "professional_cds") -> Dict[str, Any]:
        """
        Executa a investigação completa:
        1. Validação de Escopo & Gatilhos de Emergência
        2. Normalização e Frase Clínica Compacta
        3. Construção do Grafo de Hipóteses e Testes
        4. Otimização por Teoria dos Jogos (Minimax Regret) & Ganho de Informação
        5. Verificação de Segurança Z3
        6. Ancoragem em Literatura Médica Real com DOI e GRADE
        7. Geração de YAML resposta_medico_virtual_supremo
        """
        start_time = time.time()
        patient_profile = case_data.get("patient_profile", {})
        chief_complaint = case_data.get("chief_complaint", "Sintomas clínicos em avaliação")
        duration = case_data.get("duration", "Início recente")
        severity = case_data.get("severity", "moderada")

        # 1. Gatilhos de Emergência
        emergency_check = self.verifier.check_immediate_red_flags(case_data)

        # 2. Representação do Problema (Frase Clínica)
        prob_representation = ClinicalAnamnesisGenerator.generate_problem_representation(
            patient_profile, chief_complaint, duration, severity
        )

        # 3. Extração / Mapeamento de Hipóteses e Testes
        raw_hypotheses = case_data.get("hypotheses", [])
        hypotheses_objs: List[DiagnosticHypothesis] = []

        if raw_hypotheses:
            for h in raw_hypotheses:
                hypotheses_objs.append(DiagnosticHypothesis(
                    name=h.get("name", "Condição Clínica"),
                    prior_probability=float(h.get("prior_probability", 0.2)),
                    severity_level=h.get("severity_level", "moderada"),
                    critical_miss_penalty=float(h.get("critical_miss_penalty", 5.0)),
                    status=h.get("status", "provavel"),
                    supporting_findings=h.get("supporting_findings", []),
                    opposing_findings=h.get("opposing_findings", []),
                    confidence_rationale=h.get("confidence_rationale", "Baseado em apresentação clínica inicial.")
                ))
        else:
            # Hipóteses default para cenários cardiovasculares / gerais comuns
            hypotheses_objs = [
                DiagnosticHypothesis(
                    name="Síndrome Coronariana Aguda (SCA)",
                    prior_probability=0.15,
                    severity_level="critica",
                    critical_miss_penalty=9.5,
                    status="grave_nao_perder",
                    supporting_findings=["Dor torácica", "Fatores de risco cardiovascular"],
                    confidence_rationale="Hipótese crítica com risco de óbito precoce."
                ),
                DiagnosticHypothesis(
                    name="Tromboembolismo Pulmonar (TEP)",
                    prior_probability=0.10,
                    severity_level="critica",
                    critical_miss_penalty=9.0,
                    status="grave_nao_perder",
                    supporting_findings=["Dispneia associada"],
                    confidence_rationale="Exige exclusão por Escore de Wells / D-Dímero."
                ),
                DiagnosticHypothesis(
                    name="Dor Torácica Musculoesquelética / Costocondrite",
                    prior_probability=0.75,
                    severity_level="baixa",
                    critical_miss_penalty=1.0,
                    status="provavel",
                    supporting_findings=["Dor aos movimentos"],
                    confidence_rationale="Alta prevalência na atenção primária."
                )
            ]

        # 4. Grafo de Decisão e Exames Disponíveis
        raw_tests = case_data.get("available_tests", [])
        test_objs: List[DiagnosticTest] = []

        if raw_tests:
            for t in raw_tests:
                test_objs.append(DiagnosticTest(
                    name=t.get("name", "Exame"),
                    target_condition=t.get("target_condition", "Geral"),
                    sensitivity=float(t.get("sensitivity", 0.9)),
                    specificity=float(t.get("specificity", 0.9)),
                    cost_score=float(t.get("cost_score", 3.0)),
                    invasiveness_score=float(t.get("invasiveness_score", 1.0)),
                    turnaround_hours=float(t.get("turnaround_hours", 2.0)),
                    contraindications=t.get("contraindications", [])
                ))
        else:
            test_objs = [
                DiagnosticTest(
                    name="ECG de 12 Derivações + Troponina Ultrassensível Seriada",
                    target_condition="Síndrome Coronariana Aguda (SCA)",
                    sensitivity=0.98,
                    specificity=0.92,
                    cost_score=2.0,
                    invasiveness_score=1.0,
                    turnaround_hours=1.0,
                    contraindications=[]
                ),
                DiagnosticTest(
                    name="Escore de Wells + D-Dímero de Alta Sensibilidade",
                    target_condition="Tromboembolismo Pulmonar (TEP)",
                    sensitivity=0.96,
                    specificity=0.60,
                    cost_score=3.0,
                    invasiveness_score=1.0,
                    turnaround_hours=1.5,
                    contraindications=[]
                ),
                DiagnosticTest(
                    name="Angiotomografia de Tórax para Artérias Pulmonares",
                    target_condition="Tromboembolismo Pulmonar (TEP)",
                    sensitivity=0.99,
                    specificity=0.98,
                    cost_score=7.0,
                    invasiveness_score=4.0,
                    turnaround_hours=3.0,
                    contraindications=["iodinated_contrast"]
                ),
                DiagnosticTest(
                    name="Palpação Torácica Focal e Teste de Mobilidade",
                    target_condition="Dor Torácica Musculoesquelética / Costocondrite",
                    sensitivity=0.85,
                    specificity=0.80,
                    cost_score=1.0,
                    invasiveness_score=0.0,
                    turnaround_hours=0.1,
                    contraindications=[]
                )
            ]

        # 5. Otimização por Teoria dos Jogos (Minimax Regret)
        game_engine = ClinicalGameTheoryEngine(hypotheses_objs, test_objs)
        minimax_strategy = game_engine.compute_minimax_regret()

        # 6. Cálculo de Ganho de Informação de Shannon para cada exame
        info_gains = {}
        for t in test_objs:
            ig = ShannonEntropyEngine.calculate_information_gain(hypotheses_objs, t)
            info_gains[t.name] = round(ig, 4)

        # 7. Verificação de Segurança Z3 nas Ações Recomendadas
        best_test_details = minimax_strategy.get("best_test_details") or {}
        safety_validation = self.verifier.verify_contraindications(patient_profile, best_test_details)

        # 8. Ancoragem em Literatura Médica Real
        grounded_evidences = []
        for h in hypotheses_objs:
            evs = self.evidence_lib.find_evidence_by_topic(h.name)
            for ev in evs:
                grounded_evidences.append(ev.to_dict())

        if not grounded_evidences:
            grounded_evidences = self.evidence_lib.search_grounded_evidence(chief_complaint)

        # 9. Montagem da Saída no Padrão Médico Virtual Supremo (YAML)
        response_data = {
            "resposta_medico_virtual_supremo": {
                "meta": {
                    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "language": "pt-BR",
                    "mode": mode,
                    "response_gen_id": "05272024-resposta-medico-virtual-supremo",
                    "run_id": str(uuid.uuid4()),
                    "skill_version": "2.0.0",
                    "game_theory_strategy": minimax_strategy.get("game_type"),
                },
                "safety": {
                    "emergency_detected": emergency_check["is_emergency"],
                    "escalation_required": emergency_check["is_emergency"],
                    "emergency_details": emergency_check["triggers_found"],
                    "intended_user": "profissional de saúde (Supervisão Obrigatória)" if mode == "professional_cds" else "paciente (Informativo)",
                    "limitations": [
                        "Não substitui consulta médica presencial nem exame físico direto",
                        "Prescrição e dosagem requerem avaliação clínica e assinatura profissional",
                        "Decisão baseada em otimização Minimax Regret e probabilidade bayesiana"
                    ]
                },
                "clinical_summary": {
                    "problem_representation": prob_representation,
                    "chief_complaint": chief_complaint,
                    "severity": severity,
                },
                "assessment": {
                    "hypotheses": [h.to_dict() for h in hypotheses_objs],
                    "information_gain_ranking": sorted(info_gains.items(), key=lambda x: x[1], reverse=True),
                },
                "game_theory_decision": {
                    "minimax_recommended_test": minimax_strategy.get("recommended_action"),
                    "max_regret_scores": minimax_strategy.get("max_regrets"),
                    "safety_validation": safety_validation,
                },
                "plan_for_human_review": {
                    "immediate_actions": [
                        emergency_check["recommended_action"]
                    ] if emergency_check["is_emergency"] else [
                        f"Solicitar prioritariamente: {minimax_strategy.get('recommended_action')} (Maior redução de risco e arrependimento)",
                        "Monitorar estabilidade de sinais vitais e padrão da queixa"
                    ],
                    "tests_to_consider": [
                        {"name": t.name, "information_gain": info_gains.get(t.name, 0.0), "target": t.target_condition}
                        for t in test_objs
                    ],
                    "red_flags": [
                        "Dor torácica de início súbito com irradiação para mandíbula ou dorso",
                        "Síncope, hipotensão arterial ou saturação de O2 < 90%",
                        "Instabilidade hemodinâmica ou dispneia em repouso"
                    ],
                    "treatment_options_to_validate": [
                        "Conduta terapêutica estratificada conforme resultado da troponina seriada e ECG",
                        "Evitar AINEs se houver risco hemorrágico ou disfunção renal associada"
                    ]
                },
                "evidence": grounded_evidences,
                "audit": {
                    "z3_logical_checks": safety_validation.get("z3_formal_status"),
                    "checks_passed": safety_validation.get("checks_passed"),
                    "human_review_required": True,
                },
                "mandatory_footer": {
                    "tool": "Médico Virtual Supremo v2.0 — Apoio Clínico Auditável",
                    "disclaimer": "Esta é uma ferramenta de apoio à decisão médica. Não substitui avaliação profissional.",
                    "author": "Marcelo Claro",
                    "instagram": "https://www.instagram.com/marceloclaro.geomaker/"
                }
            }
        }

        return response_data
