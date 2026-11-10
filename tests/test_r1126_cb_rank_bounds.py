"""Contraprovas de posto para aumento do desenho CB (R1126)."""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pytest

import quantum_mitigation.cb_rank_bounds as rb


def test_matrix_ranks_and_cz_specificity():
    assert rb.anticommutation_matrix().shape == (15, 15)
    assert rb.full_matrix_rank() == 15
    assert rb.orbit_average_rank("cz") == 9
    # Identidade recupera D; não é um ciclo físico comparável ao CZ.
    assert rb.orbit_average_rank("identity") == 15


def test_cz_permutation_is_involution_and_preserves_orbits():
    perm = rb.clifford_permutation("cz")
    assert [perm[perm[i]] for i in range(15)] == list(range(15))
    assert rb.cz_orbits() == [
        ("XX", "YY"), ("XY", "YX"), ("XI", "XZ"), ("YI", "YZ"),
        ("IX", "ZX"), ("IY", "ZY"), ("IZ",), ("ZI",), ("ZZ",),
    ] or sorted(rb.cz_orbits()) == sorted([
        ("XX", "YY"), ("XY", "YX"), ("XI", "XZ"), ("YI", "YZ"),
        ("IX", "ZX"), ("IY", "ZY"), ("IZ",), ("ZI",), ("ZZ",),
    ])


def test_orbit_rows_are_averages_of_d_rows():
    matrix = rb.orbit_average_matrix("cz")
    d = rb.anticommutation_matrix()
    labels = rb.PAULIS_2Q
    for orbit in rb.cz_orbits():
        indices = [labels.index(p) for p in orbit]
        expected = d[indices].mean(axis=0)
        for index in indices:
            np.testing.assert_allclose(matrix[index], expected, atol=1e-12)


def test_augmentation_depends_on_choice():
    positive = rb.stacked_rank(["cz", ("random", 0)])
    negative = rb.stacked_rank(["cz", ("random", 1)])
    assert positive["rank"] == 15
    assert negative["rank"] < 15
    assert positive["condition_number"] < 1e12


def test_separate_generators_remain_underdetermined():
    for cycles in (1, 2, 3):
        audit = rb.separate_generator_audit(cycles)
        assert audit["rank"] == 9 * cycles
        assert audit["unknowns"] == 15 * cycles
        assert audit["identifiable"] is False
        assert audit["deficiency"] == 6 * cycles


def test_submodels_are_identifiable_only_under_null_assumption():
    local = rb.submodel_rank(rb.LOCAL_LABELS)
    twoq = rb.submodel_rank(rb.TWO_QUBIT_LABELS)
    assert local["rank"] == 6 == local["n_parameters"]
    assert twoq["rank"] == 9 == twoq["n_parameters"]
    assert local["requires_other_rates_zero"] is True
    assert twoq["requires_other_rates_zero"] is True


def test_greedy_augmentation_search_is_deterministic():
    first = rb.augmentation_search(seeds=range(4))
    second = rb.augmentation_search(seeds=range(4))
    assert first == second
    assert first["rank"] == 15
    assert first["status"] == "design_found"
    assert first["selected_seeds"]
    assert first["assumption"].startswith("mesmo gerador")


def test_audit_declares_limits_and_no_hardware():
    audit = rb.audit()
    assert audit["cz_only_rank"] == 9
    assert audit["full_matrix_rank"] == 15
    assert audit["augmentation"]["rank_possible"] == 15
    assert audit["separate_generators"]["identifiable"] is False
    assert "hardware" in audit["limits"].lower()
    assert "nenhuma taxa" in audit["limits"].lower()
    text = Path(rb.__file__).read_text(encoding="utf-8")
    for forbidden in ("submit_optimized", "connect_gjq", "GJQ_API_KEY", "allow_hardware"):
        assert forbidden not in text


def test_every_orbit_matrix_is_well_formed():
    for seed in range(3):
        matrix = rb.orbit_average_matrix(("random", seed))
        assert matrix.shape == (15, 15)
        assert np.all(np.isfinite(matrix))
        assert np.linalg.matrix_rank(matrix) <= 15


def test_harness_rank_command_is_offline_and_new_file(tmp_path):
    import importlib.util
    import json

    path = (
        Path(__file__).resolve().parents[1]
        / "harnesses/quantum-error-mitigation/cb_protocol.py"
    )
    spec = importlib.util.spec_from_file_location("cb_protocol_rank", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    out = tmp_path / "rank.json"
    assert module.main(["rank", "--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["cz_only_rank"] == 9
    assert payload["hardware_executed"] is False
    assert module.main(["rank", "--out", str(out)]) == 2
