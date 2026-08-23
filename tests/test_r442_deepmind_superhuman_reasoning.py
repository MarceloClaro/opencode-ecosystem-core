# -*- coding: utf-8 -*-
"""
Testes Unitários e de Integração para a SPEC-935-R442
======================================================
Validação TDD dos módulos de raciocínio científico Google DeepMind Superhuman:
- FormalProofVerifier (SymPy + Z3)
- AletheiaHypothesisEngine & AletheiaLatexFormatter
- IMOBenchmarkHarness & GradingHeadDeepMind
- Integração MarceloClaroOrchestrator e Doctor
"""

import unittest
from sdd.spec_engine import spec_registry, spec_verifier
from integrations.deepmind import (
    AletheiaHypothesisEngine,
    AletheiaLatexFormatter,
    FormalProofVerifier,
    IMOBenchmarkHarness,
    GradingHeadDeepMind,
    IMOProblem,
)
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from marceloclaro.doctor import _check_deepmind_superhuman_reasoning


class TestDeepMindSuperhumanReasoningR442(unittest.TestCase):

    def setUp(self):
        self.verifier = FormalProofVerifier()
        self.engine = AletheiaHypothesisEngine(verifier=self.verifier)
        self.harness = IMOBenchmarkHarness(verifier=self.verifier)
        self.orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    def test_spec_r442_registered(self):
        """Valida que a spec SPEC-935-R442 está presente no registro SDD."""
        spec = spec_registry.get("SPEC-935-R442")
        self.assertIsNotNone(spec, "SPEC-935-R442 deve estar registrada no SpecRegistry")

    def test_formal_verifier_algebraic_identity(self):
        """Valida a verificação simbólica de identidades e desigualdades."""
        # Identidade verdadeira: (a + b)^2 == a^2 + 2*a*b + b^2
        valid, msg = self.verifier.verify_algebraic_identity("(a + b)**2", "a**2 + 2*a*b + b**2")
        self.assertTrue(valid, f"Identidade deveria ser confirmada: {msg}")

        # Identidade falsa
        invalid, _ = self.verifier.verify_algebraic_identity("x + 1", "x + 2")
        self.assertFalse(invalid, "Expressões distintas não devem ser consideradas idênticas")

    def test_formal_verifier_logical_implication(self):
        """Valida o motor de implicação lógica."""
        premises = ["P_imply_Q", "P"]
        conclusion = "Q"
        valid, msg = self.verifier.verify_logical_implication(premises, conclusion)
        self.assertTrue(valid, f"Implicação lógica deve ser válida: {msg}")

    def test_formal_verifier_proof_steps(self):
        """Valida a verificação de passos encadeados de prova."""
        steps = [
            {"statement": "x**2 - 1 = (x - 1)*(x + 1)", "justification": "Fatoração de diferença de quadrados"},
            {"statement": "Para x > 1, (x-1) > 0 e (x+1) > 0", "justification": "Aritmética básica"},
        ]
        res = self.verifier.verify_proof_steps("Provar que x^2 - 1 > 0 para x > 1", steps)
        self.assertTrue(res.is_valid)
        self.assertGreaterEqual(res.confidence, 0.90)
        self.assertEqual(len(res.verified_steps), 2)

    def test_aletheia_decomposition(self):
        """Valida a decomposição de hipótese em lemas e passos pelo Aletheia."""
        claim = "A taxa de generalização de redes invariantes a simetrias decresce estritamente com O(1/sqrt(N))."
        decomp = self.engine.decompose(claim, domain="physics")

        self.assertEqual(decomp.domain, "physics")
        self.assertGreaterEqual(len(decomp.lemmas), 3)
        self.assertGreaterEqual(len(decomp.proof_steps), 3)
        self.assertIn("\\documentclass{article}", decomp.latex_document)
        self.assertIn("Theorem", decomp.latex_document)
        self.assertGreaterEqual(decomp.confidence_score, 0.85)

    def test_aletheia_latex_formatter(self):
        """Valida a estrutura do LaTeX gerado no padrão acadêmico do DeepMind."""
        decomp = self.engine.decompose("Teorema da Conservação de Entropia em Redes de Roteamento")
        doc = decomp.latex_document

        self.assertIn("\\newtheorem{theorem}{Theorem}", doc)
        self.assertIn("\\newtheorem{lemma}{Lemma}", doc)
        self.assertIn("\\begin{lemma}", doc)
        self.assertIn("\\begin{proof}", doc)
        self.assertIn("\\qed", doc)

    def test_imobench_problems_and_grading_head(self):
        """Valida o carregamento dos problemas do IMO Bench e a calibração do grading head (0 a 7)."""
        problems = self.harness.sample_dataset
        self.assertGreaterEqual(len(problems), 3)

        problem = problems[0]
        grading = GradingHeadDeepMind()

        # Resposta perfeita
        score_7, msg_7 = grading.grade(problem, "Pelo método da indução matemática e lema 1, a resposta exata é 3. Equação: N = 3.")
        self.assertEqual(score_7, 7)

        # Resposta com gap menor
        score_5, _ = grading.grade(problem, "A resposta final encontrada para o problema é 3.")
        self.assertEqual(score_5, 5)

        # Resposta vazia
        score_0, _ = grading.grade(problem, "")
        self.assertEqual(score_0, 0)

    def test_imobench_harness_execution(self):
        """Valida a execução completa da bateria de benchmark."""
        report = self.harness.run_benchmark(limit=3)
        self.assertEqual(report["total_problems"], 3)
        self.assertGreaterEqual(report["accuracy"], 0.6)
        self.assertGreaterEqual(report["average_grade_0_to_7"], 4.0)

    def test_orchestrator_deepmind_methods(self):
        """Valida os métodos integrados no MarceloClaroOrchestrator."""
        decomp = self.orchestrator.aletheia_decompose("Conjectura da Convergência Causal", domain="academic")
        self.assertIn("lemmas", decomp)
        self.assertIn("latex_document", decomp)

        proof = self.orchestrator.aletheia_prove("Invariância de Pareto em Jogos Conexos", domain="gametheory")
        self.assertIn("latex_document", proof)
        self.assertGreaterEqual(proof["confidence"], 0.8)

        eval_res = self.orchestrator.imobench_evaluate(limit=2)
        self.assertEqual(eval_res["total_problems"], 2)

        valid_ident, _ = self.orchestrator.formal_verify_identity("sin(x)**2 + cos(x)**2", "1")
        self.assertTrue(valid_ident)

    def test_doctor_deepmind_check(self):
        """Valida que o check do doctor para o DeepMind Superhuman passa sem erros."""
        check = _check_deepmind_superhuman_reasoning()
        self.assertEqual(check.status, "pass")
        self.assertIn("DeepMind Superhuman Reasoning ativo", check.detail)


if __name__ == "__main__":
    unittest.main()
