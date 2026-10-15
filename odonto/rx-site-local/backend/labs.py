"""Laboratórios de treino e validação REAIS — SPEC-935-R900 FR-005/FR-007/FR-010.

Lê os relatórios reais em ``odonto/local/outputs/*/report.json`` (nada é
inventado), confere o *gate* fail-closed da coorte travada e resume o estado de
validação. Os números de AUROC/AUPRC vêm do disco; a nota sobre o valor
retirado (0,827) é mantida explícita para não reintroduzir alegação antiga.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from .paths import OUTPUTS, ensure_import_path
from . import datasets as datasets_mod

ensure_import_path()

CLAIM_LEVEL = "comparacao_empirica"
DISCLAIMER = (
    "Comparação empírica local — NÃO é desempenho clínico validado, nem "
    "generalização externa, nem prova de eficácia. Revisão humana obrigatória."
)
LOCKED_COHORT = {"rows": 996, "events": 83, "children": 81}

_gate_cache: dict[str, Any] | None = None
_gate_lock = threading.Lock()

LAB_LABELS = {
    "table_s1_onset": "Table_S1 · onset H→C (coorte clínica travada)",
    "kaggle_caries_img": "Kaggle caries · características de imagem",
}


def model_reports() -> list[dict[str, Any]]:
    """Relatórios reais de treino, com hashes dos artefatos."""
    labs: list[dict[str, Any]] = []
    if not OUTPUTS.is_dir():
        return labs
    for path in sorted(OUTPUTS.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_dir() or path.name.startswith("_"):
            continue
        report_path = path / "report.json"
        if not report_path.is_file():
            continue
        try:
            report = json.loads(report_path.read_text())
        except Exception as exc:
            labs.append({"lab": path.name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        artifacts: list[dict[str, Any]] = []
        for name in ("model.joblib", "oof_predictions.csv", "report.md"):
            f = path / name
            if f.is_file():
                artifacts.append(
                    {"name": name, "bytes": f.stat().st_size,
                     "sha256": datasets_mod.sha256_file(f)}
                )
        ensemble = (report.get("models") or {}).get("ensemble") or {}
        labs.append(
            {
                "lab": path.name,
                "label": LAB_LABELS.get(path.name, path.name),
                "path": str(path.relative_to(OUTPUTS.parent)),
                "mock": False,
                "real": True,
                "claim_level": report.get("claim_level", CLAIM_LEVEL),
                "target": report.get("target"),
                "n_rows": report.get("n_rows"),
                "n_groups": report.get("n_groups"),
                "events": report.get("events"),
                "n_folds": report.get("n_folds"),
                "seed": report.get("seed"),
                "metrics": {
                    "auroc": ensemble.get("auroc"),
                    "auprc": ensemble.get("auprc"),
                    "brier": ensemble.get("brier"),
                    "sensitivity": ensemble.get("sensitivity"),
                    "specificity": ensemble.get("specificity"),
                    "threshold": ensemble.get("threshold"),
                    "threshold_opt": ensemble.get("threshold_opt"),
                    "sensitivity_opt": ensemble.get("sensitivity_opt"),
                    "specificity_opt": ensemble.get("specificity_opt"),
                    "ci95_auroc": (ensemble.get("ci95") or {}).get("auroc"),
                    "flag": ensemble.get("flag"),
                },
                "models": list((report.get("models") or {}).keys()),
                "artifacts": artifacts,
            }
        )
    return labs


def training_progress() -> dict[str, Any]:
    """Progresso honesto: job real quando houver; senão, marco persistido."""
    from .jobs import manager

    job = manager.latest()
    if job is not None:
        completed, target = job.completed, job.total
        source = "job"
        basis = "stage"
    else:
        # marco persistido = quantidade de laboratórios reais com relatório
        completed = target = max(1, len(model_reports()))
        source = "persisted"
        basis = "artifact-count"
    completed = max(0, int(completed))
    target = max(1, int(target))
    return {
        "completed": completed,
        "target": target,
        "remaining": max(0, target - completed),
        "percentage": round(100.0 * completed / target, 1),
        "basis": basis,
        "source": source,
        "real": True,
        "mock": False,
        "job": job.payload() if job is not None else None,
    }


def cohort_gate(recompute: bool = False) -> dict[str, Any]:
    """Gate fail-closed da coorte travada (996/83/81) — Table_S1.xlsx real."""
    global _gate_cache
    with _gate_lock:
        if _gate_cache is not None and not recompute:
            return _gate_cache

    from .paths import resolve_table_s1

    result: dict[str, Any] = {
        "source": "Table_S1.xlsx",
        "expected": dict(LOCKED_COHORT),
        "sha256_expected": datasets_mod.SOURCE_SHA256,
        "locked_ok": False,
        "real": True,
        "mock": False,
        "error": None,
    }
    try:
        from odontoca import data as data_mod, train as train_mod

        path = resolve_table_s1()
        result["sha256"] = datasets_mod.sha256_file(path)
        result["sha256_ok"] = result["sha256"] == datasets_mod.SOURCE_SHA256
        frame = data_mod.load_table_s1(path)  # verifica SHA-256 internamente
        onset, _target = train_mod.prepare_onset_s1(frame)
        counts = train_mod.cohort_counts(onset)
        result["observed"] = counts
        result["locked_ok"] = counts == LOCKED_COHORT
    except Exception as exc:  # fail-closed: divergência é reportada, não escondida
        result["error"] = f"{type(exc).__name__}: {exc}"
    with _gate_lock:
        _gate_cache = result
    return result


def validation() -> dict[str, Any]:
    """Painel consolidado de validação — o que é e o que NÃO é validado."""
    return {
        "real": True,
        "mock": False,
        "claim_level": CLAIM_LEVEL,
        "disclaimer": DISCLAIMER,
        "cohort_gate": cohort_gate(),
        "laboratories": model_reports(),
        "automatos_celulares": {
            "module": "odonto/local/odontoca/ca.py",
            "claim_level": "descritivo_nao_causal",
            "states": ["H", "C", "F", "M"],
            "note": "Regra H→C aprendida dos dados; simulação descritiva, nunca causal.",
        },
        "external_validation": {
            "status": "bloqueado",
            "reason": "Exige coorte prospectiva com CEP e pré-registro.",
            "protocol": "odonto/external_validation_protocol.md",
        },
        "honest_tier": {
            "level": "comparacao_empirica",
            "local_scope": [
                "coorte clínica travada reproduzida (996/83/81)",
                "CV agrupada com OOF e intervalo por bootstrap",
                "ensemble comparado a baselines no mesmo split",
                "autômato celular descritivo sobre transições reais",
            ],
            "not_validated": [
                "desempenho clínico ou utilidade diagnóstica",
                "generalização para outra população/centro",
                "inferência causal de qualquer intervenção",
                "aprovação editorial ou mérito de periódico",
            ],
        },
        "notes": [
            "AUROC 0,827 foi RETIRADO (coorte divergente); usar o valor do relatório atual.",
            "Ensemble não supera todos os baselines na coorte clínica — ver report.json.",
        ],
    }
