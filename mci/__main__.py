"""CLI do pacote mci — métricas descritivas inspiradas em IIT.

Uso:
    python -m mci iiit-metrics --help
    python -m mci iiit-metrics analyze --limit 50 --n-states 10
    python -m mci iiit-metrics score --traces traces.json
    python -m mci iiit-metrics classify --score 0.75
    python -m mci iiit-metrics graph --traces traces.json
    python -m mci iiit-metrics synthetic --n-traces 20 --seed 0

Nenhum comando mede consciência ou calcula Φ. ``analyze`` falha de forma
explícita quando o MetaBus está indisponível; dados sintéticos só existem no
subcomando ``synthetic`` e são rotulados.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Optional, Sequence

from mci.iiit_metrics import (
    DEFAULT_N_STATES,
    build_causal_graph_from_traces,
    calculate_causal_efficacy,
    classify_iit_maturity_level,
    collect_trace_features,
    iiit_metrics_cli,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mci",
        description="Métricas descritivas do ecossistema; não medem consciência e não calculam Φ.",
    )
    metrics = parser.add_subparsers(dest="metric", required=True)
    iit = metrics.add_parser(
        "iiit-metrics",
        help="Métricas descritivas inspiradas em IIT (sem Φ e sem consciência).",
    )
    commands = iit.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser(
        "analyze",
        help="Analisa eventos do MetaBus; falha se a telemetria estiver indisponível.",
    )
    analyze.add_argument("--limit", type=int, default=50, help="Eventos recentes a analisar.")
    analyze.add_argument("--n-states", type=int, default=DEFAULT_N_STATES, help="Bins de discretização.")
    analyze.add_argument("--agent", default=None, help="Filtro de agente (metadado).")

    score = commands.add_parser(
        "score",
        help="Calcula métricas a partir de um arquivo JSON de traces.",
    )
    score.add_argument("--traces", required=True, help="Arquivo JSON com lista de traces.")
    score.add_argument("--n-states", type=int, default=DEFAULT_N_STATES, help="Bins de discretização.")

    classify = commands.add_parser(
        "classify",
        help="Classifica descritivamente um score de 0 a 1.",
    )
    classify.add_argument("--score", type=float, required=True, help="Score descritivo (0 a 1).")

    graph = commands.add_parser(
        "graph",
        help="Mostra o grafo de transição sequencial (não causal).",
    )
    graph.add_argument("--traces", required=True, help="Arquivo JSON com lista de traces.")
    graph.add_argument("--n-states", type=int, default=DEFAULT_N_STATES, help="Bins de discretização.")

    synthetic = commands.add_parser(
        "synthetic",
        help="Gera dados sintéticos explícitos para teste; não representam telemetria.",
    )
    synthetic.add_argument("--n-traces", type=int, default=50, help="Número de traces sintéticas.")
    synthetic.add_argument("--n-states", type=int, default=DEFAULT_N_STATES, help="Bins de discretização.")
    synthetic.add_argument("--seed", type=int, default=0, help="Semente reprodutível.")
    return parser


def _read_traces(path: str):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Erro ao ler traces: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(data, list):
        print("Erro: o arquivo de traces deve conter uma lista JSON.", file=sys.stderr)
        raise SystemExit(1)
    return data


def _synthetic_traces(n_traces: int, seed: int):
    if n_traces < 1:
        raise SystemExit("Erro: --n-traces deve ser >= 1.")
    rng = random.Random(seed)
    outcomes = ["success", "failure", "abstained", "missing"]
    weights = [0.60, 0.15, 0.20, 0.05]
    return [
        {
            "action_id": f"synthetic_{index}",
            "outcome": rng.choices(outcomes, weights=weights, k=1)[0],
            "confidence_after": round(rng.uniform(0.30, 0.95), 3),
            "strategy": f"s{rng.randrange(4)}",
        }
        for index in range(n_traces)
    ]


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "analyze":
        payload = iiit_metrics_cli(
            limit=args.limit,
            session_id=args.agent,
            n_states=args.n_states,
        )
        print(payload["formatted_output"], flush=True)
        if not payload["result"].available:
            reason = getattr(payload["result"], "metadata", {}).get("reason")
            if reason == "no_outcomes":
                message = "Erro: nenhum outcome utilizável nos eventos; nenhum score foi calculado."
            else:
                message = "Erro: telemetria indisponível; nenhum score foi calculado."
            print(message + " Nenhum dado sintético foi gerado.", file=sys.stderr)
            raise SystemExit(2)
        return 0

    if args.command == "score":
        traces = _read_traces(args.traces)
        payload = iiit_metrics_cli(traces=traces, n_states=args.n_states)
        print(payload["formatted_output"])
        if not payload["result"].available:
            raise SystemExit(2)
        return 0

    if args.command == "classify":
        print(f"Classificação: {classify_iit_maturity_level(args.score)}")
        return 0

    if args.command == "graph":
        traces = _read_traces(args.traces)
        features = collect_trace_features(traces, n_states=args.n_states)
        if features["total_traces"] == 0:
            print("Status: insufficient_data — sem traces para o grafo.", file=sys.stderr)
            raise SystemExit(2)
        graph_result = build_causal_graph_from_traces(features)
        efficacy = calculate_causal_efficacy(graph_result)
        print("=== Grafo de Transição Sequencial (não causal) ===")
        print(f"Nós: {graph_result.unique_nodes}")
        print(f"Links: {graph_result.total_links}")
        print(f"Densidade: {graph_result.density}")
        print(f"Influência sequencial (não causal): {efficacy}")
        print("Limite: adjacência temporal não demonstra causalidade.")
        return 0

    if args.command == "synthetic":
        print("=== DADOS SINTÉTICOS — não representam telemetria ===")
        traces = _synthetic_traces(args.n_traces, args.seed)
        payload = iiit_metrics_cli(traces=traces, n_states=args.n_states)
        print(payload["formatted_output"])
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
