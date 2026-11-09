"""MCP Core-native para pesquisa quântica na plataforma GJQ/CETC-ICQ (R1099).

Usa `gjq-client==0.2.1` e Qiskit 2.3.0. Diferente do servidor oficial
`gjq-runtime-mcp-server`, este wrapper:
  - exige `confirm=True` para submeter qualquer job;
  - bloqueia hardware (`Guoji08`, `Baihua`) sem `allow_hardware=True`;
  - não expõe ferramenta que aceite API key no prompt;
  - não executa comandos externos nem avalia código arbitrário;
  - mantém stdout limpo para o transporte stdio do MCP.

Limites: 200 qubits, 100.000 shots, 50.000 caracteres de QASM e 20 submissões
por processo. Nenhum job é submetido sem `GJQ_API_KEY` no ambiente.
"""
from __future__ import annotations

import contextlib
import math
import os
import sys
import threading
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from integrations.gjq_backend_registry import BACKENDS, is_hardware_name

DEFAULT_MAX_QUBITS = 200
MAX_QUBITS_CAP = 997
MAX_QASM_CHARS = 50_000
DEFAULT_MAX_SHOTS = 100_000
DEFAULT_MAX_SUBMISSIONS = 20
HARDWARE_BACKENDS = {
    backend.id for backend in BACKENDS if backend.requires_allow_hardware
}

_service = None
_service_lock = threading.Lock()
_submission_count = 0
_submission_lock = threading.Lock()


def _import_gjq():
    try:
        import gjq_client
        from gjq_client import (
            Estimator,
            GJQRuntimeService,
            Sampler,
            generate_preset_pass_manager,
        )
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise RuntimeError(
            "gjq-client ausente. Instale gjq-client==0.2.1 no .venv-quantum."
        ) from exc
    return gjq_client, GJQRuntimeService, Sampler, Estimator, generate_preset_pass_manager


def _max_qubits() -> int:
    raw = os.environ.get("GJQ_MAX_QUBITS", "")
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_QUBITS
    return min(value, MAX_QUBITS_CAP) if value > 0 else DEFAULT_MAX_QUBITS


def _max_shots() -> int:
    raw = os.environ.get("GJQ_MAX_SHOTS", "")
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_SHOTS
    return value if value > 0 else DEFAULT_MAX_SHOTS


def _max_submissions() -> int:
    raw = os.environ.get("GJQ_MAX_SUBMISSIONS_PER_SESSION", "")
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_MAX_SUBMISSIONS
    return value if value > 0 else DEFAULT_MAX_SUBMISSIONS


def _key_present() -> bool:
    return bool(os.environ.get("GJQ_API_KEY", "").strip())


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "tolist"):
        try:
            return _jsonable(value.tolist())
        except Exception:
            pass
    if hasattr(value, "to_dict"):
        try:
            return _jsonable(value.to_dict())
        except Exception:
            pass
    if hasattr(value, "item"):
        try:
            return _jsonable(value.item())
        except Exception:
            pass
    return str(value)


@contextlib.contextmanager
def _stdout_to_stderr():
    """O SDK imprime tabelas em stdout; stdio MCP exige stdout limpo."""
    with contextlib.redirect_stdout(sys.stderr):
        yield


def _get_service():
    global _service
    if _service is not None:
        return _service
    with _service_lock:
        if _service is not None:
            return _service
        if not _key_present():
            raise RuntimeError("GJQ_API_KEY ausente no ambiente")
        _, GJQRuntimeService, _, _, _ = _import_gjq()
        channel = os.environ.get("GJQ_CHANNEL", "gjq_cloud")
        with _stdout_to_stderr():
            _service = GJQRuntimeService(
                api_key=os.environ["GJQ_API_KEY"],
                channel=channel,
            )
        return _service


def _validate_shots(shots: int) -> None:
    if isinstance(shots, bool) or not isinstance(shots, int):
        raise ValueError("shots deve ser inteiro")
    limit = _max_shots()
    if not 1 <= shots <= limit:
        raise ValueError(f"shots deve estar entre 1 e {limit}")


def _parse_qasm(qasm: str):
    from qiskit import QuantumCircuit, qasm2, qasm3

    if not isinstance(qasm, str) or not qasm.strip():
        raise ValueError("qasm obrigatório")
    if len(qasm) > MAX_QASM_CHARS:
        raise ValueError(f"qasm excede {MAX_QASM_CHARS} caracteres")
    try:
        circuit = qasm3.loads(qasm)
    except Exception:
        try:
            circuit = qasm2.loads(qasm)
        except Exception:
            try:
                circuit = QuantumCircuit.from_qasm_str(qasm)
            except Exception as exc:
                raise ValueError(f"OpenQASM inválido: {exc}") from exc
    if circuit.num_qubits < 1:
        raise ValueError("o circuito não tem qubits")
    limit = _max_qubits()
    if circuit.num_qubits > limit:
        raise ValueError(f"o circuito excede {limit} qubits")
    return circuit


def _is_hardware(backend_name: str) -> bool:
    """Gate conservador: aliases de hardware/emulação exigem allow_hardware."""
    return is_hardware_name(backend_name)


def _reserve_submission() -> int:
    global _submission_count
    limit = _max_submissions()
    with _submission_lock:
        if _submission_count >= limit:
            raise RuntimeError(
                f"limite de {limit} submissões por processo atingido; reinicie o MCP"
            )
        _submission_count += 1
        return _submission_count


def _release_submission() -> None:
    global _submission_count
    with _submission_lock:
        if _submission_count > 0:
            _submission_count -= 1


def _submission_count_value() -> int:
    with _submission_lock:
        return _submission_count


def _job_id(job: Any) -> str:
    if hasattr(job, "job_id"):
        try:
            return str(job.job_id())
        except Exception:
            pass
    raw = getattr(job, "_job_id", None)
    if isinstance(raw, (list, tuple)):
        if len(raw) != 1:
            raise RuntimeError(f"esperado um task_id, recebido {len(raw)}")
        raw = raw[0]
    if raw is None or not str(raw).strip():
        raise RuntimeError("o job não retornou task_id")
    return str(raw)


def _prepare_circuit(backend: Any, qasm: str, transpile: bool, optimization_level: int):
    _, _, _, _, generate_preset_pass_manager = _import_gjq()
    circuit = _parse_qasm(qasm)
    if transpile:
        pm = generate_preset_pass_manager(
            backend=backend, optimization_level=optimization_level
        )
        circuit = pm.run(circuit)
    return circuit


def _distribution(counts: dict[str, int]) -> dict[str, Any]:
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("counts vazio")
    probabilities = {k: v / total for k, v in counts.items()}
    standard_error = {
        k: math.sqrt(p * (1 - p) / total) if total else 0.0
        for k, p in probabilities.items()
    }
    return {
        "total": total,
        "probabilities": {k: round(v, 9) for k, v in probabilities.items()},
        "standard_error": {k: round(v, 9) for k, v in standard_error.items()},
    }


def create_server() -> FastMCP:
    server = FastMCP("gjq-runtime")
    readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    network_read = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=True)
    submit = ToolAnnotations(readOnlyHint=False, destructiveHint=True, openWorldHint=True)

    @server.tool(name="gjq_runtime_status", annotations=readonly)
    def gjq_runtime_status() -> dict:
        """Versão do SDK, limites e presença da chave; não acessa a rede."""
        try:
            gjq_client, _, _, _, _ = _import_gjq()
            sdk_version = getattr(gjq_client, "__version__", None)
            sdk_present = True
        except RuntimeError:
            sdk_version = None
            sdk_present = False
        return {
            "sdk_present": sdk_present,
            "sdk_version": sdk_version,
            "api_key_present": _key_present(),
            "channel": os.environ.get("GJQ_CHANNEL", "gjq_cloud"),
            "max_shots": _max_shots(),
            "max_submissions": _max_submissions(),
            "submissions_used": _submission_count_value(),
            "max_qubits": _max_qubits(),
            "max_qubits_default": DEFAULT_MAX_QUBITS,
            "max_qubits_env": "GJQ_MAX_QUBITS",
            "max_qubits_cap": MAX_QUBITS_CAP,
            "hardware_backends": sorted(
                {backend.api_name or backend.display_name for backend in BACKENDS
                 if backend.requires_allow_hardware}
            ),
            "hardware_backend_ids": sorted(HARDWARE_BACKENDS),
            "confirm_required": True,
            "allow_hardware_required": True,
            "executed": False,
            "network_access": False,
        }

    @server.tool(name="gjq_list_backends", annotations=network_read)
    def gjq_list_backends() -> dict:
        """Lista backends disponíveis; requer GJQ_API_KEY e acessa a nuvem."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        with _stdout_to_stderr():
            backends = _get_service().list_backends()
        backends = _jsonable(backends)
        return {"status": "success", "total": len(backends), "backends": backends}

    @server.tool(name="gjq_least_busy", annotations=network_read)
    def gjq_least_busy() -> dict:
        """Retorna o backend com menor fila; pode ser simulador."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        with _stdout_to_stderr():
            backend = _get_service().least_busy()
        return {
            "status": "success",
            "backend_name": getattr(backend, "name", str(backend)),
            "note": "least_busy pode retornar simulador; confirme o tipo antes de assumir hardware.",
        }

    @server.tool(name="gjq_backend_config", annotations=network_read)
    def gjq_backend_config(backend_name: str) -> dict:
        """Configuração estática do backend (portas, acoplamentos, qubits)."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        with _stdout_to_stderr():
            backend = _get_service().backend(backend_name)
            if backend is None:
                raise ValueError(f"backend '{backend_name}' indisponível")
            config = backend.configuration()
        return {"status": "success", "backend": backend_name, "configuration": _jsonable(config)}

    @server.tool(name="gjq_backend_properties", annotations=network_read)
    def gjq_backend_properties(backend_name: str) -> dict:
        """Propriedades de calibração; pode retornar null em simuladores."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        with _stdout_to_stderr():
            backend = _get_service().backend(backend_name)
            if backend is None:
                raise ValueError(f"backend '{backend_name}' indisponível")
            props = backend.properties()
        return {"status": "success", "backend": backend_name, "properties": _jsonable(props)}

    @server.tool(name="gjq_sample", annotations=submit)
    def gjq_sample(
        qasm: str,
        backend_name: str,
        shots: int = 1024,
        optimization_level: int = 1,
        transpile: bool = True,
        amplitude_index: list[int] | None = None,
        allow_hardware: bool = False,
        confirm: bool = False,
    ) -> dict:
        """Submete sampling; exige confirm=True e GJQ_API_KEY."""
        if confirm is not True:
            raise ValueError("confirm=True é obrigatório para submeter sampling")
        _validate_shots(shots)
        if optimization_level not in range(4):
            raise ValueError("optimization_level deve estar entre 0 e 3")
        if _is_hardware(backend_name) and not allow_hardware:
            return {
                "status": "blocked",
                "reason": "hardware exige allow_hardware=True e revisão de custo",
                "backend": backend_name,
                "executed": False,
            }
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        _, _, Sampler, _, _ = _import_gjq()
        with _stdout_to_stderr():
            service = _get_service()
            backend = service.backend(backend_name)
            if backend is None:
                raise ValueError(f"backend '{backend_name}' indisponível")
            circuit = _prepare_circuit(backend, qasm, transpile, optimization_level)
            slot = _reserve_submission()
            try:
                job = Sampler(backend=backend).run(
                    circuit, shots=shots, amplitude_index=amplitude_index
                )
                task_id = _job_id(job)
            except Exception:
                _release_submission()
                raise
        return {
            "status": "success",
            "task_id": task_id,
            "backend": backend_name,
            "shots": shots,
            "hardware": _is_hardware(backend_name),
            "submissions_used": slot,
            "executed": True,
            "note": "Use gjq_task_status e gjq_task_result; não reenvie o mesmo circuito.",
        }

    @server.tool(name="gjq_estimate", annotations=submit)
    def gjq_estimate(
        qasm: str,
        backend_name: str,
        observable: list,
        shots: int = 1024,
        optimization_level: int = 1,
        transpile: bool = True,
        amplitude_index: list[int] | None = None,
        allow_hardware: bool = False,
        confirm: bool = False,
    ) -> dict:
        """Submete estimativa de valor esperado; exige confirm=True."""
        if confirm is not True:
            raise ValueError("confirm=True é obrigatório para submeter estimativa")
        _validate_shots(shots)
        if optimization_level not in range(4):
            raise ValueError("optimization_level deve estar entre 0 e 3")
        if not isinstance(observable, list) or not observable:
            raise ValueError("observable deve ser uma lista [['ZZ', 1.0], ...]")
        if _is_hardware(backend_name) and not allow_hardware:
            return {
                "status": "blocked",
                "reason": "hardware exige allow_hardware=True e revisão de custo",
                "backend": backend_name,
                "executed": False,
            }
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente", "executed": False}
        from qiskit.quantum_info import SparsePauliOp

        _, _, _, Estimator, _ = _import_gjq()
        obs = SparsePauliOp.from_list(
            [(str(term), complex(coeff)) for term, coeff in observable]
        )
        with _stdout_to_stderr():
            service = _get_service()
            backend = service.backend(backend_name)
            if backend is None:
                raise ValueError(f"backend '{backend_name}' indisponível")
            circuit = _prepare_circuit(backend, qasm, transpile, optimization_level)
            slot = _reserve_submission()
            try:
                job = Estimator(backend=backend).run(
                    circuit,
                    shots=shots,
                    observable=obs,
                    amplitude_index=amplitude_index,
                )
                task_id = _job_id(job)
            except Exception:
                _release_submission()
                raise
        return {
            "status": "success",
            "task_id": task_id,
            "backend": backend_name,
            "shots": shots,
            "hardware": _is_hardware(backend_name),
            "submissions_used": slot,
            "executed": True,
        }

    @server.tool(name="gjq_task_status", annotations=network_read)
    def gjq_task_status(task_id: str) -> dict:
        """Consulta não bloqueante do estado da tarefa."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente"}
        with _stdout_to_stderr():
            state = _get_service().task_status(task_id)
        return {"status": "success", "task_id": task_id, "task_status": _jsonable(state)}

    @server.tool(name="gjq_task_result", annotations=network_read)
    def gjq_task_result(task_id: str, observable: list | None = None) -> dict:
        """Lê o resultado; se houver counts, inclui auditoria da soma."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente"}
        from qiskit.quantum_info import SparsePauliOp

        obs = None
        if observable:
            obs = SparsePauliOp.from_list(
                [(str(term), complex(coeff)) for term, coeff in observable]
            )
        with _stdout_to_stderr():
            service = _get_service()
            result = service.task_result(task_id, observable=obs)
            state = service.task_status(task_id)
        result = _jsonable(result)
        audit = None
        if isinstance(result, dict) and all(
            isinstance(v, int) for v in result.values()
        ) and result:
            audit = _distribution(result)
            audit["ok"] = True
        return {
            "status": "success",
            "task_id": task_id,
            "task_status": _jsonable(state),
            "result": result,
            "audit": audit,
            "limit": "Soma correta não prova fidelidade, emaranhamento ou vantagem quântica.",
        }

    @server.tool(name="gjq_task_detail", annotations=network_read)
    def gjq_task_detail(task_id: str) -> dict:
        """Detalhes da tarefa (backend, shots, horário)."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente"}
        with _stdout_to_stderr():
            detail = _get_service().task_detail(task_id)
        return {"status": "success", "task_id": task_id, "detail": _jsonable(detail)}

    @server.tool(name="gjq_list_tasks", annotations=network_read)
    def gjq_list_tasks() -> dict:
        """Lista as tarefas ativas do usuário."""
        if not _key_present():
            return {"status": "blocked", "reason": "GJQ_API_KEY ausente"}
        with _stdout_to_stderr():
            tasks = _get_service().list_tasks()
        tasks = _jsonable(tasks)
        return {"status": "success", "total": len(tasks), "tasks": tasks}

    @server.tool(name="gjq_audit_counts", annotations=readonly)
    def gjq_audit_counts(counts: dict[str, int], shots: int | None = None) -> dict:
        """Audita counts localmente, sem rede."""
        if not isinstance(counts, dict) or not counts:
            raise ValueError("counts deve ser um dicionário não vazio")
        normalized: dict[str, int] = {}
        for key, value in counts.items():
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("cada count deve ser inteiro não negativo")
            normalized[str(key)] = value
        distribution = _distribution(normalized)
        alerts = []
        if shots is not None:
            _validate_shots(shots)
            if distribution["total"] != shots:
                alerts.append(f"soma {distribution['total']} != shots {shots}")
        return {
            "ok": not alerts,
            "total": distribution["total"],
            "probabilities": distribution["probabilities"],
            "standard_error": distribution["standard_error"],
            "alerts": alerts,
            "limit": "Soma correta não prova fidelidade, emaranhamento ou vantagem quântica.",
        }

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
