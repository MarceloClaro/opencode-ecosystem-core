---
spec_id: SPEC-935-R755
title: Teorema de Eficiência do Roteamento por Atenção (Análogo Transformer)
component: transformer/attention, plugins/lean-nucleo-verificacao/teoremas, tests/test_r755
status: proposed
round_id: R755
test_file: tests/test_r755_teorema_roteamento.py
---

# SPEC-935-R755 — Teorema de Eficiência do Roteamento por Atenção

## 1. Fundamento no código real

`transformer/attention.py`: `AttentionRouter` com 4 cabeças (`semantic 0.30`,
`capability 0.35`, `confidence 0.25`, `load 0.10`), `_validated_weights` exigindo
combinação convexa (soma 1, cada peso em `[0,1]`), `_softmax` com subtração do máximo
(estabilidade, como no Transformer) e ranking ordenado do melhor ao pior com pesos
somando 1. Hard gates antes de qualquer score; heurística determinística auditável,
não rede neural treinada.

## 2. Definição honesta de eficiência (sem overclaim)

"Mais eficiente" aqui significa **ótimo relativo à utilidade definida**, em 3 sentidos
precisos — nunca superioridade universal sobre outros orquestradores:

- **E1 calibração:** pesos de atenção formam distribuição de probabilidade (somam 1,
  cada um em `(0,1)`); escores finais ficam limitados pelos componentes.
- **E2 limitação convexa:** com pesos somando 1, o score combinado nunca escapa ao
  intervalo dos scores das cabeças — sem explosão, sem ambiguidade (o que
  `_validated_weights` impõe por `ValueError`).
- **E3 otimalidade gulosa:** a seleção top-1/top-k retorna candidato(s) de utilidade
  máxima — nenhum outro elegível tem utilidade maior. Complexidade `O(n log k)`
  documentada como propriedade medida da implementação, não como teorema.

## 3. Teoremas (Lean + Mathlib, `machine_checked` via lake-env R754)

Arquivo: `plugins/lean-nucleo-verificacao/teoremas/roteamento_atencao.lean`

- **T1 `softmax_soma_um`:** `∑ i, (exp (f i) / ∑ j, exp (f j)) = 1` (tipo finito não-vazio).
  Prova: `Finset.sum_pos` (exp > 0) + `Finset.sum_div` + `div_self`.
- **T2 `combinacao_convexa_limitada`:** pesos não-negativos somando 1 e `x i ≤ M`
  implicam `∑ w i * x i ≤ M`. Prova: `Finset.sum_le_sum` + `mul_le_mul_of_nonneg_left`
  + `Finset.sum_mul` + `hsum`.
- **T3 `roteamento_guloso_otimo`:** existe `melhor ∈ candidatos` com utilidade ≥ todas.
  Prova: `Finset.exists_max_image`.
- **T4 `softmax_invariante_max` (R756):** subtrair constante `c` não muda os pesos.
  Prova: `Real.exp_sub` + `Finset.sum_div` + `field_simp` (fecha sozinho).
- **T5 `softmax_mem_Ioo` (R756):** cada peso em `(0,1)` com `Nontrivial`.
  Prova: `div_pos` + `div_lt_one` + `Finset.add_sum_erase` + `linarith`.
- **T6 `combinacao_convexa_limitada_baixo` (R756):** `m ≤ ∑ w·x` (espelho de T2).
- **T7 `softmax_peso_total_singleton` (R758):** candidato único recebe peso 1
  (`∀ j, j = i`), complementando T5. Auditoria `#print axioms`: 7/7 só com
  `[propext, Classical.choice, Quot.sound]`, sem `sorryAx` (`bancada/axiomas.txt`).
- **T8 `peso_cresce_com_escore` (R761):** peso estritamente crescente no
  próprio escore — justifica a regra de decisão.
- **T9 `topk_dominam_resto` (R761):** take k de lista pairwise-decrescente
  domina o resto — o padrão top-k do ranking.
- **T10 `temperatura_aguca_maximo` (R763):** esfriar aumenta o peso do
  maximizador único — nitidez sem limites (forma elementar da calibração).
- **T11 `sem_overflow_apos_max` (R763):** expoentes ≤ 0 após majorante —
  ausência de overflow do truque numérico.

## 4. Aceite (`tests/test_r755_teorema_roteamento.py`)

1. Arquivo `.lean` existe com os 11 nomes de teorema e sem `sorry`/`admit`.
2. `lean_verify(código, project_dir=demo)` → `machine_checked`.
3. `bancada/axiomas.txt` contém os 11 nomes e nenhum `sorryAx`.

## 5. Contraprova e ablação (R758, `bancada/`)

- `contraprova_float.py`: 20k vetores, 0 violações (soma, limites,
  invariância shift, argmax, singleton, vazio).
- `bancada_ablacao.py --qw {0.3,0.6,0.9}`: confiança embaralhada/anti/ruidosa,
  `media_igual`, `sem_confianca`, diffs pareados + taxa de vitória.

## 6. Invioláveis

- Nenhuma alegação de "orquestrador mais eficiente do mundo"; só otimalidade relativa provada.
- `sorry`/`admit` bloqueiam; sem projeto lake+Mathlib, máximo `syntax_verified`.

## 7. Índice complementar de cobertura documental (R809)

Esta seção associa os nomes já descritos em T1–T3 e T5 a suas rodadas para
auditoria de correspondência entre o arquivo Lean e a SPEC. O índice preserva
o escopo dos enunciados existentes e não comprova compilação Lean nesta revisão,
validação externa ou equivalência automática entre a prova e o código Python.

- `softmax_soma_um` (R755): soma dos pesos softmax igual a 1 em tipo finito não vazio.
- `combinacao_convexa_limitada` (R755): limite superior da soma convexa sob pesos
  não negativos de soma 1 e componentes limitados por um majorante.
- `roteamento_guloso_otimo` (R755): existência de elemento de utilidade máxima
  em conjunto finito não vazio.
- `softmax_mem_Ioo` (R756): pesos softmax estritamente entre 0 e 1 sob as
  hipóteses `Nonempty` e `Nontrivial`; a maiúscula de `Ioo` integra o identificador.
