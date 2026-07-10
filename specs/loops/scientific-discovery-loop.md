# scientific-discovery — Loop Specification

**Descrição:** Repete o pipeline R101-R105 (scientific_discovery_pipeline) ate atingir o gate de exportacao do R103 ou um estado terminal de parada (no_op/blocked/stalled/exhausted/error).

**Use quando:** Uma unica rodada do pipeline cientifico nao atingiu o gate de qualidade (export_gate_passed) e vale a pena tentar novas rodadas de EvoSci/Deep Research antes de desistir.

## Trigger
- Tipo: `manual`
- Justificativa: O resultado de cada rodada (gate passou/reprovou, readiness_score) muda a decisao da proxima rodada (continuar, parar por estagnacao, ou parar por orcamento) — satisfaz a 'golden rule' do loop engineering: ha feedback real entre voltas.

## Objetivo e Verificação
- Objetivo: R103 aprova export_gate_passed e R104d/R105 completam com sucesso.
- Verificável: sim
- Nível na escada de verificação: **1** (zona: autonomous)
- Check real: export_gate_passed do R103 (threshold deterministico sobre traceability/coverage do AuditGraph) — zona autonoma da escada de verificacao, sem juiz de modelo envolvido.

## Arquitetura
- `solo`

## Estados Terminais Nomeados
- `success`
- `no_op`
- `blocked`
- `stalled`
- `exhausted`
- `error`

## Regra de Parada
- Detector de estagnação: janela=3, limiar=0.02
- Teto de orçamento: 5 iterações

## Memória
- mci.metabus.metabus.memory (episodic + confidence_ledger, persistido em .mci_state/)

## Guardrails
- Erro nao tratado interrompe o loop imediatamente (nao tenta mascarar como sucesso)
- Estagnacao (variacao de readiness_score < limiar por 'window' rodadas) para o loop antes do teto de orcamento
- R101 sem nenhuma ideia gerada e classificado como no_op, nao como falha

## Boa-formação (checklist automático)
- `well_formed`: True
