"""Contratos de rastreabilidade e fechamento da SPEC-935-R447."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = REPO_ROOT / "specs" / "SPEC-935-R447-auditoria-tecnica-ecossistema.md"
RECEIPT_PATH = REPO_ROOT / "VALIDATION_R447.md"
CYCLES_PATH = REPO_ROOT / "evolution" / "cycles.json"


def _spec() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def _receipt() -> str:
    return RECEIPT_PATH.read_text(encoding="utf-8")


def _cycles() -> str:
    return CYCLES_PATH.read_text(encoding="utf-8")


def test_r447_receipt_records_doctor_environment_and_scope() -> None:
    """A auditoria registra ambiente, doctor e escopo somente leitura."""
    spec = _spec()
    receipt = _receipt()

    assert "spec_id: SPEC-935-R447" in spec
    assert "test_file: tests/test_r447_auditoria_tecnica_ecossistema.py" in spec
    assert "`environment_health_recorded`" in spec
    assert "VALIDATION_R447.md" in spec
    assert "## Ambiente registrado" in receipt
    assert "python3 -m marceloclaro.cli doctor" in receipt
    assert "18 checks aprovados" in receipt
    assert "somente de leitura" in receipt.lower()


def test_r447_receipt_records_test_collection_and_execution_or_impediment() -> None:
    """A coleta e a execução integral são registradas sem inventar sucesso."""
    receipt = _receipt().lower()

    assert "pytest --collect-only -q" in receipt
    assert "pytest -q" in receipt
    assert (
        "não reconstitui o stdout original" in receipt
        or "não foi preservada" in receipt
        or "impedimento" in receipt
    )
    assert "validation_r448.md" in receipt
    assert "validation_r452.md" in receipt
    assert "validation_r453.md" in receipt


def test_r447_receipt_lists_traceable_findings_with_severity() -> None:
    """Os achados mantêm severidade, evidência rastreável e recomendação."""
    receipt = _receipt()

    assert "## Achados" in receipt
    for marker in (
        "R447-A1",
        "R447-A2",
        "R447-A3",
        "R447-A4",
        "Severidade",
        "Evidência rastreável",
        "Recomendação",
    ):
        assert marker in receipt


def test_r447_receipt_separates_domain_reviews() -> None:
    """Arquitetura, qualidade, segurança e documentação aparecem em seções próprias."""
    receipt = _receipt()

    for heading in (
        "### Arquitetura",
        "### Qualidade e testes",
        "### Segurança",
        "### Documentação",
    ):
        assert heading in receipt


def test_r447_receipt_prioritizes_conservative_recommendations_and_limits() -> None:
    """A síntese final mantém priorização e anti-overclaim explícitos."""
    receipt = _receipt().lower()

    assert "## recomendações priorizadas" in receipt
    assert "alta prioridade" in receipt
    assert "certificação externa" in receipt
    assert "super-humana" in receipt
    assert "## limites conhecidos" in receipt


def test_r447_spec_and_cycle_preserve_read_only_scope() -> None:
    """Spec e ciclo de evolução deixam claro o caráter somente leitura."""
    spec = _spec().lower()
    cycles = _cycles()

    assert "`read_only_scope_recorded`" in spec
    assert "nenhuma alteração funcional" in spec
    assert '"round_id": "R447"' in cycles
    assert "VALIDATION_R447.md" in cycles
    assert "somente leitura" in cycles.lower()
