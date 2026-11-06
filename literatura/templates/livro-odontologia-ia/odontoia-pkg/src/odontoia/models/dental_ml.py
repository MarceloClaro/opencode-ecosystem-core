"""
Módulo dental_ml — Aprendizado de máquina clássico para periodontia.

Implementa modelos baseados em parâmetros clínicos tabulares para:
    - Classificação de estágio de periodontite
    - Importância de características clínicas
    - Predição de risco periodontal

Funções:
    train_periodontal_classifier    : Treina classificador para periodontite
    periodontal_feature_importance  : Importância das features clínicas
    predict_periodontal_staging       : Predição de estágio
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# =============================================================================
# Dados clínicos sintéticos de periodontia (para demonstração)
# =============================================================================

# Nomes das características clínicas usadas na classificação periodontal
PERIODONTAL_FEATURES: List[str] = [
    "profundidade_sondagem_mm",      # Profundidade de sondagem (mm)
    "nivel_insercao_clinica_mm",      # Nível de inserção clínica (mm)
    "sangramento_sondagem",          # Sangramento à sondagem (0/1)
    "perda_ossea_radiografica_pct",  # Perda óssea radiográfica (%)
    "mobilidade_dental",              # Mobilidade dental (0-3)
    "placa_visivel",                 # Placa bacteriana visível (0/1)
    "fumante",                       # Tabagismo (0/1)
    "diabetes",                      # Diabetes (0/1)
    "idade",                         # Idade do paciente
    "higiene_oral_indice",           # Índice de higiene oral (0-3)
]

# Mapeamento de estágios periodontais (AAP/EFP 2018)
PERIODONTAL_STAGES: Dict[int, str] = {
    0: "saudavel",
    1: "gengivite",
    2: "periodontite_estagio_I",
    3: "periodontite_estagio_II",
    4: "periodontite_estagio_III",
    5: "periodontite_estagio_IV",
}


def _generate_synthetic_periodontal_data(
    n_samples: int = 500,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray]:
    """Gera dados clínicos tabulares sintéticos para periodontia.

    Args:
        n_samples: Número de pacientes sintéticos
        random_state: Semente aleatória

    Returns:
        Tupla (X, y) com features clínicas e estágios periodontais
    """
    rng = np.random.default_rng(random_state)

    X = np.zeros((n_samples, len(PERIODONTAL_FEATURES)))
    for i in range(n_samples):
        # Simula distribuições realísticas baseadas em literatura clínica
        idade = rng.integers(18, 85)
        fumante = rng.binomial(1, 0.25)
        diabetes = rng.binomial(1, 0.15)

        # Profundidade de sondagem (saudável: 1-3mm, periodontite: 3-12mm)
        if rng.random() < 0.4:
            # Saudável / gengivite
            probing_depth = rng.normal(2.0, 0.8)
            probing_depth = max(1.0, min(3.5, probing_depth))
            cal = rng.normal(1.0, 0.5)
            bleeding = rng.binomial(1, 0.3)
            bone_loss = rng.uniform(0, 10)
            mobility = rng.choice([0, 1], p=[0.8, 0.2])
            stage = 0 if rng.random() < 0.6 else 1
        else:
            # Periodontite
            probing = rng.uniform(3.5, 12.0)
            cal = rng.uniform(2.0, 10.0)
            bleeding = 1
            bone_loss = rng.uniform(10, 60)
            mobility = rng.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1])

            # Determina estágio
            if bone_loss < 15:
                stage = 2
            elif bone_loss < 33:
                stage = 3
            else:
                stage = 4

        plaque = rng.binomial(1, 0.6)
        hygiene = rng.uniform(0, 5)

        X[i] = [
            round(probing, 1),
            round(cal, 1),
            bleeding,
            round(bone_loss, 1),
            mobility,
            plaque,
            fumant,
            diabetes,
            idade,
            round(hygiene, 1),
        ]
        y[i] = stage

    return X.astype(np.float32), y.astype(np.int64)


# =============================================================================
# Funções públicas
# =============================================================================


def train_periodontal_classifier(
    X: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    model_type: str = "random_forest",
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[object, object, dict, np.ndarray, np.ndarray]:
    """Treina um classificador de estágio periodontal.

    Args:
        X: Matriz de features (n_samples, n_features).
           Se None, gera dados sintéticos automaticamente.
        y: Rótulos de estágio (0-5). Se None, gera sintéticos.
        model_type: Tipo de modelo ('random_forest' ou 'logistic')
        test_size: Fração para teste (padrão 0.2)
        random_state: Semente para reprodutibilidade

    Returns:
        Tupla (model, scaler, metrics, X_test, y_test)
        - model: Modelo treinado (RandomForestClassifier ou LogisticRegression)
        - scaler: StandardScaler ajustado aos dados
        - metrics: Dict com acurácia, relatório de classificação e matriz confusão
        - X_test: Features de teste
        - y_test: Rótulos de teste

    Example:
        >>> model, scaler, metrics, X_test, y_test = train_periodontal_classifier()
        >>> print(f"Acurácia: {metrics['accuracy']:.2%}")
    """
    # Gera dados sintéticos se não fornecidos
    if X is None or y is None:
        X, y = _generate_synthetic_periodontal_data(n_samples=500)

    # Divisão treino-teste estratifcada
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    # Padronização
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Treinamento
    if model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=4,
            class_weight="balanced",
            random_state=random_state,
        )
    elif model_type == "logistic":
        model = LogisticRegression(
            multi_class="multinomial",
            max_iter=2000,
            class_weight="balanced",
            random_state=random_state,
        )
    else:
        raise ValueError(f"model_type '{model_type}' não suportado")

    model.fit(X_train_scaled, y_train)

    # Predição e métricas
    y_pred = model.predict(X_test_scaled)
    accuracy = np.mean(y_pred == y_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "accuracy": accuracy,
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y_test, y_pred),
    }

    return model, scaler, metrics, X_test, y_test


def periodontal_feature_importance(
    model: object,
    feature_names: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Retorna a importância das características clínicas no modelo.

    Args:
        model: Modelo treinado (RandomForestClassifier ou LogisticRegression)
        feature_names: Lista de nomes das características

    Returns:
        Dicionário {feature_name: importance_score} ordenado decrescente

    Example:
        >>> model, _, _, _, _ = train_periodontal_classifier()
        >>> importance = periodontal_feature_importance(model)
        >>> for feat, imp in list(importance.items())[:3]:
        ...     print(f"{feat}: {imp:.3f}")
    """
    if feature_names is None:
        feature_names = PERIODONTAL_FEATURES

    if hasattr(model, "feature_importances_"):
        # Random Forest / árvores
        scores = model.feature_importances_
    elif hasattr(model, "coef_"):
        # Regressão Logística: magnitude dos coeficientes
        scores = np.abs(model.coef_).mean(axis=0)
    else:
        raise TypeError(f"Modelo {type(model).__name__} não oferece importâncias")

    if len(scores) != len(feature_names):
        raise ValueError(
            f"Número de scores ({len(scores)}) diferente do número de "
            f"features ({len(feature_names)})"
        )

    # Ordena por importância decrescente
    indices = np.argsort(scores)[::-1]
    return {feature_names[i]: float(scores[i]) for i in indices}


def predict_periodontal_staging(
    model: object,
    scaler: object,
    features: List[float],
) -> Tuple[int, str, Dict[int, float]]:
    """Prediz o estágio periodontal para um paciente.

    Args:
        model: Modelo treinado (sklearn compatível)
        scaler: StandardScaler ajustado
        features: Lista de 10 valores clínicos na ordem:
            [profundidade_sondagem, nivel_insercao, sangramento,
             perda_ossea, mobilidade, placa, fumante, diabetes,
             idade, indice_higiene]

    Returns:
        Tupla (stage_idx, stage_name, confidence_by_stage)

    Example:
        >>> paciente = [4.5, 3.0, 1, 25.0, 1, 1, 0, 0, 45, 3.0]
        >>> stage_idx, stage_name, probs = predict_periodontal_staging(
        ...     model, scaler, paciente
        ... )
        >>> print(f"Diagnóstico: {stage_name}")
    """
    features_array = np.array(features, dtype=np.float32).reshape(1, -1)
    features_scaled = scaler.transform(features_array)

    stage_idx = model.predict(features_scaled)[0]
    stage_name = PERIODONTAL_STAGES.get(int(stage_idx), "desconhecido")

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(features_scaled)[0]
        confidence = {PERIODONTAL_STAGES.get(i, "unknown"): float(p) for i, p in enumerate(probs)}
    else:
        confidence = {stage_name: 1.0}

    return int(stage_idx), stage_name, confidence



def _confusion_matrix(y_true, y_pred):
    """Calcula matriz de confusão manualmente."""
    labels = sorted(set(y_true) | set(y_pred))
    n = len(labels)
    cm = np.zeros((n, n), dtype=np.int64)
    label_to_idx = {l: i for i, l in enumerate(labels)}
    for t, p in zip(y_true, y_pred):
        cm[label_to_idx[t], label_to_idx[p]] += 1
    return cm



def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcula acurácia da classificação."""
    return float(np.mean(y_true == y_pred))


def classification_report(y_true, y_pred, output_dict=False, zero_division=0):
    """Relatório de classificação."""
    from sklearn.metrics import classification_report as sk_report
    return sk_report(y_true, y_pred, output_dict=output_dict, zero_division=zero_division)


confusion_matrix = _confusion_matrix