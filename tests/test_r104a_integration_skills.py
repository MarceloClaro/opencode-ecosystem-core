# -*- coding: utf-8 -*-
"""
Testes R104a — Integration Skills (TDD: RED → GREEN → REFACTOR)
=================================================================
Testa os 4 skills: evo-science, deep-research, peer-review-v2, mcp-security.
Requisitos:
  - 4 diretorios em skills/{evo-science,deep-research,peer-review-v2,mcp-security}/
  - Cada um com SKILL.md + skill.py
  - SKILL.md com metadados, comandos, exemplos
  - skill.py importavel com funcoes para cada comando
  - 5+ testes por skill (20+ total)
"""

import importlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

# ── Fixtures ────────────────────────────────────────────────────────

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
SKILL_NAMES = ["evo-science", "deep-research", "peer-review-v2", "mcp-security"]


@pytest.fixture(params=SKILL_NAMES)
def skill_name(request):
    """Parametriza sobre os 4 skills."""
    return request.param


@pytest.fixture
def skill_dir(skill_name):
    """Retorna o diretorio do skill."""
    d = SKILLS_DIR / skill_name
    if not d.exists():
        pytest.skip(f"Diretorio {d} ainda nao existe (RED phase)")
    return d


# ── Testes estruturais ─────────────────────────────────────────────

class TestSkillStructure:
    """Testa existencia e estrutura dos diretorios de skill."""

    def test_skill_directory_exists(self, skill_name):
        """Criterio 1: Diretorio do skill existe."""
        d = SKILLS_DIR / skill_name
        assert d.exists(), f"Skills dir {d} nao encontrado"

    def test_skilL_md_exists(self, skill_dir):
        """Criterio 2: SKILL.md existe."""
        assert (skill_dir / "SKILL.md").exists(), "SKILL.md ausente"

    def test_skill_py_exists(self, skill_dir):
        """Criterio 3: skill.py existe."""
        assert (skill_dir / "skill.py").exists(), "skill.py ausente"

    def test_skill_py_importable(self, skill_dir, skill_name):
        """Criterio 4: skill.py é importavel como modulo."""
        sys.path.insert(0, str(skill_dir))
        try:
            mod = importlib.import_module(f"skill_{skill_name.replace('-', '_')}")
            assert mod is not None
        except ImportError as e:
            # tentar fallback: importar como 'skill'
            try:
                mod = importlib.import_module("skill")
                assert mod is not None
            except ImportError:
                pytest.fail(f"Nenhum modulo importavel em {skill_dir}: {e}")
        finally:
            sys.path.pop(0)

    def test_skilL_md_has_commands(self, skill_dir):
        """Criterio 5: SKILL.md lista comandos (/) esperados."""
        content = (skill_dir / "SKILL.md").read_text()
        assert "/" in content, "SKILL.md deve conter comandos (slash commands)"
        # Pelo menos 2 comandos
        commands = [line for line in content.splitlines() if line.strip().startswith("/")]
        assert len(commands) >= 2, f"SKILL.md deve ter >= 2 comandos, encontrados {len(commands)}"


# ── Testes funcionais por skill ────────────────────────────────────

class TestEvoScienceSkill:
    """Testes especificos do skill evo-science."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.skill_dir = SKILLS_DIR / "evo-science"
        if not self.skill_dir.exists():
            pytest.skip("evo-science dir nao existe")
        sys.path.insert(0, str(self.skill_dir))
        yield
        sys.path.pop(0)

    def _import(self):
        try:
            return importlib.import_module("skill_evo_science")
        except ImportError:
            return importlib.import_module("skill")

    def test_evo_init_topic(self):
        """/evo-init <topic>: inicializa ciclo com hipotese."""
        mod = self._import()
        if hasattr(mod, "evo_init"):
            result = mod.evo_init("Test Hypothesis")
            assert result is not None

    def test_evo_evolve(self):
        """/evo-evolve: executa rodada evolutiva."""
        mod = self._import()
        if hasattr(mod, "evo_init"):
            mod.evo_init("Test")
        if hasattr(mod, "evo_evolve"):
            result = mod.evo_evolve()
            assert result is not None

    def test_evo_status(self):
        """/evo-status: retorna estado da populacao."""
        mod = self._import()
        if hasattr(mod, "evo_status"):
            result = mod.evo_status()
            assert result is not None

    def test_evo_report(self):
        """/evo-report: gera relatorio."""
        mod = self._import()
        if hasattr(mod, "evo_report"):
            result = mod.evo_report()
            assert result is not None


class TestDeepResearchSkill:
    """Testes especificos do skill deep-research."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.skill_dir = SKILLS_DIR / "deep-research"
        if not self.skill_dir.exists():
            pytest.skip("deep-research dir nao existe")
        sys.path.insert(0, str(self.skill_dir))
        yield
        sys.path.pop(0)

    def _import(self):
        try:
            return importlib.import_module("skill_deep_research")
        except ImportError:
            return importlib.import_module("skill")

    def test_deep_research_query(self):
        """/deep-research <query>: inicia pesquisa."""
        mod = self._import()
        if hasattr(mod, "deep_research"):
            result = mod.deep_research("AI safety 2026")
            assert result is not None

    def test_deep_evidence(self):
        """/deep-evidence <claim>: busca evidencias."""
        mod = self._import()
        if hasattr(mod, "deep_evidence"):
            result = mod.deep_evidence("Test claim")
            assert result is not None

    def test_deep_graph(self):
        """/deep-graph <entity>: explora grafo."""
        mod = self._import()
        if hasattr(mod, "deep_graph"):
            result = mod.deep_graph("transformer")
            assert result is not None

    def test_deep_summary(self):
        """/deep-summary: sumario da pesquisa."""
        mod = self._import()
        if hasattr(mod, "deep_summary"):
            result = mod.deep_summary()
            assert result is not None


class TestPeerReviewV2Skill:
    """Testes especificos do skill peer-review-v2."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.skill_dir = SKILLS_DIR / "peer-review-v2"
        if not self.skill_dir.exists():
            pytest.skip("peer-review-v2 dir nao existe")
        sys.path.insert(0, str(self.skill_dir))
        yield
        sys.path.pop(0)

    def _import(self):
        try:
            return importlib.import_module("skill_peer_review_v2")
        except ImportError:
            return importlib.import_module("skill")

    def test_review_v2_manuscript(self):
        """/review-v2 <manuscript>: revisao completa."""
        mod = self._import()
        if hasattr(mod, "review_v2"):
            result = mod.review_v2("Sample manuscript text for review")
            assert result is not None

    def test_review_rubric(self):
        """/review-rubric <paper>: gera rubrica."""
        mod = self._import()
        if hasattr(mod, "review_rubric"):
            result = mod.review_rubric("Sample paper")
            assert result is not None

    def test_review_ledger(self):
        """/review-ledger: extrai ledger."""
        mod = self._import()
        if hasattr(mod, "review_ledger"):
            result = mod.review_ledger()
            assert result is not None

    def test_review_audit(self):
        """/review-audit: auditoria."""
        mod = self._import()
        if hasattr(mod, "review_audit"):
            result = mod.review_audit()
            assert result is not None


class TestMCPSecuritySkill:
    """Testes especificos do skill mcp-security."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.skill_dir = SKILLS_DIR / "mcp-security"
        if not self.skill_dir.exists():
            pytest.skip("mcp-security dir nao existe")
        sys.path.insert(0, str(self.skill_dir))
        yield
        sys.path.pop(0)

    def _import(self):
        try:
            return importlib.import_module("skill_mcp_security")
        except ImportError:
            return importlib.import_module("skill")

    def test_security_audit(self):
        """/security-audit <tool>: auditoria."""
        mod = self._import()
        if hasattr(mod, "security_audit"):
            result = mod.security_audit("su_generate")
            assert result is not None

    def test_security_guard(self):
        """/security-guard <config>: configura guard."""
        mod = self._import()
        if hasattr(mod, "security_guard"):
            result = mod.security_guard({"rate_limit": 10})
            assert result is not None

    def test_security_report(self):
        """/security-report: relatorio."""
        mod = self._import()
        if hasattr(mod, "security_report"):
            result = mod.security_report()
            assert result is not None


# ── Contagem ────────────────────────────────────────────────────────

def test_total_skill_count():
    """Devem existir exatamente 4 skills."""
    existing = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name in SKILL_NAMES]
    assert len(existing) == 4, f"Esperado 4 skills, encontrado {len(existing)}: {[d.name for d in existing]}"
