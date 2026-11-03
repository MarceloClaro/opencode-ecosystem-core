---
spec_id: SPEC-935-R935
title: Inventário GDC metadata-only open access para TCGA-KIRC
component: integrations.gdc_metadata_inventory
status: proposed
test_file: tests/test_r935_gdc_metadata_inventory.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    query:
    - tests/test_r935_gdc_metadata_inventory.py::test_query_is_fixed_open_released_and_metadata_only
    pagination:
    - tests/test_r935_gdc_metadata_inventory.py::test_pagination_is_reconciled_by_unique_file_id
    association:
    - tests/test_r935_gdc_metadata_inventory.py::test_file_case_sample_aliquot_links_fail_closed
    integrity:
    - tests/test_r935_gdc_metadata_inventory.py::test_file_metadata_and_checksums_are_validated
    - tests/test_r935_gdc_metadata_inventory.py::test_missing_default_version_fields_use_bounded_versions_metadata
    download_gate:
    - tests/test_r935_gdc_metadata_inventory.py::test_budget_and_version_compatibility_gate_content
    - tests/test_r935_gdc_metadata_inventory.py::test_data_release_ranges_use_common_latest_release_intersection
    manifest:
    - tests/test_r935_gdc_metadata_inventory.py::test_manifest_is_atomic_local_metadata_only_artifact
    - tests/test_r935_gdc_metadata_inventory.py::test_operator_authorized_outlier_is_excluded_with_provenance_rationale
---

# R935 — contrato do inventário de metadata GDC

## Escopo

Implementar um cliente delimitado para consultar somente metadata do endpoint
oficial `https://api.gdc.cancer.gov/files` com filtros fixos TCGA-KIRC, STAR
Counts, `access=open` e `state=released`. O manifesto de saída é
`outputs/core-r934/gdc-manifest.json`. Nenhum endpoint de conteúdo/download,
credential, URL arbitrária, package install ou execução do script Markdown é
permitido. Por autorização explícita do operador em 2026-10-21, o teto agregado
de conteúdo é 6 GiB (6 × 1024³ bytes), substituindo o limite anterior de 2 GiB.
R935 continua sem baixar conteúdo; a elevação do teto não remove os bloqueios de
compatibilidade workflow/release nem autoriza download por si só. O operador
autorizou, em 2026-10-21, excluir do conjunto primário somente o UUID
`2b0106c5-7e32-423b-957f-06c9f2e7751b` por divergência de `workflow_version`,
preservando-o no manifesto com rationale de proveniência. Seu intervalo
`data_release` `36.0-46.0` se sobrepõe ao principal `32.0-46.0`; esta diferença
textual não é motivo de exclusão quando há releases comuns. Incompatibilidades
adicionais continuam bloqueadas.

## Critérios de Aceitação Executáveis

- `query` — endpoint/filters/fields são constantes e metadata-only; não seguir
  redirecionamento para outro host/endpoint e não aceitar URL/headers do usuário;
  warnings ausentes/malformados ou de schema são bloqueadores. Não solicitar `version`/`data_release`
  explicitamente, pois o preflight reportou esses nomes como não reconhecidos
  nesse parâmetro de projeção; validar os valores default quando fornecidos. Para
  todos os arquivos selecionados, consultar somente `/files/versions/{GDC_UUID[,..]}`
  em batches fixos de até 50 UUIDs, nunca endpoint de conteúdo; verificar ID,
  latest ID/versão, MD5, tamanho e a lista `latest_release` da versão corrente.
  Preencher valores ausentes a partir dessa resposta. Qualquer warning aborta.
- `pagination` — ler `data.pagination.total/from/size/count`, validar os tipos e
  size/from/count, requisitar sort estável por file_id, verificar ordem monotônica,
  exigir páginas contínuas/completas e total estável, rejeitar file_id ausente/duplicado ou
  conflito entre `id` e `file_id`; fazer duas passagens metadata-only e recusar
  manifesto elegível se a projeção canônica dos metadados divergir. Hits e tamanho
  agregados contam cada file_id uma vez.
- `association` — validar exatamente um case/sample/aliquot para cada arquivo
  incluído; os IDs e submitter/barcodes precisam estar presentes e coerentes.
  Validar formato/códigos TCGA de patient/sample/aliquot, além do prefixo;
  preservar plate TCGA alfanumérico válido;
  Permitir apenas Primary Tumor e Solid Tissue Normal; selecionar uma aliquota
  por paciente/condição pela ordem lexicográfica de aliquot submitter_id e
  file_id como tie-break; validar que os barcodes de sample e aliquot pertençam
  ao patient submitter_id, aceitar plate TCGA alfanumérico válido e que o código
  de amostra coincida com sample_type;
   persistir os demais como excluídos para sensibilidade. Reconciliar a lista
   `latest_release` de cada arquivo selecionado em `/files/versions`; faixas
   textuais `data_release` diferentes são compatíveis quando a interseção das
   listas exatas de releases é não vazia. Registrar essa interseção e o release
   comum escolhido, sem inferir conteúdo idêntico a partir da string da faixa.
   Aplicar exclusivamente a exceção autorizada do UUID
   `2b0106c5-7e32-423b-957f-06c9f2e7751b`, verificando workflow
   `5a02c12930eb23436322a7494047b907b97570c5` e ausência de candidato alternativo
   do mesmo paciente/condição. Marcar `excluded_workflow_version_incompatible`;
   preservar o registro, checksum, data_release, latest_release e rationale no
   manifesto, sem contar bytes na coorte primária. A justificativa é preservar
   workflow homogêneo: sem demonstração de equivalência entre versões STAR
   Counts, misturá-las poderia confundir processamento com variação biológica.
   A decisão é metadata-only, anterior a expressão/desfecho e não declara o
   arquivo inválido. Nenhuma outra divergência de workflow pode ser excluída
   automaticamente.
  Repetições de ID com atributos divergentes também são conflito, não sobrescrever;
  nested JSON com tipo inesperado é bloqueado.
  Tipos de amostra fora do escopo são registrados como excluídos antes dos gates
  de release/metadados necessários aos tipos-alvo.
  Qualquer relação ambígua bloqueia a elegibilidade de conteúdo do conjunto.
- `integrity` — arquivos selecionados devem ter `access=open`, `state=released`,
  `file_size` inteiro positivo, `md5sum` válido, `version` numérica positiva e
  `data_release` major.minor ou intervalo major.minor; validar a lista de releases
  exatos em `latest_release` para a versão corrente. `data_release` é proveniência
  por arquivo; igualdade textual entre faixas não é requisito se houver release
  comum. `file_id` obrigatório e `id`, se presente,
  precisa coincidir. Bloqueios de metadado devem identificar somente `file_id` e
  nomes de campos ausentes/inválidos, sem valores clínicos ou conteúdo. Não
  inferir SHA-256 externo.
- `download_gate` — somar bytes sobre file_id selecionados únicos. Mais que 6 GiB,
  workflow_version heterogêneo, interseção vazia das listas `latest_release` dos
  arquivos incluídos após a única exclusão autorizada, campos
  faltantes ou cardinalidade ambígua bloqueiam download. `version` é por file_id
  e pode variar entre arquivos; isso não é por si só conflito.
- `manifest` — escrever atomicamente somente metadata, query/filter, páginas,
  contagens, relações, decisões de seleção/exclusão, bytes, checksums e status.
  Vincular a consulta por SHA-256 canônico e emitir sidecar SHA-256 do manifesto.
  A exclusão autorizada precisa aparecer na linha do arquivo e em um registro
  estruturado `authorized_exclusions`, com UUID, workflow/release observados,
  `latest_release`, data de autorização, base da decisão e rationale; manter os
  metadados no manifesto, mas não incluí-los em `selected_file_count`,
  `selected_bytes` ou downloads. Registrar também a interseção exata
  `common_data_releases` e o release comum escolhido para o conjunto primário.
  Usar arquivo temporário exclusivo no mesmo diretório, sem seguir symlink nos
  componentes e com substituição atômica; o CLI usa destino fixo e `root` de teste não é parâmetro
  operacional. Campos de conteúdo/read counts não podem estar presentes. O JSON de saída deve
  preservar `cohort_query_sent=true`, `file_content_downloaded=false` e
  `analysis_executed=false`.

## Verificação

TDD RED→GREEN antes de chamar GDC. Testes usam respostas sintéticas locais,
sem rede. A consulta real será uma operação separada expressamente autorizada
no escopo R934; nenhum teste consulta a API. Timeout, warning ou resposta parcial
não produz manifesto `ready`.
