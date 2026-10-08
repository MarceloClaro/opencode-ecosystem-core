# -*- coding: utf-8 -*-
"""
figure_layout_qa.py — Detector de sobreposição textual e ilustrativa
======================================================================
MDPI exige, na seção "Preparing Figures, Schemes and Tables":

    "The figure content should be complete and the characters should not
     be masked."

Sobreposição é, portanto, um defeito editorial, não uma questão de gosto.
Este módulo mede as caixas delimitadoras REAIS de cada artista de texto e de
cada marcador, e reporta interseções. Ele não substitui a revisão visual
humana, mas torna a verificação reproduzível e impede regressão silenciosa.

O que é considerado defeito
--------------------------
1. texto ↔ texto           sempre defeito (rótulos nunca devem se cruzar)
2. texto ↔ marcador        defeito quando o texto não é o rótulo do marcador
3. texto ↔ patch          NÃO é defeito quando o texto é o rótulo do próprio
                          contêiner (ex.: nome dentro da sua caixa no fluxograma)

Como os-checkboxes são deliberadamente ignorados
-------------------------------------------------
Um rótulo sentado dentro do seu próprio patch é o comportamento correto. Sem
essa distinção o detector acusaria o fluxograma inteiro como erro.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
from matplotlib.transforms import Bbox

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


@dataclass
class Collision:
    kind: str
    a: str
    b: str
    overlap_px: float
    detail: str = ""


@dataclass
class Report:
    name: str
    collisions: list = field(default_factory=list)
    n_text: int = 0
    n_markers: int = 0

    @property
    def ok(self) -> bool:
        return not self.collisions


def _iter_text(fig):
    """Yield (axes, artist, label) for every visible, non-empty text artist.

    `ax.texts` alone is NOT sufficient: it omits the axes title, the axis
    labels and every legend entry, which are precisely the artists most likely
    to collide with data or with each other. Omitting them would make this
    detector report a clean figure while real masking goes unnoticed.
    """
    for ax in fig.get_axes():
        artists = list(ax.texts)
        # title and axis labels are separate artists, not in ax.texts
        for obj in (ax.title, ax.xaxis.label, ax.yaxis.label):
            if obj is not None and obj.get_text().strip():
                artists.append(obj)
        for getter in ("get_xticklabels", "get_yticklabels"):
            artists += list(getattr(ax, getter)())
        legend = ax.get_legend()
        if legend is not None:
            artists += list(legend.get_texts())
        for t in artists:
            if not t.get_visible():
                continue
            txt = t.get_text()
            if not str(txt).strip():
                continue
            yield ax, t, str(txt)


def text_boxes(fig, renderer):
    out = []
    for ax, t, txt in _iter_text(fig):
        try:
            bb = t.get_window_extent(renderer)
        except Exception:
            continue
        if bb.width <= 1 or bb.height <= 1:
            continue
        out.append((ax, txt, bb))
    return out


def marker_boxes(fig, renderer):
    """Bounding boxes of scatter markers, derived from their point sizes."""
    out = []
    for ax in fig.get_axes():
        dpi = fig.dpi
        for coll in ax.collections:
            try:
                offs = coll.get_offsets()
                sizes = np.atleast_1d(coll.get_sizes()).astype(float)
            except Exception:
                continue
            if offs is None or len(offs) == 0:
                continue
            pts = ax.transData.transform(np.asarray(offs))
            for i, (cx, cy) in enumerate(pts):
                if not (np.isfinite(cx) and np.isfinite(cy)):
                    continue
                s = sizes[i % len(sizes)]
                diameter_px = np.sqrt(s) * (dpi / 72.0)
                half = diameter_px / 2.0
                out.append((ax, f"marker[{i}]", Bbox.from_bounds(cx - half, cy - half,
                                                                 diameter_px, diameter_px)))
    return out


def patch_boxes(fig, renderer):
    """Bounding boxes of circular/elliptical data glyphs.

    Panel (a) of the teeth figure draws each tooth with `ax.add_patch(Circle)`.
    A Circle is a Patch, NOT a Collection, so a detector that looks only at
    `ax.collections` sees no teeth at all and reports a clean figure while the
    numeric labels sit on top of the glyphs. FancyBboxPatch is skipped on
    purpose: in the flow diagram it is the box that *owns* the text inside it,
    and counting it would flag the intended layout as broken.
    """
    from matplotlib.patches import FancyBboxPatch

    out = []
    for ax in fig.get_axes():
        for p in ax.patches:
            if isinstance(p, FancyBboxPatch):
                continue
            try:
                verts = p.get_path().vertices
                pts = p.get_transform().transform(verts)
            except Exception:
                continue
            if len(pts) == 0:
                continue
            x0, y0 = pts.min(axis=0)
            x1, y1 = pts.max(axis=0)
            if not (np.isfinite(x0) and np.isfinite(x1)):
                continue
            out.append((ax, type(p).__name__,
                        Bbox.from_bounds(x0, y0, x1 - x0, y1 - y0)))
    return out


def _intersect(b1: Bbox, b2: Bbox) -> float:
    x0 = max(b1.x0, b2.x0)
    x1 = min(b1.x1, b2.x1)
    y0 = max(b1.y0, b2.y0)
    y1 = min(b1.y1, b2.y1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def analyse(fig, name: str, min_overlap_px: float = 4.0) -> Report:
    """Detect text-text and text-marker collisions in one figure."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = text_boxes(fig, renderer)
    markers = marker_boxes(fig, renderer)
    glyphs = patch_boxes(fig, renderer)
    rep = Report(name=name, n_text=len(texts), n_markers=len(markers) + len(glyphs))

    # 1) texto <-> texto
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            area = _intersect(texts[i][2], texts[j][2])
            if area > min_overlap_px:
                rep.collisions.append(Collision(
                    "texto/texto",
                    texts[i][1][:46], texts[j][1][:46],
                    round(area, 1),
                    f"eixo {texts[i][0]} / {texts[j][0]}"))

    # 2) texto <-> marcador (rótulos numéricos junto aos dentes)
    for ax_t, txt, bb in texts:
        for ax_m, name_m, bb_m in markers:
            if ax_t is not ax_m:
                continue
            area = _intersect(bb, bb_m)
            if area > min_overlap_px:
                rep.collisions.append(Collision(
                    "texto/marcador", txt[:46], name_m, round(area, 1),
                    "rótulo invade o símbolo"))

    # 3) texto <-> glifo circular (o painel (a) desenha dentes com Circle)
    for ax_t, txt, bb in texts:
        for ax_g, name_g, bb_g in glyphs:
            if ax_t is not ax_g:
                continue
            area = _intersect(bb, bb_g)
            if area > min_overlap_px:
                rep.collisions.append(Collision(
                    "texto/glifo", txt[:46], name_g, round(area, 1),
                    "rótulo sobre o glifo do dente"))
    return rep


def report_lines(rep: Report) -> str:
    lines = [f"\n=== {rep.name} ===",
             f"  textos: {rep.n_text}   marcadores: {rep.n_markers}   "
             f"colisões: {len(rep.collisions)}"]
    if rep.ok:
        lines.append("  OK — nenhuma sobreposição detectada acima do limiar.")
    else:
        seen = set()
        for c in rep.collisions:
            key = (c.kind, c.a, c.b)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"  [{c.kind}] {c.a!r} x {c.b!r} "
                         f"= {c.overlap_px} px^2  ({c.detail})")
    return "\n".join(lines)


def audit(output_dir: Path | None = None) -> list:
    """Render both figures in EN and PT and audit each one."""
    import render_cohort_and_teeth_figures as R

    reports = []
    for lang in ("en", "pt"):
        R.LANG = lang
        if lang == "pt":
            R.OUT_FLOW = R.ROOT / "manuscript_assets" / "Figure_cohort_flow_pt.png"
            R.OUT_TEETH = R.ROOT / "manuscript_assets" / "Figure_teeth_training_propagation_pt.png"
        else:
            R.OUT_FLOW = R.ROOT / "manuscript_assets" / "Figure_cohort_flow.png"
            R.OUT_TEETH = R.ROOT / "manuscript_assets" / "Figure_teeth_training_propagation.png"
        df = R.load()
        _, fig = R.figure_cohort_flow(keep=True)
        reports.append(analyse(fig, f"fluxograma da coorte [{lang}]"))
        _, fig = R.figure_teeth(df, keep=True)
        reports.append(analyse(fig, f"dentes e propagação [{lang}]"))
    return reports


def main() -> int:
    reports = audit()
    print("\n".join(report_lines(r) for r in reports))
    total = sum(len(r.collisions) for r in reports)
    print(f"\nTOTAL DE COLISÕES: {total}")
    if total:
        print("MDPI: 'the characters should not be masked' — colisão é defeito.")
        return 1
    print("AUDITORIA DE SOBREPOSIÇÃO: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())