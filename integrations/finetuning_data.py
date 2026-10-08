"""Gate local de dados e comparações para fine-tuning (SPEC-935-R658).

Não treina modelos nem atesta que uma avaliação foi executada. A deduplicação
usa NFKC e espaços normalizados, preserva acentos/case e o texto dos pares
selecionados; não identifica duplicatas semânticas. Diagnósticos não expõem
pares, IDs ou nomes de fontes.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import unicodedata
from typing import Any


_SPLITS = ("train", "validation", "test")
_FIELDS = ("id", "group_id", "input", "output")
_HASH = re.compile(r"[0-9a-fA-F]{64}\Z")


def _normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def _valid_text(value: Any) -> bool:
    if not isinstance(value, str) or not _normalized(value):
        return False
    try:
        value.encode("utf-8")
        return True
    except UnicodeError:
        return False


def _sha(value: Any) -> str:
    serialized = json.dumps(value, sort_keys=True, ensure_ascii=False,
                            separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _diagnostic(code: str, count: int = 1) -> dict:
    return {"code": code, "count": count}


def _blocked(diagnostics: list[dict]) -> dict:
    return {"status": "blocked", "diagnostics": diagnostics,
            "splits": {split: [] for split in _SPLITS}, "manifest": {}}


def _record_key(record: dict) -> tuple[str, ...]:
    return tuple(record[field] for field in ("group_id", "id", "input", "output"))


def validate_and_split(records: list[dict], seed: int = 42) -> dict:
    """Valida pares e prepara três conjuntos determinísticos por fonte.

    Duplicatas normalizadas que envolvem fontes distintas conectam essas
    fontes em um componente indivisível, inclusive transitivamente. Apenas
    uma representação determinística de cada par é mantida. Exigem-se três
    componentes independentes; cerca de 10% deles vão para cada conjunto de
    validação/teste, com pelo menos um em cada. Essa proporção é de componentes,
    não de linhas. Nenhum arquivo é lido ou escrito por esta função.
    """
    if not isinstance(seed, int) or isinstance(seed, bool):
        return _blocked([_diagnostic("invalid_seed")])
    if not isinstance(records, list) or not records:
        return _blocked([_diagnostic("invalid_dataset")])

    valid = []
    invalid_count = 0
    for record in records:
        if not isinstance(record, dict) or any(
            not _valid_text(record.get(field))
            for field in _FIELDS
        ):
            invalid_count += 1
            continue
        # Preserve os textos: normalização serve à identidade/deduplicação,
        # não à remoção de estrutura de prompts, código ou respostas.
        valid.append({"id": _normalized(record["id"]),
                      "group_id": _normalized(record["group_id"]),
                      "input": record["input"], "output": record["output"]})
    if invalid_count:
        return _blocked([_diagnostic("invalid_records", invalid_count)])

    valid.sort(key=_record_key)
    ids: set[str] = set()
    answers: dict[str, str] = {}
    duplicate_ids = 0
    conflicting_answers = 0
    for record in valid:
        if record["id"] in ids:
            duplicate_ids += 1
        ids.add(record["id"])
        question, answer = _normalized(record["input"]), _normalized(record["output"])
        if question in answers and answers[question] != answer:
            conflicting_answers += 1
        answers.setdefault(question, answer)
    diagnostics = []
    if duplicate_ids:
        diagnostics.append(_diagnostic("duplicate_ids", duplicate_ids))
    if conflicting_answers:
        diagnostics.append(_diagnostic("conflicting_answers", conflicting_answers))
    if diagnostics:
        return _blocked(diagnostics)

    groups = sorted({record["group_id"] for record in valid})
    parents = {group: group for group in groups}

    def root(group: str) -> str:
        while parents[group] != group:
            parents[group] = parents[parents[group]]
            group = parents[group]
        return group

    content_sources: dict[tuple[str, str], str] = {}
    unique: dict[tuple[str, str], dict] = {}
    for record in valid:
        key = (_normalized(record["input"]), _normalized(record["output"]))
        if key in content_sources:
            first, second = sorted((root(content_sources[key]), root(record["group_id"])))
            parents[second] = first
        else:
            content_sources[key] = record["group_id"]
            unique[key] = record

    components: dict[str, list[str]] = {}
    for group in groups:
        components.setdefault(root(group), []).append(group)
    component_keys = sorted(components)
    if len(component_keys) < 3:
        return _blocked([_diagnostic("insufficient_independent_groups", len(component_keys))])

    random.Random(seed).shuffle(component_keys)
    holdout_count = max(1, len(component_keys) // 10)
    assigned = {}
    component_counts = {split: 0 for split in _SPLITS}
    group_counts = {split: 0 for split in _SPLITS}
    for index, component in enumerate(component_keys):
        if index < holdout_count:
            split = "validation"
        elif index < 2 * holdout_count:
            split = "test"
        else:
            split = "train"
        assigned[component] = split
        component_counts[split] += 1
        group_counts[split] += len(components[component])

    splits = {split: [] for split in _SPLITS}
    for record in sorted(unique.values(), key=_record_key):
        splits[assigned[root(record["group_id"])]].append(dict(record))
    manifest = {
        "seed": seed,
        "dataset_sha256": _sha(valid),
        "split_sha256": {split: _sha(rows) for split, rows in splits.items()},
        "input_count": len(valid),
        "deduplicated_count": len(valid) - len(unique),
        "record_counts": {split: len(rows) for split, rows in splits.items()},
        "group_counts": group_counts,
        "source_group_count": len(groups),
        "effective_group_count": len(components),
        "split_effective_group_counts": component_counts,
        "normalization": "NFKC+whitespace",
        "semantic_deduplication": False,
    }
    return {"status": "accepted", "diagnostics": [],
            "splits": splits, "manifest": manifest}


def _finite_number(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def evaluation_gate(baseline: dict, candidate: dict,
                    min_improvement: float = 0.0) -> dict:
    """Compara resultados informados sobre o mesmo conjunto congelado.

    Um retorno accepted significa que os números/identidades informados
    passaram este gate. Não comprova execução real, validade da métrica,
    significância estatística ou superioridade externa do modelo. A comparação
    ao limiar admite erro relativo de ponto flutuante de 1e-12, sem tolerância
    absoluta; a exigência de melhoria estritamente positiva permanece exata.
    """
    report = {"status": "blocked", "diagnostics": [],
              "verification_scope": "reported_results_only"}

    def block(code: str) -> dict:
        report["diagnostics"].append(_diagnostic(code))
        return report

    if not _finite_number(min_improvement) or min_improvement < 0:
        return block("invalid_improvement_threshold")
    required = ("dataset_sha256", "metric", "direction", "sample_count", "value")
    for data in (baseline, candidate):
        if not isinstance(data, dict) or any(field not in data for field in required):
            return block("incomplete_evaluation")
        if not _valid_hash(data["dataset_sha256"]):
            return block("invalid_dataset_hash")
        if not isinstance(data["metric"], str) or not data["metric"].strip():
            return block("invalid_metric")
        if data["direction"] not in ("higher", "lower"):
            return block("invalid_direction")
        if (not isinstance(data["sample_count"], int)
                or isinstance(data["sample_count"], bool) or data["sample_count"] <= 0):
            return block("invalid_sample_count")
        if not _finite_number(data["value"]):
            return block("invalid_metric_value")
        if "benchmark_ids_sha256" in data and not _valid_hash(data["benchmark_ids_sha256"]):
            return block("invalid_benchmark_hash")

    if baseline["dataset_sha256"].lower() != candidate["dataset_sha256"].lower():
        return block("dataset_mismatch")
    if any(baseline[field] != candidate[field] for field in ("metric", "direction", "sample_count")):
        return block("evaluation_protocol_mismatch")
    if "benchmark_ids_sha256" in baseline or "benchmark_ids_sha256" in candidate:
        if not all("benchmark_ids_sha256" in data for data in (baseline, candidate)):
            return block("incomplete_benchmark_identity")
        if baseline["benchmark_ids_sha256"].lower() != candidate["benchmark_ids_sha256"].lower():
            return block("benchmark_identity_mismatch")

    improvement = candidate["value"] - baseline["value"]
    if baseline["direction"] == "lower":
        improvement = -improvement
    if not _finite_number(improvement):
        return block("invalid_improvement_value")
    report.update({"dataset_sha256": baseline["dataset_sha256"].lower(),
                   "sample_count": baseline["sample_count"],
                   "baseline_value": baseline["value"],
                   "candidate_value": candidate["value"],
                   "improvement": improvement, "min_improvement": min_improvement})
    below_threshold = (improvement < min_improvement
                       and not math.isclose(improvement, min_improvement,
                                            rel_tol=1e-12, abs_tol=0.0))
    if improvement <= 0 or below_threshold:
        return block("insufficient_improvement")
    report["status"] = "accepted"
    return report
