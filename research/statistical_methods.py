"""Métodos estatísticos delimitados do R663; nenhuma execução de código recebido."""
from __future__ import annotations

import csv
import math
import random
import statistics
from pathlib import Path
from typing import Any

METHODS = ("descriptive", "pearson", "welch_t")
MAX_CSV_BYTES = 5_000_000
MAX_ROWS = 50_000
SEED = 663
PERMUTATIONS = 999


def validate_configuration(method: str, variables: dict[str, Any]) -> None:
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    if not isinstance(variables, dict):
        raise ValueError("variables must be an object")
    keys = {"value"} if method == "descriptive" else {"x", "y"} if method == "pearson" else {"value", "group", "groups"}
    if set(variables) != keys:
        raise ValueError(f"variables must contain exactly {sorted(keys)}")
    for key in keys - {"groups"}:
        if not isinstance(variables[key], str) or not variables[key].strip() or len(variables[key]) > 128:
            raise ValueError(f"invalid column name: {key}")
    if method == "pearson" and variables["x"] == variables["y"]:
        raise ValueError("pearson requires two distinct columns")
    if method == "welch_t":
        groups = variables["groups"]
        if not isinstance(groups, list) or len(groups) != 2 or any(not isinstance(g, str) or not g or len(g) > 128 for g in groups) or groups[0] == groups[1]:
            raise ValueError("groups must contain two distinct nonempty labels")
        if variables["value"] == variables["group"]:
            raise ValueError("value and group columns must differ")


def _read_rows(dataset_csv: str | Path) -> list[dict[str, str]]:
    path = Path(dataset_csv)
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_CSV_BYTES:
        raise ValueError("CSV missing, empty or exceeds the 5 MB limit")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV requires unique column names")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("CSV row does not match the header")
            rows.append(row)
            if len(rows) > MAX_ROWS:
                raise ValueError("CSV exceeds the 50000 row limit")
    if not rows:
        raise ValueError("CSV contains no observations")
    return rows


def _numbers(rows: list[dict[str, str]], column: str) -> list[float]:
    if column not in rows[0]:
        raise ValueError(f"column absent: {column}")
    try:
        values = [float(row[column]) for row in rows]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"column must contain complete numeric values: {column}") from exc
    if any(not math.isfinite(value) or abs(value) > 1e100 for value in values):
        raise ValueError(f"column contains nonfinite values: {column}")
    return values


def _summary(values: list[float]) -> dict[str, float | int]:
    return {"n": len(values), "mean": statistics.mean(values),
            "standard_deviation": statistics.stdev(values),
            "median": statistics.median(values), "min": min(values), "max": max(values)}


def _correlation(x: list[float], y: list[float]) -> float:
    mx, my = statistics.mean(x), statistics.mean(y)
    covariance = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return covariance / denominator


def execute_analysis(dataset_csv: str | Path, method: str, variables: dict[str, Any]) -> dict[str, Any]:
    """Executa um método prespecificado, sem selecionar resultado por significância."""
    validate_configuration(method, variables)
    rows = _read_rows(dataset_csv)
    from scipy import stats
    result: dict[str, Any] = {
        "method": method, "n": len(rows), "variables": variables,
        "alpha": 0.05, "seed": SEED, "experiment_executed": True,
        "causal_inference": False, "missing_values_policy": "reject",
        "assumptions": ["Observações independentes; esta premissa não é confirmada pelo código.",
                        "A origem e a adequação da amostra dependem da proveniência informada.",
                        "Um único método é executado, sem busca por resultados significativos."],
    }
    if method == "pearson":
        x, y = _numbers(rows, variables["x"]), _numbers(rows, variables["y"])
        if len(x) < 5 or statistics.pstdev(x) == 0 or statistics.pstdev(y) == 0:
            raise ValueError("pearson requires at least five pairs and nonconstant columns")
        correlation = stats.pearsonr(x, y)
        interval = correlation.confidence_interval(confidence_level=0.95)
        generator = random.Random(SEED)
        extreme = 0
        observed = abs(float(correlation.statistic))
        permuted = y.copy()
        for _ in range(PERMUTATIONS):
            generator.shuffle(permuted)
            extreme += abs(_correlation(x, permuted)) >= observed - 1e-12
        result.update({
            "null_hypothesis": "Correlação linear populacional igual a zero.",
            "estimate": float(correlation.statistic), "statistic": float(correlation.statistic),
            "p_value": float(correlation.pvalue), "alternative": "two-sided",
            "confidence_interval_95": [float(interval.low), float(interval.high)],
            "descriptive": {variables["x"]: _summary(x), variables["y"]: _summary(y)},
            "permutation": {"replicates": PERMUTATIONS, "seed": SEED,
                            "p_value": (extreme + 1) / (PERMUTATIONS + 1), "extreme": extreme},
        })
        result["assumptions"].append("O p-valor paramétrico e o intervalo de Fisher pressupõem distribuição bivariada adequada; o teste de permutação pressupõe permutabilidade sob a hipótese nula.")
    elif method == "welch_t":
        column, group_column = variables["value"], variables["group"]
        values = _numbers(rows, column)
        if group_column not in rows[0]:
            raise ValueError(f"column absent: {group_column}")
        groups = variables["groups"]
        if any(row[group_column] not in groups for row in rows):
            raise ValueError("all observations must belong to the two predefined groups")
        grouped = {label: [value for row, value in zip(rows, values) if row[group_column] == label] for label in groups}
        a, b = grouped[groups[0]], grouped[groups[1]]
        if min(len(a), len(b)) < 3:
            raise ValueError("welch_t requires at least three observations per group")
        if statistics.variance(a) + statistics.variance(b) == 0:
            raise ValueError("welch_t requires variation in at least one group")
        test = stats.ttest_ind(a, b, equal_var=False)
        difference = statistics.mean(a) - statistics.mean(b)
        standard_error = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
        margin = float(stats.t.ppf(0.975, test.df)) * standard_error
        result.update({
            "null_hypothesis": "Diferença entre as médias populacionais igual a zero.",
            "estimate": difference, "statistic": float(test.statistic), "p_value": float(test.pvalue),
            "degrees_of_freedom": float(test.df), "alternative": "two-sided",
            "confidence_interval_95": [difference - margin, difference + margin],
            "group_sizes": {label: len(grouped[label]) for label in groups},
            "descriptive": {label: _summary(grouped[label]) for label in groups},
        })
        result["assumptions"].append("Os grupos são independentes; a inferência de Welch exige distribuição aproximadamente normal ou amostras adequadas e não implica equivalência de grupos não aleatorizados.")
    else:
        values = _numbers(rows, variables["value"])
        if len(values) < 3:
            raise ValueError("descriptive requires at least three observations")
        result.update({"null_hypothesis": None, "estimate": statistics.mean(values), "p_value": None,
                       "descriptive": {variables["value"]: _summary(values)}})
    result["limitations"] = ["A análise não estabelece causalidade.",
                            "A revisão computacional não substitui revisão humana por pares.",
                            "Não há certificação externa de originalidade ou generalização."]
    return result
