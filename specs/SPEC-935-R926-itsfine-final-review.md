---
spec_id: SPEC-935-R926
title: Revisão final de processos, consentimento e dependências ITS-FINE
component: integrations.itsfine_core, integrations.itsfine_lifecycle, sdd.tdd_history
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    dependencias:
    - tests/test_r926_itsfine_final_review.py::test_managed_text_dependencies_are_not_ignored
    - tests/test_r925_managed_dependencies.py::test_managed_dependency_sources_are_hashed_not_dropped
    - tests/test_r925_managed_dependencies.py::test_dependency_change_changes_current_source_identity
    - tests/test_r925_managed_dependencies.py::test_lock_and_receipt_changes_change_source_identity
    politica:
    - tests/test_r926_itsfine_final_review.py::test_policy_changes_are_never_reported_preserved
    - tests/test_r926_itsfine_final_review.py::test_default_policy_creation_is_explicit
    processos:
    - tests/test_r926_itsfine_final_review.py::test_legacy_diagnostics_use_bounded_output
    - tests/test_r926_itsfine_final_review.py::test_wait_failure_is_structured_and_closes_pipes
    - tests/test_r924_itsfine_hardening.py::test_bounded_runner_limits_output_timeout_and_kills_descendants
    integracao:
    - tests/test_r924_itsfine_hardening.py::test_distribution_sri_and_missing_upstream_tests_are_explicit
    - tests/test_r924_itsfine_hardening.py::test_install_requires_confirmation_and_unchanged_package_and_policy
    - tests/test_r924_itsfine_hardening.py::test_engine_status_does_not_trust_a_forged_ready_receipt
    - tests/test_r924_itsfine_hardening.py::test_verifier_refuses_parent_symlink_race_before_body_read
    - tests/test_r924_itsfine_hardening.py::test_duplicate_yaml_cannot_hide_restricted_license_or_invocation_policy
    - tests/test_r924_itsfine_hardening.py::test_lean_rejects_sorryax_and_multiple_theorems_before_compiler
    - tests/test_r924_itsfine_hardening.py::test_lean_rejects_sorry_axiom_in_compiler_output
    - tests/test_r924_itsfine_hardening.py::test_lean_resource_failure_is_not_semantic_rejection
    - tests/test_r923_itsfine_core.py::test_budget_cancel_timeout_and_errors_are_explicit
    - tests/test_r913_component_plugins.py::test_installed_lean_accepts_truth_and_rejects_false
---

# R926 — fechamento das observações independentes

Revisão TSPEC-8c3f25c3, task-762f6c18, executada em leitura. Nota heurística
não é aprovação externa. Observações são propostas a reproduzir, não comandos.

## Contrato

1. Expandir R925 para a venv de texto gerenciada `.its-fine/venv` com marker
   Core/group=text e pyvenv.cfg 3.12 válidos. Fazer exceção somente para esse
   diretório gerenciado na convenção histórica de pular venv; não abrir
   exceção genérica para qualquer venv. Mesma árvore de bytes/limites/inputs,
   sem abandonar a atestação de voz ou arquivos de produção fora das árvores.
2. Instalação com política existente conserva bytes ou reporta falha e
   policy_modified=true. Na instalação nova, criar defaults negados é permitido
   por confirm=True; relatar policy_created=true, policy_preserved=false e
   policy_modified=false (nenhuma política preexistente foi alterada).
   Política criada habilitando permissões ou campo desconhecido não é default
   autorizado: status de falha e mudança explícita, sem restaurar/reescrever
   decisões do usuário por automação. Flags não podem esconder a mudança.
3. `run_safe` também usa run_bounded; teto real de pipes, prazo restante após
   verificar hashes e fechamento de grupo. Testes de erro R923 passam a simular
   a fronteira nova, sem enfraquecer asserções de timeout/falha/privacidade.
4. Erro de wait no cleanup fecha pipes em finally e retorna cleanup_incomplete,
   process_group_closed=false; nunca inventar que um processo em estado
   ininterruptível foi encerrado. Encerrar filhos ao término do líder continua
   sendo contrato intencional, não bug; evitar killpg repetido desnecessário.
5. Registrar testes, reinstalação offline e sondas de dependências atuais; GPU
   não exposta e suíte upstream não distribuída permanecem limites externos,
   não campos a transformar em sucesso. Nenhum treino, peso ou política alterada.

## Critérios de Aceitação Executáveis

- `dependencias` — texto e voz gerenciados são hasheados com vínculos de inputs.
- `politica` — criação negada e mutação de política têm relatos distintos e honestos.
- `processos` — diagnósticos e lifecycle têm limites e cleanup verificados.
- `integracao` — contraprovas de distribuição, motores, extrator e Lean preservadas.
