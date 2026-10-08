# -*- coding: utf-8 -*-
"""
render_cohort_and_teeth_figures.py — Figuras de coorte e de dentes de treino
============================================================================
Gera duas figuras a partir de dados REAIS do pipeline executado:

  Figure_cohort_flow.png
      Fluxograma da coorte (estilo CONSORT) com as 11 verificações de contagem
      reproduzidas do arquivo público verificado.

  Figure_teeth_training_propagation.png
      (a) Gráfico dentário FDI: tamanho do dente = nº de transições usadas no
          treinamento; cor = taxa de propagação H→C observada; contorno
          espesso = "máscara de propagação" (dente com ≥1 evento H→C).
      (b) Mapa espacial dos nichos com a máscara de eventos sobreposta,
          usando as coordenadas x/y reais do arquivo de origem.

ANTI-OVERCLAIM (obrigatório)
---------------------------
Este estudo NÃO contém imagens dentárias, radiografias ou segmentação por
aprendizado profundo. Nenhuma figura aqui simula uma radiografia. O termo
"máscara" refere-se exclusivamente a uma sobreposição binária sobre dados
tabulares/espaciais reais (evento H→C observado). O ramo de imagem do
pipeline não foi executado e nada aqui o representa.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CSV_CANDIDATES = [
    Path("/tmp/OdontoCA_v1_3_5/01_clinical/ca_onset_1step_model.csv"),
    ROOT / "manuscript_assets" / "01_clinical" / "ca_onset_1step_model.csv",
]
OUT_FLOW = ROOT / "manuscript_assets" / "Figure_cohort_flow.png"
OUT_TEETH = ROOT / "manuscript_assets" / "Figure_teeth_training_propagation.png"

# --- camada de idioma ---------------------------------------------------------
# O repositorio usa o sufixo `_pt` para variantes PT-BR (ver
# render_corrected_figures_pt.py). As duas figuras deste script sao
# compartilhadas entre o manuscrito EN e o controle PT-BR, portanto precisam
# de rotulos proprios. Sem isso, o controle PT exibiria texto ingles.
LANG = "en"


def T(text: str) -> str:
    """Translate a figure label according to LANG; identity for English."""
    return PT.get(text, text) if LANG == "pt" else text


def out_flow() -> Path:
    """Destination derived from LANG.

    This used to be a module global set only by main(), so calling
    figure_teeth() directly after `LANG = "pt"` wrote Portuguese content into
    the ENGLISH file and left Figure_*_pt.png stale — both files ended up
    byte-identical (same md5) while the PT control silently showed English.
    """
    name = "Figure_cohort_flow.png" if LANG == "en" else "Figure_cohort_flow_pt.png"
    return ROOT / "manuscript_assets" / name


def out_teeth() -> Path:
    name = ("Figure_teeth_training_propagation.png" if LANG == "en"
            else "Figure_teeth_training_propagation_pt.png")
    return ROOT / "manuscript_assets" / name


PT = {
    # --- fluxograma -----------------------------------------------------------
    "Public worksheet `all_metadata`\n(source study, Table_S1)":
        "Planilha publica `all_metadata`\n(estudo de origem, Table_S1)",
    "downloaded at pinned commit; SHA-256 verified":
        "baixada no commit fixado; SHA-256 verificado",
    "Children in source file": "Criancas no arquivo de origem",
    "unique child identifiers": "identificadores unicos de crianca",
    "Records at composite position T5161": "Registros na posicao composta T5161",
    "not a single tooth; excluded": "nao e um dente individual; excluidos",
    "Single-tooth records": "Registros por dente individual",
    "modelled at tooth level": "modelados no nivel do dente",
    "Observed same-tooth transitions": "Transicoes observadas do mesmo dente",
    "any two recorded consecutive visits": "quaisquer duas consultas consecutivas registradas",
    "Consecutive-index transitions": "Transicoes de indice consecutivo",
    "the notebook's target counts": "contagens-alvo do notebook",
    "Healthy-incidence cohort (state H at t)": "Coorte de incidencia saudavel (estado H em t)",
    "Excluded: follow-up interval of 0 months": "Excluido: intervalo de seguimento de 0 meses",
    "defensible but unquantified; it was an event": "defensavel porem nao quantificado; era um evento",
    "Primary predictive analysis": "Analise preditiva primaria",
    "grouped, child-disjoint nested validation": "validacao aninhada agrupada, disjoint por crianca",
    "Figure A. Cohort derivation from the public source worksheet":
        "Figura A. Derivacao da coorte a partir da planilha publica de origem",
    "Red = exclusion. ": "Vermelho = exclusao. ",
    # --- dentes ---------------------------------------------------------------
    "(a)  Teeth contributing training rows, sized by n and coloured by observed H→C rate":
        "(a)  Dentes que contribuem linhas de treinamento, dimensionados por n e "
        "coloridos pela taxa observada de H→C",
    "propagation\nmask (posterior)": "mascara de\npropagacao (posterior)",
    "Upper primary dentition": "Denticao primaria superior",
    "Lower primary dentition": "Denticao primaria inferior",
    "Circle area is proportional to transitions used in training\n"
    "(r ∝ √n; max n = 122). Beside each tooth: upper number = n\n"
    "(training transitions); lower number = observed H→C events.\n"
    "Heavy red outline = propagation mask (≥1 observed event).\n"
    "All 83 events fell in molars.":
        "A area do circulo e proporcional ao numero de transicoes\n"
        "usadas no treinamento (r ∝ √n; max n = 122). Ao lado de cada dente:\n"
        "numero superior = n (transicoes de treinamento);\n"
        "numero inferior = eventos H→C observados. Contorno vermelho espesso =\n"
        "mascara de propagacao (≥1 evento observado). Todos os 83 eventos\n"
        "ocorreram em molares.",
    "(b)  Observed propagation on the real niche coordinates":
        "(b)  Propagacao observada nas coordenadas reais dos nichos",
    "observed H\u2192C rate": "taxa observada de H\u2192C",
    "Coordinates are the source dataset's own niche x/y values.\n"
    "No radiograph, segmentation model or image branch is represented.":
        "As coordenadas sao os proprios valores x/y de nicho do conjunto de origem.\n"
        "Nenhuma radiografia, modelo de segmentacao ou ramo de imagem esta representado.",
    "Figure B. Training teeth and observed H\u2192C propagation in the OdontoCA analysis cohort "
    "(996 transitions, 83 events, 81 children)":
        "Figura B. Dentes de treinamento e propagacao observada H\u2192C na coorte de analise "
        "do OdontoCA (996 transicoes, 83 eventos, 81 criancas)",
    "events": "eventos",
}

EXPECTED = {"rows": 996, "events": 83, "children": 81}

# Fluxograma: (rótulo, detalhe, n, eventos, é_exclusão)
FLOW = [
    ("Public worksheet `all_metadata`\n(source study, Table_S1)",
     "downloaded at pinned commit; SHA-256 verified", 2504, None, None),
    ("Children in source file", "unique child identifiers", 89, None, None),
    ("Records at composite position T5161", "not a single tooth; excluded", 220, None, True),
    ("Single-tooth records", "modelled at tooth level", 2284, None, None),
    ("Observed same-tooth transitions", "any two recorded consecutive visits", 1388, None, None),
    ("Consecutive-index transitions", "913 H→H · 84 H→C · 163 C→C · 0 C→H", 1160, None, None),
    ("Healthy-incidence cohort (state H at t)", "the notebook's target counts", 997, 84, None),
    ("Excluded: follow-up interval of 0 months",
     "defensible but unquantified; it was an event", 1, 1, True),
    ("Primary predictive analysis", "grouped, child-disjoint nested validation", 996, 83, None),
]


def load() -> pd.DataFrame:
    for c in CSV_CANDIDATES:
        if c.exists():
            df = pd.read_csv(c)
            break
    else:
        raise SystemExit(
            "CSV do pipeline não encontrado. Execute o notebook antes:\n  "
            + "\n  ".join(str(c) for c in CSV_CANDIDATES)
        )
    df = df[df.delta_months > 0]
    got = {"rows": len(df), "events": int(df.progression_event.sum()),
           "children": int(df.child_id.nunique())}
    if got != EXPECTED:
        raise SystemExit(f"FAIL-CLOSED: coorte {got} != {EXPECTED}")
    return df


# ----------------------------------------------------------------- Figura 1
def figure_cohort_flow(keep: bool = False):
    fig, ax = plt.subplots(figsize=(7.4, 9.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(FLOW) * 1.32 + 0.6)
    ax.axis("off")

    y = len(FLOW) * 1.32 + 0.2
    for i, (label, detail, n, ev, excl) in enumerate(FLOW):
        h = 1.0
        color = "#f6f7f9"
        edge = "#2f3e4e"
        if excl:
            color, edge = "#fdecea", "#b3261e"
        elif i == len(FLOW) - 1:  # primary analysis set (last stage)
            color, edge = "#e6f4ea", "#1e7d32"
        ax.add_patch(FancyBboxPatch(
            (0.6, y - h), 8.8, h, boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=color, edgecolor=edge, linewidth=1.6,
        ))
        ax.text(0.85, y - 0.34, T(label), fontsize=8.6, fontweight="bold",
                va="center", color="#12212e")
        ax.text(0.85, y - 0.66, T(detail), fontsize=7.2, va="center",
                color="#4a5a68", style="italic")
        ax.text(6.55, y - 0.5, f"n = {n:,}".replace(",", "."), fontsize=9.4,
                fontweight="bold", va="center", ha="center", color="#12212e")
        if ev is not None:
            ax.text(8.35, y - 0.5, T("events") + f" = {ev}", fontsize=8.2, va="center",
                    ha="center", color="#8a1c15")
        if i < len(FLOW) - 1:
            ax.annotate("", xy=(5.0, y - h - 0.30), xytext=(5.0, y - h - 0.02),
                        arrowprops=dict(arrowstyle="-|>", color="#5b6b7a", lw=1.4))
        y -= 1.32

    ax.text(5.0, len(FLOW) * 1.32 + 0.52,
            T("Figure A. Cohort derivation from the public source worksheet"),
            fontsize=10.2, fontweight="bold", ha="center", color="#12212e")
    ax.text(5.0, 0.16,
            "All 11 pre-specified count checks reproduced exactly (2504 · 89 · 220 · 2284 · "
            "1388 · 1160 · 913 · 84 · 163 · 0 · 997).\nRed = exclusion. "
            "Source: Table_S1.xlsx, SHA-256 b7819fee…84fa.",
            fontsize=6.9, ha="center", color="#4a5a68")
    fig.tight_layout()
    fig.savefig(out_flow(), dpi=600, bbox_inches="tight", facecolor="white")
    if keep:
        return out_flow(), fig
    plt.close(fig)
    return out_flow()


# ----------------------------------------------------------------- Figura 2
def figure_teeth(df: pd.DataFrame, keep: bool = False):
    """Panel (a) anatomically-placed FDI chart; panel (b) real niche coordinates.

    Layout contract (MDPI: "the figure content should be complete and the
    characters should not be masked"):
      * every label is placed with `offset points`, never with a guessed data
        offset, so spacing is independent of font size and of the 600 dpi
        requirement;
      * panel (a) uses aspect="equal", otherwise `Circle` renders as an
        ellipse and the "area proportional to n" encoding becomes a lie;
      * row headers sit outside the tooth band, and panel (b) carries no free
        text inside the plotting area;
      * `constrained_layout` replaces `tight_layout`, which cannot coexist with
        a colorbar and emitted a layout warning.
    """
    agg = (df.groupby(["tooth_fdi", "x", "y"], as_index=False)
             .agg(n=("progression_event", "size"), ev=("progression_event", "sum")))
    agg["rate"] = agg.ev / agg.n
    maxn = agg.n.max()

    # Split the two arches vertically. The offset is 0.44 (0.22 each way):
    # at 0.26 the anterior labels of one arch landed inside the molar circles of
    # the other arch. A geometric sweep of label-box vs circle-box intersections
    # shows 2 residual overlaps at 0.26-0.40 and 0 from 0.44 upward.
    _upper_fdi = [51, 52, 53, 54, 55, 61, 62, 63, 64, 65]
    agg["arc"] = np.where(agg.tooth_fdi.astype(int).isin(_upper_fdi), 1, -1)
    agg["py"] = agg.y + 0.44 * agg["arc"]

    # Mandibular incisors: close the arch downward (corrected layout).
    # In the source coordinates the four incisors sit at py 0.532-0.579, i.e.
    # ABOVE the canines (T83 0.387 / T73 0.380), which renders the lower arch
    # convex and drops the incisors into the space a reader reads as the oral
    # cavity/tongue. Anatomically the mandibular incisors are the most ANTERIOR
    # teeth, so with anterior drawn downward they must dip BELOW the canines and
    # close the arch into a smooth symmetric concave curve.
    # Only py is touched. x keeps the measured lateral spacing, and n/ev are
    # never modified, so circle area stays proportional to n and the panel (b)
    # coordinates are untouched. Applied BEFORE the normal solve below, so the
    # outward label direction is derived from the corrected arch rather than the
    # stale convex one.
    _INCISORS = (82, 81, 71, 72)
    _inc = agg.tooth_fdi.astype(int).isin(_INCISORS)
    # Symmetrise on the PAIRED mean |x|: the raw coordinates are almost but not
    # exactly mirror images (|T82| 0.3233 vs |T72| 0.2840), which would render a
    # visibly lopsided arch. Pairing makes the curve exactly symmetric while
    # leaving each circle on its own measured x.
    _fdi = agg.loc[_inc, "tooth_fdi"].astype(int)
    _t = agg.loc[_inc, "x"].abs()
    _t_lat = float((_t[_fdi.isin((82, 72))]).mean())
    _t_cen = float((_t[_fdi.isin((81, 71))]).mean())
    # py = cy + k*x^2  -> concave up, minimum on the midline.
    # cy 0.160 / k 1.732 puts the lateral incisors at py 0.320, clear below the
    # canines, and the central pair at py 0.175 as the lowest point of the arch.
    _CY, _K = 0.160, 1.732
    agg.loc[_inc, "py"] = np.where(_fdi.isin((81, 71)),
                                   _CY + _K * _t_cen ** 2,
                                   _CY + _K * _t_lat ** 2)

    # Label direction = outward normal of the arch curve, NOT sign(x). Using
    # sign(x) pointed the central-incisor labels at their own arch neighbours
    # (T61 -> T62), because the arch advances in x while moving forward in y.
    # The normal always points away from the arch centroid, i.e. into empty space.
    agg["lx"] = 0.0
    agg["ly"] = 0.0
    for _arc in (1, -1):
        _sub = agg[agg["arc"] == _arc].sort_values("x").reset_index(drop=True)
        _cx, _cy = _sub.x.mean(), _sub.y.mean()
        _P = {int(r.tooth_fdi): (r.x, r.y) for _, r in _sub.iterrows()}
        _O = [int(f) for f in _sub.tooth_fdi]
        for _i, _f in enumerate(_O):
            _pv = _P[_O[_i - 1]] if _i > 0 else None
            _nx = _P[_O[_i + 1]] if _i + 1 < len(_O) else None
            if _pv and _nx:
                _tv = (_nx[0] - _pv[0], _nx[1] - _pv[1])
            elif _nx:
                _tv = (_nx[0] - _P[_f][0], _nx[1] - _P[_f][1])
            else:
                _tv = (_P[_f][0] - _pv[0], _P[_f][1] - _pv[1])
            _L = math.hypot(*_tv)
            _ux, _uy = -_tv[1] / _L, _tv[0] / _L
            if _ux * (_P[_f][0] - _cx) + _uy * (_P[_f][1] - _cy) < 0:
                _ux, _uy = -_ux, -_uy
            agg.loc[agg.tooth_fdi == _f, ["lx", "ly"]] = [_ux, _uy]
    # Exact area-proportional sizing. The legend claims the circle AREA is
    # proportional to the transition count, so the radius must be
    # R_MAX*sqrt(n/maxn). A linear radius makes area ∝ n², and adding a
    # visibility floor R_MIN² makes the area merely affine in n — both would
    # make the legend a false statement about the encoding.
    R_MAX = 0.130
    agg["r"] = R_MAX * np.sqrt(agg.n / maxn)

    # Layout is solved explicitly instead of by constrained_layout: the layout
    # engine re-runs at savefig and rescales the axes AFTER any label offset has
    # been computed, which silently puts labels back on top of the glyphs. With
    # fixed rectangles the geometry used to compute offsets is the geometry that
    # is saved.
    FIG_W, FIG_H = 12.6, 8.8
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    # --- solve the vertical span so every label fits inside the axes box.
    # Labels sit radially outward at (radius + GAP); each column stacks three
    # numbers vertically, so the half-extent perpendicular to the offset is
    # STACK_PT plus half a text line.
    # GAP is expressed in POINTS, not data units. In data units the clearance
    # shrank as the axes grew, so the lowest number of each column ("0") slid
    # back onto the glyph edge; in points the clearance is scale-invariant.
    LINE_PT, GAP_PT = 10.0, 21.0
    STACK_PT = LINE_PT + 3.5            # half-height of the 3-number column, pt
    rect_h = 0.615                       # fraction of figure height
    ax_h_pt = rect_h * FIG_H * 72.0      # axes height in points (fixed)
    _horiz = agg.lx.abs() >= agg.ly.abs()

    def _anchors(ptd):
        gap = GAP_PT * ptd
        return agg.x + agg.lx * (agg.r + gap), agg.py + agg.ly * (agg.r + gap)

    yspan = 1.0
    for _ in range(40):                 # converges because pt_to_data ∝ 1/yspan
        pt_to_data = yspan / ax_h_pt
        _, ay_ = _anchors(pt_to_data)
        ytop = float(ay_.max()) + STACK_PT * pt_to_data + 0.06
        ybot = float(ay_.min()) - STACK_PT * pt_to_data - 0.06
        yspan = ytop - ybot
    pt_to_data = yspan / ax_h_pt
    ax_, ay_ = _anchors(pt_to_data)
    # horizontal span: sideways labels grow outward by their text width
    _out = np.where(_horiz, 0.078, 0.039)
    _xmax = float((ax_ + np.where(ax_ >= 0, _out, -_out)).max())
    _xmin = float((ax_ - np.where(ax_ >= 0, 0.0, _out)).min())
    _xmin = min(_xmin, -float((agg.x - agg.r).min()))
    _xmax = max(_xmax, float((agg.x + agg.r).max()))
    _pad = 0.05
    xspan = (_xmax - _xmin) + 2 * _pad
    xcen = (_xmax + _xmin) / 2

    # rect width must match the data aspect so aspect="equal" never rescales
    rect_w = rect_h * FIG_H / FIG_W * (xspan / yspan)
    ax = fig.add_axes([0.055, 0.235, rect_w, rect_h])
    ax2 = fig.add_axes([0.60, 0.235, 0.30, rect_h])
    cmap = matplotlib.colormaps["YlOrRd"]

    for a in (ax, ax2):
        a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_visible(False)

    ax.set_xlim(xcen - xspan / 2, xcen + xspan / 2)
    ax.set_ylim(ybot, ytop)
    ax.set_aspect("equal")  # a Circle must render as a circle for "area ∝ n"

    def r_of(n):
        return float(R_MAX * math.sqrt(n / maxn))

    for px, py, n, ev, rate in zip(agg.x, agg.py, agg.n, agg.ev, agg.rate):
        ax.add_patch(plt.Circle(
            (px, py), r_of(n), facecolor=cmap(0.10 + 0.85 * rate),
            edgecolor="#8b1a10" if ev > 0 else "#9aa7b2",
            linewidth=2.4 if ev > 0 else 0.9, zorder=3))

    pt_to_data = yspan / ax_h_pt
    # Labels go OUTWARD from the arch axis. Placed above the glyph they ran
    # straight into the next tooth up the arch: neighbouring teeth are only
    # ~0.29 apart while the glyphs are 0.13 in radius. Outward placement puts
    # every label in empty space, deterministically.
    for px, py, n, ev, fdi, ux, uy in zip(
            agg.x, agg.py, agg.n, agg.ev, agg.tooth_fdi, agg.lx, agg.ly):
        off = r_of(n) / pt_to_data + GAP_PT
        dx, dy = ux * off, uy * off
        if abs(ux) >= abs(uy):
            ha, va = ("left" if ux > 0 else "right"), "center"
        else:
            ha, va = "center", "center"
        ax.annotate(f"T{int(fdi)}", (px, py), xytext=(dx, dy + LINE_PT),
                    textcoords="offset points", ha=ha, va=va,
                    fontsize=6.2, color="#5b6b7a", zorder=5)
        ax.annotate(f"{int(n)}", (px, py), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va=va,
                    fontsize=7.4, color="#22303c", fontweight="bold", zorder=5)
        ax.annotate(f"{int(ev)}", (px, py), xytext=(dx, dy - LINE_PT),
                    textcoords="offset points", ha=ha, va=va,
                    fontsize=7.0, zorder=5,
                    color="#8b1a10" if ev > 0 else "#7b8794",
                    fontweight="bold" if ev > 0 else "normal")

    ax.set_title(T("(a)  Teeth contributing training rows, sized by n and coloured by observed H→C rate"),
                 fontsize=9.6, fontweight="bold", loc="left", color="#12212e", pad=13)
    # Arch headers and the decoding note live outside the axes box, so they
    # cannot land on a glyph by construction.
    ax.annotate(T("Upper primary dentition"), xy=(0.5, 1.0), xycoords="axes fraction",
                xytext=(0, 8), textcoords="offset points", ha="center",
                va="bottom", fontsize=9.2, fontweight="bold", color="#12212e",
                annotation_clip=False)
    ax.annotate(T("Lower primary dentition"), xy=(0.5, 0.0), xycoords="axes fraction",
                xytext=(0, -46), textcoords="offset points", ha="center",
                va="top", fontsize=9.2, fontweight="bold", color="#12212e",
                annotation_clip=False)
    # Wrapped by hand: an unwrapped caption forces the tight bbox to the width of
    # its longest line, which made the PT figure 17.0 in wide against 14.8 in for
    # EN — same content, different aspect ratio.
    ax.annotate(T("Circle area is proportional to transitions used in training\n"
                  "(r ∝ √n; max n = 122). Beside each tooth: upper number = n\n"
                  "(training transitions); lower number = observed H→C events.\n"
                  "Heavy red outline = propagation mask (≥1 observed event).\n"
                  "All 83 events fell in molars."),
                xy=(0.5, 0.0), xycoords="axes fraction", xytext=(0, -62),
                textcoords="offset points", ha="center", va="top", fontsize=6.9,
                color="#4a5a68", annotation_clip=False)

    # ---- (b) real niche coordinates ----------------------------------------
    has_ev = df[df.progression_event == 1]
    no_ev = df[df.progression_event == 0]
    ax2.scatter(no_ev.x, no_ev.y, s=16, c="#cfd8de", edgecolors="none",
                label=f"H→H (n = {len(no_ev)})", zorder=2)
    ax2.scatter(has_ev.x, has_ev.y, s=54, c="#c62828", edgecolors="#5d1414",
                linewidths=0.5, alpha=0.92,
                label=f"H→C events (n = {len(has_ev)})", zorder=4)
    cx, cy = has_ev.x.mean(), has_ev.y.mean()
    ax2.add_patch(plt.Circle((cx, cy), 0.40, facecolor="#c62828", alpha=0.10,
                             edgecolor="#c62828", linestyle="--", linewidth=1.5,
                             zorder=3))
    # Label sits outside the plotting area: no free text over the data.
    ax2.annotate(T("dashed envelope = centroid region of observed H→C events"),
                 (cx, cy - 0.40), xytext=(0, -26), textcoords="offset points",
                 ha="center", va="top", fontsize=6.9, color="#8b1a10", zorder=5)
    ax2.set_xlim(-0.95, 0.95)
    ax2.set_ylim(0.10, 1.30)
    ax2.set_title(T("(b)  Observed propagation on the real niche coordinates"),
                  fontsize=9.6, fontweight="bold", loc="left", color="#12212e", pad=10)
    leg = ax2.legend(fontsize=7.2, loc="upper right", frameon=True,
                     framealpha=0.92, edgecolor="#c3ccd4")
    leg.get_frame().set_linewidth(0.6)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, agg.rate.max()))
    cb = fig.colorbar(sm, ax=ax2, fraction=0.045, pad=0.03)
    cb.set_label(T("observed H→C rate"), fontsize=7.6)
    cb.ax.tick_params(labelsize=7)

    fig.suptitle(
        T("Figure B. Training teeth and observed H→C propagation in the OdontoCA analysis cohort "
          "(996 transitions, 83 events, 81 children)"),
        fontsize=10.6, fontweight="bold", color="#12212e")
    png = out_teeth()
    # MDPI accepts vector artwork for line art and requires >=600 dpi for raster.
    # The layout is solved on a 12.6 in working canvas, so the raster is written
    # at that canvas width (600 dpi native, never upscaled); placed at the 5.8 in
    # manuscript column that resolves to ~1300 dpi effective. The vector siblings
    # are resolution-independent and are what removes the pre-check risk.
    fig.savefig(png, dpi=600, bbox_inches="tight", facecolor="white")
    for _ext in ("pdf", "svg"):
        fig.savefig(png.with_name(f"{png.stem}.{_ext}"), bbox_inches="tight",
                    facecolor="white")
    if keep:
        return png, fig
    plt.close(fig)
    return png


def main() -> int:
    global LANG
    if "--lang=pt" in sys.argv or "--pt" in sys.argv:
        LANG = "pt"
    df = load()
    molar = df.tooth_fdi.astype(int).isin([54, 55, 64, 65, 74, 75, 84, 85])
    facts = {
        "rows": int(len(df)),
        "events": int(df.progression_event.sum()),
        "children": int(df.child_id.nunique()),
        "children_with_event": int(df[df.progression_event == 1].child_id.nunique()),
        "molar_rows": int(molar.sum()),
        "molar_events": int(df.loc[molar, "progression_event"].sum()),
        "anterior_rows": int((~molar).sum()),
        "anterior_events": int(df.loc[~molar, "progression_event"].sum()),
    }
    print(json.dumps(facts, indent=2))
    assert facts["anterior_events"] == 0, "anterior events > 0; figure text must change"
    p1 = figure_cohort_flow()
    p2 = figure_teeth(df)
    for p in (p1, p2):
        print(f"gerado[{LANG}]: {p.relative_to(ROOT)}  ({p.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
