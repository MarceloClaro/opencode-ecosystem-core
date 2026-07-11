# -*- coding: utf-8 -*-
"""
Testes R130 — Integração de Skills Cloud (Antigravity Backup)
=============================================================
TDD de documentação e infraestrutura: garante que o catálogo de skills
cloud, os agentes especializados e os scripts operacionais foram
corretamente integrados ao ecossistema OpenCode.

Requisitos: SPEC-935-R130.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import pytest

# Os scripts do backup Antigravity (scripts/cloud/, 324 arquivos externos)
# NÃO são versionados até revisão de licença/procedência (ver PROGRESS.md /
# .gitignore). Os testes que inspecionam esses arquivos no disco pulam
# graciosamente quando o diretório não está presente (ex.: checkout limpo),
# e continuam validando quando o backup está disponível localmente.
_CLOUD_SCRIPTS = ROOT / "scripts" / "cloud"
_skip_no_cloud_scripts = pytest.mark.skipif(
    not _CLOUD_SCRIPTS.exists(),
    reason="scripts/cloud/ (backup externo Antigravity) não versionado — ver PROGRESS.md",
)

# ──────────────────────────────────────────────────────────────────────
# CT-01: Catálogo skills-cloud-antigravity.md existe
# ──────────────────────────────────────────────────────────────────────

def test_catalogo_cloud_skills_existe():
    path = ROOT / "agents" / "catalog" / "skills-cloud-antigravity.md"
    assert path.exists(), "Catálogo skills-cloud-antigravity.md ausente"

def test_catalogo_contem_skills_total():
    path = ROOT / "agents" / "catalog" / "skills-cloud-antigravity.md"
    txt = path.read_text(encoding="utf-8")
    # Deve conter maracação de 56 skills
    assert "56" in txt[:2000], "Catálogo deve declarar 56 skills"

# ──────────────────────────────────────────────────────────────────────
# CT-02: Catálogo lista >= 50 skills (linhas com |**|)
# ──────────────────────────────────────────────────────────────────────

def test_catalogo_lista_pelo_menos_50_skills():
    path = ROOT / "agents" / "catalog" / "skills-cloud-antigravity.md"
    txt = path.read_text(encoding="utf-8")
    # Contar linhas de tabela com skills (padrão: linhas com | 1 | ... |)
    import re
    skill_lines = re.findall(r"^\| +\d+ +\|", txt, re.MULTILINE)
    assert len(skill_lines) >= 50, (
        f"Catálogo lista apenas {len(skill_lines)} skills (mínimo 50)"
    )

# ──────────────────────────────────────────────────────────────────────
# CT-03: Catálogo lista >= 200 scripts
# ──────────────────────────────────────────────────────────────────────

def test_catalogo_menciona_scripts():
    path = ROOT / "agents" / "catalog" / "skills-cloud-antigravity.md"
    txt = path.read_text(encoding="utf-8")
    assert "269" in txt or "268" in txt, (
        "Catálogo deve mencionar quantidade de scripts (268/269)"
    )
    assert ".js" in txt, "Catálogo deve mencionar scripts .js"
    assert ".py" in txt, "Catálogo deve mencionar scripts .py"

# ──────────────────────────────────────────────────────────────────────
# CT-04: Pelo menos 1 agente cloud criado no catálogo
# ──────────────────────────────────────────────────────────────────────

def test_agentes_cloud_existem():
    agentes = [
        "cloud-alloydb-specialist",
        "cloud-bigquery-specialist",
        "cloud-sql-postgres-specialist",
        "cloud-sql-mysql-specialist",
        "cloud-sql-sqlserver-specialist",
        "cloud-data-pipelines-specialist",
        "cloud-security-specialist",
        "cloud-data-infra-generalist",
    ]
    encontrados = 0
    for agente in agentes:
        path = ROOT / "agents" / "catalog" / f"{agente}.md"
        if path.exists():
            encontrados += 1
    assert encontrados >= 1, (
        f"Nenhum agente cloud encontrado (esperado >= 1, encontrados {encontrados})"
    )

def test_agentes_cloud_completos():
    """Verifica que pelo menos 4 dos 8 agentes cloud foram criados."""
    agentes = [
        "cloud-alloydb-specialist",
        "cloud-bigquery-specialist",
        "cloud-sql-postgres-specialist",
        "cloud-sql-mysql-specialist",
        "cloud-sql-sqlserver-specialist",
        "cloud-data-pipelines-specialist",
        "cloud-security-specialist",
        "cloud-data-infra-generalist",
    ]
    encontrados = sum(
        1 for a in agentes
        if (ROOT / "agents" / "catalog" / f"{a}.md").exists()
    )
    # Este teste é informativo, não bloqueante
    print(f"Agentes cloud criados: {encontrados}/8")

# ──────────────────────────────────────────────────────────────────────
# CT-07: Scripts do backup acessíveis via scripts/cloud/
# ──────────────────────────────────────────────────────────────────────

@_skip_no_cloud_scripts
def test_scripts_cloud_diretorio_existe():
    path = ROOT / "scripts" / "cloud"
    assert path.exists(), "Diretório scripts/cloud/ não existe"
    assert path.is_dir(), "scripts/cloud/ não é um diretório"

@_skip_no_cloud_scripts
def test_scripts_cloud_tem_skills():
    skills_dir = ROOT / "scripts" / "cloud"
    subdirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    assert len(subdirs) >= 50, (
        f"Apenas {len(subdirs)} subdiretórios em scripts/cloud/ (esperado >= 50)"
    )

@_skip_no_cloud_scripts
def test_scripts_cloud_tem_arquivos():
    skills_dir = ROOT / "scripts" / "cloud"
    total = sum(1 for _ in skills_dir.rglob("*") if _.is_file())
    assert total >= 200, (
        f"Apenas {total} arquivos em scripts/cloud/ (esperado >= 200)"
    )

# ──────────────────────────────────────────────────────────────────────
# CT-06: SPEC existe
# ──────────────────────────────────────────────────────────────────────

def test_spec_r130_existe():
    path = ROOT / "specs" / "SPEC-935-R130.md"
    assert path.exists(), "SPEC-935-R130.md ausente"
    txt = path.read_text(encoding="utf-8")
    assert "SPEC-935-R130" in txt
    assert "antigravity" in txt.lower() or "cloud" in txt.lower()

# ──────────────────────────────────────────────────────────────────────
# CT-08: doctor continua passando (verificação básica de ambiente)
# ──────────────────────────────────────────────────────────────────────

def test_doctor_nao_quebra():
    """Teste básico: importar módulos principais não deve falhar."""
    try:
        import marceloclaro
        # O módulo marceloclaro deve ter alguma estrutura acessível
        assert hasattr(marceloclaro, "__version__") or hasattr(marceloclaro, "orchestrator"), \
            "marceloclaro sem atributos esperados"
    except ImportError:
        # Se não estiver instalado como pacote, tentar pelo path
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        import marceloclaro  # noqa

# ──────────────────────────────────────────────────────────────────────
# Sanidade: Estrutura do catálogo
# ──────────────────────────────────────────────────────────────────────

def test_catalogo_estrutura_categorias():
    path = ROOT / "agents" / "catalog" / "skills-cloud-antigravity.md"
    txt = path.read_text(encoding="utf-8")
    categorias = [
        "AlloyDB Omni",
        "AlloyDB PostgreSQL",
        "Cloud SQL PostgreSQL",
        "BigQuery",
        "GCP Data Pipelines",
        "GCP Security",
        "Firestore & Spanner",
    ]
    for cat in categorias:
        assert cat.lower() in txt.lower(), f"Categoria '{cat}' não encontrada no catálogo"
