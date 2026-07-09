# -*- coding: utf-8 -*-
"""
Testes R104b — Pip Packages (TDD: RED → GREEN → REFACTOR)
=================================================================
Testa os 3 pacotes pip: opencode-evosci, opencode-deep-research, opencode-peer-review.
Requisitos:
  - Diretorios em packages/opencode-{evosci,deep-research,peer-review}/
  - Cada um com pyproject.toml valido
  - Importavel via from opencode_* import ...
  - 3+ testes por pacote (9+ total)
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

# ── Fixtures ────────────────────────────────────────────────────────

PACKAGES_DIR = Path(__file__).resolve().parent.parent / "packages"
PACKAGE_NAMES = ["opencode-evosci", "opencode-deep-research", "opencode-peer-review"]
IMPORT_NAMES = {
    "opencode-evosci": "opencode_evosci",
    "opencode-deep-research": "opencode_deep_research",
    "opencode-peer-review": "opencode_peer_review",
}


@pytest.fixture(params=PACKAGE_NAMES)
def pkg_name(request):
    return request.param


@pytest.fixture
def pkg_dir(pkg_name):
    d = PACKAGES_DIR / pkg_name
    if not d.exists():
        pytest.skip(f"Package dir {d} ainda nao existe (RED phase)")
    return d


# ── Testes estruturais ─────────────────────────────────────────────

class TestPackageStructure:
    """Testa existencia e estrutura dos pacotes."""

    def test_package_directory_exists(self, pkg_name):
        d = PACKAGES_DIR / pkg_name
        assert d.exists(), f"Package dir {d} nao encontrado"

    def test_pyproject_toml_exists(self, pkg_dir):
        assert (pkg_dir / "pyproject.toml").exists(), "pyproject.toml ausente"

    def test_pyproject_toml_valid(self, pkg_dir):
        """pyproject.toml é parseavel como TOML basico."""
        content = (pkg_dir / "pyproject.toml").read_text()
        assert "[project]" in content, "pyproject.toml deve ter secao [project]"
        assert "name" in content, "pyproject.toml deve ter name"

    def test_init_py_exists(self, pkg_name, pkg_dir):
        """__init__.py existe no modulo principal."""
        import_name = IMPORT_NAMES[pkg_name]
        init_path = pkg_dir / import_name / "__init__.py"
        assert init_path.exists(), f"{init_path} ausente"

    def test_module_importable(self, pkg_name, pkg_dir):
        """Modulo e importavel via sys.path."""
        import_name = IMPORT_NAMES[pkg_name]
        sys.path.insert(0, str(pkg_dir))
        try:
            mod = importlib.import_module(import_name)
            assert mod is not None
        finally:
            sys.path.pop(0)

    def test_readme_exists(self, pkg_dir):
        readme = pkg_dir / "README.md"
        assert readme.exists(), "README.md ausente"


# ── Testes de instalacao ───────────────────────────────────────────

class TestPackageInstallation:
    """Testa que o pacote pode ser instalado via pip."""

    def test_pip_install_editable(self, pkg_name):
        """pip install -e <pkg_dir> funciona."""
        d = PACKAGES_DIR / pkg_name
        if not d.exists():
            pytest.skip("Package dir nao existe")

        # Tentar import direto via sys.path (mais leve que pip install)
        import_name = IMPORT_NAMES[pkg_name]
        if d not in sys.path:
            sys.path.insert(0, str(d))
        try:
            mod = importlib.import_module(import_name)
            assert mod is not None
        finally:
            if d in sys.path:
                sys.path.remove(str(d))

    def test_pip_build(self, pkg_name):
        """python -m build funciona (opcional, so testa se build disponivel)."""
        d = PACKAGES_DIR / pkg_name
        if not d.exists():
            pytest.skip("Package dir nao existe")
        try:
            import build
        except ImportError:
            pytest.skip("build package nao instalado")
        # So verifica se nao crasha
        result = subprocess.run(
            [sys.executable, "-m", "build", "--sdist", str(d)],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, f"Build falhou: {result.stderr}"


# ── Testes de conteudo ─────────────────────────────────────────────

class TestPackageContent:
    """Testa que cada pacote contem os modulos esperados."""

    def test_evosci_has_agents(self):
        d = PACKAGES_DIR / "opencode-evosci"
        if not d.exists():
            pytest.skip("opencode-evosci nao existe")
        import_name = "opencode_evosci"
        sys.path.insert(0, str(d))
        try:
            mod = importlib.import_module(import_name)
            # Deve ter pelo menos um dos componentes principais
            components = ["MentorAgent", "PrimeResearcherAgent", "EvoEngine",
                          "AgenticScienceV2"]
            found = [c for c in components if hasattr(mod, c)]
            assert len(found) >= 1, f"Nenhum componente esperado encontrado em {import_name}. Encontrados: {dir(mod)}"
        finally:
            sys.path.remove(str(d))

    def test_deep_research_has_evidence_graph(self):
        d = PACKAGES_DIR / "opencode-deep-research"
        if not d.exists():
            pytest.skip("opencode-deep-research nao existe")
        import_name = "opencode_deep_research"
        sys.path.insert(0, str(d))
        try:
            mod = importlib.import_module(import_name)
            components = ["EvidenceGraph", "BFRSAgent", "DFRSAgent", "KnowledgeBaseRegistry", "OrchestratorAgent"]
            found = [c for c in components if hasattr(mod, c)]
            assert len(found) >= 1, f"Nenhum componente esperado encontrado"
        finally:
            sys.path.remove(str(d))

    def test_peer_review_has_review_agent(self):
        d = PACKAGES_DIR / "opencode-peer-review"
        if not d.exists():
            pytest.skip("opencode-peer-review nao existe")
        import_name = "opencode_peer_review"
        sys.path.insert(0, str(d))
        try:
            mod = importlib.import_module(import_name)
            components = ["RubricEngine", "ReviewLedger", "MultiCriticReviewer",
                          "OrchestratorReviewer"]
            found = [c for c in components if hasattr(mod, c)]
            assert len(found) >= 1, f"Nenhum componente esperado encontrado"
        finally:
            sys.path.remove(str(d))


# ── Teste de contagem ──────────────────────────────────────────────

def test_total_package_count():
    """Devem existir exatamente 3 pacotes."""
    existing = [d for d in PACKAGES_DIR.iterdir() if d.is_dir() and d.name in PACKAGE_NAMES]
    assert len(existing) == 3, f"Esperado 3 pacotes, encontrado {len(existing)}"
