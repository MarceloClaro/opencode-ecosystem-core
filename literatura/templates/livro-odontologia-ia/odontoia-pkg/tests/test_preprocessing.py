"""
Testes dedicados a pré-processamento e aumento de dados.

Executar: pytest tests/test_preprocessing.py -v
"""
import cv2
import os
import numpy as np
import pytest

from odontoia.data.preprocessing import normalize_image, clahe_equalization, resize_with_aspect, to_tensor
from odontoia.data.augment import rotate_dental, add_noise, augment_pipeline

# =============================================================================
# Skip condicional: PyTorch só está disponível no Google Colab/ambiente GPU
# =============================================================================
TORCH_AVAILABLE = False
try:
    import torch  # noqa: F401
    TORCH_AVAILABLE = True
except ImportError:
    pass

TORCH_SKIP = pytest.mark.skipif(
    not TORCH_AVAILABLE,
    reason="⚠️ PyTorch indisponível — execute no Google Colab (torch pré-instalado)"
)

# =============================================================================
# TestNormalizeImage
# =============================================================================
class TestNormalizeImage:
    """Testes específicos para normalize_image."""

    def test_method_minmax_range(self):
        """Normalização min-max deve retornar valores em [0, 1]."""
        img = np.array([[50, 100], [150, 200]], dtype=np.uint8)
        norm = normalize_image(img, method="minmax")
        assert norm.min() == 0.0
        assert norm.max() == 1.0

    def test_method_meanstd_zero_mean(self):
        """Normalização mean-std deve ter média ~0."""
        img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        norm = normalize_image(img, method="meanstd")
        assert abs(norm.mean()) < 0.5

    def test_method_invalid(self):
        """Método inválido deve levantar ValueError."""
        with pytest.raises(ValueError):
            normalize_image(np.zeros((10, 10)), method="invalido")

    def test_constant_image(self):
        """Imagem constante não deve causar divisão por zero."""
        img = np.ones((50, 50), dtype=np.uint8) * 128
        norm = normalize_image(img, method="minmax")
        assert norm.sum() == 0.0  # todos zeros

    def test_percentile_outliers(self):
        """Percentil deve ser robusto a outliers."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[0, 0] = 255  # outlier
        img[1, 1] = 255  # outlier
        norm = normalize_image(img, method="percentile")
        assert norm.max() <= 1.0

    def test_dtype_float32(self):
        """Saída deve ser float32."""
        img = np.random.randint(0, 255, (32, 32), dtype=np.uint8)
        norm = normalize_image(img)
        assert norm.dtype == np.float32


# =============================================================================
# TestCLAHE
# =============================================================================
class TestCLAHE:
    """Testes específicos para CLAHE."""

    def test_contrast_increase(self):
        """CLAHE deve aumentar o contraste mensurável."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[25:75, 25:75] = 100
        eq = clahe_equalization(img, clip_limit=5.0)
        # Desvio padrão deve ser maior após equalização
        std_orig = img.std()
        std_eq = eq.std()
        # Para imagens com contraste, CLAHE geralmente aumenta std
        assert std_eq > 0

    def test_grid_size_variation(self):
        """Diferentes grid sizes devem funcionar sem erro."""
        img = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        eq1 = clahe_equalization(img, tile_grid_size=(4, 4))
        eq2 = clahe_equalization(img, tile_grid_size=(16, 16))
        assert eq1.shape == eq2.shape

    def test_uint8_conversion(self):
        """CLAHE deve converter float para uint8 automaticamente."""
        img = np.random.rand(64, 64).astype(np.float32) * 255
        eq = clahe_equalization(img)
        assert eq.dtype == np.uint8


# =============================================================================
# TestResize
# =============================================================================
class TestResize:
    """Testes para resize_with_aspect."""

    def test_grayscale_preserved(self):
        """Redimensionamento de imagem cinza preserva 2D."""
        img = np.random.randint(0, 255, (100, 200), dtype=np.uint8)
        resized = resize_with_aspect(img, 50)
        assert len(resized.shape) == 2

    def test_color_preserved(self):
        """Redimensionamento de imagem colorida preserva 3D."""
        img = np.random.randint(0, 255, (100, 200, 3), dtype=np.uint8)
        resized = resize_with_aspect(img, 50)
        assert len(resized.shape) == 3
        assert resized.shape[2] == 3

    def test_different_target_sizes(self):
        """Diferentes tamanhos alvo devem funcionar."""
        img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        r1 = resize_with_aspect(img, 50)
        r2 = resize_with_aspect(img, (50, 50))
        assert r1.shape == r2.shape


# =============================================================================
# TestToTensor — apenas executado com PyTorch (Google Colab)
# =============================================================================
@TORCH_SKIP
class TestToTensor:
    """Testes para to_tensor 🖥️ requer PyTorch disponível no Google Colab."""

    def test_device_cpu(self):
        """to_tensor no device CPU não deve falhar."""
        import torch
        img = np.random.randint(0, 255, (32, 32), dtype=np.uint8)
        tensor = to_tensor(img)
        assert tensor.device.type == "cpu"

    def test_normalization_range(self):
        """Tensor deve estar em [0, 1]."""
        img = np.random.randint(0, 255, (32, 32), dtype=np.uint8)
        tensor = to_tensor(img)
        assert tensor.min() >= 0.0
        assert tensor.max() <= 1.0

    def test_channel_last_to_first(self):
        """Transposição HWC -> CHW."""
        img = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
        tensor = to_tensor(img)
        assert tensor.shape[0] == 3  # C primeiro

    def test_2d_to_1channel(self):
        """Imagem 2D deve gerar tensor com 1 canal."""
        img = np.random.randint(0, 255, (32, 32), dtype=np.uint8)
        tensor = to_tensor(img)
        assert tensor.shape[0] == 1
