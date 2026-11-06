"""
Módulo segmentation — Métricas de segmentação semântica para radiografias
odontológicas.

Funções:
    dice_coefficient : Coeficiente Dice (DSC) — similaridade de segmentação
    iou_score        : Intersection over Union (IoU / Jaccard Index)
    hausdorff_distance : Distância de Hausdorff (precisão de bordas)
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def dice_coefficient(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    smooth: float = 1e-7,
) -> float:
    """Calcula o coeficiente Dice (DSC — Dice Similarity Coefficient).

    DSC = 2 * |A ∩ B| / (|A| + |B|)

    Métrica padrão para segmentação semântica em imagens médicas,
    incluindo radiografias odontológicas.

    Args:
        y_true: Máscara binária verdadeira (H, W) ou (H, W, C)
        y_pred: Máscara binária predita (H, W) ou (H, W, C)
        smooth: Suavização para evitar divisão por zero

    Returns:
        Coeficiente Dice (0 = nenhuma sobreposição, 1 = sobreposição perfeita)

    Example:
        >>> y_true = np.zeros((256, 256))
        >>> y_true[50:150, 50:150] = 1
        >>> y_pred = np.zeros((256, 256))
        >>> y_pred[60:140, 60:140] = 1
        >>> dice = dice_coefficient(y_true, y_pred)
        >>> print(f"Dice: {dice:.4f}")
        Dice: 0.6400
    """
    # Binariza
    y_t = (y_true > 0.5).astype(np.float32)
    y_p = (y_pred > 0.5).astype(np.float32)

    intersection = np.sum(y_t * y_p)
    union = np.sum(y_t) + np.sum(y_p)

    if union == 0:
        return 1.0  # ambos vazios: concordância perfeita

    dice = (2.0 * intersection + smooth) / (union + smooth)
    return float(dice)


def iou_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    smooth: float = 1e-7,
) -> float:
    """Calcula o IoU (Intersection over Union / Jaccard Index).

    IoU = |A ∩ B| / |A ∪ B|

    Métrica complementar ao Dice, mais sensível a falsos positivos.

    Args:
        y_true: Máscara binária verdadeira (H, W)
        y_pred: Máscara binária predita (H, W)
        smooth: Suavização para estabilidade numérica

    Returns:
        IoU (0 = nenhuma sobreposição, 1 = sobreposição perfeita)

    Example:
        >>> iou = iou_score(y_true, y_pred)
        >>> print(f"IoU: {iou:.4f}")
    """
    y_true = (y_true > 0.5).astype(np.float32)
    y_pred = (y_pred > 0.5).astype(np.float32)

    intersection = np.sum(y_true * y_pred)
    union = np.sum(y_true) + np.sum(y_pred) - intersection

    if union == 0:
        return 1.0

    return float((intersection + smooth) / (union + smooth))


def hausdorff_distance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    percentile: float = 95.0,
) -> float:
    """Calcula a distância de Hausdorff percentil entre dois contornos.

    Mede a máxima distância entre as bordas das segmentações.
    Valores baixos = segumentação precisa nas bordas.

    Args:
        y_true: Máscara verdadeira binária (H, W)
        y_pred: Máscara predita binária (H, W)
        percentile: Percentil usado (95% HD = HD95, padrão)

    Returns:
        Distância de Hausdorff (em pixels)

    Example:
        >>> hd = hausdorff_distance(y_true, y_pred)
        >>> print(f"HD95: {hd:.2f} px")
    """
    from scipy.ndimage import binary_erosion, distance_transform_edt

    # Extrai contornos: borda = máscara - erosão
    if y_true.max() > 0 and y_pred.max() > 0:
        from scipy.ndimage import distance_transform_edt

        dist_true = distance_transform_edt(~(y_true > 0))
        dist_pred = distance_transform_edt(~(y_pred > 0))

        # Distâncias das bordas de um para o outro
        d1 = np.ravel(dist_pred[y_true > 0])
        d2 = np.ravel(dist_true[y_pred > 0])

        if d1.size == 0 or d2.size == 0:
            return float("inf")

        hd = max(np.percentile(d1, percentile), np.percentile(d2, percentile))
        return float(hd)
    return float("inf")


def segmentation_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> dict:
    """Calcula todas as métricas de segmentação de uma vez.

    Args:
        y_true: Máscara verdadeira (H, W) ou (H, W, C)
        y_pred: Máscara predita (H, W) ou (H, W, C)

    Returns:
        Dicionário com dice, iou, hd95

    Example:
        >>> metrics = segmentation_metrics(y_true, y_pred)
        >>> print(f"Dice: {metrics['dice']:.4f}, IoU: {metrics['iou']:.4f}")
    """
    dice = dice_coefficient(y_true, y_pred)
    iou = iou_score(y_true, y_pred)
    hd95 = hausdorff_distance(y_true, y_pred, percentile=95.0)

    return {
        "dice": dice,
        "iou": iou,
        "hd95": hd95,
        "hd95_valido": hd95 != float("inf"),
    }