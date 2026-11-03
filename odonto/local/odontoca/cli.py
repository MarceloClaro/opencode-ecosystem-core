"""CLI OdontoCA Local — SPEC-935-R898 (download/train/predict/report/ca-sim)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cmd_download(args: argparse.Namespace) -> int:
    from . import data as data_mod

    dest = data_mod.download_kaggle(
        args.ref, args.dest, consent=args.i_know_kaggle
    )
    print(f"ok: {args.ref} → {dest} (provenance.json gravado)")
    return 0


def _cmd_train(args: argparse.Namespace) -> int:
    from . import data as data_mod, train as train_mod

    df, target = train_mod.load_frame_from_args(args.csv, args.xlsx, args.target)
    if args.task == "onset":
        df, target = train_mod.prepare_onset_s1(df)
        group = args.group
        counts = train_mod.cohort_counts(df)
        print(f"coorte onset: {counts}", file=sys.stderr)
        if getattr(args, "verify_locked", False):
            try:
                train_mod.verify_locked_cohort(df)
            except train_mod.CohortMismatchError as exc:
                print(f"erro (fail-closed): {exc}", file=sys.stderr)
                return 3
            print(f"gate fail-closed OK: {train_mod.LOCKED_COHORT}", file=sys.stderr)
    else:
        group = args.group
    if group is not None and group not in df.columns:
        print(f"erro: coluna de grupo '{group}' ausente", file=sys.stderr)
        return 2
    report = train_mod.run_training(
        df,
        target=target,
        group=group,
        out_dir=args.out,
        n_folds=args.folds,
        seed=args.seed,
        threshold=args.threshold,
    )
    ens = report["models"]["ensemble"]
    print(
        json.dumps(
            {
                "status": "ok",
                "out": str(args.out),
                "target": target,
                "claim_level": report["claim_level"],
                "ensemble_auroc": ens["auroc"],
                "baseline": report["baseline_prevalence"],
                "flag": ens["flag"],
            },
            ensure_ascii=False,
        )
    )
    return 0


def _cmd_predict(args: argparse.Namespace) -> int:
    from . import predict as pred_mod

    df = pred_mod.predict_to_csv(args.model, args.csv, args.out)
    print(f"ok: {len(df)} linhas → {args.out}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from . import train as train_mod

    rep = train_mod.regenerate_report(args.out)
    print(json.dumps({"status": "ok", "claim_level": rep["claim_level"]}, ensure_ascii=False))
    return 0


def _cmd_ca_sim(args: argparse.Namespace) -> int:
    from . import ca as ca_mod
    from . import train as train_mod

    df, _target = train_mod.load_frame_from_args(args.csv, None, args.target)
    if "tooth_fdi" not in df.columns and "Position_Tooth" in df.columns:
        df = df.rename(columns={"Position_Tooth": "tooth_fdi"})
    if "tooth_fdi" not in df.columns:
        print("erro: CSV precisa de tooth_fdi", file=sys.stderr)
        return 2
    result = ca_mod.simulate_evolution(
        df.head(args.n_teeth), rule=None, steps=args.steps, seed=args.seed
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({"status": "ok", "claim_level": result["claim_level"], "out": str(out)}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="odontoca",
        description="OdontoCA Local — CA + ML para cárie (SPEC-935-R898; "
        "comparação empírica, revisão humana obrigatória).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("download", help="baixa dataset Kaggle (consentimento explícito)")
    d.add_argument("--ref", required=True, help="owner/slug do dataset Kaggle")
    d.add_argument("--dest", required=True)
    d.add_argument(
        "--i-know-kaggle",
        action="store_true",
        help="consentimento explícito do operador para download",
    )
    d.set_defaults(func=_cmd_download)

    t = sub.add_parser("train", help="treina modelos com CV agrupada")
    t.add_argument("--csv", help="caminho CSV/parquet de entrada")
    t.add_argument("--xlsx", help="Table_S1.xlsx (SHA-256 verificado)")
    t.add_argument("--target", help="coluna-alvo (auto-detect se omitido)")
    t.add_argument("--group", help="coluna de agrupamento (ex.: paciente)")
    t.add_argument(
        "--task",
        choices=("default", "onset"),
        default="default",
        help="onset: subconjunto H com alvo H→C (Table_S1, anti-leakage)",
    )
    t.add_argument("--out", default="outputs")
    t.add_argument("--folds", type=int, default=5)
    t.add_argument("--seed", type=int, default=0)
    t.add_argument("--threshold", type=float, default=0.5)
    t.add_argument(
        "--verify-locked",
        action="store_true",
        help="fail-closed: exige a coorte travada 996/83/81 (task=onset)",
    )
    t.set_defaults(func=_cmd_train)

    pr = sub.add_parser("predict", help="inferência com modelo salvo")
    pr.add_argument("--model", required=True)
    pr.add_argument("--csv", required=True)
    pr.add_argument("--out", required=True)
    pr.set_defaults(func=_cmd_predict)

    r = sub.add_parser("report", help="regenera relatório do OOF salvo")
    r.add_argument("--out", required=True, help="diretório com oof_predictions.csv")
    r.set_defaults(func=_cmd_report)

    s = sub.add_parser("ca-sim", help="simulação descritiva de progressão (não causal)")
    s.add_argument("--csv", required=True)
    s.add_argument("--target")
    s.add_argument("--steps", type=int, default=3)
    s.add_argument("--n-teeth", type=int, default=32)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", default="outputs/ca_sim.json")
    s.set_defaults(func=_cmd_ca_sim)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:  # fail-closed com mensagem clara
        print(f"erro: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
