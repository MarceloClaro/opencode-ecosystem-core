"""Regenera as Figuras 2–3 em português, usando a mesma análise e predições OOF.

O relatório e as figuras originais em inglês permanecem intactos. A análise
escreve seu JSON temporário fora do repositório e apenas as duas figuras em
português são salvas em manuscript_assets.
"""

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_recall_curve, roc_curve

import calibrated_clinical_prediction as original


HERE = Path(__file__).resolve().parent
REPORT = HERE / "calibrated_clinical_internal_validation_corrected_sklearn190.json"


def decimal(value: float) -> str:
    return f"{value:.3f}".replace(".", ",")


def figures_pt(y: np.ndarray, predictions: dict, metrics: dict) -> None:
    colors = {"clinical_minimal": "#25668c", "clinical_spatial": "#bf7924"}
    labels = {"clinical_minimal": "Clínico mínimo", "clinical_spatial": "Clínico + espacial"}

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=600)
    for name, variants in predictions.items():
        p = variants["uncalibrated"]
        precision, recall, _ = precision_recall_curve(y, p)
        fpr, tpr, _ = roc_curve(y, p)
        axes[0].plot(
            recall, precision,
            label=f"{labels[name]} — Precisão média (AP) {decimal(metrics[name]['uncalibrated']['pr_auc'])}",
            color=colors[name], lw=2,
        )
        axes[1].plot(
            fpr, tpr,
            label=f"{labels[name]} (AUC {decimal(metrics[name]['uncalibrated']['roc_auc'])})",
            color=colors[name], lw=2,
        )
    axes[0].axhline(y.mean(), ls="--", color="#777", label=f"Proporção de eventos {decimal(y.mean())}")
    axes[1].plot([0, 1], [0, 1], ls="--", color="#777", label="Acaso")
    axes[0].set(xlabel="Sensibilidade", ylabel="Precisão", title="A. Precisão–sensibilidade")
    axes[1].set(xlabel="Taxa de falsos positivos", ylabel="Sensibilidade", title="B. Curva ROC")
    for ax in axes:
        ax.legend(fontsize=8)
        ax.grid(alpha=0.15)
        # pin ticks inside xlim; see calibrated_clinical_prediction.py
        ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    fig.tight_layout()
    fig.savefig(HERE / "Figure_2_discrimination_corrected_sklearn190_pt.png", dpi=600, bbox_inches="tight")
    plt.close(fig)

    method_labels = {
        "uncalibrated": "Sem recalibração",
        "intercept_only": "Só intercepto",
        "intercept_and_slope": "Intercepto + inclinação",
    }
    method_colors = {
        "uncalibrated": "#69747c",
        "intercept_only": "#25668c",
        "intercept_and_slope": "#bf7924",
    }
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=600)
    for ax, (name, variants) in zip(axes, predictions.items()):
        ax.plot([0, 0.5], [0, 0.5], ls="--", color="#333", lw=1, label="Ideal")
        for method, p in variants.items():
            original._reliability(ax, y, p, method_labels[method], method_colors[method])
        ax.set(
            xlim=(0, 0.5), ylim=(0, 0.5),
            xlabel="Risco médio previsto",
            ylabel="Proporção observada de eventos",
            title=labels[name],
        )
        ax.grid(alpha=0.15)
        ax.legend(fontsize=7)
        ax.set_xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
        ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    fig.tight_layout()
    fig.savefig(HERE / "Figure_3_calibration_corrected_sklearn190_pt.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    if original.VERSION_TAG != "190":
        raise RuntimeError("Esta versão das figuras exige scikit-learn 1.9.0")
    expected = json.loads(REPORT.read_text(encoding="utf-8"))
    original._figures = figures_pt
    with TemporaryDirectory(prefix="odonto_figures_pt_") as temporary:
        original.OUT = Path(temporary)
        with redirect_stdout(StringIO()):
            actual = original.run()
    if actual["metrics"] != expected["metrics"] or actual["fold_log"] != expected["fold_log"]:
        raise AssertionError("A execução não reproduziu as métricas e dobras auditadas")
    for name in (
        "Figure_2_discrimination_corrected_sklearn190_pt.png",
        "Figure_3_calibration_corrected_sklearn190_pt.png",
    ):
        path = HERE / name
        print(f"{path} ({path.stat().st_size} bytes)")
