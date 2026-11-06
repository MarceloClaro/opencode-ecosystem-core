"""Cálculos KDP de capa, lombada, bleed e trim.

As fórmulas são implementadas no Core para não depender de planilha externa.
A espessura de papel é configurável e documentada; a lista de trims KDP é
deliberadamente conservadora e pode ser atualizada sem quebrar o contrato.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, Dict, Tuple


class KDPError(ValueError):
    """Entrada inválida para o cálculo KDP."""


class PaperStock(str, Enum):
    WHITE = "white"
    CREAM = "cream"


class InkType(str, Enum):
    BW = "bw"
    STANDARD_COLOR = "standard_color"
    PREMIUM_COLOR = "premium_color"


# Espessura por página, em polegadas. Valores de referência KDP.
PAPER_THICKNESS_IN: Dict[Tuple[PaperStock, InkType], float] = {
    (PaperStock.WHITE, InkType.BW): 0.002252,
    (PaperStock.CREAM, InkType.BW): 0.002500,
    (PaperStock.WHITE, InkType.STANDARD_COLOR): 0.002252,
    (PaperStock.WHITE, InkType.PREMIUM_COLOR): 0.002347,
}

# Trims comuns aceitos pela KDP (polegadas). A lista não é exaustiva; serve
# como alerta, não como certificação. Confirmar sempre no previewer da KDP.
KDP_TRIM_SIZES_IN: Tuple[Tuple[float, float], ...] = (
    (5.00, 8.00),
    (5.06, 7.81),
    (5.25, 8.00),
    (5.25, 8.25),
    (5.50, 8.25),
    (5.50, 8.50),
    (6.00, 9.00),
    (6.14, 9.21),
    (6.69, 9.61),
    (7.00, 10.00),
    (7.44, 9.69),
    (7.50, 9.25),
    (8.00, 10.00),
    (8.27, 11.69),
    (8.50, 11.00),
)

TRIM_RE = re.compile(r"^(?P<w>\d+(?:\.\d+)?)x(?P<h>\d+(?:\.\d+)?)(?P<unit>in|mm)$")
MM_PER_IN = 25.4


def parse_trim(value: str) -> Tuple[float, float]:
    """Converte ``6x9in`` ou ``160x230mm`` em largura/altura em polegadas."""
    match = TRIM_RE.fullmatch(value.strip())
    if not match:
        raise KDPError("trim deve ser LARGURAxALTURA em in ou mm (ex.: 6x9in)")
    width = float(match.group("w"))
    height = float(match.group("h"))
    if match.group("unit") == "mm":
        width /= MM_PER_IN
        height /= MM_PER_IN
    if not 3.0 <= width <= 15.0 or not 4.0 <= height <= 18.0:
        raise KDPError("trim fora da faixa editorial de 3..15 x 4..18 polegadas")
    return width, height


def is_kdp_trim_supported(width_in: float, height_in: float,
                          tolerance_in: float = 0.02) -> bool:
    """Indica se o trim está na lista conservadora de tamanhos KDP."""
    return any(
        abs(width_in - width) <= tolerance_in and abs(height_in - height) <= tolerance_in
        for width, height in KDP_TRIM_SIZES_IN
    )


@dataclass(frozen=True)
class KDPCoverSpec:
    """Especificação de capa completa (frente + lombada + contracapa)."""

    trim_width_in: float
    trim_height_in: float
    page_count: int
    paper: PaperStock = PaperStock.CREAM
    ink: InkType = InkType.BW
    bleed_in: float = 0.125
    safe_margin_in: float = 0.25

    def __post_init__(self) -> None:
        if isinstance(self.page_count, bool) or not isinstance(self.page_count, int):
            raise KDPError("page_count deve ser inteiro")
        if not 24 <= self.page_count <= 828:
            raise KDPError("page_count deve ficar entre 24 e 828 (KDP paperback)")
        if not 3.0 <= self.trim_width_in <= 15.0:
            raise KDPError("largura do trim fora da faixa KDP")
        if not 4.0 <= self.trim_height_in <= 18.0:
            raise KDPError("altura do trim fora da faixa KDP")
        if self.bleed_in < 0.125:
            raise KDPError("bleed mínimo KDP é 0,125 in")
        if self.safe_margin_in < 0.25:
            raise KDPError("margem de segurança mínima é 0,25 in")
        if not isinstance(self.paper, PaperStock):
            object.__setattr__(self, "paper", PaperStock(self.paper))
        if not isinstance(self.ink, InkType):
            object.__setattr__(self, "ink", InkType(self.ink))
        if (self.paper, self.ink) not in PAPER_THICKNESS_IN:
            raise KDPError(
                f"combinação não suportada pela KDP: {self.paper.value}/{self.ink.value}"
            )

    @property
    def paper_thickness_in(self) -> float:
        return PAPER_THICKNESS_IN[(self.paper, self.ink)]

    @property
    def spine_in(self) -> float:
        return self.page_count * self.paper_thickness_in

    @property
    def full_cover_width_in(self) -> float:
        return 2 * self.bleed_in + 2 * self.trim_width_in + self.spine_in

    @property
    def full_cover_height_in(self) -> float:
        return 2 * self.bleed_in + self.trim_height_in

    @property
    def cover_pixels_300dpi(self) -> Tuple[int, int]:
        return (
            int(round(self.full_cover_width_in * 300)),
            int(round(self.full_cover_height_in * 300)),
        )

    @property
    def barcode_area_in(self) -> Tuple[float, float]:
        return (2.0, 1.2)

    @property
    def spine_text_allowed(self) -> bool:
        return self.page_count >= 100

    @property
    def trim_supported(self) -> bool:
        return is_kdp_trim_supported(self.trim_width_in, self.trim_height_in)

    @property
    def warnings(self) -> Tuple[str, ...]:
        rows = []
        if not self.trim_supported:
            rows.append(
                f"trim {self.trim_width_in:.3f}x{self.trim_height_in:.3f} in "
                "não está na lista KDP; confirmar no previewer antes do upload."
            )
        if abs(self.bleed_in - 0.125) > 1e-9:
            rows.append("bleed diferente de 0,125 in; a KDP espera 0,125 in.")
        if not self.spine_text_allowed:
            rows.append("menos de 100 páginas: evitar texto na lombada.")
        if self.spine_in < 0.25:
            rows.append("lombada estreita: revisar legibilidade e dobra.")
        return tuple(rows)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trim_in": [round(self.trim_width_in, 4), round(self.trim_height_in, 4)],
            "page_count": self.page_count,
            "paper": self.paper.value,
            "ink": self.ink.value,
            "paper_thickness_in": self.paper_thickness_in,
            "spine_in": round(self.spine_in, 4),
            "bleed_in": self.bleed_in,
            "safe_margin_in": self.safe_margin_in,
            "full_cover_in": [
                round(self.full_cover_width_in, 4),
                round(self.full_cover_height_in, 4),
            ],
            "cover_pixels_300dpi": list(self.cover_pixels_300dpi),
            "barcode_area_in": list(self.barcode_area_in),
            "spine_text_allowed": self.spine_text_allowed,
            "trim_supported": self.trim_supported,
            "warnings": list(self.warnings),
        }


def kdp_cover_spec(trim: str, page_count: int, *,
                   paper: str = "cream", ink: str = "bw",
                   bleed_in: float = 0.125,
                   safe_margin_in: float = 0.25) -> KDPCoverSpec:
    """Atalho: monta ``KDPCoverSpec`` a partir de um trim textual."""
    width, height = parse_trim(trim)
    return KDPCoverSpec(
        trim_width_in=width,
        trim_height_in=height,
        page_count=page_count,
        paper=PaperStock(paper),
        ink=InkType(ink),
        bleed_in=bleed_in,
        safe_margin_in=safe_margin_in,
    )
