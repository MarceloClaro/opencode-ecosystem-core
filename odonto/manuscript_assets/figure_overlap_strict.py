#!/usr/bin/env python3
"""Strict overlap audit for the OdontoCA figures (MDPI: characters must not be masked).

Why this exists
---------------
The first detector (`figure_layout_qa.py`) only walked `ax.texts`, so it never
saw tick labels, axis labels, colourbar tick labels, axis titles or the suptitle.
It reported PASS while the rendered PNG still showed overlapping text. This
audit enumerates EVERY text artist in the figure and reports EVERY non-empty
intersection, with no area threshold, measured at the same dpi used for export.

Usage:
    python3 manuscript_assets/figure_overlap_strict.py [--lang=en|pt|both]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_cohort_and_teeth_figures as R  # noqa: E402

EXPORT_DPI = 600


def _text_artists(fig):
    """Every text-bearing artist in the figure, tagged with a readable id."""
    out = []
    seen = set()

    def add(artist, where, label):
        try:
            t = artist.get_text()
        except Exception:
            return
        if t is None or not str(t).strip():
            return
        if not artist.get_visible():
            return
        if id(artist) in seen:      # fig.suptitle lives in fig.texts AND fig._suptitle
            return
        seen.add(id(artist))
        out.append((artist, where, str(t).replace("\n", "⏎")))

    for ax in fig.axes:
        for a in ax.texts:
            add(a, "text", "")
        add(ax.title, "title", "")
        add(ax.xaxis.label, "xlabel", "")
        add(ax.yaxis.label, "ylabel", "")
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            add(lbl, "tick", "")
        leg = ax.get_legend()
        if leg is not None:
            for t in leg.get_texts():
                add(t, "legend", "")
    for t in fig.texts:
        add(t, "suptext", "")
    try:
        add(fig._suptitle, "suptitle", "")
    except Exception:
        pass
    return out


def _boxes(fig, renderer):
    res = []
    for artist, where, label in _text_artists(fig):
        try:
            bb = artist.get_window_extent(renderer)
        except Exception:
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        res.append((bb, where, label))
    return res


def _contains(outer, inner, tol=2.0):
    """True when `inner` lies wholly within `outer` (an intentional container)."""
    return (inner.x0 >= outer.x0 - tol and inner.x1 <= outer.x1 + tol
            and inner.y0 >= outer.y0 - tol and inner.y1 <= outer.y1 + tol)


def _inter(a, b):
    w = min(a.x1, b.x1) - max(a.x0, b.x0)
    h = min(a.y1, b.y1) - max(a.y0, b.y0)
    if w <= 0 or h <= 0:
        return 0.0, 0.0, 0.0
    return w * h, w, h


def _markers(fig, renderer):
    pts = []
    for i, ax in enumerate(fig.axes):
        for coll in ax.collections:
            try:
                offs = coll.get_offsets()
            except Exception:
                continue
            if offs is None or len(offs) == 0:
                continue
            pts.append((i, np.asarray(offs, dtype=float)))
    return pts


def _glyphs(fig):
    """Drawn glyphs (teeth circles and label containers), per axes index."""
    out = []
    for i, ax in enumerate(fig.axes):
        for p in ax.patches:
            out.append((i, p))
    return out


def audit_figure(name: str, fig) -> dict:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    if type(fig.canvas).__name__ == "FigureCanvasBase":
        FigureCanvasAgg(fig)          # captured figures may carry no real canvas
    fig.set_dpi(EXPORT_DPI)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = _boxes(fig, renderer)

    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, wa, la = boxes[i]
            b, wb, lb = boxes[j]
            area, w, h = _inter(a, b)
            if area > 0:
                hits.append((area, w, h, f"[{wa}] {la[:34]!r}", f"[{wb}] {lb[:34]!r}"))

    for bb, wb, lb in boxes:
        for ax_i, patch in _glyphs(fig):
            try:
                pb = patch.get_window_extent(renderer)
            except Exception:
                continue
            if pb.width <= 0 or pb.height <= 0:
                continue
            if type(patch).__name__ == "FancyBboxPatch" and _contains(pb, bb):
                continue      # label sits inside its own container: by design
            area, w, h = _inter(bb, pb)
            if area > 0:
                hits.append((area, w, h, f"[{wb}] {lb[:34]!r}",
                             f"[glifo {type(patch).__name__}] area={area:.1f}px²"))
        for ax_i, offs in _markers(fig, renderer):
            pts = fig.axes[ax_i].transData.transform(offs)
            inside = ((pts[:, 0] >= bb.x0) & (pts[:, 0] <= bb.x1)
                      & (pts[:, 1] >= bb.y0) & (pts[:, 1] <= bb.y1))
            if inside.any():
                hits.append((float(inside.sum()), 0.0, 0.0,
                             f"[{wb}] {lb[:34]!r}",
                             f"{int(inside.sum())} marcador(es) dentro do texto"))
    hits.sort(key=lambda t: -t[0])
    return {"name": name, "n_text": len(boxes), "hits": hits}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="both", choices=["en", "pt", "both"])
    args = ap.parse_args()

    langs = ["en", "pt"] if args.lang == "both" else [args.lang]
    df = R.load()
    failed = False

    for lang in langs:
        R.LANG = lang
        for label, fn in (("fluxograma", lambda d: (None, R.figure_cohort_flow(keep=True)[1])),
                          ("dentes", lambda d: (None, R.figure_teeth(d, keep=True)[1]))):
            _, fig = fn(df)
            rep = audit_figure(f"{label} [{lang}]", fig)
            n = len(rep["hits"])
            print(f"\n=== {rep['name']} ===")
            print(f"  artistas de texto: {rep['n_text']}   sobreposições: {n}")
            if n:
                failed = True
                for area, w, h, a, b in rep["hits"][:25]:
                    print(f"    {area:9.1f} px²  ({w:.1f}x{h:.1f} px)  {a}  X  {b}")
                if n > 25:
                    print(f"    ... +{n - 25} occurrences")
            plt.close(fig)

    print("\n" + "=" * 60)
    print("AUDITORIA ESTRITA: " + ("FALHA — sobreposições presentes" if failed else "PASS"))
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())