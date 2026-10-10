"""Comportamento dos controles e do guia do podcast, sem navegador ou rede."""

import json
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "artigos" / "pucrs-roteamento-atencao" / "site" / "podcast.mjs"


def execute_node(body):
    node = shutil.which("node")
    assert node, "Node.js é necessário para conferir o player do podcast."
    script = (
        "import { formatTime, seekPosition, progressPercent, REFLECTIONS } "
        f"from {json.dumps(MODULE.as_uri())};\n" + body
    )
    result = subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize(
    "seconds,expected",
    [(0, "00:00"), (9.99, "00:09"), (60, "01:00"),
     (1355.766712, "22:35"), (3599, "59:59"),
     (3600, "01:00:00"), (3661.9, "01:01:01"), (360000, "100:00:00"),
     (-20, "00:00")],
)
def test_time_labels_use_elapsed_whole_seconds(seconds, expected):
    assert execute_node(f"process.stdout.write(JSON.stringify(formatTime({seconds})));" ) == expected


@pytest.mark.parametrize("invalid", ["NaN", "Infinity", "-Infinity", "null", "undefined", "'15'", "true", "{}", "[]"])
def test_invalid_values_never_create_invalid_labels_or_positions(invalid):
    result = execute_node(
        f"const bad={invalid}; process.stdout.write(JSON.stringify({{"
        "label:formatTime(bad),current:seekPosition(bad,15,100),"
        "delta:seekPosition(40,bad,100),duration:seekPosition(40,15,bad),"
        "progressCurrent:progressPercent(bad,100),progressDuration:progressPercent(40,bad)}));"
    )
    assert result == {
        "label": "00:00", "current": 0, "delta": 0, "duration": 0,
        "progressCurrent": 0, "progressDuration": 0,
    }


@pytest.mark.parametrize("current,delta,duration,expected", [
    (40, 15, 100, 55), (40, -15, 100, 25),
    (2, -15, 100, 0), (95, 15, 100, 100),
    (-10, 15, 100, 15), (110, -15, 100, 85),
    (20.25, 15, 100.5, 35.25), (40, 15, 0, 0), (40, 15, -10, 0),
])
def test_seeking_moves_in_both_directions_and_saturates(current, delta, duration, expected):
    assert execute_node(
        f"process.stdout.write(JSON.stringify(seekPosition({current},{delta},{duration})));"
    ) == pytest.approx(expected)


def test_finite_overflow_cannot_escape_media_duration():
    result = execute_node(
        "process.stdout.write(JSON.stringify({end:seekPosition(Number.MAX_VALUE,Number.MAX_VALUE,Number.MAX_VALUE),"
        "start:seekPosition(0,-Number.MAX_VALUE,Number.MAX_VALUE),"
        "progress:progressPercent(Number.MAX_VALUE,Number.MIN_VALUE)}));"
    )
    assert result == {"end": float.fromhex("0x1.fffffffffffffp+1023"), "start": 0, "progress": 100}


@pytest.mark.parametrize("current,duration,expected", [
    (0, 100, 0), (25, 100, 25), (50.5, 101, 50),
    (100, 100, 100), (150, 100, 100), (-10, 100, 0),
    (50, 0, 0), (50, -100, 0),
])
def test_progress_uses_actual_duration_and_stays_between_zero_and_one_hundred(current, duration, expected):
    assert execute_node(
        f"process.stdout.write(JSON.stringify(progressPercent({current},{duration})));"
    ) == pytest.approx(expected)


def test_reflection_content_is_complete_and_has_relevant_followup_destinations():
    reflections = execute_node("process.stdout.write(JSON.stringify(REFLECTIONS));")
    assert len(reflections) == 3
    assert len({row["id"] for row in reflections}) == 3
    assert [row["href"] for row in reflections] == ["#ecossistema", "#laboratorio", "#evidencias"]
    for row in reflections:
        assert all(isinstance(row[key], str) and row[key].strip()
                   for key in ("id", "title", "prompt", "answer", "href", "linkLabel"))
        assert "timestamp" not in row
    project, weight, proofs = [row["answer"].casefold() for row in reflections]
    assert "roteamento" in project and "mira" in project
    assert "probabilidade" in weight and "sucesso" in weight and "não" in weight
    assert "propriedades" in proofs and "programa" in proofs and "não" in proofs
