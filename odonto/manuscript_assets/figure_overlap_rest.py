#!/usr/bin/env python3
"""Overlap audit for the three manuscript figures that were never audited.

`figure_overlap_strict.py` covers the cohort flowchart and the teeth chart.
The manuscript also embeds:

    Figure_1_pipeline_v2_compact.png           (render_pipeline_v2_compact.py)
    Figure_2_discrimination_corrected_sklearn190.png
    Figure_3_calibration_corrected_sklearn190.png   (calibrated_clinical_prediction.py)

Neither generator exposes its Figure, so this script captures them by
temporarily wrapping `Figure.savefig` and reuses the strict audit.

Usage:  python3 manuscript_assets/figure_overlap_rest.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import figure_overlap_strict as S  # noqa: E402

CAPTURED: list[Figure] = []
_real_savefig = Figure.savefig


def _capture(self, *a, **k):
    CAPTURED.append(self)
    return _real_savefig(self, *a, **k)


def main() -> int:
    import matplotlib.pyplot as plt

    Figure.savefig = _capture
    try:
        import render_pipeline_v2_compact as P1
        import calibrated_clinical_prediction as C

        figs = [("Figure_1_pipeline_v2_compact", getattr(P1, "fig", None))]
        CAPTURED.clear()
        try:
            C.run()
        except Exception as exc:  # data/env dependent
            print(f"[aviso] calibrated_clinical_prediction.run() falhou: {exc}")
        figs.append(("Figure_2_discrimination_sklearn190", CAPTURED[0] if CAPTURED else None))
        figs.append(("Figure_3_calibration_sklearn190", CAPTURED[1] if len(CAPTURED) > 1 else None))
    finally:
        Figure.savefig = _real_savefig

    failed = False
    for name, fig in figs:
        if fig is None:
            print(f"\n=== {name} ===\n  [aviso] figura nao obtida; audite manualmente")
            failed = True
            continue
        rep = S.audit_figure(name, fig)
        n = len(rep["hits"])
        print(f"\n=== {rep['name']} ===")
        print(f"  artistas de texto: {rep['n_text']}   sobreposicoes: {n}")
        if n:
            failed = True
            for area, w, h, a, b in rep["hits"][:20]:
                print(f"    {area:9.1f} px²  ({w:.1f}x{h:.1f} px)  {a}  X  {b}")
            if n > 20:
                print(f"    ... +{n - 20}")
        plt.close(fig)

    print("\n" + "=" * 60)
    print("AUDITORIA RESTANTE: " + ("FALHA" if failed else "PASS"))
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())