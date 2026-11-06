"""
Subpacote 'visualization' — Visualização e explicabilidade de modelos
para odontologia.

Componentes:
    gradcam : Grad-CAM para mapas de ativação (explicabilidade de CNNs)
    roc     : Curvas ROC para avaliação de diagnóstico
    report  : Geração de relatórios de diagnóstico

Exemplo:
    >>> from odontoia.visualization import plot_gradcam, plot_roc_curve
    >>> plot_gradcam(model, img_tensor, class_idx=1)
"""

from odontoia.visualization.gradcam import plot_gradcam
from odontoia.visualization.roc import plot_roc_curve, find_optimal_threshold
from odontoia.visualization.report import generate_diagnostic_report

__all__ = [
    "plot_gradcam",
    "plot_roc_curve",
    "find_optimal_threshold",
    "generate_diagnostic_report",
]