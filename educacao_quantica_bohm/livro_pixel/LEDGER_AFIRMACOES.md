# Ledger de afirmações: o que está provado, medido, calculado ou interpretado {#ledger}

> **Regra:** nenhuma afirmação deste livro tem o mesmo status que outra. Uma
> identidade matemática pode ser provada no Lean; um count de hardware é medido;
> uma interpretação é argumentada. O ledger separa os tipos para impedir
> overclaim.

## 1. Tipos de status

| Status | Significado | Como verificar |
|---|---|---|
| **machine-checked** | provado no Lean 4 + Mathlib | `lake env lean QuantumTrails.lean` |
| **calculated** | conta reproduzível à mão ou por script | fórmula + substituição + resultado |
| **measured** | medido em hardware, com data, backend e task ID | JSON/CSV + task ID |
| **measured (simulador)** | medido em simulador da plataforma, não em hardware | JSON + task ID + backend |
| **bibliographic** | referência com DOI/URL verificada | Crossref/DataCite + ficha |
| **interpretive** | interpretação filosófica, não teste empírico | argumento + referência |
| **protocol** | plano de pesquisa, ainda não executado | protocolo + critérios |
| **not verified** | afirmação sem evidência suficiente | marcar para revisão |

## 2. Ledger principal

| Afirmação | Tipo | Evidência | Verificação | Status |
|---|---|---|---|---|
| `H² = I` | matemática | `QuantumTrails.lean`, `H_mul_H` | Lean 4.35.0 + Mathlib | machine-checked |
| `X² = I` | matemática | `QuantumTrails.lean`, `X_mul_X` | Lean | machine-checked |
| `Z² = I` | matemática | `QuantumTrails.lean`, `Z_mul_Z` | Lean | machine-checked |
| `H Z H = X` | matemática | `QuantumTrails.lean`, `H_mul_Z_mul_H` | Lean | machine-checked |
| `(√2)² = 2` | matemática | `QuantumTrails.lean`, `sqrt2_sq` | Lean | machine-checked |
| `(1/√2)² = 1/2` | matemática | `QuantumTrails.lean`, `inv_sqrt2_sq` | Lean | machine-checked |
| `(2√2)² = 8` | matemática | `QuantumTrails.lean`, `quantum_chsh_sq` | Lean | machine-checked |
| `P(0)+P(1)=1` | matemática | `QuantumTrails.lean`, `prob_sum` | Lean | machine-checked |
| CHSH clássico `S ≤ 2` | matemática | `QuantumTrails.lean`, `chsh_classical` | Lean | machine-checked |
| Tabela-verdade do CNOT | matemática | `QuantumTrails.lean`, `cnot` + exemplos | Lean | machine-checked |
| CNOT aplicado duas vezes devolve a entrada | matemática | `QuantumTrails.lean`, `cnot_involutive` | Lean | machine-checked |
| Estado de Bell normalizado | matemática | `QuantumTrails.lean`, `bell_normalized` | Lean | machine-checked |
| CHSH quântico `S = 2√2` | matemática/física | `QuantumTrails.lean`, `chsh_bell_eigen` e `chsh_bell_expectation` | Lean + derivação | machine-checked (caso Bell) |
| Phase damping preserva a população | modelo | `QuantumTrails.lean`, `phaseDamping_p0` | Lean | machine-checked (fenomenológico) |
| Phase damping não aumenta a coerência | modelo | `QuantumTrails.lean`, `phaseDamping_coh_abs_le` | Lean | machine-checked (fenomenológico) |
| Depolarizing normaliza a população | modelo | `QuantumTrails.lean`, `depolarizing_p0_nonneg` e `depolarizing_p0_le_one` | Lean | machine-checked (fenomenológico) |
| Depolarizing em p=1 leva a 1/2 | modelo | `QuantumTrails.lean`, `depolarizing_one_p0` | Lean | machine-checked (fenomenológico) |
| GHZ 4 qubits: 418 e 389 counts | empírico | `dados_experimentos/E06.json`; task IDs | JSON + data | measured |
| Fidelidade proxy 78,81% | empírico/cálculo | `(418+389)/1024` | conta + JSON | calculated |
| Baihua: 437 e 230 counts | empírico | `ghz4_baihua.json` | JSON + data | measured |
| CHSH `S=2,3828` | empírico/cálculo | `chsh_guoji08.json` | conta + JSON | calculated |
| CHSH GJQ no FAS-GPU `S=2,871094 ± 0,043506` | empírico/simulado | `docs/gjq-runtime/chsh-2026-11-08.json`; task IDs | conta + JSON | measured (simulador) |
| Bell GJQ no FAS-GPU: `00`=507, `11`=517 | empírico/simulado | `docs/gjq-runtime/bell-2026-11-08.json`; task ID | JSON + conta | measured (simulador) |
| VQC 4/4 | empírico/cálculo | `vqc_xor_guoji08.json` | JSON + conta | measured |
| Phase damping igual ao baseline | modelo/empírico | `vqc_forte.json` | script + dados | measured/model |
| Ruído benéfico não observado | empírico | 4 pontos, sem curva | dados + limite | measured |
| T1 médio 73,07 µs; T2 26,36 µs | empírico | `calibracao_basica.csv` | CSV | measured |
| `simulator=False` no Guoji08 | empírico | `configuration()` em 7 nov. 2026 | registro | measured |
| 44 DOIs ativos | bibliográfico | `RELATORIO_DOIS.md` | Crossref/DataCite | bibliographic |
| 5 URLs oficiais | bibliográfico | `RELATORIO_DOIS.md` | acesso em 2026-11-07 | bibliographic |
| Bohm é uma interpretação entre várias | interpretativo | Bohm (1952); Bohm & Hiley (1993) | literatura | interpretive |
| Ordem implicada é proposta metafísica | interpretativo | Bohm (1980) | literatura | interpretive |
| Diálogo de Bohm é prática coletiva | interpretativo | Bohm (1996) | literatura | interpretive |
| O livro melhora a aprendizagem | protocolo | `AVALIACAO_EFICACIA.md` | estudo não executado | protocol |
| O livro tem peer review 3/10 | avaliação | `PACOTE_PEER_REVIEW.md` | sem pareceres externos | not verified (pendente) |
| O livro é 10/10 em didática | avaliação | scanners + comparação | julgamento | interpretive |
| Lean prova counts de hardware | falso | Lean não acessa backend | — | not verified (falso) |

## 3. O que o Lean prova — e o que não prova

### 3.1 Prova

- identidades de portas;
- normalização de probabilidades;
- limite clássico de CHSH;
- identidade algébrica do valor quântico;
- tabela-verdade do CNOT.

### 3.2 Não prova

- counts, calibração, fidelidade, ruído;
- que o backend executou o circuito;
- que o estado preparado é puro ou emaranhado;
- que a interpretação de Bohm é verdadeira;
- que o livro ensina melhor;
- que o peer review foi feito.

## 4. Como usar o ledger

1. Antes de citar um número, localize a linha.
2. Verifique o status.
3. Se for `measured`, confira data, backend e task ID.
4. Se for `calculated`, refaça a conta.
5. Se for `interpretive`, não apresente como resultado.
6. Se for `protocol`, não apresente como conclusão.
7. Se for `not verified`, não use em material de divulgação.

> **Regra:** a frase “está no livro” não é evidência. O status é.
