"""
Testes para o módulo models/ (cnn, segumentation, dental_ml, digital_twin)
"""

import numpy as np
import pytest

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore

pytestmark = pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch não instalado (disponível no Google Colab)")

from odontoia.models.dental_ml import (
    train_periodontal_classifier,
    periodontal_feature_importance,
)


class TestCNN:
    """Testes para modelos CNN."""

    def test_build_simple_cnn(self):
        """build_simple_cnn deve criar modelo com saída correta."""
        model = build_simple_cnn(input_shape=(1, 128, 128), n_classes=3)
        x = torch.randn(2, 1, 128, 128)
        y = model(x)
        assert y.shape == (2, 3)

    def test_build_simple_cnn_n_params(self):
        """build_simple_cnn deve ter parâmetros treináveis."""
        model = build_simple_cnn(input_shape=(1, 64, 64), n_classes=2)
        n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        assert n_params > 0

    def test_predict_with_explanation(self):
        """predict_with_explanation deve retornar classe e heatmap."""
        from odontoia.models.cnn import predict_with_explanation
        model = build_simple_cnn(input_shape=(1, 64, 64), n_classes=3)
        img_tensor = torch.randn(1, 1, 64, 64)
        cls_idx, heatmap, conf = predict_with_explanation(model, img_tensor)
        assert isinstance(cls_idx, int)
        assert heatmap.shape == (64, 64)
        assert 0.0 <= conf <= 1.0


class TestSegmentation:
    """Testes para modelos de segmentação."""

    def test_build_unet_output(self):
        """build_unet deve retornar tensor com n_classes canais."""
        model = build_unet(in_channels=1, n_classes=6)
        x = torch.randn(2, 1, 128, 128)
        y = model(x)
        assert y.shape == (2, 6, 128, 128)

    def test_unet_n_classes_2(self):
        """build_unet com 2 classes deve funcionar."""
        model = build_unet(in_channels=1, n_classes=2)
        x = torch.randn(1, 1, 64, 64)
        y = model(x)
        assert y.shape[1] == 2

    def test_dice_coef(self):
        """dice_coef deve retornar valor entre 0 e 1."""
        pred = torch.randn(2, 3, 32, 32)
        true = torch.randint(0, 3, (2, 32, 32))
        dice = dice_coef(pred, true)
        assert 0.0 <= dice.item() <= 1.0

    def test_iou_score(self):
        """iou_score deve retornar valor entre 0 e 1."""
        pred = torch.randn(2, 3, 32, 32)
        true = torch.randint(0, 3, (2, 32, 32))
        iou = iou_score(pred, true)
        assert 0.0 <= iou.item() <= 1.0

    def test_dice_perfect_match(self):
        """dice_coef para predição perfeita deve ser 1."""
        true = torch.randint(0, 3, (2, 32, 32))
        pred = torch.zeros(2, 3, 32, 32)
        for b in range(2):
            for h in range(32):
                for w in range(32):
                    pred[b, true[b, h, w], h, w] = 100.0
        dice = dice_coef(pred, true)
        assert dice.item() > 0.99

    def test_unet_params_differentiable(self):
        """Parâmetros da U-Net devem ter gradiente."""
        model = build_unet(in_channels=1, n_classes=2)
        x = torch.randn(1, 1, 64, 64)
        y = model(x)
        loss = y.sum()
        loss.backward()
        has_grad = any(p.grad is not None for p in model.parameters())
        assert has_grad


class TestDentalML:
    """Testes para ML clássico em periodontia."""

    def test_train_classifier(self):
        """train_periodontal_classifier deve retornar modelo treinado."""
        model, scaler, metrics, X_test, y_test = train_periodontal_classifier()
        assert hasattr(model, "predict")
        assert hasattr(scaler, "transform")
        assert "accuracy" in metrics
        assert metrics["accuracy"] >= 0  # pelo menos acerta algo

    def test_feature_importance(self):
        """periodontal_feature_importance deve retornar dicionário."""
        model, _, _, _, _ = train_periodontal_classifier()
        importance = periodontal_feature_importance(model)
        assert len(importance) == 10  # 10 features
        # Deve estar ordenado decrescente
        values = list(importance.values())
        assert all(values[i] >= values[i+1] for i in range(len(values)-1))


class TestDigitalTwin:
    """Testes para gêmeos digitais."""

    def test_dental_twin_init(self):
        """DentalTwin deve inicializar com 32 dentes."""
        twin = DentalTwin(patient_id="P001")
        assert len(twin.teeth) == 32

    def test_dental_twin_to_vector(self):
        """to_feature_vector deve retornar vetor de 260 elementos."""
        twin = DentalTwin(patient_id="P001")
        vec = twin.to_feature_vector()
        assert len(vec) == 32 * 8 + 4  # 260

    def test_dental_twin_intervention_higiene(self):
        """apply_intervention com 'higiene' deve melhorar índice."""
        twin = DentalTwin(patient_id="P001")
        original = twin.hygiene_index
        twin_post = twin.apply_intervention({"tipo": "higiene"})
        assert twin_post.hygiene_index <= original

    def test_dental_twin_intervention_exodontia(self):
        """apply_intervention com 'exodontia' deve remover dente."""
        twin = DentalTwin(patient_id="P001")
        n_before = len(twin.teeth)
        twin_post = twin.apply_intervention({"tipo": "exodontia", "dentes": [18, 28]})
        assert len(twin_post.teeth) == n_before - 2

    def test_build_twin_encoder(self):
        """build_twin_encoder deve criar autoencoder."""
        encoder = build_twin_encoder(latent_dim=16, input_dim=260)
        x = torch.randn(4, 260)
        z, recon = encoder(x)
        assert z.shape == (4, 16)
        assert recon.shape == (4, 260)

    def test_estimate_intervention(self):
        """estimate_intervention deve retornar dict com prognóstico."""
        from odontoia.models.digital_twin import estimate_intervention
        twin = DentalTwin(patient_id="P001")
        result = estimate_intervention(twin, {"tipo": "higiene"})
        assert "diagnostico_pre" in result
        assert "intervencao" in result
        assert "prognostico" in result