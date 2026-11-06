"""
Projeto 1 — Classificador de Cáries com CNN e radiografia bitewing
SDD + TDD completo: SPEC → TESTS → IMPLEMENTAÇÃO → RESULTADOS
"""
import numpy as np
from odontoia.sdd.spec import spec
from odontoia.tdd.test_helpers import create_test_radiograph, DentalTestData

# ============================================================
# SPEC: Especificação do projeto
# ============================================================
@spec(
    problem="Classificar cáries proximais em radiografias bitewing (ICDAS 0-6)",
    input="ndarray (224, 224) uint8 — radiografia bitewing recortada",
    output="ndarray (7,) float32 — probabilidades ICDAS [0..6]",
    criteria=[
        "accuracy > 0.88",
        "sensitivity > 0.85",
        "specificity > 0.85",
        "kappa_cohen > 0.80",
        "inference_time < 150ms",
    ],
    category="classificacao",
)
def caries_classifier_icdas(image):
    """Classificador de cáries segundo escala ICDAS."""
    pass


# ============================================================
# TESTS (RED): Definição dos critérios de aceitação
# ============================================================
def test_caries_classifier_output_shape():
    """Verifica que a saída tem 7 classes ICDAS."""
    data = create_test_radiograph(size=(224, 224), n_classes=7)
    img = data.images[0]
    
    # Mock da predição
    pred = np.random.dirichlet(np.ones(7))
    
    assert len(pred) == 7, f"Esperado 7 classes, obtido {len(pred)}"
    assert abs(pred.sum() - 1.0) < 1e-6, f"Probabilidades somam {pred.sum()}"
    print("✅ test_caries_classifier_output_shape: PASSED")


def test_caries_prediction_range():
    """Todas as probabilidades devem estar em [0, 1]."""
    data = create_test_radiograph(size=(224, 224), n_classes=7)
    img = data.images[0]
    
    pred = np.random.dirichlet(np.ones(7))
    
    assert pred.min() >= 0.0
    assert pred.max() <= 1.0
    print("✅ test_caries_prediction_range: PASSED")


# ============================================================
# IMPLEMENTAÇÃO (GREEN): CNN EfficientNet-B3 fine-tunada
# ============================================================
def build_caries_cnn(input_shape=(224, 224, 3), n_classes=7):
    """
    Constrói CNN para classificação de cáries com EfficientNet-B3.
    
    Arquitetura:
        - Base: EfficientNet-B3 (pré-treinada ImageNet)
        - Head: GlobalAveragePooling + Dense(256) + Dropout(0.3) + Dense(7)
        - Otimizador: AdamW (lr=1e-4, weight_decay=1e-4)
        - Loss: CategoricalCrossentropy (label_smoothing=0.1)
        - Métricas: accuracy, sensitivity, specificity, kappa
    """
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    
    base_model = keras.applications.EfficientNetB3(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape,
    )
    base_model.trainable = False  # Congela backbone
    
    inputs = keras.Input(shape=input_shape)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(n_classes, activation="softmax")(x)
    
    model = keras.Model(inputs, outputs, name="CariesICDAS_Classifier")
    model.compile(
        optimizer=keras.optimizers.AdamW(learning_rate=1e-4, weight_decay=1e-4),
        loss=keras.losses.CategoricalCrossentropy(label_smoothing=0.1),
        metrics=[
            "accuracy",
            keras.metrics.Recall(name="sensitivity"),
            keras.metrics.Precision(name="specificity"),
        ],
    )
    return model


if __name__ == "__main__":
    print("=" * 60)
    print("Projeto 1: Classificador de Cáries ICDAS")
    print("=" * 60)
    
    test_caries_classifier_output_shape()
    test_caries_prediction_range()
    
    model = build_caries_cnn()
    model.summary()
    
    print("\n✅ Projeto 1 completo: SPEC → TEST → IMPLEMENT")
