"""Graphical abstract: single-takeaway summary of the executed clinical analysis.

Encodes only what the manuscript reports. Every number below is taken verbatim
from calibrated_clinical_internal_validation_corrected_sklearn190.json, which was
regenerated against the SHA-256-verified source file; test_06 re-derives them
from that JSON so the figure cannot silently drift from the results.

Layout contract: 1 data unit == 1 inch, so a point size maps to data units as
points/72. Body text is held at >= 7.5 pt because the figure is laid out at
7.25 in wide and the journal will reproduce it close to 1:1. Collision and
containment are asserted by test_graphical_abstract_layout.py.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
STEM = HERE / "Graphical_Abstract"

INK = "#153e5a"
BLUE = "#23618a"
LIGHT_BLUE = "#7fb2d4"
MUTED = "#5b6b76"
RED = "#9c362b"

W, H = 7.25, 4.55
fig, ax = plt.subplots(figsize=(W, H), dpi=400)
fig.patch.set_facecolor("white")
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

PREVALENCE = 0.0833


def box(x, y, w, h, fill, stroke, text, *, fontsize=8.0, ink=INK, weight="normal"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            linewidth=1.25, edgecolor=stroke, facecolor=fill,
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, color=ink, weight=weight, linespacing=1.25)


def arrow(x0, y0, x1, y1, color=BLUE, size=9.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=size, linewidth=1.0, color=color))


def header(y, text, x=0.15, color=BLUE, size=8.5):
    ax.text(x, y, text, fontsize=size, fontweight="bold", color=color, va="center")


# --- title ----------------------------------------------------------------
ax.text(0.15, 4.30, "Tooth-level prediction of early-childhood caries",
        fontsize=13, fontweight="bold", color=INK, va="center")
ax.text(0.15, 4.08,
        "Reproducible internal validation in a public cohort, with patient-separated folds",
        fontsize=9, color=MUTED, va="center")

# --- row 1: cohort reconstruction -----------------------------------------
header(3.78, "COHORT REBUILT FROM THE RELEASED TABLE")

row1 = [
    ("2,504 records\n89 children", "#eef6fc", "#bcd9ec"),
    ("2,284 single-\ntooth rows", "#eef6fc", "#bcd9ec"),
    ("997 transitions\nreconstructed", "#eef6fc", "#bcd9ec"),
    ("996 analysed\n83 events (8.3%)", "#dceaf6", "#7fb2d4"),
]
bw, gap, y1 = 1.60, 0.18, 3.08
for i, (label, fill, stroke) in enumerate(row1):
    x = 0.15 + i * (bw + gap)
    box(x, y1, bw, 0.56, fill, stroke, label, fontsize=8.0)
    if i < len(row1) - 1:
        arrow(x + bw + 0.02, y1 + 0.28, x + bw + gap - 0.02, y1 + 0.28)
ax.text(0.15, 2.92,
        "All 11 prespecified count checks matched the published source.",
        fontsize=7.5, color=MUTED, va="center")

# --- row 2: evaluation design ---------------------------------------------
header(2.74, "EVALUATION DESIGN")

design = [
    "Child is the\ngrouping unit",
    "5 × 3 nested folds\nfixed seed",
    "Penalty chosen\nin inner folds",
    "Recalibration on\ntraining children",
]
bw2, y2 = 1.60, 2.06
for i, label in enumerate(design):
    box(0.15 + i * (bw2 + gap), y2, bw2, 0.54, "#f4f8fb", "#cfe0ec",
        label, fontsize=7.8)
ax.text(0.15, 1.90,
        "Paired child-cluster bootstrap, 1,000 resamples; prevalence reference 0.083 shown dashed.",
        fontsize=7.5, color=MUTED, va="center")

# --- row 3: results -------------------------------------------------------
header(1.72, "INTERNAL RESULTS", color=INK)
header(1.72, "WHAT THIS DOES NOT SHOW", x=3.505, color=INK)

ax.add_patch(FancyBboxPatch(
    (0.15, 0.40), 3.20, 1.20,
    boxstyle="round,pad=0.03,rounding_size=0.08",
    linewidth=1.1, edgecolor="#dbe6ee", facecolor="#fbfdfe", zorder=0))
ax.add_patch(FancyBboxPatch(
    (3.505, 0.40), 1.72, 1.20,
    boxstyle="round,pad=0.04,rounding_size=0.10",
    linewidth=1.25, edgecolor="#a9cfba", facecolor="#eaf4ee"))
ax.add_patch(FancyBboxPatch(
    (5.38, 0.40), 1.72, 1.20,
    boxstyle="round,pad=0.04,rounding_size=0.10",
    linewidth=1.25, edgecolor="#dcc49a", facecolor="#fbf1e6"))

# Denominators live inside the results panel: at 8 pt they no longer fit beside
# the section header, and dropping them would break the denominator chain.
ax.text(0.30, 1.47, "996 transitions  ·  83 events  ·  81 children",
        fontsize=7.5, color=MUTED, va="center", ha="left")

# inset_axes takes axes FRACTIONS, not the data coordinates used everywhere else
_XL, _YL = ax.get_xlim(), ax.get_ylim()
axin = ax.inset_axes(
    [0.42 / _XL[1], 0.44 / _YL[1], 0.88 / _XL[1], 0.60 / _YL[1]]
)
axin.plot([0, 1], [0, 1], ls="--", lw=0.8, color="#c3ccd3")
axin.plot([0, 1], [0, PREVALENCE], ls="--", lw=0.8, color="#d8c9a8")
axin.bar([0.28, 0.70], [0.686, 0.737], width=0.22,
         color=[LIGHT_BLUE, BLUE], zorder=2)
axin.set_xlim(0, 1)
axin.set_ylim(0, 1)
axin.set_xticks([])
axin.set_yticks([0, 0.5, 1])
axin.tick_params(labelsize=7.0, length=2.0, colors=MUTED)
for spine in ("top", "right"):
    axin.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    axin.spines[spine].set_color("#c3ccd3")
    axin.spines[spine].set_linewidth(0.7)
axin.set_title("ROC area", fontsize=7.0, color=INK, pad=2.5)

# Three short lines per model: at 8 pt the single-line metric string no longer
# fits the panel, and abbreviating "average precision" would cost clarity.
for y, (name, roc, ap, colour) in zip(
    (1.24, 0.82),
    (("Minimal clinical", "0.686", "0.166", LIGHT_BLUE),
     ("Clinical + spatial", "0.737", "0.178", BLUE)),
):
    ax.add_patch(FancyBboxPatch(
        (1.42, y - 0.17), 0.06, 0.34,
        boxstyle="square,pad=0", linewidth=0, facecolor=colour))
    ax.text(1.55, y + 0.12, name, fontsize=8.0, color=INK, weight="bold", va="center")
    ax.text(1.55, y, f"ROC area {roc}", fontsize=7.5, color=MUTED, va="center")
    ax.text(1.55, y - 0.12, f"avg. precision {ap}", fontsize=7.5, color=MUTED,
            va="center")

# --- row 4: interpretation -------------------------------------------------
ax.text(3.505 + 1.72 / 2, 1.00, "Discrimination above\nchance,\nbut modest",
        ha="center", va="center", fontsize=8.0, color=INK, linespacing=1.25)
ax.text(5.38 + 1.72 / 2, 1.00,
        "Spatial context did\nnot beat the minimal\nmodel; intervals\nincluded zero",
        ha="center", va="center", fontsize=8.0, color=INK, linespacing=1.25)

# --- conclusion band ------------------------------------------------------
ax.add_patch(FancyBboxPatch(
    (0.15, 0.03), 6.95, 0.30,
    boxstyle="round,pad=0.02,rounding_size=0.06",
    linewidth=1.0, edgecolor="#e3c9c6", facecolor="#fdf4f3"))
ax.text(3.62, 0.18,
        "Both paired model comparisons spanned zero. No decision threshold was derived.\n"
        "Internal and exploratory — external validation is required before clinical use.",
        ha="center", va="center", fontsize=7.5, color=RED, linespacing=1.35)

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
for ext in ("png", "pdf"):
    fig.savefig(f"{STEM}.{ext}", dpi=400, facecolor="white")
plt.close(fig)
print(STEM)
