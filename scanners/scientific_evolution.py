"""R990: avaliação automática de dois candidatos fechados; não modifica scanners."""
from __future__ import annotations

import argparse
import hashlib
import json

from scanners.scientific_reasoning_scanner import ScientificReasoningScanner


def confusion_metrics(labels, predictions):
    if (not isinstance(labels, list) or not isinstance(predictions, list)
            or not labels or len(labels) != len(predictions)
            or any(type(value) is not bool for value in labels + predictions)):
        raise ValueError("Rótulos e predições booleanos de mesmo tamanho são obrigatórios")
    tp = sum(y and p for y, p in zip(labels, predictions))
    fp = sum(not y and p for y, p in zip(labels, predictions))
    tn = sum(not y and not p for y, p in zip(labels, predictions))
    fn = sum(y and not p for y, p in zip(labels, predictions))
    recall = tp / (tp + fn) if tp + fn else None
    specificity = tn / (tn + fp) if tn + fp else None
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "n": len(labels),
            "precision": tp / (tp + fp) if tp + fp else None, "recall": recall,
            "balanced_accuracy": (recall + specificity) / 2 if recall is not None and specificity is not None else None}


def _validate_corpus(rows):
    if not isinstance(rows, list) or not 8 <= len(rows) <= 200:
        raise ValueError("Corpus deve ter 8 a 200 casos")
    ids, texts, groups = set(), set(), {}
    splits = {"dev": [], "holdout": []}
    total = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "group", "split", "text", "label"}:
            raise ValueError("Campos do caso inválidos")
        if any(not isinstance(row[k], str) or not row[k].strip() for k in ("id", "group", "split", "text")):
            raise ValueError("Texto ou identificação ausente")
        if len(row["id"]) > 80 or len(row["group"]) > 80 or len(row["text"]) > 8000:
            raise ValueError("Caso excessivo")
        split = row["split"]
        if split not in splits or type(row["label"]) is not bool or row["id"] in ids:
            raise ValueError("Partição, ID ou rótulo inválido")
        normalized = " ".join(ScientificReasoningScanner._normalize(row["text"]).split())
        digest = hashlib.sha256(normalized.encode()).hexdigest()
        if digest in texts or (row["group"] in groups and groups[row["group"]] != split):
            raise ValueError("Duplicação ou vazamento entre partições")
        total += len(row["text"].encode("utf-8"))
        ids.add(row["id"])
        texts.add(digest)
        groups[row["group"]] = split
        splits[split].append(dict(row))
    if total > 256_000:
        raise ValueError("Corpus excede 256 KB")
    for cases in splits.values():
        if len(cases) < 4 or {r["label"] for r in cases} != {True, False}:
            raise ValueError("Cada partição requer ao menos 4 casos e ambas as classes")
    return splits


def evaluate_candidates(rows):
    splits = _validate_corpus(rows)
    scanner = ScientificReasoningScanner()
    metrics = {"legacy": {}, "contextual": {}}
    # A decisão usa só desenvolvimento. Holdout não escolhe candidato substituto.
    for split in ("dev", "holdout"):
        cases = splits[split]
        labels = [row["label"] for row in cases]
        reports = [scanner.scan_text(row["text"]) for row in cases]
        metrics["legacy"][split] = confusion_metrics(labels, [bool(r["detected_fallacies"]) for r in reports])
        metrics["contextual"][split] = confusion_metrics(labels, [r["triage"]["asserted_trigger_count"] > 0 for r in reports])
        if split == "dev":
            selected = ("contextual" if metrics["contextual"][split]["balanced_accuracy"]
                        > metrics["legacy"][split]["balanced_accuracy"] else "legacy")
    baseline, candidate = metrics["legacy"]["holdout"], metrics[selected]["holdout"]
    regression = candidate["fp"] > baseline["fp"] or candidate["fn"] > baseline["fn"]
    delta = {key: candidate[key] - baseline[key] for key in ("fp", "fn", "balanced_accuracy")}
    status = "no_improvement" if selected == "legacy" else "regression_blocked" if regression else "candidate_recommended"
    serialized = json.dumps(rows, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()
    return {"status": status, "selected_on_development": selected, "metrics": metrics,
            "holdout_delta": delta, "holdout_improvement": delta["balanced_accuracy"] > 0 and not regression,
            "corpus_sha256": hashlib.sha256(serialized).hexdigest(),
            "split_sizes": {name: len(cases) for name, cases in splits.items()},
            "promoted": False, "authority_changed": False, "human_review_required": True,
            "external_validation": False, "agents_executed": False,
            "proposed_tasks": [
                {"agent_id": "scientist-falsification", "task": "Auditar erros, negação, citação endossada e casos adversariais."},
                {"agent_id": "scientist-statistics", "task": "Avaliar tamanho, dependência entre casos e incerteza das métricas."},
                {"agent_id": "scientist-audit", "task": "Revisar corpus independente antes de autorizar adoção."}],
            "limitations": ["Rótulos e independência dos grupos são declarados pelo fornecedor do corpus.",
                            "Holdout pequeno não demonstra generalização ou validade científica.",
                            "Citações endossadas, ironia e negação distante podem exigir revisão humana.",
                            "Recomendação não altera código, permissões, modelos, confiança ou outros scanners."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compara candidatos de triagem; não promove nem altera scanners.")
    parser.add_argument("--corpus-json", required=True)
    args = parser.parse_args(argv)
    from scientific_lab.council import decode_json
    result = evaluate_candidates(decode_json(args.corpus_json, 320_000))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
