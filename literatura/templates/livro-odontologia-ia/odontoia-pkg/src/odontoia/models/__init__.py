"""
Subpacote 'models' — Modelos de aprendizado de máquina para odontologia.

Componentes:
    cnn             : Modelos CNN para classificação de imagens odontológicas
    segmentation    : Arquiteturas de segmentação (U-Net) com métricas Dice/IoU
    detection       : Detecção de objetos (YOLO simplificado)
    dental_ml       : ML clássico para periodontia (dados tabulares)
    digital_twin    : Gêmeos digitais simplificados para planejamento

Exemplo:
    >>> from odontoia.models.cnn import build_simple_cnn
    >>> model = build_simple_cnn(input_shape=(256, 256, 1), n_classes=3)
"""

from odontoia.models.dental_ml import (
    train_periodontal_classifier,
    periodontal_feature_importance,
    predict_periodontal_staging,
)

# Módulos com dependência opcional de PyTorch
try:
    from odontoia.models.cnn import build_simple_cnn, build_resnet50_finetune, predict_with_explanation
except ImportError:
    build_simple_cnn = None
    build_resnet50_finetune = None
    predict_with_explanation = None

try:
    from odontoia.models.segmentation import build_unet, dice_coef, iou_score
except ImportError:
    build_unet = None
    dice_coef = None
    iou_score = None

try:
    from odontoia.models.detection import build_simple_yolo, non_max_suppression
except ImportError:
    build_simple_yolo = None
    non_max_suppression = None

try:
    from odontoia.models.digital_twin import (
        DentalTwin,
        ToothState,
        build_twin_encoder,
        estimate_intervention,
    )
except ImportError:
    DentalTwin = None
    ToothState = None
    build_twin_encoder = None
    estimate_intervention = None

__all__ = [
    # cnn
    "build_simple_cnn",
    "build_resnet50_finetune",
    "predict_with_explanation",
    # segmentation
    "build_unet",
    "dice_coef",
    "iou_score",
    # detection
    "build_simple_yolo",
    "non_max_suppression",
    # dental_ml
    "train_periodontal_classifier",
    "periodontal_feature_importance",
    "predict_periodontal_staging",
    # digital_twin
    "DentalTwin",
    "build_twin_encoder",
    "estimate_intervention",
    "ToothState",
]
