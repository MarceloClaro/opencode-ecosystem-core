#!/usr/bin/env python3
"""Teste TDD para verificação do ambiente.
Capítulo 1 — Prática 1.1.
"""

import unittest
import sys
import importlib


class TestSetupAmbiente(unittest.TestCase):
    """Testes para verificar o ambiente de desenvolvimento."""

    def test_python_version(self):
        """Verifica que Python >= 3.9 está instalado."""
        major, minor, *_ = sys.version_info
        self.assertGreaterEqual(major, 3)
        self.assertGreaterEqual(minor, 9)

    def test_numpy_installed(self):
        """Numpy deve estar instalada."""
        import numpy as np
        self.assertTrue(hasattr(np, "__version__"))

    def test_tensorflow_installed(self):
        """TensorFlow deve estar instalado."""
        import tensorflow as tf
        self.assertTrue(hasattr(tf, "__version__"))

    def test_torch_installed(self):
        """PyTorch deve estar instalado."""
        import torch
        self.assertTrue(hasattr(torch, "__version__"))

    def test_opencv_installed(self):
        """OpenCV deve estar instalado."""
        import cv2
        self.assertTrue(hasattr(cv2, "__version__"))

    def test_sklearn_installed(self):
        """Scikit-learn deve estar instalado."""
        import sklearn
        self.assertTrue(hasattr(sklearn, "__version__"))

    def test_matplotlib_installed(self):
        """Matplotlib deve estar instalado."""
        import matplotlib
        self.assertTrue(hasattr(matplotlib, "__version__"))

    def test_pandas_installed(self):
        """Pandas deve estar instalado."""
        import pandas as pd
        self.assertTrue(hasattr(pd, "__version__"))

    def test_pillow_installed(self):
        """Pillow deve estar instalado."""
        from PIL import Image
        self.assertTrue(hasattr(Image, "open"))


if __name__ == "__main__":
    unittest.main(verbosity=2)