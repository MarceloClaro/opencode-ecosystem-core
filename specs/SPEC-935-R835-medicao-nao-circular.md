# SPEC-935-R835 — Medição lexical não circular

Status: proposed

## Problema observado

A revisão dirigida R3 identificou duas projeções de `behavioral_gate`, um corpus
de autodescoberta produzido com nomes e termos dos próprios arquivos e testes
que verificavam presença desses nomes. Esse procedimento mede menções lexicais
do inventário; não mede correção, qualidade epistêmica ou execução funcional.
`successor_generator` também aparece em duas dimensões do mesmo inventário.

## Contrato

1. Cada categoria tem um identificador e proprietário canônicos únicos. A visão
   `protocolos.behavioral_gate` é um alias da implementação em `trust_economy`;
   `evolucao.successor_generator` é um alias da categoria de `scanners`. Aliases
   preservam os consumidores de dimensão, sem aumentar denominadores, cobertura
   global ou cobertura de camadas. O vocabulário canônico é único por categoria.
2. A autodescoberta existente continua disponível com escopo explícito:
   `autodiscovery_lexical`, `functional_validation: false`,
   `externally_validated: false`, confiança não calibrada. Cem por cento de
   menções nunca representa completude do produto ou conhecimento.
3. O pipeline aceita `corpus_mode="retained"` sem ler/enriquecer o corpus com
   arquivos do Core. Exige identificador, SHA-256 esperado e correspondência
   exata dos bytes UTF-8. O relatório registra hashes de entrada/medição, tamanho
   e `retained_input_lexical`. A origem externa declarada não é validação externa.
4. O corpus retido de aceitação é um trecho do despacho humano de revisão R3,
   guardado sem construção a partir do mapa de palavras-chave. É entrada de
   regressão local, não benchmark independente de qualidade ou segurança.
5. Corpus vazio tem densidade zero. `z3 staking sdd tdd` não tem cobertura de
   cem por cento. Negação e fronteiras lexicais permanecem aplicáveis.
6. A entrada fornecida participa da chave de cache da autodescoberta; a ordenação
   do corpus não depende da ordem de conclusão das leituras concorrentes.

## Aceitação e evidência

`tests/test_r835_medicao_nao_circular.py` deve registrar RED antes das mudanças,
GREEN depois, valores tipados, contagens de categorias canônicas, aliases,
hashes, negação e exclusão do enriquecimento em corpus retido. A comparação
funcional continua sendo responsabilidade de testes do comportamento real de
cada motor, fora deste scanner. Recibos em `outputs/core-r835/`.

O diagnóstico de saúde prévio foi executado pelo orquestrador: 22/22,
`outputs/core-r829/doctor-before-review-repair.json`. A decisão final é humana;
esta especificação não autoriza alegar suíte global aprovada ou validação externa.

## Corpus congelado e medida executada

`tests/fixtures/r835-review-heldout.txt`: trecho do despacho humano R3,
SHA-256 UTF-8 `36596b3048f3dcce8f701abb99cceb33a9e485bc9a78463e30b80359a4f5d9bf`.
Na execução local registrada em `outputs/core-r835/retained-diagnostic.json`,
foram encontradas 4 de 81 categorias canônicas (5% arredondado). Trata-se de
menções contidas no trecho, sem representar cobertura funcional do ecossistema.
O corpus vazio mediu 0/81; `z3 staking sdd tdd`, 4/81; as duas categorias com
aliases, 2/81. Esses valores resultam do scanner executado, não de fixture de
percentual de cobertura.
