---
spec_id: SPEC-935-R947
title: Adaptador AiramVeras interoperável com frameworks e sistemas de dados
component: integrations.airamveras_adapter
status: implemented
test_file: tests/test_r947_airamveras_interop.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    canonical_bundle:
    - tests/test_r947_airamveras_interop.py::test_adapter_builds_canonical_bundle_with_row_level_provenance
    - tests/test_r947_airamveras_interop.py::test_bundle_includes_machine_readable_record_schema
    framework_exports:
    - tests/test_r947_airamveras_interop.py::test_bundle_exports_records_json_and_csv_without_disk_writes
    safety_boundary:
    - tests/test_r947_airamveras_interop.py::test_adapter_rejects_restricted_sources_and_never_reads_student_tables
    mcp_interop:
    - tests/test_r947_airamveras_interop.py::test_caed_spaece_mcp_exposes_framework_neutral_export
    agent_contract:
    - tests/test_r947_airamveras_interop.py::test_matrix_specialist_advertises_canonical_exports
---

# R947 — contrato de interoperabilidade AiramVeras

## Objetivo

Adicionar ao Core um adaptador próprio e desacoplado do código do repositório
AiramVeras para transformar matrizes públicas CAEd/SPAECE allowlisted em um
bundle canônico consumível por diferentes frameworks e sistemas de dados. Não
importar nem copiar código do repositório AiramVeras; não alterar a pasta
original do usuário.

## Critérios de aceitação

- **Contrato canônico** — bundle versionado com `schema_id`/`schema_version`,
  identificador do sistema e matriz, edição/ano quando conhecido, etapa/série,
  componente, descritores, origem por observação (arquivo, página, URL e
  SHA-256 disponível), limites e classificação `public_assessment_matrix`.
  `SPAECE` legado sem ano declarado conserva ano `null`; não infere edição.
- **Interoperabilidade** — a mesma representação deve exportar para objetos
  Python/records, JSON e CSV em memória, sem exigir Pandas, Polars, Spark,
  HuggingFace ou outra dependência do consumidor. O esquema/documentação deve
  permitir que conectores específicos sejam escritos depois; não alegar suporte
  implementado para frameworks que não foram testados. Exportação não salva
  arquivos, publica dados ou inicia treino.
- **Conexão com o MCP** — acrescentar `export_matrix_bundle` ao servidor
  `caed-spaece-data`, limitado aos IDs/sistemas allowlisted e aos formatos
  `records`, `json` e `csv`; chamadas continuam em SQLite read-only e com limite
  de linhas.
- **Privacidade** — reutilizar apenas o adaptador de matrizes públicas; continuar
  excluindo resultados, diretórios `RESTRITO`, microdados, nomes, matrículas,
  identificadores de estudantes e scripts do repositório AiramVeras.
- **Proveniência e licença** — preservar os campos de origem/hash sem inventar
  licença nem transferir copyright. O repositório público AiramVeras não teve
  licença de reutilização de código confirmada; a implementação no Core deve ser
  independente e baseada no contrato/schema público das matrizes.
- **Verificação** — testes unitários cobrem bundle, exportadores, filtros e
  fronteira de privacidade; a suíte R894/R942/R944 e `doctor` não apresentam
  falhas novas. Não executar código, notebook, build ou teste do repositório
  AiramVeras.

## Limites

“Integrável a qualquer framework” significa intercâmbio por um contrato estável
e formatos neutros JSON/CSV/records. Cada framework futuro precisará de um
adaptador próprio; não é possível alegar compatibilidade universal automática.
O contrato cobre matrizes públicas, não dados de resultados individuais nem o
pipeline analítico completo do AiramVeras.
