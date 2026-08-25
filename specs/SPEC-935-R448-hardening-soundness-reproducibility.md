---
spec_id: SPEC-935-R448
title: Hardening de soundness, instalação, SDD e reprodutibilidade
component: integrations/deepmind, installer, sdd, tests, requirements, documentation
status: green
round_id: R448
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    formal_counterexample_rejected:
      - tests/test_r448_hardening.py::test_counterexample_is_not_accepted_as_a_proof
    unproven_paths_are_not_promoted:
      - tests/test_r448_hardening.py::test_alphaproof_fallback_is_explicitly_unproven
      - tests/test_r448_hardening.py::test_aletheia_generated_lemmas_start_unverified
    installers_fail_closed:
      - tests/test_r448_installer_security.py::test_installers_never_persist_unrestricted_sudo_or_disable_host_protections
      - tests/test_r448_installer_security.py::test_installers_do_not_pipe_network_content_to_an_interpreter
      - tests/test_r448_installer_security.py::test_automatic_installs_require_version_and_sha256_verification
    tests_are_hermetic:
      - tests/test_mirofish_gametheory_publishing.py::TestOrchestratorIntegration::test_produce_scientific_work_uses_injected_output_root
      - tests/test_r221_self_correction_engine.py::TestR221SelfCorrectionEngine::test_corrigendum_path_injetavel
    sdd_body_criteria_are_loaded:
      - tests/test_r448_sdd_contracts.py::test_registry_extracts_backticked_ids_from_executable_markdown_items
      - tests/test_r448_sdd_contracts.py::test_verifier_rejects_agent_claim_without_runtime_test_evidence
    known_regressions_green:
      - tests/test_r212_doctor_litert.py::test_run_doctor_inclui_exatamente_um_check_litert_lm
      - tests/test_r425_pacote_submissao.py::test_selecao_zip_injetavel_e_deterministica
      - tests/test_r435_harness_universal.py::TestR435UniversalBridge::test_orchestrate_creates_tspec_green
      - tests/test_r445_alphageometry_autoformalization.py::TestAlphaGeometryAutoformalizationR445::test_doctor_check_geometry
    dependency_manifests_are_pinned:
      - tests/test_r448_sdd_contracts.py::test_runtime_and_development_manifests_are_explicitly_pinned
    documentation_is_reconciled:
      - tests/test_r448_documentation_reconciliation.py::test_structural_counts_are_consistent_in_operational_documents
      - tests/test_r448_documentation_reconciliation.py::test_manual_has_one_mira_option_and_only_real_direct_commands
      - tests/test_r448_documentation_reconciliation.py::test_docs_do_not_promote_unqualified_readiness_or_perfection_claims
    public_type_hints_resolve:
      - tests/test_r448_hardening.py::test_orchestrator_public_annotations_are_resolvable
    malformed_formal_input_is_rejected:
      - tests/test_r448_hardening.py::test_malformed_equations_never_verify_without_sympy
      - tests/test_r448_hardening.py::test_alphaproof_respects_zero_max_depth_for_direct_identities
      - tests/test_r448_hardening.py::test_alphaproof_fallback_is_explicitly_unproven
    formal_runtime_dependencies_are_declared:
      - tests/test_r448_hardening.py::test_formal_runtime_dependencies_are_explicitly_pinned
    installers_propagate_failures:
      - tests/test_r448_installer_security.py::test_shell_installers_fail_before_aliases_or_launchers_when_smoke_tests_fail
      - tests/test_r448_installer_security.py::test_windows_wrapper_exits_before_shortcuts_when_wsl_provisioning_fails
    verified_bytes_are_executed:
      - tests/test_r448_installer_security.py::test_wsl_executes_normalized_bytes_that_are_verified_again_after_copy
    venv_interpreter_is_used:
      - tests/test_r448_installer_security.py::test_ecosystem_runtime_commands_and_shortcuts_use_the_created_virtualenv
    sdd_requires_trusted_test_evidence:
      - tests/test_r448_sdd_contracts.py::test_verifier_rejects_agent_claim_without_runtime_test_evidence
      - tests/test_r448_sdd_contracts.py::test_orchestrator_rejects_self_attested_markdown_evidence_without_runtime_test
    ci_uses_pinned_static_lint:
      - tests/test_r448_sdd_contracts.py::test_ci_uses_declared_dev_dependencies_and_does_not_hide_late_failures
    critical_countermodel_mutation_killed:
      - tests/test_r448_formal_mutation.py::test_countermodel_predicate_distinguishes_unsat_from_sat
      - tests/test_r448_sdd_contracts.py::test_mutation_gate_targets_the_formal_soundness_contract
      - tests/test_r448_sdd_contracts.py::test_mutation_runner_prioritizes_the_generated_mutant_tree
    quality_report_timeout_covers_suite:
      - tests/test_r448_sdd_contracts.py::test_quality_report_timeout_covers_the_full_suite_duration
---

# SPEC-935-R448 — Hardening de Soundness, Instalação, SDD e Reprodutibilidade

## 1. Objetivo

Eliminar os bloqueadores identificados na auditoria R447 sem ampliar alegações
de qualidade. O ciclo deve falhar fechado: uma conclusão sem demonstração,
ausente não pode ser promovida a sucesso.

## 2. Escopo

1. Corrigir falsos positivos em `FormalProofVerifier`, AlphaProof e Aletheia.
2. Remover elevação persistente de privilégio e execução remota sem verificação
   dos instaladores.
3. Tornar testes herméticos: sem apagar arquivos rastreados nem editar o
   `CORRIGENDUM.md` real; datas e diretórios devem ser injetáveis.
4. Carregar critérios Markdown no registro SDD como contratos verificáveis.
5. Corrigir as quatro falhas de regressão observadas e tornar manifestos de
   dependências explícitos e pinados.
6. Reconciliar README, MANUAL e ARCHITECTURE com o comportamento e métricas
   atuais, empregando linguagem sem certificação externa.
7. Garantir que anotações públicas do orquestrador sejam resolvíveis em runtime.
8. Eliminar caminhos de sucesso para expressões formais malformadas e declarar
   os motores simbólicos usados em runtime.
9. Preservar fail-closed nos caminhos de erro, retomada e execução dos
   instaladores, incluindo o interpretador da virtualenv.
10. Impedir que a evidência declarada pelo próprio agente seja suficiente para
    promover uma entrega a verde no gate SDD.

## 3. Critérios de Aceitação Executáveis

- `formal_counterexample_rejected` — uma implicação com contramodelo retorna
  `False` e nunca “demonstrada”.
- `unproven_paths_are_not_promoted` — fallbacks de AlphaProof/Aletheia são
  rotulados como não provados ou pendentes de verificação.
- `installers_fail_closed` — nenhum instalador grava `NOPASSWD:ALL` ou usa
  `curl | shell`; downloads exigem versão e SHA-256 verificável.
- `tests_are_hermetic` — produção científica e autocorreção recebem destinos
  temporários injetados; a suíte não altera arquivos rastreados.
- `sdd_body_criteria_are_loaded` — critérios do corpo Markdown são extraídos,
  possuem identificadores estáveis e o `SpecVerifier` falha sem evidência.
- `known_regressions_green` — R212, R425, R435 e R445 passam de forma
  determinística.
- `dependency_manifests_are_pinned` — requisitos centrais e de desenvolvimento
  são pinados e contêm dependências obrigatórias das superfícies carregadas.
- `documentation_is_reconciled` — documentos operacionais usam o número atual
   de checks, MCPs e comandos, distinguindo métricas internas de validação
   externa.
- `public_type_hints_resolve` — anotações públicas do orquestrador podem ser
  materializadas por `typing.get_type_hints` sem `NameError`.
- `malformed_formal_input_is_rejected` — equações sem ambos os operandos e
  metas fora do limite de busca não produzem uma prova positiva.
- `formal_runtime_dependencies_are_declared` — SymPy e Z3 usados pelo
  verificador são dependências pinadas e instaláveis no ambiente declarado.
- `installers_propagate_failures` — falha de provisionamento ou smoke test
  encerra com código não nulo, não cria lançadores de êxito e não anuncia
  conclusão.
- `verified_bytes_are_executed` — qualquer normalização de fim de linha ocorre
  antes da conferência, ou os bytes finais executados são conferidos novamente.
- `venv_interpreter_is_used` — atalhos, smoke tests e comandos subsequentes
  usam o interpretador da virtualenv criada pelo instalador.
- `sdd_requires_trusted_test_evidence` — resultado autoafirmado pelo agente,
  sem execução de teste vinculada à spec, não promove a entrega a verde.
- `ci_uses_pinned_static_lint` — a CI instala o manifesto de desenvolvimento
  pinado e executa lint estático obrigatório sobre a superfície de runtime
  endurecida, sem depender de uma versão transitória do linter.
- `critical_countermodel_mutation_killed` — a mutação da decisão positiva
  ``unsat``/``sat`` é exercitada por Mutmut e não pode sobreviver ao gate
  focado; este controle não representa cobertura total do verificador.
- `quality_report_timeout_covers_suite` — o relatório chamado pela CI aceita
  a duração observada da suíte integral, em vez de abortar antes de produzir
  seu resultado.

## 4. Estratégia TDD

1. Adicionar testes de contramodelo, integridade do instalador, isolamento,
   parsing SDD e manifests antes das mudanças funcionais.
2. Executar os testes em RED e registrar as falhas esperadas.
3. Implementar correções mínimas para GREEN.
4. Executar testes de regressão, suíte completa e verificação de árvore Git;
   qualquer mutação inesperada do checkout reprova o ciclo.

## 5. Não objetivos

- Não declarar certificação externa, prova matemática geral, qualidade
  acadêmica de periódico ou segurança absoluta.
- Não baixar, executar ou confiar em um artefato remoto cujo hash não seja
  fornecido e verificado.
