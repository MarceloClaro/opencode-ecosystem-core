"""
Testes para o módulo metrics/ (classification, segmentation)
"""

import numpy as np
import pytest

from odontoia.metrics.classification import (
    sensitivity,
    specificity,
    accuracy,
    precision,
    recall,
    f1_score,
    youden_index,
    binary_clinical_metrics,
)
from odontoia.metrics.segmentation import dice_coefficient, iou_score, segmentation_metrics
from odontoia.metrics.stats import cohens_kappa, mcnemar_test, diagnostic_odds_ratio


class TestClassificationMetrics:
    """Testes para métricas de classificação."""

    def test_sensitivity_perfect(self):
        """sensibilidade = 1.0 quando FN = 0."""
        assert sensitivity(tp=100, fn=0) == 1.0

    def test_sensitivity_zero(self):
        """sensibilidade = 0.0 quando TP = 0."""
        assert sensitivity(tp=0, fn=100) == 0.0

    def test_sensitivity_no_cases(self):
        """sensibilidade = 0.0 quando TP+FN = 0."""
        assert sensitivity(tp=0, fn=0) == 0.0

    def test_specificity_perfect(self):
        """especificidade = 1.0 quando FP = 0."""
        assert specificity(tn=100, fp=0) == 1.0

    def test_specificity_zero(self):
        """especificidade = 0.0 quando TN = 0."""
        assert specificity(tn=0, fp=100) == 0.0

    def test_accuracy_perfect(self):
        """acurácia = 1.0 quando todas corretas."""
        assert accuracy(tp=50, tn=50, fp=0, fn=0) == 1.0

    def test_accuracy_half(self):
        """acurácia = 0.5 quando metade correta."""
        assert accuracy(tp=25, tn=25, fp=25, fn=25) == 0.5

    def test_precision_perfect(self):
        """precisão = 1.0 quando FP = 0."""
        assert precision(tp=80, fp=0) == 1.0

    def test_precision_half(self):
        """precisão = 0.5 quando TP = FP."""
        assert precision(tp=50, fp=50) == 0.5

    def test_recall_equals_sensitivity(self):
        """recall deve ser idêntico à sensitivity."""
        assert recall(tp=75, fn=25) == sensitivity(tp=75, fn=25)

    def test_f1_score_perfect(self):
        """F1 = 1.0 quando classificação perfeita."""
        assert f1_score(tp=100, tn=100, fp=0, fn=0) == 1.0

    def test_f1_score_zero(self):
        """F1 = 0.0 quando TP = 0."""
        assert f1_score(tp=0, tn=100, fp=100, fn=100) == 0.0

    def test_youden_index(self):
        """Índice de Youden = 0.8 para sens=0.9, esp=0.9."""
        j = youden_index(tp=90, tn=90, fp=10, fn=10)
        assert abs(j - 0.8) < 0.001

    def test_binary_clinical_metrics(self):
        """binary_clinical_metrics deve retornar todas as métricas."""
        metrics = binary_clinical_metrics(tp=80, tn=85, fp=15, fn=20)
        assert "sensibilidade" in metrics
        assert "especificidade" in metrics
        assert "acuracia" in metrics
        assert "f1_score" in metrics
        assert metrics["sensibilidade"] == pytest.approx(0.8, abs=0.01)

    def test_roc_auc(self):
        """roc_auc deve calcular AUC corretamente."""
        from odontoia.metrics.classification import roc_auc_score
        y_true = np.array([0, 0, 1, 1])
        y_score = np.array([0.1, 0.4, 0.35, 0.8])
        auc = roc_auc_score(y_true, y_score)
        assert 0.5 <= auc <= 1.0

    def test_roc_auc_single_class(self):
        """roc_auc com uma classe deve retornar 0.5."""
        from odontoia.metrics.classification import roc_auc_score
        y_true = np.array([0, 0, 0])
        y_score = np.array([0.1, 0.2, 0.3])
        auc = roc_auc_score(y_true, y_score)
        assert auc == 0.5


class TestSegmentationMetrics:
    """Testes para métricas de segmentação."""

    def test_dice_perfect_overlap(self):
        """Dice = 1.0 para máscaras idênticas."""
        mask = np.random.randint(0, 2, (64, 64)).astype(np.float32)
        assert dice_coefficient(mask, mask) == pytest.approx(1.0, abs=0.001)

    def test_dice_no_overlap(self):
        """Dice = 0.0 para máscaras sem interseção."""
        mask1 = np.zeros((64, 64), dtype=np.float32)
        mask1[10:30, 10:30] = 1
        mask2 = np.zeros((64, 64), dtype=np.float32)
        mask2[40:60, 40:60] = 1
        assert dice_coefficient(mask1, mask2) < 0.01

    def test_iou_perfect_overlap(self):
        """IoU = 1.0 para máscaras idênticas."""
        mask = np.random.randint(0, 2, (64, 64)).astype(np.float32)
        assert iou_score(mask, mask) == pytest.approx(1.0, abs=0.001)

    def test_iou_no_overlap(self):
        """IoU = 0.0 para máscaras sem interseção."""
        mask1 = np.zeros((32, 32), dtype=np.float32)
        mask1[0:10, 0:10] = 1
        mask2 = np.zeros((32, 32), dtype=np.float32)
        mask2[20:30, 20:30] = 1
        assert iou_score(mask1, mask2) < 0.01

    def test_segmentation_metrics_complete(self):
        """segmentation_metrics deve retornar dice, iou e hd95."""
        mask = np.random.randint(0, 2, (32, 32)).astype(np.float32)
        met = segmentation_metrics(mask, mask)
        assert "dice" in met
        assert "iou" in met
        assert "hd95" in met


class TestStats:
    """Testes para funções estatísticas."""

    def test_cohens_kappa_perfect(self):
        """Kappa = 1.0 para concordância perfeita."""
        y1 = np.array([0, 1, 2, 0, 1, 2])
        assert cohens_kappa(y1, y1) == pytest.approx(1.0, abs=0.001)

    def test_cohens_kappa_random(self):
        """Kappa próximo de 0 para concordância aleatória."""
        rng = np.random.default_rng(42)
        y1 = rng.integers(0, 3, size=100)
        y2 = rng.integers(0, 3, size=100)
        kappa = cohens_kappa(y1, y2)
        assert -0.3 <= kappa <= 0.3  # pode variar mas não deve ser 1

    def test_mcnemar_test(self):
        """mcnemar_test deve retornar dicionário com campos esperados."""
        rng = np.random.default_rng(42)
        y_true = rng.integers(0, 2, size=100)
        model_a = rng.integers(0, 2, size=100)
        model_b = rng.integers(0, 2, size=100)
        result = mcnemar_test(y_true, model_a, model_b)
        assert "statistic" in result
        assert "p_value" in result
        assert "significant" in result

    def test_diagnostic_odds_ratio(self):
        """DOR deve ser > 1 para teste com poder diagnóstico."""
        dor = diagnostic_odds_ratio(tp=85, tn=90, fp=10, fn=15)
        assert dor > 1.0

    def test_diagnostic_odds_ratio_no_power(self):
        """DOR = 1 para teste sem poder diagnóstico."""
        dor = diagnostic_odds_ratio(tp=50, tn=50, fp=50, fn=50)
        assert abs(dor - 1.0) < 0.1