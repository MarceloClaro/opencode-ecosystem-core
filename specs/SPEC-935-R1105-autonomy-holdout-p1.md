# SPEC-935-R1105 — P1: harness de autonomia e tarefas reservadas

Data: 2026-11-12. Estado: harness implementado e validado com adaptadores
scriptados; nenhum modelo externo executado nesta fase.
Evidência: `docs/research/iit-autonomia-r1103/p1-verification.md`.

Origem: `specs/SPEC-935-R1104-iit-metrics-p0.md` e
`docs/research/iit-autonomia-r1103/experiments.json`.

## Escopo

Criar a infraestrutura reproduzível para o experimento A0–A4:

- Conjunto de tarefas reservadas (`heldout`) com resposta verificável,
  evidência, risco e política de abstenção.
- Harness de avaliação que aceite qualquer adaptador de agente e calcule:
  correção, Brier, risco-cobertura, repetição de erros, ações não autorizadas,
  custo por tarefa correta e suporte de citação.
- Adaptador scriptado para validar o harness sem chamar modelo, rede ou
  executor externo.
- Relatório de dry-run explicitamente rotulado como validação do harness,
  não como resultado de modelo.

## Fora do escopo

Não executar Codex, Antigravity, Claude ou qualquer LLM. Não instalar
dependências. Não alterar permissões. Não promover trust. Não declarar
melhoria de autonomia, consciência ou Φ. A execução A0–A4 com agentes reais
depende de executor com autenticação/saúde verificadas e autorização própria.

## Critérios de aceitação

- CA01: `benchmarks/autonomy_tasks.json` contém pelo menos 12 tarefas
  reservadas, com IDs únicos, categorias, evidência, resposta esperada, risco
  e custo máximo.
- CA02: o loader valida schema e rejeita ID duplicado, ação inválida,
  resposta ausente e citação inexistente.
- CA03: o harness calcula correção, Brier, risco-cobertura, repetição de
  erros, ações não autorizadas, custo por tarefa correta e suporte de citação.
- CA04: o dry-run com adaptador scriptado gera JSON com
  `experiment_status='harness_validation_only_not_model_result'`.
- CA05: nenhum teste ou dry-run chama rede, LLM, MCP ou registry real.
- CA06: testes novos começam RED e terminam GREEN; o subconjunto existente
  de evolução/ecossistema permanece passando.
- CA07: o relatório declara limitações, hash do conjunto de tarefas e
  separação `heldout`/`dev`.
- CA08: repetição de erros é calculada apenas quando há múltiplas tentativas;
  sem tentativas repetidas, o campo é `null`, não zero inventado.
- CA09: suporte de citação distingue precisão, recall e F1; tarefas sem
  citação obrigatória não entram no denominador.
- CA10: o harness não declara superioridade de nenhuma política; apenas
  mede o adaptador fornecido.

## Plano TDD

1. `tests/test_r1105_autonomy_harness.py` cobre CA01–CA10.
2. Executar RED.
3. Implementar `benchmarks/autonomy_tasks.json` e
   `benchmarks/autonomy_harness.py`.
4. Executar GREEN, dry-run e testes de evolução/ecossistema.
5. Registrar evidência em
   `docs/research/iit-autonomia-r1103/p1-verification.md`.

## Evidência de conclusão

- Saída RED/GREEN.
- `p1-harness-dry-run.json` com status de validação.
- Hash do conjunto de tarefas.
- Declaração explícita de que A0–A4 com agentes reais não foi executado.
