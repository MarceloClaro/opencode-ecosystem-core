"""Contratos documentais da SPEC-935-R449."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_has_complete_operational_entrypoint() -> None:
    required_sections = {
        "## Visão geral",
        "## Capacidades principais",
        "## Início rápido local",
        "## Instalação segura e procedência",
        "## Uso básico",
        "## Arquitetura resumida",
        "## Limites de segurança e operação",
        "## Validação, contribuição e release",
        "## Documentação e licença",
    }

    assert required_sections <= set(re.findall(r"^## .+$", README, flags=re.MULTILINE))
    assert ".venv/bin/python -m marceloclaro.cli doctor" in README
    assert ".venv/bin/python -m pytest tests/ -q --tb=short --timeout=120" in README


def test_readme_documents_installation_without_fabricated_integrity_data() -> None:
    for marker in (
        "ECOSYSTEM_VERSION",
        "ECOSYSTEM_REF",
        "ECOSYSTEM_SOURCE_SHA256",
        "ProvisionSha256",
        "CommonInstallerSha256",
        "<sha-256-publicado-com-64-caracteres>",
    ):
        assert marker in README

    assert "curl | bash" not in README
    assert "curl | sh" not in README
    assert not re.search(r"\b[a-fA-F0-9]{64}\b", README)
    assert 'git describe --tags --exact-match HEAD' in README
    assert "sha256sum -c" in README
    assert "shasum -a 256 -c" in README


def test_readme_links_to_canonical_guides_and_policies() -> None:
    required_files = {
        "MANUAL.md",
        "ARCHITECTURE.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CORRIGENDUM.md",
        "installer/README.md",
        "installer/windows/README.md",
        "CHANGELOG.md",
        "LICENSE",
        "VALIDATION_R448.md",
    }

    for relative_path in required_files:
        assert (ROOT / relative_path).is_file(), relative_path
        assert relative_path in README

    for target in re.findall(r"\[[^\]]+\]\(([^)#]+)\)", README):
        if "://" not in target:
            assert (ROOT / target).is_file(), target


def test_readme_states_observed_validation_and_limits_without_overclaim() -> None:
    normalized_readme = " ".join(README.split())

    assert "SPEC-935-R448" in README
    assert "18/18" in README
    assert "3.488 passed" in README
    assert "70 skipped" in README
    assert "execução local" in README.lower()
    assert "certificação externa" in README.lower()
    assert "WSL2" in README
    assert "não substituem revisão humana" in README.lower()
    assert "superhuman" not in README.lower()
    assert "/home/" not in README
    assert "disponíveis na sua máquina." in README
    assert "não transforma as fontes encontradas em evidência já revisada." in normalized_readme
    assert "quatro subtestes aprovados." in README
    assert ".venv/bin/python -m pip install -r requirements-dev.txt" in README


def test_contributing_and_security_policies_are_actionable_and_conservative() -> None:
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert "SPEC" in contributing
    assert "pytest" in contributing
    assert "git diff --check" in contributing
    assert "Security Advisories" in security
    assert "https://github.com/MarceloClaro/opencode-ecosystem-core/security/advisories/new" in security
    assert "[Security Advisories](https://github.com/MarceloClaro/opencode-ecosystem-core/security/advisories/new)" in security
    assert "não abra issue pública" in security.lower()
    assert "garantia" not in security.lower()


def test_r448_validation_receipt_records_scope_environment_and_gates() -> None:
    receipt = (ROOT / "VALIDATION_R448.md").read_text(encoding="utf-8")

    assert "067ba78156663daa8c3e9b98d2e75b68d8b85278" in receipt
    assert "Python 3.14.4" in receipt
    assert "Linux 6.18.33.2-microsoft-standard-WSL2" in receipt
    assert "working tree" in receipt.lower()
    assert "bash -n installer/common/install_clis.sh" in receipt
    assert "bash -n installer/linux/install.sh" in receipt
    assert "bash -n installer/macos/install.sh" in receipt
    assert "bash -n installer/windows/provision.sh" in receipt
    assert "pwsh -NoProfile -Command" in receipt
    assert ".venv/bin/mutmut run --max-children 4" in receipt
    assert "1/1" in receipt


def test_readme_preserves_legacy_mira_storytelling_and_metric_navigation() -> None:
    required_markers = {
        "Apresentações MIRA",
        "MiraDeckPipeline",
        "MiraEngine",
        "mira-presenter",
        "Como funciona a apresentação MIRA",
        "Presentation On Storytelling",
        "Act I — A Ilha de Agentes",
        "Fluxograma Intuitivo",
        "Arquitetura Técnica Multilateral",
        "Ciclo de Vida SDD / TDD",
        "Mapa da Arquitetura Completa (v3.9.0)",
        "R47–R127",
        "média móvel",
        "não gate",
    }

    missing_markers = sorted(marker for marker in required_markers if marker not in README)
    assert not missing_markers, f"marcadores ausentes: {missing_markers}"
    assert README.count("```mermaid") >= 4
    assert "snapshot histórico" in README.lower()
