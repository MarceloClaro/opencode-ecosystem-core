# -*- coding: utf-8 -*-
"""
Testes do modelo travado e da inferencia — SPEC-935-R645 (ciclo R645).

Obras para o caminho de PREDICAO CLINICA: o manuscrito so pode ser enquadrado
como estudo de predicao clinica se existir um artefato travado, reproduzivel e
inferivel por terceiros, com provenance e avisos anti-overclaim embutidos.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "manuscript_assets"
BUNDLE = ASSETS / "odontoca_clinical_model.joblib"
CARD = ASSETS / "odontoca_clinical_model_card.json"

sys.path.insert(0, str(ASSETS))


def _require_artifacts(test):
    if not BUNDLE.exists() or not CARD.exists():
        raise unittest.SkipTest(
            "Artefatos ausentes; gere com: python3 manuscript_assets/lock_final_model.py"
        )


class TestLockedModelArtifact(unittest.TestCase):

    def setUp(self):
        _require_artifacts(self)
        self.bundle = joblib.load(BUNDLE)
        self.card = json.loads(CARD.read_text(encoding="utf-8"))

    # --- fail-closed da coorte -----------------------------------------
    def test_cohort_matches_manuscript(self):
        self.assertEqual(self.card["cohort"], {"rows": 996, "events": 83, "children": 81})

    # --- escolha do primario e uma decisao justificada ------------------
    def test_primary_is_clinical_minimal(self):
        self.assertEqual(self.bundle["primary_model"], "clinical_minimal")
        self.assertIn("available at a routine visit", self.bundle["role_note"])

    def test_spatial_model_is_secondary_not_silent_default(self):
        self.assertIn("clinical_spatial", self.bundle["pipelines"])
        self.assertEqual(self.card["secondary_exploratory_model"], "clinical_spatial")

    def test_no_forbidden_variable_in_any_model(self):
        forbidden = {
            "Future_Status_Tooth", "HostGroup", "Time_to_decay", "delta_months",
            "future_status_source_t", "host_group_source", "progression_event",
            "state_t1", "time_to_decay_source_t", "timepoint_t1",
        }
        for name, cols in self.bundle["required_columns"].items():
            leak = forbidden.intersection(cols)
            self.assertFalse(leak, f"[{name}] variavel de desfecho/futuro: {leak}")

    # --- recalibracao e hiperparametros ---------------------------------
    def test_recalibration_present_and_monotone(self):
        for name, params in self.bundle["recalibration"].items():
            self.assertIn("intercept", params)
            self.assertIn("slope", params)
            self.assertGreater(params["slope"], 0, f"[{name}] slope deve ser positivo")

    def test_selected_c_within_grid(self):
        for name, value in self.bundle["selected_C"].items():
            self.assertIn(value, [0.01, 0.1, 1.0, 10.0], f"[{name}] C fora da grade")

    # --- provenance ------------------------------------------------------
    def test_versions_and_seed_recorded(self):
        for key in ("python", "scikit_learn", "numpy", "scipy", "pandas"):
            self.assertIn(key, self.bundle["versions"])
        self.assertEqual(self.bundle["seed"], 20260930)
        self.assertTrue(self.bundle["locked_utc"].startswith("20"))

    def test_source_data_hash_pinned(self):
        self.assertIn("b7819fee", json.dumps(self.bundle["source"]))

    def test_artifact_hash_matches_file(self):
        import hashlib
        h = hashlib.sha256(BUNDLE.read_bytes()).hexdigest()
        self.assertEqual(self.card["artifact"]["sha256"], h)

    # --- anti-overclaim: avisos obrigatorios -----------------------------
    def test_card_declares_no_external_validation(self):
        self.assertIn("NEITHER is external validation", self.card["interpretation_warning"])
        self.assertTrue(
            any("No external or temporal validation" in item
                for item in self.card["known_limitations"]),
            "known_limitations deve declarar ausencia de validacao externa/temporal",
        )

    def test_card_discloses_full_cohort_c_selection_optimism(self):
        d = self.card["hyperparameter_selection_disclosure"]
        self.assertIn("selected ONCE on the full cohort", d)
        self.assertIn("0.753 vs 0.686", d)

    def test_card_points_to_manuscript_numbers_for_reporting(self):
        self.assertIn("0.686", self.card["performance_to_report"])
        self.assertIn("0.0745", self.card["performance_to_report"])

    def test_card_is_research_only_no_threshold(self):
        use = self.card["intended_use"]
        self.assertIn("Research use only", use)
        self.assertIn("Not a medical device", use)
        self.assertIn("No decision threshold was pre-specified", use)
        self.assertIn("must not be used to trigger treatment", use)

    def test_apparent_metrics_labelled_optimistic(self):
        for name in self.card["models"]:
            key = [k for k in self.card["models"][name] if k.startswith("apparent_metrics")]
            self.assertTrue(key and "OPTIMISTIC" in key[0],
                            f"[{name}] metricas aparentes devem ser rotuladas OPTIMISTIC")

    def test_apparent_beats_crossfitted_as_expected_for_overfitting(self):
        """Sanity: o modelo aparente deve parecer melhor que o cross-fitted."""
        m = self.card["models"]["clinical_minimal"]
        self.assertGreater(
            m["apparent_metrics_OPTIMISTIC"]["roc_auc"],
            m["cross_fitted_recalibrated_metrics"]["roc_auc"],
        )


class TestInferenceScript(unittest.TestCase):

    def setUp(self):
        _require_artifacts(self)
        from predict_clinical_risk import load_bundle
        self.bundle = load_bundle(BUNDLE)
        self.rows = pd.DataFrame(
            {
                "tooth_position": ["51", "51", "61"],
                "age_months_t": [30.0, 30.0, 42.0],
                "host_dmfs_t": [1.0, 1.0, 4.0],
                "neighbor_caries_count": [1.0, 0.0, 2.0],
            }
        )

    def test_returns_one_row_per_input_tooth(self):
        from predict_clinical_risk import predict
        out = predict(self.bundle, self.rows, "clinical_minimal")
        self.assertEqual(len(out), len(self.rows))
        self.assertTrue(out["risk_calibrated"].between(0, 1).all())
        self.assertTrue((out["risk_calibrated"] >= 0).all())

    def test_higher_dmfs_and_age_not_lower_risk(self):
        """Sanity monotonicidade clinica: mais carga de cárie -> risco maior."""
        from predict_clinical_risk import predict
        low = pd.DataFrame([{
            "tooth_position": "51", "age_months_t": 12.0,
            "host_dmfs_t": 0.0, "neighbor_caries_count": 0.0,
        }])
        high = pd.DataFrame([{
            "tooth_position": "51", "age_months_t": 48.0,
            "host_dmfs_t": 6.0, "neighbor_caries_count": 4.0,
        }])
        p = predict(self.bundle, self.rows, "clinical_minimal")
        self.assertGreater(
            float(predict(self.bundle, high, "clinical_minimal")["risk_calibrated"].iloc[0]),
            float(predict(self.bundle, low, "clinical_minimal")["risk_calibrated"].iloc[0]),
        )

    def test_missing_column_fails_closed(self):
        from predict_clinical_risk import predict
        with self.assertRaises(SystemExit):
            predict(self.bundle, self.rows[["tooth_position"]], "clinical_minimal")

    def test_unknown_model_fails_closed(self):
        from predict_clinical_risk import predict
        with self.assertRaises(SystemExit):
            predict(self.bundle, self.rows, "modelo_inexistente")

    def test_unknown_tooth_position_does_not_crash(self):
        """handle_unknown='ignore' deve absorver categoria nova, nao estourar."""
        from predict_clinical_risk import predict
        weird = self.rows.copy()
        weird["tooth_position"] = ["99", "99", "99"]
        out = predict(self.bundle, weird, "clinical_minimal")
        self.assertTrue(out["risk_calibrated"].between(0, 1).all())

    def test_cli_end_to_end_writes_output_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.csv"
            dst = Path(tmp) / "out.csv"
            self.rows.to_csv(src, index=False)
            proc = subprocess.run(
                [sys.executable, str(ASSETS / "predict_clinical_risk.py"),
                 str(src), "-o", str(dst)],
                capture_output=True, text=True, timeout=300,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr[-2000:])
            out = pd.read_csv(dst)
            self.assertIn("risk_calibrated", out.columns)
            self.assertIn("sklearn_version", out.columns)
            meta = json.loads(proc.stdout)
            self.assertIn("Nao usar para acionar tratamento", meta["warning"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
