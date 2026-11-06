"""
Módulo classification — Métricas de classificação clínica para odontologia.

Implementa métricas padrão da literatura para avaliação de modelos de
diagnóstico bucal assistido por computador.

Funções:
    sensitivity            : Sensibilidade (taxa de verdadeiros positivos)
    specificity            : Especificidade (taxa de verdadeiros negativos)
    accuracy               : Acurácia global
    precision              : Precisão (valor preditivo positivo)
    recall                 : Revocação (sensibilidade — alias)
    f1_score               : F1-Score (média harmônica precisão-recall)
    confusion_matrix_plot  : Matriz de confusão visual
    auc_roc                : AUC da curva ROC
    roc_auc                : Alias para auc_roc
    youden_index           : Índice de Youden (J = sensibilidade + especificidade - 1)
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np


def sensitivity(tp: int, fn: int) -> float:
    """Calcula a sensibilidade (taxa de verdadeiros positivos).

    Sensibilidade = TP / (TP + FN)

    Representa a capacidade do teste de identificar corretamente os
    pacientes que realmente têm a condição.

    Na odontologia, alta sensibilidade é crucial para:
        - Rastreio de lesões de alto risco (ex: câncer bucal)
        - Detecção precoce de cáries oclusais

    Args:
        tp: Número de verdadeiros positivos
        fn: Número de falsos negativos

    Returns:
        Sensibilidade no intervalo [0, 1]

    Example:
        >>> sens = sensitivity(tp=85, fn=15)
        >>> print(f"Sensibilidade: {sens:.2%}")
        Sensibilidade: 85.00%

    Note:
        Se (TP + FN) = 0, retorna 0.0
    """
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)


def specificity(tn: int, fp: int) -> float:
    """Calcula a especificidade (taxa de verdadeiros negativos).

    Especificidade = TN / (TN + FP)

    Representa a capacidade de identificar corretamente os pacientes
    que NÃO têm a condição.

    Na odontologia, alta especificidade é crucial para:
        - Evitar tratamentos desnecessários (falsos positivos)
        - Diagnóstico diferencial de lesões benignas vs. malignas

    Args:
        tn: Número de verdadeiros negativos
        fp: Número de falsos positivos

    Returns:
        Especificidade no intervalo [0, 1]

    Example:
        >>> spec = specificity(tn=90, fp=10)
        >>> print(f"Especificidade: {spec:.2%}")
        Especificidade: 90.00%
    """
    if tn + fp == 0:
        return 0.0
    return tn / (tn + fp)


def accuracy(tp: int, tn: int, fp: int, fn: int) -> float:
    """Calcula a acurácia geral do classificador.

    Acurácia = (TP + TN) / (TP + TN + FP + FN)

    Args:
        tp: Verdadeiros positivos
        tn: Verdadeiros negativos
        fp: Falsos positivos
        fn: Falsos negativos

    Returns:
        Acurácia no intervalo [0, 1]

    Example:
        >>> acc = accuracy(tp=80, tn=85, fp=15, fn=20)
        >>> print(f"Acurácia: {acc:.2%}")
    """
    total = tp + tn + fp + fn
    if total == 0:
        return 0.0
    return (tp + tn) / total


def precision(tp: int, fp: int) -> float:
    """Calcula a precisão (valor preditivo positivo).

    Precisão = TP / (TP + FP)

    Args:
        tp: Verdadeiros positivos
        fp: Falsos positivos

    Returns:
        Precisão no intervalo [0, 1]

    Example:
        >>> prec = precision(tp=80, fp=20)
        >>> print(f"Precisão: {prec:.2%}")
        Precisão: 80.00%
    """
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)


def recall(tp: int, fn: int) -> float:
    """Calcula o recall (sinônimo de sensibilidade).

    Recall = TP / (TP + FN)

    Args:
        tp: Verdadeiros positivos
        fn: Falsos negativos

    Returns:
        Recall no intervalo [0, 1]
    """
    return sensitivity(tp, fn)


def f1_score(tp: int, tn: int, fp: int, fn: int) -> float:
    """Calcula o F1-Score (média harmônica entre precisão e recall).

    F1 = 2 * (precisão * recall) / (precisão + recall)

    Equivalente a:
        F1 = 2TP / (2TP + FP + FN)

    Args:
        tp: Verdadeiros positivos
        tn: Verdadeiros negativos (não usado diretamente)
        fp: Falsos positivos
        fn: Falsos negativos

    Returns:
        F1-Score no intervalo [0, 1]

    Example:
        >>> f1 = f1_score(tp=80, tn=85, fp=15, fn=20)
        >>> print(f"F1: {f1:.2%}")
    """
    if 2 * tp + fp + fn == 0:
        return 0.0
    return (2 * tp) / (2 * tp + fp + fn)


def youden_index(tp: int, tn: int, fp: int, fn: int) -> float:
    """Calcula o Índice de Youden.

    J = sensibilidade + especificidade - 1

    Mede a capacidade do teste em equilibrar sensibilidade e especificidade.

    Args:
        tp: Verdadeiros positivos
        tn: Verdadeiros negativos
        fp: Falsos positivos
        fn: Falsos negativos

    Returns:
        Índice de Youden no intervalo [-1, 1]

    Example:
        >>> j = youden_index(tp=85, tn=90, fp=10, fn=15)
        >>> print(f"Índice de Youden: {j:.2f}")
    """
    sens = sensitivity(tp, fn)
    esp = specificity(tn, fp)
    return sens + esp - 1.0


def roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Calcula a AUC (Area Under the ROC Curve).

    A AUC representa a probabilidade de o classificador ordenar um
    positivo aleatório acima de um negativo aleatório.

    Args:
        y_true: Rótulos binários verdadeiros (0 ou 1)
        y_score: Scores de predição (probabilidades ou scores)

    Returns:
        AUC no intervalo [0, 1]; 0.5 = aleatório, 1.0 = perfeito

    Example:
        >>> y_true = np.array([0, 0, 1, 1])
        >>> y_score = np.array([0.1, 0.4, 0.35, 0.8])
        >>> auc_val = roc_auc(y_true, y_score)
        >>> print(f"AUC: {auc_val:.3f}")
    """
    from sklearn.metrics import roc_auc_score as sk_auc
    # Garante formato 1D
    y_t = np.array(y_true).ravel()
    y_s = np.array(y_score).ravel()
    # Se só uma classe, AUC não é definida
    if len(np.unique(y_t)) < 2:
        return 0.5
    return float(sk_auc(y_t, y_s))


# Alias
roc_auc_score = roc_auc


def confusion_matrix_plot(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
    title: str = "Matriz de Confusão — Diagnóstico Odontológico",
    cmap: str = "Blues",
    normalize: bool = True,
) -> None:
    """Plota a matriz de confusão da classificação.

    Gera uma visualização da matriz de confusão usando matplotlib.

    Args:
        y_true: Rótulos verdadeiros (array 1D)
        y_pred: Rótulos preditos (array 1D)
        labels: Lista de nomes das classes (ex: ['saudável', 'cárie', 'lesão'])
        title: Título do gráfico (em português, padrão clínico)
        cmap: Mapa de cores matplotlib
        normalize: Se True, exibe proporções em vez de valores absolutos

    Example:
        >>> y_true = np.array([0, 0, 1, 1, 2, 2])
        >>> y_pred = np.array([0, 0, 1, 2, 2, 2])
        >>> confusion_matrix_plot(y_true, y_pred,
        ...     labels=['saudável', 'cárie', 'lesão'])
    """
    import matplotlib.pyplot as plt
    from sklearn.metrics._plot.confusion_matrix import ConfusionMatrixDisplay
    from sklearn.metrics import confusion_matrix

    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)
        display = ConfusionMatrixDisplay(confusion_matrix=cm_norm, display_labels=labels)
    else:
        display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)

    fig, ax = plt.subplots(figsize=(8, 6))
    display.plot(ax=ax, cmap=cmap, values_format=".2f" if normalize else "d")
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()



def binary_clinical_metrics(
    tp: int, tn: int, fp: int, fn: int
) -> dict:
    """Calcula todas as métricas clínicas binárias de uma vez.

    Args:
        tp: Verdadeiros positivos
        tn: Verdadeiros negativos
        fp: Falsos positivos
        fn: Falsos negativos

    Returns:
        Dicionário com sensibilidade, especificidade, acurácia, precisão,
        F1, índice de Youden, VPP e NPVP

    Example:
        >>> metrics = binary_clinical_metrics(tp=80, tn=85, fp=15, fn=20)
        >>> print(metrics['sensibilidade'])
    """
    sens = sensitivity(tp, fn)
    esp = specificity(tn, fp)
    acc = accuracy(tp, tn, fp, fn)
    prec = precision(tp, fp)
    f1 = f1_score(tp, tn, fp, fn)
    youden = youden_index(tp, tn, fp, fn)

    return {
        "sensibilidade": sens,
        "especificidade": esp,
        "acuracia": acc,
        "precisao_vpp": prec,
        "f1_score": f1,
        "youden": youden,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }