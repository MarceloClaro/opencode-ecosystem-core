# Dossiê Cultural R360 — Molambudos

## Estatuto

Este documento é uma **auditoria heurística interna** de doze segmentos. Ele
**não constitui validação cultural externa**, parecer nativo independente ou
autorização de publicação. A **revisão humana** bilíngue e temática continua
obrigatória; o **release bloqueado** é mantido em todos os casos. Houve
**nenhuma alteração automática** no manuscrito ou nos glossários.

## Método e rastreabilidade

- 6 unidades × 2 variantes-alvo = 12 execuções do `cultural-episteme-agent`.
- Cada sessão está identificada no JSON e nas tabelas abaixo.
- Duas respostas tiveram chaves idempotentes divergentes; foram rejeitadas pelo
  gate e corrigidas pelas mesmas sessões antes da persistência.
- Os envelopes persistidos são compactações contratuais das conclusões centrais;
  a saída integral permanece vinculada ao ID da sessão runtime.
- Spans, hashes, preflight e decisões podem ser recalculados localmente.
- Scores são sinais internos não calibrados e não provam qualidade.

## Curral do Governo

EN e ZH preservam a metáfora de gado, mas deixam a categoria institucional vulnerável à opacidade. A troca simples por concentration camp/集中收容营 faria o movimento inverso: explicaria a instituição e poderia apagar a anáfora animalizante.

| Alvo | Gate derivado | Principais códigos | Sessão |
|---|---|---|---|
| en-US | `human_review` | HISTORICAL_SOURCE_GAP, OVERLOCALIZATION, TERM_CONFLICT | `ses_041c58f80ffexxPfy8pXv1CJ9A` |
| zh-CN | `human_review` | CULTURAL_LOSS, PRAGMATIC_FAILURE, TERM_CONFLICT, VOICE_SHIFT | `ses_041c58f4affez18ObsmAVlAYvm` |

## Retirantes

A retenção EN evita equivalência jurídica falsa, mas exige uma glosa acessível. 逃荒者 comunica fuga por escassez, porém não contém sozinho a seca cearense e pode domesticar o referente por uma matriz histórica chinesa.

| Alvo | Gate derivado | Principais códigos | Sessão |
|---|---|---|---|
| en-US | `human_review` | LITERALISM, TERM_CONFLICT, UNDERLOCALIZATION | `ses_041c58f0fffey6pWdzr08GMsyN` |
| zh-CN | `human_review` | CULTURAL_LOSS, LITERALISM, TARGET_VARIETY_USAGE_RISK | `ses_041c58ee0ffe1rdzZRje394SWa` |

## Rasga Mortalha

Shroud-Ripper e 裹尸布撕裂者 preservam a etimologia, mas podem parecer epítetos góticos inventados. Retenção, glosa e repetição global precisam ser decididas em conjunto; R356 promete uma glosa ZH ainda não visível no recorte.

| Alvo | Gate derivado | Principais códigos | Sessão |
|---|---|---|---|
| en-US | `human_review` | DOMESTICATION_ERASURE_RISK, LITERALISM, SYMBOL_DRIFT | `ses_041c58eb7ffekeLqjqGhOezfLH` |
| zh-CN | `human_review` | LITERALISM, PRAGMATIC_FAILURE, REGISTER_SHIFT, TERM_CONFLICT | `ses_041c58e83ffe5sn0Y3nIHKLDqj` |

## Molambudos

A retenção EN preserva o termo-título, condicionada a glosa única. Em ZH, a alternância 莫兰布多斯→破衣人 dentro da mesma cena enfraquece a repetição que liga insulto, praga, categoria social e título.

| Alvo | Gate derivado | Principais códigos | Sessão |
|---|---|---|---|
| en-US | `human_review` | PRAGMATIC_FAILURE, REGISTER_SHIFT, TERM_CONFLICT | `ses_041c58e51ffeiptwO2UIgaHhzx` |
| zh-CN | `human_review` | DOMESTICATION_ERASURE_RISK, PRAGMATIC_FAILURE, SYMBOL_DRIFT, TERM_CONFLICT | `ses_041c58dfbffeTI31oDYwOereUs` |

## Hospital Colônia

Hospital-Colony pode sugerir calque ou colônia territorial; 收容院 pode reduzir um nome próprio a categoria genérica de asilo/abrigo. Nome histórico, forma curta e alegações factuais exigem revisão temática e fontes.

| Alvo | Gate derivado | Principais códigos | Sessão |
|---|---|---|---|
| en-US | `insufficient_context` | HISTORICAL_SOURCE_GAP, LITERALISM, TERM_CONFLICT | `ses_041c58dc4ffew5hXH6W50EoxNN` |
| zh-CN | `human_review` | DOMESTICATION_ERASURE_RISK, HISTORICAL_SOURCE_GAP, PRAGMATIC_FAILURE, TERM_CONFLICT | `ses_041c58d74ffeRVhN4opcWtY3bh` |

## Você é o próximo

EN mantém a ameaça direta sem modalização no recorte. ZH mantém 你就是下一个, mas há indícios de sintaxe calcada nos locativos e de mudança do motivo de transmissão para invasão em 进入你.

| Alvo | Gate derivado | Principais códigos | Sessão |
|---|---|---|---|
| en-US | `candidate_for_human_review` | nenhum indício no escopo | `ses_041c58d3dffen1L4h81q2G2EtY` |
| zh-CN | `revise` | LITERALISM, SYMBOL_DRIFT, TARGET_VARIETY_USAGE_RISK | `ses_041c58d07ffeaGy2ZvSx6f0HD8` |

## Decisões humanas pendentes

1. arbitrar a estratégia dupla de Curral do Governo sem apagar instituição nem metáfora.
2. definir retenção, glosa e usos posteriores de retirantes.
3. decidir retenção/calque/glosa de Rasga Mortalha nas recorrências.
4. definir o escopo de 莫兰布多斯 versus 破衣人.
5. fixar o nome histórico Hospital Colônia e suas formas curtas em EN/ZH.
6. confirmar por revisão nativa a manutenção da ameaça e do motivo de transmissão.

## Resultado seguro

Os pareceres identificaram conflitos terminológicos, riscos de literalismo,
apagamento/domesticação, mudança simbólica, registro e lacunas históricas. A
versão EN da ameaça não gerou preocupação candidata neste recorte, mas isso
significa apenas ausência de indício no escopo examinado. Nenhuma recomendação
foi aplicada, nenhum delta foi aprovado e todos permanecem `proposed`.
