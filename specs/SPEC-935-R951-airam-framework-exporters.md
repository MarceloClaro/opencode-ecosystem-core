---
spec_id: SPEC-935-R951
title: Registry explícito de exportadores para bundles AiramVeras
component: integrations.airamveras_adapter.FrameworkExportRegistry
status: implemented
test_file: tests/test_r951_airam_framework_exporters.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    standard_formats:
    - tests/test_r951_airam_framework_exporters.py::test_jsonl_export_is_stable_and_provenance_complete
    - tests/test_r951_airam_framework_exporters.py::test_existing_builtin_formats_remain_compatible
    framework_extension:
    - tests/test_r951_airam_framework_exporters.py::test_framework_exporter_registry_is_explicit_and_bounded
    mcp_format:
    - tests/test_r951_airam_framework_exporters.py::test_caed_spaece_mcp_advertises_jsonl
---

# R951 — extensibilidade de exportação AiramVeras

## Objetivo

Melhorar o bundle `airamveras.education-matrix` para interoperar com sistemas
que consomem JSON Lines e permitir que hosts confiáveis registrem exportadores
framework-specific em processo, sem alterar o schema canônico nem executar
plugins carregados de caminhos arbitrários.

## Critérios de aceitação executáveis

- `standard_formats` — acrescentar formato `jsonl` que emite um registro JSON
  por linha, preserva `record_id`, chave de matriz e proveniência, e não grava
  arquivos. JSON, CSV e records existentes permanecem compatíveis.
- `framework_extension` — criar `FrameworkExportRegistry` com formato ID
  validado, exportadores callable, rejeição de duplicatas por padrão, saída
  JSON-serializável e limitada por tamanho máximo de payload configurável pelo
  host até um teto rígido de 16 MiB, e registro explícito pelo chamador
  confiável. Não descobrir módulos por diretório nem importar código dinâmico.
- `mcp_format` — `export_matrix_bundle` aceita records, JSON, JSONL ou CSV; a
  ferramenta continua read-only, não recebe callable, nome de módulo ou path
  de plugin, e não recebe diretório de saída.

## Limites

Formatos neutros facilitam consumo por frameworks compatíveis; não afirmar
conectores nativos para Pandas/Polars/Spark/HuggingFace sem implementação e
teste próprios. Dados continuam restritos a descritores públicos allowlisted.
- **Verificação** — testes unitários RED→GREEN e regressões R944/R947 passam;
  nenhuma fonte Airam, resultado individual ou plugin externo é executado.
