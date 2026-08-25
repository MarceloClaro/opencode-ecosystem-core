---
spec_id: SPEC-935-R453
title: Fechamento de credenciais, prova SDD e preflight privilegiado
component: agents/catalog, templates, sdd, installer, tests, documentation
status: green
round_id: R453
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    tracked_google_api_keys_are_absent:
      - tests/test_r453_precommit_security_closure.py::test_tracked_index_contains_no_high_confidence_secret_pattern
      - tests/test_r453_precommit_security_closure.py::test_secret_scan_reads_the_index_instead_of_a_divergent_worktree
    sdd_requires_delivery_and_safe_test_target:
      - tests/test_r453_precommit_security_closure.py::test_runtime_evidence_never_promotes_an_absent_delivery
      - tests/test_r453_precommit_security_closure.py::test_pytest_runner_rejects_option_like_target_and_uses_option_terminator
    trusted_evidence_scope_is_explicit:
      - tests/test_r453_precommit_security_closure.py::test_sdd_documentation_does_not_misrepresent_same_process_evidence
    installer_preflight_precedes_privilege_and_cli_work:
      - tests/test_r453_precommit_security_closure.py::test_shell_installers_preflight_before_privilege_or_cli_installation
      - tests/test_r453_precommit_security_closure.py::test_shell_preflight_requires_clean_checkouts_and_rejects_repository_userinfo
      - tests/test_r453_precommit_security_closure.py::test_external_artifact_preflight_occurs_before_privilege_and_windows_install
      - tests/test_r453_precommit_security_closure.py::test_installer_sources_are_bound_to_verified_trees_before_libraries
    privileged_cli_path_is_not_reused:
      - tests/test_r453_precommit_security_closure.py::test_cli_installation_drops_sudo_ticket_and_does_not_execute_found_cli_versions
      - tests/test_r453_precommit_security_closure.py::test_installer_path_is_fixed_before_preflight_and_ollama_never_executes_an_unattested_binary
      - tests/test_r453_precommit_security_closure.py::test_cli_steps_keep_a_system_path_and_abort_on_first_integrity_error
      - tests/test_r453_precommit_security_closure.py::test_external_artifact_preflight_is_pure_and_rejects_query_strings
    windows_wrapper_forwards_external_artifact_inputs:
      - tests/test_r453_precommit_security_closure.py::test_windows_wrapper_forwards_all_external_artifact_inputs_to_wsl
      - tests/test_r453_precommit_security_closure.py::test_privileged_launchers_use_absolute_system_binaries_and_direct_bash
      - tests/test_r453_precommit_security_closure.py::test_windows_validates_bytes_and_sanitizes_bash_before_wsl_installation
    secret_scan_covers_tracked_text:
      - tests/test_r453_precommit_security_closure.py::test_tracked_index_contains_no_high_confidence_secret_pattern
      - tests/test_r453_precommit_security_closure.py::test_secret_scan_reads_the_index_instead_of_a_divergent_worktree
    installer_limitations_remain_honest:
      - tests/test_r453_precommit_security_closure.py::test_installer_docs_keep_explicit_non_guarantees
    sdd_runtime_gate_accommodates_observed_suite_duration:
      - tests/test_r453_precommit_security_closure.py::test_sdd_runtime_timeout_exceeds_the_observed_full_suite_duration
---

# SPEC-935-R453 — Fechamento de credenciais, prova SDD e preflight privilegiado

## Objetivo

Remediar bloqueadores concretos da revisão pré-commit sem ampliar alegações de
segurança: remover credenciais rastreadas, impedir promoção SDD sem entrega,
fechar injeção de alvo do pytest e fazer instaladores validarem sua revisão e
entradas antes de efeitos privilegiados ou CLIs externas.

## Critérios de Aceitação Executáveis

- `tracked_google_api_keys_are_absent` — nenhum arquivo textual rastreado
  contém padrão de chave Google/Gemini; exemplos usam variável de ambiente ou
  marcador não secreto, e a política orienta revogação/rotação da credencial
  eventualmente exposta.
- `sdd_requires_delivery_and_safe_test_target` — evidência runtime não promove
  `output=None`; o runner recusa alvos iniciados por hífen e separa opções do
  alvo pytest com `--`.
- `trusted_evidence_scope_is_explicit` — documentação e código não descrevem
  um selo privado no mesmo processo como fronteira contra código arbitrário;
  ele é limitado a impedir autoatestado por dados de agentes.
- `installer_preflight_precedes_privilege_and_cli_work` — Linux, macOS e WSL
  verificam ref imutável, checkout-fonte local e destino antes de `sudo`,
  Homebrew, gerenciador de pacotes ou instalação de CLIs; falhas encerram antes
  de efeitos privilegiados. Ambos os checkouts devem estar limpos, a URL de
  repositório não pode conter credenciais, consulta ou fragmento, e o checkout
  verificado deve ser a árvore que fornece scripts e bibliotecas executados.
- `privileged_cli_path_is_not_reused` — tickets `sudo` são invalidados antes
  da instalação/sondagem de CLIs, e o fluxo não executa `--version` de binário
  já encontrado apenas para anunciá-lo. Validação e downloads de cada CLI usam
  somente `PATH` de sistema e interrompem no primeiro erro de integridade.
- `windows_wrapper_forwards_external_artifact_inputs` — o wrapper recebe e
  encaminha explicitamente ao WSL os parâmetros de procedência requeridos por
  OpenCode, Antigravity, Claude Code e Ollama; a documentação enumera-os sem
  fornecer hashes inventados. O wrapper valida a configuração selecionada antes
  de instalar WSL, confere bytes locais/remotos antes de qualquer alteração
  WSL/DISM e usa executáveis de sistema absolutos para abrir WSL/DISM. A etapa
  não interativa do WSL usa ambiente mínimo e Bash sem perfis de usuário.
- `secret_scan_covers_tracked_text` — a regressão varre todos os arquivos
  textuais rastreados **no índice que será commitado** e detecta padrões de
  credenciais de alta precisão de mais de um provedor; binários são excluídos
  por presença de byte NUL, não por uma lista curta de extensões.
- `installer_limitations_remain_honest` — o material não promete integridade
  transitiva NPM, segurança atômica contra concorrência local ou E2E Windows
  não executado.
- `sdd_runtime_gate_accommodates_observed_suite_duration` — o timeout padrão
  do executor SDD e do relatório de qualidade da CI suporta a duração observada
  da suíte integral, em vez de transformar uma execução verde e ainda em curso
  em falsa evidência vermelha.

## Estratégia TDD

1. Criar testes RED para segredo rastreado, entrega SDD ausente, alvo pytest,
   ordem de preflight e repasse Windows/WSL.
2. Aplicar remoção, guardas e documentação mínima fail-closed.
3. Executar revisão de segredo, testes focados, suíte integral e gates SDD.

## Não objetivos

- Não revogar uma chave no provedor externo sem acesso à conta do proprietário;
  o repositório só pode removê-la e orientar rotação.
- Não transformar Python no mesmo processo em sandbox contra código arbitrário.
- Não prometer ausência total de TOCTOU em shell sem primitivas atômicas do SO.
- Não fazer bootstrap de uma distro WSL sem `git`: ele é pré-requisito explícito
  para verificar o checkout-fonte antes de operações privilegiadas.
