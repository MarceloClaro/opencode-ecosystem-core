---
spec_id: SPEC-935-R919
title: Recibo documental reproduzível e integridade de mensagens do SDK
component: scripts.build_documentation_receipt, integrations.opencode_agent_sdk
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    recibo:
    - tests/test_r916_documentation_atlas.py::test_current_r916_receipt_matches_map_and_flow_artifacts
    - tests/test_r919_core_gaps.py::test_receipt_roundtrip_and_check_is_read_only
    integridade:
    - tests/test_r919_core_gaps.py::test_receipt_detects_artifact_drift
    - tests/test_r919_core_gaps.py::test_receipt_rejects_stale_source_or_catalog
    - tests/test_r919_core_gaps.py::test_receipt_rejects_unsafe_or_duplicate_flow
    - tests/test_r919_core_gaps.py::test_receipt_does_not_overwrite_artifacts
    mensagem:
    - tests/test_r919_core_gaps.py::test_chat_once_rejects_malformed_message
    - tests/test_r919_core_gaps.py::test_invalid_response_emits_only_error
    ambiente:
    - tests/test_r919_core_gaps.py::test_ollama_preflight_independent_of_configuration_source
    ferramenta:
    - tests/test_r919_core_gaps.py::test_tool_message_preserves_output_that_fits_context
    - tests/test_r919_core_gaps.py::test_large_tool_output_blocks_next_request_without_truncation
    compatibilidade:
    - tests/test_r659_sdk_hooks_contract.py::test_global_matchers_deny
    - tests/test_r659_sdk_hooks_contract.py::test_signature_is_adapted_without_retrying_hook_body
    - tests/test_r659_sdk_hooks_contract.py::test_lifecycle_and_assistant_tool_history
    - tests/test_r659_sdk_hooks_contract.py::test_invalid_arguments_never_execute
    - tests/test_r659_sdk_hooks_contract.py::test_session_end_even_on_errors_and_budget
    - tests/test_r659_sdk_hooks_contract.py::test_close_runs_post_and_session_end
    - tests/test_r659_sdk_hooks_contract.py::test_malformed_provider_calls_fail_without_tool
---

# R919 — correções delimitadas dos gaps R916/R918

## Problema e escopo

Continuação autorizada pelo usuário. O teste de recibo R916 ficou falhando por
arquivo ausente. A revisão local encontrou corte silencioso de resultados de
ferramentas, bypass do preflight Ollama por configuração de ambiente e ausência
de validação dos tipos da mensagem retornada pelo provedor.

Preservar todas as alterações anteriores, exclusões do operador e recibos
históricos. Não trocar modelo/default, fazer inferência real, instalar, baixar,
comitar nem publicar. Não prometer ausência de outros bugs no Core.

## Contrato

1. Gerador local `python3 -m scripts.build_documentation_receipt` emite o recibo
   `docs/verification-documentation-r916-ollama-quantizacao.json` a partir dos
   bytes atuais, com commit/worktree, contagens, caminhos e hashes de todos os
   fluxos Mermaid/SVG e artefatos documentais enumerados. `--check` é somente
   leitura e retorna não zero se o recibo estiver ausente, alterado ou obsoleto.
   Não incluir seu próprio hash nem timestamps mutáveis na identidade.
2. Revalidar o inventário contra fontes rastreadas e o vínculo do catálogo ao
   mesmo commit/worktree. Recusar IDs/arquivos duplicados, caminhos com traversal,
   symlinks e destinos que sobrescrevam fontes/artefatos. Escrita atômica somente
   após todas as validações. Hash de SVG existente não significa renderização
   executada nesta rodada. Não transportar resultados históricos como atuais.
3. `chat_once` valida choices/message, conteúdo texto ou null e tool_calls antes
   de retornar sucesso. Respostas inválidas geram `invalid_provider_response`,
   sem texto/uso/result de sucesso e sem conteúdo privado na mensagem de erro.
4. A identidade de endpoint Ollama loopback independe da origem da configuração
   (explícita, ambiente ou autodetecção). Aplicar `/api/show` e o menor teto do
   operador. Não fazer retries, fallback ou sondagem arbitrária de outro host.
5. Resultado de ferramenta permanece íntegro na mensagem serializada; não cortar
   JSON em 4.000 caracteres. Recalcular o contexto antes da próxima chamada e
   bloquear explicitamente se excedido. Pós-hook permanece antes de `tool_use`.
6. Preservar o caminho de chamada sem reserva explícita de saída compatível com
   o SDK anterior. Testes R659 isolam `/api/show` e conferem o evento aditivo
   `usage`, mantendo todas as asserções de hooks, negação e efeitos. Respostas
   inválidas são recusadas antes de `usage` também na fronteira do loop.

## Critérios de Aceitação Executáveis

- `recibo` — recibo atual existe e corresponde a todos os fluxos; geração e check reproduzíveis.
- `integridade` — contraprovas recusam deriva, origem obsoleta e caminhos inseguros sem escrita indevida.
- `mensagem` — mensagens inválidas são recusadas sem exceção nem sucesso aparente.
- `ambiente` — configuração equivalente por ambiente não contorna o preflight Ollama.
- `ferramenta` — resultados são preservados ou o orçamento bloqueia explicitamente a próxima requisição.
- `compatibilidade` — contratos R659 continuam herméticos e preservam lifecycle e guardas, com uso de tokens explícito.

## Evidência e limites

Registrar RED real desta rodada antes das correções e GREEN do mesmo oráculo;
não reconstruir cronologia da sessão anterior. Regenerar mapas e âncoras se as
fontes rastreadas mudarem. Rodar regressões R649/R659/R879/R881/R914/R916/R917/R918,
checks de mapas/Mermaid/README e doctor. Aceite local SDD/BehavioralGate não é
validação externa, benchmark de modelo ou execução de todos os subsistemas.
Notas de revisão automática não substituem a leitura do resultado do revisor.
