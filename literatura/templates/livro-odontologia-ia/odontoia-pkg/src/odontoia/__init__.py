"""
odontoia — Pacote oficial do livro "Odontologia & Inteligência Artificial"
=======================================================================

Fornece módulos especializados para:

    data            : Carregamento e pré-processamento de dados odontológicos
    sdd             : Specification-Driven Development
    tdd             : Helpers para Test-Driven Development odontológico
    metrics         : Métricas clínicas e estatísticas
    visualization   : Visualização e explicabilidade (Grad-CAM, ROC)
    models          : Modelos de ML/DL para diagnóstico bucal

Uso típico:

    >>> from odontoia.data import load_panoramic
    >>> from odontoia.metrics.classification import accuracy
    >>> from odontoia.sdd import spec

Versão: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Edson Laranjeiras (via OpenCode Ecosystem)"
__license__ = "MIT"

# =============================================================
# Importações lazy (compatíveis com Colab CPU e GPU)
# =============================================================

# Módulos sem dependência de torch (sempre disponíveis)
from odontoia import sdd
from odontoia import tdd

# Módulos com dependências opcionais de deep learning
try:
    from odontoia import data
except ImportError as e:
    _data_import_error = e
    data = None

try:
    from odontoia import metrics
except ImportError as e:
    _metrics_import_error = e
    metrics = None

try:
    from odontoia import visualization
except ImportError as e:
    _visualization_import_error = e
    visualization = None

try:
    from odontoia import models
except ImportError as e:
    _models_import_error = e
    models = None
