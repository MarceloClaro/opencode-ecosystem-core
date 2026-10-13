---
spec_id: SPEC-935-R840
title: Cache limitado do frontmatter sem leituras obsoletas
component: marceloclaro.catalog_loader
status: proposed
test_file: tests/test_r840_catalog_frontmatter_cache.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    cache:
    - tests/test_r840_catalog_frontmatter_cache.py::test_repeated_load_parses_equal_bytes_once
    - tests/test_r840_catalog_frontmatter_cache.py::test_same_bytes_different_paths_share_only_frontmatter
    - tests/test_r840_catalog_frontmatter_cache.py::test_changed_content_same_mtime_size_is_reparsed_then_reused
    - tests/test_r840_catalog_frontmatter_cache.py::test_parser_identity_change_invalidates_cache
    - tests/test_r840_catalog_frontmatter_cache.py::test_nested_results_are_independent_of_prior_consumer
    - tests/test_r840_catalog_frontmatter_cache.py::test_cache_stores_independent_parser_result
    - tests/test_r840_catalog_frontmatter_cache.py::test_files_are_read_again_on_cache_hit
    - tests/test_r840_catalog_frontmatter_cache.py::test_removed_file_is_not_returned_from_cache
    - tests/test_r840_catalog_frontmatter_cache.py::test_added_file_is_seen_in_sorted_current_listing
    - tests/test_r840_catalog_frontmatter_cache.py::test_unreadable_file_does_not_reuse_previous_card
    - tests/test_r840_catalog_frontmatter_cache.py::test_invalid_utf8_is_not_hidden_by_cache
    - tests/test_r840_catalog_frontmatter_cache.py::test_missing_directory_remains_empty
    - tests/test_r840_catalog_frontmatter_cache.py::test_body_change_is_observed_and_raw_bytes_form_key
    - tests/test_r840_catalog_frontmatter_cache.py::test_original_universal_newline_semantics_are_preserved
    - tests/test_r840_catalog_frontmatter_cache.py::test_capability_taxonomy_is_rederived_on_cache_hit
    - tests/test_r840_catalog_frontmatter_cache.py::test_cache_has_bounded_lru_and_evicts_oldest
    - tests/test_r840_catalog_frontmatter_cache.py::test_oversized_cards_are_parsed_without_storage
    - tests/test_r840_catalog_frontmatter_cache.py::test_parser_exception_is_not_cached
    - tests/test_r840_catalog_frontmatter_cache.py::test_environment_cannot_select_external_implementation
---

# R840 — Cache limitado do catálogo

A proposta e o RED/GREEN da cópia isolada foram conservados em outputs/core-r840.

## Critérios de Aceitação Executáveis

- `cache` — leitura fresca, interpretação reutilizada por bytes e parser, LRU limitado, cópias independentes e resultados funcionais corretos em todos os casos associados.

## Contrato

Cache somente de frontmatter, máximo 512 entradas e bypass acima de 128 KiB.
Toda chamada lê arquivos atuais. A chave compara bytes completos e identidade do
parser, sem confiar em mtime/tamanho. Cache não contém catálogo final, saúde,
credenciais ou inferência. Adições, remoções, alterações e erros são observados;
capabilities são derivadas novamente. Cópias profundas protegem armazenamento e retorno.

A interface, ordem, UTF-8 e novas linhas universais permanecem compatíveis.
Dependência de repetição no mesmo processo é explícita: chamada fria não recebe
promessa de aceleração. O limite não mede toda a memória de objetos YAML.

## Regressão exigida

Conservar e executar o requisito R110 de menos de cinco segundos, R810 de
diagnóstico estrutural sem processos/rede/inferência e os consumidores do catálogo.
Comparar os 255 cartões reais antes/depois e medir custos, sem alegar ganho universal.
Ajustar a unidade de recuperação hierárquica para usar exclusivamente seus dois
registros controlados; ela não pode depender de observações deixadas por outras baterias.

## Proveniência

Registrar RED anterior à alteração do produto pelo primário e GREEN dos mesmos
testes com histórico R839. A assinatura é local e não prova qualidade do oráculo
ou validação externa. Custos medidos e listas de cartões não são inferência LLM.

O oráculo do Core carrega sempre `marceloclaro/catalog_loader.py` do projeto.
Uma variável de ambiente não pode substituir esse arquivo por candidato externo.
Seletores da proposta privada não são aceitos no teste canônico; a contraprova
do seletor e os pares anteriores ficam preservados, sem reclassificação retroativa.
