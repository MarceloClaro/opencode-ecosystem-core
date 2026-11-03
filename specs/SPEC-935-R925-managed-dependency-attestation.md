---
spec_id: SPEC-935-R925
title: Atestação agregada de fontes de dependências gerenciadas e integração ITS-FINE
component: sdd.tdd_history
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    fonte:
    - tests/test_r925_managed_dependencies.py::test_managed_dependency_sources_are_hashed_not_dropped
    - tests/test_r925_managed_dependencies.py::test_dependency_change_changes_current_source_identity
    - tests/test_r925_managed_dependencies.py::test_unmanaged_tree_is_not_exempt_and_symlinks_fail_closed
    inputs:
    - tests/test_r925_managed_dependencies.py::test_lock_and_receipt_changes_change_source_identity
    integracao:
    - tests/test_r924_itsfine_hardening.py::test_distribution_sri_and_missing_upstream_tests_are_explicit
    - tests/test_r924_itsfine_hardening.py::test_install_requires_confirmation_and_unchanged_package_and_policy
    - tests/test_r924_itsfine_hardening.py::test_bounded_runner_limits_output_timeout_and_kills_descendants
    - tests/test_r924_itsfine_hardening.py::test_engine_status_does_not_trust_a_forged_ready_receipt
    - tests/test_r924_itsfine_hardening.py::test_verifier_refuses_parent_symlink_race_before_body_read
    - tests/test_r924_itsfine_hardening.py::test_duplicate_yaml_cannot_hide_restricted_license_or_invocation_policy
    - tests/test_r924_itsfine_hardening.py::test_lean_rejects_sorryax_and_multiple_theorems_before_compiler
    - tests/test_r924_itsfine_hardening.py::test_lean_rejects_sorry_axiom_in_compiler_output
    - tests/test_r924_itsfine_hardening.py::test_lean_resource_failure_is_not_semantic_rejection
    - tests/test_r913_component_plugins.py::test_installed_lean_accepts_truth_and_rejects_false
---

# R925 — reduzir tamanho do manifesto sem reduzir fontes verificadas

## Causa observada

Preparar a venv de voz instalou fontes de terceiros suficientes para ultrapassar
20.000 entradas no mapa plano de TDDHistory._sources. A falha ocorreu antes de
iniciar pytest; não é RED autenticado e não será promovida como tal.
Não aumentar cegamente o teto, renomear arquivos para ocultá-los, excluir os
novos testes ou fabricar um histórico. Preservar os recibos R924 já observados.

## Contrato

1. Somente `.its-fine/venvs/hf-tts/lib/python3.12/site-packages` de uma venv
   com pyvenv.cfg regular e marker Core regular/JSON (`kind`, root, group=voice
   conferidos) pode usar representação agregada. Arquivos de produção fora
   desse diretório mantêm exatamente a cobertura anterior no mapa files.
   O mecanismo não aceita raiz arbitrária, exclusão configurável ou execução.
2. Hash de árvore ordenada inclui caminho relativo e SHA256 de CADA fonte que
   o scanner anterior leria (.py, .h, .c etc. e configurações enumeradas).
   Não saltar corpos fonte, nem confiar só em METADATA/RECORD/pip freeze.
   `dependency_trees` registra digest, source_files e source_bytes. Fontes não
   gerenciadas continuam sob o teto plano anterior; contrato legado sem venv
   permanece com git_head/files, sem mudança cosmética obrigatória.
3. Recusar links/arquivos especiais, limite por arquivo 64 MiB e teto por árvore
   de 100.000 fontes/1 GiB fonte. Traversal/nodes não viram código executado.
4. Inputs incluem hashes de marker/pyvenv.cfg, locks text/voice e recibos
   `.its-fine/core/engines/*.json` existentes. Alterar fonte OU lock/recibo
   invalida a identidade GREEN corrente, sem confundir hash com validação externa.
5. Capturar RED nativo dos testes antes da mudança. O runner Core estava
   bloqueado pelo próprio bug: após corrigir a representação das fontes, emitir
   RED autenticado novo enquanto o vínculo dos inputs ainda está em implementação;
   depois completar esse vínculo e executar GREEN do contrato inteiro. Não
   atribuir timestamps/assinaturas retrospectivos ao RED nativo inicial.

## Critérios de Aceitação Executáveis

- `fonte` — agregação mantém hashes, alterações e falhas de caminhos; nada é ocultado.
- `inputs` — locks e recibos fazem parte da identidade atestada.
- `integracao` — instalação, processos, motores, extrator e Lean mantêm as contraprovas R924.

A atestação continua local; bibliotecas nativas fora dos sufixos cobertos não
ganham certificação por isso. Não provar mérito científico ou impedir dono do
host de modificar o runtime/chave. Nenhuma edição de dados, política ou modelo.
