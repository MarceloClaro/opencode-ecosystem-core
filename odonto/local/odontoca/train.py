"""Treino, CV agrupada e métricas — SPEC-935-R898 FR-005/006/007/010."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import pandas as pd

from . import CLAIM_LEVEL, data as data_mod, models as models_mod

ID_LIKE = ("patient_id", "HostID", "child_id", "sample_id", "id", "SEQN", "path", "file")
# Colunas que vazam o desfecho futuro (nunca entram como preditor).
LEAK_COLS = (
    "Future_Status_Tooth", "Time_to_decay", "transition_class",
    "progression_event", "Status_Tooth", "dmfs_Tooth",
)
DEFAULT_FOLDS = 5


LOCKED_COHORT = {"rows": 996, "events": 83, "children": 81}


class CohortMismatchError(RuntimeError):
    """A coorte derivada não confere com a coorte travada (fail-closed)."""


def cohort_counts(out: pd.DataFrame) -> dict:
    """Contagens da coorte de análise: linhas, eventos e crianças únicas."""
    child = out["HostID"] if "HostID" in out.columns else out.get("child_id")
    return {
        "rows": int(len(out)),
        "events": int(out["caries_onset"].sum()),
        "children": int(pd.Series(child).nunique()),
    }


def verify_locked_cohort(
    out: pd.DataFrame, expected: dict | None = None
) -> dict:
    """Gate fail-closed: exige a coorte travada (996 linhas / 83 eventos / 81 crianças).

    Replica a verificação da cell 58 do notebook v1.4.0. Divergência levanta
    :class:`CohortMismatchError` em vez de prosseguir silenciosamente.
    """
    expected = expected or LOCKED_COHORT
    got = cohort_counts(out)
    if got != expected:
        raise CohortMismatchError(
            f"coorte divergente: obtido {got} != esperado {expected}"
        )
    return got


def prepare_onset_s1(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Subconjunto em risco (H) com alvo H→C replicando o manuscrito.

    Replica fielmente ``clean_single_tooth`` + ``build_transitions`` do
    notebook OdontoCA v1.4.0:

    1. restringe às posições primárias de 2 dígitos (exclui o composto ``T5161``);
    2. ordena por criança×dente×``Timepoint``;
    3. usa o PRÓXIMO ``Status_Tooth`` (não ``Future_Status_Tooth``, que não é
       transição temporal);
    4. mantém apenas transições de **um passo** (``Timepoint`` consecutivo,
       ``delta_timepoints == 1``) com **intervalo positivo** (``delta_months > 0``);
    5. subconjunto em risco: estado atual ``H``; desfecho ``caries_onset`` = 1
       quando o próximo estado é ``C``.

    Não aplica ``Future_Status_Tooth``/``Time_to_decay`` (colunas que vazam).
    """
    needed = {"Status_Tooth", "HostID", "Month", "Timepoint", "Position"}
    if not needed <= set(df.columns):
        raise ValueError(f"task=onset exige colunas {needed}")
    d = df.copy()
    d["_child"] = d["HostID"].astype(str)
    d["_pos"] = d["Position"].astype(str)
    d["_ti"] = pd.to_numeric(
        d["Timepoint"].astype(str).str.extract(r"(\d+)")[0], errors="coerce"
    )
    d["_month"] = pd.to_numeric(d["Month"], errors="coerce")

    fdi = d["_pos"].str.replace(r"^T", "", regex=True)
    d["tooth_fdi"] = pd.to_numeric(
        fdi.where(fdi.str.fullmatch(r"\d{2}")), errors="coerce"
    )
    d = d[d["tooth_fdi"].notna() & d["_ti"].notna()].copy()
    if d.empty:
        raise ValueError("task=onset sem posições primárias válidas")

    d = d.sort_values(["_child", "_pos", "_ti"])
    g = d.groupby(["_child", "_pos"], sort=False)
    d["next_status"] = g["Status_Tooth"].shift(-1)
    d["_ti_next"] = g["_ti"].shift(-1)
    d["_month_next"] = g["_month"].shift(-1)
    one_step = (
        (d["_ti_next"] - d["_ti"]).eq(1)
        & (d["_month_next"] - d["_month"]).gt(0)
    )
    risk = (
        d["Status_Tooth"].astype(str).str.upper().eq("H")
        & one_step
        & d["next_status"].notna()
    )
    out = d.loc[risk].copy()
    out["caries_onset"] = (
        out["next_status"].astype(str).str.upper().eq("C")
    ).astype(int)
    out["tooth_fdi"] = out["tooth_fdi"].astype(int)
    out = out.drop(
        columns=[
            c
            for c in list(LEAK_COLS)
            + ["next_status", "_ti", "_ti_next", "_month_next"]
            if c in out.columns
        ]
    )
    if out["caries_onset"].nunique() < 2:
        raise ValueError(
            "task=onset sem eventos H→C deriváveis (uma classe só); "
            f"evento={int(out['caries_onset'].sum())}"
        )
    return out, "caries_onset"


def grouped_cv_splits(
    groups: np.ndarray | list[str],
    n_splits: int = DEFAULT_FOLDS,
    seed: int = 0,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Split por grupo (criança/paciente) — FR-006, sem vazamento."""
    from sklearn.model_selection import GroupKFold

    groups = np.asarray(groups)
    n_groups = len(np.unique(groups))
    n_splits = int(max(2, min(n_splits, n_groups)))
    gkf = GroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    dummy = np.zeros(len(groups))
    for tr, te in gkf.split(dummy, groups=groups):
        yield tr, te


def stratified_splits(
    y: np.ndarray,
    n_splits: int = DEFAULT_FOLDS,
    seed: int = 0,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """KFold estratificado quando não há grupos (ex.: imagens rotuladas)."""
    from sklearn.model_selection import StratifiedKFold

    y = np.asarray(y, dtype=int)
    _, counts = np.unique(y, return_counts=True)
    n_splits = int(max(2, min(n_splits, int(counts.min()))))
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for tr, te in skf.split(np.zeros(len(y)), y):
        yield tr, te


def bootstrap_ci(
    y: np.ndarray,
    p: np.ndarray,
    n_boot: int = 500,
    seed: int = 0,
    alpha: float = 0.05,
) -> dict[str, dict[str, float]]:
    """IC percentil 95% (bootstrap) para AUROC/AUPRC/Brier — FR-007."""
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    rng = np.random.default_rng(seed)
    stats: dict[str, list[float]] = {"auroc": [], "auprc": [], "brier": []}
    n = len(y)
    for _ in range(int(n_boot)):
        idx = rng.integers(0, n, size=n)
        yb, pb = y[idx], p[idx]
        if len(np.unique(yb)) < 2:
            continue
        stats["auroc"].append(float(roc_auc_score(yb, pb)))
        stats["auprc"].append(float(average_precision_score(yb, pb)))
        stats["brier"].append(float(brier_score_loss(yb, pb)))
    out: dict[str, dict[str, float]] = {}
    for k, vals in stats.items():
        if not vals:
            out[k] = {"lo": 0.0, "hi": 1.0, "point": float("nan")}
        else:
            arr = np.asarray(vals)
            out[k] = {
                "lo": float(np.quantile(arr, alpha / 2)),
                "hi": float(np.quantile(arr, 1 - alpha / 2)),
                "point": float(np.median(arr)),
            }
    return out


def best_threshold(y: np.ndarray, p: np.ndarray) -> float:
    """Limiar que maximiza o índice de Youden (sens + espec − 1) no OOF."""
    from sklearn.metrics import roc_curve

    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    if len(np.unique(y)) < 2:
        return 0.5
    fpr, tpr, thr = roc_curve(y, p)
    youden = tpr - fpr
    return float(thr[int(np.argmax(youden))])


def compute_metrics(
    y: np.ndarray,
    p: np.ndarray,
    threshold: float = 0.5,
    baseline: float | None = None,
) -> dict[str, Any]:
    """AUROC/AUPRC/Brier/sensibilidade/especificidade + flag — FR-007/FR-010."""
    from sklearn.metrics import (
        average_precision_score,
        brier_score_loss,
        roc_auc_score,
    )

    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    yhat = (p >= threshold).astype(int)
    tp = int(((yhat == 1) & (y == 1)).sum())
    fn = int(((yhat == 0) & (y == 1)).sum())
    tn = int(((yhat == 0) & (y == 0)).sum())
    fp = int(((yhat == 1) & (y == 0)).sum())
    sens = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    base = float(baseline) if baseline is not None else float(np.mean(y))
    if len(np.unique(y)) >= 2:
        auroc = float(roc_auc_score(y, p))
        auprc = float(average_precision_score(y, p))
    else:
        auroc, auprc = 0.5, base
    m: dict[str, Any] = {
        "auroc": auroc,
        "auprc": auprc,
        "brier": float(brier_score_loss(y, p)),
        "sensitivity": sens,
        "specificity": spec,
        "n": int(len(y)),
        "events": int(y.sum()),
        "prevalence": base,
        "threshold": threshold,
        "baseline": base,
        "flag": "BELOW_BASELINE" if (auroc < 0.5 or auroc < base) else "OK",
    }
    return m


def _design_matrix(
    df: pd.DataFrame,
    target: str,
    group: str | None = None,
) -> tuple[pd.DataFrame, np.ndarray]:
    y = df[target]
    if pd.api.types.is_numeric_dtype(y):
        y = pd.to_numeric(y, errors="coerce")
        if y.notna().sum() and y.dropna().nunique() > 2:
            y = (y > y.median()).astype(int)
        y = y.fillna(0).astype(int)
    else:
        # texto (inclui dtype ``str`` do pandas 3): mapeia tokens positivos
        y = (
            y.astype(str).str.upper().isin({"C", "CARIES", "YES", "Y", "TRUE", "1", "DECAY", "CAVITY"})
        ).astype(int)
    drop = {target}
    if group and group in df.columns:
        drop.add(group)
    for c in ID_LIKE:
        if c in df.columns and c != target:
            drop.add(c)
    for c in LEAK_COLS:
        if c in df.columns and c != target:
            drop.add(c)
    X = df.drop(columns=[c for c in drop if c in df.columns], errors="ignore")
    num = X.select_dtypes(include="number").columns
    for c in X.columns:
        if c not in num:
            X[c] = X[c].astype(str)
    X = pd.get_dummies(X, drop_first=True)
    X = X.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return X, y.to_numpy(dtype=int)


def run_training(
    df: pd.DataFrame,
    target: str,
    group: str | None = None,
    out_dir: str | Path = "outputs",
    n_folds: int = DEFAULT_FOLDS,
    seed: int = 0,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """CV agrupada com OOF, ensemble, calibração final e relatório — FR-005+."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    X, y = _design_matrix(df, target, group)

    if group and group in df.columns:
        groups = df[group].astype(str).to_numpy()
        splitter = grouped_cv_splits(groups, n_splits=n_folds, seed=seed)
        n_groups = len(np.unique(groups))
    else:
        groups = np.arange(len(df)).astype(str)
        splitter = stratified_splits(y, n_splits=n_folds, seed=seed)
        n_groups = len(df)

    base = models_mod.build_models(seed=seed)
    oof = {name: np.zeros(len(y)) for name in base}
    oof_ens = np.zeros(len(y))
    fold_ids = np.full(len(y), -1, dtype=int)

    for fold, (tr, te) in enumerate(splitter):
        fold_ids[te] = fold
        fold_preds = []
        for name, est in base.items():
            est.fit(X.iloc[tr], y[tr])
            p = est.predict_proba(X.iloc[te])[:, 1]
            oof[name][te] = p
            fold_preds.append(p)
        oof_ens[te] = np.mean(fold_preds, axis=0)

    baseline = float(np.mean(y))
    thr_opt = best_threshold(y, oof_ens)
    metrics: dict[str, Any] = {}
    for name in list(base) + ["ensemble"]:
        p = oof_ens if name == "ensemble" else oof[name]
        metrics[name] = compute_metrics(y, p, threshold=threshold, baseline=baseline)
    # desempenho no limiar ótimo (Youden) — dados desbalanceados
    ens_opt = compute_metrics(y, oof_ens, threshold=thr_opt, baseline=baseline)
    metrics["ensemble"]["threshold_opt"] = thr_opt
    metrics["ensemble"]["sensitivity_opt"] = ens_opt["sensitivity"]
    metrics["ensemble"]["specificity_opt"] = ens_opt["specificity"]
    ci = bootstrap_ci(y, oof_ens, n_boot=300, seed=seed)
    metrics["ensemble"]["ci95"] = ci

    # Modelo final calibrado para inferência (fit em todos os dados)
    final = models_mod.EnsembleClassifier(list(base.values()))
    final.fit(X, y)
    try:
        calibrated = models_mod.calibrate(final, X, y, method="sigmoid")
    except Exception:
        calibrated = final

    bundle = {
        "model": calibrated,
        "feature_names": list(X.columns),
        "target": target,
        "group": group,
        "baseline": baseline,
        "metrics": metrics,
        "seed": seed,
        "threshold": threshold,
        "claim_level": CLAIM_LEVEL,
        "version": "odontoca-local-1.0.0",
    }
    import joblib

    joblib.dump(bundle, out / "model.joblib")

    oof_df = pd.DataFrame(
        {
            "y_true": y,
            "proba_ensemble": oof_ens,
            "fold": fold_ids,
        }
    )
    for name in base:
        oof_df[f"proba_{name}"] = oof[name]
    oof_df.to_csv(out / "oof_predictions.csv", index=False)

    report = {
        "claim_level": CLAIM_LEVEL,
        "n_rows": int(len(y)),
        "n_groups": int(n_groups),
        "events": int(y.sum()),
        "baseline_prevalence": baseline,
        "target": target,
        "group": group,
        "n_folds": int(n_folds),
        "seed": seed,
        "models": metrics,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    (out / "report.md").write_text(_render_md(report))
    return report


def regenerate_report(out_dir: str | Path) -> dict[str, Any]:
    """Recalcula relatório a partir do OOF salvo — subcomando ``report``."""
    out = Path(out_dir)
    oof = pd.read_csv(out / "oof_predictions.csv")
    y = oof["y_true"].to_numpy(dtype=int)
    baseline = float(np.mean(y))
    metrics: dict[str, Any] = {}
    for col in [c for c in oof.columns if c.startswith("proba_")]:
        name = col.removeprefix("proba_")
        metrics[name] = compute_metrics(y, oof[col].to_numpy(), baseline=baseline)
    metrics.setdefault("ensemble", metrics.get("oof_ens", {}))
    if "proba_ensemble" in oof.columns:
        metrics["ensemble"] = compute_metrics(
            y, oof["proba_ensemble"].to_numpy(), baseline=baseline
        )
        metrics["ensemble"]["ci95"] = bootstrap_ci(
            y, oof["proba_ensemble"].to_numpy(), n_boot=300
        )
    report = {
        "claim_level": CLAIM_LEVEL,
        "n_rows": int(len(y)),
        "events": int(y.sum()),
        "baseline_prevalence": baseline,
        "models": metrics,
        "regenerated": True,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    (out / "report.md").write_text(_render_md(report))
    return report


def _render_md(rep: dict[str, Any]) -> str:
    lines = [
        "# OdontoCA Local — Relatório de Treino",
        "",
        f"> **Nível de alegação:** {rep.get('claim_level', CLAIM_LEVEL)} — "
        "comparação empírica sob revisão humana; sem garantia de acurácia "
        "superior nem de aceitação editorial.",
        "",
        f"- Linhas: {rep.get('n_rows')} | Eventos: {rep.get('events')} | "
        f"Baseline (prevalência): {rep.get('baseline_prevalence'):.3f}",
        f"- Alvo: `{rep.get('target')}` | Grupo: `{rep.get('group')}` | "
        f"Folds: {rep.get('n_folds', '—')} | Seed: {rep.get('seed', '—')}",
        "",
        "| Modelo | AUROC | AUPRC | Brier | Sens. | Espec. | Flag |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, m in rep.get("models", {}).items():
        if not isinstance(m, dict) or "auroc" not in m:
            continue
        lines.append(
            f"| {name} | {m['auroc']:.3f} | {m['auprc']:.3f} | {m['brier']:.3f} | "
            f"{m['sensitivity']:.3f} | {m['specificity']:.3f} | {m['flag']} |"
        )
    ens = rep.get("models", {}).get("ensemble", {})
    if isinstance(ens, dict) and "threshold_opt" in ens:
        lines += [
            "",
            f"### Ensemble no limiar ótimo (Youden) = {ens['threshold_opt']:.3f}",
            "",
            f"- Sensibilidade: {ens['sensitivity_opt']:.3f} | "
            f"Especificidade: {ens['specificity_opt']:.3f}",
            "- O limiar 0,5 não é adequado a alvos desbalanceados; use o limiar "
            "de decisão apenas com revisão clínica humana.",
        ]
    ci = ens.get("ci95") if isinstance(ens, dict) else None
    if ci:
        lines += [
            "",
            "### IC 95% (bootstrap) do ensemble",
            "",
            "| Métrica | Lo | Hi |",
            "|---|---|---|",
        ]
        for k, v in ci.items():
            lines.append(f"| {k} | {v['lo']:.3f} | {v['hi']:.3f} |")
    lines += [
        "",
        "## Limitações",
        "",
        "- Validação interna (CV); não substitui validação externa (TRIPOD+AI).",
        "- `BELOW_BASELINE` indica desempenho ≤ acaso/prevalência — não usar "
        "o modelo nesse regime.",
        "- Revisão humana obrigatória antes de qualquer uso.",
        "",
    ]
    return "\n".join(lines)


def load_frame_from_args(csv: str | None, xlsx: str | None, target: str | None):
    """Resolve entrada: xlsx da fonte primária (hash verificado) ou CSV."""
    if xlsx:
        df = data_mod.load_table_s1(xlsx)
        tgt = data_mod.detect_target(df, target)
        return df, tgt
    if csv:
        loaded = data_mod.load_csv(csv, target)
        return loaded.df, loaded.target
    raise ValueError("informe --csv ou --xlsx")
