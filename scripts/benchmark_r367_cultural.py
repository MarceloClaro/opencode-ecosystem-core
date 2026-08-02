# -*- coding: utf-8 -*-
"""Benchmark cultural medido — SPEC-935-R367.

Executa os guardas de tradução reais (R364/R365/R366) sobre o corpus
interno rotulado e calcula precisão/recall/F1 por código. Os números são
descritivos deste corpus, nesta data — não constituem validação externa
nem promessa de desempenho, e o relatório diz isso explicitamente.

Uso:
    python3 scripts/benchmark_r367_cultural.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from translation.author_voice import review_segment  # noqa: E402
from translation.back_translation import verify  # noqa: E402
from translation.cultural_episteme import build_terminology_delta  # noqa: E402
from translation.terminology_graph import TerminologyGraph  # noqa: E402

CORPUS_PATH = os.path.join(
    ROOT, "validacao_externa", "cultural_episteme", "benchmark_corpus_r367.json"
)
REPORT_JSON = os.path.join(
    ROOT, "validacao_externa", "cultural_episteme", "benchmark_r367_report.json"
)
REPORT_MD = os.path.join(
    ROOT, "validacao_externa", "cultural_episteme", "benchmark_r367_report.md"
)

DISCLAIMER = (
    "Números medidos em corpus interno rotulado, pequeno e construído pela "
    "própria equipe; NÃO constituem validação externa, benchmark independente "
    "nem promessa de desempenho em obras reais. Servem para acompanhar a "
    "evolução das regras e documentar limitações conhecidas."
)


# ── fixtures determinísticas (mesmo desenho dos testes R364/R365) ─────

def _request(revision: str) -> Dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "review_id": "benchmark-r367",
        "segment_id": "BENCH:setup",
        "source_language": "pt-BR",
        "target_language": "en-US",
        "source_text": "setup",
        "translated_text": "setup",
        "author_voice_profile": {
            "narrator_age": "child",
            "region": "Sertão do Ceará",
            "register": "oral, memorialístico e popular",
        },
        "terminology_graph": {
            "graph_id": "benchmark-terms",
            "revision": revision,
            "concepts": [],
        },
        "historical_context": {
            "period": "1915",
            "region": "Ceará",
            "support_status": "documented",
            "provenance": [{
                "source": "corpus interno R367",
                "author": "equipe editorial",
                "date": "2026-08-02",
                "limitations": "fixture de benchmark",
            }],
        },
        "cultural_dossier": {
            "target_variety": "English (United States)",
            "provenance": [{
                "source": "corpus interno R367",
                "author": "equipe editorial",
                "date": "2026-08-02",
                "limitations": "fixture de benchmark",
            }],
            "anachronism_markers": [],
        },
        "previous_translation_decisions": [],
    }


def _build_graph() -> TerminologyGraph:
    graph = TerminologyGraph("benchmark-terms")
    graph.apply_delta(build_terminology_delta(
        _request("0"),
        {
            "source_term": "retirante",
            "entity_type": "regional",
            "preferred_en": "retirante",
            "preferred_zh_cn": "逃荒者",
            "preserve_portuguese": True,
            "forbidden_translations": ["migrant", "refugee"],
        },
        "termo cultural central; não domesticar",
    ))
    graph.apply_delta(build_terminology_delta(
        _request("1"),
        {
            "source_term": "olho",
            "entity_type": "symbol",
            "preferred_en": "the eye",
            "preferred_zh_cn": "眼睛",
            "preserve_portuguese": False,
            "forbidden_translations": [],
        },
        "símbolo recorrente da obra",
    ))
    graph.approve("retirante", reviewer="revisora-en-01")
    graph.approve("olho", reviewer="revisora-en-01")
    return graph


def _voice_profile() -> Dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "profile_id": "voice-benchmark-r367",
        "work_id": "benchmark",
        "register": "oral, memorialístico, sertanejo",
        "voice_markers": [
            {"marker": "retirante", "kind": "regionalism", "strategy": "preserve"},
            {"marker": "oxente", "kind": "orality", "strategy": "gloss"},
            {
                "marker": "Currais do Governo",
                "kind": "institution",
                "strategy": "adapt",
                "approved_renderings": {
                    "en": ["Government Corrals"],
                    "zh_cn": ["政府围栏营"],
                },
            },
        ],
        "forbidden_modernisms": ["smartphone", "ok", "stress"],
        "provenance": [{
            "source": "corpus interno R367",
            "author": "equipe editorial",
            "date": "2026-08-02",
            "limitations": "fixture de benchmark",
        }],
    }


def _bt_payload(case_input: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "review_id": "benchmark-r367",
        "segment_id": "BENCH:bt",
        "source_text": case_input["source_text"],
        "back_translated_text": case_input["back_translated_text"],
        "translated_text": case_input.get("translated_text", ""),
        "source_language": "pt-BR",
        "pivot_language": "en-US",
        "declared_entities": ["Joaquim"],
        "glossary_terms": [
            {"source_term": "retirante", "preserve_portuguese": True},
        ],
        "provenance": [{
            "source": "corpus interno R367",
            "author": "equipe editorial",
            "date": "2026-08-02",
            "limitations": "fixture de benchmark",
        }],
    }


# ── execução ──────────────────────────────────────────────────────────

def _predict(case: Dict[str, Any], graph: TerminologyGraph,
             profile: Dict[str, Any]) -> Set[str]:
    module = case["module"]
    inp = case["input"]
    if module == "terminology":
        findings = graph.check_segment(
            inp["source_text"], inp["translated_text"], inp["target_language"]
        )
    elif module == "voice":
        findings = review_segment(
            profile, inp["source_text"], inp["translated_text"],
            inp["target_language"],
        )["findings"]
    elif module == "backtranslation":
        findings = verify(_bt_payload(inp))["findings"]
    else:
        raise ValueError(f"módulo desconhecido: {module}")
    return {f["code"] for f in findings}


def _safe_div(num: int, den: int):
    return (num / den) if den else None


def run_benchmark(corpus_path: str = CORPUS_PATH) -> Dict[str, Any]:
    with open(corpus_path, encoding="utf-8") as f:
        corpus = json.load(f)

    profile = _voice_profile()
    tp: Dict[str, int] = {}
    fp: Dict[str, int] = {}
    fn: Dict[str, int] = {}
    case_results = []

    for case in corpus["cases"]:
        graph = _build_graph()  # grafo novo por caso: sem estado acumulado
        predicted = _predict(case, graph, profile)
        expected = set(case["expected_codes"])
        for code in predicted & expected:
            tp[code] = tp.get(code, 0) + 1
        for code in predicted - expected:
            fp[code] = fp.get(code, 0) + 1
        for code in expected - predicted:
            fn[code] = fn.get(code, 0) + 1
        case_results.append({
            "case_id": case["case_id"],
            "module": case["module"],
            "expected": sorted(expected),
            "predicted": sorted(predicted),
            "match": predicted == expected,
            "known_limitation": bool(case.get("known_limitation", False)),
        })

    codes = sorted(set(tp) | set(fp) | set(fn))
    per_code = {}
    for code in codes:
        code_tp, code_fp, code_fn = tp.get(code, 0), fp.get(code, 0), fn.get(code, 0)
        precision = _safe_div(code_tp, code_tp + code_fp)
        recall = _safe_div(code_tp, code_tp + code_fn)
        f1 = (
            _safe_div(2 * precision * recall, precision + recall)
            if precision is not None and recall is not None and (precision + recall)
            else None
        )
        per_code[code] = {
            "tp": code_tp, "fp": code_fp, "fn": code_fn,
            "precision": precision, "recall": recall, "f1": f1,
        }

    total_tp, total_fp, total_fn = sum(tp.values()), sum(fp.values()), sum(fn.values())
    micro = {
        "precision": _safe_div(total_tp, total_tp + total_fp),
        "recall": _safe_div(total_tp, total_tp + total_fn),
    }

    return {
        "schema_version": "1.0.0",
        "spec": "SPEC-935-R367",
        "measured": True,
        "claim": "internal-fixture-benchmark",
        "disclaimer": DISCLAIMER,
        "corpus_size": len(corpus["cases"]),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "per_code": per_code,
        "micro": micro,
        "cases": case_results,
    }


def _fmt(value) -> str:
    return "—" if value is None else f"{value:.2f}"


def write_reports(report: Dict[str, Any]) -> None:
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    lines = [
        "# Benchmark Cultural Medido — R367",
        "",
        f"Gerado em {report['generated_at']} sobre corpus interno rotulado de "
        f"{report['corpus_size']} casos.",
        "",
        f"> {report['disclaimer']}",
        "",
        "Este relatório NÃO constitui validação externa. Qualquer uso comercial",
        "destes números deve citá-los como medição descritiva em corpus interno,",
        "com data e tamanho do corpus.",
        "",
        "## Métricas por código",
        "",
        "| Código | TP | FP | FN | Precisão | Recall | F1 |",
        "|---|---|---|---|---|---|---|",
    ]
    for code, m in sorted(report["per_code"].items()):
        lines.append(
            f"| {code} | {m['tp']} | {m['fp']} | {m['fn']} | "
            f"{_fmt(m['precision'])} | {_fmt(m['recall'])} | {_fmt(m['f1'])} |"
        )
    micro = report["micro"]
    lines += [
        "",
        f"**Agregado (micro):** precisão {_fmt(micro['precision'])}, "
        f"recall {_fmt(micro['recall'])}.",
        "",
        "## Limitações conhecidas evidenciadas pelo corpus",
        "",
    ]
    for case in report["cases"]:
        if case["known_limitation"]:
            lines.append(
                f"- `{case['case_id']}` ({case['module']}): esperado "
                f"{case['expected']}, detectado {case['predicted']} — "
                "limitação conhecida das regras atuais."
            )
    lines.append("")
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    result = run_benchmark()
    write_reports(result)
    print(json.dumps(result["micro"], ensure_ascii=False))
    print(f"relatórios: {REPORT_JSON} / {REPORT_MD}")
