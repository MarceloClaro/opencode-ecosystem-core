# harness-reasoning-97 — Loop Specification

**Descrição:** Loop universal do Harness OpenCode até gate 97: pré-raciocínio (12 motores) → execução com qualquer modelo (ModelRouter) → calibração + grading → reflexion.

**Use quando:** Produção do harness universal não atingiu gate 97 e há orçamento sem estagnação.

## Trigger
- Tipo: `manual`
- Justificativa: Cada iteração consome execução com modelo roteado; continuar depende do calibrado/grading.

## Objetivo e Verificação
- Objetivo: calibrated>=0.97 e grade>=6 com qualquer task_type/provider
- Verificável: sim
- Nível na escada de verificação: **1** (zona: autonomous)
- Check real: confidence_calibrator + GradingHead 0-7 determinísticos

## Arquitetura
- `maker_checker`

## Estados Terminais Nomeados
- `success`
- `exhausted`
- `error`
- `stalled`

## Regra de Parada
- Detector de estagnação: janela=2, limiar=0.02
- Teto de orçamento: 3 iterações

## Memória
- mci.metabus.metabus.memory (semantic harness.*)

## Guardrails
- Gate 97 só com status completed real; erro não é sucesso.
- Estagnação encerra como stalled.
- task_type/provider/model propagados a cada iteração.

## Boa-formação (checklist automático)
- `well_formed`: True
