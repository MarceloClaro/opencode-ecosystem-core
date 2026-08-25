---
spec_id: SPEC-935-R449
title: README operacional completo e preparação de release R448
component: README, documentation, release
status: green
round_id: R449
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    readme_has_operational_entrypoint:
      - tests/test_r449_readme_release.py::test_readme_has_complete_operational_entrypoint
    readme_documents_supported_install_paths:
      - tests/test_r449_readme_release.py::test_readme_documents_installation_without_fabricated_integrity_data
    readme_links_canonical_guides:
      - tests/test_r449_readme_release.py::test_readme_links_to_canonical_guides_and_policies
    readme_documents_validation_scope:
      - tests/test_r449_readme_release.py::test_readme_states_observed_validation_and_limits_without_overclaim
    readme_documents_safety_limits:
      - tests/test_r449_readme_release.py::test_readme_states_observed_validation_and_limits_without_overclaim
    readme_has_contribution_and_release_flow:
      - tests/test_r449_readme_release.py::test_readme_has_complete_operational_entrypoint
      - tests/test_r449_readme_release.py::test_contributing_and_security_policies_are_actionable_and_conservative
    readme_avoids_placeholder_integrity_values:
      - tests/test_r449_readme_release.py::test_readme_documents_installation_without_fabricated_integrity_data
    readme_preserves_documented_legacy_navigation:
      - tests/test_r449_readme_release.py::test_readme_preserves_legacy_mira_storytelling_and_metric_navigation
---

# SPEC-935-R449 — README operacional completo e preparação de release R448

## Objetivo

Atualizar o README principal para que uma pessoa consiga compreender o
ecossistema, instalar o caminho suportado, executar validações e localizar a
documentação canônica sem converter métricas internas em alegações de
certificação externa.

## Critérios de Aceitação Executáveis

- `readme_has_operational_entrypoint` — o README apresenta propósito,
  capacidades, arquitetura resumida e uma rota de início local verificável.
- `readme_documents_supported_install_paths` — instalação local e Windows
  indicam pré-requisitos, caminhos oficiais e exigem hashes fornecidos pelo
  mantenedor, sem valores inventados.
- `readme_links_canonical_guides` — README, MANUAL, ARCHITECTURE,
  CONTRIBUTING, SECURITY e CORRIGENDUM possuem links ou referências diretas.
- `readme_documents_validation_scope` — a validação R448 é descrita como
  resultado local reproduzível, com limites explícitos e sem certificação
  externa implícita.
- `readme_documents_safety_limits` — os limites de modelos, instaladores,
  evidência formal e execução Windows são explícitos para o usuário.
- `readme_has_contribution_and_release_flow` — contribuição, testes, lint,
  quality report e fluxo de release/push são documentados.
- `readme_avoids_placeholder_integrity_values` — README não apresenta hashes
  de exemplo como se fossem artefatos publicáveis ou verificáveis.
- `readme_preserves_documented_legacy_navigation` — a atualização mantém as
  rotas documentais de MIRA, storytelling, diagramas e métricas históricas,
  identificando snapshots legados sem apresentá-los como estado atual.

## Estratégia TDD

1. Criar testes documentais que falham para seções, comandos, links e limites
   ausentes.
2. Reescrever o README a partir do comportamento efetivamente implementado.
3. Validar os testes R449, a suíte integral e o gate SDD antes do commit.

## Não objetivos

- Não prometer certificação, segurança absoluta, desempenho sobre-humano,
  disponibilidade de serviços externos ou E2E Windows não executado.
- Não publicar tokens, chaves, hashes inventados ou diretórios pessoais.
