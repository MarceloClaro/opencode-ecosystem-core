---
spec_id: SPEC-935-R865
title: Primário único e especificação explícita para análise coordenada
component: integrations.ecosystem_mcp
status: implemented
test_file: tests/test_r865_shared_primary.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    identidade:
    - tests/test_r865_shared_primary.py::test_library_then_execution_preserves_primary
    - tests/test_r865_shared_primary.py::test_execution_then_library_preserves_primary
    - tests/test_r865_shared_primary.py::test_concurrent_initialization_has_one_primary
    carregamento:
    - tests/test_r865_shared_primary.py::test_catalog_is_loaded_once_on_same_primary
    especificacao:
    - tests/test_r865_shared_primary.py::test_text_spec_is_registered_before_executor
    - tests/test_r865_shared_primary.py::test_invalid_text_spec_does_not_construct_primary
    - tests/test_r865_shared_primary.py::test_actual_text_spec_is_registered_and_remains_text_only
    - tests/test_r865_shared_primary.py::test_template_requires_spec_before_execution
---

# R865 — Um primário por servidor MCP

Biblioteca e execução criavam dois MarceloClaroOrchestrator no mesmo processo.
Os callbacks de identidade lógica do segundo substituíam os do primeiro no
MetaBus. Todas as operações do servidor devem compartilhar o mesmo primário,
com carregamento do catálogo uma única vez, somente quando necessário para
execução. A criação concorrente deve conservar a identidade.

## Critérios de Aceitação Executáveis

- `identidade` — biblioteca, coordenador autônomo e workflow usam o mesmo
  objeto MarceloClaro, independentemente da ordem de criação ou concorrência.
- `carregamento` — a interface leve permanece sem catálogo; o primário carrega
  agentes idempotentemente ao passar à coordenação de execução.
- `especificacao` — análise/revisão de texto pode registrar uma spec dinâmica
  antes de executar. Esse contrato declara critérios heurísticos de texto,
  não é entrega de software, prova científica ou substituto de RED→GREEN.
  Entradas inválidas não criam o primário. O template informa spec_id e o gate
  de software permanece fechado quando faltam contrato ou histórico.

O novo tool não invoca modelos nem escreve aplicações. Software mantém os
contratos existentes. Specs dinâmicas pertencem à sessão MCP; a CLI exige
spec carregável e não reutiliza um ID transitório de outro processo.
