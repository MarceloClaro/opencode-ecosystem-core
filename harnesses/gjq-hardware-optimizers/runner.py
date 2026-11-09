#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner do otimizador hardware-aware para GJQ (SPEC-935-R1109).

Comandos:
    profile    lê o Target real e salva o perfil (não submete)
    optimize   otimiza um circuito (não submete)
    benchmark  otimiza vários circuitos (não submete)
    compare    compara baseline vs otimizado e mitiga leitura
    mitigate   aplica mitigação de leitura a counts locais
    run        otimiza e submete ao GJQ com confirm/allow_hardware
    status     consulta o status de um task_id
    result     lê o resultado de um task_id
    audit      audita counts locais
    doctor     mostra SDK, chave e backends de hardware do registro
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from qiskit import qasm2, qasm3  # noqa: E402

from gjq_hardware_opt import (  # noqa: E402
    BackendUnavailable,
    GJQExecutionError,
    GJQOptimizer,
    HardwareProfile,
    MissingGJQKey,
    SubmissionBlocked,
    audit_counts,
    build_baseline_candidate,
    cached_account_present,
    calibration_circuit,
    case_payload,
    confusion_from_calibration_counts,
    connect_gjq,
    correlation,
    credential_present,
    execution_record,
    export_comparison,
    measurement_order,
    mitigate_probabilities,
    mitigate_subspace,
    readout_confusion_matrix,
    subspace_matrix_from_calibration,
    tvd_vs_ideal,
    export_benchmark,
    export_execution,
    export_result,
    key_present,
    live_profile,
    load_circuit,
    select_circuits,
    submission_gate,
    submit_optimized,
    task_detail,
    task_result,
    task_status,
    wait_for_result,
)
from gjq_hardware_opt.target import build_target_from_profile  # noqa: E402
from integrations.gjq_backend_registry import BACKENDS  # noqa: E402

OUT_PADRAO = Path(__file__).resolve().parent / "resultados"


def _json_print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _profile_summary(profile: HardwareProfile) -> dict:
    return profile.summary()


def _read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _unwrap(payload: dict, key: str) -> dict:
    if isinstance(payload, dict) and key in payload and isinstance(payload[key], dict):
        return payload[key]
    return payload


def _load_profile_input(args) -> tuple[HardwareProfile, object | None, object | None]:
    if args.profile:
        profile = HardwareProfile.from_dict(_read_json(args.profile))
        return profile, build_target_from_profile(profile), None
    if args.backend:
        service, backend = connect_gjq(
            args.backend,
            use_cached_account=getattr(args, "use_cached_account", False),
        )
        profile = live_profile(backend)
        return profile, build_target_from_profile(profile), backend
    raise SystemExit("use --backend (ao vivo) ou --profile (JSON offline)")


def _load_profile_for_export(args) -> HardwareProfile:
    if args.config:
        config = _unwrap(_read_json(args.config), "configuration")
        properties = None
        if args.properties:
            properties = _unwrap(_read_json(args.properties), "properties")
        return HardwareProfile.from_gjq_payloads(config, properties)
    if not args.backend:
        raise SystemExit("use --backend ou --config/--properties")
    _, backend = connect_gjq(
        args.backend,
        use_cached_account=getattr(args, "use_cached_account", False),
    )
    return live_profile(backend)


def _optimizer(args, profile: HardwareProfile, target):
    return GJQOptimizer(
        profile,
        target=target,
        strategy=args.strategy,
        seed=args.seed,
        quick=args.quick,
    )


def cmd_profile(args) -> int:
    profile = _load_profile_for_export(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = profile.to_dict()
    (out / "perfil.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _json_print(
        {
            "status": "ok",
            "backend": profile.backend_name or profile.name,
            "profile_kind": profile.profile_kind,
            "summary": _profile_summary(profile),
            "profile_file": str(out / "perfil.json"),
            "hardware_executed": False,
            "network": False if args.config else True,
        }
    )
    return 0


def cmd_optimize(args) -> int:
    profile, target, _ = _load_profile_input(args)
    item = load_circuit(args.circuit)
    result = _optimizer(args, profile, target).optimize(item["circuit"])
    out = Path(args.out)
    exported = export_result(result, out)
    _json_print(
        {
            "status": "ok",
            "circuit": item["name"],
            "backend": profile.backend_name or profile.name,
            "profile_kind": profile.profile_kind,
            "chosen": result.chosen.to_dict(),
            "baseline": result.baseline.to_dict(),
            "selection": result.selection,
            "layout": result.layout.to_dict(),
            "out_dir": exported["out_dir"],
            "files": exported["files"],
            "hardware_executed": False,
            "network": bool(args.backend),
        }
    )
    return 0


def cmd_benchmark(args) -> int:
    profile, target, _ = _load_profile_input(args)
    items = select_circuits(args.set, args.only)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "perfil.json").write_text(
        json.dumps(profile.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    rows = []
    for item in items:
        circuit_out = out / "circuitos" / item["name"]
        try:
            result = _optimizer(args, profile, target).optimize(item["circuit"])
            export_result(result, circuit_out)
            rows.append(
                {
                    "circuit": item["name"],
                    "description": item["description"],
                    "status": "pass",
                    "baseline": result.baseline.to_dict(),
                    "chosen": result.chosen.to_dict(),
                    "improvement": result.selection["improvement"],
                    "selection": result.selection,
                    "layout": result.layout.to_dict(),
                    "out_dir": str(circuit_out),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "circuit": item["name"],
                    "description": item["description"],
                    "status": "fail",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    passed = [row for row in rows if row["status"] == "pass"]
    summary = {
        "circuits": len(rows),
        "pass": len(passed),
        "fail": len(rows) - len(passed),
        "mean_error_baseline": (
            sum(r["baseline"]["estimate"]["error_budget_proxy"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "mean_error_chosen": (
            sum(r["chosen"]["estimate"]["error_budget_proxy"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "mean_error_reduction_rel": (
            sum(r["improvement"]["error_budget_rel"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "mean_depth_baseline": (
            sum(r["baseline"]["metrics"]["depth"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "mean_depth_chosen": (
            sum(r["chosen"]["metrics"]["depth"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "mean_2q_baseline": (
            sum(r["baseline"]["metrics"]["num_2q"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "mean_2q_chosen": (
            sum(r["chosen"]["metrics"]["num_2q"] for r in passed) / len(passed)
            if passed
            else 0.0
        ),
        "improved_error": sum(
            1
            for r in passed
            if r["chosen"]["estimate"]["error_budget_proxy"]
            < r["baseline"]["estimate"]["error_budget_proxy"]
        ),
        "improved_depth": sum(
            1
            for r in passed
            if r["chosen"]["metrics"]["depth"] < r["baseline"]["metrics"]["depth"]
        ),
    }
    data = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "profile_name": profile.name,
        "profile_kind": profile.profile_kind,
        "profile_fingerprint": profile.target_fingerprint,
        "strategy": args.strategy,
        "seed": args.seed,
        "quick": bool(args.quick),
        "summary": summary,
        "results": rows,
        "hardware_executed": False,
        "network": False,
        "limits": (
            "Métricas de compilação e proxy de erro; não é execução física, "
            "não mede fidelidade de estado e não prova vantagem quântica."
        ),
    }
    exported = export_benchmark(data, out)
    _json_print(
        {
            "status": "ok",
            "summary": summary,
            "out_dir": exported["out_dir"],
            "files": exported["files"],
            "hardware_executed": False,
            "network": bool(args.backend),
        }
    )
    return 0 if summary["fail"] == 0 else 1


def _submit_and_wait(service, backend, circuit, args, label: str):
    gate = submission_gate(
        args.backend,
        shots=args.shots,
        circuit=circuit,
        confirm=args.confirm,
        allow_hardware=args.allow_hardware,
        api_key_present=True,
    )
    if not gate["allowed"]:
        raise SubmissionBlocked(f"{label}: {gate['reason']}")
    submission = submit_optimized(
        backend,
        circuit,
        shots=args.shots,
        confirm=args.confirm,
        allow_hardware=args.allow_hardware,
        api_key_present=True,
    )
    wait = wait_for_result(
        service,
        submission["task_id"],
        timeout=args.timeout,
        poll_interval=args.poll,
    )
    counts = wait.get("result")
    if not counts and wait.get("task_status") == "DONE":
        fallback = task_result(service, submission["task_id"])
        counts = fallback.get("result")
    if not isinstance(counts, dict) or not counts:
        raise GJQExecutionError(
            f"{label}: counts indisponíveis (status {wait.get('task_status')})"
        )
    return submission, wait, counts


def _build_comparison_plan(args, profile, baseline, optimized) -> dict:
    cases = {}
    for name, candidate in (("baseline", baseline), ("otimizado", optimized)):
        circuit = candidate.circuit
        order = measurement_order(circuit)
        calibration_qasm = {}
        if args.calibrate:
            states = (
                ("00", "01", "10", "11")
                if args.full_calibration
                else ("00", "11")
            )
            for prepared in states:
                calibration_qasm[prepared] = qasm2.dumps(
                    calibration_circuit(order, prepared)
                )
        cases[name] = {
            "used_physical": candidate.used_physical,
            "metrics": candidate.metrics,
            "estimate": candidate.estimate,
            "measurement_order": order,
            "qasm2": qasm2.dumps(circuit),
            "qasm3": qasm3.dumps(circuit),
            "calibration_qasm2": calibration_qasm,
        }
    return {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "backend": args.backend or profile.backend_name,
        "profile_name": profile.name,
        "profile_kind": profile.profile_kind,
        "profile_fingerprint": profile.target_fingerprint,
        "calibration_date": profile.last_update_date,
        "shots": args.shots,
        "repetitions": int(args.repetitions),
        "full_calibration": bool(args.full_calibration),
        "strategy": args.strategy,
        "seed": args.seed,
        "quick": bool(args.quick),
        "calibrate": bool(args.calibrate),
        "full_calibration": bool(args.full_calibration),
        "repetitions": int(args.repetitions),
        "submissions_estimated": (
            2 * int(args.repetitions)
            + (2 * 4 if args.calibrate and args.full_calibration else 0)
            + (2 * 2 if args.calibrate and not args.full_calibration else 0)
        ),
        "baseline": cases["baseline"],
        "optimized": cases["otimizado"],
        "hardware_executed": False,
        "network": bool(args.backend),
        "limits": (
            "Plano apenas; nenhum job foi submetido. A execução exige o "
            "primário com --confirm e --allow-hardware. A calibração |11> usa "
            "rx(pi) e inclui preparação do |1>."
        ),
    }


def cmd_compare(args) -> int:
    if args.plan:
        profile, target, backend = _load_profile_input(args)
        service = None
    else:
        if args.profile:
            raise SystemExit(
                "execução de hardware exige --backend; --profile serve apenas para --plan"
            )
        if not credential_present(args.use_cached_account):
            _json_print(
                {
                    "status": "blocked",
                    "reason": (
                        "GJQ_API_KEY ausente no ambiente; use --use-cached-account "
                        "para a conta cacheada"
                    ),
                    "hardware_executed": False,
                    "network": False,
                }
            )
            return 2
        service, backend = connect_gjq(
            args.backend,
            use_cached_account=args.use_cached_account,
        )
        profile = live_profile(backend)
        target = build_target_from_profile(profile)
    item = load_circuit(args.circuit)
    optimized = _optimizer(args, profile, target).optimize(item["circuit"])
    baseline = build_baseline_candidate(
        item["circuit"], profile, target, seed=args.seed
    )
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "perfil.json").write_text(
        json.dumps(profile.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if args.plan:
        plan = _build_comparison_plan(args, profile, baseline, optimized.chosen)
        plan_text = json.dumps(plan, indent=2, ensure_ascii=False, sort_keys=True)
        plan["plan_sha256"] = hashlib.sha256(plan_text.encode("utf-8")).hexdigest()
        plan_path = out / "plano_comparacao.json"
        plan_path.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        _json_print(
            {
                "status": "planned",
                "backend": plan["backend"],
                "shots": plan["shots"],
                "calibrate": plan["calibrate"],
                "submissions_estimated": plan["submissions_estimated"],
                "plan_sha256": plan["plan_sha256"],
                "out_dir": str(out),
                "plan_file": str(plan_path),
                "hardware_executed": False,
                "network": bool(args.backend),
            }
        )
        return 0
    cases = {}
    for name, candidate in (("baseline", baseline), ("otimizado", optimized.chosen)):
        circuit = candidate.circuit
        order = measurement_order(circuit)
        calibration_counts = {}
        calibration_ids = {}
        matrix = None
        leakage = {}
        model = None
        if args.calibrate:
            states = (
                ("00", "01", "10", "11")
                if args.full_calibration
                else ("00", "11")
            )
            for prepared in states:
                calibration = calibration_circuit(order, prepared)
                sub, wait, counts = _submit_and_wait(
                    service, backend, calibration, args,
                    f"{name}/calibracao/{prepared}",
                )
                calibration_counts[prepared] = counts
                calibration_ids[prepared] = sub["task_id"]
            if args.full_calibration:
                model = confusion_from_calibration_counts(
                    calibration_counts, order
                )
                matrix = model.matrix
                leakage = {}
            else:
                matrix, leakage = subspace_matrix_from_calibration(
                    calibration_counts, ("00", "11")
                )
        repetitions = []
        task_ids = []
        aggregate: dict[str, int] = {}
        for repetition in range(int(args.repetitions)):
            submission, wait, counts = _submit_and_wait(
                service, backend, circuit, args,
                f"{name}/repeticao/{repetition + 1}",
            )
            task_ids.append(submission["task_id"])
            total = sum(int(v) for v in counts.values())
            probabilities = {
                str(k): int(v) / total for k, v in counts.items()
            } if total else {}
            if args.calibrate and args.full_calibration:
                mitigation_rep = mitigate_probabilities(probabilities, model)
            elif args.calibrate:
                mitigation_rep = mitigate_subspace(
                    probabilities, matrix, ("00", "11")
                )
            else:
                mitigation_rep = mitigate_probabilities(
                    probabilities, readout_confusion_matrix(profile, order)
                )
            mitigated = mitigation_rep.get("probabilities", {})
            rep_payload = {
                "repetition": repetition + 1,
                "task_id": submission["task_id"],
                "counts": counts,
                "audit": audit_counts(counts, args.shots),
                "raw_correlation_00_11": correlation(probabilities),
                "raw_tvd_vs_ideal": tvd_vs_ideal(probabilities),
                "mitigated_correlation_00_11": correlation(mitigated),
                "mitigated_tvd_vs_ideal": tvd_vs_ideal(mitigated),
                "mitigated_tvd_subspace": (
                    0.5 * (
                        abs(float(mitigated.get("00", 0.0)) - 0.5)
                        + abs(float(mitigated.get("11", 0.0)) - 0.5)
                    )
                    if "00" in mitigated and "11" in mitigated
                    else None
                ),
                "mitigation": mitigation_rep,
            }
            repetitions.append(rep_payload)
            for key, value in counts.items():
                aggregate[str(key)] = aggregate.get(str(key), 0) + int(value)
        counts = aggregate
        total = sum(int(v) for v in counts.values())
        probabilities = {
            str(k): int(v) / total for k, v in counts.items()
        } if total else {}
        if args.calibrate and args.full_calibration:
            mitigation = mitigate_probabilities(probabilities, model)
            mitigation["leakage_by_prepared"] = {}
        elif args.calibrate:
            mitigation = mitigate_subspace(probabilities, matrix, ("00", "11"))
            mitigation["leakage_by_prepared"] = leakage
        else:
            mitigation = mitigate_probabilities(
                probabilities, readout_confusion_matrix(profile, order)
            )
            mitigation["leakage_by_prepared"] = {}
        mitigation["calibration_counts"] = calibration_counts
        mitigation["calibration_task_ids"] = calibration_ids
        payload = case_payload(
            name,
            candidate,
            counts,
            args.shots * int(args.repetitions),
            task_id=task_ids[0] if task_ids else None,
            task_ids=task_ids,
            calibration_task_ids=calibration_ids,
            calibration_counts=calibration_counts,
            mitigation=mitigation,
            repetitions=repetitions,
            shots_per_repetition=args.shots,
        )
        payload["qasm2"] = qasm2.dumps(circuit)
        payload["qasm3"] = qasm3.dumps(circuit)
        payload["measurement_order"] = order
        payload["wait"] = wait
        cases[name] = payload

    comparison = {
        "delta_raw_correlation": (
            cases["otimizado"]["raw_correlation_00_11"]
            - cases["baseline"]["raw_correlation_00_11"]
        ),
        "delta_raw_tvd": (
            cases["otimizado"]["raw_tvd_vs_ideal"]
            - cases["baseline"]["raw_tvd_vs_ideal"]
        ),
    }
    if (
        cases["baseline"].get("mitigated_tvd_subspace") is not None
        and cases["otimizado"].get("mitigated_tvd_subspace") is not None
    ):
        comparison["delta_mitigated_tvd"] = (
            cases["otimizado"]["mitigated_tvd_subspace"]
            - cases["baseline"]["mitigated_tvd_subspace"]
        )
    data = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "backend": args.backend,
        "hardware": True,
        "profile_name": profile.name,
        "profile_kind": profile.profile_kind,
        "profile_fingerprint": profile.target_fingerprint,
        "calibration_date": profile.last_update_date,
        "shots": args.shots,
        "repetitions": int(args.repetitions),
        "full_calibration": bool(args.full_calibration),
        "strategy": args.strategy,
        "seed": args.seed,
        "quick": bool(args.quick),
        "calibrate": bool(args.calibrate),
        "baseline": cases["baseline"],
        "optimized": cases["otimizado"],
        "comparison": comparison,
        "hardware_executed": True,
        "network": True,
        "limits": (
            "Uma execução por caso não é estudo estatístico nem prova de "
            "vantagem quântica. A mitigação de leitura é uma estimativa dentro "
            "do subespaço calibrado; não é fidelidade de estado."
        ),
    }
    exported = export_comparison(data, out)
    _json_print(
        {
            "status": "ok",
            "backend": args.backend,
            "shots": args.shots,
            "repetitions": int(args.repetitions),
            "full_calibration": bool(args.full_calibration),
            "calibrate": bool(args.calibrate),
            "baseline": {
                "task_id": cases["baseline"]["task_id"],
                "task_ids": cases["baseline"]["task_ids"],
                "raw_correlation_00_11": cases["baseline"]["raw_correlation_00_11"],
                "raw_tvd_vs_ideal": cases["baseline"]["raw_tvd_vs_ideal"],
                "mitigated_tvd_subspace": cases["baseline"].get("mitigated_tvd_subspace"),
                "used_physical": cases["baseline"]["candidate"]["used_physical"],
            },
            "otimizado": {
                "task_id": cases["otimizado"]["task_id"],
                "task_ids": cases["otimizado"]["task_ids"],
                "raw_correlation_00_11": cases["otimizado"]["raw_correlation_00_11"],
                "raw_tvd_vs_ideal": cases["otimizado"]["raw_tvd_vs_ideal"],
                "mitigated_tvd_subspace": cases["otimizado"].get("mitigated_tvd_subspace"),
                "used_physical": cases["otimizado"]["candidate"]["used_physical"],
            },
            "comparison": comparison,
            "out_dir": exported["out_dir"],
            "files": exported["files"],
            "hardware_executed": True,
            "network": True,
        }
    )
    return 0


def cmd_run(args) -> int:
    if not credential_present(args.use_cached_account):
        _json_print(
            {
                "status": "blocked",
                "reason": (
                    "GJQ_API_KEY ausente no ambiente; use --use-cached-account "
                    "para a conta cacheada"
                ),
                "hardware_executed": False,
                "network": False,
            }
        )
        return 2
    service, backend = connect_gjq(
        args.backend,
        use_cached_account=args.use_cached_account,
    )
    profile = live_profile(backend)
    item = load_circuit(args.circuit)
    result = _optimizer(args, profile, build_target_from_profile(profile)).optimize(
        item["circuit"]
    )
    out = Path(args.out)
    export_result(result, out)

    gate = submission_gate(
        args.backend,
        shots=args.shots,
        circuit=result.chosen.circuit,
        confirm=args.confirm,
        allow_hardware=args.allow_hardware,
        api_key_present=True,
    )
    if not gate["allowed"]:
        _json_print(
            {
                "status": "blocked",
                "gate": gate,
                "chosen": result.chosen.to_dict(),
                "out_dir": str(out),
                "hardware_executed": False,
                "network": True,
            }
        )
        return 2

    submission = submit_optimized(
        backend,
        result.chosen.circuit,
        shots=args.shots,
        confirm=args.confirm,
        allow_hardware=args.allow_hardware,
        api_key_present=True,
    )
    wait = None
    counts = None
    if args.wait:
        wait = wait_for_result(
            service,
            submission["task_id"],
            timeout=args.timeout,
            poll_interval=args.poll,
        )
        counts = wait.get("result") if wait.get("status") == "done" else None
    qasm2_text = qasm2.dumps(result.chosen.circuit)
    qasm3_text = qasm3.dumps(result.chosen.circuit)
    ideal = {"00": 0.5, "11": 0.5} if item["name"] in {"bell", "E05", "E05_1"} else None
    record = execution_record(
        profile=profile,
        result=result,
        submission=submission,
        qasm2=qasm2_text,
        qasm3=qasm3_text,
        wait=wait,
        counts=counts,
        ideal_distribution=ideal,
    )
    exported = export_execution(record, out)
    _json_print(
        {
            "status": "submitted",
            "task_id": submission["task_id"],
            "backend": submission["backend"],
            "hardware": submission["hardware"],
            "shots": submission["shots"],
            "chosen": result.chosen.to_dict(),
            "gate": gate,
            "wait": wait,
            "counts_audit": record.get("counts_audit"),
            "out_dir": exported["out_dir"],
            "files": exported["files"],
            "hardware_executed": True,
            "network": True,
            "note": "Guarde o task_id; não reenvie o mesmo circuito.",
        }
    )
    if args.wait:
        return 0 if wait and wait.get("status") == "done" else 1
    return 0


def cmd_status(args) -> int:
    if not credential_present(args.use_cached_account):
        _json_print(
            {
                "status": "blocked",
                "reason": "credencial GJQ ausente; use --use-cached-account",
            }
        )
        return 2
    service, _ = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    payload = task_status(service, args.task_id)
    _json_print(payload)
    return 0 if payload.get("status") == "success" else 1


def cmd_result(args) -> int:
    if not credential_present(args.use_cached_account):
        _json_print(
            {
                "status": "blocked",
                "reason": "credencial GJQ ausente; use --use-cached-account",
            }
        )
        return 2
    service, _ = connect_gjq(
        args.backend, use_cached_account=args.use_cached_account
    )
    status = task_status(service, args.task_id)
    if status.get("task_status") not in {"DONE", "ERROR", "CANCELLED"}:
        _json_print(
            {
                "status": "not_final",
                "task_id": args.task_id,
                "task_status": status.get("task_status"),
                "note": "Use status até DONE, ERROR ou CANCELLED.",
            }
        )
        return 1
    result = task_result(service, args.task_id)
    detail = task_detail(service, args.task_id)
    counts = result.get("result") if isinstance(result, dict) else None
    audit = audit_counts(counts, args.shots) if counts else None
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "task_id": args.task_id,
        "backend": args.backend,
        "task_status": status.get("task_status"),
        "result": counts,
        "counts_audit": audit,
        "detail": detail.get("detail"),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "network": True,
        "hardware_executed": True,
        "limits": (
            "Uma execução não prova fidelidade, emaranhamento, vantagem quântica "
            "ou interpretação de Bohm."
        ),
    }
    (out / "resultado_task.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if counts is not None:
        (out / "counts.json").write_text(
            json.dumps(counts, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    _json_print(payload)
    return 0 if audit is None or audit.get("ok") else 1


def cmd_mitigate(args) -> int:
    counts = _read_json(args.counts)
    profile = HardwareProfile.from_dict(_read_json(args.profile))
    qubits = tuple(int(q) for q in args.qubits.split(",") if q.strip())
    total = sum(int(v) for v in counts.values())
    if total <= 0:
        raise SystemExit("counts vazio")
    probabilities = {str(k): int(v) / total for k, v in counts.items()}
    if args.matrix:
        matrix_payload = _read_json(args.matrix)
        matrix = (
            matrix_payload.get("matrix")
            if isinstance(matrix_payload, dict)
            else matrix_payload
        )
        states = tuple(s.strip() for s in args.states.split(",") if s.strip())
        mitigation = mitigate_subspace(probabilities, matrix, states)
        matrix_source = "matriz informada"
    else:
        mitigation = mitigate_probabilities(
            probabilities, readout_confusion_matrix(profile, qubits)
        )
        matrix_source = "perfil"
    audit = audit_counts(counts, args.shots)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "counts": counts,
        "probabilities": probabilities,
        "audit": audit,
        "mitigation": mitigation,
        "matrix_source": matrix_source,
        "qubits": list(qubits),
        "profile_name": profile.name,
        "profile_fingerprint": profile.target_fingerprint,
        "hardware_executed": False,
        "network": False,
        "limits": (
            "Mitigação local; não é fidelidade. A calibração |11> usa rx(pi) e "
            "inclui preparação do |1>; o leakage 01/10 não é corrigido pela "
            "inversão 00/11."
        ),
    }
    (out / "mitigacao.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# Mitigação de leitura — resultado",
        "",
        f"Perfil **{profile.name}** · qubits {list(qubits)} · matriz: {matrix_source}.",
        "",
        "## Counts",
        "",
        "| Bitstring | Counts | Probabilidade |",
        "|---|---:|---:|",
    ]
    for key in sorted(probabilities):
        lines.append(f"| `{key}` | {counts[key]} | {probabilities[key]:.6f} |")
    lines += [
        "",
        "## Mitigação",
        "",
        f"- Método: `{mitigation.get('method')}`.",
        f"- Matriz: `{mitigation.get('matrix')}`.",
        f"- Condição: {mitigation.get('condition_number'):.3f}.",
        f"- Massa negativa clipada: {mitigation.get('negative_mass_clipped'):.6f}.",
    ]
    if "leakage_outside_subspace" in mitigation:
        lines.append(
            f"- Leakage fora do subespaço: {mitigation['leakage_outside_subspace']:.4f}."
        )
    lines += [
        "",
        "| Estado | Raw | Mitigado |",
        "|---|---:|---:|",
    ]
    for key in sorted(mitigation["probabilities"]):
        lines.append(
            f"| `{key}` | {probabilities.get(key, 0):.6f} | "
            f"{mitigation['probabilities'][key]:.6f} |"
        )
    lines += [
        "",
        "## Limites",
        "",
        "- Não é fidelidade de estado.",
        "- A calibração |11> inclui preparação do |1> via `rx(pi)`.",
        "- A inversão 00/11 não corrige leakage para 01/10.",
        "- Uma execução não é estudo estatístico.",
        "",
    ]
    (out / "RELATORIO_MITIGACAO.md").write_text("\n".join(lines), encoding="utf-8")
    _json_print(
        {
            "status": "ok",
            "qubits": list(qubits),
            "matrix_source": matrix_source,
            "mitigation": mitigation,
            "audit": audit,
            "out_dir": str(out),
            "files": [
                str(out / "mitigacao.json"),
                str(out / "RELATORIO_MITIGACAO.md"),
            ],
            "hardware_executed": False,
            "network": False,
        }
    )
    return 0 if audit.get("ok") else 1


def cmd_audit(args) -> int:
    counts = _read_json(args.counts)
    audit = audit_counts(counts, args.shots)
    _json_print(audit)
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "auditoria.json").write_text(
            json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return 0 if audit.get("ok") else 1


def cmd_doctor(args) -> int:
    sdk_version = None
    sdk_present = False
    try:
        import gjq_client

        sdk_version = getattr(gjq_client, "__version__", None)
        sdk_present = True
    except ImportError:
        pass
    import qiskit

    hardware = [
        {
            "id": backend.id,
            "name": backend.display_name,
            "api_name": backend.api_name,
            "status": backend.status,
            "qubits": backend.qubits,
            "requires_allow_hardware": backend.requires_allow_hardware,
        }
        for backend in BACKENDS
        if backend.requires_allow_hardware
    ]
    _json_print(
        {
            "status": "ok",
            "api_key_present": key_present(),
            "cached_account_present": cached_account_present(),
            "gjq_client_present": sdk_present,
            "gjq_client_version": sdk_version,
            "qiskit_version": qiskit.__version__,
            "hardware_backends": hardware,
            "confirm_required": True,
            "allow_hardware_required": True,
            "note": "O catálogo é um snapshot; confirme status e fila com gjq_list_backends.",
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Otimizador hardware-aware para backends GJQ (R1109)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_profile = sub.add_parser("profile", help="lê o Target e salva o perfil")
    p_profile.add_argument("--backend", help="nome do backend GJQ (ao vivo)")
    p_profile.add_argument("--config", help="JSON de gjq_backend_config")
    p_profile.add_argument("--properties", help="JSON de gjq_backend_properties")
    p_profile.add_argument("--out", default=str(OUT_PADRAO))
    p_profile.add_argument(
        "--use-cached-account", action="store_true",
        help="usa a conta GJQ já cacheada pelo SDK, sem ler a chave",
    )
    p_profile.set_defaults(func=cmd_profile)

    for name, func, help_text in (
        ("optimize", cmd_optimize, "otimiza um circuito sem submeter"),
        ("benchmark", cmd_benchmark, "otimiza vários circuitos sem submeter"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--backend", help="backend GJQ ao vivo")
        p.add_argument("--profile", help="perfil JSON offline")
        p.add_argument("--circuit", required=(name == "optimize"), help="nome ou .qasm")
        p.add_argument("--set", default="experiments", choices=["synthetic", "experiments", "all"])
        p.add_argument("--only", nargs="*", default=None)
        p.add_argument("--strategy", default="balanced")
        p.add_argument("--seed", type=int, default=42)
        p.add_argument("--quick", action="store_true")
        p.add_argument("--out", default=str(OUT_PADRAO))
        p.add_argument(
            "--use-cached-account", action="store_true",
            help="usa a conta GJQ já cacheada pelo SDK, sem ler a chave",
        )
        p.set_defaults(func=func)

    p_compare = sub.add_parser(
        "compare",
        help="compara baseline vs otimizado e aplica mitigação de leitura",
    )
    p_compare.add_argument("--backend")
    p_compare.add_argument("--profile", help="perfil JSON para --plan offline")
    p_compare.add_argument("--circuit", default="E05")
    p_compare.add_argument("--shots", type=int, default=4096)
    p_compare.add_argument("--repetitions", type=int, default=1)
    p_compare.add_argument(
        "--full-calibration",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="calibra |00>, |01>, |10> e |11> e usa matriz 4x4",
    )
    p_compare.add_argument("--strategy", default="balanced")
    p_compare.add_argument("--seed", type=int, default=42)
    p_compare.add_argument("--quick", action="store_true")
    p_compare.add_argument(
        "--plan", action="store_true",
        help="gera o plano e os QASM sem submeter nenhum job",
    )
    p_compare.add_argument("--confirm", action="store_true")
    p_compare.add_argument("--allow-hardware", action="store_true")
    p_compare.add_argument(
        "--calibrate",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="roda |00> e |11> nos mesmos qubits para a matriz de leitura",
    )
    p_compare.add_argument("--timeout", type=float, default=900.0)
    p_compare.add_argument("--poll", type=float, default=5.0)
    p_compare.add_argument("--out", default=str(OUT_PADRAO))
    p_compare.add_argument(
        "--use-cached-account", action="store_true",
        help="usa a conta GJQ já cacheada pelo SDK, sem ler a chave",
    )
    p_compare.set_defaults(func=cmd_compare)

    p_run = sub.add_parser("run", help="otimiza e submete ao GJQ")
    p_run.add_argument("--backend", required=True, help="backend GJQ ao vivo")
    p_run.add_argument("--circuit", required=True, help="nome ou .qasm")
    p_run.add_argument("--shots", type=int, default=1024)
    p_run.add_argument("--strategy", default="balanced")
    p_run.add_argument("--seed", type=int, default=42)
    p_run.add_argument("--quick", action="store_true")
    p_run.add_argument("--confirm", action="store_true", help="confirma a submissão")
    p_run.add_argument(
        "--allow-hardware",
        action="store_true",
        help="autoriza hardware/emulação; obrigatório para Baihua/Guoji/Yudu",
    )
    p_run.add_argument("--wait", action="store_true", help="aguarda o resultado")
    p_run.add_argument("--timeout", type=float, default=600.0)
    p_run.add_argument("--poll", type=float, default=5.0)
    p_run.add_argument("--out", default=str(OUT_PADRAO))
    p_run.add_argument(
        "--use-cached-account", action="store_true",
        help="usa a conta GJQ já cacheada pelo SDK, sem ler a chave",
    )
    p_run.set_defaults(func=cmd_run)

    p_status = sub.add_parser("status", help="consulta o status de um task_id")
    p_status.add_argument("--backend", default="Baihua")
    p_status.add_argument("--task-id", required=True)
    p_status.add_argument(
        "--use-cached-account", action="store_true",
        help="usa a conta GJQ já cacheada pelo SDK, sem ler a chave",
    )
    p_status.set_defaults(func=cmd_status)

    p_result = sub.add_parser("result", help="lê o resultado de um task_id")
    p_result.add_argument("--backend", default="Baihua")
    p_result.add_argument("--task-id", required=True)
    p_result.add_argument("--shots", type=int, default=None)
    p_result.add_argument("--out", default=str(OUT_PADRAO))
    p_result.add_argument(
        "--use-cached-account", action="store_true",
        help="usa a conta GJQ já cacheada pelo SDK, sem ler a chave",
    )
    p_result.set_defaults(func=cmd_result)

    p_mitigate = sub.add_parser(
        "mitigate", help="aplica mitigação de leitura a counts locais"
    )
    p_mitigate.add_argument("--counts", required=True)
    p_mitigate.add_argument("--profile", required=True)
    p_mitigate.add_argument(
        "--qubits", required=True,
        help="qubits físicos na ordem MSB->LSB, separados por vírgula",
    )
    p_mitigate.add_argument(
        "--matrix", help="matriz 2x2 ou JSON com a chave matrix",
    )
    p_mitigate.add_argument("--states", default="00,11")
    p_mitigate.add_argument("--shots", type=int, default=None)
    p_mitigate.add_argument("--out", default=str(OUT_PADRAO))
    p_mitigate.set_defaults(func=cmd_mitigate)

    p_audit = sub.add_parser("audit", help="audita counts locais")
    p_audit.add_argument("--counts", required=True)
    p_audit.add_argument("--shots", type=int, default=None)
    p_audit.add_argument("--out", default=None)
    p_audit.set_defaults(func=cmd_audit)

    p_doctor = sub.add_parser("doctor", help="mostra SDK, chave e backends")
    p_doctor.set_defaults(func=cmd_doctor)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except MissingGJQKey as exc:
        _json_print(
            {
                "status": "blocked",
                "reason": str(exc),
                "hardware_executed": False,
                "network": False,
            }
        )
        return 2
    except BackendUnavailable as exc:
        _json_print({"status": "error", "reason": str(exc), "hardware_executed": False})
        return 2
    except SubmissionBlocked as exc:
        _json_print({"status": "blocked", "reason": str(exc), "hardware_executed": False})
        return 2
    except GJQExecutionError as exc:
        _json_print({"status": "error", "reason": str(exc), "hardware_executed": False})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
