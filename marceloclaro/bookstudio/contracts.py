"""Contratos de projeto editorial: manifesto, KDP, design e validação."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List

from marceloclaro.book_studio import BookError, BookManifest
from .kdp import KDPCoverSpec, KDPError, kdp_cover_spec
from .tokens import DesignTokens, default_tokens

PROJECT_FILE = "book.project.json"


def validate_isbn(value: str) -> bool:
    """Valida ISBN-10 e ISBN-13 por checksum, sem consultar rede."""
    if not isinstance(value, str):
        return False
    raw = "".join(ch for ch in value.upper() if ch.isdigit() or ch == "X")
    if len(raw) == 10:
        if not raw[:9].isdigit():
            return False
        total = 0
        for index, char in enumerate(raw):
            digit = 10 if char == "X" else int(char)
            total += (10 - index) * digit
        return total % 11 == 0
    if len(raw) == 13:
        if not raw.isdigit():
            return False
        total = sum(int(char) * (1 if index % 2 == 0 else 3)
                    for index, char in enumerate(raw))
        return total % 10 == 0
    return False


@dataclass(frozen=True)
class BookProject:
    manifest: BookManifest
    page_count: int
    isbn: str | None = None
    paper: str = "cream"
    ink: str = "bw"
    bleed_in: float = 0.125
    cover_art_dpi: int = 0
    design: DesignTokens = field(default_factory=default_tokens)
    interior_pdf: str | None = None
    cover_pdf: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.manifest, BookManifest):
            raise BookError("manifest deve ser BookManifest")
        if isinstance(self.page_count, bool) or not isinstance(self.page_count, int):
            raise BookError("page_count deve ser inteiro")
        if not 1 <= self.page_count <= 2000:
            raise BookError("page_count deve ficar entre 1 e 2000")
        if isinstance(self.cover_art_dpi, bool) or not isinstance(self.cover_art_dpi, int):
            raise BookError("cover_art_dpi deve ser inteiro")
        if self.cover_art_dpi < 0:
            raise BookError("cover_art_dpi não pode ser negativo")
        if not isinstance(self.design, DesignTokens):
            raise BookError("design deve ser DesignTokens")
        if not isinstance(self.metadata, dict):
            raise BookError("metadata deve ser objeto")

    def kdp_spec(self) -> KDPCoverSpec:
        return kdp_cover_spec(
            self.manifest.trim,
            self.page_count,
            paper=self.paper,
            ink=self.ink,
            bleed_in=self.bleed_in,
        )

    def validate(self) -> List[Dict[str, str]]:
        issues: List[Dict[str, str]] = []

        try:
            spec = self.kdp_spec()
        except (KDPError, ValueError) as exc:
            issues.append({"id": "kdp", "status": "fail", "detail": str(exc)})
            spec = None

        if spec is not None:
            if not spec.trim_supported:
                issues.append({
                    "id": "kdp:trim",
                    "status": "warn",
                    "detail": (
                        f"trim {self.manifest.trim} fora da lista KDP; "
                        "confirmar no previewer antes do upload"
                    ),
                })
            if not spec.spine_text_allowed:
                issues.append({
                    "id": "kdp:spine_text",
                    "status": "warn",
                    "detail": "menos de 100 páginas: evitar texto na lombada",
                })
            issues.append({
                "id": "kdp:spine",
                "status": "pass",
                "detail": f"{spec.spine_in:.4f} in para {self.page_count} páginas",
            })

        if self.cover_art_dpi == 0:
            issues.append({
                "id": "cover:dpi",
                "status": "fail",
                "detail": "capa sem DPI declarado; exigir arte em 300 DPI",
            })
        elif self.cover_art_dpi < 300:
            issues.append({
                "id": "cover:dpi",
                "status": "fail",
                "detail": f"capa a {self.cover_art_dpi} DPI; mínimo 300 DPI",
            })
        else:
            issues.append({
                "id": "cover:dpi",
                "status": "pass",
                "detail": f"{self.cover_art_dpi} DPI",
            })

        if self.isbn is not None:
            if validate_isbn(self.isbn):
                issues.append({"id": "isbn", "status": "pass", "detail": self.isbn})
            else:
                issues.append({
                    "id": "isbn",
                    "status": "fail",
                    "detail": f"ISBN inválido: {self.isbn}",
                })

        for label, value in (("interior_pdf", self.interior_pdf),
                             ("cover_pdf", self.cover_pdf)):
            if value is None:
                continue
            target = Path(value).expanduser()
            if target.is_file():
                issues.append({"id": label, "status": "pass", "detail": str(target)})
            else:
                issues.append({
                    "id": label,
                    "status": "fail",
                    "detail": f"arquivo ausente: {value}",
                })

        for item in self.design.validate():
            if item["status"] == "fail":
                issues.append({
                    "id": f"design:{item['id']}",
                    "status": "fail",
                    "detail": item["detail"],
                })
            elif item["status"] == "warn":
                issues.append({
                    "id": f"design:{item['id']}",
                    "status": "warn",
                    "detail": item["detail"],
                })

        return issues

    @property
    def ok(self) -> bool:
        return not any(item["status"] == "fail" for item in self.validate())

    def to_dict(self) -> Dict[str, Any]:
        try:
            kdp = self.kdp_spec().to_dict()
        except (KDPError, ValueError) as exc:
            kdp = {"error": str(exc)}
        return {
            "schema_version": 1,
            "manifest": self.manifest.to_dict(),
            "page_count": self.page_count,
            "isbn": self.isbn,
            "paper": self.paper,
            "ink": self.ink,
            "bleed_in": self.bleed_in,
            "cover_art_dpi": self.cover_art_dpi,
            "design": self.design.to_dict(),
            "interior_pdf": self.interior_pdf,
            "cover_pdf": self.cover_pdf,
            "metadata": self.metadata,
            "kdp": kdp,
            "ok": self.ok,
            "issues": self.validate(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookProject":
        if not isinstance(data, dict):
            raise BookError("projeto deve ser objeto")
        manifest_data = data.get("manifest")
        if not isinstance(manifest_data, dict):
            raise BookError("projeto sem manifest")
        manifest_data = dict(manifest_data)
        if "chapters" in manifest_data:
            manifest_data["chapters"] = tuple(manifest_data["chapters"])
        if "output_formats" in manifest_data:
            manifest_data["output_formats"] = tuple(manifest_data["output_formats"])
        manifest = BookManifest(**manifest_data)
        design_data = data.get("design")
        design = DesignTokens.from_dict(design_data) if isinstance(design_data, dict) else default_tokens()
        return cls(
            manifest=manifest,
            page_count=int(data.get("page_count", 0)),
            isbn=data.get("isbn"),
            paper=str(data.get("paper", "cream")),
            ink=str(data.get("ink", "bw")),
            bleed_in=float(data.get("bleed_in", 0.125)),
            cover_art_dpi=int(data.get("cover_art_dpi", 0)),
            design=design,
            interior_pdf=data.get("interior_pdf"),
            cover_pdf=data.get("cover_pdf"),
            metadata=dict(data.get("metadata") or {}),
        )


def load_project(path: str | Path) -> BookProject:
    target = Path(path).expanduser().resolve()
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BookError(f"projeto ilegível: {target}") from exc
    return BookProject.from_dict(data)


def save_project(path: str | Path, project: BookProject) -> Path:
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return target
