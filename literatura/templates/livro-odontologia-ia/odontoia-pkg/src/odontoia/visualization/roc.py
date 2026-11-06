"""
Módulo roc — Curvas ROC para avaliação de diagnóstico odontológico.

Funções:
    plot_roc_curve         : Plota uma ou mais curvas ROC
    find_optimal_threshold  : Encontra o limiar ótimo (Índice de Youden)
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, roc_auc_score


def plot_roc_curve(
    y_true_list: List[np.ndarray],
    y_score_list: List[np.ndarray],
    labels: Optional[List[str]] = None,
    title: str = "Curva ROC — Diagnóstico Odontológico",
    figsize: Tuple[int, int] = (8, 6),
    show_auc: bool = True,
) -> Tuple[plt.Figure, plt.Axes]:
    """Plota curvas ROC de um ou mais modelos/classificadores.

    A curva ROC (Receiver Operating Characteristic) mostra o trade-off
    entre sensibilidade e especificidade para diferentes limiares
    de classificação.

    Args:
        y_true_list: Lista de arrays com rótulos verdadeiros (0/1)
        y_score_list: Lista de arrays com scores/probabilidades preditas
        labels: Lista de rótulos para legendas (ex: ['CNN', 'RF', 'RegLog'])
        title: Título do gráfico
        figsize: Tamanho da figura
        show_auc: Se True, exibe AUC na legenda

    Example:
        >>> y_true = np.array([0, 0, 1, 1, 0, 1])
        >>> y_score = np.array([0.1, 0.2, 0.6, 0.8, 0.3, 0.9])
        >>> plot_roc_curve([y_true], [y_score], labels=['CNN ResNet'])
    """
    fig, ax = plt.subplots(figsize=figsize)

    if labels is None:
        labels = [f"Modelo {i+1}" for i in range(len(y_true_list))]

    for i, (y_true, y_score) in enumerate(zip(y_true_list, y_score_list)):
        # Remove NaN
        valid = ~(np.isnan(y_score) | np.isnan(y_true))
        yt = y_true[valid]
        ys = y_score[valid]

        if len(np.unique(yt)) < 2:
            print(f"Aviso: Apenas uma classe presente para {labels[i]}")
            continue

        fpr, tpr, thresholds = roc_curve(yt, ys)
        auc_val = roc_auc_score(yt, ys)

        label = labels[i]
        if show_auc:
            label += f" (AUC = {auc_val:.3f})"

        ax.plot(fpr, tpr, lw=2, label=label, alpha=0.8)

    # Diagonal (classificador aleatório)
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Aleatório (AUC=0.5)")
    ax.fill_between([0, 1], [0, 1], alpha=0.05, color="gray")

    ax.set_xlabel("1 - Especificade (FPR)", fontsize=12)
    ax.set_ylabel("Sensibilidade (TPR)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(loc="lower right")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    return fig, ax


def find_optimal_threshold(
    y_true: np.ndarray,
    y_score: np.ndarray,
    maximize: str = "youden",
) -> Tuple[float, float, float]:
    """Encontra o limiar ótimo de classificação usando o Índice de Youden.

    O limiar ótimo é o ponto que maximiza a distância vertical entre a
    curva ROC e a diagonal (sensibilidade + especificidade máximo).

    Args:
        y_true: Rótulos verdadeiros (binário)
        y_score: Scores preditos (probabilidades)
        maximize: Critério de otimização
            'youden': Maximiza sensibilidade + especificidade - 1 (padrão)
            'distance': Minimiza distância ao canto (0,1)

    Returns:
        Tupla (optimal_threshold, sensitivity_at_threshold, specificity_at_threshold)

    Example:
        >>> y_true = np.array([0, 0, 1, 1])
        >>> y_score = np.array([0.1, 0.2, 0.6, 0.8])
        >>> thr, sens, esp = find_optimal_threshold(y_true, y_score)
        >>> print(f"Threshold ótimo: {thr:.3f}, Sens: {sens:.3f}, Esp: {esp:.3f}")
    """
    # Remove inválidos
    valid = ~(np.isnan(y_score) | np.isnan(y_true))
    yt = y_true[valid]
    ys = y_score[valid]

    if len(np.unique(yt)) < 2:
        return 0.5, 0.0, 0.0

    fpr, tpr, thresholds = roc_curve(yt, ys)

    if maximize == "youden":
        youden = tpr - fpr  # J = TPR - FPR = sensibilidade + especificade - 1
        best_idx = np.argmax(youden)
    elif maximize == "distance":
        dist = np.sqrt((1 - tpr) ** 2 + fpr ** 2)
        best_idx = np.argmin(dist)
    else:
        raise ValueError(f"maximize '{maximize}' não suportado")

    opt_threshold = thresholds[best_idx]
    opt_sensitivity = tpr[best_idx]
    opt_specificity = 1 - fpr[best_idx]

    # Garante threshold válido
    if opt_threshold > 1.0:
        # thresholds do roc_curve podem ser > 1 no sklearn
        opt_threshold = 0.5

    return float(opt_threshold), float(opt_sensitivity), float(opt_specificity)