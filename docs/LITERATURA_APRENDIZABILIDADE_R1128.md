# Literatura aplicada — aprendibilidade de Pauli e o gargalo do CZ

**Data:** 2026-11-10
**Pergunta:** o posto 9 do desenho somente-CZ é um limite fundamental ou uma
deficiência do desenho? Que técnica real permite avançar?
**Resposta curta:** é uma deficiência do desenho. Para um Clifford de 2 qubits,
o espaço aprendível tem dimensão **13** e restam **2** graus não aprendíveis.
O desenho de 9 órbitas perdia 4 funções por não intercalar Cliffords de 1 qubit.

## Fontes e o que foi efetivamente lido

| Fonte | DOI | Leitura | Uso |
|---|---|---|---|
| Chen, Liu, Otten, Seif, Fefferman & Jiang, *The learnability of Pauli noise*, Nat. Commun. 14, 52 (2023) | `10.1038/s41467-022-35759-4` | texto principal, Teoremas 1–2, Figs. 1–6, seção de experimentos | base do resultado 13/2 e da técnica de Cliffords intercalados |
| van den Berg & Wocjan, *Techniques for learning sparse Pauli-Lindblad noise models*, Quantum 8, 1556 (2024) | `10.22331/q-2024-12-10-1556` | abstract e seções 1–5 do HTML/arXiv:2311.15408v4 | rotações Pauli, correções de 1 qubit, seleção de bases, NNLS |
| van den Berg, Minev, Kandala & Temme, *Probabilistic error cancellation with sparse Pauli–Lindblad models*, Nat. Phys. 19, 1116 (2023) | `10.1038/s41567-023-02042-2` | metadados Crossref e referências; texto não relido nesta rodada | modelo esparso e PEC |
| Blume-Kohout et al., *Demonstration of qubit operations below a rigorous fault tolerance threshold with gate set tomography*, Nat. Commun. 8, 14485 (2017) | `10.1038/ncomms14485` | metadados Crossref/abstract | GST autoconsistente e diamond norm |

Artigos de 2026 identificados na lista de citações, **não lidos** nesta rodada
e não usados como evidência: *Disambiguating Pauli Noise in Quantum Computers*
(`10.1103/69wc-gzl6`), *Efficient Self-Consistent Learning of Gate Set Pauli
Noise* (`10.1103/1pnv-t9px`) e *Multilayer Cycle Benchmarking*
(`10.1103/4hbl-hpl3`). Ficam como próximos leads, não como técnica validada.

## 1. O resultado que corrige a R1126

Chen et al. modelam o ruído de Pauli preso a uma porta Clifford e perguntam
o que é aprendível quando estados, portas e medições têm ruído desconhecido.
Os resultados centrais:

1. **Teorema 1:** a fidelidade de Pauli `λ_a` é aprendível se, e somente se,
   o **padrão de peso** de `P_a` é preservado pela porta. O padrão de peso é a
   string binária que diz quais qubits são não-identidade.
2. **Teorema 2:** o espaço de funções aprendíveis é o **espaço de ciclos** do
   grafo de transferência de padrões; o não aprendível é o **espaço de cortes**.
   O número de graus não aprendíveis é `2^n − c`, com `c` componentes conexas.
3. Para um Clifford de 2 qubits, há **no máximo 2 graus não aprendíveis**.
   O CB é ótimo: aprende toda a informação aprendível.
4. Fidelidades individuais com padrão preservado podem ser isoladas inserindo
   **Cliffords de 1 qubit** que mapeiam o Pauli de volta a si mesmo. A Fig. 1(b)
   mostra isso para o CNOT; o mesmo princípio vale para o CZ.
5. As funções de corte podem ser **limitadas** por restrições físicas
   (taxas de erro não negativas). O “intercept CB” tenta estimá-las sob a
   hipótese de preparação perfeita; no experimento, a hipótese produziu
   estimativas fora da região física, o que delimita o ruído de preparação.

## 2. Aplicação ao CZ

O grafo do CZ tem 4 vértices (padrões `00`, `01`, `10`, `11`) e 15 arestas
(uma por Pauli não-identidade). As arestas que mudam de padrão são
`IX, IY, XI, XZ, YI, YZ, ZX, ZY`; as preservadas são
`IZ, ZI, XX, XY, YX, YY, ZZ`.

```
E = 15, V = 4, c = 2
posto de ciclos = E − V + c = 13
posto de cortes = V − c = 2
```

Portanto:

- **13 funções aprendíveis** (7 fidelidades individuais + 6 produtos de ciclo);
- **2 funções não aprendíveis** sem hipótese adicional;
- o desenho de médias de órbita da R1126 mede **9** dessas 13 funções;
- faltam **4** funções, que exigem as correções de 1 qubit.

Isso não é um detalhe: o posto 9 não é um limite do hardware nem da matriz
completa; é o subespaço do desenho atual. A R1126 já havia mostrado que a
matriz completa tem posto 15 e que o aumento por ciclos depende de hipótese.
A R1128 identifica a hipótese correta e o limite fundamental: **13/2**.

## 3. Técnicas extraídas

### 3.1 Cliffords de 1 qubit intercalados

Para um Pauli cujo padrão é preservado, inserir uma sequência de Cliffords de
1 qubit que o mapeie de volta ao mesmo Pauli permite ajustar o decaimento
individual, em vez de apenas o produto de órbita. Exemplo do artigo para o
CNOT: `XZ ↔ YY`, ambos de peso 2; uma camada `sqrt(Z) ⊗ sqrt(X)` troca os dois
e permite aprender `λ_XZ` e `λ_YY`. Para o CZ, o par específico difere, mas o
princípio é o mesmo: só se aplica quando o padrão de peso é preservado.

**Consequência:** o próximo protocolo deve gerar circuitos com correções de
1 qubit e declarar a hipótese de que essas portas são suficientemente menos
ruidosas. Sem isso, não se pode chamar o resultado de “13 funções medidas”.

### 3.2 Espaço de ciclos e de cortes

Não é necessário enumerar todos os experimentos possíveis: o grafo de padrões
dá uma base do que é aprendível e do que é gauge. Para o CZ, 13 vetores de
ciclo e 2 de corte; qualquer função fora do espaço de ciclos é inviável sem
hipótese adicional.

**Consequência:** o harness deve reportar a base e o posto antes de ajustar
qualquer modelo. Um ajuste NNLS em desenho de posto deficiente não “resolve”
o corte; apenas escolhe uma solução.

### 3.3 Intercept CB e restrição física

O intercepto do decaimento contém informação de SPAM. Sob preparação perfeita,
o intercepto pode estimar as funções de corte; na prática, a hipótese falhou
no experimento do artigo, e as estimativas ficaram fora da região física.
A região física (todas as taxas de Pauli não negativas) fornece **bounds**,
não uma identificação.

**Consequência:** as 2 funções restantes podem ser limitadas, mas não liberadas
para PEC 2q sem uma hipótese explícita e validada.

### 3.4 Rotações Pauli e seleção de bases (van den Berg & Wocjan 2024)

- Twirl por rotações Pauli `R_P(θ)`, com `θ=π/2`, usando `S`, `H` e `SX` para
  permutar termos e **averiguar fidelidades**; reduz o número de fidelidades
  únicas.
- Sequências de correção de 1 qubit para extrair fidelidades individuais
  quando o suporte é preservado.
- Seleção de bases por **coloração de grafo** e **covering arrays** para
  minimizar o número de bases de aprendizagem.
- Aprendizagem por **NNLS** de `M(ℬ,𝒦) λ = −log(f)/2`, com a condição de
  posto coluna completo; a “hipótese de simetria” é usada quando a
  desambiguação não é possível.

**Consequência:** o modelo `M λ = −log(f)/2` do nosso `cycle_benchmarking.py`
está alinhado com a literatura, mas o nosso desenho não garantia posto. O NNLS
deve ser precedido de auditoria de posto e a hipótese de simetria deve ser
declarada, não embutida.

### 3.5 Twirl/frame e mitigação híbrida em hardware

Três fontes adicionais foram consultadas para o desenho de twirl/frame e para
a camada híbrida, sem transferir resultados de outro processador:

| Fonte | Leitura | Técnica extraída | Uso no Core |
|---|---|---|---|
| Hashim et al., *Randomized Compiling for Scalable Quantum Computing on a Noisy Superconducting Quantum Processor*, PRX 11, 041039 (2021), DOI `10.1103/PhysRevX.11.041039` | metadados Crossref; abstract não lido | RC com rastreamento de frame, caracterização do ciclo vestido e benchmarking em supercondutor | motivou `twirl` por CZ e registro de frames na R1130 |
| Ferracin et al., *Efficiently improving the performance of noisy quantum computers*, Quantum 8, 1410 (2024), DOI `10.22331/q-2024-07-15-1410` | abstract e referências | “Noiseless Output Extrapolation” e “Pauli Error Cancellation”, combinando PEC e amplificação de ruído para processos gate-dependentes/não locais; melhora de até 86% em variation distance num processador de 4 qubits | justifica a camada híbrida PEC/ZNE, mas não foi executada |
| Kim et al., *Evidence for the utility of quantum computing before fault tolerance*, Nature 618, 500 (2023), DOI `10.1038/s41586-023-06096-3` | abstract Crossref | PEC com modelo esparso de Pauli-Lindblad em 127 qubits | evidência externa de que o modelo esparso é útil; não é o Baihua nem o nosso desenho |

**Limite:** nenhum desses resultados foi reproduzido no Baihua. Eles orientam
o desenho e as hipóteses; não são evidência de que o nosso protocolo funciona.
O twirl da R1130 é de Pauli em nível de CZ, não uma implementação completa de
RC com pós-processamento de frames em hardware.

### 3.6 Rotas de 2026 para os bloqueios

- **GSPN:** Chen, Zhang, Jiang e Flammia, *Efficient self-consistent learning
  of gate set Pauli noise*, PRX Quantum 7, 010305 (2026), DOI
  `10.1103/1pnv-t9px`. Aprende o gate set inteiro (SPAM, 1q, CZ) com ansatz
  linear e caracteriza os graus autoconsistentemente aprendíveis; aplica-se a
  CZ paralelo. Código: `github.com/csenrui/PauliGST`.
- **MLCB:** Calzona, Papič, Figueroa-Romero e Auer, *Multilayer cycle
  benchmarking for high-accuracy error characterization*, Phys. Rev. Research
  8, 013111 (2026), DOI `10.1103/4hbl-hpl3`. Analisa múltiplas camadas
  conjuntamente e reduz graus não aprendíveis em até 75%, melhorando PEC.
- **Gauge:** Chen et al., *Disambiguating Pauli noise in quantum computers*,
  PRX Quantum 7, 033045 (2026), DOI `10.1103/69wc-gzl6`. Com aprendizagem
  autoconsistente, o gauge não deve bloquear observáveis mitigados; a escolha
  de gauge afeta o overhead de amostragem.
- **ZNE layerwise:** Russo e Mari, *Quantum error mitigation by layerwise
  Richardson extrapolation*, Phys. Rev. A 110, 062420 (2024), DOI
  `10.1103/PhysRevA.110.062420`. Amplifica camadas independentemente e usa
  interpolação de Lagrange multivariada; não assume uma escala global
  monotônica.

Essas fontes foram lidas em abstract/metadados (GSPN, MLCB, gauge) ou no
abstract (LRE); nenhuma foi executada no Baihua. Elas definem **rotas**, não
resultados do nosso hardware.

## 4. O que muda no código e nos agentes

| Arquivo | Mudança |
|---|---|
| `quantum_mitigation/cb_learnability.py` | grafo de padrões, bases de ciclo/corte, 13/2, comparação com o posto 9 |
| `tests/test_r1128_cb_learnability.py` | contraprovas de contagem, bases e ortogonalidade |
| `harnesses/quantum-error-mitigation/cb_protocol.py` | comando `learnability` |
| `docs/HANDOFF_CB_GST.md` | correção da interpretação do posto 9 |
| skill e cartas dos agentes | 13 aprendíveis, 2 não aprendíveis, Cliffords de 1 qubit |
| `docs/RELATORIO_CB_R1126.md` | nota de correção para o resultado 13/2 |
| `quantum_mitigation/interleaved_cb.py` | desenho 7+6, twirl/frame, ruído 1q e pré-registro |
| `tests/test_r1129_interleaved_cb.py` | recuperação exata das 13 funções |
| `tests/test_r1130_twirl_noise_prereg.py` | twirl, ruído das correções e pré-registro |
| `lean/quantum-cb/QuantumCB.lean` | contraprova finita dos invariantes 13/2 |
| `tests/test_r1131_lean_counterproof.py` | compilação/verificação do arquivo Lean |

O que **não** muda: nenhuma taxa foi medida; PEC 2q, ZNE e comparação de
layouts continuam bloqueados; o teste de RC em hardware continua sem ganho
detectado; a calibração de leitura continua sendo de subespaço 00/11.

A implementação R1129 materializa o desenho de 13 funções (7 individuais + 6
pares) e o valida em simulação exata, com erro máximo `3,33×10⁻¹⁶`. A R1130
adiciona twirl/frame, ruído simulado das correções e pré-registro; a R1131
formaliza em Lean 4 os invariantes finitos (13/2). Nada foi executado no
Baihua; ver `docs/RELATORIO_CB_R1129.md`, `docs/RELATORIO_R1130.md` e
`docs/RELATORIO_LEAN_R1131.md`.

## 5. Limites

- A derivação 13/2 supõe ruído de Pauli e SPAM twirlado; ruído coerente não
  twirlado pode invalidar o modelo.
- As correções de 1 qubit são supostas suficientemente menos ruidosas; isso
  precisa ser medido, não presumido.
- O grafo é do CZ ideal; o CZ físico compilado pode ter outro padrão.
- As 2 funções de corte não são identificadas; bounds físicos não são
  identificação.
- O artigo de 2023 foi lido no texto principal; os artigos de 2026 foram
  apenas identificados e não foram usados como evidência.
- Nenhum resultado desta rodada é validação externa ou prova de vantagem.

## 6. Próximo passo técnico

1. Gerar o desenho de CB com correções de 1 qubit para os 7 Paulis de padrão
   preservado e os produtos de ciclo necessários.
2. Validar em simulador que o desenho recupera as 13 funções e que o posto é
   13; manter as 2 de corte como não identificadas.
3. Pré-registrar shots, seeds, ordem e hipótese de ruído das correções.
4. Só então considerar hardware; PEC 2q continua condicionado às 2 funções
   de corte e à validação do modelo.
