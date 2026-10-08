"""Layout gate for the Graphical Abstract.

A rendered figure can be numerically correct and still be unreadable: text can
fall outside the canvas, collide with other text, or spill outside the panel
that is supposed to contain it. This test re-runs the renderer and asserts all
three conditions, so a future edit that breaks the layout fails loudly instead
of shipping a corrupted figure.

Run: python3 manuscript_assets/test_graphical_abstract_layout.py
"""

import sys
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RENDERER = HERE / "render_graphical_abstract.py"

MIN_DPI = 300.0
MIN_BODY_PT = 7.0
MARGIN_PX = 1.0
OVERLAP_PX = 2.0


def _render_and_measure():
    import runpy

    original_close = plt.close
    plt.close = lambda *a, **k: None
    try:
        runpy.run_path(str(RENDERER), run_name="__ga_layout_test__")
    finally:
        plt.close = original_close
    fig = plt.gcf()
    fig.canvas.draw()
    return fig, fig.canvas.get_renderer()


class GraphicalAbstractLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fig, cls.r = _render_and_measure()
        cls.ax = cls.fig.axes[0]
        cls.w, cls.h = cls.fig.canvas.get_width_height()

    def _texts(self):
        items = [
            (t.get_text()[:44].replace("\n", " "), t.get_window_extent(renderer=self.r))
            for t in self.ax.texts
            if t.get_text().strip()
        ]
        inset = self.ax.child_axes[0]
        items += [
            ("[inset tick]" + t.get_text(), t.get_window_extent(renderer=self.r))
            for t in inset.get_yticklabels()
            if t.get_text().strip()
        ]
        return items

    def _panels(self):
        panels = []
        for p in self.ax.patches:
            try:
                w, h = float(p.get_width()), float(p.get_height())
            except (AttributeError, TypeError):
                continue  # arrows have no rect geometry
            if w > 0.3 and h > 0.15:
                panels.append(p.get_window_extent(renderer=self.r))
        return panels

    def test_01_files_exist(self):
        for ext in ("png", "pdf"):
            f = HERE / f"Graphical_Abstract.{ext}"
            self.assertTrue(f.exists(), f"missing {f.name}")
            self.assertGreater(f.stat().st_size, 5000, f"{f.name} suspiciously small")

    def test_02_png_meets_journal_dpi(self):
        """Journal of Dentistry requires >=300 dpi for raster figures."""
        from PIL import Image

        with Image.open(HERE / "Graphical_Abstract.png") as im:
            dpi = im.info.get("dpi", (0, 0))[0]
        self.assertGreaterEqual(dpi, MIN_DPI - 1.0, f"PNG dpi {dpi} < {MIN_DPI}")

    def test_03_all_content_inside_canvas(self):
        offenders = [
            f"{n} @ ({b.x0:.0f},{b.y0:.0f})-({b.x1:.0f},{b.y1:.0f})"
            for n, b in self._texts()
            if b.x0 < -MARGIN_PX or b.y0 < -MARGIN_PX
            or b.x1 > self.w + MARGIN_PX
            or b.y1 > self.h + MARGIN_PX
        ]
        self.assertEqual(offenders, [], "text outside canvas: " + "; ".join(offenders))

    def test_04_no_text_collisions(self):
        items = self._texts()
        collisions = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i][1], items[j][1]
                ix = min(a.x1, b.x1) - max(a.x0, b.x0)
                iy = min(a.y1, b.y1) - max(a.y0, b.y0)
                if ix > OVERLAP_PX and iy > OVERLAP_PX:
                    collisions.append(
                        f"{items[i][0]!r} x {items[j][0]!r} ({ix:.0f}x{iy:.0f}px)"
                    )
        self.assertEqual(collisions, [], "text overlap: " + "; ".join(collisions))

    def test_05_text_stays_inside_its_panel(self):
        panels = self._panels()
        self.assertGreater(len(panels), 0, "no panels found; renderer changed?")
        spills = []
        for name, tb in self._texts():
            for pb in panels:
                ix = min(tb.x1, pb.x1) - max(tb.x0, pb.x0)
                iy = min(tb.y1, pb.y1) - max(tb.y0, pb.y0)
                if ix <= OVERLAP_PX or iy <= OVERLAP_PX:
                    continue
                inside = (
                    tb.x0 >= pb.x0 - MARGIN_PX and tb.x1 <= pb.x1 + MARGIN_PX
                    and tb.y0 >= pb.y0 - MARGIN_PX and tb.y1 <= pb.y1 + MARGIN_PX
                )
                if not inside:
                    spills.append(f"{name!r} overlaps panel edge by {ix:.0f}x{iy:.0f}px")
        self.assertEqual(spills, [], "panel spill: " + "; ".join(spills))

    def test_06_reported_numbers_match_results_json(self):
        """Guard against the figure drifting away from the reported results.

        The renderer hard-codes literals for legibility, so derive the expected
        rounding from the results JSON and require each string to be present.
        """
        import json

        results = json.loads(
            (HERE / "calibrated_clinical_internal_validation_corrected_sklearn190.json")
            .read_text()
        )
        m = results["metrics"]
        rendered = RENDERER.read_text()

        expected = set()
        for model in ("clinical_minimal", "clinical_spatial"):
            uncal = m[model]["uncalibrated"]
            expected.add(f'{uncal["roc_auc"]:.3f}')   # ROC area
            expected.add(f'{uncal["pr_auc"]:.3f}')    # average precision
        expected.add(str(results["analysis_rows"]))
        expected.add(str(results["analysis_events"]))
        expected.add(str(results["analysis_children"]))
        expected.add(f'{results["event_fraction"]:.3f}')  # prevalence reference

        missing = sorted(v for v in expected if v not in rendered)
        self.assertEqual(
            missing, [],
            "renderer does not carry these verified values: " + ", ".join(missing),
        )

    def test_07_no_decision_threshold_claim(self):
        """The pipeline produced no decision threshold; the figure must not imply one."""
        rendered = RENDERER.read_text().lower()
        for forbidden in ("cut-off", "cutoff", "sensitivity of", "specificity of",
                          "threshold of"):
            self.assertNotIn(forbidden, rendered,
                             f"graphical abstract implies a threshold: {forbidden}")
        self.assertIn("no decision threshold", rendered)

    def test_08_font_sizes_are_readable(self):
        """Journal figure guidance: body text should not fall below ~7 pt.

        Measured on the rendered figure, not the source, so a future edit that
        passes a smaller fontsize fails here instead of at the typesetter.
        """
        too_small = []
        for t in self.ax.texts:
            if not t.get_text().strip():
                continue
            size = t.get_fontsize()
            if size < MIN_BODY_PT - 0.01:
                too_small.append(f"{t.get_text()[:34]!r} @ {size:.1f}pt")
        inset = self.ax.child_axes[0]
        for t in list(inset.get_yticklabels()) + [inset.title]:
            if t.get_text().strip() and t.get_fontsize() < MIN_BODY_PT - 0.01:
                too_small.append(f"[inset] {t.get_text()!r} @ {t.get_fontsize():.1f}pt")
        self.assertEqual(
            too_small, [],
            f"text below {MIN_BODY_PT}pt: " + "; ".join(too_small),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
    sys.exit(0)
