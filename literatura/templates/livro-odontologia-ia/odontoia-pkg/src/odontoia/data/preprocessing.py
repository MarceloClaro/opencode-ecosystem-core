"""
Módulo preprocessing — Preparação de imagens odontológicas para modelos de IA.

Funções disponíveis:
    normalize_image     : Normalização min-max para [0,1]
    clahe_equalization    : CLAHE para realce de radiografias
    resize_with_aspect    : Redimensionamento preservando proporção
    to_tensor             : Conversão para tensor PyTorch (C, H, W)
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

import cv2
import numpy as np


def normalize_image(img: np.ndarray, method: str = "minmax") -> np.ndarray:
    """Normaliza uma imagem odontológica para o intervalo [0, 1].

    Args:
        img: Array 2D (H, W) ou 3D (H, W, C) com valores uint8 ou float
        method: Método de normalização
            - 'minmax': (img - min) / (max - min) -> [0, 1]
            - 'meanstd': (img - mean) / std -> média 0, std 1
            - 'percentile': usa percentis 2 e 98 para robustez

    Returns:
        Imagem normalizada como float32
    """
    img = img.astype(np.float32)
    if method == "minmax":
        vmin, vmax = img.min(), img.max()
        if vmax > vmin:
            return (img - vmin) / (vmax - vmin)
        return np.zeros_like(img, dtype=np.float32)
    elif method == "meanstd":
        mean, std = img.mean(), img.std()
        if std > 0:
            return (img - mean) / std
        return img - mean
    elif method == "percentile":
        p2, p98 = np.percentile(img, (2, 98))
        if p98 > p2:
            img = np.clip(img, p2, p98)
            return (img - p2) / (p98 - p2)
        return np.zeros_like(img, dtype=np.float32)
    else:
        raise ValueError(f"Método desconhecido: {method}. Use 'minmax', 'meanstd' ou 'percentile'.")


def clahe_equalization(img: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int,int] = (8, 8)) -> np.ndarray:
    """Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization) para realçar
    detalhes em radiografias odontológicas.

    CLAHE é especialmente útil para melhorar o contraste de radiografias
    panorâmicas e bitewing, destacando bordas de estruturas dentárias.

    Args:
        img: Imagem 2D (escala de cinza) como array uint8 ou float
        clip_limit: Limite de clipping para evitar amplificação de ruído
        tile_grid_size: Grade de tiles para equalização adaptativa

    Returns:
        Imagem equalizada como uint8
    """
    # Garantir uint8
    if img.dtype != np.uint8:
        if img.max() <= 1.0:
            img = (img * 255).astype(np.uint8)
        else:
            img = img.astype(np.uint8)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(img)


def resize_with_aspect(img: np.ndarray, target_size: Union[int, Tuple[int,int]], pad: bool = True, pad_value: int = 0) -> np.ndarray:
    """Redimensiona uma imagem odontológica preservando a proporção (aspect ratio).

    Importante para radiografias panorâmicas: distorções de proporção podem
    alterar a relação anatômica e levar a classificações incorretas.

    Args:
        img: Imagem de entrada (H, W) ou (H, W, C)
        target_size: Tamanho alvo (int -> square, tuple -> (height, width))
        pad: Se True, preenche com padding para dimensão exata
        pad_value: Valor de preenchimento (0 = preto)

    Returns:
        Imagem redimensionada
    """
    if isinstance(target_size, int):
        target_size = (target_size, target_size)

    h, w = img.shape[:2]
    th, tw = target_size

    # Calcular escala mantendo aspect ratio
    scale = min(th / h, tw / w)
    new_h, new_w = int(h * scale), int(w * scale)

    # Redimensionar
    if len(img.shape) == 2:
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    if pad:
        # Criar canvas e centralizar
        if len(img.shape) == 2:
            canvas = np.full(target_size, pad_value, dtype=img.dtype)
        else:
            canvas = np.full((th, tw, img.shape[2]), pad_value, dtype=img.dtype)

        y_off = (th - new_h) // 2
        x_off = (tw - new_w) // 2
        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
        return canvas

    return resized


def to_tensor(img: np.ndarray) -> "torch.Tensor":
    """Converte uma imagem NumPy (H, W, C) para tensor PyTorch (C, H, W) com
    valores normalizados para [0, 1].

    Compatível com DataLoader do PyTorch para treinamento em batch.

    Args:
        img: Array NumPy (H, W) ou (H, W, C) com dtype uint8 ou float

    Returns:
        Tensor PyTorch formato (C, H, W), dtype float32, range [0, 1]

    Note:
        Requer PyTorch instalado (via `pip install torch` ou ambiente Colab).
    """
    try:
        import torch
    except ImportError:
        raise ImportError(
            "PyTorch não está instalado. Instale com:\n"
            "  pip install torch\n"
            "Ou execute no Google Colab (torch já vem pré-instalado)."
        )

    # Garantir canal
    if len(img.shape) == 2:
        img = np.expand_dims(img, axis=-1)

    # Normalizar e converter HWC -> CHW
    if img.dtype == np.uint8:
        img = img.astype(np.float32) / 255.0
    else:
        img = img.astype(np.float32)

    # (H, W, C) -> (C, H, W)
    tensor = torch.from_numpy(img).permute(2, 0, 1)

    return tensor
