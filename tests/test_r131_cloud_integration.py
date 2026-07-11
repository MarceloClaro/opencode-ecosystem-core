# -*- coding: utf-8 -*-
"""
Testes R131 — Integração Cloud Fase 2/3/4
=========================================
Valida: agentes cloud no opencode.json, pipeline MASWOS Cloud,
AntiBridge com skills cloud, e ciclo de evolução.

Requisitos: SPEC-935-R130 (extensão).
"""
from pathlib import Path
import json
import re

import pytest

ROOT = Path(__file__).resolve().parent.parent

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


# ═══════════════════════════════════════════════════════════════
# CT-01: opencode.json contém os 8 agentes cloud
# ═══════════════════════════════════════════════════════════════

def test_opencode_json_tem_agentes_cloud():
    path = ROOT / "opencode.json"
    assert path.exists(), "opencode.json ausente"
    config = json.loads(path.read_text(encoding="utf-8"))
    agents = config.get("agent", {})
    cloud_agents = [
        "cloud-alloydb-specialist",
        "cloud-bigquery-specialist",
        "cloud-sql-postgres-specialist",
        "cloud-sql-mysql-specialist",
        "cloud-sql-sqlserver-specialist",
        "cloud-data-pipelines-specialist",
        "cloud-security-specialist",
        "cloud-data-infra-generalist",
    ]
    for agent_id in cloud_agents:
        assert agent_id in agents, f"Agente {agent_id} não registrado no opencode.json"
        entry = agents[agent_id]
        assert entry.get("mode") == "subagent", f"{agent_id} não é subagent"
        assert "prompt" in entry, f"{agent_id} sem prompt"
    print(f"  8/8 agentes cloud verificados no opencode.json")


def test_opencode_json_total_agents_aumentou():
    path = ROOT / "opencode.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    total = len(config.get("agent", {}))
    assert total >= 170, f"opencode.json tem apenas {total} agentes (esperado >= 170)"
    print(f"  opencode.json: {total} agentes totais")


# ═══════════════════════════════════════════════════════════════
# CT-02: MASWOS Cloud — detecção de tópico
# ═══════════════════════════════════════════════════════════════

def test_maswos_is_cloud_topic():
    """Tópicos cloud devem ser identificados."""
    from academic.maswos import is_cloud_topic

    cloud_topics = [
        "AlloyDB Omni performance tuning",
        "Cloud SQL PostgreSQL migration",
        "BigQuery ML para análise preditiva",
        "Dataflow pipelines em streaming",
        "GCP infrastructure as code",
        "Cloud database optimization",
        "Infraestrutura em nuvem para data lakes",
        "google cloud data warehouse",
    ]
    generic_topics = [
        "Inteligência artificial na medicina",
        "Literatura brasileira contemporânea",
        "Bioinformática aplicada",
        "Ensino de matemática",
    ]

    for topic in cloud_topics:
        assert is_cloud_topic(topic), f"FALSO NEGATIVO: '{topic}' deveria ser cloud"
    
    for topic in generic_topics:
        assert not is_cloud_topic(topic), f"FALSO POSITIVO: '{topic}' não deveria ser cloud"
    
    print(f"  is_cloud_topic: {len(cloud_topics)} cloud ✅, {len(generic_topics)} genérico ✅")


def test_maswos_cloud_stages_exist():
    """Estágios cloud definidos no pipeline."""
    from academic.maswos import CLOUD_STAGES
    assert len(CLOUD_STAGES) == 8, f"CLOUD_STAGES tem {len(CLOUD_STAGES)} estágios (esperado 8)"
    
    stage_names = [s[0] for s in CLOUD_STAGES]
    assert "cloud_diagnostico" in stage_names
    assert "cloud_arquitetura" in stage_names
    assert "cloud_banco_dados" in stage_names
    assert "cloud_bigquery_analytics" in stage_names
    print(f"  CLOUD_STAGES: {len(CLOUD_STAGES)} estágios definidos ✅")


def test_maswos_cloud_agents_exist_in_catalog():
    """Agentes referenciados em CLOUD_STAGES devem existir no catálogo."""
    from academic.maswos import CLOUD_STAGES
    
    for stage_name, agent_id, capability in CLOUD_STAGES:
        path = ROOT / "agents" / "catalog" / f"{agent_id}.md"
        assert path.exists(), f"Agente {agent_id} referenciado em CLOUD_STAGES mas não existe no catálogo"
    print(f"  {len(CLOUD_STAGES)} agentes cloud do MASWOS verificados no catálogo ✅")


def test_maswos_cloud_run_dry():
    """Pipeline MASWOS Cloud em dry-run deve retornar resultados skipped."""
    from academic.maswos import run_maswos_cloud
    
    result = run_maswos_cloud("BigQuery performance optimization")
    assert result is not None
    assert result.topic.startswith("[CLOUD]")
    assert len(result.stages) == 8
    completed = sum(1 for s in result.stages if s.status == "completed")
    skipped = sum(1 for s in result.stages if s.status == "skipped")
    assert skipped == 8, f"Deveriam ser 8 skipped (dry-run), obtidos {skipped}"
    print(f"  MASWOS Cloud dry-run: {completed} completed, {skipped} skipped ✅")


def test_maswos_generic_topic_usas_pipeline_padrao():
    """Tópico genérico não deve ativar pipeline cloud."""
    from academic.maswos import run_maswos_cloud
    
    result = run_maswos_cloud("Inteligência artificial na medicina")
    assert result is not None
    assert not result.topic.startswith("[CLOUD]")
    # Pipeline padrão tem 16 estágios
    assert len(result.stages) == 16
    print(f"  Pipeline genérico: {len(result.stages)} estágios (padrão) ✅")


# ═══════════════════════════════════════════════════════════════
# CT-03: AntiBridge — capacidades cloud registradas
# ═══════════════════════════════════════════════════════════════

def test_antigravity_bridge_cloud_capabilities():
    """AntiBridge deve conter as capacidades cloud."""
    bridge_path = ROOT / "integrations" / "antigravity" / "antigravity-bridge.ts"
    assert bridge_path.exists(), "antigravity-bridge.ts ausente"
    
    content = bridge_path.read_text(encoding="utf-8")
    
    # Verificar que as capacidades cloud foram adicionadas
    cloud_caps = [
        "cloud_alloydb_admin",
        "cloud_bigquery_analytics",
        "cloud_sql_postgres_admin",
        "cloud_dataflow_pipelines",
        "cloud_gcs_security",
        "cloud_lakehouse_federation",
    ]
    for cap in cloud_caps:
        assert cap in content, f"Capacidade cloud '{cap}' não encontrada no AntiBridge"
    
    # Verificar padrões de trigger cloud
    cloud_patterns = [
        "alloydb",
        "cloud sql",
        "data pipeline",
        "infrastructure as code",
    ]
    for pattern in cloud_patterns:
        assert pattern.lower() in content.lower(), f"Trigger pattern '{pattern}' não encontrado"
    
    # Verificar afinidades cloud
    assert "cloud-alloydb-specialist" in content
    assert "cloud-bigquery-specialist" in content
    print(f"  AntiBridge: {len(cloud_caps)} capacidades cloud verificadas ✅")


def test_antigravity_bridge_version_updated():
    bridge_path = ROOT / "integrations" / "antigravity" / "antigravity-bridge.ts"
    content = bridge_path.read_text(encoding="utf-8")
    assert "v1.1" in content, "Versão do AntiBridge não atualizada para v1.1"
    assert "SPEC-935-R130" in content, "AntiBridge sem referência SPEC-935-R130"
    print(f"  AntiBridge versão e referência SPEC-935-R130 verificadas ✅")


# ═══════════════════════════════════════════════════════════════
# CT-04: Evolution Registry
# ═══════════════════════════════════════════════════════════════

def test_evolution_cycle_r135_existe():
    """Ciclo de evolução R135 deve estar registrado."""
    cycles_file = ROOT / "evolution" / "cycles.json"
    assert cycles_file.exists(), "cycles.json ausente"
    data = json.loads(cycles_file.read_text(encoding="utf-8"))
    cycles = data.get("cycles", data if isinstance(data, list) else [])
    
    r135 = None
    for c in cycles:
        if c.get("round_id") == "R135":
            r135 = c
            break
    
    assert r135 is not None, "Ciclo R135 não encontrado no evolution registry"
    assert r135.get("score", 0) >= 7.0, f"Score R135 ({r135.get('score')}) abaixo de 7.0"
    changes = r135.get("changes", [])
    assert len(changes) >= 5, f"R135 tem apenas {len(changes)} changes (esperado >= 5)"
    print(f"  Evolution R135: score {r135.get('score')}, {len(changes)} changes ✅")


# ═══════════════════════════════════════════════════════════════
# CT-05: Scripts cloud — verificação de integridade
# ═══════════════════════════════════════════════════════════════

@_skip_no_cloud_scripts
def test_scripts_cloud_skills_maiores():
    """Skills maiores (>= 10KB) devem estar presentes."""
    skills_dir = ROOT / "scripts" / "cloud"
    big_skills = [
        "alloydb-omni-kubernetes",
        "alloydb-omni-performance",
        "alloydb-postgres-monitor",
        "cloud-sql-postgres-health",
        "cloud-sql-postgres-monitor",
        "cloud-sql-postgres-vectorassist",
        "gcp-dataflow",
        "gcp-pipeline-orchestration",
    ]
    for skill in big_skills:
        skill_path = skills_dir / skill / "SKILL.md"
        assert skill_path.exists(), f"Skill grande ausente: {skill}"
        size = skill_path.stat().st_size
        assert size >= 10000, f"Skill {skill} tem {size} bytes (esperado >= 10000)"
    print(f"  {len(big_skills)} skills grandes verificadas ✅")


@_skip_no_cloud_scripts
def test_scripts_cloud_python_scripts():
    """Scripts Python de automação devem existir."""
    skills_dir = ROOT / "scripts" / "cloud"
    
    python_scripts = [
        "bigquery-data-transfer-service/scripts/bigquery_dts.py",
        "data-autocleaning/scripts/dataplex_scanner.py",
        "gcp-pipeline-orchestration/scripts/trigger/airflow_trigger.py",
        "gcs-security-assessment/scripts/evaluate_project_security_posture.py",
    ]
    for rel_path in python_scripts:
        full_path = skills_dir / rel_path
        assert full_path.exists(), f"Script Python ausente: {rel_path}"
    print(f"  {len(python_scripts)} scripts Python verificados ✅")


# ═══════════════════════════════════════════════════════════════
# CT-06: Cobertura de licenciamento
# ═══════════════════════════════════════════════════════════════

@_skip_no_cloud_scripts
def test_skills_cloud_licenca_apache():
    """Skills devem mencionar licença Apache 2.0."""
    skills_dir = ROOT / "scripts" / "cloud"
    apache_count = 0
    total = 0
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                total += 1
                content = skill_md.read_text(encoding="utf-8")
                if "apache" in content.lower() and "2.0" in content:
                    apache_count += 1
    assert apache_count >= 50, f"Apenas {apache_count}/{total} skills com licença Apache 2.0"
    print(f"  {apache_count}/{total} skills com licença Apache 2.0 ✅")
