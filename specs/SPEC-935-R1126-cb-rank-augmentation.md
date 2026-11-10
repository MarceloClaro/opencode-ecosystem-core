# SPEC-935-R1126 — Limites de posto e aumento de desenho no CB do CZ

**Status:** implementação local, sem hardware
**Data:** 2026-11-09
**Depende de:** R1125 (paridade, posto 9 do CZ)

## 1. Pergunta

O posto 9 do desenho somente-CZ é um limite de *todos* os desenhos CB com
gerador compartilhado, ou apenas da simetrização por órbitas do CZ? Em outras
palavras: acrescentar outros ciclos Cliffords pode identificar as 15 taxas?

## 2. Resultado matemático a testar

Seja `D` a matriz 15×15 de anticomutação, com `y = D γ`, onde `y_P =
−log(f_P)/2` e `γ_Q ≥ 0` são as taxas do gerador de Pauli-Lindblad.

- `D` tem posto **15** (é invertível).
- Um ciclo Clifford `U`, repetido com profundidade par, mede médias de `y`
  sobre as órbitas de `P ↦ U P U†`. A matriz do desenho é `A_U D`, onde `A_U`
  projeta cada linha na média da órbita.
- Somente-CZ: `rank(A_CZ D) = 9`.
- Identidade: `rank(A_I D) = 15` (mas não é um ciclo físico comparável).
- Acrescentar ciclos adequados pode elevar o posto a 15 **se** o mesmo gerador
  `γ` (ou um gerador conjugado por transformação conhecida) governar todos os
  ciclos. É uma hipótese física forte, não um resultado.
- Se cada ciclo tiver seu próprio gerador, há `15k` incógnitas e `9k` equações
  independentes para `k` ciclos: `rank = 9k < 15k`, sempre subdeterminado.
- Submodelos: apenas taxas locais (6) têm posto 6; apenas taxas de dois qubits
  (9) têm posto 9. Isso é identificabilidade **sob a hipótese** de que as
  demais taxas são nulas.

## 3. Requisitos

- **R1.** Implementar `anticommutation_matrix`, `clifford_permutation`,
  `orbit_average_matrix`, `stacked_rank`, `submodel_rank`,
  `separate_generator_audit` e `augmentation_search`.
- **R2.** Verificar o posto 9 do CZ e o posto 15 da matriz completa.
- **R3.** Demonstrar um par de sementes em que acrescentar um Clifford eleva o
  posto a 15 e outro em que não eleva, mostrando que a escolha importa.
- **R4.** Demonstrar que geradores separados permanecem subdeterminados.
- **R5.** Declarar explicitamente a hipótese de gerador compartilhado/conjugado
  e que identidade não é um ciclo físico equivalente ao CZ.
- **R6.** Nenhum acesso a hardware, rede, submissão ou credencial.
- **R7.** Testes determinísticos, sem aleatoriedade não semeada.
- **R8.** Não declarar que o desenho aumentado foi executado ou validado.

## 4. Não objetivos

- Projetar o circuito físico completo do desenho aumentado.
- Provar que o ruído real é compartilhado entre ciclos.
- Executar GST, PEC, ZNE ou comparar layouts.
- Declarar as 15 taxas medidas.

## 5. Critérios de aceitação

- matriz completa com posto 15;
- CZ com posto 9;
- identidade com posto 15, marcada como não física para o argumento;
- semente positiva e negativa documentadas;
- geradores separados com défice `6k`;
- submodelo local 6 e dois-qubits 9;
- busca gulosa determinística encontra posto 15;
- nenhuma string de submissão/hardware no módulo;
- nenhuma taxa medida ou promoção de confiança.
