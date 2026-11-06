"""
Módulo augment — Aumento de dados odontológico.

Fornece transformações realísticas para radiografias dentárias:

    rotate_dental       : Rotação angular limitada (dentes têm orientação preferencial)
    horizontal_flip     : Espelhamento horizontal (simetria natural)
    add_noise           : Ruído gaussiano ou poisson (simula variação de aquisição)
    random_crop_dental  : Corte aleatório com foco em regiões dentais
    dental_pipeline     : Pipeline completo de aumento
"""

from __future__ import annotations

import random
from typing import Callable, List, Optional, Tuple, Union

import cv2
import numpy as np


def rotate_dental(
    img: np.ndarray,
    max_angle: float = 15.0,
    border_value: int = 0,
) -> np.ndarray:
    """Rotaciona a imagem com ângulo limitado para preservar orientação dental.

    Dentes têm orientação anatômica preferencial (raiz para baixo/cima).
    Rotações muito grandes (>30°) geram exemplos não realísticos.

    Args:
        img: Imagem 2D (H, W) ou 3D (H, W, C)
        max_angle: Ângulo máximo de rotação em graus (padrão ±15°)
        label_value: Valor do preenchimento das bordas (0 = preto)

    Returns:
        Imagem rotacionada com mesmo shape da entrada

    Example:
        >>> img = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        >>> img_rot = rotate_dental(img, max_angle=20.0)
    """
    angle = random.uniform(-max_angle, max_angle)
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, scale=1.0)
    # Garante que a imagem inteira fique visível
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)
    M[0, 2] += new_w / 2 - center[0]
    M[1, 2] += new_h / 2 - center[1]
    rotated = cv2.warpAffine(
        img, M, (new_w, new_h), borderValue=border_value
    )

    # Se a rotação criou dimensões muito diferentes, redimensiona de volta
    if len(img.shape) == 2:
        rotated = cv2.resize(rotated, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        rotated = cv2.resize(rotated, (w, h), interpolation=cv2.INTER_LINEAR)

    return rotated


def horizontal_flip(img: np.ndarray, prob: float = 0.5) -> np.ndarray:
    """Aplica espelhamento horizontal com probabilidade definida.

    Radiografias odontológicas frequentemente exibem simetria bilateral,
    tornando o espelhamento horizontal uma transformação realística.

    Args:
        img: Imagem 2D ou 3D
        prob: Probabilidade de aplicar o flip (padrão 0.5)

    Returns:
        Imagem (possivelmente) espelhada horizontalmente

    Example:
        >>> flip_h = horizontal_flip(img, prob=0.5)
    """
    if random.random() < prob:
        return cv2.flip(img, 1)  # flip horizontal
    return img


def add_noise(
    img: np.ndarray,
    noise_type: str = "gaussian",
    intensity: float = 0.05,
) -> np.ndarray:
    """Adiciona ruído realístico a radiografias odontológicas.

    Simula variações de aquisição comuns em aparelhos de raios-X.

    Args:
        img: Imagem uint8 ou float32 no intervalo [0, 255] ou [0, 1]
        noise_type: Tipo de ruído
            - 'gaussian': ruído gaussiano aditivo
            - 'poisson': ruído Poisson (shot noise)
            - 'salt_pepper': ruído sal-e-pimenta (artefatos de sensor)
        intensity: Intensidade do ruído (0.0 a 1.0)
            Para gaussiano: desvio padrão = intensity * 255 (se uint8)
            Para salt_pepper: probability de pixels afetados

    Returns:
        Imagem com ruído adicionado, mesmo dtype da entrada

    Example:
        >>> img = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
        >>> img_noisy = add_noise(img, noise_type='gaussian', intensity=0.1)
    """
    # Converte para float32 para processamento
    is_uint8 = img.dtype == np.uint8
    img_float = img.astype(np.float32)
    max_val = 255.0 if is_uint8 else 1.0

    if noise_type == "gaussian":
        sigma = intensity * 255.0 if is_uint8 else intensity * 255.0
        noise = np.random.normal(0, sigma, img_float.shape).astype(np.float32)
        img_float = img_float + noise

    elif noise_type == "poisson":
        # Ruído Poisson: varia conforme intensidade do sinal
        factor = 1.0 / (intensity * 255.0 + 1e-8)
        scaled = img_float * factor
        noisy = np.random.poisson(np.maximum(scaled, 0)).astype(np.float32)
        img_float = noisy / factor

    elif noise_type == "salt_pepper":
        salt_prob = intensity / 2
        peppper_prob = intensity / 2
        random_mask = np.random.random(img_float.shape)
        img_float[random_mask < salt_prob] = max_val
        img_float[random_mask > 1 - peppper_prob] = 0

    else:
        raise ValueError(f"Tipo de ruído desconhecido: '{noise_type}'")

    # Limit to valid range and cast back
    img_float = np.clip(img_float, 0, max_val)
    return img_float.astype(img.dtype) if is_uint8 else img_float


def random_crop_dental(
    img: np.ndarray,
    crop_size: Union[int, Tuple[int, int]],
    prob: float = 0.3,
    label_value: int = 0,
) -> np.ndarray:
    """Aplica corte aleatório com foco simulado em região dental.

    Útil para simular imagens com diferentes regiões de interesse,
    como segmentos específicos da arcada dentária.

    Args:
        img: Imagem 2D (H, W) ou 3D (H, W, C) uint8 ou float
        crop_size: Tamanho do corte (int para quadrado ou (h, w))
        label_value: Valor para preenchimento das bordas (0 = preto)

    Returns:
        Imagem cortada (possivelmente com bordas)
        Retorna ao tamanho original via redimensionamento

    Example:
        >>> img = np.random.rand(256, 512)
        >>> img_cropped = random_crop_dental(img, crop_size=200, prob=0.7)
    """
    if random.random() >= prob:
        return img

    h, w = img.shape[:2]

    if isinstance(crop_size, int):
        crop_h = crop_w = crop_size
    else:
        crop_h, crop_w = crop_size

    # Garante que o corte não seja maior que a imagem
    crop_h = min(crop_h, h)
    crop_w = min(crop_w, w)

    # Posição aleatória do corte
    y = random.randint(0, h - crop_h) if h > crop_h else 0
    x = random.randint(0, w - crop_w) if w > crop_w else 0

    if len(img.shape) == 2:
        crop = img[y : y + crop_h, x : x + crop_w].copy()
    else:
        crop = img[y : y + crop_h, x : x + crop_w, :].copy()

    # Redimensiona de volta ao tamanho original
    crop = cv2.resize(crop, (w, h), interpolation=cv2.INTER_LINEAR)
    return crop


def augment_pipeline(
    img: np.ndarray,
    augmentations: Optional[List[Callable]] = None,
) -> np.ndarray:
    """Aplica uma pipeline de aumento de dados odontológicos.

    Args:
        img: Imagem odontológica de entrada
        augmentations: Lista de funções de aumento. Se None, usa pipeline
                       padrão: [horizontal_flip, rotate_dental, add_noise]

    Returns:
        Imagem transformada pela pipeline

    Example:
        >>> img_aug = augment_pipeline(img)
        >>> # Pipeline customizada:
        >>> custom = [lambda i: rotate_dental(i, 10), lambda i: add_noise(i, 'poisson', 0.1)]
        >>> img_aug = augment_pipeline(img, custom)
    """
    if augmentations is None:
        augmentations = [
            lambda x: horizontal_flip(x, prob=0.5),
            lambda x: rotate_dental(x, max_angle=15.0),
            lambda x: add_noise(x, noise_type="gaussian", intensity=0.03),
        ]

    augmented = img.copy()
    for aug_fn in augmentations:
        augmented = aug_fn(augmented)

    return augmented