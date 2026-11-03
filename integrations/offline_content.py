"""R1022 — catálogo e planejador de conteúdo offline.

Inspirado no modelo de coleções por categoria/tier do Project NOMAD
(Apache-2.0), sem copiar seus dados ou código. O módulo é somente leitura:
não baixa, não instala, não executa e não acessa a rede.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

MAX_CATALOG_BYTES = 8 * 1024 * 1024
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
RESOURCE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
KINDS = frozenset(
    {"zim", "epub", "pdf", "dataset", "map", "course", "video", "audio", "other"}
)


class CatalogError(ValueError):
    """Falha de catálogo ou de plano, com código estável para teste/CLI."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CatalogError("invalid_schema", f"{field} deve ser texto não vazio")
    return value.strip()


def _slug(value: Any, field: str) -> str:
    text = _text(value, field)
    if not SLUG.fullmatch(text):
        raise CatalogError("invalid_schema", f"{field} inválido: {text!r}")
    return text


def _resource_id(value: Any) -> str:
    text = _text(value, "resource.id")
    if not RESOURCE_ID.fullmatch(text):
        raise CatalogError("invalid_schema", f"resource.id inválido: {text!r}")
    return text


def _https_url(value: Any) -> str:
    text = _text(value, "resource.url")
    parsed = urlparse(text)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise CatalogError("invalid_url", f"URL deve ser https sem credenciais: {text!r}")
    return text


def _size(resource: Mapping[str, Any]) -> tuple[int, bool, float | None]:
    raw_bytes = resource.get("bytes")
    raw_mb = resource.get("size_mb")
    if raw_bytes is not None:
        if isinstance(raw_bytes, bool) or not isinstance(raw_bytes, int) or raw_bytes <= 0:
            raise CatalogError("invalid_size", "bytes deve ser inteiro positivo")
        return raw_bytes, False, None
    if raw_mb is not None:
        if isinstance(raw_mb, bool) or not isinstance(raw_mb, (int, float)) or raw_mb <= 0:
            raise CatalogError("invalid_size", "size_mb deve ser número positivo")
        return int(float(raw_mb) * 1024 * 1024), True, float(raw_mb)
    raise CatalogError("invalid_size", "recurso exige bytes ou size_mb")


def _normalise_resource(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise CatalogError("invalid_schema", "recurso deve ser objeto")
    identifier = _resource_id(raw.get("id"))
    title = _text(raw.get("title"), f"{identifier}.title")
    version = _text(raw.get("version"), f"{identifier}.version")
    url = _https_url(raw.get("url"))
    size_bytes, estimated, size_mb = _size(raw)
    kind = raw.get("kind", "other")
    if not isinstance(kind, str) or kind not in KINDS:
        raise CatalogError("invalid_kind", f"{identifier}.kind inválido: {kind!r}")
    license_name = raw.get("license")
    if license_name is not None and (
        not isinstance(license_name, str) or not license_name.strip()
    ):
        raise CatalogError("invalid_schema", f"{identifier}.license inválido")
    digest = raw.get("sha256")
    if digest is not None:
        if not isinstance(digest, str) or not SHA256.fullmatch(digest.lower()):
            raise CatalogError("invalid_sha256", f"{identifier}.sha256 inválido")
        digest = digest.lower()
    return {
        "id": identifier,
        "title": title,
        "version": version,
        "url": url,
        "bytes": size_bytes,
        "size_mb": size_mb,
        "estimated": estimated,
        "kind": kind,
        "license": license_name.strip() if isinstance(license_name, str) else None,
        "sha256": digest,
    }


def load_catalog(path: str | Path) -> dict[str, Any]:
    """Carrega e valida um catálogo local. Não segue symlink nem baixa URLs."""
    catalog_path = Path(path)
    if catalog_path.is_symlink():
        raise CatalogError("unsafe_path", "catálogo não pode ser symlink")
    try:
        stat = catalog_path.stat()
    except OSError as exc:
        raise CatalogError("file_missing", str(exc)) from exc
    if not catalog_path.is_file():
        raise CatalogError("file_missing", "catálogo deve ser arquivo regular")
    if stat.st_size > MAX_CATALOG_BYTES:
        raise CatalogError(
            "file_too_large",
            f"catálogo excede {MAX_CATALOG_BYTES} bytes",
        )
    try:
        document = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CatalogError("invalid_json", str(exc)) from exc
    if not isinstance(document, Mapping):
        raise CatalogError("invalid_schema", "documento deve ser objeto JSON")
    schema_version = _text(document.get("schema_version"), "schema_version")
    raw_categories = document.get("categories")
    if not isinstance(raw_categories, list) or not raw_categories:
        raise CatalogError("invalid_schema", "categories deve ser lista não vazia")

    categories: list[dict[str, Any]] = []
    seen_categories: set[str] = set()
    seen_resources: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []

    for raw_category in raw_categories:
        if not isinstance(raw_category, Mapping):
            raise CatalogError("invalid_schema", "categoria deve ser objeto")
        category_id = _slug(raw_category.get("id"), "category.id")
        if category_id in seen_categories:
            raise CatalogError("duplicate_category", category_id)
        seen_categories.add(category_id)
        category = {
            "id": category_id,
            "title": _text(raw_category.get("title"), f"{category_id}.title"),
            "description": _text(
                raw_category.get("description", ""), f"{category_id}.description"
            )
            if raw_category.get("description") is not None
            else "",
            "tiers": [],
        }
        raw_tiers = raw_category.get("tiers")
        if not isinstance(raw_tiers, list) or not raw_tiers:
            raise CatalogError("invalid_schema", f"{category_id}.tiers vazio")
        seen_tiers: set[str] = set()
        for raw_tier in raw_tiers:
            if not isinstance(raw_tier, Mapping):
                raise CatalogError("invalid_schema", "tier deve ser objeto")
            tier_id = _slug(raw_tier.get("id"), "tier.id")
            if tier_id in seen_tiers:
                raise CatalogError("duplicate_tier", tier_id)
            seen_tiers.add(tier_id)
            includes = raw_tier.get("includes_tiers", [])
            if includes is None:
                includes = []
            if not isinstance(includes, list) or any(
                not isinstance(item, str) or not item.strip() for item in includes
            ):
                raise CatalogError(
                    "invalid_schema", f"{tier_id}.includes_tiers inválido"
                )
            tier = {
                "id": tier_id,
                "title": _text(raw_tier.get("title"), f"{tier_id}.title"),
                "description": _text(
                    raw_tier.get("description", ""), f"{tier_id}.description"
                )
                if raw_tier.get("description") is not None
                else "",
                "includes_tiers": [item.strip() for item in includes],
                "resources": [],
            }
            raw_resources = raw_tier.get("resources", [])
            if raw_resources is None:
                raw_resources = []
            if not isinstance(raw_resources, list):
                raise CatalogError("invalid_schema", f"{tier_id}.resources inválido")
            for raw_resource in raw_resources:
                resource = _normalise_resource(raw_resource)
                identifier = resource["id"]
                previous = seen_resources.get(identifier)
                if previous is not None:
                    if (
                        previous["url"] != resource["url"]
                        or previous["bytes"] != resource["bytes"]
                        or previous["sha256"] != resource["sha256"]
                    ):
                        raise CatalogError(
                            "resource_conflict",
                            f"recurso duplicado com conteúdo divergente: {identifier}",
                        )
                    if f"deduplicated:{identifier}" not in warnings:
                        warnings.append(f"deduplicated:{identifier}")
                    continue
                seen_resources[identifier] = resource
                tier["resources"].append(resource)
            category["tiers"].append(tier)
        categories.append(category)

    return {
        "schema_version": schema_version,
        "categories": categories,
        "warnings": warnings,
    }


def _tier_index(catalog: Mapping[str, Any]) -> dict[str, list[tuple[str, Mapping[str, Any]]]]:
    index: dict[str, list[tuple[str, Mapping[str, Any]]]] = {}
    for category in catalog["categories"]:
        for tier in category["tiers"]:
            index.setdefault(tier["id"], []).append((category["id"], tier))
    return index


def _resolve_selection(
    catalog: Mapping[str, Any], selection: str
) -> tuple[str, str]:
    if not isinstance(selection, str) or not selection.strip():
        raise CatalogError("invalid_selection", "seleção deve ser texto")
    selection = selection.strip()
    categories = {category["id"]: category for category in catalog["categories"]}
    if ":" in selection:
        category_id, tier_id = selection.split(":", 1)
        category = categories.get(category_id)
        if category is None:
            raise CatalogError("category_not_found", category_id)
        if not any(tier["id"] == tier_id for tier in category["tiers"]):
            raise CatalogError("tier_not_found", f"{category_id}:{tier_id}")
        return category_id, tier_id
    matches = _tier_index(catalog).get(selection, [])
    if not matches:
        raise CatalogError("tier_not_found", selection)
    if len(matches) > 1:
        raise CatalogError("ambiguous_tier", selection)
    return matches[0][0], selection


def plan(catalog: Mapping[str, Any], selections: Sequence[str]) -> dict[str, Any]:
    """Resolve tiers/includes e calcula totais, sem baixar ou executar nada."""
    if not isinstance(selections, Sequence) or isinstance(selections, (str, bytes)):
        raise CatalogError("invalid_selection", "selections deve ser lista")
    if not selections:
        raise CatalogError("invalid_selection", "informe ao menos uma seleção")
    categories = {category["id"]: category for category in catalog["categories"]}
    selected_categories: set[str] = set()
    selected_tiers: set[str] = set()
    resources: dict[str, dict[str, Any]] = {}
    warnings = list(catalog.get("warnings", []))

    def add_tier(category_id: str, tier_id: str, stack: tuple[str, ...]) -> None:
        if tier_id in stack:
            raise CatalogError("include_cycle", " → ".join((*stack, tier_id)))
        category = categories.get(category_id)
        if category is None:
            raise CatalogError("category_not_found", category_id)
        tier = next((item for item in category["tiers"] if item["id"] == tier_id), None)
        if tier is None:
            raise CatalogError("tier_not_found", f"{category_id}:{tier_id}")
        selected_categories.add(category_id)
        if tier_id in selected_tiers:
            return
        selected_tiers.add(tier_id)
        for included in tier["includes_tiers"]:
            if not any(item["id"] == included for item in category["tiers"]):
                raise CatalogError("include_not_found", f"{tier_id} → {included}")
            add_tier(category_id, included, (*stack, tier_id))
        for resource in tier["resources"]:
            previous = resources.get(resource["id"])
            if previous is not None:
                if (
                    previous["url"] != resource["url"]
                    or previous["bytes"] != resource["bytes"]
                    or previous["sha256"] != resource["sha256"]
                ):
                    raise CatalogError("resource_conflict", resource["id"])
                continue
            resources[resource["id"]] = dict(resource)

    for selection in selections:
        category_id, tier_id = _resolve_selection(catalog, selection)
        add_tier(category_id, tier_id, ())

    ordered = [resources[identifier] for identifier in sorted(resources)]
    total_bytes = sum(item["bytes"] for item in ordered)
    estimated_bytes = sum(item["bytes"] for item in ordered if item["estimated"])
    licenses: dict[str, int] = {}
    for item in ordered:
        license_name = item["license"] or "unknown"
        licenses[license_name] = licenses.get(license_name, 0) + 1
        if item["license"] is None and f"missing_license:{item['id']}" not in warnings:
            warnings.append(f"missing_license:{item['id']}")
        if item["estimated"] and f"estimated_size:{item['id']}" not in warnings:
            warnings.append(f"estimated_size:{item['id']}")
    return {
        "status": "planned",
        "selections": list(selections),
        "categories": sorted(selected_categories),
        "tiers": sorted(selected_tiers),
        "resources": ordered,
        "totals": {
            "category_count": len(selected_categories),
            "tier_count": len(selected_tiers),
            "resource_count": len(ordered),
            "total_bytes": total_bytes,
            "estimated_bytes": estimated_bytes,
            "exact_bytes": total_bytes - estimated_bytes,
            "licenses": dict(sorted(licenses.items())),
        },
        "warnings": warnings,
        "notes": [
            "Plano somente leitura: nenhuma URL foi acessada, baixada ou executada.",
            "Tamanhos em size_mb são aproximados e marcados como estimados.",
        ],
    }


def human_bytes(value: int) -> str:
    if value >= 1024**3:
        return f"{value / 1024**3:.1f} GiB"
    if value >= 1024**2:
        return f"{value / 1024**2:.1f} MiB"
    if value >= 1024:
        return f"{value / 1024:.1f} KiB"
    return f"{value} B"


def render_plan(result: Mapping[str, Any]) -> str:
    totals = result["totals"]
    lines = [
        "# Plano de conteúdo offline",
        "",
        f"**Total planejado:** {human_bytes(totals['total_bytes'])} "
        f"({totals['resource_count']} recurso(s), {totals['tier_count']} tier(s)).",
        f"**Estimado:** {human_bytes(totals['estimated_bytes'])}; "
        f"**exato:** {human_bytes(totals['exact_bytes'])}.",
        "",
        "| ID | Título | Versão | Tamanho | Licença |",
        "|---|---|---|---|---|",
    ]
    for item in result["resources"]:
        lines.append(
            f"| `{item['id']}` | {item['title']} | {item['version']} | "
            f"{human_bytes(item['bytes'])} | {item['license'] or 'desconhecida'} |"
        )
    lines.extend(["", "**Avisos:**"])
    lines.extend(f"- {warning}" for warning in result["warnings"]) if result[
        "warnings"
    ] else lines.append("- nenhum")
    lines.extend(
        [
            "",
            "Nada foi baixado, instalado ou executado. Este plano é somente leitura.",
        ]
    )
    return "\n".join(lines) + "\n"


def _print_json(value: Any, stream: Any = None) -> None:
    target = sys.stdout if stream is None else stream
    json.dump(value, target, ensure_ascii=False, indent=2, sort_keys=True)
    target.write("\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="offline-content", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan", help="planeja tiers e tamanhos")
    plan_parser.add_argument("catalog")
    plan_parser.add_argument(
        "--select",
        action="append",
        required=True,
        help="categoria:tier ou tier; pode repetir",
    )
    plan_parser.add_argument("--json", action="store_true")
    list_parser = subparsers.add_parser("list", help="lista categorias e tiers")
    list_parser.add_argument("catalog")
    list_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        catalog = load_catalog(args.catalog)
        if args.command == "list":
            rows = [
                {
                    "category": category["id"],
                    "category_title": category["title"],
                    "tier": tier["id"],
                    "tier_title": tier["title"],
                    "resources": len(tier["resources"]),
                }
                for category in catalog["categories"]
                for tier in category["tiers"]
            ]
            if args.json:
                _print_json({"status": "ok", "tiers": rows})
            else:
                for row in rows:
                    print(
                        f"{row['category']}:{row['tier']} — {row['tier_title']} "
                        f"({row['resources']} recurso(s))"
                    )
            return 0
        result = plan(catalog, args.select)
        if args.json:
            _print_json(result)
        else:
            print(render_plan(result), end="")
        return 0
    except CatalogError as exc:
        if getattr(args, "json", False):
            _print_json({"status": "error", "code": exc.code, "error": str(exc)}, sys.stderr)
        else:
            print(f"erro [{exc.code}]: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
