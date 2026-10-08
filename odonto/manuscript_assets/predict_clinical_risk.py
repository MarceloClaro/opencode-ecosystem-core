# -*- coding: utf-8 -*-
"""
predict_clinical_risk.py — Inferencia com o modelo travado do OdontoCA
========================================================================
Uso previsto: validacao externa. Um centro externo informa os preditores de
consulta de uma crianca e recebe o risco por dente para a proxima consulta
registrada. O artefato e o mesmo que sera publicado, de modo que a validacao
externa pontua exatamente o modelo travado.

USO RESTRITO A PESQUISA. O modelo nao possui limiar de decisao pre-especificado
e nao deve acionar tratamento. Calibracao e desempenho sao indeterminados fora
da coorte de desenvolvimento ate que uma coorte externa independente seja
pontuada.

Exemplo:
    python3 predict_clinical_risk.py novos_pacientes.csv -o riscos.csv
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DEFAULT_BUNDLE = HERE / "odontoca_clinical_model.joblib"

# Colunas minimas que o avaliador externo precisa fornecer, por conjunto.
HELP = {
    "clinical_minimal": ["tooth_position", "age_months_t", "host_dmfs_t",
                          "neighbor_caries_count"],
    "clinical_spatial": ["tooth_position", "age_months_t", "host_dmfs_t",
                         "neighbor_caries_count", "niche_icm", "niche_ul",
                         "niche_lr", "niche_ap", "host_status_t",
                         "spatial_weighted_dmfs_t", "sum_dmfs_t", "sum_ns_dt_t",
                         "sum_s_dt_t"],
}


def load_bundle(path: Path) -> dict:
    bundle = joblib.load(path)
    for key in ("pipelines", "recalibration", "selected_C", "primary_model", "versions"):
        if key not in bundle:
            raise SystemExit(f"Artefato invalido: faltou '{key}'")
    return bundle


def validate_columns(frame: pd.DataFrame, columns: list[str], label: str) -> list[str]:
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise SystemExit(
            f"[{label}] colunas obrigatorias ausentes: {missing}\n"
            f"Disponiveis: {list(frame.columns)}"
        )
    return missing


def predict(bundle: dict, frame: pd.DataFrame, model_name: str) -> pd.DataFrame:
    from calibrated_clinical_prediction import apply_recalibration

    if model_name not in bundle["pipelines"]:
        raise SystemExit(
            f"Modelo desconhecido: {model_name}. "
            f"Disponiveis: {sorted(bundle['pipelines'])}"
        )
    columns = bundle["required_columns"][model_name]
    validate_columns(frame, columns, model_name)
    raw = bundle["pipelines"][model_name].predict_proba(frame[columns])[:, 1]
    calibrated = apply_recalibration(raw, bundle["recalibration"][model_name])
    out = pd.DataFrame(
        {
            "risk_uncalibrated": np.round(raw, 6),
            "risk_calibrated": np.round(calibrated, 6),
        },
        index=frame.index,
    )
    out["model"] = model_name
    out["selected_C"] = bundle["selected_C"][model_name]
    out["intended_use"] = "research-only; no pre-specified decision threshold"
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("input", type=Path, help="CSV com uma linha por dente em avaliacao")
    parser.add_argument("-o", "--output", type=Path, help="CSV de saida (default: stdout)")
    parser.add_argument("--model", default=None, help="primary_model do artefato")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--both", action="store_true", help="Pontuar os dois conjuntos disponiveis"
    )
    args = parser.parse_args(argv)

    if not args.bundle.exists():
        raise SystemExit(
            f"Artefato ausente: {args.bundle}. Gere com lock_final_model.py antes."
        )
    bundle = load_bundle(args.bundle)
    frame = pd.read_csv(args.input)
    if frame.empty:
        raise SystemExit("CSV de entrada vazio")

    targets = (
        ["clinical_minimal", "clinical_spatial"]
        if args.both
        else [args.model or bundle["primary_model"]]
    )
    results = [predict(bundle, frame, m) for m in targets]

    provenance = pd.DataFrame(
        {
            "n_rows_scored": [len(frame)] * len(results),
            "sklearn_version": [bundle["versions"]["scikit_learn"]] * len(results),
            "seed": [bundle["seed"]] * len(results),
            "locked_utc": [bundle["locked_utc"]] * len(results),
        }
    )
    payload = pd.concat(results + [provenance], axis=1)

    if args.output:
        payload.to_csv(args.output, index=False)
        meta = {
            "output": str(args.output),
            "models": targets,
            "sklearn_version": bundle["versions"]["scikit_learn"],
            "required_columns": {m: bundle["required_columns"][m] for m in targets},
            "warning": "Pesquisa. Sem limiar de decisao. Nao usar para acionar tratamento.",
        }
        print(json.dumps(meta, indent=2, ensure_ascii=False))
    else:
        payload.to_csv(sys.stdout, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
