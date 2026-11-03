---
spec_id: SPEC-935-R922
title: Integração final de ensaio acadêmico e plugins locais com hardening
component: integrations.local_plugin_extraction, marceloclaro.runtime_actions, marceloclaro.orchestrator
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    seguranca:
    - tests/test_r922_academic_plugin_integration.py::test_restricted_frontmatter_is_not_split_by_internal_dashes
    - tests/test_r922_academic_plugin_integration.py::test_punctuated_quoted_secret_is_rejected_without_leak
    - tests/test_r922_academic_plugin_integration.py::test_canonical_service_rejects_lexical_symlink_root
    selecao:
    - tests/test_r922_academic_plugin_integration.py::test_selected_inventory_does_not_touch_unrelated_packages
    - tests/test_r922_academic_plugin_integration.py::test_drvfs_projection_is_data_only_and_requires_observed_mount
    primario:
    - tests/test_r922_academic_plugin_integration.py::test_primary_facade_validates_and_dispatches_selected_operations
    - tests/test_r922_academic_plugin_integration.py::test_selected_extraction_uses_canonical_registry_without_runtime
    simulacao:
    - tests/test_r920_academic_simulation.py::test_plan_has_no_execution
    - tests/test_r920_academic_simulation.py::test_cases_are_deterministic_and_stage_specific
    - tests/test_r920_academic_simulation.py::test_preserve_negative_evidence_without_approval
    - tests/test_r920_academic_simulation.py::test_stale_or_tampered_plan_rejected_before_execution
    - tests/test_r920_academic_simulation.py::test_strict_limits_and_global_reservations
    - tests/test_r920_academic_simulation.py::test_cooperative_cancel_and_timeout
    - tests/test_r920_academic_simulation.py::test_local_only_without_scores_or_answers
    - tests/test_r920_academic_simulation.py::test_service_actions_persist_and_verify
    regressao:
    - tests/test_r916_documentation_atlas.py::test_current_r916_receipt_matches_map_and_flow_artifacts
    - tests/test_r919_core_gaps.py::test_chat_once_rejects_malformed_message
    - tests/test_r919_core_gaps.py::test_ollama_preflight_independent_of_configuration_source
    - tests/test_r919_core_gaps.py::test_tool_message_preserves_output_that_fits_context
    - tests/test_r919_core_gaps.py::test_large_tool_output_blocks_next_request_without_truncation
    - tests/test_r921_local_plugin_extraction.py::test_nested_restriction_is_not_read_or_copied
    - tests/test_r921_local_plugin_extraction.py::test_anthropic_document_skill_bodies_are_never_loaded
    - tests/test_r921_local_plugin_extraction.py::test_registry_commit_failure_rolls_back_new_packages_and_cleans_staging
    - tests/test_r921_local_plugin_extraction.py::test_source_change_before_registry_commit_aborts_and_cleans_staging
---

# R922 — integração e contraprovas da revisão independente

## Escopo

Continuação autorizada. R919, R920 e R921 tiveram gates locais executados em
seus estados anteriores; esta spec revalida a integração atual após hardening.
Não promover esses gates a avaliação científica externa. Preservar oráculos
anteriores e registros históricos, incluindo falhas, limites e recusas.

## Requisitos

1. Delimitadores de frontmatter são linhas completas, nunca substring `---`
   dentro de description. Licença Proprietary explícita bloqueia corpo e ramo.
2. Atribuições concretas de segredo entre aspas, inclusive com pontuação, são
   recusadas com diagnóstico sanitizado. Não prometer detector universal.
3. ScientificPluginService conserva raiz lexical para que seus métodos de
   extração recusem symlinks antes de resolve(), assim como a função pública.
4. Acrescentar `inventory_selected_plugins(cache_root, plugin_ids)` e método
   `ScientificPluginService.extract_selected(cache_root=..., plugin_ids=...)`.
   Escopo é lista explícita não vazia de IDs canônicos e versões fixadas;
   inspecionar SOMENTE os pacotes selecionados, sem varrer perfil/irmãos ou
   baixar nada. Recusas de caminho/tipo/tamanho/credencial continuam válidas
   dentro do escopo. Revalidar somente o mesmo escopo antes do commit.
5. Windows/WSL: adaptar bits executáveis SOMENTE quando a montagem efetiva
   observada em /proc/self/mountinfo for 9p/DrvFS sem opção metadata, e apenas
   no caminho selecionado de importação instrucional. Detectar o mount mais
   específico, sem inferir pela string /mnt/c ou permitir override do usuário.
   Falha na detecção mantém recusa conservadora. Preservar fstat/hashes reais,
   symlinks proibidos, allowlist de textos, UTF-8 e licenças. Nunca carregar
   scripts/hooks/transporte ou conceder execução; destino sem bit executável.
   Inventário declara permission_projection. Caminho R921 legado permanece
   estrito em POSIX. Nenhum chmod na origem ou alteração de mount/ACL.
6. Primário scientific_plugin_action expõe inventory_local/extract_selected,
   com cache_root e plugin_ids obrigatórios, validados antes dos efeitos.
   Não aceitar destino arbitrário ou override de permissões pela fachada.
   Usar serviço canônico, registrar observação sem promoção de confiança.
7. Executar demonstração sintética com 7 estágios x 3 cenários, seed explícita,
   orçamento global, revisão-base única e hashes reproduzíveis. Sem manuscrito
   do usuário, os dados são fixture DIDÁTICA e não pesquisa real. Registrar
   perguntas/pendências/uso, nunca nota, veredito ou resultados inventados.
8. Execução real dos plugins é cópia seletiva permitida de dados instrucionais,
   não execução dos plugins. Licença ausente/restrita fica reference_only.
   Não reinstalar nem remover materiais legados. Guia operacional registra
   exemplos de uso via primário, diferenças de scope e pendências.

## Critérios de Aceitação Executáveis

- `seguranca` — contraprovas de frontmatter, segredo e raiz lexical bloqueiam antes de cópia indevida.
- `selecao` — escopo limitado e projeção de modos comprovada não afrouxam guardas POSIX.
- `primario` — fachada valida/encaminha ao registro canônico e distingue cópia de inferência.
- `simulacao` — contratos de integridade, reprodução, etapas e revisão humana R920 preservados.
- `regressao` — recibo atual, SDK e contraprovas críticas de extração continuam passando.

## Não objetivos

Não autenticar serviços, controlar GUI do ChatGPT, extrair cookies, copiar código
AGPL/proprietário, instalar, inferir revisão por pares real, comitar ou publicar.
Integridade local e detecção de licença são controles delimitados, não prova
jurídica, científica ou de isolamento contra o dono do host.
