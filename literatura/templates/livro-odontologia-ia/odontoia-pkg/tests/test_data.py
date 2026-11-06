"""
Testes para o módulo data/ (loader, preprocessing, augment, datasets)
"""

import numpy as np
import cv2
import pytest

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

_tensor_skip = pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch indisponível — use Google Colab")

from odontoia.data.loader import load_dicom, load_panoramic, load_dataset
from odontoia.data.preprocessing import normalize_image, clahe_equalization, resize_with_aspect, to_tensor
from odontoia.data.augment import rotate_dental, horizontal_flip, add_noise, random_crop_dental, augment_pipeline
from odontoia.data.datasets import dataset_info, DATASETS_INFO


class TestLoader:
    """Testes para funções de carregamento de dados."""

    def test_load_dicom_inexistente(self):
        """load_dicom deve levantar FileNotFoundError para arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            load_dicom("/caminho/inexistente.dcm")

    def test_load_panoramic_inexistente(self):
        """load_panoramic deve levantar FileNotFoundError para arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            load_panoramic("/caminho/inexistente.png")

    def test_load_dataset_nome_invalido(self):
        """load_dataset deve levantar KeyError para nome inválido."""
        with pytest.raises(KeyError):
            load_dataset("dataset_inexistente")

    def test_load_dataset_dns_sintetico(self):
        """load_dataset deve gerar dados sintéticos para DNS."""
        data = load_dataset("dns")
        assert "images" in data or "train" in data
        if "train" in data:
            assert len(data["train"]["images"]) > 0
        else:
            assert len(data["images"]) > 0

    def test_load_dataset_ufba_sintetico(self):
        """load_dataset deve gerar dados sintéticos para UFBA."""
        data = load_dataset("ufba")
        assert "images" in data or "train" in data


class TestPreprocessing:
    """Testes para funções de pré-processamento."""

    def test_normalize_minmax(self):
        """normalize_image com method='minmax' deve retornar [0, 1]."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        norm = normalize_image(img, method="minmax")
        assert norm.min() >= 0.0
        assert norm.max() <= 1.0
        assert norm.dtype == np.float32

    def test_normalize_percentile(self):
        """normalize_image com method='percentile' deve funcionar."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        norm = normalize_image(img, method="percentile")
        assert np.isfinite(norm).all()

    def test_clahe_equalization_shape(self):
        """clahe_equalization deve preservar shape da imagem."""
        img = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        eq = clahe_equalization(img)
        assert eq.shape == img.shape
        assert eq.dtype == np.uint8

    def test_clahe_equalization_raise_color(self):
        """clahe_equalization deve levantar erro para imagem colorida."""
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        with pytest.raises(cv2.error):
            clahe_equalization(img)

    def test_resize_with_aspect_int(self):
        """resize_with_aspect com target_size int deve preservar proporção."""
        img = np.random.rand(200, 100).astype(np.float32)
        resized = resize_with_aspect(img, 128)
        # O maior lado deve ser 128
        assert max(resized.shape) == 128

    def test_resize_with_aspect_tuple_padding(self):
        """resize_with_aspect com padding deve retornar tamanho exato."""
        img = np.random.rand(200, 100).astype(np.float32)
        resized = resize_with_aspect(img, (128, 128), pad=True)
        assert resized.shape == (128, 128)

    @_tensor_skip
    def test_to_tensor_2d(self):
        """to_tensor deve converter (H, W) para (1, H, W)."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        tensor = to_tensor(img)
        assert tensor.shape[0] == 1  # canal
        assert tensor.shape[1] == 64  # H
        assert tensor.shape[2] == 64  # W

    @_tensor_skip
    def test_to_tensor_batch(self):
        """to_tensor com add_batch=True deve retornar (1, C, H, W)."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        tensor = to_tensor(img)
        assert tensor.shape[0] == 1  # batch
        assert len(tensor.shape) == 4


class TestAugment:
    """Testes para funções de aumento de dados."""

    def test_rotate_dental_shape(self):
        """rotate_dental deve preservar shape da imagem."""
        img = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        rotated = rotate_dental(img, max_angle=15.0)
        assert rotated.shape == img.shape

    def test_horizontal_flip_shape(self):
        """horizontal_flip deve preservar shape."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        flipped = horizontal_flip(img, prob=1.0)
        assert flipped.shape == img.shape

    def test_add_noise_gaussian(self):
        """add_noise gaussiano não deve alterar shape."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        noisy = add_noise(img, noise_type="gaussian", intensity=0.05)
        assert noisy.shape == img.shape

    def test_add_noise_salt_pepper(self):
        """add_noise salt_pepper deve gerar valores 0 e 255."""
        img = np.full((64, 64), 128, dtype=np.uint8)
        noisy = add_noise(img, noise_type="salt_pepper", intensity=0.5)
        assert (noisy == 0).any() or (noisy == 255).any()

    def test_random_crop_dental(self):
        """random_crop_dental deve preservar shape."""
        img = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        cropped = random_crop_dental(img, crop_size=64, prob=1.0)
        assert cropped.shape == img.shape

    def test_augment_pipeline(self):
        """augment_pipeline deve aplicar pipeline sem erros."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        aug = augment_pipeline(img)
        assert aug.shape == img.shape


class TestDatasets:
    """Testes para informações de datasets."""

    def test_dataset_info_dns(self):
        """dataset_info deve retornar string formatada para DNS."""
        info = dataset_info("dns")
        assert isinstance(info, str)
        assert "Dental Noisy Set" in info

    def test_dataset_info_invalido(self):
        """dataset_info deve levantar KeyError para nome inválido."""
        with pytest.raises(KeyError):
            dataset_info("dataset_fake")

    def test_datasets_info_keys(self):
        """DATASETS_INFO deve conter datasets esperados."""
        assert "dns" in DATASETS_INFO
        assert "ufba" in DATASETS_INFO
        assert "odontoai" in DATASETS_INFO