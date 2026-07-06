#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ecosystem_coverage_reaches_100pct():
    from scanners import diagnostic_pipeline

    report = diagnostic_pipeline.run("ecosystem", domain="ecosystem")

    assert report["noological"]["summary"]["overall_coverage_pct"] == 100
    assert report["noological"]["summary"]["categories_absent"] == 0


def test_ecosystem_layers_all_present():
    from scanners import diagnostic_pipeline

    report = diagnostic_pipeline.run("ecosystem", domain="ecosystem")
    layers = report["ecosystem_layers"]

    assert set(layers.keys()) == {
        "core_orchestration",
        "diagnostico_evolucao",
        "governanca_economia",
        "raciocinio_conhecimento",
        "integracao_infra",
    }
    assert all(v["coverage_pct"] > 0 for v in layers.values())


def test_ecosystem_teleology_uses_ecosystem_dimensions():
    from scanners import diagnostic_pipeline

    report = diagnostic_pipeline.run("ecosystem", domain="ecosystem")
    teleo = report["teleological"]

    assert isinstance(teleo.get("score"), (int, float))
    assert teleo["score"] > 0.0
    assert all(
        gap.get("dimension") in {
            "trust_economy",
            "protocolos",
            "evolucao",
            "scanners",
            "agentes",
            "mci_core",
            "integracoes",
            "infra_dados",
            "governanca",
            "razao_logica",
        }
        for gap in teleo.get("gaps", [])
    )


def test_ecosystem_evolutionary_has_no_absent_categories():
    from scanners import diagnostic_pipeline

    report = diagnostic_pipeline.run("ecosystem", domain="ecosystem")

    assert report["evolutionary"]["absent_categories"] == 0
