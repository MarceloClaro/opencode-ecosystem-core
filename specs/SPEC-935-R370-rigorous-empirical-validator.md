---
spec_id: SPEC-935-R370
title: RigorousEmpiricalValidator — estatística computada de dados brutos + contraprovas por permutação
component: mci/rigorous_validation.py + agentic_science_v2/review_agent.py
status: draft
test_file: tests/test_r370_rigorous_validation.py
---

# SPEC-935-R370 — RigorousEmpiricalValidator

**Data:** 2026-08-02
**Motivação:** `mci/statistical_validator.py::validate_statistics()` já implementa
correção de múltiplas comparações (Bonferroni/BH), classificação de Cohen's d
e Bayes factor aproximado (Sellke 2001) — mas **valida números já fornecidos
em `context`** (`p_value`, `effect_size`, etc. chegam prontos). Nada no
ecossistema hoje **computa** estatística a partir de dados brutos, roda
validação cruzada real, ou executa uma contraprova genuína (tentativa de
falsificação) contra uma alegação empírica. Este ciclo fecha esse gap para
tornar o pipeline científico (R101→R105) e o orquestrador `/marceloclaro`
efetivamente mais rigorosos, não apenas mais bem documentados.

**Limite epistêmico (obrigatório em todo relatório deste módulo):** nenhuma
função aqui "prova" uma hipótese. Um resultado convergente significa que a
alegação **resistiu a tentativas independentes de falsificação** (permutação
de rótulos, duas famílias de teste, validação cruzada) — não que ela seja
verdadeira, causal ou relevante no mundo real. Interpretação final é sempre
humana (`human_gate=True` em todo relatório).

## 1. Restrição de dependências

Zero dependência de `numpy`/`scipy` (nem declarada em requirements, nem
importada) — segue a convenção já estabelecida em
`mci/statistical_validator.py`, que reimplementa tudo em `statistics`/`math`/
`random` da stdlib. Toda amostragem aleatória usa uma instância local
`random.Random(seed)` (nunca o módulo global `random`), com `seed` parametrizável
e um default fixo por função, para que os testes assertem valores exatos.

## 2. Componentes

### 2.1 `permutation_counter_proof(group_a, group_b, statistic_fn, n_permutations=2000, seed=935370)`

Motor de contraprova genérico e reutilizável:
1. Calcula `observed = statistic_fn(group_a, group_b)`.
2. Agrupa os dois grupos (`pooled = group_a + group_b`), e por `n_permutations`
   iterações: embaralha `pooled` com o `Random(seed)` local, reparte nos
   tamanhos originais de `group_a`/`group_b`, recalcula `statistic_fn` na
   partição embaralhada.
3. `p_value = (1 + count(|permuted| >= |observed|)) / (n_permutations + 1)`
   (correção +1 padrão para nunca reportar p=0).
4. Retorna `{observed_statistic, p_value, n_permutations, seed, null_distribution_summary}`
   — `null_distribution_summary` traz min/max/mean/stdev da distribuição nula
   gerada (não a lista inteira, para não inchar o relatório).
5. Determinístico: mesma entrada + mesmo `seed` → mesmo `p_value` bit a bit.

### 2.2 `two_sample_hypothesis_test(group_a, group_b, seed=935370, n_permutations=2000)`

Duas lentes independentes sobre os mesmos dados brutos, ambas via
`permutation_counter_proof`:
- **Paramétrica:** estatística de Welch-t (`(mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)`,
  variâncias amostrais via `statistics.variance`).
- **Não-paramétrica:** estatística de Mann-Whitney U (soma de postos via
  `statistics` + desempate por média de postos).
- **Effect size:** Cohen's d (`(mean_a - mean_b) / pooled_stdev`), com IC 95%
  via bootstrap (reamostragem com reposição, `B=2000` por padrão, mesmo
  `Random(seed)` local, percentil 2.5/97.5).
- Requer `len(group_a) >= 3 and len(group_b) >= 3` (fail-closed via
  `ValueError` abaixo disso — amostra insuficiente para permutação
  significativa).

### 2.3 `k_fold_cross_validate(data, k, scorer_fn, seed=935370)`

Harness genérico de validação cruzada:
- Embaralha os índices de `data` com `Random(seed)` local, particiona em `k`
  folds (tamanhos o mais equilibrados possível quando `len(data) % k != 0`).
- Para cada fold: `scorer_fn(train_indices, test_indices) -> float`.
- Retorna `{fold_scores, mean, stdev, coefficient_of_variation, stable}` —
  `stable=False` quando `coefficient_of_variation > 0.5` (limiar fixo,
  documentado como convenção, não tunável por chamada nesta versão).
  **Caso de borda:** quando `abs(mean) < 1e-9` (score médio ~zero, comum em
  scorers como correlação ou delta), `coefficient_of_variation` usa
  `stdev / 1e-9` seria instável/sem sentido — nesse caso o cálculo usa
  `max(abs(mean), 1e-9)` como denominador e o resultado é sinalizado com
  `low_mean_denominator: True` no retorno, para o chamador saber que a
  métrica de estabilidade é pouco informativa ali (nunca lança exceção).
- Cada índice aparece em exatamente um fold de teste (partição exaustiva e
  disjunta) — invariante testada.
- Fail-closed: `k < 2`, `k > len(data)`, ou `data` vazio → `ValueError`.

### 2.4 `convergent_validity_report(group_a, group_b, alpha=0.05, seed=935370, n_permutations=2000)`

Combina 2.2 acima com o veredito já existente:
1. Roda `two_sample_hypothesis_test`.
2. Monta `context` para `mci.statistical_validator.validate_statistics()`
   com `p_value` (do teste paramétrico), `effect_size` (Cohen's d),
   `confidence_interval` (IC bootstrap), `sample_size` (`n_a + n_b`) —
   **reaproveita a função existente sem duplicar a lógica de veredito**.
3. `convergent = True` **se e somente se**:
   - `p_value` paramétrico `< alpha` **e**
   - `p_value` não-paramétrico `< alpha` **e**
   - o sinal do Cohen's d concorda com o sinal da diferença de médias
     (sempre verdadeiro por construção, mas checado explicitamente) **e**
   - o IC bootstrap do effect size **não contém zero**.
4. Retorna envelope com `schema_version`, `convergent`, os dois testes brutos,
   o veredito reaproveitado (`validate_statistics`), `human_gate: True`, e
   `disclaimer` (texto do limite epistêmico da §0, verbatim ou equivalente).

## 3. Integração no R103 (Peer Review)

`agentic_science_v2/review_agent.py::OrchestratorReviewer` ganha
`verify_statistical_claim(claim_id, group_a, group_b, ledger) -> dict`:
- Roda `convergent_validity_report(group_a, group_b)`.
- Se `convergent=True`: chama `ledger.verify_claim(claim_id, notes=<resumo
  com os dois p-values e o effect size>)`.
- Se `convergent=False`: **não** verifica a claim; se ela já não estiver na
  `verification_agenda`, adiciona entrada explicando qual teste discordou
  (ex.: "Mann-Whitney não significante (p=0.18); Welch-t significante
  (p=0.03) — sem convergência").
- Não lança exceção para `convergent=False` — é um resultado válido do
  processo de revisão, não um erro.

## 4. Critérios de aceitação

1. `permutation_counter_proof`: determinístico (mesmo seed → mesmo p-value);
   dois grupos idênticos → p-value alto (não significativo); grupos com
   grande diferença clara → p-value baixo.
2. `two_sample_hypothesis_test`: Welch-t e Mann-Whitney concordam em sinal
   para os mesmos dados; amostra `< 3` por grupo → `ValueError`.
3. `k_fold_cross_validate`: partição exaustiva e disjunta dos índices
   (união = todos os índices, interseção vazia entre folds de teste);
   `k inválido` → `ValueError`; scorer com alta variância entre folds →
   `stable=False`.
4. `convergent_validity_report`: `convergent=True` só quando as quatro
   condições da §2.4 se satisfazem simultaneamente (testado com fixture que
   quebra cada condição isoladamente); `human_gate=True` sempre;
   `disclaimer` sempre presente.
5. `verify_statistical_claim`: claim é verificada no ledger apenas quando
   `convergent=True`; caso contrário, permanece pendente com nota explicativa.
6. Zero import de `numpy`/`scipy` no módulo novo (checado por teste).
7. Suíte do ciclo verde; nenhuma regressão em `test_r103` ou nos testes do
   `statistical_validator` existente.
