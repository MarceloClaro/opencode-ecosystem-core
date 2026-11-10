#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conexão, gates e submissão ao runtime GJQ (R1109).

A chave vem apenas de ``GJQ_API_KEY``. Nenhuma função aceita a chave em
argumento, imprime a chave ou grava a chave no resultado. A submissão de
hardware exige ``confirm=True`` e ``allow_hardware=True``.
"""
from __future__ import annotations

import contextlib
import hashlib
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .profile import HardwareProfile

MAX_SHOTS_DEFAULT = 100_000
FINAL_STATES = {"DONE", "ERROR", "CANCELLED"}
STATUS_MAP = {
    "INITIALIZING": "INITIALIZING",
    "pending": "QUEUED",
    "running": "RUNNING",
    "completed": "DONE",
    "failed": "ERROR",
    "error": "ERROR",
    "cancelled": "CANCELLED",
    "canceled": "CANCELLED",
    "CANCELLED": "CANCELLED",
    "DONE": "DONE",
    "ERROR": "ERROR",
    "QUEUED": "QUEUED",
    "RUNNING": "RUNNING",
}


class GJQExecutionError(RuntimeError):
    pass


class MissingGJQKey(GJQExecutionError):
    pass


class BackendUnavailable(GJQExecutionError):
    pass


class SubmissionBlocked(GJQExecutionError):
    pass


CACHED_ACCOUNT = Path.home() / ".gjq_client" / "gjq_client_account.json"


def key_present() -> bool:
    return bool(os.environ.get("GJQ_API_KEY", "").strip())


def cached_account_present() -> bool:
    return CACHED_ACCOUNT.is_file()


def credential_present(use_cached_account: bool = False) -> bool:
    return key_present() or (use_cached_account and cached_account_present())


@contextlib.contextmanager
def _quiet_client():
    """O SDK imprime tabelas e task IDs; mantém stdout limpo para o CLI."""
    with contextlib.redirect_stdout(sys.stderr):
        yield


def connect_gjq(
    backend_name: str,
    *,
    api_key: str | None = None,
    channel: str | None = None,
    use_cached_account: bool = False,
):
    """Conecta ao runtime GJQ e devolve ``(service, backend)``.

    A chave vem de ``GJQ_API_KEY``. ``use_cached_account=True`` permite usar o
    arquivo de conta já cacheado pelo SDK, sem ler nem imprimir a chave.
    """
    key = (api_key if api_key is not None else os.environ.get("GJQ_API_KEY", "")).strip()
    if not key and not use_cached_account:
        raise MissingGJQKey(
            "GJQ_API_KEY ausente no ambiente; use --use-cached-account para a conta cacheada"
        )
    if not key and not cached_account_present():
        raise MissingGJQKey("conta cacheada do GJQ ausente")
    try:
        from gjq_client import GJQRuntimeService
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise GJQExecutionError(
            "gjq-client ausente; instale gjq-client==0.2.1 no .venv-quantum"
        ) from exc
    with _quiet_client():
        if key:
            service = GJQRuntimeService(
                api_key=key,
                channel=channel or os.environ.get("GJQ_CHANNEL", "gjq_cloud"),
            )
        else:
            service = GJQRuntimeService(
                channel=channel or os.environ.get("GJQ_CHANNEL", "gjq_cloud"),
            )
        backend = service.backend(backend_name)
    if backend is None:
        raise BackendUnavailable(f"backend indisponível: {backend_name!r}")
    return service, backend


def live_profile(backend, *, refresh: bool = True) -> HardwareProfile:
    """Lê configuração/propriedades ao vivo e monta o perfil do Target."""
    with _quiet_client():
        properties = backend.properties(refresh=refresh)
        target = backend.target
    configuration = backend.configuration()
    last_update = getattr(properties, "last_update_date", None) if properties is not None else None
    allowed_edges = [
        tuple(int(x) for x in edge)
        for edge in (getattr(configuration, "coupling_map", None) or ())
        if len(edge) == 2
    ]
    operational = None
    if properties is not None:
        try:
            faulty = set(properties.faulty_qubits())
        except Exception:
            faulty = set()
        operational = [q for q in range(int(target.num_qubits)) if q not in faulty]
    return HardwareProfile.from_target(
        target,
        name=str(backend.name),
        profile_kind="gjq_live_target",
        calibration_source="backend.target + backend.properties (live)",
        backend_name=str(backend.name),
        backend_version=getattr(configuration, "backend_version", None),
        last_update_date=str(last_update) if last_update is not None else None,
        allowed_edges=allowed_edges or None,
        operational_qubits=operational,
        degraded_qubit_threshold=0.05,
    )


def submission_gate(
    backend_name: str,
    *,
    shots: int,
    circuit,
    confirm: bool,
    allow_hardware: bool,
    api_key_present: bool | None = None,
    max_shots: int = MAX_SHOTS_DEFAULT,
) -> dict[str, Any]:
    """Gate único para qualquer submissão. Não acessa a rede."""
    from integrations.gjq_backend_registry import is_hardware_name

    present = key_present() if api_key_present is None else bool(api_key_present)
    hardware = bool(is_hardware_name(backend_name))
    base = {
        "backend": backend_name,
        "hardware": hardware,
        "shots": shots,
        "confirm": bool(confirm),
        "allow_hardware": bool(allow_hardware),
        "api_key_present": present,
        "executed": False,
    }
    if not present:
        return {**base, "allowed": False, "reason": "GJQ_API_KEY ausente no ambiente"}
    if confirm is not True:
        return {**base, "allowed": False, "reason": "confirm=True é obrigatório"}
    if hardware and allow_hardware is not True:
        return {
            **base,
            "allowed": False,
            "reason": "hardware exige allow_hardware=True e revisão de custo",
        }
    if isinstance(shots, bool) or not isinstance(shots, int) or not 1 <= shots <= max_shots:
        return {
            **base,
            "allowed": False,
            "reason": f"shots deve estar entre 1 e {max_shots}",
        }
    if circuit is None:
        return {**base, "allowed": False, "reason": "circuito ausente"}
    if not any(instruction.operation.name == "measure" for instruction in circuit.data):
        return {**base, "allowed": False, "reason": "o circuito precisa de medição"}
    return {**base, "allowed": True, "reason": "ok"}


def _job_id(job: Any) -> str:
    raw = getattr(job, "job_id", None)
    if callable(raw):
        raw = raw()
    if raw is None:
        raw = getattr(job, "_job_id", None)
    if isinstance(raw, (list, tuple)):
        if len(raw) != 1:
            raise GJQExecutionError(f"esperado um task_id, recebido {len(raw)}")
        raw = raw[0]
    if raw is None or not str(raw).strip():
        raise GJQExecutionError("o job não retornou task_id")
    return str(raw)


def submit_optimized(
    backend,
    circuit,
    *,
    shots: int,
    confirm: bool,
    allow_hardware: bool,
    api_key_present: bool | None = None,
    max_shots: int = MAX_SHOTS_DEFAULT,
    amplitude_index: list[int] | None = None,
    options: dict | None = None,
) -> dict[str, Any]:
    """Submete o circuito já otimizado, sem retranspilar."""
    gate = submission_gate(
        backend.name,
        shots=shots,
        circuit=circuit,
        confirm=confirm,
        allow_hardware=allow_hardware,
        api_key_present=api_key_present,
        max_shots=max_shots,
    )
    if not gate["allowed"]:
        raise SubmissionBlocked(gate["reason"])
    try:
        from gjq_client import Sampler
    except ImportError as exc:  # pragma: no cover
        raise GJQExecutionError("gjq-client ausente") from exc
    with _quiet_client():
        job = Sampler(backend=backend, options=options).run(
            circuit,
            shots=shots,
            amplitude_index=amplitude_index,
        )
    task_id = _job_id(job)
    return {
        "status": "submitted",
        "task_id": task_id,
        "backend": str(backend.name),
        "shots": int(shots),
        "hardware": bool(gate["hardware"]),
        "submitted_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "amplitude_index": amplitude_index,
        "options": options,
        "transpile": False,
        "executed": True,
        "note": "Use status/result com o task_id; não reenvie o mesmo circuito.",
    }


def _mapped_status(service, task_id: str) -> str | None:
    """Mapeia o status do SDK e da resposta bruta, tolerando ``None``."""
    try:
        with _quiet_client():
            state = service.task_status(task_id)
    except Exception:
        state = None
    if state:
        return str(state)
    try:
        with _quiet_client():
            raw = service._client.task_status(task_id)
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    if raw.get("error_code") not in (0, None):
        return "ERROR"
    value = raw.get("task_state")
    if value is None:
        return None
    return STATUS_MAP.get(str(value)) or STATUS_MAP.get(str(value).lower())


def task_status(service, task_id: str) -> dict[str, Any]:
    state = _mapped_status(service, task_id)
    return {"status": "success", "task_id": task_id, "task_status": state}


def task_detail(service, task_id: str) -> dict[str, Any]:
    if not key_present():
        return {"status": "blocked", "reason": "GJQ_API_KEY ausente"}
    with _quiet_client():
        detail = service.task_detail(task_id)
    return {"status": "success", "task_id": task_id, "detail": detail}


def task_result(service, task_id: str, *, timeout: float = 120.0) -> dict[str, Any]:
    """Lê counts; usa o RuntimeJob como fallback se o wrapper devolver vazio."""
    with _quiet_client():
        try:
            result = service.task_result(task_id)
        except Exception:
            result = None
    if result:
        return {"status": "success", "task_id": task_id, "result": result}
    try:
        from gjq_client.gjq_runtime.runtime_job import RuntimeJob

        with _quiet_client():
            detail = service.task_detail(task_id)
            job = RuntimeJob(
                service._client,
                task_id,
                backend_name=detail.get("backend_name") if isinstance(detail, dict) else None,
                shots=detail.get("shots") if isinstance(detail, dict) else None,
                circuit_type="sampler",
            )
            result = job.result(timeout=timeout)
    except Exception:
        result = None
    return {"status": "success" if result else "unavailable", "task_id": task_id, "result": result}


def wait_for_result(
    service,
    task_id: str,
    *,
    timeout: float = 600.0,
    poll_interval: float = 2.0,
) -> dict[str, Any]:
    """Consulta o status sem polling apertado e devolve o resultado final."""
    started = time.monotonic()
    last_status = None
    while True:
        status = _mapped_status(service, task_id)
        last_status = status
        if status in FINAL_STATES:
            break
        if time.monotonic() - started >= timeout:
            return {
                "status": "timeout",
                "task_id": task_id,
                "task_status": last_status,
                "waited_seconds": round(time.monotonic() - started, 3),
                "result": None,
                "detail": None,
            }
        time.sleep(poll_interval)
    result = task_result(service, task_id) if status == "DONE" else {"result": None}
    detail = task_detail(service, task_id)
    return {
        "status": "done" if status == "DONE" else str(status).lower(),
        "task_id": task_id,
        "task_status": status,
        "waited_seconds": round(time.monotonic() - started, 3),
        "result": result.get("result"),
        "detail": detail.get("detail"),
    }


def audit_counts(counts: Any, shots: int | None = None) -> dict[str, Any]:
    """Audita a soma dos counts e calcula probabilidades e erro padrão."""
    if not isinstance(counts, dict) or not counts:
        return {"ok": False, "reason": "counts vazio ou inválido", "blocks": []}
    total = sum(int(v) for v in counts.values())
    probabilities = {
        str(k): (int(v) / total if total else 0.0) for k, v in counts.items()
    }
    standard_error = {
        key: math.sqrt(p * (1.0 - p) / total) if total else 0.0
        for key, p in probabilities.items()
    }
    expected = int(shots) if isinstance(shots, int) and not isinstance(shots, bool) else total
    return {
        "ok": total == expected,
        "total": total,
        "shots_expected": expected,
        "alert": None if total == expected else f"soma {total} != shots {expected}",
        "probabilities": {k: round(v, 9) for k, v in probabilities.items()},
        "standard_error": {k: round(v, 9) for k, v in standard_error.items()},
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def observed_metrics(
    counts: Any,
    ideal_distribution: dict[str, float] | None = None,
) -> dict[str, Any] | None:
    """Métricas descritivas dos counts; não são fidelidade de estado."""
    if not isinstance(counts, dict) or not counts:
        return None
    total = sum(int(v) for v in counts.values())
    if total <= 0:
        return None
    probabilities = {str(k): int(v) / total for k, v in counts.items()}
    correlated = probabilities.get("00", 0.0) + probabilities.get("11", 0.0)
    out: dict[str, Any] = {
        "total": total,
        "probabilities": {k: round(v, 9) for k, v in probabilities.items()},
        "correlated_00_11": correlated,
        "correlated_standard_error": math.sqrt(
            correlated * (1.0 - correlated) / total
        ) if 0.0 <= correlated <= 1.0 else None,
        "note": (
            "A fração 00/11 é uma taxa de outcomes correlacionados, não "
            "fidelidade de estado nem prova de emaranhamento."
        ),
    }
    if ideal_distribution:
        keys = set(probabilities) | set(ideal_distribution)
        out["tvd_vs_ideal"] = 0.5 * sum(
            abs(probabilities.get(k, 0.0) - ideal_distribution.get(k, 0.0))
            for k in keys
        )
        out["ideal_distribution"] = dict(ideal_distribution)
    return out


def execution_record(
    *,
    profile: HardwareProfile,
    result,
    submission: dict[str, Any],
    qasm2: str,
    qasm3: str,
    wait: dict[str, Any] | None = None,
    counts: Any = None,
    ideal_distribution: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Monta o registro de proveniência de uma submissão."""
    audit = audit_counts(counts, submission.get("shots")) if counts is not None else None
    observed = observed_metrics(counts, ideal_distribution) if counts is not None else None
    return {
        "schema_version": 1,
        "task_id": submission.get("task_id"),
        "backend": submission.get("backend"),
        "hardware": submission.get("hardware"),
        "shots": submission.get("shots"),
        "submitted_at": submission.get("submitted_at"),
        "transpile": False,
        "profile_name": profile.name,
        "profile_kind": profile.profile_kind,
        "profile_fingerprint": profile.target_fingerprint,
        "calibration_source": profile.calibration_source,
        "last_update_date": profile.last_update_date,
        "strategy": result.strategy,
        "chosen_layout_kind": result.chosen.layout_kind,
        "chosen_optimization_level": result.chosen.optimization_level,
        "chosen_seed": result.chosen.seed,
        "chosen_metrics": result.chosen.metrics,
        "chosen_estimate": result.chosen.estimate,
        "baseline_metrics": result.baseline.metrics,
        "baseline_estimate": result.baseline.estimate,
        "qasm2_sha256": _sha256_text(qasm2),
        "qasm3_sha256": _sha256_text(qasm3),
        "wait": wait,
        "counts": counts,
        "counts_audit": audit,
        "observed": observed,
        "limits": (
            "Uma execução não prova fidelidade, emaranhamento, vantagem quântica "
            "ou interpretação de Bohm. O proxy de erro não é calibração."
        ),
    }
