"""R990: corpus sintético de software, não validação científica externa."""
import importlib
import json

import pytest

from scanners.scientific_reasoning_scanner import ScientificReasoningScanner


def evolution():
    assert importlib.util.find_spec("scanners.scientific_evolution"), "Evolução R990 ausente"
    return importlib.import_module("scanners.scientific_evolution")


def corpus():
    examples = [
        ("dev", "O método sempre funciona.", True),
        ("dev", "Obviamente esta amostra é suficiente.", True),
        ("dev", 'Exemplo inadequado: "correlação implica causalidade".', False),
        ("dev", "Não há evidência conclusiva nesta amostra.", False),
        ("holdout", "Our approach always works across domains.", True),
        ("holdout", "The test proves that all populations benefit.", True),
        ("holdout", 'The critic quotes “obviously this is certain”.', False),
        ("holdout", "The association does not establish a cause.", False),
    ]
    return [{"id": f"case-{i}", "group": f"group-{i}", "split": split,
             "text": text, "label": label} for i, (split, text, label) in enumerate(examples)]


def test_contextual_findings_preserve_quotes_and_offsets():
    text = 'Não prova que funciona. O autor cita “sempre funciona”. Obviamente é preciso revisar.'
    scan = ScientificReasoningScanner().scan_text(text)
    assert "triage" in scan
    findings = scan["triage"]["findings"]
    assert {f["context"] for f in findings} == {"negated", "quoted", "asserted"}
    normalized = ScientificReasoningScanner._normalize(text)
    for finding in findings:
        assert normalized[finding["start"]:finding["end"]] == finding["match"]
        assert finding["offset_basis"] == "normalized_text"
    assert len(scan["triage"]["input_sha256"]) == 64


def test_empty_abstention_and_no_promotion_even_at_high_score():
    scanner = ScientificReasoningScanner()
    assert "triage" in scanner.scan_text("   ")
    assert scanner.scan_text("   ")["triage"]["status"] == "abstained"
    rich = scanner.scan_text("Hipótese falsificável. Se há teste então reduz a métrica. Grupo de controle. Amostragem. Baseline. Reprodutibilidade. P-valor. Preditor.")
    assert rich["authority"]["scientific_certification"] is False
    assert rich["authority"]["publication_allowed"] is False
    assert rich["score_kind"] == "lexical_heuristic"


def test_direct_scanner_rejects_excess():
    assert hasattr(ScientificReasoningScanner, "MAX_TEXT_CHARS")
    with pytest.raises(ValueError):
        ScientificReasoningScanner().scan_text("a" * 1_000_001)


def test_super_pipeline_declares_operational_limits(monkeypatch):
    from scanners import pipeline
    monkeypatch.setattr(pipeline.diagnostic_pipeline, "run", lambda **kw: {
        "noological": {"total_coverage_pct": 100}, "teleological": {"total_gaps": 0}})
    result = pipeline.SuperRigorPipeline().audit_production("Hipótese, teste, baseline.")
    assert "authority" in result
    assert result["authority"]["scientific_certification"] is False
    assert result["authority"]["publication_allowed"] is False
    assert result["human_review_required"] is True


def test_evolution_computes_real_confusion_matrices_without_promotion():
    result = evolution().evaluate_candidates(corpus())
    assert result["selected_on_development"] == "contextual"
    assert result["status"] == "candidate_recommended"
    assert result["metrics"]["contextual"]["holdout"] == {
        "tp": 2, "fp": 0, "tn": 2, "fn": 0, "n": 4,
        "precision": 1.0, "recall": 1.0, "balanced_accuracy": 1.0}
    assert result["promoted"] is False and result["authority_changed"] is False
    assert result["human_review_required"] is True
    assert len(result["corpus_sha256"]) == 64 and result["external_validation"] is False
    assert result["proposed_tasks"] and result["agents_executed"] is False
    assert "holdout_delta" in result
    assert result["holdout_delta"] == {"fp": -1, "fn": 0, "balanced_accuracy": 0.25}
    assert result["holdout_improvement"] is True


def test_no_positive_predictions_is_not_perfect_precision():
    metrics = evolution().confusion_metrics([True, False], [False, False])
    assert metrics["precision"] is None and metrics["recall"] == 0.0
    assert metrics["balanced_accuracy"] == 0.5


@pytest.mark.parametrize("mutation", ["text_leak", "group_leak", "bad_label", "empty", "single_class", "unknown_split"])
def test_invalid_corpus_fails_closed(mutation):
    rows = corpus()
    if mutation == "text_leak": rows[4]["text"] = rows[0]["text"]
    elif mutation == "group_leak": rows[4]["group"] = rows[0]["group"]
    elif mutation == "bad_label": rows[0]["label"] = "true"
    elif mutation == "empty": rows = []
    elif mutation == "single_class":
        for row in rows: row["label"] = False
    elif mutation == "unknown_split": rows[0]["split"] = "train"
    with pytest.raises(ValueError): evolution().evaluate_candidates(rows)


def test_holdout_regression_does_not_select_another_candidate():
    rows = corpus()
    # A citação é um overclaim endossado neste caso hipotético: contexto lexical não resolve tudo.
    rows[6]["label"] = True
    result = evolution().evaluate_candidates(rows)
    assert result["selected_on_development"] == "contextual"
    assert result["status"] == "regression_blocked" and not result["promoted"]


def test_tie_is_not_an_evolution():
    rows = corpus()
    rows[2]["text"] = "Amostra pequena com limitação reconhecida."
    rows[6]["text"] = "Results remain uncertain in this study."
    result = evolution().evaluate_candidates(rows)
    assert result["status"] == "no_improvement" and result["promoted"] is False


def test_cli_calibration_does_not_use_fallback(monkeypatch, capsys):
    from marceloclaro import scientific_lab as cli
    assert "scanner-evolve" in cli.HELP
    monkeypatch.setattr(cli, "dispatch", lambda *a: pytest.fail("Fallback externo"))
    assert cli.main(["scanner-evolve", "--corpus-json", json.dumps(corpus())]) == 0
    assert json.loads(capsys.readouterr().out)["promoted"] is False
