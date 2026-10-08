"""Reproducible graphical abstract; aggregate JSON is the sole numeric source.

Exports English and Portuguese vector PDF/SVG and 6000 x 2400 PNG files.
No generative image model, patient image, external icon, or fabricated data.
"""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "calibrated_clinical_internal_validation_corrected_sklearn190.json"
DATA = json.loads(SOURCE.read_text(encoding="utf-8"))
for f in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"),
          Path("/mnt/c/Windows/Fonts/arial.ttf"), Path("/mnt/c/Windows/Fonts/arialbd.ttf")):
    if f.exists():
        font_manager.fontManager.addfont(str(f))
font = "Arial" if any(f.name == "Arial" for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": font, "svg.fonttype": "none", "pdf.fonttype": 42})

W, H, DPI = 15, 6, 400
INK, MUTED, BLUE, TEAL = "#163C52", "#455D6B", "#1C6086", "#137C77"


def make(language):
    pt = language == "PT"
    def number(n, decimals=4):
        s = f"{n:.{decimals}f}".replace("-", "−")
        return s.replace(".", ",") if pt else s
    fig, ax = plt.subplots(figsize=(W, H), dpi=DPI)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, W), ylim=(0, H)); ax.axis("off")
    texts, panels = [], []
    def text(x, y, label, size=16, color=INK, weight="normal", align="left"):
        t = ax.text(x, y, label, ha=align, va="center", fontsize=size,
                    color=color, weight=weight, linespacing=1.35)
        texts.append(t)
        return t
    def panel(x, y, w, h, fill, stroke):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.16",
                          facecolor=fill, edgecolor=stroke, linewidth=1.1)
        ax.add_patch(p); panels.append(p)
    def arrow(x1, x2, y):
        ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>",
                     mutation_scale=22, linewidth=1.8, color=BLUE))

    title = "Predição de cárie por dente: recalibração em coorte pública" if pt else "Tooth-level caries prediction: recalibration in a public cohort"
    text(.3, 5.57, title, 24, weight="bold")
    text(.3, 5.12, "OdontoCA • Estudo exploratório com validação interna" if pt else
         "OdontoCA • Exploratory study with internal validation", 16, MUTED)

    panel(.3, 1.2, 2.55, 3.52, "#EDF5FA", "#B7D2E1")
    panel(3.3, 1.2, 3.6, 3.52, "#F3F7F9", "#C7D8E2")
    panel(7.35, 1.2, 7.35, 3.52, "#F1F7F5", "#BDD9D3")
    arrow(2.92, 3.23, 2.98); arrow(6.97, 7.28, 2.98)

    text(1.575, 4.37, "COORTE" if pt else "COHORT", 16, BLUE, "bold", "center")
    text(1.575, 3.62, str(DATA["analysis_rows"]), 43, BLUE, "bold", "center")
    text(1.575, 3.09, "transições dentárias" if pt else "tooth transitions", 17, INK, align="center")
    text(1.575, 2.48, f'{DATA["analysis_children"]} ' + ("crianças" if pt else "children"), 22, INK, "bold", "center")
    events = f'{DATA["analysis_events"]} ' + ("eventos" if pt else "events")
    text(1.575, 1.86, events + f' ({number(100 * DATA["event_fraction"], 1)}%)', 17, INK, align="center")

    text(5.1, 4.37, "VALIDAÇÃO" if pt else "VALIDATION", 16, BLUE, "bold", "center")
    text(5.1, 3.75, f'{DATA["outer_folds"]} × {DATA["inner_folds"]}', 31, BLUE, "bold", "center")
    text(5.1, 3.13, "partições aninhadas\nagrupadas por criança" if pt else
         "nested folds\ngrouped by child", 17, INK, align="center")
    text(5.1, 2.21, "Recalibração no treino\nintercepto + inclinação" if pt else
         "Training-only recalibration\nintercept + slope", 16, TEAL, "bold", "center")
    text(5.1, 1.52, "Avaliação em crianças retidas" if pt else
         "Evaluation on held-out children", 13, MUTED, align="center")

    text(11.025, 4.37, "BRIER: ORIGINAL → RECALIBRADO" if pt else
         "BRIER: ORIGINAL → RECALIBRATED", 16, TEAL, "bold", "center")
    text(11.025, 4.05, "Valores menores são melhores" if pt else "Lower values are better", 13, MUTED, align="center")
    rows = [("clinical_minimal", 3.67, "Clínico mínimo" if pt else "Minimal clinical"),
            ("clinical_spatial", 2.52, "Clínico + espacial" if pt else "Clinical + spatial")]
    for model, y, label in rows:
        m = DATA["metrics"][model]
        d = DATA["calibration_minus_uncalibrated"][model]["intercept_and_slope"]["brier"]
        text(7.65, y, label, 16, INK, "bold")
        text(14.4, y, f'{number(m["uncalibrated"]["brier"])} → {number(m["intercept_and_slope"]["brier"])}',
             23, TEAL, "bold", "right")
        delta = f'Δ {number(d["estimate"], 5)}'
        interval = ("IC 95%" if pt else "95% CI") + f' [{number(d["ci95"][0], 5)}; {number(d["ci95"][1], 5)}]'
        text(7.65, y - .42, delta + "    " + interval, 16, MUTED)
    text(7.65, 1.51, "Δ = recalibrado − original; bootstrap pareado por criança" if pt else
         "Δ = recalibrated − original; paired child-cluster bootstrap", 12.5, MUTED)
    ax.plot([7.65, 14.4], [2.98, 2.98], color="#CCE0DA", linewidth=1)

    panel(.3, .2, 14.4, .73, "#FCF5ED", "#E5D2B7")
    conclusion = ("O valor adicional espacial e a utilidade clínica permanecem incertos.\n"
                  "É necessária validação externa antes do uso clínico.") if pt else (
                  "Spatial added value and clinical utility remain unconfirmed.\n"
                  "External validation is needed before clinical use.")
    text(7.5, .565, conclusion, 16, "#734B28", "bold", "center")

    # Measure the actual renderer: no clipping or text collisions are permitted.
    fig.canvas.draw(); renderer = fig.canvas.get_renderer()
    bounds = [(t.get_text(), t.get_window_extent(renderer)) for t in texts]
    fw, fh = fig.canvas.get_width_height()
    errors = []
    for label, b in bounds:
        if b.x0 < 0 or b.y0 < 0 or b.x1 > fw or b.y1 > fh:
            errors.append("outside canvas: " + label)
    for i, (a, ba) in enumerate(bounds):
        for b, bb in bounds[i+1:]:
            if min(ba.x1, bb.x1) - max(ba.x0, bb.x0) > 2 and min(ba.y1, bb.y1) - max(ba.y0, bb.y0) > 2:
                errors.append("text collision: " + a + " / " + b)
    assert not errors, "\n".join(errors)
    stem = HERE / ("Graphical_Abstract_Final" + ("_PT" if pt else ""))
    for ext in ("png", "pdf", "svg"):
        fig.savefig(stem.with_suffix("."+ext), dpi=DPI, facecolor="white",
                    metadata={"Creator": "Matplotlib; reproducible aggregate-data visualization"} if ext == "pdf" else None)
    plt.close(fig)
    return {"language": language, "files": [str(stem.with_suffix("."+x).name) for x in ("png", "pdf", "svg")],
            "width_px": fw, "height_px": fh, "dpi": DPI, "aspect_ratio": W/H,
            "minimum_font_points": min(t.get_fontsize() for t in texts), "font": font,
            "text_collision_count": 0, "canvas_overflow_count": 0}


if __name__ == "__main__":
    report = {"data_source": SOURCE.name, "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "analysis_status": DATA["analysis_status"], "outputs": [make("EN"), make("PT")]}
    (HERE / "graphical_abstract_final_quality.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
