# dsh-reasoning-97 — Loop Specification

**Descrição:** Loop reflexivo raciocinado da ponte DeepSeek Harness até o gate 97: pré-raciocínio (ensemble 12 motores) → execução dsh → ingestão → calibração + grading → reflexão e refinamento iterativo.

**Use quando:** Uma produção autônoma do dsh não atingiu o gate calibrado 0.97 e há orçamento de iterações restantes sem estagnação.

## Trigger
- Tipo: `manual`
- Justificativa: Cada iteração consome execução do harness e raciocínio; decisão de continuar depende do resultado calibrado e do grading da volta anterior.

## Objetivo e Verificação
- Objetivo: calibrated_confidence>=0.97 e grade.score>=6 (gate 97)
- Verificável: sim
- Nível na escada de verificação: **1** (zona: autonomous)
- Check real: calibrate_confidence com sinais fortes (p<0.001, effect>=0.8, BF>=100) e GradingHead 0-7 com nota >=6; ambos determinísticos e auditáveis.

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
- mci.metabus.metabus.memory (episodic + semantic deepseek_harness.*)

## Guardrails
- Erro de execução não é sucesso — registra error e continua se houver orçamento.
- Estagnação (variação <0.02 em 2 iterações) encerra como stalled.
- Gate 97 só é verdadeiro com eventos reais do runner (status completed).

## Boa-formação (checklist automático)
- `well_formed`: True
