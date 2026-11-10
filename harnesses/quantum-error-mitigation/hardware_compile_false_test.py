#!/usr/bin/env python3
"""R1140 — teste controlado de compile=False no Baihua.

Um único job, 4.096 shots, circuito Bell em 106/107, QASM pré-compilado com
initial_layout identidade de 108 qubits. O teste verifica aceitação, task ID,
soma dos counts, hash do QASM e layout local; não é estudo estatístico.

Uso:
    plan  --out DIR
    run   --out DIR --confirm --allow-hardware --use-cached-account
    status --out DIR
    result --out DIR --shots 4096 --use-cached-account

Hardware exige GJQ_HARDWARE_ENABLED=1 no ambiente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qiskit import qasm2

from integrations import gjq_core_provider as provider
from quantum_mitigation.compilation_audit import build_physical_circuit

BACKEND = "Baihua"
PAIR = (106, 107)
NUM_QUBITS = 108
SHOTS = 4096
OUT_DEFAULT = Path(__file__).resolve().parent / "resultados" / "r1140_compile_false"


def _json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _write_new(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"destino existente: {path}")
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def build_manifest() -> dict:
    circuit = build_physical_circuit(PAIR, num_qubits=NUM_QUBITS)
    qasm = qasm2.dumps(circuit)
    payload = {
        "schema_version": 1,
        "protocol": "r1140-compile-false-controlled",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "backend": BACKEND,
        "pair": list(PAIR),
        "num_qubits": NUM_QUBITS,
        "shots": SHOTS,
        "jobs": 1,
        "compile": False,
        "transpile": True,
        "initial_layout": "identity_108",
        "qasm2": qasm,
        "qasm_sha256": _sha(qasm),
        "decision_rules": [
            "task_id deve existir; ausência bloqueia",
            "soma dos counts deve ser 4096",
            "final_index_layout[106]=106 e [107]=107",
            "qubits ativos devem ser [106,107]",
            "um job não prova fidelidade, emaranhamento ou vantagem",
            "se o serviço recompilar/renomear, registrar e bloquear nova submissão",
        ],
        "requires_confirm": True,
        "requires_allow_hardware": True,
        "requires_hardware_enabled": True,
        "hardware_submission_allowed": False,
        "limits": (
            "Smoke test de compilação; não é estudo estatístico. "
            "O layout físico do servidor não é devolvido pelo SDK."
        ),
    }
    payload["manifest_sha256"] = _sha(
        json.dumps(payload, sort_keys=True, separators=(",", ":"))
    )
    return payload


def cmd_plan(args) -> int:
    payload = build_manifest()
    _write_new(Path(args.out) / "preregistration.json", payload)
    _json({"status": "ok", "path": str(Path(args.out) / "preregistration.json"),
           "manifest_sha256": payload["manifest_sha256"], "hardware_executed": False})
    return 0


def cmd_run(args) -> int:
    if not args.confirm or not args.allow_hardware:
        _json({"status": "blocked", "reason": "exige --confirm e --allow-hardware"})
        return 2
    if os.environ.get("GJQ_HARDWARE_ENABLED", "").strip().lower() not in {"1", "true", "yes", "on"}:
        _json({"status": "blocked", "reason": "defina GJQ_HARDWARE_ENABLED=1"})
        return 2
    out = Path(args.out)
    manifest_path = out / "preregistration.json"
    if not manifest_path.exists():
        _json({"status": "blocked", "reason": "preregistration.json ausente"})
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("hardware_submission_allowed") is not False:
        _json({"status": "blocked", "reason": "manifesto inválido"})
        return 2
    try:
        layout = provider.compilation_audit(
            BACKEND, PAIR, use_cached_account=args.use_cached_account
        )
    except Exception as exc:
        payload = {
            "status": "blocked",
            "stage": "layout_audit",
            "error_type": type(exc).__name__,
            "reason": str(exc)[:800],
            "executed": False,
        }
        _write_new(out / "run.json", payload)
        _json(payload)
        return 2
    _write_new(out / "layout_audit.json", layout)
    if layout.get("status") != "success" or not layout["audit"]["identity_preserved"]:
        payload = {
            "status": "blocked",
            "stage": "layout_audit",
            "reason": "identidade 106/107 não preservada",
            "layout": layout,
            "executed": False,
        }
        _write_new(out / "run.json", payload)
        _json(payload)
        return 2
    try:
        payload = provider.submit(
            manifest["qasm2"],
            BACKEND,
            shots=SHOTS,
            confirm=True,
            allow_hardware=True,
            use_cached_account=args.use_cached_account,
            optimization_level=0,
            transpile_circuit=True,
            compile=False,
            initial_layout=list(range(NUM_QUBITS)),
        )
    except Exception as exc:  # rede, SSL, autenticação ou SDK
        payload = {
            "status": "blocked",
            "error_type": type(exc).__name__,
            "reason": str(exc)[:800],
            "executed": False,
        }
    _write_new(out / "run.json", payload)
    _json(payload)
    return 0 if payload.get("status") == "submitted" else 2


def cmd_status(args) -> int:
    out = Path(args.out)
    run_path = out / "run.json"
    if not run_path.exists():
        _json({"status": "blocked", "reason": "run.json ausente"})
        return 2
    run = json.loads(run_path.read_text(encoding="utf-8"))
    task_id = run.get("task_id")
    if not task_id:
        _json({"status": "blocked", "reason": "sem task_id", "run": run})
        return 2
    try:
        payload = provider.result(task_id, use_cached_account=args.use_cached_account)
    except Exception as exc:
        payload = {"status": "blocked", "error_type": type(exc).__name__,
                   "reason": str(exc)[:800], "executed": False}
    _write_new(out / "status.json", payload)
    _json(payload)
    return 0 if payload.get("status") in {"success", "not_final"} else 2


def cmd_result(args) -> int:
    out = Path(args.out)
    run_path = out / "run.json"
    if not run_path.exists():
        _json({"status": "blocked", "reason": "run.json ausente"})
        return 2
    run = json.loads(run_path.read_text(encoding="utf-8"))
    task_id = run.get("task_id")
    if not task_id:
        _json({"status": "blocked", "reason": "sem task_id"})
        return 2
    try:
        payload = provider.result(
            task_id, shots=args.shots, use_cached_account=args.use_cached_account
        )
    except Exception as exc:
        payload = {"status": "blocked", "error_type": type(exc).__name__,
                   "reason": str(exc)[:800], "executed": False}
    _write_new(out / "result.json", payload)
    _json(payload)
    return 0 if payload.get("status") == "success" else 2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run", "status", "result"):
        item = sub.add_parser(name)
        item.add_argument("--out", default=str(OUT_DEFAULT))
        item.add_argument("--confirm", action="store_true")
        item.add_argument("--allow-hardware", action="store_true")
        item.add_argument("--use-cached-account", action="store_true")
        item.add_argument("--shots", type=int, default=SHOTS)
    args = parser.parse_args(argv)
    return {"plan": cmd_plan, "run": cmd_run, "status": cmd_status, "result": cmd_result}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
