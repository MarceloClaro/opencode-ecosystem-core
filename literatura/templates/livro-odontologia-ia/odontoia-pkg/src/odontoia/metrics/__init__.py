"""
Subpacote 'metrics' — Métricas clínicas e estatísticas para odontologia.

Componentes:
    classification : Métricas de classificação (acurácia, sensibilidade, F1, AUC)
    segmentation   : Métricas de segmentação (Dice, IoU)
    stats          : Testes estatísticos (Kappa, McNemar, correlação)

Exemplo:
    >>> from odontoia.metrics import accuracy, sensitivity, dice_coef
    >>> acc = accuracy(tp=50, tn=40, fp=5, fn=5)
"""

from odontoia.metrics.classification import (
    sensitivity,
    specificity,
    accuracy,
    precision,
    recall,
    f1_score,
    confusion_matrix_plot,
    roc_auc_score,
    youden_index,
)
from odontoia.metrics.segmentation import dice_coefficient, iou_score
from odontoia.metrics.stats import kappa_score, mcnemar_test, cohens_kappa

__all__ = [
    "sensitivity",
    "specificity",
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "confusion_matrix_plot",
    "roc_auc",
    "youden_index",
    "dice_coefficient",
    "iou_score",
    "kappa_score",
    "mcnemar_test",
    "cohens_kappa",
]