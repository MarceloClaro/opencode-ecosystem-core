"""R1142–R1145 — classificação quântica com baseline clássico e auditoria.

Pipeline auditável:

- dataset sintético de círculos concêntricos;
- feature maps ZZ/Pauli/angle/reupload, com escala e repetições;
- kernel quântico por fidelidade;
- kernel ridge clássico;
- baseline RBF clássico;
- split treino/validação/teste sem vazamento (seleção na validação);
- bootstrap sobre a matriz de confusão;
- curva de aprendizado e comparação descritiva com Caro 2022;
- kernel estimado por shots com ruído de leitura simulado.

Não executa hardware e não declara vantagem quântica. O objetivo é medir
gaps de generalização, escolha de feature map, custo de kernel e concorrência
clássica, conforme Havlíček 2019, Huang 2021 e Caro 2022.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Pauli, Statevector, partial_trace

LIMITS = (
    "Dataset sintético 2D. Não prova vantagem quântica, generalização em dados "
    "reais ou superioridade sobre kernels clássicos. O kernel quântico é "
    "calculado por statevector; a variante ruidosa simula shots e erro de "
    "leitura, não calibração real."
)
SCALE_LIMITS = (
    "A curva de aprendizado é descritiva: um dataset por seed e um expoente "
    "ajustado não validam nem refutam o limite de Caro 2022."
)
NOISE_LIMITS = (
    "Ruído de leitura modelado de forma independente por qubit; não inclui "
    "crosstalk, drift, decoerência nem calibração do backend. A seleção de "
    "hiperparâmetros usa o kernel exato e é declarada como tal."
)


def make_circles(
    n_per_class: int = 20,
    *,
    noise: float = 0.05,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    if n_per_class < 2:
        raise ValueError("n_per_class deve ser >= 2")
    rng = np.random.default_rng(int(seed))
    angles_inner = rng.uniform(0, 2 * np.pi, n_per_class)
    angles_outer = rng.uniform(0, 2 * np.pi, n_per_class)
    inner = np.column_stack([
        0.45 * np.cos(angles_inner),
        0.45 * np.sin(angles_inner),
    ])
    outer = np.column_stack([
        1.0 * np.cos(angles_outer),
        1.0 * np.sin(angles_outer),
    ])
    inner += rng.normal(0, noise, inner.shape)
    outer += rng.normal(0, noise, outer.shape)
    X = np.vstack([inner, outer])
    y = np.hstack([np.zeros(n_per_class, dtype=int), np.ones(n_per_class, dtype=int)])
    order = rng.permutation(len(y))
    return X[order], y[order]


def split_train_test(
    X: np.ndarray,
    y: np.ndarray,
    *,
    test_fraction: float = 0.5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction deve estar em (0,1)")
    cut = int(round(len(y) * (1 - test_fraction)))
    if cut <= 0 or cut >= len(y):
        raise ValueError("split vazio")
    return X[:cut], y[:cut], X[cut:], y[cut:]


_KINDS = ("zz", "pauli", "angle", "reupload")


def feature_map(
    point: np.ndarray,
    *,
    reps: int = 1,
    kind: str = "zz",
    scale: float = 1.0,
) -> QuantumCircuit:
    if kind not in _KINDS:
        raise ValueError(f"feature map desconhecido: {kind}")
    point = np.asarray(point, dtype=float)
    if point.shape != (2,):
        raise ValueError("ponto deve ter duas coordenadas")
    if scale <= 0:
        raise ValueError("scale deve ser positivo")
    circuit = QuantumCircuit(2)
    for _ in range(int(reps)):
        if kind in ("zz", "pauli"):
            circuit.h(0)
            circuit.h(1)
            circuit.rz(scale * point[0], 0)
            circuit.rz(scale * point[1], 1)
            if kind == "zz":
                circuit.rzz(
                    scale * (np.pi - point[0]) * (np.pi - point[1]),
                    0,
                    1,
                )
            else:
                circuit.rzz(scale * point[0] * point[1], 0, 1)
        elif kind == "angle":
            circuit.ry(scale * point[0], 0)
            circuit.ry(scale * point[1], 1)
            circuit.rzz(scale * point[0] * point[1], 0, 1)
        else:  # reupload
            circuit.ry(scale * point[0], 0)
            circuit.ry(scale * point[1], 1)
            circuit.rz(scale * point[0] * point[1], 0)
            circuit.rzz(scale * point[0] * point[1], 0, 1)
    return circuit


def quantum_kernel_entry(
    left: np.ndarray,
    right: np.ndarray,
    *,
    reps: int = 1,
    kind: str = "zz",
    scale: float = 1.0,
) -> float:
    a = Statevector.from_instruction(
        feature_map(left, reps=reps, kind=kind, scale=scale)
    )
    b = Statevector.from_instruction(
        feature_map(right, reps=reps, kind=kind, scale=scale)
    )
    overlap = np.vdot(a.data, b.data)
    return float(abs(overlap) ** 2)


def kernel_matrix(
    left: np.ndarray,
    right: np.ndarray,
    *,
    reps: int = 1,
    kind: str = "zz",
    scale: float = 1.0,
) -> np.ndarray:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    matrix = np.empty((len(left), len(right)), dtype=float)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            matrix[i, j] = quantum_kernel_entry(
                a, b, reps=reps, kind=kind, scale=scale
            )
    return matrix


def rbf_kernel(
    left: np.ndarray,
    right: np.ndarray,
    *,
    gamma: float = 1.0,
) -> np.ndarray:
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    squared = (
        np.sum(left**2, axis=1)[:, None]
        + np.sum(right**2, axis=1)[None, :]
        - 2 * left @ right.T
    )
    return np.exp(-gamma * np.maximum(squared, 0.0))


def kernel_ridge_predict(
    K_train: np.ndarray,
    y_train: np.ndarray,
    K_test: np.ndarray,
    *,
    ridge: float = 1e-3,
) -> np.ndarray:
    if ridge <= 0:
        raise ValueError("ridge deve ser positivo")
    labels = np.where(np.asarray(y_train) > 0, 1.0, -1.0)
    alpha = np.linalg.solve(K_train + ridge * np.eye(len(K_train)), labels)
    scores = K_test @ alpha
    return (scores >= 0).astype(int)


def confusion(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    if y_true.shape != y_pred.shape:
        raise ValueError("formas diferentes")
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    return float(np.mean(y_true == y_pred))


def leakage_audit(
    X_train: np.ndarray,
    X_test: np.ndarray,
) -> dict:
    train = {tuple(np.round(row, 12)) for row in np.asarray(X_train)}
    test = {tuple(np.round(row, 12)) for row in np.asarray(X_test)}
    return {
        "disjoint": not bool(train & test),
        "train_size": len(train),
        "test_size": len(test),
        "overlap": sorted(train & test)[:5],
    }


def bootstrap_accuracy_ci(
    confusion_counts: dict,
    *,
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> dict:
    """IC percentil da acurácia, reamostrando a matriz de confusão.

    A acurácia depende apenas de tp/tn/fp/fn; reamostrar as quatro células com
    reposição é equivalente a reamostrar observações individuais.
    """
    if not 0 < confidence < 1:
        raise ValueError("confidence deve estar em (0,1)")
    if int(n_boot) < 100:
        raise ValueError("n_boot deve ser >= 100")
    try:
        counts = np.array(
            [
                int(confusion_counts["tp"]),
                int(confusion_counts["tn"]),
                int(confusion_counts["fp"]),
                int(confusion_counts["fn"]),
            ],
            dtype=int,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("matriz de confusão inválida") from exc
    if np.any(counts < 0):
        raise ValueError("contagens não podem ser negativas")
    total = int(counts.sum())
    if total == 0:
        raise ValueError("matriz de confusão vazia")
    rng = np.random.default_rng(int(seed))
    draws = rng.multinomial(total, counts / total, size=int(n_boot))
    accuracies = (draws[:, 0] + draws[:, 1]) / total
    tail = (1.0 - float(confidence)) / 2.0
    low, high = np.percentile(accuracies, [100 * tail, 100 * (1 - tail)])
    return {
        "accuracy": float((counts[0] + counts[1]) / total),
        "ci_low": float(low),
        "ci_high": float(high),
        "confidence": float(confidence),
        "n_boot": int(n_boot),
        "n_test": total,
        "method": "percentil bootstrap sobre a matriz de confusão",
    }


def _split_three(X, y):
    n = len(y)
    first = int(round(0.6 * n))
    second = int(round(0.8 * n))
    if first <= 0 or second <= first or second >= n:
        raise ValueError("amostra pequena para treino/validação/teste")
    return X[:first], y[:first], X[first:second], y[first:second], X[second:], y[second:]


def _states(points, *, kind, reps, scale):
    return np.vstack([
        Statevector.from_instruction(
            feature_map(point, kind=kind, reps=reps, scale=scale)
        ).data
        for point in np.asarray(points, dtype=float)
    ])


def _kernel_from_states(left_states, right_states):
    overlaps = np.conj(np.asarray(left_states)) @ np.asarray(right_states).T
    return np.abs(overlaps) ** 2


_PAULI = {
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex),
    "Y": np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex),
}
_IDENTITY = np.eye(2, dtype=complex)


def _projected(states):
    """Expectativas de Pauli por qubit (Huang 2021), qubit 0 = LSB."""
    psi = np.asarray(states)
    features = []
    for qubit in (0, 1):
        for label in ("X", "Y", "Z"):
            if qubit == 0:
                operator = np.kron(_IDENTITY, _PAULI[label])
            else:
                operator = np.kron(_PAULI[label], _IDENTITY)
            values = np.einsum("ia,ab,ib->i", psi.conj(), operator, psi)
            features.append(np.real(values))
    return np.column_stack(features)


def _search_classical(X_train, y_train, X_val, y_val, X_test, y_test):
    best = None
    for gamma in (0.5, 1.0, 2.0):
        for ridge in (1e-2, 1e-1):
            K_train = rbf_kernel(X_train, X_train, gamma=gamma)
            K_val = rbf_kernel(X_val, X_train, gamma=gamma)
            K_test = rbf_kernel(X_test, X_train, gamma=gamma)
            pred_val = kernel_ridge_predict(K_train, y_train, K_val, ridge=ridge)
            pred_test = kernel_ridge_predict(K_train, y_train, K_test, ridge=ridge)
            row = {
                "gamma": gamma,
                "ridge": ridge,
                "validation_accuracy": accuracy(y_val, pred_val),
                "test_accuracy": accuracy(y_test, pred_test),
                "validation_confusion": confusion(y_val, pred_val),
                "test_confusion": confusion(y_test, pred_test),
            }
            if best is None or row["validation_accuracy"] > best["validation_accuracy"]:
                best = row
    return best


def _search_quantum(
    X_train,
    y_train,
    X_val,
    y_val,
    X_test,
    y_test,
    *,
    kinds=("zz", "angle", "reupload"),
    reps_grid=(1, 2),
    scales=(0.5, 1.0, 1.5),
    ridges=(1e-2, 1e-1),
    gammas=(0.5, 1.0),
):
    points = np.vstack([X_train, X_val, X_test])
    n_train = len(X_train)
    n_val = len(X_val)
    best_quantum = None
    best_projected = None
    evaluated = 0
    for kind in kinds:
        for reps in reps_grid:
            for scale in scales:
                states = _states(points, kind=kind, reps=reps, scale=scale)
                train_states = states[:n_train]
                val_states = states[n_train:n_train + n_val]
                test_states = states[n_train + n_val:]
                K_train = _kernel_from_states(train_states, train_states)
                K_val = _kernel_from_states(val_states, train_states)
                K_test = _kernel_from_states(test_states, train_states)
                features = _projected(states)
                train_features = features[:n_train]
                val_features = features[n_train:n_train + n_val]
                test_features = features[n_train + n_val:]
                projected_matrices = {
                    gamma: (
                        rbf_kernel(train_features, train_features, gamma=gamma),
                        rbf_kernel(val_features, train_features, gamma=gamma),
                        rbf_kernel(test_features, train_features, gamma=gamma),
                    )
                    for gamma in gammas
                }
                for ridge in ridges:
                    evaluated += 1
                    pred_val = kernel_ridge_predict(K_train, y_train, K_val, ridge=ridge)
                    pred_test = kernel_ridge_predict(K_train, y_train, K_test, ridge=ridge)
                    row = {
                        "kind": kind,
                        "reps": reps,
                        "scale": scale,
                        "ridge": ridge,
                        "validation_accuracy": accuracy(y_val, pred_val),
                        "test_accuracy": accuracy(y_test, pred_test),
                        "validation_confusion": confusion(y_val, pred_val),
                        "test_confusion": confusion(y_test, pred_test),
                    }
                    if (
                        best_quantum is None
                        or row["validation_accuracy"] > best_quantum["validation_accuracy"]
                    ):
                        best_quantum = row
                    for gamma in gammas:
                        evaluated += 1
                        P_train, P_val, P_test = projected_matrices[gamma]
                        pred_val_p = kernel_ridge_predict(
                            P_train, y_train, P_val, ridge=ridge
                        )
                        pred_test_p = kernel_ridge_predict(
                            P_train, y_train, P_test, ridge=ridge
                        )
                        row_p = {
                            "kind": kind,
                            "reps": reps,
                            "scale": scale,
                            "ridge": ridge,
                            "gamma": gamma,
                            "validation_accuracy": accuracy(y_val, pred_val_p),
                            "test_accuracy": accuracy(y_test, pred_test_p),
                            "validation_confusion": confusion(y_val, pred_val_p),
                            "test_confusion": confusion(y_test, pred_test_p),
                        }
                        if (
                            best_projected is None
                            or row_p["validation_accuracy"]
                            > best_projected["validation_accuracy"]
                        ):
                            best_projected = row_p
    return best_quantum, best_projected, evaluated


def improved_audit(
    *,
    n_per_class: int = 20,
    seed: int = 42,
    noise: float = 0.05,
) -> dict:
    X, y = make_circles(n_per_class=n_per_class, seed=seed, noise=noise)
    X_train, y_train, X_val, y_val, X_test, y_test = _split_three(X, y)
    leakage = leakage_audit(np.vstack([X_train, X_val]), X_test)
    if not leakage["disjoint"]:
        raise ValueError("vazamento treino/teste")
    classical_best = _search_classical(
        X_train, y_train, X_val, y_val, X_test, y_test
    )
    quantum_best, projected_best, evaluated = _search_quantum(
        X_train, y_train, X_val, y_val, X_test, y_test
    )
    return {
        "schema_version": 1,
        "n_per_class": int(n_per_class),
        "seed": int(seed),
        "noise": float(noise),
        "n_train": len(y_train),
        "n_validation": len(y_val),
        "n_test": len(y_test),
        "configs_evaluated": int(evaluated),
        "quantum": quantum_best,
        "projected": projected_best,
        "classical": classical_best,
        "leakage": leakage,
        "selection": "validação; teste não participa da escolha",
        "sources": {
            "feature_spaces": "10.1038/s41586-019-0980-2",
            "generalization": "10.1038/s41467-022-32550-3",
            "data_power": "10.1038/s41467-021-22539-9",
        },
        "limits": LIMITS,
        "hardware_executed": False,
        "rates_measured": False,
    }


def _ci_for(row, *, n_boot, confidence, seed):
    return bootstrap_accuracy_ci(
        row["test_confusion"],
        n_boot=n_boot,
        confidence=confidence,
        seed=seed,
    )


def benchmark_improved(
    *,
    n_per_class: int = 40,
    noise: float = 0.15,
    seeds=(42, 43, 44),
    bootstrap: int = 2000,
    confidence: float = 0.95,
) -> dict:
    rows = []
    for position, seed in enumerate(seeds):
        payload = improved_audit(
            n_per_class=n_per_class,
            seed=int(seed),
            noise=noise,
        )
        row = {
            "seed": int(seed),
            "quantum": payload["quantum"],
            "projected": payload["projected"],
            "classical": payload["classical"],
        }
        for name in ("quantum", "projected", "classical"):
            row[f"{name}_ci"] = _ci_for(
                payload[name],
                n_boot=bootstrap,
                confidence=confidence,
                seed=1000 + position,
            )
        rows.append(row)
    summary = {}
    for name in ("quantum", "projected", "classical"):
        values = [row[name]["test_accuracy"] for row in rows]
        pooled = {
            key: sum(row[name]["test_confusion"][key] for row in rows)
            for key in ("tp", "tn", "fp", "fn")
        }
        pooled_ci = bootstrap_accuracy_ci(
            pooled,
            n_boot=bootstrap,
            confidence=confidence,
            seed=2000,
        )
        summary[name] = {
            "mean_test_accuracy": float(np.mean(values)),
            "std_test_accuracy": (
                float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            ),
            "values": values,
            "pooled_accuracy": pooled_ci["accuracy"],
            "ci_low": pooled_ci["ci_low"],
            "ci_high": pooled_ci["ci_high"],
            "cis": [row[f"{name}_ci"] for row in rows],
        }
    return {
        "schema_version": 1,
        "n_per_class": int(n_per_class),
        "noise": float(noise),
        "seeds": [int(seed) for seed in seeds],
        "rows": rows,
        "summary": summary,
        "bootstrap": {
            "n_boot": int(bootstrap),
            "confidence": float(confidence),
            "method": "percentil sobre a matriz de confusão; pooled entre seeds",
        },
        "limits": LIMITS,
        "hardware_executed": False,
        "rates_measured": False,
    }


def _fit_power_law(errors, sizes):
    errors = np.asarray(errors, dtype=float)
    sizes = np.asarray(sizes, dtype=float)
    mask = (errors > 0) & (sizes > 0)
    if int(mask.sum()) < 2:
        return None
    slope, intercept = np.polyfit(np.log(sizes[mask]), np.log(errors[mask]), 1)
    predicted = intercept + slope * np.log(sizes[mask])
    observed = np.log(errors[mask])
    residual = float(np.sum((observed - predicted) ** 2))
    total = float(np.sum((observed - np.mean(observed)) ** 2))
    r2 = 1.0 - residual / total if total > 1e-15 else 1.0
    return {
        "a": float(np.exp(intercept)),
        "exponent": float(-slope),
        "r2": float(r2),
        "points_used": int(mask.sum()),
    }


def learning_curve(
    *,
    per_class_sizes=(20, 40, 80, 160),
    seeds=(42, 43, 44),
    noise: float = 0.15,
    bootstrap: int = 2000,
    confidence: float = 0.95,
) -> dict:
    """Curva de aprendizado com seleção em validação e IC bootstrap."""
    sizes = [int(size) for size in per_class_sizes]
    if len(sizes) < 2:
        raise ValueError("per_class_sizes exige ao menos dois tamanhos")
    if any(size < 6 for size in sizes):
        raise ValueError("per_class_sizes mínimo é 6")
    if len(set(sizes)) != len(sizes):
        raise ValueError("per_class_sizes não pode repetir")
    seed_list = [int(seed) for seed in seeds]
    if not seed_list:
        raise ValueError("seeds não pode ser vazio")

    points = []
    accuracy_matrix = {"quantum": [], "projected": [], "classical": []}
    for size in sizes:
        payloads = [
            improved_audit(n_per_class=size, seed=seed, noise=noise)
            for seed in seed_list
        ]
        point = {
            "n_per_class": size,
            "n_train": payloads[0]["n_train"],
            "n_validation": payloads[0]["n_validation"],
            "n_test": payloads[0]["n_test"],
            "leakage": payloads[0]["leakage"],
        }
        for name in ("quantum", "projected", "classical"):
            values = [payload[name]["test_accuracy"] for payload in payloads]
            pooled = {
                key: sum(payload[name]["test_confusion"][key] for payload in payloads)
                for key in ("tp", "tn", "fp", "fn")
            }
            ci = bootstrap_accuracy_ci(
                pooled,
                n_boot=bootstrap,
                confidence=confidence,
                seed=3000 + size,
            )
            point[name] = {
                "mean_test_accuracy": float(np.mean(values)),
                "values": values,
                "pooled_accuracy": ci["accuracy"],
                "ci_low": ci["ci_low"],
                "ci_high": ci["ci_high"],
                "n_test_pooled": ci["n_test"],
            }
            accuracy_matrix[name].append(values)
        points.append(point)

    train_sizes = [point["n_train"] for point in points]
    fits = {}
    for name in ("quantum", "projected", "classical"):
        pooled_errors = [1.0 - point[name]["pooled_accuracy"] for point in points]
        fit = _fit_power_law(pooled_errors, train_sizes)
        fits[name] = fit
        if fit is None:
            continue
        rng = np.random.default_rng(1145)
        exponents = []
        for _ in range(int(bootstrap)):
            resampled_errors = []
            for values in accuracy_matrix[name]:
                draws = rng.integers(0, len(values), size=len(values))
                resampled_errors.append(1.0 - float(np.mean([values[i] for i in draws])))
            resampled_fit = _fit_power_law(resampled_errors, train_sizes)
            if resampled_fit is not None:
                exponents.append(resampled_fit["exponent"])
        if exponents:
            tail = (1.0 - confidence) / 2.0
            low, high = np.percentile(
                exponents, [100 * tail, 100 * (1 - tail)]
            )
            fit["ci_low"] = float(low)
            fit["ci_high"] = float(high)
            fit["valid_resamples"] = len(exponents)
        else:
            fit["ci_low"] = None
            fit["ci_high"] = None
            fit["valid_resamples"] = 0
    return {
        "schema_version": 1,
        "per_class_sizes": sizes,
        "seeds": seed_list,
        "noise": float(noise),
        "points": points,
        "fits": fits,
        "fitted_exponent": fits["quantum"]["exponent"] if fits["quantum"] else None,
        "caro_prediction_exponent": 0.5,
        "interpretation": (
            "Comparação descritiva com o expoente 0,5 de Caro 2022; não valida "
            "nem refuta o limite teórico. Erros zero são censurados no ajuste."
        ),
        "bootstrap": {
            "n_boot": int(bootstrap),
            "confidence": float(confidence),
            "resampling_unit": "seed dentro de cada tamanho",
        },
        "limits": f"{LIMITS} {SCALE_LIMITS}",
        "hardware_executed": False,
        "rates_measured": False,
    }


def _readout_pair(readout_error):
    if isinstance(readout_error, (tuple, list, np.ndarray)):
        if len(readout_error) != 2:
            raise ValueError("readout_error deve ser float ou (e01, e10)")
        e01, e10 = float(readout_error[0]), float(readout_error[1])
    else:
        e01 = e10 = float(readout_error)
    if not (0.0 <= e01 <= 1.0 and 0.0 <= e10 <= 1.0):
        raise ValueError("probabilidades de erro devem estar em [0,1]")
    return e01, e10


def _readout_weights(e01: float, e10: float) -> np.ndarray:
    """P(ler 0 em ambos os qubits | estado base i), qubit 0 = LSB."""
    weights = np.ones(4, dtype=float)
    for index in range(4):
        probability = 1.0
        for qubit in (0, 1):
            bit = (index >> qubit) & 1
            probability *= e10 if bit else (1.0 - e01)
        weights[index] = probability
    return weights


def _feature_operators(points, *, kind, reps, scale):
    return np.asarray([
        Operator(feature_map(point, kind=kind, reps=reps, scale=scale)).data
        for point in np.asarray(points, dtype=float)
    ])


def _all_zero_probabilities(left_states, right_unitaries, e01, e10):
    """P(medir 00) para U(y)† U(x)|0>, com ruído de leitura por qubit."""
    adjoints = np.conj(np.transpose(right_unitaries, (0, 2, 1)))
    amplitudes = np.einsum("jab,ib->ija", adjoints, left_states)
    probabilities = np.abs(amplitudes) ** 2
    weights = _readout_weights(e01, e10)
    return np.clip(np.real(probabilities @ weights), 0.0, 1.0)


def _sample_kernel(probabilities, shots: int, rng):
    return rng.binomial(int(shots), probabilities) / float(shots)


def _noisy_matrices(psi, unitaries, n_train, n_val, e01, e10):
    p_train = _all_zero_probabilities(psi[:n_train], unitaries[:n_train], e01, e10)
    p_val = _all_zero_probabilities(
        psi[n_train:n_train + n_val], unitaries[:n_train], e01, e10
    )
    p_test = _all_zero_probabilities(
        psi[n_train + n_val:], unitaries[:n_train], e01, e10
    )
    return p_train, p_val, p_test


def _evaluate_kernel_matrices(K_train, K_val, K_test, y_train, y_val, y_test, ridge):
    pred_val = kernel_ridge_predict(K_train, y_train, K_val, ridge=ridge)
    pred_test = kernel_ridge_predict(K_train, y_train, K_test, ridge=ridge)
    return {
        "validation_accuracy": accuracy(y_val, pred_val),
        "test_accuracy": accuracy(y_test, pred_test),
        "validation_confusion": confusion(y_val, pred_val),
        "test_confusion": confusion(y_test, pred_test),
    }


def _split_data(n_per_class, seed, noise):
    X, y = make_circles(n_per_class=n_per_class, seed=seed, noise=noise)
    X_train, y_train, X_val, y_val, X_test, y_test = _split_three(X, y)
    leakage = leakage_audit(np.vstack([X_train, X_val]), X_test)
    if not leakage["disjoint"]:
        raise ValueError("vazamento treino/teste")
    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
        "leakage": leakage,
    }


def _entry_for_config(data, config):
    points = np.vstack([data["X_train"], data["X_val"], data["X_test"]])
    n_train = len(data["y_train"])
    n_val = len(data["y_val"])
    feature = {key: config[key] for key in ("kind", "reps", "scale")}
    psi = _states(points, **feature)
    unitaries = _feature_operators(points, **feature)
    return {
        "kind": config["kind"],
        "reps": config["reps"],
        "scale": config["scale"],
        "psi": psi,
        "unitaries": unitaries,
        "K_train": _kernel_from_states(psi[:n_train], psi[:n_train]),
        "K_val": _kernel_from_states(psi[n_train:n_train + n_val], psi[:n_train]),
        "K_test": _kernel_from_states(psi[n_train + n_val:], psi[:n_train]),
    }


def _prepare_seed(n_per_class, seed, noise):
    data = _split_data(n_per_class, seed, noise)
    base = improved_audit(n_per_class=n_per_class, seed=seed, noise=noise)
    config = {
        key: base["quantum"][key] for key in ("kind", "reps", "scale", "ridge")
    }
    entry = _entry_for_config(data, config)
    data.update({
        "config": config,
        "base": base,
        "psi": entry["psi"],
        "unitaries": entry["unitaries"],
    })
    return data


_FEATURE_GRID = tuple(
    (kind, reps, scale)
    for kind in ("zz", "angle", "reupload")
    for reps in (1, 2)
    for scale in (0.5, 1.0, 1.5)
)
_NOISY_RIDGES = (1e-2, 1e-1, 1.0)


def _build_feature_cache(data, *, grid=_FEATURE_GRID):
    points = np.vstack([data["X_train"], data["X_val"], data["X_test"]])
    n_train = len(data["y_train"])
    n_val = len(data["y_val"])
    cache = []
    for kind, reps, scale in grid:
        psi = _states(points, kind=kind, reps=reps, scale=scale)
        cache.append({
            "kind": kind,
            "reps": reps,
            "scale": scale,
            "psi": psi,
            "unitaries": _feature_operators(
                points, kind=kind, reps=reps, scale=scale
            ),
            "K_train": _kernel_from_states(psi[:n_train], psi[:n_train]),
            "K_val": _kernel_from_states(psi[n_train:n_train + n_val], psi[:n_train]),
            "K_test": _kernel_from_states(psi[n_train + n_val:], psi[:n_train]),
        })
    return cache


def _selection_key(row):
    """Pré-registro: validação, depois maior ridge, menor escala, menos reps."""
    return (
        row["validation_accuracy"],
        row["ridge"],
        -row["scale"],
        -row["reps"],
    )


def _noisy_search(cache, data, *, e01, e10, shots, rng, ridges=_NOISY_RIDGES):
    """Seleciona no kernel ruidoso de validação; o teste não participa."""
    n_train = len(data["y_train"])
    n_val = len(data["y_val"])
    best = None
    best_entry = None
    best_matrices = None
    best_key = None
    for entry in cache:
        p_train, p_val, p_test = _noisy_matrices(
            entry["psi"], entry["unitaries"], n_train, n_val, e01, e10
        )
        noisy_train = _sample_kernel(p_train, shots, rng)
        noisy_train = (noisy_train + noisy_train.T) / 2.0
        noisy_val = _sample_kernel(p_val, shots, rng)
        noisy_test = _sample_kernel(p_test, shots, rng)
        for ridge in ridges:
            row = _evaluate_kernel_matrices(
                noisy_train,
                noisy_val,
                noisy_test,
                data["y_train"],
                data["y_val"],
                data["y_test"],
                ridge,
            )
            row.update({
                "kind": entry["kind"],
                "reps": entry["reps"],
                "scale": entry["scale"],
                "ridge": ridge,
            })
            key = _selection_key(row)
            if best is None or key > best_key:
                best = row
                best_entry = entry
                best_matrices = (noisy_train, noisy_val, noisy_test)
                best_key = key
    return best, best_entry, best_matrices


def noisy_kernel_audit(
    *,
    n_per_class: int = 40,
    seed: int = 42,
    noise: float = 0.15,
    shots: int = 4096,
    readout_error=0.02,
    config: dict | None = None,
    selection: str = "noisy",
    bootstrap: int = 2000,
    confidence: float = 0.95,
) -> dict:
    """Avalia o classificador com kernel estimado por shots e leitura ruidosa.

    selection="noisy" (padrão): escolhe hiperparâmetros na validação usando o
    mesmo kernel ruidoso que será usado no teste. selection="exact" congela o
    config escolhido no kernel exato e mede o estresse daí decorrente.
    """
    if int(shots) < 1:
        raise ValueError("shots deve ser >= 1")
    if selection not in ("exact", "noisy"):
        raise ValueError("selection deve ser 'exact' ou 'noisy'")
    e01, e10 = _readout_pair(readout_error)
    data = _split_data(n_per_class, seed, noise)
    n_train = len(data["y_train"])
    n_val = len(data["y_val"])
    rng = np.random.default_rng(
        [int(seed), int(shots), int(round(e01 * 1e6)), int(round(e10 * 1e6))]
    )
    if selection == "exact":
        if config is None:
            base = improved_audit(n_per_class=n_per_class, seed=seed, noise=noise)
            config = {
                key: base["quantum"][key]
                for key in ("kind", "reps", "scale", "ridge")
            }
        else:
            config = {
                key: config[key] for key in ("kind", "reps", "scale", "ridge")
            }
        entry = _entry_for_config(data, config)
        noisy_row = None
        p_train, p_val, p_test = _noisy_matrices(
            entry["psi"], entry["unitaries"], n_train, n_val, e01, e10
        )
        noisy_train = _sample_kernel(p_train, shots, rng)
        noisy_train = (noisy_train + noisy_train.T) / 2.0
        noisy_val = _sample_kernel(p_val, shots, rng)
        noisy_test = _sample_kernel(p_test, shots, rng)
        noisy_row = _evaluate_kernel_matrices(
            noisy_train, noisy_val, noisy_test,
            data["y_train"], data["y_val"], data["y_test"], config["ridge"],
        )
        selection_basis = (
            "kernel exato na validação; ruído aplicado só na avaliação"
        )
        chosen = dict(config)
    else:
        cache = _build_feature_cache(data)
        noisy_row, entry, matrices = _noisy_search(
            cache, data, e01=e01, e10=e10, shots=int(shots), rng=rng
        )
        _, _, noisy_test = matrices
        chosen = {
            key: noisy_row[key] for key in ("kind", "reps", "scale", "ridge")
        }
        selection_basis = "validação com kernel ruidoso; teste ruidoso"
    exact_row = _evaluate_kernel_matrices(
        entry["K_train"], entry["K_val"], entry["K_test"],
        data["y_train"], data["y_val"], data["y_test"], chosen["ridge"],
    )
    ci = bootstrap_accuracy_ci(
        noisy_row["test_confusion"],
        n_boot=bootstrap,
        confidence=confidence,
        seed=7000 + int(seed),
    )
    return {
        "schema_version": 1,
        "n_per_class": int(n_per_class),
        "seed": int(seed),
        "noise": float(noise),
        "n_train": n_train,
        "n_validation": n_val,
        "n_test": len(data["y_test"]),
        "config": chosen,
        "selection": selection,
        "shots": int(shots),
        "readout_model": {
            "symmetric": bool(e01 == e10),
            "e01": e01,
            "e10": e10,
        },
        "mean_abs_kernel_error": float(
            np.mean(np.abs(noisy_test - entry["K_test"]))
        ),
        "exact_test_accuracy": exact_row["test_accuracy"],
        "exact_test_confusion": exact_row["test_confusion"],
        "noisy_test_accuracy": noisy_row["test_accuracy"],
        "noisy_test_confusion": noisy_row["test_confusion"],
        "noisy_validation_accuracy": noisy_row["validation_accuracy"],
        "ci_low": ci["ci_low"],
        "ci_high": ci["ci_high"],
        "ci": ci,
        "selection_basis": selection_basis,
        "leakage": data["leakage"],
        "limits": f"{LIMITS} {NOISE_LIMITS}",
        "hardware_executed": False,
        "rates_measured": False,
    }


def noise_sweep(
    *,
    n_per_class: int = 40,
    seeds=(42, 43, 44),
    noise: float = 0.15,
    shots=(512, 2048, 8192),
    readout_errors=(0.0, 0.02, 0.05),
    bootstrap: int = 1000,
    confidence: float = 0.95,
) -> dict:
    """Varre shots e erro de leitura com seleção no kernel ruidoso."""
    shots_list = [int(value) for value in shots]
    if not shots_list or any(value < 1 for value in shots_list):
        raise ValueError("shots deve conter inteiros >= 1")
    readout_list = [_readout_pair(value) for value in readout_errors]
    if not readout_list:
        raise ValueError("readout_errors não pode ser vazio")
    rows = []
    for seed in [int(value) for value in seeds]:
        data = _split_data(n_per_class, seed, noise)
        cache = _build_feature_cache(data)
        for e01, e10 in readout_list:
            for count in shots_list:
                rng = np.random.default_rng(
                    [int(seed), count, int(round(e01 * 1e6)), int(round(e10 * 1e6))]
                )
                row, entry, matrices = _noisy_search(
                    cache, data, e01=e01, e10=e10, shots=count, rng=rng
                )
                exact_row = _evaluate_kernel_matrices(
                    entry["K_train"], entry["K_val"], entry["K_test"],
                    data["y_train"], data["y_val"], data["y_test"], row["ridge"],
                )
                ci = bootstrap_accuracy_ci(
                    row["test_confusion"],
                    n_boot=bootstrap,
                    confidence=confidence,
                    seed=8000 + int(seed) + count,
                )
                rows.append({
                    "seed": int(seed),
                    "shots": count,
                    "readout_model": {
                        "symmetric": bool(e01 == e10),
                        "e01": e01,
                        "e10": e10,
                    },
                    "config": {
                        key: row[key] for key in ("kind", "reps", "scale", "ridge")
                    },
                    "noisy_test_accuracy": row["test_accuracy"],
                    "noisy_test_confusion": row["test_confusion"],
                    "exact_test_accuracy": exact_row["test_accuracy"],
                    "mean_abs_kernel_error": float(
                        np.mean(np.abs(matrices[2] - entry["K_test"]))
                    ),
                    "ci_low": ci["ci_low"],
                    "ci_high": ci["ci_high"],
                })
    grouped = {}
    for row in rows:
        key = (row["shots"], row["readout_model"]["e01"], row["readout_model"]["e10"])
        grouped.setdefault(key, []).append(row)
    summary = []
    for key, values in sorted(grouped.items()):
        noisy = [row["noisy_test_accuracy"] for row in values]
        exact = [row["exact_test_accuracy"] for row in values]
        summary.append({
            "shots": key[0],
            "readout_error": key[1] if key[1] == key[2] else [key[1], key[2]],
            "mean_noisy_test_accuracy": float(np.mean(noisy)),
            "std_noisy_test_accuracy": (
                float(np.std(noisy, ddof=1)) if len(noisy) > 1 else 0.0
            ),
            "mean_exact_test_accuracy": float(np.mean(exact)),
            "mean_kernel_error": float(np.mean([
                row["mean_abs_kernel_error"] for row in values
            ])),
            "n": len(values),
        })
    return {
        "schema_version": 1,
        "n_per_class": int(n_per_class),
        "seeds": [int(value) for value in seeds],
        "noise": float(noise),
        "rows": rows,
        "summary": summary,
        "selection_basis": "validação com kernel ruidoso; teste ruidoso",
        "noisy_ridge_grid": list(_NOISY_RIDGES),
        "bootstrap": {
            "n_boot": int(bootstrap),
            "confidence": float(confidence),
        },
        "limits": f"{LIMITS} {NOISE_LIMITS}",
        "hardware_executed": False,
        "rates_measured": False,
    }


def audit(*, n_per_class: int = 20, seed: int = 42) -> dict:
    X, y = make_circles(n_per_class=n_per_class, seed=seed)
    X_train, y_train, X_test, y_test = split_train_test(X, y)
    leakage = leakage_audit(X_train, X_test)
    if not leakage["disjoint"]:
        raise ValueError("vazamento treino/teste")
    K_train_q = kernel_matrix(X_train, X_train)
    K_test_q = kernel_matrix(X_test, X_train)
    pred_q = kernel_ridge_predict(K_train_q, y_train, K_test_q)
    K_train_c = rbf_kernel(X_train, X_train)
    K_test_c = rbf_kernel(X_test, X_train)
    pred_c = kernel_ridge_predict(K_train_c, y_train, K_test_c)
    return {
        "schema_version": 1,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "quantum_accuracy": accuracy(y_test, pred_q),
        "classical_accuracy": accuracy(y_test, pred_c),
        "quantum_confusion": confusion(y_test, pred_q),
        "classical_confusion": confusion(y_test, pred_c),
        "leakage": leakage,
        "sources": {
            "feature_spaces": "10.1038/s41586-019-0980-2",
            "generalization": "10.1038/s41467-022-32550-3",
            "data_power": "10.1038/s41467-021-22539-9",
        },
        "limits": LIMITS,
        "hardware_executed": False,
        "rates_measured": False,
    }
