"""
Módulo report — Geração de relatórios de diagnóstico odontológico.

Funções:
    generate_diagnostic_report : Cria relatório formatado com métricas clínicas
"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np


def generate_diagnostic_report(
    model_name: str,
    metrics: Dict[str, float],
    confusion_matrix: Optional[np.ndarray] = None,
    class_names: Optional[List[str]] = None,
    include_recommendation: bool = True,
) -> str:
    """Gera um relatório de diagnóstico odontológico formatado.

    Cria um sumário textual das métricas do modelo, adequado para
    apresentação clínica ou científica.

    Args:
        model_name: Nome do modelo (ex: 'OdontoCNN', 'ResNet50')
        metrics: Dicionário de métricas. Chaves reconhecidas:
            - 'accuracy', 'sensitivity', 'specificity', 'precision',
              'f1', 'auc', 'youden'
        confusion_matrix: Matriz de confusão (opcional)
        class_names: Nomes das classes (opcional)
        include_recommendation: Se True, inclui recomendação baseada nas métricas

    Returns:
        String formatada com o relatório completo

    Example:
        >>> report = generate_diagnostic_report(
        ...     model_name="ResNet50-Finetune",
        ...     metrics={'accuracy': 0.92, 'sensitivity': 0.89, 'specificity': 0.94}
        ... )
        >>> print(report)
    """
    lines = []
    separator = "=" * 60

    # Cabeçalho
    lines.append(separator)
    lines.append(f"RELATÓRIO DE DIAGNÓSTICO ODONTOLÓGICO")
    lines.append(f"Modelo: {model_name}")
    lines.append(separator)

    # Métricas
    lines.append("\n📊 MÉTRICAS CLÍNICAS:")
    lines.append("-" * 40)

    metric_names = {
        "accuracy": "Acurácia",
        "sensitivity": "Sensibilidade",
        "sensibilidade": "Sensibilidade",
        "specificity": "Especificidade",
        "especificidade": "Especificidade",
        "precision": "Precisão (VPP)",
        "precisao_vpp": "Precisão (VPP)",
        "f1_score": "F1-Score",
        "f1": "F1-Score",
        "auc": "AUC-ROC",
        "youden": "Índice de Youden",
    }

    for metric_key, display_name in metric_names.items():
        if metric_key in metrics:
            value = metrics[metric_key]
            if metric_key in ("auc", "youden"):
                lines.append(f"  {display_name:25s}: {value:.4f}")
            else:
                lines.append(f"  {display_name:25s}: {value:.2%}")

    # Matriz de confusão
    if confusion_matrix is not None:
        lines.append("\n📈 MATRIZ DE CONFUSÃO:")
        lines.append("-" * 40)

        if class_names:
            header = " " * 12 + "".join(f"{name:>8}" for name in class_names)
            lines.append(header)
            for i, row in enumerate(confusion_matrix):
                row_label = class_names[i] if class_names else f"C{i}"
                row_str = f"{row_label:10s}" + "".join(f"{val:8d}" for val in row)
                lines.append(row_str)
        else:
            lines.append(str(confusion_matrix))

    # Recomendação
    if include_recommendation:
        lines.append("\n📋 RECOMENDAÇÃO CLÍNICA:")
        lines.append("-" * 40)

        sens = metrics.get("sensibilidade") or metrics.get("sensitivity", 0)
        esp = metrics.get("especificidade") or metrics.get("specificity", 0)

        if sens >= 0.95 and esp >= 0.95:
            recommendation = (
                "Modelo com excelente desempenho clínico. "
                "Pode ser usado como ferramenta auxiliar de diagnóstico "
                "com alta confiança."
            )
        elif sens >= 0.90 and esp >= 0.90:
            recommendation = (
                "Bom desempenho diagnóstico. "
                "Recomenda-se uso como segunda opinião, "
                "especialmente em triagem populacional."
            )
        elif sens >= 0.80:
            recommendation = (
                "Desempenho clínico aceitável. "
                "Recomenda-se supervisão odontológica para todas as predições. "
                "Priorizar sensibilidade para não perder casos positivos."
            )
        else:
            recommendation = (
                "Desempenho clínico abaixo do ideal. "
                "Modelo ainda não apto para uso clínico. "
                "Recomenda-se novo treinamento com mais dados ou ajuste "
                "de hiperparâmetros."
            )

        lines.append(f"  {recommendation}")

    # Rodapé
    lines.append(f"\n{separator}")
    lines.append("Relatório gerado pelo pacote odontoia — Odontologia & IA")
    lines.append(f"{separator}\n")

    return "\n".join(lines)