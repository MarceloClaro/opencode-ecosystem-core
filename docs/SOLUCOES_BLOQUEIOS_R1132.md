# Rotas de desbloqueio — PEC 2q, ZNE, layouts e funções de corte

**Data:** 2026-11-10
**Status:** rotas offline implementadas; nenhum gate declarado desbloqueado
sem dados de hardware.

## 1. PEC 2q e as 2 funções de corte

### O que a literatura mostra

- **Chen et al., PRX Quantum 7, 010305 (2026), DOI `10.1103/1pnv-t9px`**:
  aprendizagem autoconsistente do gate set inteiro (SPAM, 1q, CZ) com ansatz
  linear; caracteriza os graus aprendíveis e aplica-se a CZ paralelo e ruído
  local/quase-local. Código: `github.com/csenrui/PauliGST`.
- **Calzona et al., Phys. Rev. Research 8, 013111 (2026), DOI
  `10.1103/4hbl-hpl3`**: MLCB analisa múltiplas camadas conjuntamente e reduz
  graus não aprendíveis em até 75%, melhorando modelos esparsos e PEC.
- **Chen et al., PRX Quantum 7, 033045 (2026), DOI `10.1103/69wc-gzl6`**:
  quando os parâmetros aprendíveis são caracterizados autoconsistentemente,
  os graus de gauge não impactam predições de dinâmica ruidosa nem a mitigação;
  a escolha de gauge afeta o overhead de amostragem.

### O que foi implementado

`quantum_mitigation/solution_audit.py`:

- adiciona um vetor do espaço de corte às taxas;
- verifica que as **13 funções do desenho não mudam** (`learnable_change < 1e-12`);
- verifica que as **15 fidelidades individuais mudam** (`fidelity_change > 1e-12`);
- retorna `direct_15_rate_pec_allowed=False` e a rota GSPN/MLCB.

Isso mostra que as 2 funções de corte são gauge para o desenho de 13 funções.
**Não** prova que PEC esteja desbloqueado: a invariância de PEC para qualquer
observável exige o modelo autoconsistente e validação fora do treino.

### Próximo passo para PEC

1. Implementar o gate set Pauli noise learning (GSPN) com ansatz declarado,
   incluindo SPAM, 1q e CZ.
2. Usar MLCB para reduzir os graus não aprendíveis.
3. Otimizar o gauge para o observável e o overhead de amostragem.
4. Validar em simulação e em dados independentes; só então reavaliar PEC 2q.

## 2. ZNE não monotônico

### Técnica

**Russo & Mari, Phys. Rev. A 110, 062420 (2024), DOI
`10.1103/PhysRevA.110.062420`**: layerwise Richardson extrapolation (LRE).
Cada camada tem sua própria escala; os coeficientes vêm de interpolação de
Lagrange multivariada. Não se assume uma única escala global monotônica.

### O que foi implementado

`quantum_mitigation/lre.py`:

- `lagrange_coefficients` (escalas 1,2,3 → `[3,−3,1]`);
- `lre_design` com `3^L` configurações;
- `global_design` para comparação;
- `synthetic_audit` com modelo multilinear `E(x)=offset+Σ slope_i x_i`.

No modelo multilinear, a LRE recupera o zero-ruído com erro `< 1e-12`.
Isso valida a aritmética; **não** valida o Baihua nem resolve drift/interações.

### Limite

A LRE exige mais configurações e um modelo de ruído por camada. Se o ruído
não for multilinear, são necessárias mais escalas ou outro modelo. O gate
`monotônico` do ZNE global pode ser substituído por um gate de **adequação do
modelo LRE**, não por uma promessa de ganho.

## 3. Comparação de layouts

### Técnica

- `within_pair`: mesmo par físico, comparar compiladores/estratégias;
- `layout_randomized`: pares físicos diferentes, com atribuição AB/BA
  randomizada e pareada;
- covariável `r1`;
- `n` por aproximação normal pareada;
- regra: só comparar com `enough_pairs` e `confound.allowed`.

### O que foi implementado

`quantum_mitigation/layout_design.py`:

- `paired_sample_size`;
- `randomized_assignment` (balanceada, determinística por seed);
- `confound_audit` (bloqueia 0/1 vs 106/107 sem randomização);
- `build_preregistration` com `hardware_submission_allowed=False`.

O caso anterior (baseline 0/1, otimizado 106/107) é classificado como
**confundido** se não houver randomização. O r1 físico de ~0,08 continua acima
do gate de 0,05; mitigação de leitura não o reduz. A solução é reportá-lo como
limitação/covariável ou melhorar a calibração, não apagá-lo.

## 4. Contraprova Lean e Mathlib

- O cache do Mathlib está presente: `lake exe cache get` reporta 8.908
  arquivos já descompactados; `.lake/packages/mathlib/.lake` tem 6,7 GB.
- O job dedicado `MathlibCounterproof.lean` compilou com `lake env lean`,
  retorno **0**. `rank_D` usa `Matrix.rank_le_height` e
  `Matrix.rank_mul_le_left`; as identidades finitas usam `native_decide`
  (338 axiomas nativos em `D_mul_R`, um em `C_independent`).
- A contraprova leve continua em Lean 4 core:
  `lean/quantum-cb/QuantumCB.lean`. Ela não prova o canal quântico, o twirl
  ou o hardware; Mathlib também não.

## 5. O que continua bloqueado

| Item | Status | Falta |
|---|---|---|
| PEC 2q | rota definida, não desbloqueado | GSPN/MLCB + dados + validação |
| 2 funções de corte | gauge, não medidas | modelo autoconsistente/hipótese física |
| ZNE | rota LRE, não validada | dados layerwise + modelo adequado |
| Layouts | desenho pronto, não executado | pares randomizados + r1/drift |
| Twirl/frame | simulado | compilação física e ruído real |
| Superfície | bloqueado | decoder em tempo real |

Nenhuma taxa foi medida; nenhum hardware foi executado nesta rodada.

## 6. Reprodução

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/solution_audit.py \
  --out /tmp/opencode/solutions.json
.venv-quantum/bin/python -m pytest tests/test_r1132_solutions.py -q
```
