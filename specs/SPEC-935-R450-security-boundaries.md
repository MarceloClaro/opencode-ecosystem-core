---
spec_id: SPEC-935-R450
title: Fechamento de fronteiras de entrada formal e instaladores
component: integrations/deepmind, installer, tests, documentation
status: green
round_id: R450
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    formal_text_never_reaches_sympify:
      - tests/test_r450_security_boundaries.py::test_formal_text_is_restricted_before_any_sympify_call
    installer_ecosystem_dir_is_safe_to_persist:
      - tests/test_r450_security_boundaries.py::test_ecosystem_directory_helper_rejects_shell_and_launcher_metacharacters
    artifact_cache_is_private_and_nonconfigurable:
      - tests/test_r450_security_boundaries.py::test_artifact_cache_rejects_override_and_symlinked_parent_without_permission_changes
    windows_reboot_resume_is_manual_and_explicit:
      - tests/test_r450_security_boundaries.py::test_windows_wrapper_requires_manual_reentry_after_reboot
    windows_supporting_bytes_are_verified:
      - tests/test_r450_security_boundaries.py::test_windows_wrapper_requires_manual_reentry_after_reboot
      - tests/test_r448_installer_security.py::test_wsl_executes_normalized_bytes_that_are_verified_again_after_copy
    security_regressions_are_tested_without_network_or_privilege:
      - tests/test_r450_security_boundaries.py::test_ecosystem_directory_helper_rejects_shell_and_launcher_metacharacters
      - tests/test_r450_security_boundaries.py::test_artifact_cache_rejects_override_and_symlinked_parent_without_permission_changes
      - tests/test_r450_security_boundaries.py::test_windows_wrapper_requires_manual_reentry_after_reboot
    installer_docs_match_security_boundaries:
      - tests/test_r450_security_boundaries.py::test_installer_guides_describe_the_new_fail_closed_boundaries
---

# SPEC-935-R450 — Fechamento de fronteiras de entrada formal e instaladores

## Objetivo

Remediar bloqueadores de segurança encontrados na revisão pré-commit de R448,
sem alegar E2E Windows ou segurança absoluta. Entradas textuais formais e
caminhos persistidos por instaladores devem falhar fechados antes de alcançar
um interpretador, shell, launcher ou alteração de permissões fora da raiz
dedicada.

## Critérios de Aceitação Executáveis

- `formal_text_never_reaches_sympify` — a superfície pública do verificador
  aceita apenas a gramática algébrica documentada e constrói objetos SymPy a
  partir da AST permitida; atributos, subscritos, lambdas, imports, chamadas
  arbitrárias e entradas acima dos limites são recusados antes de avaliação.
- `installer_ecosystem_dir_is_safe_to_persist` — Linux, macOS e WSL validam
  `ECOSYSTEM_DIR` por helper comum antes de gravar aliases ou launchers; o
  caminho precisa ser absoluto, sob `HOME` e formado por caracteres permitidos;
  pais simbólicos são recusados antes de qualquer clone ou escrita.
- `artifact_cache_is_private_and_nonconfigurable` — override de
  `ECOSYSTEM_ARTIFACT_CACHE` é recusado; o cache fixo sob `HOME` é não
  simbólico, pertencente ao usuário e não repara permissões de estado legado:
  uma raiz insegura é recusada sem `chmod` por caminho reaproveitado.
- `windows_reboot_resume_is_manual_and_explicit` — o wrapper não grava
  `RunOnce`; valida os parâmetros antes de solicitar WSL e informa retomada
  manual após reboot, sem declarar uma retomada automática não validada.
- `windows_supporting_bytes_are_verified` — `path_safety.sh`, carregado pelo
  provisionador no WSL, recebe SHA-256 explícito, é conferido antes da cópia e
  rehashado no destino que será executado; o staging WSL cria sessão privada
  nova e recusa pais simbólicos antes de copiar, remover ou alterar permissões.
- `security_regressions_are_tested_without_network_or_privilege` — os contratos
  cobrem as recusas em subprocessos locais, parsing PowerShell quando presente
  e não usam rede, sudo, Registro ou E2E Windows.
- `installer_docs_match_security_boundaries` — os guias informam a restrição de
  diretório persistido, a raiz fixa de cache, o hash adicional do helper e a
  retomada manual Windows, sem sugerir valores de integridade inventados.

## Estratégia TDD

1. Registrar testes RED para gramática formal, caminho persistente, cache e
   retomada Windows antes da alteração funcional.
2. Implementar validação mínima, comum e fail-closed.
3. Rodar testes focados, lint/sintaxe, suíte integral e gate SDD com evidência
   emitida pelo runtime antes de promover a spec.

## Não objetivos

- Não prometer E2E Windows elevado, persistência automática pós-reboot,
  compatibilidade com caminhos Unicode/espaços ou suporte irrestrito a sintaxe
  SymPy.
- Não tratar uma execução local como certificação de segurança externa.
