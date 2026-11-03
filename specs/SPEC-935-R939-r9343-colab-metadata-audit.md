---
spec_id: SPEC-935-R939
title: R934.3 Colab — auditoria GDC metadata-only com schema relacional
component: artigos.bio.tcga_kirc_r9343_colab
status: proposed
test_file: tests/test_r939_r9343_colab_metadata.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    notebook_integrity:
    - tests/test_r939_r9343_colab_metadata.py::test_r9343_is_fresh_nbformat_and_has_no_user_execution_state
    - tests/test_r939_r9343_colab_metadata.py::test_all_r9343_python_cells_have_valid_syntax
    - tests/test_r939_r9343_colab_metadata.py::test_all_python_cells_parse_without_execution
    schema_projection:
    - tests/test_r939_r9343_colab_metadata.py::test_files_mapping_and_related_cases_projection_are_separated
    metadata_query:
    - tests/test_r939_r9343_colab_metadata.py::test_query_is_open_released_sorted_and_metadata_only
    release_compatibility:
    - tests/test_r939_r9343_colab_metadata.py::test_common_latest_release_intersection_and_authorized_exclusion
    drive_privacy:
    - tests/test_r939_r9343_colab_metadata.py::test_drive_run_is_unique_and_public_bundle_excludes_private_metadata
    - tests/test_r939_r9343_colab_metadata.py::test_public_reports_are_aggregate_only_and_downloads_disabled
    download_gate:
    - tests/test_r939_r9343_colab_metadata.py::test_content_download_is_disabled_and_gates_are_not_promoted
---

# R939 — contrato do notebook Colab R934.3

## Escopo

Corrigir o bloqueio de schema do R934.2 sem presumir que relações `cases.*`
precisem estar no índice `/files/_mapping`: validar somente campos indexados
`files.*` no mapping e validar a projeção de caso/amostra/alíquota na resposta
real metadata-only de `/files`. Preservar R934.2 e trabalhar no novo notebook
`artigos/bio/TCGA_KIRC_R934_3_Metadata_Schema_Fix.ipynb`.

Esta versão consulta metadados apenas. `EXECUTAR_DOWNLOADS=False`; não executa
GDC `/data`, R, modelos prognósticos ou análise de pacientes. O operador autorizou
Drive em Colab com diretório UTC versionado, sem sobrescritas. `private_metadata`
fica restrito ao runtime/Drive privado e nunca entra em pacote público.

## Critérios de Aceitação Executáveis

- `notebook_integrity` — notebook nbformat 4 parseável, células sem outputs ou
  `execution_count` persistido; remover IDs/nome de usuário de runtime dos
  metadados de célula. R934.2 permanece byte-a-byte inalterado.
- `schema_projection` — `/files/_mapping` valida apenas campos indexados `files.*`
  necessários, inclusive `files.file_id`/`files.file_name`; campos relacionados
  `cases.*` são exigidos e validados no JSON real de `/files`.
  Campo ausente, warning, redirect, tipo inválido ou relação ambígua bloqueia.
- `metadata_query` — query fixa TCGA-KIRC, STAR Counts, `access=open`,
  `state=released`, ordenação estável por `file_id`; validar somente campos
  indexados `files.*` em `/files/_mapping`, validar relações `cases.*` na
  resposta real, não projetar `version` nem `data_release`, reconciliar paginação
  e duas passagens; nenhum conteúdo baixado.
- `release_compatibility` — consultar `/files/versions` para os file IDs
  selecionados em lotes ≤50, conferir ID/latest ID/versão/MD5/tamanho e obter
  `latest_release` exato. Comparar releases por interseção, nunca igualdade
  textual de faixas `data_release`. Aplicar apenas a exclusão autorizada do UUID
  `2b0106c5-7e32-423b-957f-06c9f2e7751b` por `workflow_version` divergente; sua
  faixa `36.0-46.0` é compatível com a interseção de releases. Preservar a linha,
  checksums, `latest_release` e rationale no manifesto privado; não contar bytes
  nem participante na coorte primária. Qualquer incompatibilidade adicional
  continua bloqueada.
- `drive_privacy` — Drive montado somente no Colab sob autorização do operador;
  cada run em diretório com timestamp UTC e criação exclusiva sem sobrescrita.
  Registrar índice privado de artefatos com hashes e timestamps; guardar dados
  privados no diretório privado versionado. ZIP/public summary
  contém apenas agregados, relatórios públicos e checksums permitidos, nunca
  páginas GDC brutas, file/patient IDs ou `private_metadata`; emitir sidecar
  SHA-256 verificável para o ZIP público.
- `download_gate` — manter `EXECUTAR_DOWNLOADS=False` neste R934.3; não executar
  R934/TCGA, não baixar RNA-seq, não executar análise e não promover P0–P4
  automaticamente. P1 preliminar não equivale a GREEN científico; P0 exige
  aceite metodológico, P2–P4 dependem de etapas posteriores.

## Verificação

Testes locais verificam estrutura JSON e trechos de contrato, usando fixtures
sintéticas sem rede. Depois do TDD/SpecVerifier, a consulta real autorizada será
executada em runtime Colab apenas para metadados; não executar downloads. O pacote
público deve excluir integralmente `private_metadata`.
