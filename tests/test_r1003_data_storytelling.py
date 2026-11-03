"""R1003 — Data storytelling auditável.

Contratos determinísticos, sem rede, sem LLM e sem relógio. Os testes cobrem
perfil, recomendação, gate de integridade, legenda/nota, SVG, manifesto e CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skills.data_storytelling import (
    audit_chart,
    audit_narrative,
    build_caption,
    build_manifest,
    caption_from_spec,
    profile_dataset,
    recommend_chart,
    render_svg,
    validate_caption,
    verify_manifest,
)
from skills.data_storytelling.util import DataStoryError, format_number_ptbr


# ---------------------------------------------------------------------------
# Fixtures e helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def rows():
    return [
        {"ano": 2020, "municipio_id": "A", "cobertura": 41.0, "regiao": "Norte",
         "observacao": "Registro descritivo municipal sem juízo de valor"},
        {"ano": 2021, "municipio_id": "B", "cobertura": 52.0, "regiao": "Norte",
         "observacao": "Registro descritivo municipal sem juízo de valor"},
        {"ano": 2022, "municipio_id": "C", "cobertura": 63.0, "regiao": "Sul",
         "observacao": "Registro descritivo municipal sem juízo de valor"},
        {"ano": 2023, "municipio_id": "D", "cobertura": 74.0, "regiao": "Sul",
         "observacao": "Registro descritivo municipal sem juízo de valor"},
    ]


def base_spec(**over):
    spec = {
        "chart": "bar",
        "title": "Cobertura acima de 80% dobra em quatro anos",
        "claim": "A cobertura passou de 41% para 83% entre 2020 e 2024.",
        "source": "IBGE (2024)",
        "note": (
            "Percentual de municípios com cobertura declarada; n = 120; "
            "período 2020–2024; sem imputação de ausentes."
        ),
        "legend": "Barras cinzas: 2020; barras azuis: 2024.",
        "alt_text": "Barras comparando 41% em 2020 e 83% em 2024.",
        "sample_n": 120,
        "y": {"kind": "numeric", "zero": True, "unit": "%", "scale": "linear"},
        "x": {"kind": "temporal"},
        "category_count": 2,
        "series_count": 1,
        "design": "observational",
        "sorting": "descending",
        "intent": "comparison",
        "decimals": 0,
        "data": {"n": 120},
    }
    spec.update(over)
    return spec


def codes(report):
    return {f["code"] for f in report["findings"]}


# ---------------------------------------------------------------------------
# Perfil de dados
# ---------------------------------------------------------------------------

def test_profile_infers_field_kinds(rows):
    profile = profile_dataset(rows)
    kinds = {f["name"]: f["kind"] for f in profile["fields"]}
    assert profile["n_rows"] == 4
    assert kinds["ano"] == "temporal"
    assert kinds["municipio_id"] == "identifier"
    assert kinds["cobertura"] == "numeric"
    assert kinds["regiao"] == "categorical"
    assert kinds["observacao"] == "text"


def test_profile_counts_missing_and_ragged_rows():
    rows = [
        {"a": 1, "b": None},
        {"a": 2, "b": "   "},
        {"a": 3},
    ]
    profile = profile_dataset(rows)
    fields = {f["name"]: f for f in profile["fields"]}
    assert profile["ragged_rows"] is True
    assert fields["b"]["missing"] == 3
    assert fields["b"]["non_null"] == 0


def test_profile_hash_is_deterministic_and_sensitive(rows):
    first = profile_dataset(rows)
    second = profile_dataset(list(rows))
    changed = profile_dataset(rows[:3])
    assert first["source_sha256"] == second["source_sha256"]
    assert first["source_sha256"] != changed["source_sha256"]
    assert len(first["source_sha256"]) == 64


def test_profile_mixed_field_is_explicit():
    profile = profile_dataset([{"x": 1}, {"x": "dois"}, {"x": 3}])
    field = {f["name"]: f for f in profile["fields"]}["x"]
    assert field["kind"] == "mixed"


@pytest.mark.parametrize(
    "bad, code",
    [
        ([], "empty_dataset"),
        ([["a", 1]], "invalid_row"),
        ([{"a": 1}] * 3, "row_limit_exceeded"),
    ],
)
def test_profile_fails_closed(bad, code):
    with pytest.raises(DataStoryError) as exc:
        profile_dataset(bad, max_rows=2)
    assert exc.value.code == code


def test_profile_treats_non_finite_as_missing():
    profile = profile_dataset([
        {"v": 1.0}, {"v": float("nan")}, {"v": float("inf")},
    ])
    field = {f["name"]: f for f in profile["fields"]}["v"]
    assert field["non_null"] == 1
    assert field["missing"] == 2
    assert len(profile["source_sha256"]) == 64


# ---------------------------------------------------------------------------
# Recomendação de codificação
# ---------------------------------------------------------------------------

def test_recommend_trend_prefers_line(rows):
    profile = profile_dataset(rows)
    result = recommend_chart(profile, intent="trend")
    assert result["recommendations"][0]["chart"] == "line"


def test_recommend_ranking_prefers_sorted_horizontal_bar(rows):
    profile = profile_dataset(rows)
    result = recommend_chart(profile, intent="ranking", emphasis="regiao")
    top = result["recommendations"][0]
    assert top["chart"] == "bar"
    assert top["orientation"] == "horizontal"


def test_recommend_composition_rejects_crowded_pie():
    rows = [{"categoria": f"C{i}", "valor": i + 1} for i in range(7)]
    profile = profile_dataset(rows)
    result = recommend_chart(profile, intent="composition")
    assert result["recommendations"][0]["chart"] == "stacked_bar"
    assert any(r["chart"] == "pie" for r in result["rejected"])


def test_recommend_composition_keeps_small_pie():
    rows = [{"categoria": f"C{i}", "valor": i + 1} for i in range(4)]
    profile = profile_dataset(rows)
    result = recommend_chart(profile, intent="composition")
    assert any(r["chart"] == "pie" for r in result["recommendations"])


def test_recommend_relationship_prefers_scatter():
    rows = [{"x": i, "y": i * 2} for i in range(10)]
    profile = profile_dataset(rows)
    result = recommend_chart(profile, intent="relationship")
    assert result["recommendations"][0]["chart"] == "scatter"


def test_recommend_without_compatible_field_fails_closed():
    profile = profile_dataset([{"nome": "A"}, {"nome": "B"}])
    with pytest.raises(DataStoryError) as exc:
        recommend_chart(profile, intent="trend")
    assert exc.value.code == "no_compatible_chart"


# ---------------------------------------------------------------------------
# Gate de auditoria do gráfico
# ---------------------------------------------------------------------------

def test_clean_spec_is_approved():
    report = audit_chart(base_spec())
    assert report["status"] == "approved"
    assert report["findings"] == []
    assert report["score"] == 100


def test_truncated_bar_axis_is_blocked():
    report = audit_chart(base_spec(y={"kind": "numeric", "zero": False, "unit": "%"}))
    assert report["status"] == "blocked"
    assert "TRUNCATED_AXIS" in codes(report)


def test_undeclared_baseline_requires_revision():
    report = audit_chart(base_spec(y={"kind": "numeric", "unit": "%"}))
    assert report["status"] == "revise"
    assert "UNDECLARED_BASELINE" in codes(report)


def test_dual_axis_and_three_d_are_blocked():
    dual = audit_chart(base_spec(dual_axis=True))
    three = audit_chart(base_spec(three_d=True))
    assert dual["status"] == "blocked" and "DUAL_AXIS" in codes(dual)
    assert three["status"] == "blocked" and "THREE_D" in codes(three)


def test_pie_overload_and_contract():
    crowded = audit_chart(base_spec(chart="pie", slice_count=7, part_to_whole=True))
    undeclared = audit_chart(base_spec(chart="pie", slice_count=4))
    assert "PIE_OVERLOAD" in codes(crowded)
    assert crowded["status"] == "blocked"
    assert "PIE_NOT_PART_TO_WHOLE" in codes(undeclared)


def test_causal_claim_is_blocked_only_in_observational_design():
    causal = "O programa causou queda de 12 pontos na evasão."
    observational = audit_chart(base_spec(claim=causal, design="observational"))
    experimental = audit_chart(base_spec(claim=causal, design="experimental"))
    assert "CAUSAL_CLAIM_OBSERVATIONAL" in codes(observational)
    assert observational["status"] == "blocked"
    assert "CAUSAL_CLAIM_OBSERVATIONAL" not in codes(experimental)


def test_missing_source_note_sample_and_units():
    source = audit_chart(base_spec(source=""))
    untraceable = audit_chart(base_spec(source="IBGE"))
    note = audit_chart(base_spec(note=""))
    thin = audit_chart(base_spec(note="Ver dados."))
    sample = audit_chart(base_spec(sample_n=None))
    units = audit_chart(base_spec(y={"kind": "numeric", "zero": True}))
    assert "MISSING_SOURCE" in codes(source) and source["status"] == "blocked"
    assert "SOURCE_NOT_TRACEABLE" in codes(untraceable)
    assert "MISSING_NOTE" in codes(note)
    assert "NOTE_TOO_THIN" in codes(thin)
    assert "MISSING_SAMPLE_SIZE" in codes(sample)
    assert "MISSING_UNITS" in codes(units)


def test_uncertainty_and_overplotting_are_flagged():
    uncertain = audit_chart(base_spec(estimate=True,
                                      uncertainty={"displayed": False}))
    shown = audit_chart(base_spec(estimate=True,
                                  uncertainty={"displayed": True, "kind": "IC 95%"}))
    scatter = audit_chart(base_spec(chart="scatter", sample_n=1200,
                                    data={"n": 1200}, category_count=0))
    controlled = audit_chart(base_spec(chart="scatter", sample_n=1200,
                                       data={"n": 1200}, overplotting_control=True))
    assert "MISSING_UNCERTAINTY" in codes(uncertain)
    assert "MISSING_UNCERTAINTY" not in codes(shown)
    assert "OVERPLOTTING" in codes(scatter)
    assert "OVERPLOTTING" not in codes(controlled)


def test_color_and_title_contracts():
    color = audit_chart(base_spec(color_only=True, direct_labels=False))
    safe = audit_chart(base_spec(color_only=True, direct_labels=True,
                                 colorblind_safe=True))
    title = audit_chart(base_spec(title="Gráfico de barras"))
    missing = audit_chart(base_spec(title=""))
    alt = audit_chart(base_spec(alt_text=""))
    assert "COLOR_ONLY_ENCODING" in codes(color)
    assert "COLOR_ONLY_ENCODING" not in codes(safe)
    assert "TITLE_NOT_MESSAGE" in codes(title)
    assert "MISSING_TITLE" in codes(missing) and missing["status"] == "blocked"
    assert "NO_ALT_TEXT" in codes(alt)


def test_unknown_chart_fails_closed():
    with pytest.raises(DataStoryError) as exc:
        audit_chart(base_spec(chart="radar"))
    assert exc.value.code == "unsupported_chart"


def test_audit_is_deterministic_and_does_not_mutate_the_spec():
    spec = base_spec()
    before = json.dumps(spec, ensure_ascii=False, sort_keys=True)
    first = audit_chart(spec)
    second = audit_chart(spec)
    assert first == second
    assert json.dumps(spec, ensure_ascii=False, sort_keys=True) == before


# ---------------------------------------------------------------------------
# Narrativa
# ---------------------------------------------------------------------------

def test_narrative_causal_and_absolute_claims():
    causal = audit_narrative("O programa causou queda de 12 pontos.",
                             design="observational")
    experimental = audit_narrative("O programa causou queda de 12 pontos.",
                                   design="experimental")
    absolute = audit_narrative("A taxa sempre foi maior.", scope_declared=False)
    scoped = audit_narrative("A taxa sempre foi maior.", scope_declared=True)
    assert "CAUSAL_CLAIM_OBSERVATIONAL" in codes(causal)
    assert "CAUSAL_CLAIM_OBSERVATIONAL" not in codes(experimental)
    assert "ABSOLUTE_CLAIM" in codes(absolute)
    assert "ABSOLUTE_CLAIM" not in codes(scoped)


def test_narrative_percent_hype_and_limit():
    percent = audit_narrative("Cresceu 30%.", base_declared=False)
    based = audit_narrative("Cresceu 30% sobre 1.200 casos.", base_declared=True)
    hype = audit_narrative("A arrecadação explodiu.")
    limited = audit_narrative(
        "A cobertura passou de 41% para 83% entre 2020 e 2024, segundo o IBGE "
        "(2024). O desenho descritivo não permite inferir causalidade.",
        design="descriptive",
        base_declared=True,
    )
    assert "PERCENT_WITHOUT_BASE" in codes(percent)
    assert "PERCENT_WITHOUT_BASE" not in codes(based)
    assert "HYPE_WITHOUT_NUMBER" in codes(hype)
    assert limited["status"] == "approved"


# ---------------------------------------------------------------------------
# Legenda e nota
# ---------------------------------------------------------------------------

def test_caption_builds_four_layers():
    caption = build_caption(
        number=1,
        title="Cobertura dobra em quatro anos.",
        kind="Gráfico",
        source="IBGE (2024)",
        note="Percentual de municípios com cobertura declarada",
        legend="Barras cinzas: 2020; barras azuis: 2024.",
        n=120,
        period="2020–2024",
        method="Comparação de proporções",
    )
    assert caption["label"] == "Gráfico 1 – Cobertura dobra em quatro anos"
    assert caption["fonte"].startswith("Fonte: IBGE (2024)")
    assert "n = 120" in caption["nota"]
    assert "Período: 2020–2024" in caption["nota"]
    assert "Método: Comparação de proporções" in caption["nota"]
    assert caption["markdown"].count("**") == 2
    assert validate_caption(caption)["ok"] is True
    assert len(caption["sha256"]) == 64


def test_caption_without_legend_omits_the_layer():
    caption = build_caption(number="2A", title="Título com mensagem clara",
                             source="IBGE (2024)",
                             note="Nota com n = 10 e método declarado")
    assert caption["label"].startswith("Figura 2A – ")
    assert "Legenda:" not in caption["markdown"]
    assert caption["parts"]["legend"] is False


def test_caption_validation_rejects_placeholders_and_untraceable_source():
    caption = build_caption(number=3, title="Título com mensagem clara",
                             source="IBGE",
                             note="Nota com n = 10 e método declarado")
    validation = validate_caption(caption)
    assert validation["ok"] is False
    assert any(e["code"] == "UNTRACEABLE_SOURCE" for e in validation["errors"])

    dirty = dict(caption)
    dirty["title"] = "TODO"
    assert any(e["code"] == "PLACEHOLDER_TEXT"
               for e in validate_caption(dirty)["errors"])


def test_caption_without_number_fails_validation():
    caption = build_caption(number=4, title="Título com mensagem clara",
                             source="IBGE (2024)",
                             note="Percentual sem algarismo")
    assert any(e["code"] == "NOTE_WITHOUT_NUMBER"
               for e in validate_caption(caption)["errors"])


def test_caption_formats_elaboration_prefix():
    caption = build_caption(
        number=1, title="Título com mensagem clara", source="IBGE (2024)",
        note="Nota com n = 10 e método declarado",
        elaboration="Elaboração própria com base em",
    )
    assert caption["fonte"] == "Fonte: Elaboração própria com base em IBGE (2024)."


def test_caption_includes_unit_when_legend_is_absent():
    caption = build_caption(
        number=8, title="Título com mensagem clara", source="IBGE (2024)",
        note="Nota com n = 10 e método declarado", unit="%",
    )
    assert "Unidade: %" in caption["nota"]
    assert caption["parts"]["legend"] is False


def test_caption_warns_when_note_lacks_method():
    caption = build_caption(
        number=9, title="Título com mensagem clara", source="IBGE (2024)",
        note="10 registros",
    )
    validation = validate_caption(caption)
    assert validation["ok"] is True
    assert any(w["code"] == "NOTE_WITHOUT_METHOD"
               for w in validation["warnings"])


def test_caption_escapes_html():
    caption = build_caption(number=5, title="Cobertura < 80% & risco",
                             source="IBGE (2024)",
                             note="Nota com n = 10 e método declarado")
    assert "<script>" not in caption["html"]
    assert "&lt;" in caption["html"]
    assert "&amp;" in caption["html"]


def test_caption_rejects_invalid_number_and_long_title():
    with pytest.raises(DataStoryError) as exc:
        build_caption(number=0, title="Título válido", source="IBGE (2024)",
                      note="Nota com n = 1")
    assert exc.value.code == "invalid_number"
    with pytest.raises(DataStoryError) as exc:
        build_caption(number=1, title="x" * 141, source="IBGE (2024)",
                      note="Nota com n = 1")
    assert exc.value.code == "title_too_long"


def test_caption_from_spec_pulls_chart_contract():
    spec = base_spec()
    caption = caption_from_spec(spec, number=6, kind="Gráfico")
    assert caption["title"] == spec["title"]
    assert "n = 120" in caption["nota"]
    assert validate_caption(caption)["ok"] is True
    with pytest.raises(DataStoryError) as exc:
        caption_from_spec(base_spec(note=""), number=7)
    assert exc.value.code == "missing_note"


# ---------------------------------------------------------------------------
# SVG determinístico
# ---------------------------------------------------------------------------

def bar_spec(**over):
    spec = {
        "chart": "bar",
        "title": "Cobertura < 80% em duas regiões",
        "subtitle": "Percentual de municípios, 2020–2024",
        "alt_text": "Barras verticais de 41% e 83%.",
        "source": "IBGE (2024)",
        "sample_n": 120,
        "legend": "Barras cinzas: 2020; barras azuis: 2024.",
        "data": [{"label": "2020", "value": 41}, {"label": "2024", "value": 83}],
        "y": {"zero": True, "unit": "%"},
    }
    spec.update(over)
    return spec


def test_svg_is_valid_deterministic_and_accessible():
    first = render_svg(bar_spec())
    second = render_svg(bar_spec())
    root = ET.fromstring(first)
    assert first == second
    assert root.tag.endswith("svg")
    assert root.attrib["aria-labelledby"]
    assert "Cobertura < 80% em duas regiões" in "".join(root.itertext())
    assert "41%" in first and "83%" in first
    assert "spec_sha256" in first


def test_svg_refuses_truncated_bar_and_unsupported_chart():
    with pytest.raises(DataStoryError) as exc:
        render_svg(bar_spec(y={"zero": False, "unit": "%"}))
    assert exc.value.code == "bar_requires_zero_baseline"
    with pytest.raises(DataStoryError) as exc:
        render_svg(bar_spec(chart="pie"))
    assert exc.value.code == "unsupported_render"
    with pytest.raises(DataStoryError) as exc:
        render_svg(bar_spec(title=""))
    assert exc.value.code == "missing_title"


def test_svg_line_renders_points():
    spec = {
        "chart": "line",
        "title": "Série anual de cobertura",
        "alt_text": "Linha ascendente de 2020 a 2023.",
        "source": "IBGE (2024)",
        "sample_n": 4,
        "data": [{"x": 2020, "y": 41}, {"x": 2021, "y": 52},
                 {"x": 2022, "y": 63}, {"x": 2023, "y": 74}],
        "y": {"unit": "%"},
    }
    svg = render_svg(spec)
    assert svg.count("<circle") == 4
    assert "Série anual de cobertura" in svg


def test_number_format_ptbr():
    assert format_number_ptbr(1234.5, 1) == "1.234,5"
    assert format_number_ptbr(41, 0) == "41"
    assert format_number_ptbr(0.125, 3) == "0,125"


# ---------------------------------------------------------------------------
# Manifesto
# ---------------------------------------------------------------------------

def test_manifest_is_deterministic_and_detects_tampering():
    artifacts = {"legenda.md": "# Legenda", "grafico.svg": "<svg/>"}
    first = build_manifest(artifacts)
    second = build_manifest(dict(reversed(list(artifacts.items()))))
    assert first == second
    assert [a["name"] for a in first["artifacts"]] == ["grafico.svg", "legenda.md"]
    ok = verify_manifest(first, artifacts)
    assert ok["ok"] is True
    tampered = dict(artifacts, **{"grafico.svg": "<svg>adulterado</svg>"})
    bad = verify_manifest(first, tampered)
    assert bad["ok"] is False
    assert bad["mismatches"][0]["name"] == "grafico.svg"
    missing = verify_manifest(first, {"legenda.md": "# Legenda"})
    assert missing["ok"] is False and missing["missing"] == ["grafico.svg"]


def test_manifest_normalizes_non_string_names():
    manifest = build_manifest({1: "a", 2: b"b"})
    assert [item["name"] for item in manifest["artifacts"]] == ["1", "2"]


# ---------------------------------------------------------------------------
# CLI fim a fim (prova física)
# ---------------------------------------------------------------------------

def test_cli_demo_generates_verifiable_dossier(tmp_path):
    out = tmp_path / "dossie"
    result = subprocess.run(
        [sys.executable, "-m", "skills.data_storytelling", "demo", "--out", str(out)],
        capture_output=True, text=True, timeout=60, cwd=Path.cwd(),
    )
    assert result.returncode == 0, result.stderr
    expected = {"dossie.json", "grafico.svg", "legenda.md", "auditoria.json",
                "MANIFESTO.json"}
    assert expected.issubset({p.name for p in out.iterdir()})
    manifest = json.loads((out / "MANIFESTO.json").read_text(encoding="utf-8"))
    payload = {p.name: p.read_bytes() for p in out.iterdir()
               if p.name != "MANIFESTO.json"}
    assert verify_manifest(manifest, payload)["ok"] is True
    audit = json.loads((out / "auditoria.json").read_text(encoding="utf-8"))
    assert audit["status"] == "approved"
    caption = (out / "legenda.md").read_text(encoding="utf-8")
    assert "Fonte:" in caption and "Nota:" in caption
