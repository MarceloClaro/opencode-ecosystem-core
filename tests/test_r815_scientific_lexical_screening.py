"""R815: contraprovas dos bugs lexicais, sem inferir qualidade científica."""

import pytest
import time

from scanners.scientific_reasoning_scanner import ScientificReasoningScanner


@pytest.fixture
def scanner():
    return ScientificReasoningScanner()


PT = (
    "A hipótese é falsificável. Se há aumento, então a métrica mensurável reduz. "
    "Realizamos um experimento com grupo de controle, amostragem aleatória, "
    "intervalo de confiança, variável independente, baseline e reprodutibilidade."
)
EN = (
    "The hypothesis is falsifiable. If there is an increase, then the measurable metric decreases. "
    "We conducted an experiment with a control group, random sampling, "
    "a confidence interval, an independent variable, a baseline and reproducibility."
)


def test_equivalent_pt_en_have_same_scores_and_positive_concepts(scanner):
    pt, en = scanner.scan_text(PT), scanner.scan_text(EN)
    for key in ("sri_score", "falsifiability_score", "methodology_score"):
        assert pt[key] == en[key] == 100.0
    assert pt["matched_concepts"] == en["matched_concepts"]


@pytest.mark.parametrize("word", ["sem", "segundo", "sempre", "seis", "sessão", "desejo", "else", "ifelse", "testemunho"])
def test_substrings_do_not_create_falsifiability_or_testability(scanner, word):
    assert scanner.scan_text(word)["falsifiability_score"] == 0.0
    assert scanner.evaluate_hypothesis(word)["is_testable"] is False


@pytest.mark.parametrize("text", [
    "Não há grupo de controle. Não houve amostragem. Não existe baseline.",
    "No control group was used. There was no sampling. No baseline was available.",
    "O grupo controle não foi utilizado. A amostragem não foi realizada.",
    "The control group was not used. Sampling was not performed.",
    "Sem grupo de controle, sem amostragem e sem reprodutibilidade.",
    "Without a control group, without sampling and without reproducibility.",
    "**Grupo de controle.** Nenhum grupo de controle se aplica.",
    "**Control group.** No control group applies.",
])
def test_local_negation_and_heading_do_not_count_as_method(scanner, text):
    assert scanner.scan_text(text)["methodology_score"] == 0.0


@pytest.mark.parametrize("text", [
    "Não há grupo de controle, mas realizamos amostragem.",
    "There is no control group, but we performed sampling.",
])
def test_contrast_limits_negation_scope(scanner, text):
    result = scanner.scan_text(text)
    assert result["matched_concepts"]["methodology"] == ["sampling"]
    assert result["negated_concepts"]["methodology"] == ["design"]
    assert result["methodology_score"] == pytest.approx(16.67)


@pytest.mark.parametrize("text", [
    "Não apenas amostragem, mas também baseline.",
    "Not only sampling but also baseline.",
])
def test_additive_not_only_is_not_absence(scanner, text):
    assert scanner.scan_text(text)["methodology_score"] == pytest.approx(33.33)


def test_four_concepts_do_not_saturate_and_synonyms_do_not_add_credit(scanner):
    result = scanner.scan_text("Grupo de controle. Amostragem. P-valor. Baseline.")
    assert result["methodology_score"] == pytest.approx(66.67)
    aliases = scanner.scan_text("P-valor, p-value, confidence interval, intervalo de confiança.")
    assert aliases["methodology_score"] == pytest.approx(16.67)


@pytest.mark.parametrize("text", ["", "  \n\t", "Texto administrativo sem conteúdo de pesquisa."])
def test_empty_and_unrelated_text_have_zero_without_quality_verdict(scanner, text):
    result = scanner.scan_text(text)
    assert result["sri_score"] == result["methodology_score"] == result["falsifiability_score"] == 0.0
    assert result["status"] == "low_rigor"
    assert result["scientific_quality_assessed"] is False


@pytest.mark.parametrize("text", [None, False, 12, [], {}])
def test_non_text_rejected_explicitly(scanner, text):
    with pytest.raises(ValueError, match="texto"):
        scanner.scan_text(text)
    with pytest.raises(ValueError, match="texto"):
        scanner.evaluate_hypothesis(text)


@pytest.mark.parametrize("text", [
    "O método prova que o modelo sempre funciona. A correlação implica causalidade. Obviamente.",
    "The method proves that the model always works. Correlation implies causality. Obviously.",
])
def test_equivalent_categorical_claims_flag_four_categories(scanner, text):
    assert len(scanner.scan_text(text)["detected_fallacies"]) == 4


@pytest.mark.parametrize("text", [
    "Isto não prova que o modelo é válido. A correlação não implica causalidade.",
    "This does not prove that the model is valid. Correlation does not imply causality.",
])
def test_explicit_negation_of_categorical_claim_is_not_fallacy(scanner, text):
    assert scanner.scan_text(text)["detected_fallacies"] == []


@pytest.mark.parametrize("text", [PT, EN])
def test_high_lexical_score_is_not_scientific_quality_assessment(scanner, text):
    result = scanner.scan_text(text)
    assert result["status"] == "high_rigor"  # compatibilidade da faixa legada
    assert result["score_kind"] == "lexical_heuristic"
    assert result["scientific_quality_assessed"] is False
    assert result["risk_of_bias_assessed"] is False
    assert any("PROBAST" in item for item in result["limitations"])
    assert all("bem fundamentado" not in item for item in result["recommendations"])


@pytest.mark.parametrize("text", [
    "Se aumentarmos a taxa, então o tempo reduz.",
    "If we increase the rate, then time decreases.",
])
def test_conditional_prediction_is_only_lexical_testability_indicator(scanner, text):
    result = scanner.evaluate_hypothesis(text)
    assert result["is_testable"] is True
    assert result["status"] == "valid_hypothesis"
    assert result["score_kind"] == "lexical_heuristic"
    assert result["scientific_quality_assessed"] is False


@pytest.mark.parametrize("text", ["Se houver tempo.", "If time is available.", "Então teremos tempo.", "Then we have time."])
def test_one_connector_alone_does_not_establish_conditional_prediction(scanner, text):
    assert scanner.evaluate_hypothesis(text)["is_testable"] is False


def test_unicode_accents_and_dash_variants_preserve_scores(scanner):
    accented = scanner.scan_text("Hipótese falsificável. P–valor. Variável independente.")
    plain = scanner.scan_text("Hipotese falsificavel. P-valor. Variavel independente.")
    assert accented["sri_score"] == plain["sri_score"]


def test_negated_other_method_does_not_cancel_positive_method(scanner):
    result = scanner.scan_text("We used a control group, not a sampling procedure.")
    assert result["matched_concepts"]["methodology"] == ["design"]
    assert result["negated_concepts"]["methodology"] == ["sampling"]


@pytest.mark.parametrize("text", [
    "Se não usarmos baseline, então o erro aumenta.",
    "If we do not use a baseline, then the error increases.",
])
def test_negative_premise_still_contains_conditional_prediction(scanner, text):
    result = scanner.evaluate_hypothesis(text)
    assert result["is_testable"] is True
    assert result["scientific_quality_assessed"] is False


@pytest.mark.parametrize("variant", ["async", "sync"])
@pytest.mark.parametrize("tool_name", ["scientific_reasoning_scan", "super_rigor_audit"])
def test_mcp_advertises_lexical_scope_without_scientific_quality_promise(variant, tool_name):
    import asyncio
    from scanners.scanners_mcp_server import ScannersMcpServer, list_tools

    descriptions = (
        {tool.name: tool.description for tool in asyncio.run(list_tools())}
        if variant == "async" else
        {name: metadata["description"] for name, metadata in ScannersMcpServer().get_tools().items()}
    )
    description = descriptions[tool_name].lower()
    assert "triagem lexical" in description
    assert "não avalia qualidade científica" in description


@pytest.mark.parametrize("variant", ["async", "sync"])
@pytest.mark.parametrize("tool_name", ["scientific_reasoning_scan", "super_rigor_audit"])
def test_mcp_retains_scientific_limits_in_real_result(variant, tool_name):
    import asyncio
    import json
    from scanners.scanners_mcp_server import ScannersMcpServer, call_tool

    if variant == "async":
        result = asyncio.run(call_tool(tool_name, {"text": PT}))
        assert result.isError is False
        payload = json.loads(result.content[0].text)
    else:
        payload = ScannersMcpServer().call_tool(tool_name, {"text": PT})
    assert payload["ok"] is True
    report = payload["result"]
    if tool_name == "super_rigor_audit":
        report = report["scientific_rigor"]
    assert report["score_kind"] == "lexical_heuristic"
    assert report["scientific_quality_assessed"] is False
    assert report["risk_of_bias_assessed"] is False
    assert report["limitations"]


@pytest.mark.parametrize("text", [
    "Nem grupo de controle nem amostragem.",
    "Neither a control group nor sampling was used.",
    "We used neither a control group nor sampling.",
])
def test_coordinated_negation_is_recorded_without_method_credit(scanner, text):
    result = scanner.scan_text(text)
    assert result["matched_concepts"]["methodology"] == []
    assert result["negated_concepts"]["methodology"] == ["design", "sampling"]
    assert result["methodology_score"] == 0


def test_repeated_28800_character_input_has_bounded_context_work(scanner):
    text = "baseline " * 3200
    started = time.perf_counter()
    result = scanner.scan_text(text)
    elapsed = time.perf_counter() - started
    assert result["matched_concepts"]["methodology"] == ["baseline"]
    assert result["methodology_score"] == pytest.approx(16.67)
    assert elapsed < 2.0, f"28800 caracteres demandaram {elapsed:.3f}s; contexto deve ser indexado."


@pytest.mark.parametrize("variant", ["async", "sync"])
@pytest.mark.parametrize("tool_name", ["scientific_reasoning_scan", "super_rigor_audit"])
def test_mcp_rejects_oversized_scientific_text_before_scanners(monkeypatch, variant, tool_name):
    import asyncio
    from scanners import scanners_mcp_server as server
    def forbidden(*args, **kwargs):
        raise AssertionError("O excesso de entrada não pode iniciar scanners.")
    monkeypatch.setattr(server.scientific_reasoning_scanner, "scan_text", forbidden)
    monkeypatch.setattr(server.super_rigor_pipeline, "audit_production", forbidden)
    # O contrato exige um limite público e finito, presente no schema MCP.
    limit = server.MAX_SCIENTIFIC_TEXT_CHARS
    assert type(limit) is int and 28800 < limit <= 1_000_000
    assert server.TOOL_SCHEMAS[tool_name]["properties"]["text"]["maxLength"] == limit
    args = {"text": "a" * (limit + 1)}
    if variant == "async":
        result = asyncio.run(server.call_tool(tool_name, args))
        assert result.isError is True
        assert "maxLength" in result.content[0].text
    else:
        result = server.ScannersMcpServer().call_tool(tool_name, args)
        assert result["ok"] is False
        assert "maxLength" in result["error"]


@pytest.mark.parametrize("tool_name", ["scientific_reasoning_scan", "super_rigor_audit"])
def test_mcp_schema_accepts_exact_scientific_text_limit(tool_name):
    from scanners import scanners_mcp_server as server
    from integrations.mcp_validation import validate_arguments
    limit = server.MAX_SCIENTIFIC_TEXT_CHARS
    result = validate_arguments(tool_name, {"text": "a" * limit}, server.TOOL_SCHEMAS[tool_name])
    assert result["valid"]


@pytest.mark.parametrize("tool_name", ["scientific_reasoning_scan", "super_rigor_audit"])
def test_registered_mcp_handler_rejects_excess_without_echoing_input(tool_name):
    import asyncio
    from mcp.types import CallToolRequest, CallToolRequestParams
    from scanners import scanners_mcp_server as server
    sentinel = "R815_OVERSIZED_INPUT_SENTINEL"
    text = sentinel + "a" * server.MAX_SCIENTIFIC_TEXT_CHARS
    request = CallToolRequest(params=CallToolRequestParams(name=tool_name, arguments={"text": text}))
    result = asyncio.run(server.app.request_handlers[CallToolRequest](request)).root
    assert result.isError is True
    message = result.content[0].text
    if sentinel in message or len(message) > 500:
        pytest.fail("A rejeição MCP deve explicar maxLength sem ecoar a entrada nem ampliar a resposta.")
    assert "maxLength" in message
