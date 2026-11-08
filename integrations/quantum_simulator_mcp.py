"""MCP nativo de simulação quântica do Core (R1099).

Substitui a imagem Docker de terceiro `ychen94/quantum-simulator-mcp` por um
servidor local auditável, com Qiskit 2.x e Qiskit Aer. Não executa código
arbitrário, não acessa rede, não lê segredos e não grava arquivos.

Limites: 12 qubits, 10.000 shots e 50.000 caracteres de OpenQASM 2.0.
"""
from __future__ import annotations

import logging
import math
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

# O transporte stdio exige stdout limpo. Qiskit emite logs de transpilação
# em INFO; sem esta supressão, o JSON-RPC seria corrompido.
for _logger_name in ("qiskit", "qiskit_aer"):
    logging.getLogger(_logger_name).setLevel(logging.WARNING)

MAX_QUBITS = 12
MAX_SHOTS = 10_000
MAX_QASM_CHARS = 50_000
NOISE_MODELS = {
    "none": "Simulação ideal, sem ruído.",
    "depolarizing": "Ruído depolarizante; parâmetros: error_rate e two_qubit_error_rate opcional.",
    "thermal_relaxation": "Relaxação térmica; parâmetros: t1, t2 e gate_time.",
    "readout_error": "Erro de leitura; parâmetros: prob_0_to_1 e prob_1_to_0.",
}


def _import_qiskit():
    try:
        import qiskit
        import qiskit_aer
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise RuntimeError(
            "Qiskit/Qiskit Aer ausentes. Use .venv-quantum/bin/python."
        ) from exc
    return qiskit, qiskit_aer, QuantumCircuit, transpile, AerSimulator


def _validate_shots(shots: int) -> None:
    if isinstance(shots, bool) or not isinstance(shots, int):
        raise ValueError("shots deve ser inteiro")
    if not 1 <= shots <= MAX_SHOTS:
        raise ValueError(f"shots deve estar entre 1 e {MAX_SHOTS}")


def _parse_qasm(qasm_code: str):
    _, _, QuantumCircuit, _, _ = _import_qiskit()
    if not isinstance(qasm_code, str) or not qasm_code.strip():
        raise ValueError("qasm_code obrigatório")
    if len(qasm_code) > MAX_QASM_CHARS:
        raise ValueError(f"qasm_code excede {MAX_QASM_CHARS} caracteres")
    try:
        circuit = QuantumCircuit.from_qasm_str(qasm_code)
    except Exception as exc:
        raise ValueError(f"OpenQASM 2.0 inválido: {exc}") from exc
    if circuit.num_qubits < 1:
        raise ValueError("o circuito não tem qubits")
    if circuit.num_qubits > MAX_QUBITS:
        raise ValueError(f"o circuito excede {MAX_QUBITS} qubits")
    return circuit


def _noise_model(name: str, params: dict[str, float] | None):
    from qiskit_aer.noise import (
        NoiseModel,
        ReadoutError,
        depolarizing_error,
        thermal_relaxation_error,
    )

    if name in (None, "none"):
        return None
    if name not in NOISE_MODELS:
        raise ValueError(f"noise_model deve ser um de {sorted(NOISE_MODELS)}")
    params = dict(params or {})
    model = NoiseModel()

    if name == "depolarizing":
        rate = float(params.get("error_rate", 0.001))
        if not 0.0 <= rate <= 1.0:
            raise ValueError("error_rate deve estar entre 0 e 1")
        gates = ["u1", "u2", "u3", "x", "y", "z", "h", "sx"]
        model.add_all_qubit_quantum_error(depolarizing_error(rate, 1), gates)
        two = params.get("two_qubit_error_rate")
        if two is not None:
            two = float(two)
            if not 0.0 <= two <= 1.0:
                raise ValueError("two_qubit_error_rate deve estar entre 0 e 1")
            model.add_all_qubit_quantum_error(
                depolarizing_error(two, 2), ["cx", "cz", "swap"]
            )
        return model

    if name == "thermal_relaxation":
        missing = [k for k in ("t1", "t2", "gate_time") if k not in params]
        if missing:
            raise ValueError(f"faltam parâmetros: {missing}")
        t1, t2, gate_time = (float(params[k]) for k in ("t1", "t2", "gate_time"))
        if t1 <= 0 or t2 <= 0 or gate_time <= 0:
            raise ValueError("t1, t2 e gate_time devem ser positivos")
        model.add_all_qubit_quantum_error(
            thermal_relaxation_error(t1, min(t2, t1), gate_time),
            ["u1", "u2", "u3", "x", "y", "z", "h", "sx"],
        )
        return model

    # readout_error
    missing = [k for k in ("prob_0_to_1", "prob_1_to_0") if k not in params]
    if missing:
        raise ValueError(f"faltam parâmetros: {missing}")
    p01 = float(params["prob_0_to_1"])
    p10 = float(params["prob_1_to_0"])
    if not (0.0 <= p01 <= 1.0 and 0.0 <= p10 <= 1.0):
        raise ValueError("probabilidades de leitura devem estar entre 0 e 1")
    model.add_all_qubit_readout_error(ReadoutError([[1 - p01, p01], [p10, 1 - p10]]))
    return model


def _merge_counts(raw: Any) -> tuple[dict[str, int], int]:
    if isinstance(raw, dict):
        return {str(k): int(v) for k, v in raw.items()}, 1
    if isinstance(raw, list):
        merged: dict[str, int] = {}
        for index, block in enumerate(raw):
            for key, value in block.items():
                merged[f"{index}:{key}"] = int(value)
        return merged, len(raw)
    raise ValueError("formato de counts não reconhecido")


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
    server = FastMCP("quantum-sim-core")
    readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    compute = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)

    @server.tool(name="sim_status", annotations=readonly)
    def sim_status() -> dict:
        """Informa versões, limites e modelos de ruído sem executar circuito."""
        try:
            qiskit, qiskit_aer, _, _, _ = _import_qiskit()
            available = True
            qiskit_version = qiskit.__version__
            aer_version = qiskit_aer.__version__
        except RuntimeError:
            available = False
            qiskit_version = None
            aer_version = None
        return {
            "qiskit_available": available,
            "qiskit_version": qiskit_version,
            "aer_version": aer_version,
            "max_qubits": MAX_QUBITS,
            "max_shots": MAX_SHOTS,
            "max_qasm_chars": MAX_QASM_CHARS,
            "noise_models": sorted(NOISE_MODELS),
            "writes_files": False,
            "network_access": False,
            "executed": False,
        }

    @server.tool(name="sim_noise_models", annotations=readonly)
    def sim_noise_models() -> dict:
        """Lista os modelos de ruído e seus parâmetros."""
        return dict(NOISE_MODELS)

    @server.tool(name="sim_run_qasm", annotations=compute)
    def sim_run_qasm(
        qasm_code: str,
        shots: int = 1024,
        noise_model: Literal[
            "none", "depolarizing", "thermal_relaxation", "readout_error"
        ] = "none",
        noise_params: dict[str, float] | None = None,
        seed: int = 42,
        confirm: bool = False,
    ) -> dict:
        """Executa OpenQASM 2.0 localmente; exige confirm=True e respeita limites."""
        if confirm is not True:
            raise ValueError("confirm=True é obrigatório para executar a simulação")
        _validate_shots(shots)
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("seed deve ser inteiro")
        circuit = _parse_qasm(qasm_code)
        model = _noise_model(noise_model, noise_params)

        qiskit, qiskit_aer, _, transpile, AerSimulator = _import_qiskit()
        run_circuit = circuit.copy()
        if run_circuit.num_clbits == 0:
            run_circuit.measure_all()
        simulator = AerSimulator(noise_model=model, seed_simulator=seed)
        compiled = transpile(run_circuit, simulator, seed_transpiler=seed)
        result = simulator.run(compiled, shots=shots).result()
        counts, blocks = _merge_counts(result.get_counts())
        distribution = _distribution(counts)

        return {
            "ok": True,
            "counts": counts,
            "probabilities": distribution["probabilities"],
            "standard_error": distribution["standard_error"],
            "metadata": {
                "shots": shots,
                "blocks": blocks,
                "qubits": circuit.num_qubits,
                "clbits": circuit.num_clbits,
                "depth": circuit.depth(),
                "size": len(circuit.data),
                "noise_model": noise_model,
                "seed": seed,
                "qiskit_version": qiskit.__version__,
                "aer_version": qiskit_aer.__version__,
                "executed": True,
                "writes_files": False,
                "network_access": False,
            },
            "limit": (
                "Simulação local não prova fidelidade de hardware, emaranhamento "
                "ou vantagem quântica."
            ),
        }

    @server.tool(name="sim_audit_counts", annotations=readonly)
    def sim_audit_counts(counts: dict[str, int], shots: int | None = None) -> dict:
        """Audita a soma dos counts e calcula probabilidades e erro padrão."""
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
                alerts.append(
                    f"soma {distribution['total']} != shots {shots}"
                )
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
