"""
Módulo test_helpers — Helpers e fixtures para TDD odontológico.

Fornece funções utilitárias para criar testes automatizados de funções
e modelos odontológicos, seguindo o ciclo Red-Green-Refactor.

Funções:
    create_test_patient       : Cria pacientes odontológicos mockados
    create_test_radiograph    : Gera radiografia sintética para testes
    assert_clinical_metrics   : Asserts para métricas clínicas
    generate_periodontal_dataset : Gera dataset periodontal sintético
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


# =============================================================================
# Estruturas de dados de teste
# =============================================================================


@dataclass
class DentalTestData:
    """Conjunto de dados odontológicos para testes.

    Attributes:
        images: Lista de radiografias sintéticas (H, W)
        labels: Lista de rótulos (int)
        masks: Lista de máscaras de segmentação (H, W) (opcional)
        patient_ids: Lista de IDs de paciente (opcional)
        feature_names: Nomes das features (para dados tabulares)
        feature_matrix: Matriz de características tabulares (opcional)
    """

    images: np.ndarray
    labels: np.ndarray
    masks: Optional[np.ndarray] = None
    patient_ids: Optional[List[str]] = None
    feature_names: Optional[List[str]] = None
    feature_matrix: Optional[np.ndarray] = None

    @property
    def n_samples(self) -> int:
        """Número de amostras no dataset de teste."""
        return len(self.labels)

    @property
    def n_classes(self) -> int:
        """Número de classes únicas."""
        return len(np.unique(self.labels))

    @property
    def image_shape(self) -> Tuple[int, int]:
        """Formato das imagens (H, W)."""
        return self.images.shape[1:] if self.images.ndim == 3 else (0, 0)

    def split(self, test_size: float = 0.3, random_state: int = 42):
        """Divide os dados em treino e teste.

        Args:
            test_size: Proporção para teste
            random_state: Semente aleatória

        Returns:
            Tupla (train_data, test_data) como DentalTestData
        """
        n = self.n_samples
        n_test = int(n * test_size)
        rng = np.random.default_rng(random_state)
        indices = rng.permutation(n)
        test_idx = indices[:n_test]
        train_idx = indices[n_test:]

        def _split(arr):
            if arr is None:
                return None
            return arr[train_idx], arr[test_idx]

        train = DentalTestData(
            images=self.images[train_idx],
            labels=self.labels[train_idx],
            masks=_split(self.masks) if self.masks is not None else None,
            patient_ids=[self.patient_ids[i] for i in train_idx] if self.patient_ids else None,
            feature_names=self.feature_names,
            feature_matrix=_split(self.feature_matrix) if self.feature_matrix is not None else None,
        )
        test = DentalTestData(
            images=self.images[test_idx],
            labels=self.labels[test_idx],
            masks=_split(self.masks) if self.masks is not None else None,
            patient_ids=[self.patient_ids[i] for i in test_idx] if self.patient_ids else None,
            feature_names=self.feature_names,
            feature_matrix=_split(self.feature_matrix) if self.feature_matrix is not None else None,
        )
        return train, test


# =============================================================================
# Criadores de dados sintéticos
# =============================================================================


def create_test_patient(
    patient_id: str = "TEST-001",
    idade: int = 35,
    fumante: bool = False,
    diabetes: bool = False,
    periodontal_stage: int = 0,
) -> dict:
    """Cria um paciente odontológico mockado para testes.

    Args:
        patient_id: Identificador único do paciente
        idade: Idade em anos
        fumante: Se o paciente é tabagista
        diabetes: Se o paciente tem diabetes
        periodontal_stage: Estágio periodontal (0-5)

    Returns:
        Dicionário com dados do paciente simulados

    Example:
        >>> patient = create_test_patient("PAC-001", idade=45)
        >>> assert patient['idade'] == 45
        >>> assert patient['periodontal_stage'] == 0
    """
    # Dados sintéticos do paciente
    rng = np.random.default_rng(hash(patient_id) % 2**32)

    return {
        "patient_id": patient_id,
        "idade": idade,
        "fumante": fumante,
        "diabetes": diabetes,
        "periodontal_stage": periodontal_stage,
        "higiene_oral": rng.uniform(0, 5),
        "dentes": [
            {
                "numero": num,
                "saudavel": True,
                "carie": False,
                "profundidade_sondagem": rng.uniform(1.5, 3.5),
                "mobilidade": 0,
                "sangramento": False,
            }
            for num in range(11, 49)
            if num % 10 != 0  # Pula 20, 30, 40
        ],
        "exames": {
            "perda_ossea_pct": rng.uniform(0, 15),
            "indice_placa": rng.uniform(0, 3),
            "ultima_consulta": "2026-01-15",
        },
    }


def create_test_radiograph(
    size: Tuple[int, int] = (256, 256),
    n_classes: int = 3,
    random_state: int = 42,
) -> DentalTestData:
    """Gera um dataset sintético de radiografias odontológicas para testes.

    Cria imagens simulando radiografias com estruturas ovais (dentes)
    e rótulos de classe correspondentes.

    Args:
        size: Dimensões da imagem (altura, largura)
        n_classes: Número de classes para classificação
        random_state: Semente aleatória

    Returns:
        DentalTestData com imagens e rótulos

    Example:
        >>> data = create_test_radiograph((128, 128), n_classes=2)
        >>> data.images.shape
        (32, 128, 128)
        >>> data.labels.shape
        (32,)
    """
    n_samples = 32
    rng = np.random.default_rng(random_state)
    H, W = size

    images = []
    labels = []

    for _ in range(n_samples):
        # Fundo escuro com variação
        img = rng.normal(30, 15, (H, W)).clip(0, 255).astype(np.uint8)

        # Adiciona 2-5 estruturas simulando dentes (elipses claras)
        n_teeth = rng.integers(2, 6)
        for _ in range(n_teeth):
            center = (rng.integers(10, W - 10), rng.integers(10, H - 10))
            axes = (rng.integers(8, 25), rng.integers(5, 15))
            angle = rng.uniform(-30, 30)
            intensity = rng.integers(100, 220)

            # Desenha elipse (dente) usando coordenadas
            mask = np.zeros((H, W), dtype=np.uint8)
            cv2.ellipse(mask, center, axes, angle, 0, 360, 255, -1)
            img = np.where(mask > 0, intensity, img)

        # Adiciona ruído gaussiano leve
        noise = rng.normal(0, 5, (H, W)).clip(-20, 20).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        images.append(img)
        labels.append(rng.integers(0, n_classes))

    return DentalTestData(
        images=np.array(images),
        labels=np.array(labels),
    )


def generate_periodontal_dataset(
    n_samples: int = 100,
    random_state: int = 42,
) -> DentalTestData:
    """Gera um dataset tabular de periodontia para testes de classificação.

    As features incluem: profundidade de sondagem, nível de inserção,
    sangramento, perda óssea, mobilidade e fatores de risco.

    Args:
        n_samples: Número de amostras sintéticas
        random_state: Semente para reprodutibilidade

    Returns:
        DentalTestData com feature_matrix e labels

    Example:
        >>> data = generate_periodontal_dataset(n_samples=50)
        >>> data.feature_matrix.shape
        (50, 10)
    """
    from odontoia.models.dental_ml import _generate_synthetic_periodontal_data as _gen_data

    X, y = _gen_data(n_samples, random_state)

    feature_names = [
        "profundidade_sondagem",
        "nivel_insercao_clinica",
        "sangramento",
        "perda_ossea",
        "mobilidade",
        "placa",
        "fumante",
        "diabetes",
        "idade",
        "higiene",
    ]

    return DentalTestData(
        images=np.zeros((n_samples, 1, 1)),
        labels=y,
        feature_names=feature_names,
        feature_matrix=X,
    )


# =============================================================================
# Asserções clínicas
# =============================================================================


def assert_clinical_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    min_accuracy: float = 0.8,
    min_sensitivity: float = 0.75,
    min_specificity: float = 0.75,
    raise_on_fail: bool = True,
) -> dict:
    """Avalia e verifica se as métricas clínicas atendem aos limiares mínimos.

    Útil em testes automatizados do ciclo TDD (Red-Green-Refactor)
    para validar que o modelo atinge performance clínica aceitável.

    Args:
        y_true: Rótulos verdadeiros (1D)
        y_pred: Predições (1D)
        min_accuracy: Acurácia mínima aceitável (padrão 0.8)
        min_sensitivity: Sensibilidade mínima (padrão 0.75)
        min_specificity: Especificidade mínima (padrão 0.75)
        raise_on_fail: Se True, levanta AssertionError na primeira falha
                       Se False, retorna dicionário com resultados

    Returns:
        Dicionário com métricas calculadas e flag de aprovação

    Raises:
        AssertionError: Se alguma métrica estiver abaixo do limiar
                        e raise_on_fail = True

    Example:
        >>> metrics = assert_clinical_metrics(y_true, y_pred,
        ...     min_accuracy=0.85, raise_on_fail=False)
        >>> if not metrics['approved']:
        ...     print("Modelo reprovado: acurácia muito baixa")
    """
    from odontoia.metrics.classification import (
        accuracy as _accuracy,
        sensitivity as _sensitivity,
        specificity as _specificity,
        precision as _precision,
        f1_score as _f1_score,
    )

    y_t = np.array(y_true)
    y_p = np.array(y_pred)
    unique = np.unique(y_t)

    # Calcula acurácia geral
    acc = float(np.mean(y_p == y_t))

    if len(unique) == 2:
        # Caso binário
        tp = int(np.sum((y_p == 1) & (y_t == 1)))
        tn = int(np.sum((y_p == 0) & (y_t == 0)))
        fp = int(np.sum((y_p == 1) & (y_t == 0)))
        fn = int(np.sum((y_p == 0) & (y_t == 1)))
        sens_metric = _sensitivity(tp, fn)
        spec_metric = _specificity(tn, fp)
        prec = _precision(tp, fp)
        f1 = _f1_score(tp, tn, fp, fn)
    else:
        # Multiclasse: calcula macro médio (one-vs-rest)
        results = []
        for cls in unique:
            yt_bin = (y_t == cls).astype(int)
            yp_bin = (y_p == cls).astype(int)
            tp = int(np.sum((yp_bin == 1) & (yt_bin == 1)))
            tn = int(np.sum((yp_bin == 0) & (yt_bin == 0)))
            fp = int(np.sum((yp_bin == 1) & (yt_bin == 0)))
            fn = int(np.sum((yp_bin == 0) & (yt_bin == 1)))
            results.append({
                "sens": _sensitivity(tp, fn),
                "esp": _specificity(tn, fp),
                "prec": _precision(tp, fp),
                "f1": _f1_score(tp, tn, fp, fn),
            })

        # Média macro
        sens_metric = float(np.mean([r["sens"] for r in results]))
        spec_metric = float(np.mean([r["esp"] for r in results]))
        prec = float(np.mean([r["prec"] for r in results]))
        f1 = float(np.mean([r["f1"] for r in results]))

    # Verifica limiares
    errors = []
    if acc < min_accuracy:
        errors.append(f"Acurácia {acc:.3f} < {min_accuracy}")
    if sens_metric < min_sensitivity:
        errors.append(f"Sensibilidade {sens_metric:.3f} < {min_sensitivity}")
    if spec_metric < min_specificity:
        errors.append(f"Especificidade {spec_metric:.3f} < {min_specificity}")

    result = {
        "accuracy": acc,
        "sensitivity": sens_metric,
        "specificity": spec_metric,
        "precision": prec,
        "f1": f1,
        "approved": len(errors) == 0,
        "errors": errors,
    }

    if raise_on_fail and not result["approved"]:
        raise AssertionError(
            "Métricas clínicas abaixo do limiar:\n  "
            + "\n  ".join(result["errors"])
        )

    return result