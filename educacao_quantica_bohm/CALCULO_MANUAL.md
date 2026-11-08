# Cálculo manual: do count ao resultado {#calculo-manual}

Este capítulo ensina a chegar **à mão** aos mesmos números que os scripts
produzem. Você só precisa de lápis, papel e uma calculadora. Todos os counts
abaixo são reais ou simulados desta edição.

## 1. O que é um count

Um `count` é um par:

```text
"00": 484
```

Leia assim: “o resultado `00` apareceu 484 vezes”. O total de tiros é a soma de
todos os counts. Se a soma não for 1024, o experimento não teve 1024 tiros.

## 2. A regra de ouro

Para qualquer evento A:

```text
P(A) = (número de vezes que A apareceu) / (total de tiros)
```

Exemplo: se `00` apareceu 484 vezes em 1024 tiros:

```text
P(00) = 484 / 1024 = 0,47265625 ≈ 0,473
```

Multiplique por 100 para ter porcentagem: **47,3%**.

## 3. Bell: fidelidade proxy

Counts do Guoji08 (Bell, 1024 tiros):

| Resultado | Count |
|---|---:|
| `00` | 484 |
| `11` | 480 |
| `01` | 27 |
| `10` | 33 |

Passo 1 — some os resultados ideais:

```text
484 + 480 = 964
```

Passo 2 — divida pelo total:

```text
964 / 1024 = 0,94140625
```

Passo 3 — arredonde e converta:

```text
0,9414 × 100 = 94,14% ≈ 94,1%
```

**Resultado manual:** fidelidade proxy = **94,1%**. O script mostra o mesmo
número. O ideal seria 100%; os 5,9% restantes são `01` e `10`.

## 4. GHZ: fidelidade proxy

Counts do Guoji08 (GHZ de 4 qubits, 1024 tiros):

| Resultado | Count |
|---|---:|
| `0000` | 418 |
| `1111` | 389 |
| outros | 217 |

```text
418 + 389 = 807
807 / 1024 = 0,7880859375
0,7881 × 100 = 78,81% ≈ 78,8%
```

**Resultado manual:** **78,8%**. No Baihua, `437 + 230 = 667`; `667 / 1024 =
0,6514` → **65,1%**.

## 5. CHSH: do count ao S

Counts do Guoji08, quatro circuitos, 1024 tiros cada:

| Configuração | `00` | `11` | `01` | `10` |
|---|---:|---:|---:|---:|
| E00 | 401 | 405 | 106 | 112 |
| E01 | 401 | 406 | 105 | 112 |
| E10 | 399 | 403 | 111 | 111 |
| E11 | 77 | 94 | 434 | 419 |

Para cada linha, use:

```text
E = (N00 + N11 − N01 − N10) / 1024
```

E00:

```text
401 + 405 = 806
106 + 112 = 218
806 − 218 = 588
588 / 1024 = 0,57421875 ≈ 0,574
```

E01:

```text
401 + 406 = 807
105 + 112 = 217
807 − 217 = 590
590 / 1024 = 0,576171875 ≈ 0,576
```

E10:

```text
399 + 403 = 802
111 + 111 = 222
802 − 222 = 580
580 / 1024 = 0,56640625 ≈ 0,566
```

E11:

```text
77 + 94 = 171
434 + 419 = 853
171 − 853 = −682
−682 / 1024 = −0,666015625 ≈ −0,666
```

Agora o S:

```text
S = E00 + E01 + E10 − E11
S = 0,57421875 + 0,576171875 + 0,56640625 − (−0,666015625)
S = 2,3828125 ≈ 2,383
```

**Resultado manual:** **S = 2,383**. O limite clássico é 2; o ideal quântico é
2,828. Como 2,383 > 2, houve violação observada.

## 6. VQC: P(1) e acurácia

Counts do Guoji08, quatro entradas, 1024 tiros cada:

| Entrada | `0` | `1` | Rótulo | P(1) manual | Predição |
|---|---:|---:|---:|---:|---:|
| 00 | 982 | 42 | 0 | 42/1024 = 0,041 | 0 |
| 01 | 34 | 990 | 1 | 990/1024 = 0,967 | 1 |
| 10 | 49 | 975 | 1 | 975/1024 = 0,952 | 1 |
| 11 | 980 | 44 | 0 | 44/1024 = 0,043 | 0 |

Regra: predição = 1 se P(1) ≥ 0,5; senão 0.

```text
00: 0,041 < 0,5 → 0 (rótulo 0) → acertou
01: 0,967 ≥ 0,5 → 1 (rótulo 1) → acertou
10: 0,952 ≥ 0,5 → 1 (rótulo 1) → acertou
11: 0,043 < 0,5 → 0 (rótulo 0) → acertou
```

Acurácia = 4 acertos / 4 = **4/4 = 100%**. Isso não é generalização: são quatro
pontos e um teto de 100%.

## 7. Bloch: três medidas, três componentes

Para um estado, meça em Z, X e Y. Em cada base:

```text
P(0) = N0 / 1024
componente = 2 × P(0) − 1
```

Exemplo S5 (`Ry(π/3)|0⟩`) no Guoji08:

| Base | `0` | `1` | P(0) | Componente |
|---|---:|---:|---:|---:|
| Z | 788 | 236 | 788/1024 = 0,7695 | z = 0,539 |
| X | 961 | 63 | 961/1024 = 0,9385 | x = 0,877 |
| Y | 530 | 494 | 530/1024 = 0,5176 | y = 0,035 |

Comprimento:

```text
|r| = √(x² + y² + z²)
|r| = √(0,877² + 0,035² + 0,539²)
|r| = √(0,769 + 0,001 + 0,291)
|r| = √1,061 = 1,030
```

**Achado:** 1,030 > 1. Um vetor físico não pode passar de 1; o excesso é viés
de leitura e estimativa linear. A correção exige calibração de leitura ou
máxima verossimilhança.

## 8. SWAP test: sobreposição

Counts do Guoji08:

| Resultado | Count |
|---|---:|
| `0` | 834 |
| `1` | 190 |

```text
P(0) = 834 / 1024 = 0,814453125
sobreposição = 2 × P(0) − 1
sobreposição = 2 × 0,814453125 − 1
sobreposição = 1,62890625 − 1 = 0,62890625 ≈ 0,629
```

**Resultado manual:** **0,629**. O ideal é 0,770; o hardware reduz.

## 9. Incerteza: quanto o número pode variar

Para uma proporção p com N tiros, o erro padrão é:

```text
EP = √(p × (1 − p) / N)
```

Exemplo: `p = 0,482`, `N = 1024`:

```text
EP = √(0,482 × 0,518 / 1024)
EP = √(0,0002438) = 0,0156
```

Em porcentagem: **1,56%**. O intervalo de 95% é aproximadamente:

```text
p ± 1,96 × EP = 0,482 ± 0,031 → [0,451; 0,513]
```

Por isso, uma diferença de 1 ou 2 pontos percentuais pode ser só amostragem.

## 10. Planilha manual

Copie esta tabela no caderno e preencha:

| Medida | Count | Total | p = count/total | Fórmula | Resultado |
|---|---:|---:|---:|---|---:|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

No LibreOffice/Excel:

1. Coloque os counts na coluna B.
2. Coloque o total em B10: `=SOMA(B2:B9)`.
3. Calcule p em C2: `=B2/$B$10`.
4. Calcule a métrica em D2 com a fórmula da lauda.
5. Formate como porcentagem com uma casa decimal.

## 11. Se o seu número não bater

- **Total diferente de 1024?** Confira os shots e a soma dos counts.
- **Bit order invertido?** Em Qiskit, `q0` é o bit mais à direita; no console, a
  ordem pode ser exibida ao contrário.
- **Base errada?** Para X, aplique H antes de medir; para Y, S† e H.
- **Backend diferente?** Calibração, fila e leitura mudam.
- **Arredondamento:** use três casas decimais e só arredonde no final.
- **Ruído:** uma execução não é uma calibração; repita com outra seed.

> **Regra:** se você chegar ao mesmo número com lápis e papel, entendeu o
> experimento. Se só o script chega, você ainda não entendeu.
