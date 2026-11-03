"""FR-002 — topologia FDI e vizinhos de arco/Euclidianos."""
from __future__ import annotations

import pytest

from odontoca import topology as topo


def test_fdi_sets():
    """FR-002: 20 decíduos + 32 permanentes = 52."""
    assert len(topo.DECIDUOUS) == 20
    assert len(topo.PERMANENT) == 32
    assert len(topo.DECIDUOUS | topo.PERMANENT) == 52
    assert {54, 55, 64, 65, 74, 75, 84, 85} <= topo.DECIDUOUS
    assert {11, 18, 48, 36} <= topo.PERMANENT


def test_quadrant():
    assert topo.quadrant(54) == 5
    assert topo.quadrant(65) == 6
    assert topo.quadrant(36) == 3
    assert topo.quadrant(48) == 4
    with pytest.raises(ValueError):
        topo.quadrant(99)


def test_arc_neighbors_deciduous():
    """54↔55 adjacentes e 53↔54 adjacentes; 51 é primeiro do arco (sem medial)."""
    assert topo.arc_neighbors(54) == (53, 55)
    assert topo.arc_neighbors(55) == (54, None)
    assert topo.arc_neighbors(51) == (None, 52)
    assert topo.arc_neighbors(61) == (None, 62)
    # arco permanente com 8 dentes
    assert topo.arc_neighbors(16) == (15, 17)
    assert topo.arc_neighbors(11) == (None, 12)
    assert topo.arc_neighbors(18) == (17, None)
    # quadrantes inferiores invertidos: 48 é o mais distal à esquerda
    assert topo.arc_neighbors(48) == (47, None) or topo.arc_neighbors(48) == (None, 47)


def test_spatial_neighbors():
    coords = {
        "A": (0.0, 0.0, 0.0),
        "B": (0.5, 0.0, 0.0),
        "C": (3.0, 0.0, 0.0),
    }
    near = topo.spatial_neighbors("A", coords, radius=1.0)
    assert set(near) == {"B"}
    assert topo.spatial_neighbors("C", coords, radius=1.0) == []


def test_is_molar():
    assert topo.is_molar(54) and topo.is_molar(85)
    assert not topo.is_molar(51) and not topo.is_molar(41)
