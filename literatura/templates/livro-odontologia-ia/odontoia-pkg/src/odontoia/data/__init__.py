"""
Subpacote 'data' — Carregamento e preparação de dados odontológicos.

Componentes:

    loader          : Carregamento de DICOM, radiografias panorâmicas e datasets públicos
    preprocessing   : Normalização, CLAHE, redimensionamento, conversão para tensor
    augment         : Aumento de dados odontológico com transformações realísticas
    datasets        : Informações e metadados sobre datasets públicos (DNS, UFBA, OdontoAI)

Exemplo:

    >>> from odontoia.data import load_panoramic, clahe_equalization
    >>> img = load_panoramic("caminho/para/radiografia.dcm")
    >>> img_eq = clahe_equalization(img)
"""

from odontoia.data.loader import load_dicom, load_panoramic, load_dataset
from odontoia.data.preprocessing import normalize_image, clahe_equalization, resize_with_aspect, to_tensor
from odontoia.data.augment import rotate_dental, horizontal_flip, add_noise, random_crop_dental
from odontoia.data.datasets import DATASETS_INFO, dataset_info, DATASET_LICENSES

# augment_pipeline com alias
augment_pipeline = None
dental_pipeline = None
try:
    from odontoia.data.augment import augment_pipeline as _augment_pipeline
    augment_pipeline = _augment_pipeline
    dental_pipeline = _augment_pipeline
except ImportError:
    pass

__all__ = [
    # loader
    "load_dicom",
    "load_panoramic",
    "load_dataset",
    # preprocessing
    "normalize_image",
    "clahe_equalization",
    "resize_with_aspect",
    "to_tensor",
    # augment
    "rotate_dental",
    "horizontal_flip",
    "add_noise",
    "random_crop_dental",
    "augment_pipeline",
    "dental_pipeline",
    # datasets
    "DATASETS_INFO",
    "dataset_info",
    "DATASET_LICENSES",
]
