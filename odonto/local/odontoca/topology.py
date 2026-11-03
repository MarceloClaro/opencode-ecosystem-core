"""Topologia dentária FDI e vizinhanças — SPEC-935-R898 FR-002."""
from __future__ import annotations

from math import sqrt
from typing import Iterable, Mapping, Sequence

# 20 dentes decíduos + 32 permanentes = 52.
DECIDUOUS: frozenset[int] = frozenset(
    [50 + i for i in range(1, 6)]
    + [60 + i for i in range(1, 6)]
    + [70 + i for i in range(1, 6)]
    + [80 + i for i in range(1, 6)]
)
PERMANENT: frozenset[int] = frozenset(
    [10 + i for i in range(1, 9)]
    + [20 + i for i in range(1, 9)]
    + [30 + i for i in range(1, 9)]
    + [40 + i for i in range(1, 9)]
)

DECIDUOUS_MOLARS: frozenset[int] = frozenset(
    {54, 55, 64, 65, 74, 75, 84, 85}
)


def _validate(tooth: int) -> int:
    t = int(tooth)
    if t not in DECIDUOUS and t not in PERMANENT:
        raise ValueError(f"FDI inválido: {tooth}")
    return t


def quadrant(tooth: int) -> int:
    """Dezena FDI (1–4 permanentes, 5–8 decíduos)."""
    t = _validate(tooth)
    q = t // 10
    if q not in (1, 2, 3, 4, 5, 6, 7, 8):
        raise ValueError(f"quadrante inválido: {tooth}")
    return q


def arc_neighbors(tooth: int) -> tuple[int | None, int | None]:
    """Adjacentes no arco (mesma dezena): (medial/anterior, distal/posterior).

    Decíduos terminam na unidade 5; permanentes na 8.
    """
    t = _validate(tooth)
    unit = t % 10
    last = 5 if t in DECIDUOUS else 8
    prev = t - 1 if unit > 1 else None
    next_ = t + 1 if unit < last else None
    return prev, next_


def is_molar(tooth: int) -> bool:
    t = _validate(tooth)
    return t % 10 >= 4


def spatial_neighbors(
    key: str,
    coords: Mapping[str, Sequence[float]],
    radius: float,
) -> list[str]:
    """Vizinhos por proximidade Euclidiana (raio configurável)."""
    if key not in coords:
        return []
    origin = [float(v) for v in coords[key]]
    out: list[str] = []
    for other, pos in coords.items():
        if other == key:
            continue
        if len(pos) != len(origin):
            continue
        d = sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(origin, pos)))
        if d <= radius:
            out.append(other)
    return out


def spatial_caries_count(
    tooth: int,
    status_by_tooth: Mapping[int, str],
    coords_by_tooth: Mapping[int, Sequence[float]],
    radius: float,
) -> int:
    """Conta dentes com cárie dentro do raio (features espaciais do CA)."""
    t = int(tooth)
    if t not in coords_by_tooth:
        return 0
    str_coords = {str(k): v for k, v in coords_by_tooth.items()}
    near = spatial_neighbors(str(t), str_coords, radius)
    return sum(1 for n in near if status_by_tooth.get(int(n), "H") == "C")


def arc_caries_count(tooth: int, status_by_tooth: Mapping[int, str]) -> int:
    """Conta cárie nos adjacentes de arco (limitado a 2: prev + next)."""
    prev, nxt = arc_neighbors(int(tooth))
    return sum(
        1
        for n in (prev, nxt)
        if n is not None and status_by_tooth.get(n, "H") == "C"
    )


def all_teeth() -> Iterable[int]:
    return sorted(DECIDUOUS | PERMANENT)
