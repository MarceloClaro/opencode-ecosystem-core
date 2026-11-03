"""R1022 — catálogo e planejador de conteúdo offline, somente leitura."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.offline_content import (
    CatalogError,
    load_catalog,
    main,
    plan,
    render_plan,
)


def catalog_document() -> dict:
    return {
        "schema_version": "1.0",
        "categories": [
            {
                "id": "saude",
                "title": "Saúde",
                "description": "Referências de saúde",
                "tiers": [
                    {
                        "id": "saude-essencial",
                        "title": "Essencial",
                        "description": "Primeiros socorros",
                        "resources": [
                            {
                                "id": "primeiros-socorros",
                                "title": "Primeiros socorros",
                                "version": "2026-01",
                                "url": "https://example.org/primeiros-socorros.zim",
                                "size_mb": 10,
                                "kind": "zim",
                                "license": "CC-BY-4.0",
                                "sha256": "a" * 64,
                            }
                        ],
                    },
                    {
                        "id": "saude-ampla",
                        "title": "Ampla",
                        "description": "Inclui o essencial",
                        "includes_tiers": ["saude-essencial"],
                        "resources": [
                            {
                                "id": "medicamentos",
                                "title": "Medicamentos",
                                "version": "2026-02",
                                "url": "https://example.org/medicamentos.zim",
                                "bytes": 20 * 1024 * 1024,
                                "kind": "zim",
                                "license": "CC-BY-4.0",
                            }
                        ],
                    },
                ],
            },
            {
                "id": "educacao",
                "title": "Educação",
                "description": "Cursos e livros",
                "tiers": [
                    {
                        "id": "educacao-essencial",
                        "title": "Essencial",
                        "description": "Livros abertos",
                        "resources": [
                            {
                                "id": "livros-abertos",
                                "title": "Livros abertos",
                                "version": "2026-03",
                                "url": "https://example.org/livros.epub",
                                "bytes": 5 * 1024 * 1024,
                                "kind": "epub",
                            }
                        ],
                    }
                ],
            },
        ],
    }


def write_catalog(tmp_path: Path, document: dict | None = None) -> Path:
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(document or catalog_document()), encoding="utf-8")
    return path


def test_load_valid_catalog(tmp_path: Path) -> None:
    catalog = load_catalog(write_catalog(tmp_path))
    assert catalog["schema_version"] == "1.0"
    assert [category["id"] for category in catalog["categories"]] == [
        "saude",
        "educacao",
    ]
    assert len(catalog["categories"][0]["tiers"]) == 2
    assert catalog["categories"][0]["tiers"][1]["includes_tiers"] == [
        "saude-essencial"
    ]


def test_duplicate_category_id_fails(tmp_path: Path) -> None:
    document = catalog_document()
    document["categories"].append(dict(document["categories"][0]))
    with pytest.raises(CatalogError) as error:
        load_catalog(write_catalog(tmp_path, document))
    assert error.value.code == "duplicate_category"


def test_duplicate_tier_id_fails(tmp_path: Path) -> None:
    document = catalog_document()
    document["categories"][0]["tiers"].append(
        dict(document["categories"][0]["tiers"][0])
    )
    with pytest.raises(CatalogError) as error:
        load_catalog(write_catalog(tmp_path, document))
    assert error.value.code == "duplicate_tier"


def test_conflicting_duplicate_resource_fails(tmp_path: Path) -> None:
    document = catalog_document()
    duplicate = dict(document["categories"][1]["tiers"][0]["resources"][0])
    duplicate["bytes"] = 999
    document["categories"][0]["tiers"][1]["resources"].append(duplicate)
    with pytest.raises(CatalogError) as error:
        load_catalog(write_catalog(tmp_path, document))
    assert error.value.code == "resource_conflict"


def test_identical_duplicate_resource_is_deduped(tmp_path: Path) -> None:
    document = catalog_document()
    duplicate = dict(document["categories"][0]["tiers"][0]["resources"][0])
    document["categories"][1]["tiers"][0]["resources"].append(duplicate)
    catalog = load_catalog(write_catalog(tmp_path, document))
    resources = [
        resource
        for category in catalog["categories"]
        for tier in category["tiers"]
        for resource in tier["resources"]
    ]
    assert len([item for item in resources if item["id"] == "primeiros-socorros"]) == 1
    assert any("deduplicated:primeiros-socorros" in item for item in catalog["warnings"])


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("url", "http://example.org/a.zim", "invalid_url"),
        ("bytes", -1, "invalid_size"),
        ("size_mb", 0, "invalid_size"),
        ("sha256", "abc", "invalid_sha256"),
        ("kind", "executavel", "invalid_kind"),
    ],
)
def test_invalid_resource_fields_fail(
    tmp_path: Path, field: str, value: object, code: str
) -> None:
    document = catalog_document()
    resource = document["categories"][0]["tiers"][0]["resources"][0]
    if field == "bytes":
        resource.pop("size_mb", None)
    if field == "size_mb":
        resource.pop("bytes", None)
    resource[field] = value
    with pytest.raises(CatalogError) as error:
        load_catalog(write_catalog(tmp_path, document))
    assert error.value.code == code


def test_plan_resolves_includes_and_totals(tmp_path: Path) -> None:
    catalog = load_catalog(write_catalog(tmp_path))
    result = plan(catalog, ["saude:saude-ampla"])
    assert result["status"] == "planned"
    ids = [resource["id"] for resource in result["resources"]]
    assert ids == ["medicamentos", "primeiros-socorros"]
    assert result["totals"]["resource_count"] == 2
    assert result["totals"]["total_bytes"] == 30 * 1024 * 1024
    assert result["totals"]["estimated_bytes"] == 10 * 1024 * 1024
    estimated = {item["id"]: item["estimated"] for item in result["resources"]}
    assert estimated["primeiros-socorros"] is True
    assert estimated["medicamentos"] is False


def test_plan_cycle_is_rejected(tmp_path: Path) -> None:
    document = catalog_document()
    document["categories"][0]["tiers"][0]["includes_tiers"] = ["saude-ampla"]
    catalog = load_catalog(write_catalog(tmp_path, document))
    with pytest.raises(CatalogError) as error:
        plan(catalog, ["saude:saude-essencial"])
    assert error.value.code == "include_cycle"


def test_plan_missing_tier_is_rejected(tmp_path: Path) -> None:
    catalog = load_catalog(write_catalog(tmp_path))
    with pytest.raises(CatalogError) as error:
        plan(catalog, ["saude:inexistente"])
    assert error.value.code == "tier_not_found"


def test_plan_marks_estimated_size_and_missing_license(tmp_path: Path) -> None:
    catalog = load_catalog(write_catalog(tmp_path))
    result = plan(catalog, ["educacao:educacao-essencial"])
    resource = result["resources"][0]
    assert resource["estimated"] is False
    assert "missing_license:livros-abertos" in result["warnings"]


def test_plan_is_deterministic_and_does_not_mutate_catalog(tmp_path: Path) -> None:
    catalog = load_catalog(write_catalog(tmp_path))
    before = json.dumps(catalog, sort_keys=True)
    first = plan(catalog, ["saude:saude-ampla", "educacao:educacao-essencial"])
    second = plan(catalog, ["saude:saude-ampla", "educacao:educacao-essencial"])
    assert first == second
    assert json.dumps(catalog, sort_keys=True) == before


def test_render_plan_contains_totals_and_read_only_notice(tmp_path: Path) -> None:
    result = plan(load_catalog(write_catalog(tmp_path)), ["saude:saude-ampla"])
    text = render_plan(result)
    assert "Plano de conteúdo offline" in text
    assert "Nada foi baixado" in text
    assert "Primeiros socorros" in text
    assert "30.0 MiB" in text or "30 MiB" in text


def test_cli_plan_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    catalog = write_catalog(tmp_path)
    code = main(["plan", str(catalog), "--select", "saude:saude-ampla", "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "planned"
    assert payload["totals"]["resource_count"] == 2


def test_cli_error_is_structured(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    catalog = write_catalog(tmp_path)
    code = main(["plan", str(catalog), "--select", "saude:inexistente", "--json"])
    assert code == 2
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "error"
    assert payload["code"] == "tier_not_found"


def test_load_rejects_symlink(tmp_path: Path) -> None:
    target = write_catalog(tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(CatalogError) as error:
        load_catalog(link)
    assert error.value.code == "unsafe_path"


def test_load_rejects_oversized_catalog(tmp_path: Path) -> None:
    path = tmp_path / "big.json"
    path.write_bytes(b"{" + b" " * (8 * 1024 * 1024 + 1) + b"}")
    with pytest.raises(CatalogError) as error:
        load_catalog(path)
    assert error.value.code == "file_too_large"
