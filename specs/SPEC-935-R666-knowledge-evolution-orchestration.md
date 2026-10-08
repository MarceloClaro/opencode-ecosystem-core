---
spec_id: SPEC-935-R666
title: Orquestração evidenciada da evolução do conhecimento e pesquisa reproduzível
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R663_R666_RELEASE_GATE.json
component: marceloclaro/knowledge_evolution.py + marceloclaro/science_cli.py + mci/metabus.py
test_file: tests/test_r666_knowledge_orchestration.py
---

# R666 — Potenciais, composição e sequenciamento sob o orquestrador central

1. Entradas finitas e limitadas são validadas antes de eventos, escrita ou rede.
2. O DNA representa capacidades declaradas e suas evidências; presença de código,
   importação, rótulo ou planejamento não comprovam execução.
3. Integrar R664 (potenciais/composição), R665 (dependências/sequenciamento) e
   convergência polimática em um relatório determinístico com fontes e limites.
4. Separar hipótese, execução local, reprodução computacional e validação externa.
   Ciclos, dependências desconhecidas e critérios ausentes permanecem explícitos.
5. CLI e MCP passam pelo MarceloClaroOrchestrator, que publica eventos no MetaBus
   e registra observações sem aumentar automaticamente o confidence ledger.
6. Integrar R663 para percurso científico executado e rastreável, preservando
   bloqueios, hashes, revisão computacional e declarações de limites.
7. Regenerar opencode.json, testar regressões e registrar ciclos sem avaliação
   externa fictícia. Probes com dados públicos reais ficam separados dos testes.

## Aceitação

- R666-PLAN: planos distinguem disponibilidade de execução e preservam lacunas.
- R666-META: observações persistem sem promover confiança ou validação externa.
- R666-SURFACES: interfaces compartilham o orquestrador e rejeitam entradas inválidas.
- R666-REAL: prova local de pergunta, referências, dados reais, cálculo, reprodução,
  revisão computacional e artefatos com hashes.

## Evidência local

- 19 testes R666 e regressões combinadas: 723 aprovados, um PDF ignorado
  por dependência opcional ausente. Quatro mutações isoladas foram detectadas.
- CLI executa Pearson; MCP executa Welch e conecta o resultado ao planejamento
  pelo mesmo orquestrador. Duas reexecuções em processos separados coincidem.
- `docs/evidence/R663_R666_REAL_20261004_114400/probe.json` conserva recibos HTTP,
  transformação de dados e hashes do código efetivamente executado.
- Estado `green` indica somente aprovação dos contratos no escopo local.
  Não indica revisão humana, replicação independente ou validação externa.
