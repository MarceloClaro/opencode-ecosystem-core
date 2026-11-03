"""FR-008, FR-009 — CLI de ponta a ponta e roundtrip de predict."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

LOCAL_ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "odontoca.cli", *args],
        cwd=LOCAL_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_cli_train_end_to_end(synthetic_binary: pd.DataFrame, tmp_path: Path):
    """FR-008: train em CSV sintético → report.json + report.md válidos."""
    csv = tmp_path / "synth.csv"
    synthetic_binary.to_csv(csv, index=False)
    out = tmp_path / "out"
    r = _run("train", "--csv", str(csv), "--target", "caries", "--group", "patient_id",
             "--out", str(out), "--folds", "3")
    assert r.returncode == 0, r.stderr[-3000:]
    report_json = out / "report.json"
    report_md = out / "report.md"
    assert report_json.exists() and report_md.exists()
    rep = json.loads(report_json.read_text())
    assert "models" in rep and "ensemble" in rep["models"]
    assert "auroc" in rep["models"]["ensemble"]
    assert rep["claim_level"] == "comparacao_empirica"


def test_predict_roundtrip(synthetic_binary: pd.DataFrame, tmp_path: Path):
    """FR-009: train → predict com modelo salvo; probs em [0,1]."""
    csv = tmp_path / "synth.csv"
    synthetic_binary.to_csv(csv, index=False)
    out = tmp_path / "out"
    r = _run("train", "--csv", str(csv), "--target", "caries", "--group", "patient_id",
             "--out", str(out), "--folds", "3")
    assert r.returncode == 0, r.stderr[-3000:]
    model = out / "model.joblib"
    assert model.exists()
    pred_csv = out / "predictions.csv"
    r2 = _run("predict", "--model", str(model), "--csv", str(csv), "--out", str(pred_csv))
    assert r2.returncode == 0, r2.stderr[-3000:]
    preds = pd.read_csv(pred_csv)
    proba_col = [c for c in preds.columns if c.startswith("proba")]
    assert proba_col, list(preds.columns)
    assert preds[proba_col[0]].between(0, 1).all()


def test_cli_reports_claim_level(synthetic_binary: pd.DataFrame, tmp_path: Path):
    """Anti-overclaim: relatório rotulado como comparação empírica."""
    csv = tmp_path / "synth.csv"
    synthetic_binary.to_csv(csv, index=False)
    out = tmp_path / "out"
    r = _run("train", "--csv", str(csv), "--target", "caries", "--out", str(out), "--folds", "3")
    assert r.returncode == 0, r.stderr[-3000:]
    text = (out / "report.md").read_text()
    assert "comparação empírica" in text.lower() or "comparacao empirica" in text.lower()
    assert "Qualis" not in text
