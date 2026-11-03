"""R934: contrato do protocolo pré-análise ccRCC/TCGA-KIRC; sem acesso a dados."""
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "artigos/bio/protocolo_ccrcc_tcga_kirc_r934.md"


def protocol() -> str:
    assert PROTOCOL.is_file(), "Protocolo pré-análise R934 ainda não entregue"
    return PROTOCOL.read_text(encoding="utf-8")


def test_question_and_no_results_are_explicit():
    text = protocol()
    for marker in (
        "Pergunta primária",
        "sobrevida global",
        "TCGA-KIRC",
        "Objetivo secundário",
        "resultados não verificados",
        "nenhum resultado observado",
    ):
        assert marker.casefold() in text.casefold()


def test_gdc_scope_is_open_access_and_manifested():
    text = protocol().casefold()
    for marker in (
        "tcga-kirc",
        "open-access",
        "controlled-access",
        "file uuid",
        "checksum",
        "manifesto",
        "inventário de metadados",
    ):
        assert marker in text, f"missing GDC manifest contract marker: {marker}"
    assert "controlled-access será baixado" not in text


def test_gdc_file_inventory_query_is_reproducible_and_metadata_only():
    text = protocol().casefold()
    for marker in (
        "gdc /files endpoint",
        "cases.project.project_id = tcga-kirc",
        "files.data_category = transcriptome profiling",
        "files.data_type = gene expression quantification",
        "files.analysis.workflow_type = star - counts",
        "files.access = open",
        "files.state = released",
        "file_id",
        "file_name",
        "file_size",
        "md5sum",
        "analysis.workflow_type",
        "analysis.workflow_version",
        "data_release",
        "version",
        "version é atributo por file_id, não exige homogeneidade entre arquivos",
        "workflow_version uniforme",
        "data_release por arquivo",
        "latest_release",
        "não exigir igualdade textual de",
        "interseção das listas latest_release",
        "cases.project.project_id",
        "cases.case_id",
        "cases.submitter_id",
        "cases.samples.sample_type",
        "cases.samples.sample_id",
        "cases.samples.submitter_id",
        "cases.samples.portions.analytes.aliquots.aliquot_id",
        "cases.samples.portions.analytes.aliquots.submitter_id",
        "aliquot_id é uuid gdc",
        "aliquot submitter_id é barcode",
        "primary tumor",
        "solid tissue normal",
        "não usar filtro literal 01/11",
        "uma linha por file_id",
        "metadados associados a sample_id/aliquot_id",
        "múltiplos sample_id",
        "tamanho agregado soma file_id únicos",
        "data.pagination.total igual a file_id únicos",
        "exatamente um sample_id e um aliquot_id por data file",
        "múltiplos aliquot_id",
        "sample_id ou barcode de aliquota ausente",
        "versão ativa do file",
        "tamanho ou md5sum ausente pausa",
        "nenhum download sem access=open e state=released",
        "md5sum do gdc",
        "sha-256 local pós-download",
        "consulta metadata-only de coorte foi executada",
        "614 file ids únicos",
        "pagination até data.pagination.total",
        "somente metadata; sem file content",
        "saída outputs/core-r934/gdc-manifest.json",
        "https://docs.gdc.cancer.gov/api/users_guide/search_and_retrieval/",
        "https://api.gdc.cancer.gov/files/_mapping",
        "https://api.gdc.cancer.gov/cases/_mapping",
    ):
        assert marker in text, f"missing GDC inventory marker: {marker}"
    manifest_path = ROOT / "outputs/core-r934/gdc-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    authorized_outlier_id = "2b0106c5-7e32-423b-957f-06c9f2e7751b"
    exclusions = manifest.get("authorized_exclusions", [])
    assert any(item.get("file_id") == authorized_outlier_id for item in exclusions)
    assert any(
        item.get("file_id") == authorized_outlier_id
        and "workflow" in item.get("rationale", "").casefold()
        and "variação biológica" in item.get("rationale", "").casefold()
        for item in exclusions
    )
    assert manifest.get("common_data_releases")
    assert manifest.get("selected_common_data_release") in manifest["common_data_releases"]
    assert manifest.get("common_data_releases")
    assert manifest.get("selected_common_data_release") in manifest["common_data_releases"]


def test_official_schema_audit_receipt_is_bounded():
    path = ROOT / "outputs/core-r934/gdc-schema-audit.json"
    assert path.is_file(), "Registro delimitado da conferência do schema GDC não foi gravado"
    import json
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["scope"] == "api_schema_only"
    assert receipt["cohort_query_sent"] is False
    assert receipt["file_content_downloaded"] is False
    assert receipt["controlled_accessed"] is False
    assert receipt["raw_source_body_saved"] is False
    assert receipt["external_source_hashes"] == "not_captured"
    assert "https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/" in receipt["sources"]
    assert "https://api.gdc.cancer.gov/files/_mapping" in receipt["sources"]
    assert "https://api.gdc.cancer.gov/cases/_mapping" in receipt["sources"]
    assert set(receipt["confirmed_file_fields"]) >= {
        "files.access", "files.state", "files.file_size", "files.md5sum",
        "files.analysis.workflow_type", "files.analysis.workflow_version",
        "cases.samples.sample_type", "cases.samples.sample_id",
        "cases.samples.portions.analytes.aliquots.aliquot_id",
        "cases.samples.portions.analytes.aliquots.submitter_id",
    }
    assert receipt["schema_observations"]["pagination_total_field"] == "data.pagination.total"
    assert receipt["schema_observations"]["files_versions_endpoint"] == "/files/versions/{UUID[,..]}"
    assert "latest_release" in receipt["schema_observations"]
    assert "intersect" in receipt["schema_observations"]["release_compatibility_rule"].casefold()
    assert receipt["schema_observations"]["files_versions_endpoint"] == "/files/versions/{UUID[,..]}"
    assert "latest_release" in receipt["schema_observations"]
    assert "intersect" in receipt["schema_observations"]["release_compatibility_rule"].casefold()


def test_patient_level_lockbox_and_nested_selection():
    text = protocol().casefold()
    for marker in (
        "nível de paciente",
        "holdout",
        "70%",
        "30%",
        "nested",
        "validação cruzada aninhada",
        "uma vez",
        "congelado",
    ):
        assert marker in text
    assert "seleção univariada antes da validação cruzada" not in text
    for marker in (
        "outer 5-fold", "5 repetições", "inner 5-fold", "estratificados por evento",
        "fold interno de treino", "o holdout permanece fechado", "sem feedback do holdout",
        "semente-base 2026", "fold ids salvos", "lambda.1se como seleção primária",
        "lambda.min como sensibilidade", "outer-fold não escolhe o modelo",
        "painel metabólico candidato", "glycolysis", "tca/oxphos", "gluconeogênese",
        "fontes ainda não verificadas", "sem triagem cox univariada",
        "fontes biológicas verificadas antes de congelar o painel",
    ):
        assert marker in text


def test_nested_cv_and_holdout_are_operationally_frozen():
    text = protocol().casefold()
    for marker in (
        "outer 5-fold",
        "5 repetições",
        "inner 5-fold",
        "estratificados por evento",
        "fold interno de treino",
        "o holdout permanece fechado",
        "sem feedback do holdout",
        "semente-base 2026",
        "fold ids salvos",
        "lambda.1se como seleção primária",
        "lambda.min como sensibilidade",
        "outer-fold não escolhe o modelo",
        "cv final no full discovery",
        "ajustar modelo final em lambda.1se",
        "lambda.min não avaliado no holdout",
    ):
        assert marker in text


def test_candidate_panel_is_prespecified_and_no_univariate_prefilter():
    text = protocol().casefold()
    for marker in (
        "painel metabólico candidato",
        "glycolysis",
        "tca/oxphos",
        "gluconeogênese",
        "fontes ainda não verificadas",
        "sem triagem cox univariada",
        "fontes biológicas verificadas antes de congelar o painel",
    ):
        assert marker in text


def test_raw_counts_are_summed_and_aliquots_are_traceable():
    text = protocol().casefold()
    assert "somar contagens brutas" in text
    assert "avereps" in text
    assert "não calcular média" in text
    assert "aliquot" in text
    assert "sensibilidade" in text
    assert "barcode completo da aliquota em ordem lexicográfica crescente" in text
    assert "selecionar a primeira" in text
    assert "reanalisar os pacientes com aliquotas alternativas" in text
    assert "arquivo open e released" in text


def test_aliquot_rule_is_deterministic_and_sensitive():
    text = protocol().casefold()
    assert "barcode completo da aliquota em ordem lexicográfica crescente" in text
    assert "selecionar a primeira" in text
    assert "reanalisar os pacientes com aliquotas alternativas" in text
    assert "arquivo open e released" in text


def test_validation_model_is_fitted_in_training_only():
    text = protocol().casefold()
    for marker in (
        "modelo clínico-base",
        "modelo ampliado",
        "ajustados apenas no discovery",
        "predições congeladas",
        "não estimar coeficientes no holdout",
        "intervalo de confiança",
    ):
        assert marker in text
    assert "médias geométricas de referência do discovery" in text
    assert "geomeans do discovery" in text
    assert "não recalcular size factors no holdout" in text
    assert "transformação congelada para novos pacientes" in text


def test_normalization_reference_is_from_discovery_only():
    text = protocol().casefold()
    assert "médias geométricas de referência do discovery" in text
    assert "geomeans do discovery" in text
    assert "não recalcular size factors no holdout" in text
    assert "transformação congelada para novos pacientes" in text


def test_no_outcome_threshold_is_a_delivery_gate():
    text = protocol().casefold()
    assert "nenhum resultado biológico é gate de sucesso do pipeline" in text
    assert "p > 0,05" in text
    assert "não demonstra equivalência" in text
    assert "diferença de auc" in text
    assert "sem limiar de superioridade" in text
    for marker in (
        "60 meses", "ghat(60) ≥ 0,10", "10 eventos até 60 meses",
        "1.000 reamostragens", "ic percentil", "não estimável",
        "estimador auc cumulative/dynamic com ipcw",
        "ĝ(60) pela kaplan-meier de censura",
        "90% das reamostragens convergentes",
        "abaixo de 90%, não estimar ic confirmatório",
    ):
        assert marker in text


def test_primary_metric_estimability_and_uncertainty_are_predefined():
    text = protocol().casefold()
    for marker in (
        "60 meses",
        "ghat(60) ≥ 0,10",
        "10 eventos até 60 meses",
        "1.000 reamostragens",
        "ic percentil",
        "não estimável",
        "estimador auc cumulative/dynamic com ipcw",
    ):
        assert marker in text


def test_auc_estimator_and_bootstrap_failure_rule_are_defined():
    text = protocol().casefold()
    assert "ĝ(60) pela kaplan-meier de censura" in text
    assert "90% das reamostragens convergentes" in text
    assert "abaixo de 90%, não estimar ic confirmatório" in text


def test_mui_and_immune_claims_are_bounded():
    text = protocol().casefold()
    for marker in (
        "mui",
        "descritivo",
        "ssgsea",
        "associação transcriptômica",
        "não é medida de fluxo metabólico",
        "não demonstra infiltração celular",
        "não demonstra causalidade",
        "fdr",
    ):
        assert marker in text


def test_supplied_pipeline_is_not_authorized_or_executed():
    text = protocol().casefold()
    assert "script fornecido não será executado" in text
    assert "não instalar pacotes" in text
    assert "google drive" in text
    assert "timestamp utc" in text
    assert "sem sobrescrever execuções anteriores" in text
    assert "pipeline original" in text
    assert "red→green" in text
    for marker in (
        "manifesto open-access antes de qualquer download de conteúdo", "6 gib",
        "autorização explícita do operador em 2026-10-21",
        "pausar e pedir nova decisão humana", "sem execução da análise antes do green do protocolo",
        "versão do gdc", "datas de consulta", "sementes", "log de inclusões e exclusões",
        "análise primária de casos completos", "10%", "denominador os-elegível",
        "pausar antes de modelar", "fluxo de inclusão e exclusão", "missingness",
        "mesmo conjunto de pacientes nos modelos comparados",
    ):
        assert marker in text


def test_download_and_analysis_require_manifest_and_receipts():
    text = protocol().casefold()
    for marker in (
        "manifesto open-access antes de qualquer download de conteúdo",
        "6 gib",
        "autorização explícita do operador em 2026-10-21",
        "exclusão metadata-only autorizada",
        "2b0106c5-7e32-423b-957f-06c9f2e7751b",
        "não há arquivo alternativo para o mesmo paciente/condição",
        "antes de examinar expressão ou desfecho",
        "poderia confundir efeitos de processamento/anotação com variação biológica",
        "pausar e pedir nova decisão humana",
        "sem execução da análise antes do green do protocolo",
        "versão do gdc",
        "datas de consulta",
        "sementes",
        "log de inclusões e exclusões",
    ):
        assert marker in text


def test_missingness_and_flow_are_handled_before_modeling():
    text = protocol().casefold()
    assert "análise primária de casos completos" in text
    assert "10%" in text
    assert "denominador os-elegível" in text
    assert "pausar antes de modelar" in text
    assert "fluxo de inclusão e exclusão" in text
    assert "missingness" in text
    assert "mesmo conjunto de pacientes nos modelos comparados" in text
