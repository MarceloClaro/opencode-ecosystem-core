"""
Prática 13.1 — TDD com DentalTestData para dados odontológicos sintéticos
Usa odontoia.tdd.test_helpers para ciclo Red-Green-Refactor
"""
import numpy as np
from odontoia.tdd.test_helpers import (
    DentalTestData,
    create_test_patient,
    create_test_radiograph,
    generate_periodontal_dataset,
    assert_clinical_metrics,
)


# ============================================================
# RED: Definir o teste ANTES da implementação
# ============================================================
def test_create_test_patient_valid():
    """Verifica se create_test_patient gera dados válidos."""
    patient = create_test_patient("PAC-042", idade=45, fumante=True)
    
    assert patient["patient_id"] == "PAC-042"
    assert patient["idade"] == 45
    assert patient["fumante"] is True
    assert len(patient["dentes"]) > 0
    assert patient["periodontal_stage"] == 0
    print("✅ test_create_test_patient_valid: PASSED")


def test_create_test_radiograph_shape():
    """Verifica dimensões das radiografias sintéticas."""
    data = create_test_radiograph(size=(256, 256), n_classes=3)
    
    assert data.n_samples == 32
    assert data.image_shape == (256, 256)
    assert data.n_classes == 3
    assert data.images.shape == (32, 256, 256)
    assert data.labels.shape == (32,)
    print("✅ test_create_test_radiograph_shape: PASSED")


def test_radiograph_values_range():
    """Valida que os pixels estão no intervalo [0, 255]."""
    data = create_test_radiograph(size=(128, 128), n_classes=2)
    
    assert data.images.min() >= 0, f"Valor mínimo: {data.images.min()}"
    assert data.images.max() <= 255, f"Valor máximo: {data.images.max()}"
    assert data.images.dtype == np.uint8
    print("✅ test_radiograph_values_range: PASSED")


def test_periodontal_dataset_features():
    """Verifica estrutura do dataset periodontal tabular."""
    data = generate_periodontal_dataset(n_samples=100)
    
    assert data.n_samples == 100
    assert data.feature_matrix.shape == (100, 10)
    assert data.feature_names is not None
    assert len(data.feature_names) == 10
    assert "profundidade_sondagem" in data.feature_names
    print("✅ test_periodontal_dataset_features: PASSED")


def test_split_dataset():
    """Testa a divisão treino/teste com split()."""
    data = create_test_radiograph(size=(128, 128), n_classes=2)
    train, test = data.split(test_size=0.3, random_state=42)
    
    assert train.n_samples + test.n_samples == 32
    assert test.n_samples == int(32 * 0.3)
    assert train.n_samples == 32 - test.n_samples
    print("✅ test_split_dataset: PASSED")


def test_assert_clinical_metrics_pass():
    """Testa assert_clinical_metrics com dados perfeitos."""
    y_true = np.array([0, 0, 0, 1, 1, 1])
    y_pred = np.array([0, 0, 0, 1, 1, 1])  # Perfeito
    
    result = assert_clinical_metrics(y_true, y_pred, raise_on_fail=False)
    assert result["approved"] is True
    assert result["accuracy"] == 1.0
    assert result["sensitivity"] == 1.0
    print(f"✅ test_assert_clinical_metrics_pass: acc={result['accuracy']:.3f}")


def test_assert_clinical_metrics_fail():
    """Testa assert_clinical_metrics rejeita métricas ruins."""
    y_true = np.array([0, 0, 0, 1, 1, 1])
    y_pred = np.array([1, 1, 1, 0, 0, 0])  # Totalmente errado
    
    result = assert_clinical_metrics(y_true, y_pred, raise_on_fail=False)
    assert result["approved"] is False
    assert result["accuracy"] == 0.0
    print(f"✅ test_assert_clinical_metrics_fail: approved={result['approved']}")


# ============================================================
# GREEN: Pré-processamento de imagens odontológicas
# ============================================================
def preprocess_dental_image(image, target_size=(224, 224)):
    """
    Função de pré-processamento (a ser implementada no ciclo GREEN).
    """
    import cv2
    
    # Redimensiona
    resized = cv2.resize(image, target_size)
    
    # Normaliza para [0, 1]
    normalized = resized.astype(np.float32) / 255.0
    
    # CLAHE para equalização de histograma (melhora contraste)
    if len(image.shape) == 2:  # Grayscale
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_uint8 = (normalized * 255).astype(np.uint8)
        equalized = clahe.apply(img_uint8)
        normalized = equalized.astype(np.float32) / 255.0
    
    return normalized


def test_preprocess_dental_image():
    """Testa a pipeline de pré-processamento."""
    data = create_test_radiograph(size=(300, 400), n_classes=2)
    img = data.images[0]
    
    processed = preprocess_dental_image(img, target_size=(224, 224))
    
    assert processed.shape == (224, 224)
    assert processed.min() >= 0.0
    assert processed.max() <= 1.0
    assert processed.dtype == np.float32
    print(f"✅ test_preprocess_dental_image: shape={processed.shape}, range=[{processed.min():.3f}, {processed.max():.3f}]")


# ============================================================
# REFACTOR: Melhora sem quebrar testes
# ============================================================
def preprocess_batch(images, target_size=(224, 224)):
    """Versão otimizada para batch de imagens."""
    batch = np.zeros((len(images), *target_size), dtype=np.float32)
    for i, img in enumerate(images):
        batch[i] = preprocess_dental_image(img, target_size)
    return batch


def test_preprocess_batch():
    """Verifica processamento em batch."""
    data = create_test_radiograph(size=(300, 400), n_classes=3)
    
    batch = preprocess_batch(data.images[:8], target_size=(224, 224))
    
    assert batch.shape == (8, 224, 224)
    assert batch.min() >= 0.0
    assert batch.max() <= 1.0
    print(f"✅ test_preprocess_batch: shape={batch.shape}")


# ============================================================
# EXECUÇÃO COMPLETA: RED → GREEN → REFACTOR
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("CICLO TDD: RED → GREEN → REFACTOR")
    print("=" * 60)
    
    # RED: Testes que definem o contrato
    print("\n🔴 RED — Definição dos testes:")
    test_create_test_patient_valid()
    test_create_test_radiograph_shape()
    test_radiograph_values_range()
    test_periodontal_dataset_features()
    test_split_dataset()
    test_assert_clinical_metrics_pass()
    test_assert_clinical_metrics_fail()
    
    # GREEN: Implementação que passa nos testes
    print("\n🟢 GREEN — Implementação:")
    test_preprocess_dental_image()
    
    # REFACTOR: Otimização sem quebrar
    print("\n🔵 REFACTOR — Otimização:")
    test_preprocess_batch()
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
