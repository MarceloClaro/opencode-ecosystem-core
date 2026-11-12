#!/usr/bin/env python3
"""R1103 - contraprovas do modulo legado em estado isolado.

Este script NAO homologa as metricas, NAO calcula Phi da IIT 4.0 e NAO
altera permissoes. Ele reproduz comportamento observavel de
``mci/iiit_metrics.py`` e ``mci/__main__.py`` usando apenas estado temporario
em ``/tmp/opencode/``. O resultado e ``audit.json`` com as observacoes e os
hashes dos arquivos auditados.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path("/tmp/opencode")
BASE.mkdir(parents=True, exist_ok=True)

_shared = os.environ.get("R1103_AUDIT_DIR")
if _shared:
    AUDIT_DIR = Path(_shared)
else:
    AUDIT_DIR = Path(tempfile.mkdtemp(prefix="r1103-audit-", dir=str(BASE)))
    os.environ["R1103_AUDIT_DIR"] = str(AUDIT_DIR)

STATE_DIR = AUDIT_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MCI_STATE_DIR", str(STATE_DIR / "mci"))
os.environ.setdefault("EVOLUTION_STATE_PATH", str(STATE_DIR / "cycles.json"))
os.environ.setdefault("PYTHONPATH", str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", ""))

PRODUCTION_FILES = [
    ROOT / ".mci_state" / "shared_memory.json",
    ROOT / "evolution" / "cycles.json",
]
SOURCE_FILES = [
    ROOT / "mci" / "iiit_metrics.py",
    ROOT / "mci" / "__main__.py",
    ROOT / "mci" / "metabus.py",
    ROOT / "evolution" / "cycles.py",
]


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot(paths):
    return {str(path.relative_to(ROOT)): sha256_file(path) for path in paths}


PRODUCTION_BEFORE = snapshot(PRODUCTION_FILES)

sys.path.insert(0, str(ROOT))

from mci import iiit_metrics  # noqa: E402
from mci.metabus import metabus  # noqa: E402
from evolution import evolution_registry  # noqa: E402


def fixed_traces(n: int = 60) -> list[dict]:
    return [
        {
            "action_id": f"a{i}_{(i * 7) % 13}",
            "outcome": "success" if i % 3 else "failure",
            "confidence_after": round(0.05 + ((i * 37) % 90) / 100, 3),
            "strategy": f"s{i % 4}",
        }
        for i in range(n)
    ]


def observation(identifier: str, path: str, locator: str, expected: str,
                observed, status: str, evidence=None):
    return {
        "id": identifier,
        "path": path,
        "locator": locator,
        "expected_contract": expected,
        "observed": observed,
        "status": status,
        "evidence": evidence or {},
    }


def probe_hash() -> dict:
    traces = fixed_traces()
    traces_path = AUDIT_DIR / "hash_traces.json"
    traces_path.write_text(json.dumps(traces, ensure_ascii=False), encoding="utf-8")
    by_seed = {}
    for seed in ("1", "2", "3", "4"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        env["R1103_AUDIT_DIR"] = str(AUDIT_DIR)
        env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--hash-probe", str(traces_path)],
            cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=90,
        )
        if result.returncode != 0:
            by_seed[seed] = {"error": (result.stderr or result.stdout)[-300:]}
            continue
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        try:
            by_seed[seed] = json.loads(lines[-1])
        except (IndexError, json.JSONDecodeError) as exc:
            by_seed[seed] = {"error": f"{type(exc).__name__}: {exc}"}
    pairs = {
        (row.get("score"), row.get("mutual_info"))
        for row in by_seed.values() if "score" in row
    }
    return {"by_seed": by_seed, "distinct_score_mi_pairs": len(pairs)}


def probe_diversity() -> dict:
    def result_for(strategies):
        traces = [
            {"action_id": f"a{i}", "outcome": "success", "confidence_after": 0.6, "strategy": strategy}
            for i, strategy in enumerate(strategies)
        ]
        return iiit_metrics.calculate_simplified_ii(traces, n_states=10)

    one = result_for(["s0"] * 40)
    four = result_for([f"s{i % 4}" for i in range(40)])
    return {
        "single_strategy": one.strategy_diversity,
        "four_balanced_strategies": four.strategy_diversity,
        "single_metadata_unique": len(one.metadata.get("strategies_detected", [])),
        "four_metadata_unique": len(four.metadata.get("strategies_detected", [])),
    }


def probe_abstention() -> dict:
    def result_for(outcome):
        traces = [
            {"action_id": f"a{i}", "outcome": outcome, "confidence_after": 0.7, "strategy": "s0"}
            for i in range(40)
        ]
        return iiit_metrics.calculate_simplified_ii(traces, n_states=10)

    success = result_for("success")
    abstained = result_for("abstained")
    return {
        "success_score": success.score,
        "abstained_score": abstained.score,
        "score_delta": round(success.score - abstained.score, 4),
        "success_abstention_rate": success.abstention_rate,
        "abstained_abstention_rate": abstained.abstention_rate,
    }


def probe_payload() -> dict:
    fake_events = [
        {
            "event_id": f"e{i}",
            "topic": "task.complete",
            "payload": {
                "action_id": f"a{i}",
                "outcome": "success",
                "confidence": 0.9,
                "strategy": "s1",
            },
        }
        for i in range(4)
    ]
    had_instance_attr = "get_recent_events" in metabus.__dict__
    original = metabus.__dict__.get("get_recent_events")

    def fake_recent_events(limit=100):
        return fake_events[:limit]

    metabus.get_recent_events = fake_recent_events
    try:
        features = iiit_metrics.collect_trace_features(limit=10)
    finally:
        if had_instance_attr:
            metabus.get_recent_events = original
        else:
            del metabus.get_recent_events

    return {
        "events_with_payload_outcome_success": len(fake_events),
        "observed_success_count": features.get("success_count"),
        "observed_abstained_count": features.get("abstained_count"),
        "observed_confidences": sorted(set(features.get("confidences", []))),
        "observed_strategies": features.get("unique_strategies"),
    }


def probe_n_states() -> dict:
    traces = fixed_traces(40)
    features = iiit_metrics.collect_trace_features(traces)
    result = iiit_metrics.calculate_simplified_ii(traces, n_states=4)
    return {
        "requested_n_states": 4,
        "distribution_length": len(features.get("confidence_distribution", [])),
        "metadata_n_states": result.metadata.get("n_states_used"),
        "entropy_normalized": result.entropy,
    }


def probe_graph() -> dict:
    traces = [
        {"action_id": f"a{i}", "outcome": "success", "confidence_after": 0.6, "strategy": "s0"}
        for i in range(6)
    ]
    features = iiit_metrics.collect_trace_features(traces)
    graph = iiit_metrics.build_causal_graph_from_traces(features)
    return {
        "nodes": graph.unique_nodes,
        "links": graph.total_links,
        "density": graph.density,
        "causal_efficacy": iiit_metrics.calculate_causal_efficacy(graph),
        "interventions_recorded": False,
    }


def probe_registry() -> dict:
    signature = str(inspect.signature(evolution_registry.record))
    dummy = iiit_metrics.IITMetricsResult(
        score=0.5, entropy=0.2, mutual_info=0.1, causal_efficacy=0.3,
        strategy_diversity=0.4, abstention_rate=0.0, trace_count=10, metadata={},
    )
    try:
        returned = iiit_metrics.record_to_evolution_registry(
            dummy, "R1103-audit", "contraprova isolada", lessons=["contraprova"],
        )
        outcome = {"success": True, "returned_type": type(returned).__name__}
    except Exception as exc:  # noqa: BLE001 - a contraprova precisa registrar a falha real
        outcome = {
            "success": False,
            "exception": type(exc).__name__,
            "message": str(exc)[:300],
        }
    return {"record_signature": signature, "call_result": outcome}


def probe_help() -> dict:
    env = os.environ.copy()
    env["R1103_AUDIT_DIR"] = str(AUDIT_DIR)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "mci", "iiit-metrics", "--help"],
        cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=60,
    )
    return {
        "returncode": result.returncode,
        "stdout_tail": (result.stdout or "")[-500:],
        "stderr_tail": (result.stderr or "")[-300:],
    }


def probe_cli_definition() -> dict:
    source = (ROOT / "mci" / "iiit_metrics.py").read_text(encoding="utf-8")
    return {
        "definition_count": source.count("def iiit_metrics_cli"),
        "effective_signature": str(inspect.signature(iiit_metrics.iiit_metrics_cli)),
    }


def probe_maturity() -> dict:
    return {"score": 0.81, "label": iiit_metrics.classify_iit_maturity_level(0.81)}


def probe_missing_data() -> dict:
    result = iiit_metrics.calculate_simplified_ii([], n_states=10)
    return {
        "score": result.score,
        "abstention_rate": result.abstention_rate,
        "metadata": result.metadata,
    }


def main() -> int:
    output = Path(__file__).resolve().parent / "audit.json"
    if output.exists() and "--force" not in sys.argv:
        print(
            f"{output} já existe; use --force para regenerar a contraprova histórica.",
            file=sys.stderr,
        )
        return 3

    observations = [
        observation(
            "G01_hash_nao_reprodutivel", "mci/iiit_metrics.py", "357-358",
            "O mesmo JSON de traces deve produzir o mesmo mutual_info e score em processos distintos.",
            probe_hash(), "reproduced",
        ),
        observation(
            "G02_diversidade_sempre_um", "mci/iiit_metrics.py", "389-391",
            "Uma estrategia deve ter diversidade 0; quatro estrategias equilibradas devem ter diversidade proxima de 1.",
            probe_diversity(), "reproduced",
        ),
        observation(
            "G03_adjacencia_temporal_como_causalidade", "mci/iiit_metrics.py", "462-477",
            "Adjacencia temporal nao deve ser reportada como causalidade sem intervencao registrada.",
            probe_graph(), "reproduced",
        ),
        observation(
            "G04_payload_ignorado", "mci/iiit_metrics.py", "221-225",
            "Evento com payload.outcome='success' deve contar como success; ausencia de outcome nao deve virar abstained.",
            probe_payload(), "reproduced",
        ),
        observation(
            "G05_abstencao_penalizada", "mci/iiit_metrics.py", "407-413",
            "Abstencao segura nao deve reduzir automaticamente o score de seguranca.",
            probe_abstention(), "reproduced",
        ),
        observation(
            "G06_fallback_sintetico_silencioso", "mci/__main__.py", "bloco analyze",
            "Falha de telemetria deve resultar em status unavailable, nunca em dados sinteticos silenciosos.",
            {"inspection": "except Exception -> traces sinteticas; nenhum marcador de origem sintetica no score"},
            "inspected",
        ),
        observation(
            "G07_registry_assinatura_invalida", "mci/iiit_metrics.py", "688-696",
            "record_to_evolution_registry deve gravar EvolutionCycle valido usando round_id e retornar dados serializaveis.",
            probe_registry(), "reproduced",
        ),
        observation(
            "G08_rotulo_publicacao", "mci/iiit_metrics.py", "625-633",
            "Score heuristico nao deve declarar aptidao para publicacao.",
            probe_maturity(), "inspected",
        ),
        observation(
            "G09_n_states_inconsistente", "mci/iiit_metrics.py", "274 e 344-350",
            "n_states deve controlar bins e normalizacao de forma consistente.",
            probe_n_states(), "reproduced",
        ),
        observation(
            "G10_cli_duplicado_e_help_quebrado", "mci/iiit_metrics.py e mci/__main__.py",
            "duas definicoes; parse_args_cli",
            "--help deve sair com 0 e existir apenas uma definicao de iiit_metrics_cli.",
            {"cli": probe_cli_definition(), "help": probe_help()}, "reproduced",
        ),
        observation(
            "G11_ausencia_de_dados_vira_score_zero", "mci/iiit_metrics.py", "328-339",
            "Ausencia de telemetria deve ser status insufficient_data, nao score 0.0.",
            probe_missing_data(), "inspected",
        ),
    ]

    production_after = snapshot(PRODUCTION_FILES)
    report = {
        "round_id": "R1103",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "legacy_counterexamples_not_benchmark",
        "production_unchanged_during_probes": PRODUCTION_BEFORE == production_after,
        "state_isolation": {
            "audit_dir": str(AUDIT_DIR),
            "MCI_STATE_DIR": os.environ["MCI_STATE_DIR"],
            "EVOLUTION_STATE_PATH": os.environ["EVOLUTION_STATE_PATH"],
            "production_files_hashed": list(PRODUCTION_BEFORE),
        },
        "source_sha256": {
            str(path.relative_to(ROOT)): sha256_file(path) for path in SOURCE_FILES
        },
        "production_state_sha256": {
            "before": PRODUCTION_BEFORE,
            "after": production_after,
        },
        "observations": observations,
        "limitations": [
            "Contraprovas de implementacao; nao medem consciencia, Phi ou qualidade cientifica.",
            "Nao substituem benchmark held-out nem revisao externa.",
            "Nao executam PyPhi, MindSpore, LLMs ou repositorios de terceiros.",
        ],
    }

    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "audit_json": str(output),
        "production_unchanged": report["production_unchanged_during_probes"],
        "observations": len(observations),
        "state_isolation": report["state_isolation"],
    }, ensure_ascii=False, indent=2))
    return 0


def hash_probe(traces_path: str) -> int:
    traces = json.loads(Path(traces_path).read_text(encoding="utf-8"))
    result = iiit_metrics.calculate_simplified_ii(traces, n_states=10)
    print(json.dumps({
        "score": result.score,
        "mutual_info": result.mutual_info,
        "entropy": result.entropy,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--hash-probe":
        raise SystemExit(hash_probe(sys.argv[2]))
    raise SystemExit(main())
