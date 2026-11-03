---
spec_id: SPEC-935-R955
title: Contrato de armazenamento Airam com fronteiras de dados
component: PROJETO 1/Airam veras/datamining/airam/banco.py
status: implemented
test_file: tests/test_r955_airam_storage_boundaries.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    source_readonly:
    - tests/test_r955_airam_storage_boundaries.py::test_original_sources_are_read_only_and_unchanged
    scope_separation:
    - tests/test_r955_airam_storage_boundaries.py::test_each_scope_has_disjoint_schema
    - tests/test_r955_airam_storage_boundaries.py::test_public_descriptor_allows_unknown_instrument_type
    path_safety:
    - tests/test_r955_airam_storage_boundaries.py::test_store_creation_refuses_sources_and_existing_files
    - tests/test_r955_airam_storage_boundaries.py::test_restricted_store_requires_private_posix_directory
    provenance_and_integrity:
    - tests/test_r955_airam_storage_boundaries.py::test_public_descriptors_have_composite_provenance_keys
    - tests/test_r955_airam_storage_boundaries.py::test_observations_preserve_missingness_and_block_raw_names
    - tests/test_r955_airam_storage_boundaries.py::test_aggregate_metrics_suppress_small_cells_and_require_review
    - tests/test_r955_airam_storage_boundaries.py::test_aggregate_dimensions_reject_identifiers
    - tests/test_r955_airam_storage_boundaries.py::test_claim_evidence_is_hash_and_locator_only
---

# R955 — fronteiras físicas para o banco Airam

## Objetivo

Introduzir um contrato SQLite local que impeça misturar os bancos originais,
descritores públicos, observações individuais restritas e resultados
analíticos. Esta fase cria somente o módulo e seus testes; **não migra, lê ou
grava dados reais de produção**, não modifica bancos CAEd/SPAECE/BNCC e não
gera dossiês a partir de dados individuais.

## Critérios de aceitação executáveis

- `source_readonly` — a fachada de fonte exige caminho absoluto contido na
  raiz allowlisted, abre em modo SQLite `ro`/`query_only`; tentativa de escrita
  falha e o arquivo-fonte permanece byte a byte igual.
- `scope_separation` — cada escopo (`public_matrix`,
  `restricted_observations`, `aggregate_analytics`) reside em arquivo separado,
  declara sua versão e não contém tabelas de outro escopo. O módulo não usa
  `ATTACH` nem copia automaticamente os bancos existentes.
- `path_safety` — criação recusa caminhos dentro das raízes imutáveis, symlinks
  e destinos existentes. Em POSIX, lojas locais usam diretório 0700 e arquivo
  0600; loja restrita falha fechada quando não consegue confirmar essa
  proteção. Arquivos existentes nunca têm permissões ou conteúdo alterados.
- `provenance_and_integrity` — descritores têm chave composta versionada e
  duplicatas são rejeitadas; observações restritas guardam apenas ID local
  pseudonimizado, nunca nome bruto; ausência não é zero; métricas agregadas
  abaixo do limiar configurado são suprimidas e as demais permanecem pendentes
  de revisão humana. Dimensões analíticas seguem allowlist sem aluno, escola,
  turma, nome ou matrícula; evidência armazena hash/localizador, sem texto livre.

## Contrato de dados

- Fontes originais continuam na origem e são abertas somente para leitura.
- `public_matrix` aceita apenas matrizes públicas; licença não declarada é
  preservada como tal e não autoriza redistribuição.
- `restricted_observations` é armazenamento separado, owner-only em POSIX,
  limitado a identificador local pseudonimizado de 64 dígitos hexadecimais e
  medida com unidade, participação, disponibilidade e referência fonte/linha.
  A forma do ID não prova que ele foi gerado por HMAC; a relação entre nome
  real e ID local permanece fora deste módulo.
- Sistemas sem verificação de ACL (incluindo Windows nesta versão) recusam a
  criação das lojas que possam conter dados individuais ou analíticos.
- `aggregate_analytics` registra `run_id`, hashes do manifesto/configuração,
  commit do código, método, limiar de célula e estado de revisão. Não contém
  colunas de aluno, nome ou matrícula.
- Razões, valores e contagens permanecem em tipos distintos; valor ausente
  precisa manter `availability=false` e nulos, nunca ser convertido em zero.
- Migração, normalização e consulta de dados reais são uma etapa posterior,
  com especificação, autorização e execução separadas.

## Limites

O contrato reduz mistura acidental e sobregravação; não é uma fronteira contra
outro processo executado pelo mesmo usuário/host, não autentica usuários nem
prova base legal. ACLs de diretórios existentes, recuperação de segredo e
perfis de compartilhamento permanecem responsabilidade do host/custodiante.
