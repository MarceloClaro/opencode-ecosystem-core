"""
Módulo segmentation — Modelos de segmentação semântica para radiografias
odontológicas com U-Net.

Funções:
    build_unet       : Constrói uma U-Net para segmentação dental
    dice_coef       : Coeficiente Dice (similaridade volumétrica)
    iou_score       : Intersection over Union (Jaccard Index)
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
# Métricas de segmentação
# =============================================================================


def dice_coef(
    y_pred: torch.Tensor,
    y_true: torch.Tensor,
    smooth: float = 1e-7,
) -> torch.Tensor:
    """Calcula o coeficiente Dice para segmentação semântica.

    Dice = (2 * |A ∩ B|) / (|A| + |B|)

    Usado como métrica principal para segmentação dental, onde
    classes desbalanceadas (fundo vs. dente) são comuns.

    Args:
        y_pred: Predições (logits ou probabilidades) shape (B, C, H, W)
        y_true: Ground truth shape (B, H, W) com índices de classe,
                ou (B, C, H, W) one-hot
        smooth: Pequeno valor para evitar divisão por zero

    Returns:
        Tensor escalar com o Dice médio entre classes

    Example:
        >>> pred = torch.randn(2, 3, 128, 128)
        >>> true = torch.randint(0, 3, (2, 128, 128))
        >>> dice = dice_coef(pred, true)
    """
    # Converte para probabilidades se necessário
    if y_pred.shape[1] > 1:
        y_pred = F.softmax(y_pred, dim=1)
    else:
        y_pred = torch.sigmoid(y_pred)

    # One-hot encoding do ground truth se necessário
    if y_true.shape == y_pred.shape:
        y_true_onehot = y_true
    else:
        n_classes = y_pred.shape[1]
        y_true_onehot = F.one_hot(y_true, num_classes=n_classes)
        y_true_onehot = y_true_onehot.permute(0, 3, 1, 2).float()

    # Interseção e união
    intersection = (y_pred * y_true_onehot).sum(dim=(2, 3))
    union = (y_pred + y_true_onehot).sum(dim=(2, 3))

    dice = (2.0 * intersection + smooth) / (union + smooth)
    return dice.mean()


def iou_score(
    y_pred: torch.Tensor,
    y_true: torch.Tensor,
    smooth: float = 1e-7,
) -> torch.Tensor:
    """Calcula o IoU (Intersection over Union / Jaccard Index).

    IoU = |A ∩ B| / |A ∪ B|

    Padrão ouro para avaliação de segmentação em radiografias dentárias.

    Args:
        y_pred: Predições shape (B, C, H, W) ou (B, 1, H, W)
        y_true: Ground truth shape (B, H, W) ou (B, C, H, W)
        smooth: Suavização para estabilidade numérica

    Returns:
        Tensor escalar com IoU médio entre classes

    Example:
        >>> iou = iou_score(pred, true)
    """
    if y_pred.shape[1] > 1:
        y_pred = F.softmax(y_pred, dim=1)
    else:
        y_pred = torch.sigmoid(y_pred)

    if y_true.shape != y_pred.shape:
        n_classes = y_pred.shape[1]
        y_true_onehot = F.one_hot(y_true, num_classes=n_classes)
        y_true_onehot = y_true_onehot.permute(0, 3, 1, 2).float()
    else:
        y_true_onehot = y_true

    intersection = (y_pred * y_true_onehot).sum(dim=(2, 3))
    union = (y_pred + y_true_onehot).sum(dim=(2, 3)) - intersection

    iou = (intersection + smooth) / (union + smooth)
    return iou.mean()


# =============================================================================
# Bloco convolucional duplo da U-Net
# =============================================================================


class DoubleConv(nn.Module):
    """Bloco convolucional duplo: Conv2D -> BN -> ReLU -> Conv2D -> BN -> ReLU

    Bloco básico constituinte da U-Net, usado tanto no encoder quanto no decoder.
    """

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


# =============================================================================
# U-Net completa para segmentação dental
# =============================================================================


class UNet(nn.Module):
    """U-Net para segmentação semântica de radiografias odontológicas.

    Arquitetura simétrica encoder-decoder com skip connections.
    Projetada para segmentar dentes, lesões e estruturas anatômicas
    em radiografias panorâmicas e periapicais.

    Args:
        in_channels: Número de canais de entrada (1 para tons de cinza)
        n_classes: Número de classes de segmentação
        base_filters: Número de filtros na primeira camada (dobre a cada nível)

    Example:
        >>> model = UNet(in_channels=1, n_classes=6)
        >>> x = torch.randn(2, 1, 256, 256)
        >>> y = model(x)
        >>> y.shape
        torch.Size([2, 6, 256, 256])
    """

    def __init__(
        self,
        in_channels: int = 1,
        n_classes: int = 2,
        base_filters: int = 64,
    ):
        super().__init__()

        # Encoder (contração)
        self.enc1 = DoubleConv(in_channels, base_filters)
        self.enc2 = DoubleConv(base_filters, base_filters * 2)
        self.enc3 = DoubleConv(base_filters * 2, base_filters * 4)
        self.enc4 = DoubleConv(base_filters * 4, base_filters * 8)
        self.pool = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = DoubleConv(base_filters * 8, base_filters * 16)

        # Decoder (expansão)
        self.upconv4 = nn.ConvTranspose2d(
            base_filters * 16, base_filters * 8, kernel_size=2, stride=2
        )
        self.dec4 = DoubleConv(base_filters * 16, base_filters * 8)

        self.upconv3 = nn.ConvTranspose2d(
            base_filters * 8, base_filters * 4, kernel_size=2, stride=2
        )
        self.dec3 = DoubleConv(base_filters * 8, base_filters * 4)

        self.upconv2 = nn.ConvTranspose2d(
            base_filters * 4, base_filters * 2, kernel_size=2, stride=2
        )
        self.dec2 = DoubleConv(base_filters * 4, base_filters * 2)

        self.upconv1 = nn.ConvTranspose2d(
            base_filters * 2, base_filters, kernel_size=2, stride=2
        )
        self.dec1 = DoubleConv(base_filters * 2, base_filters)

        # Camada de saída
        self.final = nn.Conv2d(base_filters, n_classes, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encoder com skip connections
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))

        # Bottleneck
        b = self.bottleneck(self.pool(e4))

        # Decoder com skip connections
        d4 = self.upconv4(b)
        # Ajuste de tamanho se necessário (padding)
        if d4.shape[-2:] != e4.shape[-2:]:
            d4 = F.interpolate(d4, size=e4.shape[-2:], mode="bilinear", align_corners=False)
        d4 = self.dec4(torch.cat([d4, e4], dim=1))

        d3 = self.upconv3(d4)
        if d3.shape[-2:] != e3.shape[-2:]:
            d3 = F.interpolate(d3, size=e3.shape[-2:], mode="bilinear", align_corners=False)
        d3 = self.dec3(torch.cat([d3, e3], dim=1))

        d2 = self.upconv2(d3)
        if d2.shape[-2:] != e2.shape[-2:]:
            d2 = F.interpolate(d2, size=e2.shape[-2:], mode="bilinear", align_corners=False)
        d2 = self.dec2(torch.cat([d2, e2], dim=1))

        d1 = self.upconv1(d2)
        if d1.shape[-2:] != e1.shape[-2:]:
            d1 = F.interpolate(d1, size=e1.shape[-2:], mode="bilinear", align_corners=False)
        d1 = self.dec1(torch.cat([d1, e1], dim=1))

        return self.final(d1)


# =============================================================================
# Função pública de alto nível
# =============================================================================


def build_unet(
    in_channels: int = 1,
    n_classes: int = 2,
    base_filters: int = 64,
) -> nn.Module:
    """Constrói uma U-Net para segmentação de radiografias odontológicas.

    Função de alto nível recomendada para o Capítulo 6 (Segmentação Semântica).

    Args:
        in_channels: Canais de entrada (1 para radiografias, 3 para RGB)
        n_classes: Número de classes de segmentação
            Ex: 2 (fundo/dente), 6 (fundo + 5 estruturas)
        base_filters: Filtros base (dobre a cada nível encoder)

    Returns:
        Modelo U-Net PyTorch não-treinado

    Example:
        >>> model = build_unet(in_channels=1, n_classes=6)
        >>> total_params = sum(p.numel() for p in model.parameters())
        >>> print(f"Parâmetros: {total_params:,}")
    """
    model = UNet(
        in_channels=in_channels,
        n_classes=n_classes,
        base_filters=base_filters,
    )
    return model