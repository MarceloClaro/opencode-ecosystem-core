"""Contratos locais R1059; não atestam qualidade visual ou perceptual."""
from copy import deepcopy
import math

import pytest

from integrations.video_reference_contract import (
    project_equirectangular,
    validate_frame_manifest,
    validate_recipe,
)


def recipe():
    return {
        "schema_version": "1.0",
        "reference": {"id": "ref-01", "duration_s": 82.174708},
        "coverage": {
            modality: {"status": "parcial", "intervals": [],
                       "point_record_ids": ["p01"] if modality == "visual" else [],
                       "gaps": [], "limitations": ["Amostras; não comprova escuta ou movimento contínuo."]}
            for modality in ("visual", "audio", "transcription")
        },
        "evidence": [{"id": "e01", "record_ids": ["p01"], "start_s": 0.5,
                      "end_s": 0.5, "method": "frame_pontual", "artifact_path": None}],
        "findings": [{"id": "f01", "category": "tipografia_hierarquia",
                      "status": "observado", "evidence_ids": ["e01"], "limitations": []}],
        "reusable_rules": [{"id": "r01", "finding_ids": ["f01"], "scope": "pontual"}],
        "limitations": ["Amostragem não equivale a revisão temporal integral."],
    }


def test_valid_partial_recipe():
    assert validate_recipe(recipe())["status"] == "valid"


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True])
def test_invalid_durations_rejected(value):
    data = recipe()
    data["reference"]["duration_s"] = value
    with pytest.raises(ValueError):
        validate_recipe(data)


def test_point_samples_cannot_be_complete():
    data = recipe()
    data["coverage"]["visual"]["status"] = "completa"
    with pytest.raises(ValueError):
        validate_recipe(data)


def test_missing_evidence_rejected():
    data = recipe()
    data["findings"][0]["evidence_ids"] = ["inventado"]
    with pytest.raises(ValueError):
        validate_recipe(data)


def test_unobserved_rule_rejected():
    data = recipe()
    data["reusable_rules"][0]["finding_ids"] = ["ausente"]
    with pytest.raises(ValueError):
        validate_recipe(data)


@pytest.mark.parametrize("start,end", [(2, 1), (0, 100), (-1, 1), (math.nan, 1)])
def test_out_of_range_evidence_rejected(start, end):
    data = recipe()
    data["evidence"][0].update(start_s=start, end_s=end)
    with pytest.raises(ValueError):
        validate_recipe(data)


def test_duplicate_evidence_rejected():
    data = recipe()
    data["evidence"].append(deepcopy(data["evidence"][0]))
    with pytest.raises(ValueError):
        validate_recipe(data)


def test_unknown_media_is_not_complete():
    data = recipe()
    data["reference"]["duration_s"] = None
    data["coverage"]["audio"]["status"] = "completa"
    with pytest.raises(ValueError):
        validate_recipe(data)


def manifest():
    return {"fps": 30, "width": 720, "height": 1280,
            "frames": [{"index": i, "file": f"frames/{i:06d}.png"} for i in range(300)]}


def test_valid_sequence_manifest():
    assert validate_frame_manifest(manifest(), count=300, fps=30, width=720, height=1280)["frames"] == 300


@pytest.mark.parametrize("problem", ["gap", "duplicate", "fps", "width", "absolute", "traversal"])
def test_invalid_sequence_rejected(problem):
    data = manifest()
    if problem == "gap":
        data["frames"].pop(100)
    elif problem == "duplicate":
        data["frames"][10] = dict(data["frames"][9])
    elif problem in {"fps", "width"}:
        data[problem] += 1
    else:
        data["frames"][0]["file"] = "/tmp/unsafe.png" if problem == "absolute" else "../unsafe.png"
    with pytest.raises(ValueError):
        validate_frame_manifest(data, count=300, fps=30, width=720, height=1280)


def test_projection_orientation_and_roraima():
    bbox = [-80, -25, -35, 20]
    assert project_equirectangular(-80, 20, bbox, 900, 900) == (0, 0)
    assert project_equirectangular(-35, -25, bbox, 900, 900) == (900, 900)
    x, y = project_equirectangular(-60.76, 5.14, bbox, 900, 900)
    assert x == pytest.approx(384.8)
    assert y == pytest.approx(297.2)


@pytest.mark.parametrize("lon,lat", [(200, 0), (0, 91), (float("nan"), 0), (-30, 5)])
def test_outside_map_not_silently_clamped(lon, lat):
    with pytest.raises(ValueError):
        project_equirectangular(lon, lat, [-80, -25, -35, 20], 900, 900)


def test_pilot_reference_package_resolves():
    import csv
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    base = root / "pilots/r1059-roraima/reference"
    data = json.loads((base / "receita-visual.json").read_text(encoding="utf-8"))
    validate_recipe(data)
    rows = list(csv.DictReader((base / "mapa-de-cenas.csv").open(encoding="utf-8")))
    assert rows
    previous = 0.0
    for row in rows:
        start, end = float(row["start_s"]), float(row["end_s"])
        assert start == pytest.approx(previous)
        assert end > start
        previous = end
    assert previous == pytest.approx(data["reference"]["duration_s"])
    ids = {item["id"] for item in data["findings"]}
    assert all(set(rule["finding_ids"]) <= ids for rule in data["reusable_rules"])
