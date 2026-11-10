"""R1139 — provider GJQ de primeira classe para o OpenCode Ecosystem Core.

Reúne, em um contrato único:

- credencial por ambiente ou conta cacheada (sem expor a chave);
- gates de confirmação/hardware;
- orçamento diário local;
- execução via SDK `gjq-client`;
- proveniência com hash do QASM submetido;
- status/resultado/auditoria de counts;
- auditoria local de compilação/layout.

Nada aqui executa hardware sem `confirm=True` e `allow_hardware=True`.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import sys
from datetime import datetime
from typing import Any

from qiskit import qasm2, qasm3, transpile
from qiskit import QuantumCircuit

from gjq_hardware_opt.execution import (
    MissingGJQKey,
    audit_counts,
    cached_account_present,
    connect_gjq,
    credential_present,
    key_present,
    submission_gate,
    submit_optimized,
    task_result,
    task_status,
)
from integrations.gjq_backend_registry import is_hardware_name
from integrations.gjq_budget import (
    budget_limits,
    check_budget,
    record_submission,
    usage_today,
)
from integrations.gjq_verified_snapshot import registry_sha256
from quantum_mitigation.compilation_audit import build_physical_circuit, audit_layout

LIMITS = (
    "Provider local. Não executa hardware sem confirmação explícita. "
    "O orçamento é local e não representa preço oficial. O layout do servidor "
    "não é devolvido; a auditoria de compilação é local."
)


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "to_dict"):
        try:
            return _jsonable(value.to_dict())
        except Exception:
            pass
    return str(value)


def _parse_qasm(qasm: str) -> QuantumCircuit:
    if not isinstance(qasm, str) or not qasm.strip():
        raise ValueError("qasm obrigatório")
    try:
        return qasm3.loads(qasm)
    except Exception:
        try:
            return qasm2.loads(qasm)
        except Exception:
            try:
                return QuantumCircuit.from_qasm_str(qasm)
            except Exception as exc:
                raise ValueError(f"OpenQASM inválido: {exc}") from exc


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(sys.stderr):
        yield


def _sdk_version() -> str:
    try:
        import gjq_client

        return str(getattr(gjq_client, "__version__", "unknown"))
    except Exception:
        return "absent"


def status() -> dict:
    """Inventário local; não abre rede nem lê a chave."""
    return {
        "schema_version": 1,
        "sdk": _sdk_version(),
        "credential": (
            "env_key"
            if key_present()
            else "cached_account"
            if cached_account_present()
            else "absent"
        ),
        "cached_account_present": cached_account_present(),
        "registry_sha256": registry_sha256(),
        "budget": {
            "limits": budget_limits(),
            "usage_today": usage_today(),
        },
        "compilation_audit": True,
        "hardware_executed": False,
        "network_access": False,
        "limits": LIMITS,
    }


def _service(use_cached_account: bool):
    from gjq_client import GJQRuntimeService

    key = os.environ.get("GJQ_API_KEY", "").strip()
    if not key and not (use_cached_account and cached_account_present()):
        raise MissingGJQKey("GJQ_API_KEY ausente e conta cacheada indisponível")
    with _quiet():
        if key:
            return GJQRuntimeService(
                api_key=key,
                channel=os.environ.get("GJQ_CHANNEL", "gjq_cloud"),
            )
        return GJQRuntimeService(channel=os.environ.get("GJQ_CHANNEL", "gjq_cloud"))


def list_backends(*, use_cached_account: bool = False) -> dict:
    if not credential_present(use_cached_account):
        return {"status": "blocked", "reason": "credencial GJQ ausente", "executed": False}
    service = _service(use_cached_account)
    with _quiet():
        backends = service.list_backends()
    return {
        "status": "success",
        "backends": [_jsonable(item) for item in backends],
        "executed": False,
        "network_access": True,
    }


def submit(
    qasm: str,
    backend_name: str,
    *,
    shots: int = 1024,
    confirm: bool = False,
    allow_hardware: bool = False,
    use_cached_account: bool = False,
    optimization_level: int = 1,
    transpile_circuit: bool = True,
    amplitude_index: list[int] | None = None,
    compile: bool | None = None,
    initial_layout: list[int] | None = None,
) -> dict:
    if confirm is not True:
        return {"status": "blocked", "reason": "confirm=True é obrigatório", "executed": False}
    if isinstance(shots, bool) or not isinstance(shots, int) or shots < 1:
        return {"status": "blocked", "reason": "shots deve ser inteiro >= 1", "executed": False}
    if optimization_level not in range(4):
        return {"status": "blocked", "reason": "optimization_level deve estar em 0..3", "executed": False}
    if not credential_present(use_cached_account):
        return {"status": "blocked", "reason": "credencial GJQ ausente", "executed": False}
    hardware = bool(is_hardware_name(backend_name))
    if hardware and not allow_hardware:
        return {
            "status": "blocked",
            "reason": "hardware exige allow_hardware=True",
            "backend": backend_name,
            "executed": False,
        }
    budget = check_budget(backend_name, shots, hardware)
    if not budget["allowed"]:
        return {"status": "blocked", "reason": budget["reason"], "budget": budget, "executed": False}
    circuit = _parse_qasm(qasm)
    if not any(instruction.operation.name == "measure" for instruction in circuit.data):
        return {"status": "blocked", "reason": "o circuito precisa de medição", "executed": False}
    service = _service(use_cached_account)
    with _quiet():
        backend = service.backend(backend_name)
    if backend is None:
        return {"status": "blocked", "reason": f"backend indisponível: {backend_name}", "executed": False}
    if transpile_circuit:
        transpile_kwargs = {
            "backend": backend,
            "optimization_level": optimization_level,
        }
        if initial_layout is not None:
            transpile_kwargs["initial_layout"] = list(initial_layout)
        circuit = transpile(circuit, **transpile_kwargs)
    final_layout = circuit.layout.final_index_layout() if circuit.layout else None
    active_physical = sorted({
        circuit.find_bit(qubit).index
        for instruction in circuit.data
        for qubit in instruction.qubits
    })
    gate = submission_gate(
        backend_name,
        shots=shots,
        circuit=circuit,
        confirm=True,
        allow_hardware=allow_hardware,
        api_key_present=True,
    )
    if not gate["allowed"]:
        return {"status": "blocked", "reason": gate["reason"], "gate": gate, "executed": False}
    submission = submit_optimized(
        backend,
        circuit,
        shots=shots,
        confirm=True,
        allow_hardware=allow_hardware,
        api_key_present=True,
        amplitude_index=amplitude_index,
        options=None if compile is None else {"compile": bool(compile)},
    )
    submitted_qasm = qasm2.dumps(circuit)
    digest = hashlib.sha256(submitted_qasm.encode()).hexdigest()
    record_submission(
        backend_name,
        shots,
        submission["task_id"],
        hardware,
        qasm_sha256=digest,
    )
    return {
        "schema_version": 1,
        "status": "submitted",
        "task_id": submission["task_id"],
        "backend": backend_name,
        "shots": int(shots),
        "hardware": hardware,
        "cached_account": bool(use_cached_account and not key_present()),
        "transpile": bool(transpile_circuit),
        "optimization_level": int(optimization_level),
        "compile": None if compile is None else bool(compile),
        "initial_layout": None if initial_layout is None else list(initial_layout),
        "final_index_layout": final_layout,
        "active_physical": active_physical,
        "qasm_sha256": digest,
        "submitted_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "budget_after": {
            "limits": budget_limits(),
            "usage_today": usage_today(),
        },
        "executed": True,
        "network_access": True,
        "limits": LIMITS,
    }


def result(
    task_id: str,
    *,
    shots: int | None = None,
    use_cached_account: bool = False,
) -> dict:
    if not isinstance(task_id, str) or not task_id.strip():
        return {"status": "blocked", "reason": "task_id obrigatório", "executed": False}
    if not credential_present(use_cached_account):
        return {"status": "blocked", "reason": "credencial GJQ ausente", "executed": False}
    service = _service(use_cached_account)
    state = task_status(service, task_id)
    if state.get("task_status") not in {"DONE", "ERROR", "CANCELLED"}:
        return {
            "status": "not_final",
            "task_id": task_id,
            "task_status": state.get("task_status"),
            "executed": False,
        }
    payload = task_result(service, task_id)
    counts = payload.get("result") if isinstance(payload, dict) else None
    audit = audit_counts(counts, shots) if counts else None
    return {
        "schema_version": 1,
        "status": "success",
        "task_id": task_id,
        "task_status": state.get("task_status"),
        "result": counts,
        "counts_audit": audit,
        "executed": False,
        "network_access": True,
    }


def compilation_audit(
    backend_name: str,
    pair: tuple[int, int] = (106, 107),
    *,
    use_cached_account: bool = False,
) -> dict:
    if not credential_present(use_cached_account):
        return {"status": "blocked", "reason": "credencial GJQ ausente", "executed": False}
    service = _service(use_cached_account)
    with _quiet():
        backend = service.backend(backend_name)
        if backend is None:
            return {"status": "blocked", "reason": "backend indisponível", "executed": False}
        target = backend.target
    num_qubits = int(getattr(target, "num_qubits", 0) or 0)
    if num_qubits <= 0:
        return {"status": "blocked", "reason": "Target sem num_qubits", "executed": False}
    circuit = build_physical_circuit(pair, num_qubits=num_qubits)
    audit = audit_layout(circuit, backend, initial_layout=list(range(num_qubits)))
    return {
        "status": "success",
        "backend": backend_name,
        "audit": audit,
        "executed": False,
        "network_access": True,
        "limits": audit.get("limits"),
    }
