# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


EXPECTED_MIRA_AGENTS = {
    "mira-new",
    "mira-references",
    "mira-animator",
    "mira-animated-metaphor",
    "mira-size-animator",
    "mira-image",
    "mira-get-videos",
    "mira-extract",
    "mira-planner",
    "mira-copywriter",
    "mira-builder",
    "mira-validator",
    "mira-visuals",
    "mira-chart",
    "mira-chart-race",
    "mira-qrcode",
    "mira-3d",
    "mira-image-template",
    "mira-survey",
    "mira-squared",
    "mira-vertical",
    "mira-thirds",
}


def test_mira_catalog_files_exist():
    for agent_id in EXPECTED_MIRA_AGENTS:
        path = Path("agents/catalog") / f"{agent_id}.md"
        assert path.exists(), str(path)


def test_catalog_loader_includes_mira_agents():
    from marceloclaro.catalog_loader import load_catalog_definitions

    definitions = load_catalog_definitions()
    ids = {d["agent_id"] for d in definitions}
    assert EXPECTED_MIRA_AGENTS <= ids


def test_mira_agents_have_non_empty_description():
    from marceloclaro.catalog_loader import load_catalog_definitions

    definitions = {d["agent_id"]: d for d in load_catalog_definitions()}
    for agent_id in EXPECTED_MIRA_AGENTS:
        assert definitions[agent_id]["description"].strip(), agent_id
