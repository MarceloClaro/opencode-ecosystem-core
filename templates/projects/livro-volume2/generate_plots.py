#!/usr/bin/env python3
"""
generate_plots.py — Geração de gráficos científicos para o livro.
Uso: python generate_plots.py [--output-dir DIR]
Gera: prony_decay.png, kfold_validation.png, zkp_audit_flow.png
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Configuração ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "images")

def parse_args():
    parser = argparse.ArgumentParser(description="Gera gráficos científicos para o livro Gêmeos Digitais na Odontologia")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT, help="Diretório de saída para as imagens")
    return parser.parse_args()

def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def save_plot(path, name):
    full_path = os.path.join(path, name)
    plt.savefig(full_path, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico salvo: {full_path}")
    plt.close()

# 1. Prony Decay Plot
def plot_prony_decay(output_dir):
    t = np.linspace(0, 10, 200)
    e_0, e_inf, tau = 4.2, 1.2, 1.8
    strain = 0.08
    stress = (e_inf + (e_0 - e_inf) * np.exp(-t / tau)) * strain
    rupture_limit = 4.5

    plt.figure(figsize=(6, 4))
    plt.plot(t, stress, label=r"Estresse do LPD $\sigma(t)$", color="#2563EB", linewidth=2.5)
    plt.axhline(rupture_limit, color="#EF4444", linestyle="--", linewidth=1.5,
                label="Limite de Ruptura (4.5 MPa)")
    plt.axhline(e_inf * strain, color="#059669", linestyle=":", linewidth=1.5,
                label=r"Estresse Residual $\sigma_\infty$ (0.096 MPa)")
    plt.xlabel("Tempo (segundos)", fontsize=10)
    plt.ylabel(r"Tensão $\sigma$ (MPa)", fontsize=10)
    plt.title("Curva de Relaxamento Temporal de Prony no LPD", fontsize=11, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=9)
    save_plot(output_dir, "prony_decay.png")

# 2. K-Fold Cross-Validation Plot
def plot_kfold_validation(output_dir):
    folds = ["Fold 1", "Fold 2", "Fold 3", "Fold 4", "Fold 5"]
    rmse_errors = [0.092, 0.108, 0.085, 0.115, 0.099]
    mean_rmse = np.mean(rmse_errors)
    anvisa_threshold = 0.15

    plt.figure(figsize=(6, 4))
    plt.bar(folds, rmse_errors, color="#10B981", alpha=0.85, edgecolor="#047857",
            width=0.5, label="RMSE por Fold")
    plt.axhline(mean_rmse, color="#F59E0B", linestyle="-.", linewidth=2,
                label=f"RMSE Médio ({mean_rmse:.4f} mm)")
    plt.axhline(anvisa_threshold, color="#EF4444", linestyle="--", linewidth=1.5,
                label="Limite ANVISA (0.150 mm)")
    plt.ylabel("RMSE (mm)", fontsize=10)
    plt.title("Calibração Biomecânica via K-Fold Cross-Validation", fontsize=11, fontweight="bold")
    plt.ylim(0, 0.18)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=9, loc="upper right")
    save_plot(output_dir, "kfold_validation.png")

# 3. ZKP Audit Flow Diagram
def plot_zkp_audit_flow(output_dir):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')

    boxes = [
        {"text": "CNS do Paciente\n(Dados Sensíveis)", "xy": (0.05, 0.4), "w": 0.2, "h": 0.2,
         "color": "#F3F4F6", "edge": "#9CA3AF"},
        {"text": "Salt Secreto\n(SHA-256)", "xy": (0.05, 0.1), "w": 0.2, "h": 0.2,
         "color": "#F3F4F6", "edge": "#9CA3AF"},
        {"text": "CNS Blindado\n(H_cns)", "xy": (0.35, 0.25), "w": 0.2, "h": 0.2,
         "color": "#DBEAFE", "edge": "#3B82F6"},
        {"text": "Desfecho Físico\n(Hash_sim)", "xy": (0.35, 0.55), "w": 0.2, "h": 0.2,
         "color": "#D1FAE5", "edge": "#10B981"},
        {"text": "Compromisso ZKP\n(C_ZKP Signature)", "xy": (0.7, 0.4), "w": 0.25, "h": 0.2,
         "color": "#FEE2E2", "edge": "#EF4444"}
    ]

    for b in boxes:
        rect = plt.Rectangle(b["xy"], b["w"], b["h"], facecolor=b["color"],
                             edgecolor=b["edge"], lw=2)
        ax.add_patch(rect)
        ax.text(b["xy"][0] + b["w"]/2, b["xy"][1] + b["h"]/2, b["text"],
                ha='center', va='center', fontsize=9, fontweight='bold', color="#1F2937")

    arrows = [
        ((0.25, 0.5), (0.35, 0.35)),
        ((0.25, 0.2), (0.35, 0.35)),
        ((0.55, 0.35), (0.7, 0.5)),
        ((0.55, 0.65), (0.7, 0.5))
    ]

    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->", lw=1.5, color="#4B5563"))

    plt.title("Fluxo de Auditoria Criptográfica Sem Perda de Privacidade (ZKP)",
              fontsize=11, fontweight="bold", pad=15)
    save_plot(output_dir, "zkp_audit_flow.png")

if __name__ == "__main__":
    args = parse_args()
    output_dir = ensure_output_dir(args.output_dir)
    print(f"Gerando gráficos em: {output_dir}")
    plot_prony_decay(output_dir)
    plot_kfold_validation(output_dir)
    plot_zkp_audit_flow(output_dir)
    print("✓ Todos os gráficos gerados com sucesso.")
