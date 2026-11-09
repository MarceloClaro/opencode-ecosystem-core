#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Perfil de hardware e extração a partir do Target real do GJQ (R1109).

O perfil é uma fotografia declarada do backend: largura, acoplamentos, portas
base, erros e durações. Ele não é uma promessa de calibração futura.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Iterable

from qiskit.transpiler import Target


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _props_error(props: Any, default: float) -> float:
    value = getattr(props, "error", None)
    if value is None:
        return float(default)
    value = float(value)
    return min(max(value, 0.0), 1.0)


def _props_duration(props: Any) -> float:
    value = getattr(props, "duration", None)
    if value is None:
        return 0.0
    return float(value)


@dataclass
class HardwareProfile:
    """Perfil declarado de um backend quântico.

    ``oneq_error`` e ``twoq_error`` são indexados por porta e por qubit/aresta.
    Arestas são direcionadas; quando o backend tem CX bidirecional, as duas
    direções aparecem no ``coupling_map``.
    """

    name: str
    num_qubits: int
    coupling_map: tuple[tuple[int, int], ...]
    basis_gates: tuple[str, ...]
    oneq_gates: tuple[str, ...]
    twoq_gates: tuple[str, ...]
    oneq_error: dict[str, dict[int, float]]
    twoq_error: dict[str, dict[tuple[int, int], float]]
    readout_error: dict[int, float]
    operational_qubits: tuple[int, ...] = ()
    oneq_duration: dict[str, dict[int, float]] = field(default_factory=dict)
    twoq_duration: dict[str, dict[tuple[int, int], float]] = field(default_factory=dict)
    readout_duration: dict[int, float] = field(default_factory=dict)
    default_error: float = 1e-3
    default_readout_error: float = 1e-2
    profile_kind: str = "synthetic_test"
    calibration_source: str = "declared"
    backend_name: str | None = None
    backend_version: str | None = None
    last_update_date: str | None = None
    target_fingerprint: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self.num_qubits = int(self.num_qubits)
        if self.num_qubits < 1:
            raise ValueError("num_qubits deve ser >= 1")
        self.default_error = float(self.default_error)
        self.default_readout_error = float(self.default_readout_error)
        for label, value in (
            ("default_error", self.default_error),
            ("default_readout_error", self.default_readout_error),
        ):
            if not 0.0 <= value < 1.0:
                raise ValueError(f"{label} deve estar em [0, 1)")

        if self.operational_qubits:
            operational = tuple(sorted({
                int(q) for q in self.operational_qubits
                if 0 <= int(q) < self.num_qubits
            }))
            if not operational:
                raise ValueError("operational_qubits não pode ficar vazio")
        else:
            operational = tuple(range(self.num_qubits))
        self.operational_qubits = operational
        operational_set = set(operational)

        edges: list[tuple[int, int]] = []
        dropped_edges: list[tuple[int, int]] = []
        for edge in self.coupling_map:
            if len(edge) != 2:
                raise ValueError(f"aresta inválida: {edge!r}")
            a, b = int(edge[0]), int(edge[1])
            if a == b:
                raise ValueError(f"auto-aresta inválida: {(a, b)!r}")
            if not (0 <= a < self.num_qubits and 0 <= b < self.num_qubits):
                raise ValueError(f"aresta fora do intervalo: {(a, b)!r}")
            if a not in operational_set or b not in operational_set:
                dropped_edges.append((a, b))
                continue
            edges.append((a, b))
        self.coupling_map = tuple(dict.fromkeys(edges))
        if dropped_edges:
            self.warnings = (*self.warnings, f"arestas com qubit não operacional removidas: {len(dropped_edges)}")

        self.basis_gates = tuple(dict.fromkeys(str(g) for g in self.basis_gates))
        self.oneq_gates = tuple(dict.fromkeys(str(g) for g in self.oneq_gates))
        self.twoq_gates = tuple(dict.fromkeys(str(g) for g in self.twoq_gates))
        if not self.oneq_gates and not self.twoq_gates:
            raise ValueError("o perfil precisa de ao menos uma porta 1q ou 2q")
        for gate in (*self.oneq_gates, *self.twoq_gates):
            if gate not in self.basis_gates:
                self.basis_gates = (*self.basis_gates, gate)

        warnings = list(self.warnings)
        normalized_oneq: dict[str, dict[int, float]] = {}
        for gate in self.oneq_gates:
            by_qubit = {int(q): float(e) for q, e in (self.oneq_error.get(gate) or {}).items()}
            for q in range(self.num_qubits):
                if q not in by_qubit:
                    by_qubit[q] = 0.0 if gate == "rz" else self.default_error
                    if gate != "rz":
                        warnings.append(f"erro 1q ausente: {gate} q{q}; usando default_error")
            for q, e in by_qubit.items():
                if not 0 <= q < self.num_qubits:
                    raise ValueError(f"qubit fora do intervalo em {gate}: {q}")
                if not 0.0 <= e < 1.0:
                    raise ValueError(f"erro 1q inválido em {gate} q{q}: {e}")
            normalized_oneq[gate] = dict(sorted(by_qubit.items()))
        self.oneq_error = normalized_oneq

        edge_set = set(self.coupling_map)
        normalized_twoq: dict[str, dict[tuple[int, int], float]] = {}
        for gate in self.twoq_gates:
            by_edge = {
                (int(a), int(b)): float(e)
                for (a, b), e in (self.twoq_error.get(gate) or {}).items()
            }
            for edge in self.coupling_map:
                if edge not in by_edge:
                    reverse = (edge[1], edge[0])
                    if reverse in by_edge:
                        by_edge[edge] = by_edge[reverse]
                    else:
                        by_edge[edge] = self.default_error
                        warnings.append(
                            f"erro 2q ausente: {gate} {edge[0]}-{edge[1]}; usando default_error"
                        )
            for edge, e in by_edge.items():
                if edge not in edge_set:
                    continue
                if not 0.0 <= e < 1.0:
                    raise ValueError(f"erro 2q inválido em {gate} {edge}: {e}")
            normalized_twoq[gate] = dict(sorted(by_edge.items()))
        self.twoq_error = normalized_twoq

        readout = {int(q): float(e) for q, e in self.readout_error.items()}
        for q in range(self.num_qubits):
            if q not in readout:
                readout[q] = self.default_readout_error
                warnings.append(f"erro de leitura ausente: q{q}; usando default_readout_error")
        for q, e in readout.items():
            if not 0 <= q < self.num_qubits:
                raise ValueError(f"qubit fora do intervalo em readout_error: {q}")
            if not 0.0 <= e < 1.0:
                raise ValueError(f"erro de leitura inválido em q{q}: {e}")
        self.readout_error = dict(sorted(readout.items()))

        self.oneq_duration = {
            gate: {int(q): float(d) for q, d in by_qubit.items()}
            for gate, by_qubit in self.oneq_duration.items()
        }
        self.twoq_duration = {
            gate: {(int(a), int(b)): float(d) for (a, b), d in by_edge.items()}
            for gate, by_edge in self.twoq_duration.items()
        }
        self.readout_duration = {int(q): float(d) for q, d in self.readout_duration.items()}
        self.warnings = tuple(dict.fromkeys(warnings))
        if self.target_fingerprint is None:
            self.target_fingerprint = self.fingerprint()

    # ------------------------------------------------------------------
    # Fingerprint e serialização
    # ------------------------------------------------------------------
    def _fingerprint_payload(self) -> dict[str, Any]:
        return {
            "num_qubits": self.num_qubits,
            "operational_qubits": sorted(self.operational_qubits),
            "coupling_map": sorted(self.coupling_map),
            "basis_gates": sorted(self.basis_gates),
            "oneq_gates": sorted(self.oneq_gates),
            "twoq_gates": sorted(self.twoq_gates),
            "oneq_error": {
                gate: sorted((q, round(e, 12)) for q, e in by_qubit.items())
                for gate, by_qubit in sorted(self.oneq_error.items())
            },
            "twoq_error": {
                gate: sorted((a, b, round(e, 12)) for (a, b), e in by_edge.items())
                for gate, by_edge in sorted(self.twoq_error.items())
            },
            "readout_error": sorted((q, round(e, 12)) for q, e in self.readout_error.items()),
            "default_error": self.default_error,
            "default_readout_error": self.default_readout_error,
        }

    def fingerprint(self) -> str:
        return hashlib.sha256(_canonical_json(self._fingerprint_payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "name": self.name,
            "num_qubits": self.num_qubits,
            "operational_qubits": list(self.operational_qubits),
            "coupling_map": [list(edge) for edge in self.coupling_map],
            "basis_gates": list(self.basis_gates),
            "oneq_gates": list(self.oneq_gates),
            "twoq_gates": list(self.twoq_gates),
            "oneq_error": {
                gate: {str(q): e for q, e in sorted(by_qubit.items())}
                for gate, by_qubit in self.oneq_error.items()
            },
            "twoq_error": {
                gate: {f"{a},{b}": e for (a, b), e in sorted(by_edge.items())}
                for gate, by_edge in self.twoq_error.items()
            },
            "readout_error": {str(q): e for q, e in self.readout_error.items()},
            "oneq_duration": {
                gate: {str(q): d for q, d in sorted(by_qubit.items())}
                for gate, by_qubit in self.oneq_duration.items()
            },
            "twoq_duration": {
                gate: {f"{a},{b}": d for (a, b), d in sorted(by_edge.items())}
                for gate, by_edge in self.twoq_duration.items()
            },
            "readout_duration": {str(q): d for q, d in sorted(self.readout_duration.items())},
            "default_error": self.default_error,
            "default_readout_error": self.default_readout_error,
            "profile_kind": self.profile_kind,
            "calibration_source": self.calibration_source,
            "backend_name": self.backend_name,
            "backend_version": self.backend_version,
            "last_update_date": self.last_update_date,
            "target_fingerprint": self.target_fingerprint,
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HardwareProfile":
        if not isinstance(data, dict):
            raise ValueError("perfil deve ser um objeto JSON")
        oneq_error = {
            gate: {int(q): float(e) for q, e in by_qubit.items()}
            for gate, by_qubit in (data.get("oneq_error") or {}).items()
        }
        twoq_error = {
            gate: {
                (int(parts[0]), int(parts[1])): float(e)
                for key, e in by_edge.items()
                for parts in [str(key).split(",")]
                if len(parts) == 2
            }
            for gate, by_edge in (data.get("twoq_error") or {}).items()
        }
        return cls(
            name=str(data["name"]),
            num_qubits=int(data["num_qubits"]),
            coupling_map=tuple(tuple(int(x) for x in edge) for edge in data.get("coupling_map") or ()),
            basis_gates=tuple(str(g) for g in data.get("basis_gates") or ()),
            oneq_gates=tuple(str(g) for g in data.get("oneq_gates") or ()),
            twoq_gates=tuple(str(g) for g in data.get("twoq_gates") or ()),
            oneq_error=oneq_error,
            twoq_error=twoq_error,
            readout_error={int(q): float(e) for q, e in (data.get("readout_error") or {}).items()},
            operational_qubits=tuple(int(q) for q in data.get("operational_qubits") or ()),
            oneq_duration={
                gate: {int(q): float(d) for q, d in by_qubit.items()}
                for gate, by_qubit in (data.get("oneq_duration") or {}).items()
            },
            twoq_duration={
                gate: {
                    (int(parts[0]), int(parts[1])): float(d)
                    for key, d in by_edge.items()
                    for parts in [str(key).split(",")]
                    if len(parts) == 2
                }
                for gate, by_edge in (data.get("twoq_duration") or {}).items()
            },
            readout_duration={int(q): float(d) for q, d in (data.get("readout_duration") or {}).items()},
            default_error=float(data.get("default_error", 1e-3)),
            default_readout_error=float(data.get("default_readout_error", 1e-2)),
            profile_kind=str(data.get("profile_kind", "saved_profile")),
            calibration_source=str(data.get("calibration_source", "saved_json")),
            backend_name=data.get("backend_name"),
            backend_version=data.get("backend_version"),
            last_update_date=data.get("last_update_date"),
            target_fingerprint=data.get("target_fingerprint"),
            warnings=tuple(str(w) for w in data.get("warnings") or ()),
        )

    # ------------------------------------------------------------------
    # Extração de Target
    # ------------------------------------------------------------------
    @classmethod
    def from_target(
        cls,
        target: Target,
        name: str,
        *,
        profile_kind: str = "synthetic_test",
        calibration_source: str = "qiskit Target",
        backend_name: str | None = None,
        backend_version: str | None = None,
        last_update_date: str | None = None,
        default_error: float = 1e-3,
        default_readout_error: float = 1e-2,
        allowed_edges: Iterable[tuple[int, int]] | None = None,
        operational_qubits: Iterable[int] | None = None,
        faulty_error_threshold: float = 0.999,
        degraded_qubit_threshold: float | None = 0.05,
    ) -> "HardwareProfile":
        """Extrai o perfil de um Target.

        ``allowed_edges`` restringe o coupling_map às arestas operacionais
        declaradas pela configuração do backend. Erros >=
        ``faulty_error_threshold`` são tratados como sentinela de aresta
        indisponível. Qubits com erro 1q >= ``degraded_qubit_threshold`` são
        excluídos do layout.
        """
        if not isinstance(target, Target):
            raise TypeError("target deve ser um qiskit.transpiler.Target")
        if target.num_qubits is None:
            raise ValueError("target sem num_qubits")
        n = int(target.num_qubits)
        warnings: list[str] = []
        oneq_gates: list[str] = []
        twoq_gates: list[str] = []
        oneq_error: dict[str, dict[int, float]] = {}
        twoq_error: dict[str, dict[tuple[int, int], float]] = {}
        oneq_duration: dict[str, dict[int, float]] = {}
        twoq_duration: dict[str, dict[tuple[int, int], float]] = {}
        readout_error: dict[int, float] = {}
        readout_duration: dict[int, float] = {}

        for op_name in list(target.operation_names):
            if op_name == "measure":
                for qarg, props in target[op_name].items():
                    if len(qarg) != 1:
                        warnings.append(f"measure com aridade {len(qarg)} ignorado")
                        continue
                    q = int(qarg[0])
                    readout_error[q] = _props_error(props, default_readout_error)
                    readout_duration[q] = _props_duration(props)
                continue
            if op_name in {"reset", "delay", "barrier"}:
                continue
            qargs = target.qargs_for_operation_name(op_name) or {}
            arities = {len(qarg) for qarg in qargs}
            if not arities:
                warnings.append(f"operação sem qargs ignorada: {op_name}")
                continue
            if arities == {1}:
                oneq_gates.append(op_name)
                oneq_error[op_name] = {}
                oneq_duration[op_name] = {}
                for qarg, props in target[op_name].items():
                    q = int(qarg[0])
                    oneq_error[op_name][q] = _props_error(props, default_error)
                    oneq_duration[op_name][q] = _props_duration(props)
            elif arities == {2}:
                twoq_gates.append(op_name)
                twoq_error[op_name] = {}
                twoq_duration[op_name] = {}
                for qarg, props in target[op_name].items():
                    a, b = int(qarg[0]), int(qarg[1])
                    twoq_error[op_name][(a, b)] = _props_error(props, default_error)
                    twoq_duration[op_name][(a, b)] = _props_duration(props)
            else:
                warnings.append(
                    f"operação com aridade {sorted(arities)} ignorada: {op_name}"
                )

        operational = (
            set(range(n))
            if operational_qubits is None
            else {int(q) for q in operational_qubits if 0 <= int(q) < n}
        )
        if not operational:
            raise ValueError("nenhum qubit operacional no perfil")
        if degraded_qubit_threshold is not None:
            for gate, by_qubit in oneq_error.items():
                if gate == "rz":
                    continue
                for q, error in by_qubit.items():
                    if error >= degraded_qubit_threshold:
                        operational.discard(q)
                        warnings.append(
                            f"qubit {q} excluído do layout: {gate} com erro {error:.3g}"
                        )
        if not operational:
            raise ValueError("todos os qubits foram excluídos por erro degradado")

        allowed = None
        if allowed_edges is not None:
            allowed = {(int(a), int(b)) for a, b in allowed_edges}

        for gate in list(twoq_gates):
            by_edge = twoq_error.get(gate, {})
            by_duration = twoq_duration.get(gate, {})
            filtered: dict[tuple[int, int], float] = {}
            filtered_duration: dict[tuple[int, int], float] = {}
            dropped = 0
            for (a, b), error in by_edge.items():
                if a not in operational or b not in operational:
                    dropped += 1
                    continue
                if error >= faulty_error_threshold:
                    dropped += 1
                    continue
                if allowed is not None and (a, b) not in allowed and (b, a) not in allowed:
                    dropped += 1
                    continue
                filtered[(a, b)] = error
                filtered_duration[(a, b)] = by_duration.get((a, b), 0.0)
            if gate in {"cz", "swap", "iswap"}:
                for (a, b), error in list(filtered.items()):
                    reverse = (b, a)
                    if reverse not in filtered:
                        filtered[reverse] = error
                        filtered_duration[reverse] = filtered_duration.get((a, b), 0.0)
            twoq_error[gate] = filtered
            twoq_duration[gate] = filtered_duration
            if dropped:
                warnings.append(f"{gate}: {dropped} arestas não operacionais removidas")
            if not filtered:
                warnings.append(f"{gate}: nenhuma aresta operacional; porta removida")
        twoq_gates = [gate for gate in twoq_gates if twoq_error.get(gate)]
        edges = sorted({edge for by_edge in twoq_error.values() for edge in by_edge})
        if not edges:
            warnings.append("target sem arestas 2q operacionais; o perfil não tem coupling_map")

        return cls(
            name=str(name),
            num_qubits=n,
            coupling_map=tuple(edges),
            basis_gates=tuple(sorted(set(oneq_gates) | set(twoq_gates))),
            oneq_gates=tuple(sorted(set(oneq_gates))),
            twoq_gates=tuple(sorted(set(twoq_gates))),
            oneq_error=oneq_error,
            twoq_error=twoq_error,
            readout_error=readout_error,
            operational_qubits=tuple(sorted(operational)),
            oneq_duration=oneq_duration,
            twoq_duration=twoq_duration,
            readout_duration=readout_duration,
            default_error=default_error,
            default_readout_error=default_readout_error,
            profile_kind=profile_kind,
            calibration_source=calibration_source,
            backend_name=backend_name or name,
            backend_version=backend_version,
            last_update_date=last_update_date,
            warnings=tuple(warnings),
        )

    @classmethod
    def from_gjq_payloads(
        cls,
        configuration: dict[str, Any],
        properties: dict[str, Any] | None = None,
        *,
        name: str | None = None,
        profile_kind: str = "gjq_saved_payload",
        default_error: float = 1e-3,
        default_readout_error: float = 1e-2,
        faulty_error_threshold: float = 0.999,
        degraded_qubit_threshold: float | None = 0.05,
    ) -> "HardwareProfile":
        """Constrói o perfil a partir dos JSON de config/properties do GJQ.

        O parser é direto para não depender de ``convert_to_target``, que pode
        perder ``qargs`` quando as properties não estão presentes.
        """
        if not isinstance(configuration, dict):
            raise ValueError("configuration deve ser um objeto JSON")
        n = int(configuration.get("n_qubits") or 0)
        if n < 1:
            raise ValueError("configuration.n_qubits deve ser >= 1")
        basis = [
            str(g)
            for g in configuration.get("basis_gates") or ()
            if str(g) not in {"measure", "reset", "delay", "barrier"}
        ]
        coupling = [
            (int(edge[0]), int(edge[1]))
            for edge in configuration.get("coupling_map") or ()
            if len(edge) == 2
        ]
        twoq_names = {
            "cx", "cz", "ecr", "swap", "iswap", "rxx", "ryy", "rzz",
            "crx", "cry", "crz", "cp", "cu", "cu1", "cu3",
        }
        oneq_gates: list[str] = []
        twoq_gates: list[str] = []
        for gate in configuration.get("gates") or ():
            gname = str(gate.get("name") or "")
            if not gname or gname in {"measure", "reset", "delay", "barrier"}:
                continue
            target = twoq_gates if gname in twoq_names else oneq_gates
            if gname not in target:
                target.append(gname)
        if not oneq_gates and not twoq_gates:
            for gname in basis:
                target = twoq_gates if gname in twoq_names else oneq_gates
                if gname not in target:
                    target.append(gname)

        oneq_error: dict[str, dict[int, float]] = {g: {} for g in oneq_gates}
        twoq_error: dict[str, dict[tuple[int, int], float]] = {g: {} for g in twoq_gates}
        oneq_duration: dict[str, dict[int, float]] = {g: {} for g in oneq_gates}
        twoq_duration: dict[str, dict[tuple[int, int], float]] = {g: {} for g in twoq_gates}
        readout_error: dict[int, float] = {}
        readout_duration: dict[int, float] = {}
        operational_flags: dict[int, bool] = {}
        last_update = None

        def seconds(value: Any, unit: Any) -> float:
            prefixes = {
                "s": 1.0, "ms": 1e-3, "us": 1e-6, "µs": 1e-6,
                "ns": 1e-9, "ps": 1e-12, "": 1.0, None: 1.0,
            }
            return float(value) * prefixes.get(unit, 1.0)

        if isinstance(properties, dict):
            last_update = properties.get("last_update_date")
            readout_pairs: dict[int, list[float]] = {}
            for q, params in enumerate(properties.get("qubits") or ()):
                for param in params or ():
                    pname = str(param.get("name") or "")
                    value = param.get("value")
                    if value is None:
                        continue
                    if pname == "readout_error":
                        readout_error[q] = float(value)
                    elif pname in {"prob_meas0_prep1", "prob_meas1_prep0"}:
                        readout_pairs.setdefault(q, []).append(float(value))
                    elif pname in {"readout_length", "meas_length"}:
                        readout_duration[q] = seconds(value, param.get("unit"))
                    elif pname == "operational":
                        operational_flags[q] = bool(value)
            for q, values in readout_pairs.items():
                if q not in readout_error and values:
                    readout_error[q] = sum(values) / len(values)
            for gate in properties.get("gates") or ():
                gname = str(gate.get("gate") or "")
                qubits = [int(q) for q in gate.get("qubits") or ()]
                params = {
                    str(param.get("name") or ""): param
                    for param in gate.get("parameters") or ()
                }
                err = params.get("gate_error")
                dur = params.get("gate_length")
                if gname in oneq_error and len(qubits) == 1:
                    q = qubits[0]
                    if err is not None and err.get("value") is not None:
                        oneq_error[gname][q] = float(err["value"])
                    if dur is not None and dur.get("value") is not None:
                        oneq_duration[gname][q] = seconds(dur["value"], dur.get("unit"))
                elif gname in twoq_error and len(qubits) == 2:
                    edge = (qubits[0], qubits[1])
                    if err is not None and err.get("value") is not None:
                        twoq_error[gname][edge] = float(err["value"])
                    if dur is not None and dur.get("value") is not None:
                        twoq_duration[gname][edge] = seconds(dur["value"], dur.get("unit"))

        operational = {
            q for q in range(n)
            if operational_flags.get(q, True)
        }
        if degraded_qubit_threshold is not None:
            for gate, by_qubit in oneq_error.items():
                if gate == "rz":
                    continue
                for q, error in by_qubit.items():
                    if error >= degraded_qubit_threshold:
                        operational.discard(q)
        if not operational:
            raise ValueError("nenhum qubit operacional no perfil salvo")

        allowed = set(coupling) if coupling else None
        for gate in list(twoq_gates):
            filtered: dict[tuple[int, int], float] = {}
            filtered_duration: dict[tuple[int, int], float] = {}
            for (a, b), error in twoq_error.get(gate, {}).items():
                if a not in operational or b not in operational:
                    continue
                if error >= faulty_error_threshold:
                    continue
                if allowed is not None and (a, b) not in allowed and (b, a) not in allowed:
                    continue
                filtered[(a, b)] = error
                filtered_duration[(a, b)] = twoq_duration.get(gate, {}).get((a, b), 0.0)
            if gate in {"cz", "swap", "iswap"}:
                for (a, b), error in list(filtered.items()):
                    reverse = (b, a)
                    if reverse not in filtered:
                        filtered[reverse] = error
                        filtered_duration[reverse] = filtered_duration.get((a, b), 0.0)
            twoq_error[gate] = filtered
            twoq_duration[gate] = filtered_duration
        twoq_gates = [gate for gate in twoq_gates if twoq_error.get(gate)]
        coupling = sorted({edge for by_edge in twoq_error.values() for edge in by_edge})

        return cls(
            name=str(name or configuration.get("backend_name") or "gjq_saved"),
            num_qubits=n,
            coupling_map=tuple(coupling),
            basis_gates=tuple(basis),
            oneq_gates=tuple(oneq_gates),
            twoq_gates=tuple(twoq_gates),
            oneq_error=oneq_error,
            twoq_error=twoq_error,
            readout_error=readout_error,
            operational_qubits=tuple(sorted(operational)),
            oneq_duration=oneq_duration,
            twoq_duration=twoq_duration,
            readout_duration=readout_duration,
            default_error=default_error,
            default_readout_error=default_readout_error,
            profile_kind=profile_kind,
            calibration_source="gjq_backend_config + gjq_backend_properties",
            backend_name=configuration.get("backend_name"),
            backend_version=configuration.get("backend_version"),
            last_update_date=str(last_update) if last_update is not None else None,
        )

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def qubit_error(self, q: int) -> float:
        """Erro médio de 1q do qubit; usado pelo layout.

        ``rz`` é tratado como virtual (erro zero) e não entra na média.
        """
        values = [
            0.0 if gate == "rz" else self.oneq_error[gate].get(q, self.default_error)
            for gate in self.oneq_gates
        ]
        if not values:
            return self.default_error
        return sum(values) / len(values)

    def pair_error(self, a: int, b: int) -> float:
        """Menor erro 2q entre as portas disponíveis para a aresta."""
        values = []
        for gate in self.twoq_gates:
            by_edge = self.twoq_error.get(gate, {})
            if (a, b) in by_edge:
                values.append(by_edge[(a, b)])
            elif (b, a) in by_edge:
                values.append(by_edge[(b, a)])
        return min(values) if values else self.default_error

    def oneq_error_for(self, gate: str, q: int) -> float:
        return float(self.oneq_error.get(gate, {}).get(q, self.default_error))

    def twoq_error_for(self, gate: str, a: int, b: int) -> float:
        by_edge = self.twoq_error.get(gate, {})
        if (a, b) in by_edge:
            return float(by_edge[(a, b)])
        if (b, a) in by_edge:
            return float(by_edge[(b, a)])
        return float(self.default_error)

    def summary(self) -> dict[str, Any]:
        operational = set(self.operational_qubits)
        oneq_values = [
            e
            for gate, by_qubit in self.oneq_error.items()
            if gate != "rz"
            for q, e in by_qubit.items()
            if q in operational
        ]
        twoq_values = [
            e
            for by_edge in self.twoq_error.values()
            for (a, b), e in by_edge.items()
            if a in operational and b in operational
        ]
        readout_values = [
            e for q, e in self.readout_error.items() if q in operational
        ]
        return {
            "name": self.name,
            "num_qubits": self.num_qubits,
            "operational_qubits": len(self.operational_qubits),
            "non_operational_qubits": self.num_qubits - len(self.operational_qubits),
            "non_operational_sample": sorted(
                set(range(self.num_qubits)) - set(self.operational_qubits)
            )[:20],
            "edges": len(self.coupling_map),
            "basis_gates": list(self.basis_gates),
            "oneq_gates": list(self.oneq_gates),
            "twoq_gates": list(self.twoq_gates),
            "oneq_error_mean": sum(oneq_values) / len(oneq_values) if oneq_values else None,
            "oneq_error_max": max(oneq_values) if oneq_values else None,
            "twoq_error_mean": sum(twoq_values) / len(twoq_values) if twoq_values else None,
            "twoq_error_max": max(twoq_values) if twoq_values else None,
            "readout_error_mean": (
                sum(readout_values) / len(readout_values) if readout_values else None
            ),
            "readout_error_max": max(readout_values) if readout_values else None,
            "profile_kind": self.profile_kind,
            "calibration_source": self.calibration_source,
            "backend_name": self.backend_name,
            "backend_version": self.backend_version,
            "last_update_date": self.last_update_date,
            "target_fingerprint": self.target_fingerprint,
            "warnings": list(self.warnings),
        }
