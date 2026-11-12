"""R1104 P0 - testes de regressao das metricas IIT simplificadas.

Os testes usam estado temporario. Nenhum deles deve gravar em
``evolution/cycles.json`` real ou no MetaBus de producao.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault(
    "EVOLUTION_STATE_PATH",
    str(Path(tempfile.mkdtemp(prefix="r1104-evolution-")) / "cycles.json"),
)

from evolution.cycles import EvolutionRegistry  # noqa: E402
from mci import iiit_metrics as mod  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def traces_with(outcome: str = "success", strategy: str = "s0", n: int = 40):
    return [
        {
            "action_id": f"a{i}",
            "outcome": outcome,
            "confidence_after": 0.6,
            "strategy": strategy,
        }
        for i in range(n)
    ]


def run_cli(args, tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["MCI_STATE_DIR"] = str(tmp_path / "mci")
    env["EVOLUTION_STATE_PATH"] = str(tmp_path / "cycles.json")
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "mci", *args],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=90,
    )


def test_same_traces_same_score_across_hash_seeds(tmp_path):
    traces = [
        {
            "action_id": f"a{i}_{(i * 7) % 13}",
            "outcome": ["success", "failure", "abstained", "missing"][i % 4],
            "confidence_after": round(0.05 + ((i * 37) % 90) / 100, 3),
            "strategy": f"s{i % 4}",
        }
        for i in range(60)
    ]
    traces_path = tmp_path / "traces.json"
    traces_path.write_text(json.dumps(traces), encoding="utf-8")
    code = (
        "import json, sys\n"
        "from mci import iiit_metrics\n"
        "traces = json.loads(open(sys.argv[1], encoding='utf-8').read())\n"
        "r = iiit_metrics.calculate_simplified_ii(traces, n_states=10)\n"
        "print(json.dumps({'score': r.score, 'mutual_info': r.mutual_info}))\n"
    )
    rows = []
    for seed in ("1", "2"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        env["MCI_STATE_DIR"] = str(tmp_path / f"mci-{seed}")
        env["EVOLUTION_STATE_PATH"] = str(tmp_path / f"cycles-{seed}.json")
        env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", code, str(traces_path)],
            cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=90,
        )
        assert result.returncode == 0, result.stderr
        rows.append(json.loads(result.stdout.strip().splitlines()[-1]))
    assert rows[0]["score"] == rows[1]["score"]
    assert rows[0]["mutual_info"] == rows[1]["mutual_info"]


def test_strategy_diversity_distinguishes_one_and_four():
    one = mod.calculate_simplified_ii(traces_with(strategy="s0"))
    four = mod.calculate_simplified_ii(
        [dict(t, strategy=f"s{i % 4}") for i, t in enumerate(traces_with())]
    )
    skewed_traces = traces_with()
    for i, trace in enumerate(skewed_traces):
        trace["strategy"] = "s0" if i < 28 else f"s{i % 4}"
    skewed = mod.calculate_simplified_ii(skewed_traces)

    assert one.strategy_diversity == 0.0
    assert 0.95 <= four.strategy_diversity <= 1.0
    assert 0.0 < skewed.strategy_diversity < four.strategy_diversity


def test_payload_is_read_and_missing_is_not_abstained(monkeypatch):
    events = [
        {"event_id": "e1", "payload": {"action_id": "a1", "outcome": "success", "confidence": 0.9, "strategy": "s1"}},
        {"event_id": "e2", "payload": {"action_id": "a2", "outcome": "failure", "confidence": 0.2, "strategy": "s2"}},
        {"event_id": "e3", "payload": {"action_id": "a3", "outcome": "abstained", "confidence": 0.5, "strategy": "s3"}},
        {"event_id": "e4", "payload": {"action_id": "a4"}},
        {"event_id": "e5", "payload": {"action_id": "a5", "outcome": "success", "confidence": "bad", "strategy": ""}},
    ]
    monkeypatch.setattr(mod.metabus, "get_recent_events", lambda limit=100: events)

    features = mod.collect_trace_features(limit=10)

    assert features["total_traces"] == 5
    assert features["success_count"] == 2
    assert features["failure_count"] == 1
    assert features["abstained_count"] == 1
    assert features["missing_outcome_count"] == 1
    assert features["confidence_missing_count"] == 2
    assert features["strategy_missing_count"] == 2


def test_abstention_is_not_penalized_and_coverage_is_separate():
    success = mod.calculate_simplified_ii(traces_with(outcome="success"))
    abstained = mod.calculate_simplified_ii(traces_with(outcome="abstained"))

    assert success.available is True
    assert abstained.available is True
    assert success.score == abstained.score
    assert success.abstention_rate == 0.0
    assert abstained.abstention_rate == 1.0
    assert success.metadata["coverage"] == 1.0
    assert abstained.metadata["coverage"] == 0.0
    assert success.metadata["mi_conditioning_variable"] == "strategy_or_missing"


def test_all_missing_outcomes_is_insufficient_data():
    traces = [{"action_id": f"a{i}", "strategy": "s0"} for i in range(5)]
    result = mod.calculate_simplified_ii(traces)

    assert result.available is False
    assert result.score is None
    assert result.metadata["reason"] == "no_outcomes"


def test_no_traces_is_insufficient_data_without_numeric_score():
    result = mod.calculate_simplified_ii([])

    assert result.available is False
    assert result.score is None
    assert result.status == "insufficient_data"


def test_registry_uses_real_signature_and_does_not_touch_real_file(tmp_path):
    real_registry = ROOT / "evolution" / "cycles.json"
    before = sha256(real_registry)
    registry = EvolutionRegistry(state_path=str(tmp_path / "cycles.json"))
    result = mod.IITMetricsResult(
        score=0.5,
        entropy=0.2,
        mutual_info=0.1,
        causal_efficacy=0.3,
        strategy_diversity=0.4,
        abstention_rate=0.0,
        trace_count=10,
        metadata={},
    )

    recorded = mod.record_to_evolution_registry(
        result,
        "R1104-test",
        "contraprova isolada",
        registry=registry,
    )

    assert recorded["round_id"] == "R1104-test"
    assert recorded["iit_simplified"]["score"] == 0.5
    assert (tmp_path / "cycles.json").exists()
    assert sha256(real_registry) == before


def test_classification_does_not_claim_publication_readiness():
    label = mod.classify_iit_maturity_level(0.81)

    assert "publica" not in label.lower()
    assert "research_grade" not in label.lower()
    assert "apto" not in label.lower()
    assert "insufficient" in mod.classify_iit_maturity_level(None).lower()


def test_n_states_controls_confidence_distribution():
    traces = traces_with()
    features = mod.collect_trace_features(traces, n_states=4)
    result = mod.calculate_simplified_ii(traces, n_states=4)

    assert len(features["confidence_distribution"]) == 4
    assert result.metadata["n_states_used"] == 4
    assert result.metadata["confidence_distribution_length"] == 4


def test_cli_has_one_definition_and_help_exits_zero(tmp_path):
    source = (ROOT / "mci" / "iiit_metrics.py").read_text(encoding="utf-8")
    assert source.count("def iiit_metrics_cli") == 1

    result = run_cli(["iiit-metrics", "--help"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert "analyze" in result.stdout


def test_cli_analyze_fails_closed_without_synthetic(monkeypatch, capsys):
    import mci.__main__ as cli

    class Unavailable:
        available = False
        status = "insufficient_data"

    monkeypatch.setattr(
        cli,
        "iiit_metrics_cli",
        lambda **kwargs: {
            "result": Unavailable(),
            "formatted_output": "Status: insufficient_data\n",
            "raw_features": {},
        },
    )

    with pytest.raises(SystemExit) as exc:
        cli.main(["iiit-metrics", "analyze"])

    assert exc.value.code != 0
    output = capsys.readouterr()
    text = output.out + output.err
    assert "insufficient_data" in text
    assert "synthetic" not in text.lower()


def test_synthetic_command_is_explicitly_labeled(tmp_path):
    result = run_cli(["iiit-metrics", "synthetic", "--n-traces", "5", "--seed", "0"], tmp_path)
    assert result.returncode == 0, result.stderr
    text = result.stdout.lower()
    assert "sintétic" in text or "synthetic" in text
    assert "não representam telemetria" in text


def test_score_output_declares_non_causal_limit(tmp_path):
    traces_path = tmp_path / "traces.json"
    traces_path.write_text(json.dumps(traces_with()), encoding="utf-8")
    result = run_cli(["iiit-metrics", "score", "--traces", str(traces_path)], tmp_path)

    assert result.returncode == 0, result.stderr
    text = result.stdout.lower()
    assert "não causal" in text
    assert "não é φ" in text
    assert "apto para publicação" not in text
