# -*- coding: utf-8 -*-
"""
Testes Unitários e de Integração para a SPEC-935-R445
======================================================
Validação TDD dos motores:
- OpenCodeAlphaGeometry (Base Dedutiva + Método de Wu + TikZ/SVG)
- AutoFormalizerEngine (Informal -> Lean 4, Lean 4 -> Informal)
- Validação Cruzada Tripla (Cross-Validation)
- Integração MarceloClaroOrchestrator e Doctor Check 18
"""

import unittest
from sdd.spec_engine import spec_registry
from integrations.deepmind import (
    GeometricDeductiveDatabase,
    WuGeometryProver,
    TikzGeometryRenderer,
    OpenCodeAlphaGeometry,
    GeometricProofResult,
    AutoFormalizerEngine,
    CrossValidationResult,
)
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from marceloclaro.doctor import _check_geometry_autoformalization_engine, run_doctor


class TestAlphaGeometryAutoformalizationR445(unittest.TestCase):

    def setUp(self):
        self.geom_engine = OpenCodeAlphaGeometry()
        self.autoform_engine = AutoFormalizerEngine()
        self.orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)

    def test_spec_r445_registered(self):
        """Valida que SPEC-935-R445 está registrada no SpecRegistry."""
        spec = spec_registry.get("SPEC-935-R445")
        self.assertIsNotNone(spec, "SPEC-935-R445 deve estar registrada no SpecRegistry")

    def test_geometry_deductive_database(self):
        """Valida a dedução lógica do Teorema da Base Média."""
        dd = GeometricDeductiveDatabase()
        dd.add_point("A", 0, 3)
        dd.add_point("B", -2, 0)
        dd.add_point("C", 4, 0)
        dd.add_fact("midpoint(m, a, b)")
        dd.add_fact("midpoint(n, a, c)")
        steps = dd.deduce()

        self.assertTrue(dd.query("parallel(mn, bc)"))
        self.assertGreater(len(steps), 0)

    def test_wu_method_midpoint_polynomial_reduction(self):
        """Valida a anulação do resíduo polinomial no Teorema da Base Média pelo Método de Wu."""
        wu = WuGeometryProver()
        proven, residue, steps = wu.prove_midpoint_parallelism()
        self.assertTrue(proven)
        self.assertEqual(residue, "0")
        self.assertGreater(len(steps), 0)

    def test_wu_method_pythagorean_reduction(self):
        """Valida a redução algébrica do Teorema de Pitágoras."""
        wu = WuGeometryProver()
        proven, residue, steps = wu.prove_pythagorean_theorem()
        self.assertTrue(proven)
        self.assertEqual(residue, "0")

    def test_tikz_and_svg_renderer(self):
        """Valida a geração de código TikZ e SVG vetorial."""
        renderer = TikzGeometryRenderer()
        tikz = renderer.render_triangle_midpoint_tikz()
        svg = renderer.render_triangle_midpoint_svg()

        self.assertIn(r"\begin{tikzpicture}", tikz)
        self.assertIn(r"\coordinate (A)", tikz)
        self.assertIn("<svg", svg)
        self.assertIn("polygon", svg)

    def test_opencode_alphageometry_solve(self):
        """Valida o solucionador integrado AlphaGeometry."""
        res_mid = self.geom_engine.solve("midpoint_theorem")
        self.assertTrue(res_mid.is_proven)
        self.assertEqual(res_mid.polynomial_residue, "0")
        self.assertIn(r"\begin{tikzpicture}", res_mid.tikz_code)

        res_pyt = self.geom_engine.solve("pythagoras")
        self.assertTrue(res_pyt.is_proven)

    def test_autoformalizer_informal_to_lean4(self):
        """Valida a tradução de enunciado informal para código formal Lean 4."""
        informal = "Para qualquer número real x e y, (x + y) * (x - y) = x^2 - y^2"
        res = self.autoform_engine.informal_to_lean4(informal, domain="algebra", theorem_name="diff_sq")

        self.assertIn("theorem diff_sq", res["lean_code"])
        self.assertIn("import Mathlib.Tactic", res["lean_code"])
        self.assertTrue(res["is_valid_syntax"])

    def test_autoformalizer_lean4_to_informal(self):
        """Valida a decompilação explicativa de código Lean 4 para português formal."""
        lean_code = """
import Mathlib.Tactic

theorem sample_sum (x : Real) : x + 0 = x := by
  intro x
  ring
"""
        res = self.autoform_engine.lean4_to_informal(lean_code, language="pt-br")
        self.assertEqual(res["theorem_name"], "sample_sum")
        self.assertIn("Demonstração Formal do Teorema `sample_sum`", res["explanation_text"])
        self.assertIn("teoria de anéis", res["explanation_text"])
        self.assertFalse(res["has_sorry"])

    def test_cross_validation_aligned(self):
        """Valida a validação cruzada positiva entre texto e código formal."""
        informal = "Seja x um número real, temos que x + 0 = x."
        lean_code = "theorem th_x (x : Real) : x + 0 = x := by intro x; ring"

        cv = self.autoform_engine.cross_validate(informal, lean_code)
        self.assertTrue(cv.is_aligned)
        self.assertEqual(cv.status, "aligned_and_verified")
        self.assertGreaterEqual(cv.confidence_score, 0.90)

    def test_cross_validation_detect_sorry(self):
        """Valida que a validação cruzada rejeita código incompleto com 'sorry'."""
        informal = "Conjectura sobre primos."
        bad_lean = "theorem unproven (n : Nat) : n > 0 := by sorry"

        cv = self.autoform_engine.cross_validate(informal, bad_lean)
        self.assertFalse(cv.is_aligned)
        self.assertEqual(cv.status, "incomplete_sorry")
        self.assertEqual(cv.confidence_score, 0.0)

    def test_orchestrator_geometry_and_autoformalize(self):
        """Valida integração dos métodos no MarceloClaroOrchestrator."""
        geom_res = self.orchestrator.solve_geometry_problem("midpoint_theorem")
        self.assertTrue(geom_res["is_proven"])

        form_res = self.orchestrator.autoformalize_to_lean4("Para x real x + 0 = x")
        self.assertTrue(form_res["is_valid_syntax"])

        exp_res = self.orchestrator.explain_lean4_proof(form_res["lean_code"])
        self.assertIn("Demonstração Formal", exp_res["explanation_text"])

        cv_res = self.orchestrator.cross_validate_reasoning("Para x real x + 0 = x", form_res["lean_code"])
        self.assertTrue(cv_res["is_aligned"])

    def test_doctor_check_geometry(self):
        """Valida o check de geometria sem acoplar ao total evolutivo do doctor."""
        check = _check_geometry_autoformalization_engine()
        self.assertEqual(check.status, "pass")
        self.assertIn("AlphaGeometry & Auto-Formalizer ativos", check.detail)

        doc_report = run_doctor()
        check_names = [item["name"] for item in doc_report["checks"]]
        self.assertIn("geometry_autoformalization_engine", check_names)
        self.assertEqual(doc_report["checks_total"], len(doc_report["checks"]))
        self.assertEqual(doc_report["checks_failed"], 0)


if __name__ == "__main__":
    unittest.main()
