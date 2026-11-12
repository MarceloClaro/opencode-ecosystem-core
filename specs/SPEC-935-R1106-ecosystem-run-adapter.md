# SPEC-935-R1106 — EcosystemRunAdapter para o harness P1

Data: 2026-11-12. Estado: adaptador implementado e testado com coordenador
falso; nenhuma execução real nesta fase.
Evidência: `docs/research/iit-autonomia-r1103/p1-verification.md`.

Origem: `specs/SPEC-935-R1105-autonomy-holdout-p1.md`.

## Escopo

Converter o resultado do `AutonomousCoordinator` em `Response` do harness P1,
com política fail-closed e sem inventar custo, confiança ou citação.

O adaptador:

- recebe `TaskView` (sem gabarito);
- monta um prompt com formato JSON explícito e evidência delimitada;
- chama `coordinator.run(...)` somente quando injetado ou quando o operador
  solicitar uma execução real;
- converte `status/success/output` em `Response`;
- retorna `abstain` em bloqueio, falha, saída vazia, JSON inválido, ação
  inválida ou resposta ausente;
- marca `cost=None` quando o coordenador não fornece custo financeiro;
- define `unauthorized_actions=0` por construção, pois o escopo é leitura e
  geração de texto; nenhuma ferramenta é executada pelo adaptador.

## Fora do escopo

Não executar Codex, Antigravity, Claude ou qualquer LLM nos testes. Não
alterar o coordenador, permissões, Blackboard ou MetaBus. Não promover trust.
Não declarar que uma execução real ocorreu.

## Critérios de aceitação

- CA01: `EcosystemRunAdapter.run(TaskView, attempt) -> Response` e
  `kind='ecosystem_run'`.
- CA02: saída JSON válida é convertida em `action`, `answer`, `confidence` e
  `citations`.
- CA03: bloqueio, falha, saída vazia, JSON inválido, ação inválida e resposta
  ausente resultam em `abstain` com `error_type` e `reason`.
- CA04: o prompt não contém `expected_action`, `expected_answer` ou
  `required_citations`; o gabarito permanece fora do adaptador.
- CA05: `cost=None` quando não há medição; o harness não calcula custo por
  acerto como zero.
- CA06: testes usam coordenador falso; nenhuma chamada externa.
- CA07: exceção do coordenador vira `abstain` com `error_type='adapter_exception'`.
- CA08: testes RED→GREEN; estado de produção inalterado.
- CA09: `unauthorized_actions=0` é estrutural e documentado; o adaptador não
  executa ferramentas.
- CA10: relatório do harness marca resultado externo como não verificado
  independentemente.

## Plano TDD

1. `tests/test_r1106_ecosystem_adapter.py` com coordenador falso.
2. RED.
3. Implementar `benchmarks/ecosystem_run_adapter.py` e ajustar o custo
   opcional no harness.
4. GREEN e regressão P1/P0.
5. Registrar em `p1-verification.md` que o piloto real continua bloqueado.
