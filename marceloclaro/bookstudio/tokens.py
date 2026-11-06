"""Design tokens, contraste WCAG e cobertura de tinta (TAC)."""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, Iterable, List, Tuple


class TokenError(ValueError):
    """Token de design inválido."""


HEX_RE = re.compile(r"^#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def normalize_hex(value: str) -> str:
    if not isinstance(value, str) or not HEX_RE.fullmatch(value.strip()):
        raise TokenError(f"cor hexadecimal inválida: {value!r}")
    raw = value.strip().lstrip("#").upper()
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    return "#" + raw


def hex_to_rgb(value: str) -> Tuple[float, float, float]:
    raw = normalize_hex(value).lstrip("#")
    return tuple(int(raw[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def relative_luminance(value: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = hex_to_rgb(value)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(foreground: str, background: str) -> float:
    a, b = relative_luminance(foreground), relative_luminance(background)
    high, low = max(a, b), min(a, b)
    return (high + 0.05) / (low + 0.05)


def cmyk_tac(cmyk: Iterable[float]) -> float:
    values = tuple(float(v) for v in cmyk)
    if len(values) != 4 or any(v < 0 or v > 1 for v in values):
        raise TokenError("CMYK deve ter quatro canais entre 0 e 1")
    return sum(values) * 100.0


@dataclass(frozen=True)
class PaletteEntry:
    name: str
    hex: str
    cmyk: Tuple[float, float, float, float] | None = None
    background: str = "paper"
    restricted_to_dark: bool = False
    use: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise TokenError("PaletteEntry.name não pode ser vazio")
        object.__setattr__(self, "hex", normalize_hex(self.hex))
        if self.background not in {"paper", "black"}:
            raise TokenError("background deve ser paper ou black")
        if self.cmyk is not None:
            values = tuple(float(v) for v in self.cmyk)
            if len(values) != 4 or any(v < 0 or v > 1 for v in values):
                raise TokenError("cmyk deve ter quatro canais entre 0 e 1")
            object.__setattr__(self, "cmyk", values)

    @property
    def tac(self) -> float | None:
        return cmyk_tac(self.cmyk) if self.cmyk is not None else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex": self.hex,
            "cmyk": list(self.cmyk) if self.cmyk is not None else None,
            "tac": round(self.tac, 2) if self.tac is not None else None,
            "background": self.background,
            "restricted_to_dark": self.restricted_to_dark,
            "use": self.use,
        }


@dataclass(frozen=True)
class DesignTokens:
    paper_hex: str = "#F2E8CF"
    ink_hex: str = "#2B2117"
    black_hex: str = "#000000"
    palette: Dict[str, PaletteEntry] = field(default_factory=dict)
    body_size_pt: float = 11.0
    leading: float = 1.45
    grid_columns: int = 12
    margins_in: Tuple[float, float, float, float] = (0.9, 0.8, 0.9, 0.9)
    text_tac_limit: float = 210.0
    image_tac_limit: float = 300.0
    min_image_dpi: int = 300

    def __post_init__(self) -> None:
        object.__setattr__(self, "paper_hex", normalize_hex(self.paper_hex))
        object.__setattr__(self, "ink_hex", normalize_hex(self.ink_hex))
        object.__setattr__(self, "black_hex", normalize_hex(self.black_hex))
        if not self.palette:
            object.__setattr__(self, "palette", dict(default_tokens().palette))
        if any(not isinstance(v, PaletteEntry) for v in self.palette.values()):
            raise TokenError("palette deve conter PaletteEntry")
        if self.body_size_pt <= 0 or self.leading <= 0:
            raise TokenError("tipografia deve ter valores positivos")
        if not 1 <= self.grid_columns <= 48:
            raise TokenError("grid_columns deve ficar entre 1 e 48")
        if len(self.margins_in) != 4 or any(v <= 0 for v in self.margins_in):
            raise TokenError("margins_in deve ter quatro valores positivos")
        if self.text_tac_limit <= 0 or self.image_tac_limit <= 0:
            raise TokenError("limites de TAC devem ser positivos")
        if self.min_image_dpi < 300:
            raise TokenError("min_image_dpi não pode ser menor que 300")

    def background_for(self, entry: PaletteEntry) -> str:
        return self.black_hex if entry.background == "black" else self.paper_hex

    def contrast(self, name: str, background: str | None = None) -> float:
        if name not in self.palette:
            raise TokenError(f"cor ausente na paleta: {name}")
        entry = self.palette[name]
        return contrast_ratio(entry.hex, background or self.background_for(entry))

    def validate(self) -> List[Dict[str, str]]:
        issues: List[Dict[str, str]] = []
        for name, entry in sorted(self.palette.items()):
            ratio = contrast_ratio(entry.hex, self.background_for(entry))
            if ratio < 4.5:
                issues.append({
                    "id": f"contrast:{name}",
                    "status": "fail",
                    "detail": (
                        f"{entry.hex} sobre {self.background_for(entry)}: "
                        f"{ratio:.2f}:1; mínimo 4,5:1"
                    ),
                })
            else:
                issues.append({
                    "id": f"contrast:{name}",
                    "status": "pass",
                    "detail": f"{ratio:.2f}:1",
                })
            if entry.restricted_to_dark:
                paper_ratio = contrast_ratio(entry.hex, self.paper_hex)
                if paper_ratio >= 4.5:
                    issues.append({
                        "id": f"restricted:{name}",
                        "status": "warn",
                        "detail": (
                            f"{entry.hex} passa no papel ({paper_ratio:.2f}:1); "
                            "a restrição a fundo escuro não é necessária."
                        ),
                    })
                else:
                    issues.append({
                        "id": f"restricted:{name}",
                        "status": "pass",
                        "detail": f"sobre papel {paper_ratio:.2f}:1; uso restrito confirmado",
                    })
            if entry.cmyk is None:
                issues.append({
                    "id": f"cmyk:{name}",
                    "status": "warn",
                    "detail": "sem CMYK; cor não validada para impressão",
                })
            elif entry.tac is not None and entry.tac > self.text_tac_limit:
                issues.append({
                    "id": f"tac:{name}",
                    "status": "fail",
                    "detail": f"TAC {entry.tac:.1f}% acima de {self.text_tac_limit:.0f}%",
                })
            else:
                issues.append({
                    "id": f"tac:{name}",
                    "status": "pass",
                    "detail": f"TAC {entry.tac:.1f}%" if entry.tac is not None else "sem CMYK",
                })
        return issues

    @property
    def valid(self) -> bool:
        return not any(item["status"] == "fail" for item in self.validate())

    @property
    def errors(self) -> List[Dict[str, str]]:
        return [item for item in self.validate() if item["status"] == "fail"]

    def to_dict(self) -> Dict[str, Any]:
        issues = self.validate()
        return {
            "paper_hex": self.paper_hex,
            "ink_hex": self.ink_hex,
            "black_hex": self.black_hex,
            "body_size_pt": self.body_size_pt,
            "leading": self.leading,
            "grid_columns": self.grid_columns,
            "margins_in": list(self.margins_in),
            "text_tac_limit": self.text_tac_limit,
            "image_tac_limit": self.image_tac_limit,
            "min_image_dpi": self.min_image_dpi,
            "palette": {
                name: {
                    **entry.to_dict(),
                    "contrast": round(
                        contrast_ratio(entry.hex, self.background_for(entry)), 2
                    ),
                }
                for name, entry in sorted(self.palette.items())
            },
            "valid": self.valid,
            "issues": issues,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignTokens":
        if not isinstance(data, dict):
            raise TokenError("design deve ser objeto")
        palette = {
            name: PaletteEntry(
                name=name,
                hex=value["hex"],
                cmyk=tuple(value["cmyk"]) if value.get("cmyk") else None,
                background=value.get("background", "paper"),
                restricted_to_dark=bool(value.get("restricted_to_dark", False)),
                use=value.get("use", ""),
            )
            for name, value in (data.get("palette") or {}).items()
        }
        return cls(
            paper_hex=data.get("paper_hex", "#F2E8CF"),
            ink_hex=data.get("ink_hex", "#2B2117"),
            black_hex=data.get("black_hex", "#000000"),
            palette=palette or dict(default_tokens().palette),
            body_size_pt=float(data.get("body_size_pt", 11.0)),
            leading=float(data.get("leading", 1.45)),
            grid_columns=int(data.get("grid_columns", 12)),
            margins_in=tuple(float(v) for v in data.get("margins_in", (0.9, 0.8, 0.9, 0.9))),
            text_tac_limit=float(data.get("text_tac_limit", 210.0)),
            image_tac_limit=float(data.get("image_tac_limit", 300.0)),
            min_image_dpi=int(data.get("min_image_dpi", 300)),
        )


def default_tokens() -> DesignTokens:
    """Paleta R1076/R1077 com CMYK e restrição do vermelho de Cuidado."""
    return DesignTokens(palette={
        "mem": PaletteEntry(
            name="mem", hex="#8A3B1F", cmyk=(0, 0.57, 0.78, 0.46),
            use="Memória; texto sobre papel",
        ),
        "doc": PaletteEntry(
            name="doc", hex="#1F5C57", cmyk=(0.66, 0, 0.06, 0.64),
            use="Documento; texto sobre papel",
        ),
        "luc": PaletteEntry(
            name="luc", hex="#552A7A", cmyk=(0.30, 0.65, 0, 0.52),
            use="Lucidez; texto sobre papel",
        ),
        "cont": PaletteEntry(
            name="cont", hex="#9B1B1B", cmyk=(0, 0.83, 0.83, 0.39),
            use="Contaminação; texto sobre papel",
        ),
        "epi": PaletteEntry(
            name="epi", hex="#6E4E10", cmyk=(0, 0.29, 0.86, 0.57),
            use="Epígrafe; texto sobre papel",
        ),
        "ink": PaletteEntry(
            name="ink", hex="#2B2117", cmyk=(0, 0.23, 0.47, 0.83),
            use="Corpo do texto",
        ),
        "cuidado": PaletteEntry(
            name="cuidado", hex="#FF4D4D", cmyk=(0, 0.70, 0.70, 0),
            background="black", restricted_to_dark=True,
            use="Cuidado; apenas fundo preto",
        ),
    })
