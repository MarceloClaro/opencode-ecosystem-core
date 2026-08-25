# -*- coding: utf-8 -*-
"""Contratos RED do domínio SDD da SPEC-935-R448.

Os testes usam specs temporárias para tornar explícito o contrato de parsing e
de evidência, sem depender da ordem de carregamento do registro global.
"""

from __future__ import annotations

import importlib
import inspect
import os
import tempfile
from collections.abc import Iterator
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path

import pytest

# O registro publica eventos no MetaBus durante o carregamento das specs.
os.environ.setdefault("MCI_STATE_DIR", tempfile.mkdtemp(prefix="mci_test_r448_sdd_"))

import marceloclaro.orchestrator as orchestrator_module
from marceloclaro.orchestrator import MarceloClaroOrchestrator
from sdd.spec_engine import SpecRegistry, SpecVerifier
from sdd.tdd_runner import TDDRunner

tdd_runner_module = importlib.import_module("sdd.tdd_runner")


@contextmanager
def _isolated_registry() -> Iterator[SpecRegistry]:
    """Isola o singleton do registro enquanto uma spec temporária é carregada."""
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
    body: str,
    test_file: str = "tests/test_r448_sdd_contracts.py",
) -> None:
    path.joinpath(f"{spec_id}.md").write_text(
        f"""---
spec_id: {spec_id}
title: Spec temporária para contratos SDD
component: sdd.spec_engine
status: red
test_file: {test_file}
---

{body}
""",
        encoding="utf-8",
    )


@pytest.fixture
def executable_spec(tmp_path: Path) -> Iterator[tuple[SpecRegistry, str]]:
    spec_id = "SPEC-TEST-EXECUTAVEL"
    _write_spec(
        tmp_path,
        spec_id,
        """## 3. Critérios de Aceitação Executáveis

- `proof_is_sound` — a prova possui uma evidência verificável.
  O identificador deve permanecer estável entre carregamentos.
- `manifest_is_pinned` — o manifesto informa versões exatas.

## 4. Fora de escopo

- `must_not_be_loaded` — este item pertence a outra seção.
""",
    )
    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        yield registry, spec_id


def test_registry_extracts_backticked_ids_from_executable_markdown_items(
    executable_spec: tuple[SpecRegistry, str],
) -> None:
    """Itens sob a seção executável viram contratos com IDs estáveis."""
    registry, spec_id = executable_spec

    spec = registry.get(spec_id)

    assert spec is not None
    assert [criterion.criterion_id for criterion in spec.criteria] == [
        "proof_is_sound",
        "manifest_is_pinned",
    ]
    assert spec.criteria[0].description == (
        "a prova possui uma evidência verificável. "
        "O identificador deve permanecer estável entre carregamentos."
    )


@pytest.mark.parametrize(
    "output",
    [
        None,
        {},
        {"status": "completed", "detail": "Entrega sem evidência por critério."},
        {
            "evidence": {
                "proof_is_sound": {
                    "passed": True,
                    "detail": "Teste de prova executado.",
                }
            }
        },
    ],
    ids=["ausente", "vazio", "sem-ids", "parcial"],
)
def test_verifier_fails_closed_for_absent_or_partial_structured_evidence(
    executable_spec: tuple[SpecRegistry, str], output: object
) -> None:
    """Ausência ou cobertura parcial de evidências não pode promover sucesso."""
    registry, spec_id = executable_spec

    result = SpecVerifier(registry).verify(
        spec_id,
        output,
        trusted_test_evidence={
            "spec_id": spec_id,
            "test_file": "tests/test_r448_sdd_contracts.py",
            "passed": True,
            "returncode": 0,
        },
    )

    assert result["verified"] is False
    assert result["status"] == "red"
    assert result["total_count"] == 2
    assert result["passed_count"] < result["total_count"]


def test_verifier_rejects_agent_claim_without_runtime_test_evidence(
    executable_spec: tuple[SpecRegistry, str],
) -> None:
    """Um dicionário autoatestado não é evidência confiável de uma spec Markdown."""
    registry, spec_id = executable_spec
    output = {
        "evidence": {
            "proof_is_sound": {
                "passed": True,
                "detail": "Contramodelos foram rejeitados pela suíte dirigida.",
            },
            "manifest_is_pinned": {
                "passed": True,
                "detail": "Todos os requisitos declarados usam versões exatas.",
            },
        }
    }

    result = SpecVerifier(registry).verify(spec_id, output)

    assert result["verified"] is False
    assert result["status"] == "red"
    assert result["passed_count"] == 0


def test_runtime_issued_evidence_for_the_spec_test_file_can_verify_markdown_contracts(
    executable_spec: tuple[SpecRegistry, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Somente o runner produz a evidência aceita após executar o test_file vinculado."""
    registry, spec_id = executable_spec
    spec = registry.get(spec_id)
    assert spec is not None
    invoked_paths: list[str] = []

    def passing_pytest(test_path: str) -> dict[str, object]:
        invoked_paths.append(test_path)
        return {"returncode": 0, "all_passed": True, "summary": "2 passed"}

    monkeypatch.setattr(tdd_runner_module, "run_pytest", passing_pytest)
    evidence = TDDRunner().run_spec_test(spec)
    result = SpecVerifier(registry).verify(
        spec_id,
        {"evidence": {"proof_is_sound": {"passed": True}}},
        trusted_test_evidence=evidence,
    )

    assert invoked_paths == ["tests/test_r448_sdd_contracts.py"]
    assert evidence.passed is True
    with pytest.raises(AttributeError):
        evidence.passed = False
    assert result["verified"] is True
    assert result["status"] == "green"
    assert result["passed_count"] == result["total_count"] == 2


@pytest.mark.parametrize(
    "outcome",
    [
        {"returncode": 1, "all_passed": False, "summary": "1 failed"},
        {"returncode": 0, "all_passed": False, "summary": "resultado inconsistente"},
        {"returncode": None, "all_passed": False, "summary": "timeout"},
    ],
    ids=["pytest-failed", "inconsistent-success-flag", "no-returncode"],
)
def test_failed_test_execution_cannot_issue_green_evidence(
    executable_spec: tuple[SpecRegistry, str],
    monkeypatch: pytest.MonkeyPatch,
    outcome: dict[str, object],
) -> None:
    """Resultado não verde do executor permanece fechado, mesmo com payload positivo."""
    registry, spec_id = executable_spec
    spec = registry.get(spec_id)
    assert spec is not None
    monkeypatch.setattr(tdd_runner_module, "run_pytest", lambda _path: outcome)

    evidence = TDDRunner().run_spec_test(spec)
    result = SpecVerifier(registry).verify(
        spec_id,
        {"evidence": {"proof_is_sound": {"passed": True}}},
        trusted_test_evidence=evidence,
    )

    assert evidence.passed is False
    assert result["verified"] is False
    assert result["status"] == "red"


def test_runtime_evidence_is_bound_to_its_originating_spec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Uma execução verde de outra spec não pode ser reutilizada como prova."""
    first_spec_id = "SPEC-TEST-ORIGEM-A"
    second_spec_id = "SPEC-TEST-ORIGEM-B"
    body = """## Critérios de Aceitação Executáveis

- `runtime_bound` — a prova pertence à spec que solicitou o teste.
"""
    _write_spec(tmp_path, first_spec_id, body)
    _write_spec(tmp_path, second_spec_id, body)
    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 2
        first_spec = registry.get(first_spec_id)
        assert first_spec is not None
        monkeypatch.setattr(
            tdd_runner_module,
            "run_pytest",
            lambda _path: {"returncode": 0, "all_passed": True, "summary": "1 passed"},
        )
        evidence = TDDRunner().run_spec_test(first_spec)
        result = SpecVerifier(registry).verify(
            second_spec_id,
            {"evidence": {"runtime_bound": {"passed": True}}},
            trusted_test_evidence=evidence,
        )

    assert evidence.passed is True
    assert result["verified"] is False
    assert result["runtime_evidence_valid"] is False


def test_absent_test_file_cannot_issue_green_evidence(tmp_path: Path) -> None:
    """A ausência do test_file declarado não pode ser contornada por autoatestado."""
    spec_id = "SPEC-TEST-SEM-TESTE"
    _write_spec(
        tmp_path,
        spec_id,
        """## Critérios de Aceitação Executáveis

- `requires_real_test` — o contrato depende de uma execução real.
""",
        test_file="tests/nao-existe-r448.py",
    )
    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        spec = registry.get(spec_id)
        assert spec is not None

        evidence = TDDRunner().run_spec_test(spec)
        result = SpecVerifier(registry).verify(
            spec_id,
            {"evidence": {"requires_real_test": {"passed": True}}},
            trusted_test_evidence=evidence,
        )

    assert evidence.passed is False
    assert result["verified"] is False
    assert result["status"] == "red"


def test_runtime_can_bind_a_spec_to_a_contained_test_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Uma spec ampla pode exigir a suíte contida no diretório ``tests``."""
    spec_id = "SPEC-TEST-DIRETORIO"
    _write_spec(
        tmp_path,
        spec_id,
        """## Critérios de Aceitação Executáveis

- `full_suite` — todos os testes vinculados devem passar.
""",
        test_file="tests",
    )
    invoked_paths: list[str] = []
    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        spec = registry.get(spec_id)
        assert spec is not None
        monkeypatch.setattr(
            tdd_runner_module,
            "run_pytest",
            lambda path: invoked_paths.append(path)
            or {"returncode": 0, "all_passed": True, "summary": "1 passed"},
        )

        evidence = TDDRunner().run_spec_test(spec)
        result = SpecVerifier(registry).verify(
            spec_id,
            {"evidence": {"full_suite": {"passed": True}}},
            trusted_test_evidence=evidence,
        )

    assert invoked_paths == ["tests"]
    assert evidence.passed is True
    assert result["verified"] is True


def test_test_file_outside_repository_is_rejected_before_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """O runtime não executa caminhos que escapem do checkout da spec."""
    spec_id = "SPEC-TEST-CAMINHO-EXTERNO"
    _write_spec(
        tmp_path,
        spec_id,
        """## Critérios de Aceitação Executáveis

- `contained_test` — o teste deve permanecer dentro do repositório.
""",
        test_file="../outside-r448.py",
    )
    invoked = False

    def unexpected_execution(_path: str) -> dict[str, object]:
        nonlocal invoked
        invoked = True
        return {"returncode": 0, "all_passed": True, "summary": "não deveria executar"}

    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        spec = registry.get(spec_id)
        assert spec is not None
        monkeypatch.setattr(tdd_runner_module, "run_pytest", unexpected_execution)

        evidence = TDDRunner().run_spec_test(spec)
        result = SpecVerifier(registry).verify(
            spec_id,
            {"evidence": {"contained_test": {"passed": True}}},
            trusted_test_evidence=evidence,
        )

    assert invoked is False
    assert evidence.passed is False
    assert evidence.error == "invalid_test_file"
    assert result["verified"] is False


def test_test_runner_exception_cannot_issue_green_evidence(
    executable_spec: tuple[SpecRegistry, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Indisponibilidade do executor também mantém a evidência em vermelho."""
    registry, spec_id = executable_spec
    spec = registry.get(spec_id)
    assert spec is not None

    def unavailable_runner(_path: str) -> dict[str, object]:
        raise RuntimeError("executor indisponível")

    monkeypatch.setattr(tdd_runner_module, "run_pytest", unavailable_runner)
    evidence = TDDRunner().run_spec_test(spec)
    result = SpecVerifier(registry).verify(
        spec_id,
        {"evidence": {"proof_is_sound": {"passed": True}}},
        trusted_test_evidence=evidence,
    )

    assert evidence.executed is False
    assert evidence.passed is False
    assert evidence.error == "test_runner_error"
    assert result["verified"] is False


def test_run_pytest_returns_a_closed_result_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """O adaptador de subprocesso converte timeout em resultado SDD reprovado."""
    def raise_timeout(*_args: object, **_kwargs: object) -> None:
        raise tdd_runner_module.subprocess.TimeoutExpired("pytest", 1)

    monkeypatch.setattr(
        tdd_runner_module.subprocess,
        "run",
        raise_timeout,
    )

    outcome = tdd_runner_module.run_pytest("tests/test_r448_sdd_contracts.py", timeout=1)

    assert outcome["returncode"] is None
    assert outcome["all_passed"] is False
    assert outcome["error"] == "timeout"


def test_full_suite_backed_specs_have_a_realistic_default_timeout() -> None:
    """Uma spec ligada a ``tests`` não pode expirar antes da suíte histórica."""
    timeout = inspect.signature(tdd_runner_module.run_pytest).parameters["timeout"].default

    assert isinstance(timeout, int)
    assert timeout >= 900


def test_orchestrator_rejects_self_attested_markdown_evidence_without_runtime_test(
    executable_spec: tuple[SpecRegistry, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """report_completion não encaminha a alegação do agente como prova do contrato."""
    registry, spec_id = executable_spec
    verifier = SpecVerifier(registry)
    published: list[tuple[str, dict[str, object]]] = []

    monkeypatch.setattr(orchestrator_module, "spec_verifier", verifier)
    monkeypatch.setattr(
        orchestrator_module.tdd_runner,
        "run_spec_test",
        lambda _spec: None,
    )
    monkeypatch.setattr(
        orchestrator_module.metabus,
        "publish",
        lambda topic, payload, source_agent=None: published.append((topic, payload)),
    )
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False, strict_sdd=True)
    task_id = "task-r448-autoatestado"
    orchestrator.task_specs[task_id] = spec_id

    orchestrator.report_completion(
        task_id,
        "agent-test",
        {
            "evidence": {
                "proof_is_sound": {"passed": True},
                "manifest_is_pinned": {"passed": True},
            }
        },
        success=True,
    )

    assert published[-1][0] == "task.complete"
    assert published[-1][1]["status"] == "failed"
    verification = published[-1][1]["sdd_verification"]
    assert isinstance(verification, dict)
    assert verification["verified"] is False
    assert registry.get(spec_id).status == "red"


def test_orchestrator_uses_runtime_test_execution_for_markdown_specs(
    executable_spec: tuple[SpecRegistry, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """O caminho verde do orquestrador recebe evidência recém-emitida pelo runner."""
    registry, spec_id = executable_spec
    verifier = SpecVerifier(registry)
    invoked_paths: list[str] = []
    published: list[tuple[str, dict[str, object]]] = []

    def passing_pytest(test_path: str) -> dict[str, object]:
        invoked_paths.append(test_path)
        return {"returncode": 0, "all_passed": True, "summary": "2 passed"}

    monkeypatch.setattr(orchestrator_module, "spec_verifier", verifier)
    monkeypatch.setattr(tdd_runner_module, "run_pytest", passing_pytest)
    monkeypatch.setattr(
        orchestrator_module.metabus,
        "publish",
        lambda topic, payload, source_agent=None: published.append((topic, payload)),
    )
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False, strict_sdd=True)
    task_id = "task-r448-runtime"
    orchestrator.task_specs[task_id] = spec_id

    orchestrator.report_completion(task_id, "agent-test", {"agent": "output"})

    assert invoked_paths == ["tests/test_r448_sdd_contracts.py"]
    assert published[-1][1]["status"] == "completed"
    verification = published[-1][1]["sdd_verification"]
    assert isinstance(verification, dict)
    assert verification["verified"] is True


def test_orchestrator_fails_closed_for_missing_markdown_test_even_when_non_strict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A compatibilidade não estrita não reabre um contrato Markdown sem teste."""
    spec_id = "SPEC-TEST-ORQUESTRADOR-SEM-TESTE"
    _write_spec(
        tmp_path,
        spec_id,
        """## Critérios de Aceitação Executáveis

- `real_test_required` — é preciso executar o teste vinculado.
""",
        test_file="tests/nao-existe-r448-orchestrador.py",
    )
    published: list[tuple[str, dict[str, object]]] = []
    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        monkeypatch.setattr(orchestrator_module, "spec_verifier", SpecVerifier(registry))
        monkeypatch.setattr(
            orchestrator_module.metabus,
            "publish",
            lambda topic, payload, source_agent=None: published.append((topic, payload)),
        )
        orchestrator = MarceloClaroOrchestrator(auto_load_agents=False, strict_sdd=False)
        task_id = "task-r448-sem-teste"
        orchestrator.task_specs[task_id] = spec_id

        orchestrator.report_completion(
            task_id,
            "agent-test",
            {"evidence": {"real_test_required": {"passed": True}}},
        )

    assert published[-1][1]["status"] == "failed"
    verification = published[-1][1]["sdd_verification"]
    assert isinstance(verification, dict)
    assert verification["verified"] is False


def test_tdd_runner_executes_the_bound_test_file_for_markdown_specs(
    executable_spec: tuple[SpecRegistry, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """O ciclo TDD também não aceita a alegação do produtor sem teste vinculado."""
    registry, spec_id = executable_spec
    spec = registry.get(spec_id)
    assert spec is not None
    invoked_paths: list[str] = []

    def passing_pytest(test_path: str) -> dict[str, object]:
        invoked_paths.append(test_path)
        return {"returncode": 0, "all_passed": True, "summary": "2 passed"}

    monkeypatch.setattr(tdd_runner_module, "spec_verifier", SpecVerifier(registry))
    monkeypatch.setattr(tdd_runner_module, "run_pytest", passing_pytest)

    result = TDDRunner(max_iterations=1).run_cycle(
        spec,
        lambda _objective, _feedback: {
            "evidence": {
                "proof_is_sound": {"passed": True},
                "manifest_is_pinned": {"passed": True},
            }
        },
    )

    assert invoked_paths == ["tests/test_r448_sdd_contracts.py"]
    assert result["success"] is True
    assert result["phase"] == "verified"


def test_legacy_spec_without_executable_section_still_loads(tmp_path: Path) -> None:
    """Specs legadas mantêm o carregamento e não ganham contratos implícitos."""
    spec_id = "SPEC-TEST-LEGADA"
    _write_spec(
        tmp_path,
        spec_id,
        """## Critérios de Aceitação

1. O comportamento histórico permanece disponível.
2. Esta seção narrativa não define contratos executáveis automaticamente.
""",
    )

    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        spec = registry.get(spec_id)

    assert spec is not None
    assert spec.title == "Spec temporária para contratos SDD"
    assert spec.criteria == []


def test_legacy_programmatic_criteria_keep_their_existing_verification_path(
    tmp_path: Path,
) -> None:
    """A blindagem vale para contratos Markdown, sem quebrar critérios legados."""
    spec_id = "SPEC-TEST-LEGADA-COMPATIVEL"
    _write_spec(
        tmp_path,
        spec_id,
        "## Critérios de Aceitação\n\n1. Contrato narrativo legado.",
    )
    with _isolated_registry() as registry:
        assert registry.load_formal_specs(str(tmp_path)) == 1
        spec = registry.get(spec_id)
        assert spec is not None
        spec.add_criterion("Saída legada válida", lambda output: output == {"ok": True})

        result = SpecVerifier(registry).verify(spec_id, {"ok": True})

    assert result["verified"] is True
    assert result["status"] == "green"


def _requirement_lines(path: Path) -> list[str]:
    return [
        line.split("#", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.split("#", 1)[0].strip()
        and not line.lstrip().startswith(("-r", "--requirement"))
    ]


def _requirement_names(lines: list[str]) -> set[str]:
    return {
        line.split("==", 1)[0].lower().replace("-", "_")
        for line in lines
    }


def test_runtime_and_development_manifests_are_explicitly_pinned() -> None:
    """Dependências de runtime e desenvolvimento são reprodutíveis e separadas."""
    root = Path(__file__).resolve().parent.parent
    runtime = _requirement_lines(root / "requirements.txt")
    development = _requirement_lines(root / "requirements-dev.txt")

    assert runtime and development
    assert all("==" in requirement for requirement in runtime)
    assert all("==" in requirement for requirement in development)
    assert {
        "mcp",
        "httpx",
        "click",
        "prompt_toolkit",
        "pyyaml",
        "jsonschema",
        "whoosh",
        "numpy",
        "scikit_learn",
        "jinja2",
        "sympy",
        "z3_solver",
        "python_docx",
        "requests",
    } <= _requirement_names(runtime)
    assert {"pytest", "pytest_timeout", "pytest_xdist", "ruff", "mutmut"} <= _requirement_names(
        development
    )
    assert not {"pytest", "pytest_timeout", "pytest_xdist", "ruff", "mutmut"} & _requirement_names(
        runtime
    )


def test_mutation_gate_targets_the_formal_soundness_contract() -> None:
    """A ferramenta de mutação tem alvo e teste explícitos, sem autodetecção ambígua."""
    root = Path(__file__).resolve().parent.parent
    config = ConfigParser()
    assert config.read(root / "setup.cfg")
    assert config.get("mutmut", "source_paths") == "integrations/deepmind/formal_safety_predicates.py"
    assert {
        line.strip() for line in config.get("mutmut", "also_copy").splitlines() if line.strip()
    } == {"integrations/__init__.py", "integrations/deepmind/"}
    assert {
        line.strip()
        for line in config.get("mutmut", "pytest_add_cli_args_test_selection").splitlines()
        if line.strip()
    } == {
        "tests/test_r448_formal_mutation.py",
    }


def test_mutation_runner_prioritizes_the_generated_mutant_tree() -> None:
    """O pytest do Mutmut não pode importar o módulo original por precedência."""
    root = Path(__file__).resolve().parent.parent
    conftest = (root / "tests" / "conftest.py").read_text(encoding="utf-8")

    assert 'os.environ.get("MUTANT_UNDER_TEST")' in conftest
    assert "sys.path.insert(0, str(root))" in conftest


def test_ci_uses_declared_dev_dependencies_and_does_not_hide_late_failures() -> None:
    """A CI instala o manifesto único e executa a suíte sem ``-x``."""
    ci = (Path(__file__).resolve().parent.parent / ".github/workflows/ci.yml").read_text(
        encoding="utf-8"
    )

    assert "pip install -r requirements-dev.txt pytest-timeout pytest-xdist" not in ci
    assert "pip install -r requirements-dev.txt" in ci
    assert "pip install ruff" not in ci
    assert "python -m ruff check" in ci
    assert "integrations/deepmind/formal_safety_predicates.py" in ci
    assert "--timeout=120 -x" not in ci
    assert ci.count("python scripts/quality_report.py") == 1


def test_quality_report_timeout_covers_the_full_suite_duration() -> None:
    """O relatório chamado pela CI não pode abortar antes da suíte integral."""
    root = Path(__file__).resolve().parent.parent
    quality_report = (root / "scripts" / "quality_report.py").read_text(encoding="utf-8")

    assert "PYTEST_TIMEOUT_SECONDS = 1200" in quality_report
    assert '[sys.executable, "-m", "ruff", "check"' in quality_report
