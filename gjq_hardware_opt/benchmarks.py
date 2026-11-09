#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Circuitos de teste para o otimizador GJQ (R1109)."""
from __future__ import annotations

from pathlib import Path

from qiskit import QuantumCircuit, qasm2, qasm3

from quantum_efficiency.benchmarks import BENCHMARKS
from quantum_efficiency.experiment_benchmarks import benchmarks_experimentos


def _synthetic() -> list[dict]:
    return [
        {
            "name": item["name"],
            "description": f"benchmark sintético {item['name']}",
            "circuit": item["circuit"],
            "set": "synthetic",
        }
        for item in BENCHMARKS
    ]


def _experiments() -> list[dict]:
    return [
        {
            "name": item["name"],
            "experiment": item["experiment"],
            "description": f"{item['experiment']} — {item['description']}",
            "circuit": item["circuit"],
            "set": "experiments",
        }
        for item in benchmarks_experimentos()
    ]


def all_circuits() -> list[dict]:
    return [*_synthetic(), *_experiments()]


def list_circuits(set_name: str = "all") -> list[dict]:
    if set_name == "synthetic":
        return _synthetic()
    if set_name == "experiments":
        return _experiments()
    if set_name == "all":
        return all_circuits()
    raise ValueError("set deve ser synthetic, experiments ou all")


def select_circuits(
    set_name: str = "all",
    only: list[str] | None = None,
) -> list[dict]:
    items = list_circuits(set_name)
    if not only:
        return items
    wanted = set(only)
    selected = [
        item
        for item in items
        if item["name"] in wanted or item.get("experiment") in wanted
    ]
    matched = {item["name"] for item in selected} | {
        item.get("experiment") for item in selected
    }
    missing = wanted - matched
    if missing:
        raise ValueError(f"circuitos desconhecidos: {sorted(missing)}")
    return selected


def load_circuit(name: str) -> dict:
    if name.endswith((".qasm", ".qasm2", ".qasm3")):
        path = Path(name)
        text = path.read_text(encoding="utf-8")
        try:
            circuit = qasm3.loads(text)
        except Exception:
            circuit = qasm2.loads(text)
        return {
            "name": path.stem,
            "description": f"QASM local {path}",
            "circuit": circuit,
            "set": "file",
        }
    items = all_circuits()
    for item in items:
        if item["name"] == name:
            return item
    for item in items:
        if item.get("experiment") == name:
            return item
    raise ValueError(f"circuito desconhecido: {name!r}")


def circuit_or_none(name: str) -> QuantumCircuit | None:
    try:
        return load_circuit(name)["circuit"]
    except ValueError:
        return None
