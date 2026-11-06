"""
Módulo detection — Modelos simplificados de detecção de objetos para
radiografias odontológicas.

Este módulo fornece implementações didáticas para o Capítulo 7
(Radiologia Odontológica com Deep Learning).

Funções:
    build_simple_yolo      : Detector YOLO simplificado (didático)
    non_max_suppression    : Supressão de não-máximos para pós-processamento
    compute_detection_metrics : Precisão, revocação e mAP para detecção
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
# Detector Simples baseado em YOLO (didático)
# =============================================================================


class SimpleYOLO(nn.Module):
    """Implementação didática simplificada de YOLO para detecção
    de objetos odontológicos.

    Arquitetura baseada no conceito YOLO (You Only Look Once):
        - Divide a imagem em grid S x S
        - Cada célula prediz B bounding boxes e C classes

    Esta implementação é intencionalmente simplificada para fins
    didáticos (Capítulo 7 do livro). Não é uma YOLO completa.

    Args:
        S: Tamanho do grid (S x S)
        B: Número de bounding boxes por célula
        C: Número de classes (ex: dente, cárie, lesão, restauração)

    Input:
        Tensor (B, 1, 448, 448) - radiografia em tons de cinza

    Output:
        Tensor (B, S, S, (B*5 + C)) onde:
            - 5 = (x, y, w, h, objectness) para cada box
            - C = probabilidades condicionais de classe

    Example:
        >>> model = SimpleYOLO(S=7, B=2, C=4)
        >>> x = torch.randn(4, 1, 448, 448)
        >>> y = model(x)
        >>> y.shape
        torch.Size([4, 7, 7, 14])
    """

    def __init__(self, S: int = 7, B: int = 2, C: int = 4):
        super().__init__()
        self.S = S
        self.B = B
        self.C = C

        # Camadas convolucionais de extração de features
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(16),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.1, inplace=True),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.1, inplace=True),
        )

        # Classificador final
        self._flattened = 64 * (S * S)
        self.fc = nn.Sequential(
            nn.Linear(self._flattened, 1024),
            nn.Dropout(0.5),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Linear(1024, S * S * (B * 5 + C)),
        )

        self.S = S
        self.B = B
        self.C = C

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass da YOLO simplificada.

        Args:
            x: Tensor (batch, 1, 448, 448)

        Returns:
            Tensor (batch, S, S, B*5 + C)
        """
        batch_size = x.shape[0]

        # Extrai features
        x = self.features(x)

        # Redimensionamento adaptativo para grid S x S
        x = F.interpolate(x, size=(self.S, self.S), mode="bilinear", align_corners=False)
        x = x.view(batch_size, -1)

        # Classificador
        x = self.fc(x)
        x = x.view(batch_size, self.S, self.S, self.B * 5 + self.C)
        return x


def build_simple_yolo(
    S: int = 7, B: int = 2, n_classes: int = 4
) -> nn.Module:
    """Constrói um detector YOLO simplificado para fins didáticos.

    Args:
        S: Tamanho do grid (padrão 7x7)
        B: Número de bounding boxes por célula (padrão 2)
        n_classes: Número de classes odontológicas

    Returns:
        Modelo SimpleYOLO pronto para treino

    Example:
        >>> detector = build_simple_yolo(S=7, B=2, n_classes=4)
    """
    return SimpleYOLO(S=S, B=B, C=n_classes)


def non_max_suppression(
    boxes: torch.Tensor,
    scores: torch.Tensor,
    iou_threshold: float = 0.5,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Aplica supressão de não-máximos (NMS) para eliminar detecções
    redundantes.

    Algoritmo:
        1. Ordena detecções por confiança decrescente
        2. Seleciona a de maior confiança
        3. Remove caixas com IoU > threshold com esta seleção
        4. Repete até não restarem caixas

    Args:
        boxes: Tensor (N, 4) com coordenadas (x1, y1, x2, y2)
        scores: Tensor (N,) com pontuação de confiança
        iou_threshold: Limiar de IoU para considerar sobreposição

    Returns:
        Tupla (boxes_filtradas, scores_filtradas)

    Example:
        >>> boxes = torch.tensor([[10, 10, 50, 50], [15, 15, 55, 55]], dtype=torch.float32)
        >>> scores = torch.tensor([0.9, 0.8])
        >>> keep_boxes, keep_scores = non_max_suppression(boxes, scores, 0.5)
    """
    if boxes.shape[0] == 0:
        return boxes.new_zeros((0, 4)), scores.new_zeros((0,))

    # Ordena por score descendente
    order = scores.argsort(descending=True)
    sorted_boxes = boxes[order]
    sorted_scores = scores[order]

    keep_boxes = []
    keep_scores = []

    while sorted_boxes.shape[0] > 0:
        # Seleciona a caixa de maior score
        best_box = sorted_boxes[0:1]
        best_score = sorted_scores[0]
        keep_boxes.append(best_box)
        keep_scores.append(best_score)

        if sorted_boxes.shape[0] > 1:
            # Calcula IoU entre a melhor caixa e as demais
            ious = _batch_iou(best_box, sorted_boxes[1:])
            # Mantém caixas com IoU < threshold
            mask = ious < iou_threshold
            sorted_boxes = sorted_boxes[1:][mask]
            sorted_scores = sorted_scores[1:][mask]
        else:
            break

    if not keep_boxes:
        return torch.zeros((0, 4)), torch.zeros((0,))

    return torch.cat(keep_boxes, dim=0), torch.stack(keep_scores)


def _batch_iou(box_a: torch.Tensor, box_b: torch.Tensor) -> torch.Tensor:
    """Calcula IoU entre um conjunto de caixas.

    Args:
        box_a: Tensor (1, 4)
        box_b: Tensor (N, 4)

    Returns:
        Tensor (N,) com IoU entre box_a e cada box_b
    """
    # Coordenadas da interseção
    x1 = torch.maximum(box_a[0], box_b[:, 0])
    y1 = torch.maximum(box_a[1], box_b[:, 1])
    x2 = torch.minimum(box_a[2], box_b[:, 2])
    y2 = torch.minimum(box_a[3], box_b[:, 3])

    # Área da interseção
    inter_area = torch.clamp(x2 - x1, min=0) * torch.clamp(y2 - y1, min=0)

    # Área da união
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[:, 2] - box_b[:, 0]) * (box_b[:, 3] - box_b[:, 1])
    union_area = area_a + area_b - inter_area

    return inter_area / (union_area + 1e-7)