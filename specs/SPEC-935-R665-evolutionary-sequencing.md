---
spec_id: SPEC-935-R665
title: Sequenciamento evolutivo condicionado a evidencias e payoffs explicitos
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R663_R666_RELEASE_GATE.json
component: scanners/evolutionary_sequencing.py + scanners/trajectory_mapper.py + gametheory/phd_auditor.py
test_file: tests/test_r665_evolutionary_sequencing.py
---

# R665 — Sequenciamento de trajetórias e análise de jogos

## Contratos

1. O sequenciador recebe capacidades e dependências declaradas com referências
   de evidência, sem inferir que uma dependência plausível seja uma necessidade
   científica demonstrada. `requires` e `enables` usam a orientação de R483/R485;
   `co_occurs` permanece afinidade, sem impor precedência.
2. Retornar fechamento dos alvos, predecessoras/sucessoras, dependências e
   evidências faltantes, ciclos e seus descendentes bloqueados, fases paralelas,
   convergências e rotas limitadas em ordem determinística. Capacidade observada
   poda a regressão apenas quando sua evidência foi fornecida.
3. Cronograma, custo e resistência são estimativas condicionais fornecidas pelo
   chamador. Valores ausentes continuam desconhecidos; nenhum tempo real ou
   recurso disponível é presumido. Fases lógicas não garantem disponibilidade
   de recursos para executar em paralelo. Rotas são cadeias de precedência,
   não alternativas que dispensam outras dependências do plano.
4. R485 oferece acesso ao contrato novo sem mudar a semântica de sua API antiga.
   Não executar rede, modelos, subprocessos ou persistência no sequenciador.
5. Nash puro e fronteira de Pareto usam payoffs reais, com estratégias por eixo
   do tensor, incluindo jogos retangulares e mais de dois jogadores. Validar
   tensores inconsistentes, valores não finitos, nomes inválidos e espaços
   excessivos. Não anunciar equilíbrio misto que não esteja implementado.

## Critérios de aceitação executáveis

- `R665-DAG` — Precedência, fechamento, ausências, ciclos e fases corretos.
- `R665-ESTIMATES` — Estimativas rotuladas, desconhecidos propagados e custos
  de rotas/convergências calculados sem dupla contagem no plano completo.
- `R665-PARETO` — Dominância real, Nash puro retangular/N jogadores e validação.
- `R665-COMPATIBILITY` — Regressões R483/R485 e jogos clássicos preservadas.

## Evidência

RED → GREEN, regressões e limites registrados no gate local da rodada.
R665 cobre 39 casos. A mutação que admite perfis dominados é detectada pelo
teste de Pareto. Entradas sintéticas validam o algoritmo e não constituem
descoberta ou validação clínica.
