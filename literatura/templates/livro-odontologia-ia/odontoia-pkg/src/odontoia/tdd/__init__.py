"""
Subpacote 'tdd' — Helpers para Test-Driven Development odontológico.

Fornece ferramentas para criar testes odontológicos, incluindo:
    - Dados de pacientes mockados
    - Radiografias sintéticas
    - Asserções clínicas
    - Decoradores de teste

Componentes:
    test_helpers : Helpers e fixtures para TDD odontológico

Exemplo:
    >>> from odontoia.tdd import create_test_patient, create_test_radiograph
    >>> patient = create_test_patient()
    >>> img = create_test_radiograph()
    >>> assert_clinical_metrics(y_true, y_pred)
"""

from odontoia.tdd.test_helpers import (
    create_test_patient,
    create_test_radiograph,
    assert_clinical_metrics,
    DentalTestData,
    generate_periodontal_dataset,
)

__all__ = [
    "create_test_patient",
    "create_test_radiograph",
    "assert_clinical_metrics",
    "DentalTestData",
    "generate_periodontal_dataset",
]