"""Contraprovas do grafo de aprendibilidade do CZ (R1128)."""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pytest

import quantum_mitigation.cb_learnability as cl


def test_cz_pattern_graph_counts():
    graph = cl.pattern_graph("cz")
    assert graph["paulis"] == 15
    assert graph["vertices"] == ["00", "01", "10", "11"]
    assert graph["components"] == 2
    assert graph["cycle_rank"] == 13
    assert graph["cut_rank"] == 2
    assert graph["learnable_dimension"] == 13
    assert graph["unlearnable_dimension"] == 2


def test_preserved_and_changed_patterns():
    graph = cl.pattern_graph("cz")
    preserved = {edge["pauli"] for edge in graph["edges"] if edge["preserved"]}
    changed = {edge["pauli"] for edge in graph["edges"] if not edge["preserved"]}
    assert preserved == {"IZ", "ZI", "XX", "XY", "YX", "YY", "ZZ"}
    assert changed == {"IX", "IY", "XI", "XZ", "YI", "YZ", "ZX", "ZY"}
    assert len(preserved) == 7
    assert len(changed) == 8


def test_cycle_and_cut_bases_are_orthogonal():
    graph = cl.pattern_graph("cz")
    incidence = cl.incidence_matrix("cz")
    cycle = np.array(
        [[vector[label] for label in cl.PAULIS_2Q] for vector in graph["cycle_basis"]],
        dtype=float,
    ).T
    cut = np.array(
        [[vector[label] for label in cl.PAULIS_2Q] for vector in graph["cut_basis"]],
        dtype=float,
    ).T
    assert cycle.shape == (15, 13)
    assert cut.shape == (15, 2)
    np.testing.assert_allclose(incidence @ cycle, 0.0, atol=1e-10)
    np.testing.assert_allclose(cut.T @ cycle, 0.0, atol=1e-10)
    assert np.linalg.matrix_rank(cycle) == 13
    assert np.linalg.matrix_rank(cut) == 2


def test_comparison_to_orbit_design():
    comparison = cl.compare_with_orbit_design()
    assert comparison["orbit_rank"] == 9
    assert comparison["learnable_rank"] == 13
    assert comparison["missing"] == 4
    assert "Cliffords de 1 qubit" in comparison["missing_reason"]


def test_identity_graph_all_learnable():
    graph = cl.pattern_graph("identity")
    assert graph["components"] == 4
    assert graph["cycle_rank"] == 15
    assert graph["cut_rank"] == 0
    assert graph["unlearnable_dimension"] == 0


def test_audit_declares_source_and_limits():
    payload = cl.audit()
    assert payload["source"]["doi"] == "10.1038/s41467-022-35759-4"
    assert payload["source"]["theorem"] == "2"
    assert payload["cz"]["cycle_rank"] == 13
    assert payload["cz"]["cut_rank"] == 2
    assert "não aprendíveis" in payload["limits"]
    assert payload["rates_measured"] is False
    assert payload["hardware_executed"] is False
    text = Path(cl.__file__).read_text(encoding="utf-8")
    for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
        assert forbidden not in text


def test_basis_entries_are_finite_and_labeled():
    graph = cl.pattern_graph("cz")
    for vector in graph["cycle_basis"] + graph["cut_basis"]:
        assert len(vector) == 15
        assert set(vector) == set(cl.PAULIS_2Q)
        assert all(np.isfinite(value) for value in vector.values())


def test_harness_learnability_command(tmp_path):
    import importlib.util
    import json

    path = (
        Path(__file__).resolve().parents[1]
        / "harnesses/quantum-error-mitigation/cb_protocol.py"
    )
    spec = importlib.util.spec_from_file_location("cb_protocol_learn", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    out = tmp_path / "learnability.json"
    assert module.main(["learnability", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["cz"]["cycle_rank"] == 13
    assert payload["hardware_executed"] is False
    assert module.main(["learnability", "--out", str(out)]) == 2
