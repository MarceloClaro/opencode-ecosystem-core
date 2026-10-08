"""Render a journal-width evidence workflow, independent of the detailed Mermaid."""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


HERE = Path(__file__).resolve().parent
STEM = HERE / "Figure_1_pipeline_v2_compact"

fig, ax = plt.subplots(figsize=(7.25, 5.8), dpi=600)
fig.patch.set_facecolor("white")
ax.set_xlim(0, 7.25)
ax.set_ylim(0, 5.8)
ax.axis("off")

PALETTE = {
    "done": ("#e8f3fb", "#23618a", "#153e5a"),
    "pending": ("#fff8e9", "#a77920", "#6b4b13"),
    "gate": ("#f2edf9", "#775497", "#443056"),
    "block": ("#fbece9", "#b23e34", "#742921"),
    "report": ("#e8f5ec", "#327354", "#25533d"),
}


def box(x, y, w, h, label, kind, fontsize=7.35):
    fill, stroke, ink = PALETTE[kind]
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.045,rounding_size=0.105",
        linewidth=1.3, edgecolor=stroke, facecolor=fill,
        linestyle="--" if kind == "pending" else "-",
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color=ink, fontfamily="DejaVu Sans",
            linespacing=1.2)


def arrow(x0, y0, x1, y1, color="#73869a", size=8.5):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                 arrowstyle="-|>", mutation_scale=size,
                                 linewidth=0.9, color=color))


ax.text(0.15, 5.57, "OdontoCA | Research workflow and evidence gates",
        fontsize=11.2, fontweight="bold", color="#173e57", va="center")
ax.text(0.15, 5.28,
        "Solid blue: executed analysis    Dashed amber: proposed / not run",
        fontsize=7.5, color="#4e5e68", va="center")

labels = [
    ("A  CI_SMOKE", "EXECUTED", 4.35, "done", [
        "Synthetic\ntooth + ASV data",
        "Consecutive\nH → C transitions",
        "Child-grouped\nnested CV",
        "OOF metrics:\ntechnical only",
    ]),
    ("B  CLINICAL", "INTERNAL ONLY", 3.39, "done", [
        "Public Table S1\nsource + checksum",
        "Reproduce cohort\nand onset counts",
        "Corrected child\nnested CV",
        "Train-only calibration;\nOOF + child CI",
    ]),
    ("C  MICROBIOME", "NOT RUN", 2.43, "pending", [
        "Qiita / BIOM\nsource + mapping",
        "Exact SampleID\nand library QC",
        "Train-fold ASV,\nCLR, scaling, PCA",
        "Real OOF model\nand uncertainty",
    ]),
    ("D  IMAGE", "NOT RUN", 1.47, "pending", [
        "Images, labels\nand provenance",
        "Patient split +\nduplicate audit",
        "Validation tuning;\nheld-out test",
        "FDI mapping +\nclinician review",
    ]),
]

box_x, bw, gap, bh = 1.46, 1.24, 0.18, 0.63
for title, status, y, style, steps in labels:
    ax.text(0.14, y + 0.39, title, fontsize=8.2, fontweight="bold",
            color="#173e57" if style == "done" else "#755013", va="center")
    ax.text(0.14, y + 0.16, status, fontsize=6.8,
            color="#23618a" if style == "done" else "#a77920", va="center")
    for i, step in enumerate(steps):
        x = box_x + i * (bw + gap)
        box(x, y, bw, bh, step, style)
        if i < len(steps) - 1:
            arrow(x + bw + 0.01, y + bh / 2,
                  x + bw + gap - 0.01, y + bh / 2,
                  "#23618a" if style == "done" else "#a77920")

ax.text(0.15, 1.13, "GATES BEFORE MULTIMODAL OR CLINICAL CLAIMS",
        fontsize=8.2, fontweight="bold", color="#443056", va="center")
gate_y, gate_h = 0.43, 0.57
box(0.18, gate_y, 2.13, gate_h,
    "Fusion only for the same cohort\nand patient + visit + tooth", "gate", 7.3)
box(2.58, gate_y, 2.10, gate_h,
    "Independent external validation\nand measured calibration", "gate", 7.3)
box(4.95, gate_y, 2.12, gate_h,
    "Manuscript labels synthetic,\ninternal and external evidence", "report", 7.3)
arrow(2.32, gate_y + gate_h / 2, 2.56, gate_y + gate_h / 2, "#775497")
arrow(4.69, gate_y + gate_h / 2, 4.93, gate_y + gate_h / 2, "#775497")
ax.text(0.15, 0.15,
        "Synthetic results do not estimate clinical performance; unmatched datasets remain separate.",
        fontsize=7.2, color="#6b3c2c", va="center")

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
for ext in ("png", "svg", "pdf"):
    fig.savefig(f"{STEM}.{ext}", dpi=600, facecolor="white")
plt.close(fig)
