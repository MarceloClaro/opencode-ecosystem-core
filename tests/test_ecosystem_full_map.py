# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_build_ecosystem_map_has_nodes_and_vectors():
    from marceloclaro.ecosystem_map import build_ecosystem_map

    graph = build_ecosystem_map()

    assert graph["summary"]["node_count"] >= 200
    assert graph["summary"]["vector_count"] >= 200


def test_build_ecosystem_map_contains_key_paths():
    from marceloclaro.ecosystem_map import build_ecosystem_map

    graph = build_ecosystem_map()
    paths = {n.get("path") for n in graph["nodes"] if n.get("path")}

    assert "marceloclaro/orchestrator.py" in paths
    assert "mci/metabus.py" in paths
    assert "mci/pipeline/scientific_governance_pipeline.py" in paths
    assert "mci/metacognitive_evaluator.py" in paths
    assert "rag/scientific.py" in paths
    assert "legal/syllogism.py" in paths
    assert "legal/balancing.py" in paths
    assert "legal/precedents.py" in paths
    assert "legal/constitutional.py" in paths
    assert "legal/argumentation.py" in paths
    assert "legal/datajud_client.py" in paths
    assert "legal/integration.py" in paths
    assert "legal/agents.py" in paths
    assert "legal/knowledge_base.py" in paths
    assert "legal/summarizer.py" in paths
    assert "scanners/legal_impact_scanner.py" in paths
    assert "webapp/app.py" in paths
    assert "webapp/legal_impact_helpers.py" in paths
    assert "specs/SPEC-920-metacognitive-superhuman-refinement.md" in paths
    assert "specs/SPEC-921-brazilian-legal-reasoning.md" in paths
    assert "specs/SPEC-922-datajud-integration.md" in paths
    assert "specs/SPEC-923-auxjuris-integration.md" in paths
    assert "specs/SPEC-924-legal-impact-scanner.md" in paths
    assert "specs/SPEC-925-webapp-legal-impact-interface.md" in paths
    assert "specs/SPEC-926-webapp-dedicated-legal-tab.md" in paths
    assert "tests/test_metacognitive_superhuman.py" in paths
    assert "tests/test_datajud_integration.py" in paths
    assert "tests/test_auxjuris_integration.py" in paths
    assert "tests/test_legal_impact_scanner.py" in paths
    assert "tests/test_webapp_legal_impact.py" in paths
    assert "research/pipelines/analyze_research_batch.py" in paths
    assert "agents/catalog/mira-new.md" in paths


def test_build_ecosystem_map_contains_key_vector_kinds():
    from marceloclaro.ecosystem_map import build_ecosystem_map

    graph = build_ecosystem_map()
    kinds = {v["kind"] for v in graph["vectors"]}

    assert "contains" in kinds
    assert "imports" in kinds
    assert "documents" in kinds
    assert "depends_on" in kinds
    assert "control_flow" in kinds


def test_full_map_artifacts_exist_and_have_core_content():
    md = Path("MAPA_ECOSSISTEMA_COMPLETO_2026-07-06.md")
    js = Path("maps/ecosystem_map_2026-07-06.json")

    assert md.exists()
    assert js.exists()

    text = md.read_text(encoding="utf-8")
    assert "# Mapa Completo do Ecossistema" in text
    assert "Taxonomia de Vetores" in text
    assert "Inventário de Nós" in text
    assert "Inventário de Vetores" in text
