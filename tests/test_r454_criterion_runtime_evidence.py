"""Contratos RED da SPEC-935-R454 para evidência SDD por critério."""

from __future__ import annotations

import importlib
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
import yaml

os.environ.setdefault("MCI_STATE_DIR", tempfile.mkdtemp(prefix="mci_test_r454_sdd_"))

from sdd.spec_engine import (
    SpecRegistry,
    SpecVerifier,
    _issue_trusted_test_evidence,
)
from sdd.tdd_runner import TDDRunner

tdd_runner_module = importlib.import_module("sdd.tdd_runner")

REPO_ROOT = Path(__file__).resolve().parent.parent
RELEASE_SPECS = tuple(f"SPEC-935-R{round_id}" for round_id in range(447, 454))


@contextmanager
def _isolated_registry() -> Iterator[SpecRegistry]:
    """Isola o singleton do registro para specs temporárias."""
    registry = SpecRegistry()
    original_specs = dict(registry.specs)
    registry.specs.clear()
    try:
        yield registry
    finally:
        registry.specs.clear()
        registry.specs.update(original_specs)


def _write_spec(
    path: Path,
    spec_id: str,
    *,
    status: str = "red",
    evidence_contract: str = "",
    test_file: str = "tests/test_r454_criterion_runtime_evidence.py",
    criteria: tuple[str, ...] = ("alpha", "beta"),
) -> None:
    items = "\n".join(
        f"- `{criterion_id}` — critério de teste {criterion_id}."
        for criterion_id in criteria
    )
    path.mkdir(parents=True, exist_ok=True)
    path.joinpath(f"{spec_id}.md").write_text(
        f"""---
spec_id: {spec_id}
title: Spec temporária para R454
component: sdd.spec_engine
status: {status}
test_file: {test_file}
{evidence_contract}---

## Critérios de Aceitação Executáveis

{items}
""",
        encoding="utf-8",
    )


def _strict_contract(criteria: dict[str, list[str]]) -> str:
    """Serializa o contrato estrito de teste sem interpolação YAML insegura."""
    serialized = yaml.safe_dump(
        {
            "evidence_contract": {
                "version": 1,
                "mode": "criterion-runtime-v1",
                "criteria": criteria,
            }
        },
        allow_unicode=True,
        sort_keys=False,
    )
    return serialized


def _passing_outcome(_target: str) -> dict[str, object]:
    return {
        "returncode": 0,
        "all_passed": True,
        "summary": "1 passed",
        "passed_count": 1,
        "failed_count": 0,
        "skipped_count": 0,
        "xfailed_count": 0,
        "collected_count": 1,
    }


def _load_strict_spec(
    tmp_path: Path,
    *,
    status: str = "red",
    criteria: dict[str, list[str]] | None = None,
):
    spec_id = "SPEC-TEST-R454-ESTRITA"
    _write_spec(
        tmp_path,
        spec_id,
        status=status,
        evidence_contract=_strict_contract(
            criteria
            or {
                "alpha": [
                    "tests/test_r454_criterion_runtime_evidence.py::test_v1_contract_requires_every_markdown_criterion"
                ],
                "beta": [
                    "tests/test_r454_criterion_runtime_evidence.py::test_v1_rejects_global_evidence_without_criterion_records"
                ],
            }
        ),
    )
    registry = SpecRegistry()
    assert registry.load_formal_specs(str(tmp_path)) == 1
    spec = registry.get(spec_id)
    assert spec is not None
    return registry, spec_id, spec


def test_v1_contract_requires_every_markdown_criterion(tmp_path: Path) -> None:
    """Contrato estrito sem vínculo para um ID Markdown falha fechado."""
    with _isolated_registry() as registry:
        _, spec_id, spec = _load_strict_spec(
            tmp_path,
            criteria={
                "alpha": [
                    "tests/test_r454_criterion_runtime_evidence.py::test_v1_contract_requires_every_markdown_criterion"
                ]
            },
        )

        result = SpecVerifier(registry).verify(spec_id, {"delivery": "presente"})

    assert spec.evidence_contract_mode == "criterion-runtime-v1"
    assert spec.evidence_contract_valid is False
    assert "beta" in spec.evidence_contract_error
    assert result["verified"] is False
    assert result["passed_count"] == 0


def test_v1_rejects_global_evidence_without_criterion_records(
    tmp_path: Path,
) -> None:
    """Uma única suíte verde não é prova coletiva para contrato v1."""
    with _isolated_registry() as registry:
        _, spec_id, spec = _load_strict_spec(tmp_path)
        global_only = _issue_trusted_test_evidence(
            spec_id,
            spec.test_file,
            executed=True,
            passed=True,
            returncode=0,
            summary="2 passed",
            contract_sha256=spec.evidence_contract_sha256,
        )

        result = SpecVerifier(registry).verify(
            spec_id,
            {"delivery": "presente"},
            trusted_test_evidence=global_only,
        )

    assert spec.evidence_contract_valid is True
    assert result["runtime_evidence_valid"] is False
    assert result["verified"] is False
    assert {item["criterion_id"] for item in result["criteria_results"]} == {
        "alpha",
        "beta",
    }
    assert not any(item["passed"] for item in result["criteria_results"])


def test_v1_requires_matching_runtime_bound_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Registros selados precisam coincidir com IDs, alvos e fingerprint v1."""
    with _isolated_registry() as registry:
        _, spec_id, spec = _load_strict_spec(tmp_path)
        monkeypatch.setattr(tdd_runner_module, "run_pytest", _passing_outcome)

        evidence = TDDRunner().run_spec_test(spec)
        result = SpecVerifier(registry).verify(
            spec_id,
            {"delivery": "presente"},
            trusted_test_evidence=evidence,
        )
        replay_with_other_contract = _issue_trusted_test_evidence(
            spec_id,
            spec.test_file,
            executed=True,
            passed=True,
            returncode=0,
            summary="2 passed",
            contract_sha256="0" * 64,
            criterion_records=evidence.criterion_records,
        )
        rejected = SpecVerifier(registry).verify(
            spec_id,
            {"delivery": "presente"},
            trusted_test_evidence=replay_with_other_contract,
        )
        agent_payload = SpecVerifier(registry).verify(
            spec_id,
            {
                "criteria_results": {
                    "alpha": {"passed": True},
                    "beta": {"passed": True},
                }
            },
        )

    assert evidence.to_dict()["scope"] == "local_runtime"
    assert evidence.to_dict()["external_validation"] is False
    assert len(evidence.criterion_records) == 2
    assert result["verified"] is True
    assert rejected["verified"] is False
    assert agent_payload["verified"] is False


def test_v1_rejects_invalid_targets_and_nonpassing_outcomes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Alvos inválidos, skipped e resultados sem coleta não promovem critérios."""
    with _isolated_registry() as registry:
        _, invalid_spec_id, invalid_spec = _load_strict_spec(
            tmp_path,
            criteria={
                "alpha": ["../outside.py::test_escape"],
                "beta": [
                    "tests/test_r454_criterion_runtime_evidence.py::test_v1_rejects_invalid_targets_and_nonpassing_outcomes"
                ],
            },
        )
        invalid_result = SpecVerifier(registry).verify(
            invalid_spec_id, {"delivery": "presente"}
        )
        assert invalid_spec.evidence_contract_valid is False

        registry.specs.clear()
        _, spec_id, spec = _load_strict_spec(tmp_path / "valid")

        def skipped_outcome(_target: str) -> dict[str, object]:
            return {
                "returncode": 0,
                "all_passed": True,
                "summary": "1 passed, 1 skipped",
                "passed_count": 1,
                "failed_count": 0,
                "skipped_count": 1,
                "xfailed_count": 0,
                "collected_count": 2,
            }

        monkeypatch.setattr(tdd_runner_module, "run_pytest", skipped_outcome)
        evidence = TDDRunner().run_spec_test(spec)
        skipped_result = SpecVerifier(registry).verify(
            spec_id,
            {"delivery": "presente"},
            trusted_test_evidence=evidence,
        )

    assert invalid_result["verified"] is False
    assert evidence.passed is False
    assert skipped_result["verified"] is False
    assert skipped_result["passed_count"] == 0


def test_v1_loaded_green_frontmatter_starts_red(tmp_path: Path) -> None:
    """Frontmatter verde não substitui uma execução fresca no modo estrito."""
    with _isolated_registry():
        _, _spec_id, spec = _load_strict_spec(tmp_path, status="green")

    assert spec.declared_status == "green"
    assert spec.status == "red"


def test_legacy_markdown_contracts_remain_compatible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Specs sem contrato v1 mantêm a rota histórica, explicitamente legada."""
    spec_id = "SPEC-TEST-R454-LEGADA"
    with _isolated_registry() as registry:
        _write_spec(tmp_path, spec_id)
        assert registry.load_formal_specs(str(tmp_path)) == 1
        spec = registry.get(spec_id)
        assert spec is not None
        monkeypatch.setattr(tdd_runner_module, "run_pytest", _passing_outcome)
        evidence = TDDRunner().run_spec_test(spec)
        result = SpecVerifier(registry).verify(
            spec_id,
            {"delivery": "presente"},
            trusted_test_evidence=evidence,
        )

    assert spec.evidence_contract_mode == "legacy"
    assert result["verified"] is True
    assert result["status"] == "green"


def test_r447_receipt_and_criteria_are_traceable() -> None:
    """A auditoria R447 fecha com recibo factual, critérios e evolução ligados."""
    spec_path = REPO_ROOT / "specs" / "SPEC-935-R447-auditoria-tecnica-ecossistema.md"
    receipt_path = REPO_ROOT / "VALIDATION_R447.md"
    cycles_path = REPO_ROOT / "evolution" / "cycles.json"

    spec = spec_path.read_text(encoding="utf-8")
    receipt = receipt_path.read_text(encoding="utf-8")
    cycles = cycles_path.read_text(encoding="utf-8")

    for criterion_id in (
        "environment_health_recorded",
        "test_execution_recorded",
        "findings_traceable",
        "domain_reviews_separated",
        "recommendations_conservative",
        "read_only_scope_recorded",
    ):
        assert f"`{criterion_id}`" in spec
    for marker in (
        "## Ambiente registrado",
        "## Comandos executados",
        "## Achados",
        "## Revisões por domínio",
        "## Limites conhecidos",
        "somente leitura",
        "certificação externa",
    ):
        assert marker in receipt
    assert "status: green" in spec
    assert "VALIDATION_R447.md" in spec
    assert "VALIDATION_R447.md" in cycles


def test_release_specs_use_criterion_runtime_v1() -> None:
    """Todas as specs que sustentam o lote usam mapa explícito por critério."""
    registry = SpecRegistry()
    for spec_id in RELEASE_SPECS:
        spec = registry.get(spec_id)
        assert spec is not None
        assert spec.evidence_contract_mode == "criterion-runtime-v1"
        assert spec.evidence_contract_valid is True
        assert set(spec.criterion_test_targets) == {
            criterion.criterion_id for criterion in spec.criteria
        }
        assert all(spec.criterion_test_targets[criterion_id] for criterion_id in spec.criterion_test_targets)


def test_runtime_evidence_is_locally_scoped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A projeção auditável delimita o resultado ao runtime local, não externo."""
    with _isolated_registry() as registry:
        _, spec_id, spec = _load_strict_spec(tmp_path)
        monkeypatch.setattr(tdd_runner_module, "run_pytest", _passing_outcome)
        evidence = TDDRunner().run_spec_test(spec)
        result = SpecVerifier(registry).verify(
            spec_id,
            {"delivery": "presente"},
            trusted_test_evidence=evidence,
        )

    projection = evidence.to_dict()
    assert result["verified"] is True
    assert projection["scope"] == "local_runtime"
    assert projection["external_validation"] is False
    assert "certificação externa" in (
        REPO_ROOT / "specs" / "SPEC-935-R454-criterion-runtime-evidence.md"
    ).read_text(encoding="utf-8")
