# -*- coding: utf-8 -*-
"""
Testes Unitários para a SPEC-935-R446: Decisão Clínica por Grafos Bayesianos,
Teoria dos Jogos (Minimax Regret) e Ancoragem em Evidências Médicas Reais.
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from integrations.medical import (
    MedicalEvidence,
    ClinicalEvidenceLibrary,
    VERIFIED_MEDICAL_GUIDELINES,
    DiagnosticHypothesis,
    DiagnosticTest,
    DiagnosticDecisionGraph,
    ShannonEntropyEngine,
    ClinicalGameTheoryEngine,
    ClinicalAnamnesisGenerator,
    ClinicalSafetyVerifier,
    ClinicalInvestigationPipeline,
)


class TestR446ClinicalGameTheoryGraphs(unittest.TestCase):

    def setUp(self):
        self.orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    def test_spec_r446_registered(self):
        """SPEC-935-R446 deve estar registrada no SpecRegistry."""
        spec = spec_registry.get("SPEC-935-R446")
        self.assertIsNotNone(spec, "SPEC-935-R446 deve existir no SpecRegistry")
        self.assertEqual(spec.status, "green")

    def test_bayesian_decision_graph_probability_update(self):
        """Atualização Bayesiana por Razão de Verossimilhança deve calibrar probabilidades pós-teste."""
        h1 = DiagnosticHypothesis(name="SCA", prior_probability=0.20, severity_level="critica", critical_miss_penalty=9.0)
        h2 = DiagnosticHypothesis(name="Costocondrite", prior_probability=0.80, severity_level="baixa", critical_miss_penalty=1.0)
        graph = DiagnosticDecisionGraph([h1, h2])

        troponin_test = DiagnosticTest(
            name="Troponina Ultrassensível",
            target_condition="SCA",
            sensitivity=0.98,
            specificity=0.95,
            cost_score=2.0,
            invasiveness_score=1.0,
            turnaround_hours=1.0
        )

        # Teste Positivo: probabilidade de SCA deve subir expressivamente
        updated = graph.update_with_test_result(troponin_test, outcome_positive=True)
        self.assertGreater(updated["SCA"], 0.80, "Troponina positiva deve elevar probabilidade de SCA para > 80%")

    def test_shannon_entropy_and_information_gain(self):
        """Cálculo de Entropia de Shannon e Ganho de Informação propedêutico."""
        h1 = DiagnosticHypothesis(name="SCA", prior_probability=0.5, severity_level="alta", critical_miss_penalty=8.0)
        h2 = DiagnosticHypothesis(name="TEP", prior_probability=0.5, severity_level="alta", critical_miss_penalty=8.0)

        t1 = DiagnosticTest(name="ECG", target_condition="SCA", sensitivity=0.90, specificity=0.90, cost_score=1.0, invasiveness_score=0.0, turnaround_hours=0.2)
        ig = ShannonEntropyEngine.calculate_information_gain([h1, h2], t1)
        self.assertGreater(ig, 0.0, "Ganho de informação deve ser estritamente positivo")

    def test_minimax_regret_prevents_critical_miss(self):
        """Minimax Regret deve priorizar a exclusão de doença fatal mesmo com baixa probabilidade inicial."""
        h_grave = DiagnosticHypothesis(name="SCA", prior_probability=0.10, severity_level="critica", critical_miss_penalty=9.5)
        h_comum = DiagnosticHypothesis(name="Costocondrite", prior_probability=0.90, severity_level="baixa", critical_miss_penalty=1.0)

        t_grave = DiagnosticTest(name="ECG + Troponina", target_condition="SCA", sensitivity=0.98, specificity=0.90, cost_score=2.0, invasiveness_score=1.0, turnaround_hours=1.0)
        t_comum = DiagnosticTest(name="Palpação", target_condition="Costocondrite", sensitivity=0.80, specificity=0.70, cost_score=1.0, invasiveness_score=0.0, turnaround_hours=0.1)

        game = ClinicalGameTheoryEngine([h_grave, h_comum], [t_grave, t_comum])
        decision = game.compute_minimax_regret()

        self.assertEqual(decision["recommended_action"], "ECG + Troponina", "Minimax Regret deve escolher o exame que protege contra o pior cenário de omissão.")

    def test_clinical_anamnesis_generation(self):
        """Gerador de anamnese deve produzir frase clínica compacta e ordenar perguntas por relevância."""
        profile = {"age": 58, "sex": "Feminino", "comorbidities": ["Diabetes tipo 2", "Hipertensão"]}
        anamnese = self.orchestrator.generate_clinical_anamnesis(profile, "Dor torácica e sudorese", duration="3 horas", severity="alta")
        self.assertIn("Feminino", anamnese["problem_representation"])
        self.assertIn("58 anos", anamnese["problem_representation"])
        self.assertIn("Diabetes tipo 2", anamnese["problem_representation"])

    def test_z3_clinical_verifier_renal_and_allergy(self):
        """Verificador Z3 deve bloquear contraste iodado em eGFR < 30 e alergias documentadas."""
        verifier = ClinicalSafetyVerifier()

        # Paciente com insuficiência renal grave
        patient_bad_kidney = {"egfr": 22.0, "is_pregnant": False, "allergies": ["dipirona"]}
        action_angiotc = {"name": "Angiotomografia", "contraindication_tags": ["iodinated_contrast"]}

        check_renal = verifier.verify_contraindications(patient_bad_kidney, action_angiotc)
        self.assertFalse(check_renal["is_safe"], "Contraste iodado deve ser bloqueado em eGFR < 30")
        self.assertTrue(any("eGFR < 30" in v for v in check_renal["violations"]))

        # Paciente com alergia
        action_dipirona = {"name": "Dipirona 1g EV", "contraindication_tags": ["analgesico"]}
        check_allergy = verifier.verify_contraindications(patient_bad_kidney, action_dipirona)
        self.assertFalse(check_allergy["is_safe"], "Fármaco deve ser bloqueado para alergia conhecida")

    def test_real_medical_evidence_grounding(self):
        """Base de evidências deve conter diretrizes reais com DOIs, PMIDs e níveis GRADE."""
        lib = ClinicalEvidenceLibrary()
        evs = lib.find_evidence_by_topic("acute_coronary_syndrome")
        self.assertGreaterEqual(len(evs), 1)
        ev = evs[0]
        self.assertTrue(ev.doi.startswith("10."), "DOI deve ser válido")
        self.assertIsNotNone(ev.pmid, "PMID deve estar presente")
        self.assertIn("Level 1", ev.oxford_evidence_level)

    def test_orchestrator_investigate_clinical_case_e2e(self):
        """Orquestrador deve executar pipeline ponta a ponta e produzir saída estruturada no padrão Médico Virtual Supremo."""
        case_data = {
            "chief_complaint": "Dor torácica opressiva",
            "patient_profile": {"age": 62, "sex": "Masculino", "egfr": 85.0, "comorbidities": ["Hipertensão"]},
            "duration": "2 horas",
            "severity": "grave",
        }
        res = self.orchestrator.investigate_clinical_case(case_data, mode="professional_cds")
        root = res.get("resposta_medico_virtual_supremo", {})
        self.assertIn("meta", root)
        self.assertIn("safety", root)
        self.assertIn("clinical_summary", root)
        self.assertIn("assessment", root)
        self.assertIn("game_theory_decision", root)
        self.assertIn("plan_for_human_review", root)
        self.assertIn("evidence", root)
        self.assertIn("mandatory_footer", root)

    def test_doctor_reports_19_checks(self):
        """Doctor deve reportar 19 checks estruturais ativos incluindo clinical_game_theory_engine."""
        from marceloclaro import doctor
        doc_res = doctor.run_doctor()
        self.assertGreaterEqual(doc_res["checks_total"], 19, "Doctor deve ter 19 checks")
        check_names = [c["name"] for c in doc_res["checks"]]
        self.assertIn("clinical_game_theory_engine", check_names)


if __name__ == "__main__":
    unittest.main()
