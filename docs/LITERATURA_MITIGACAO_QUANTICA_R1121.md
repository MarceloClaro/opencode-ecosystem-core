# Literatura para os gaps de mitigação quântica — R1121

**Status:** dossiê local com referências verificadas
**Spec:** `specs/SPEC-935-R1121-literature-mitigation-gaps.md`
**Base estruturada:** `docs/literatura_mitigacao_r1121.json`

Este documento não promete “10/10”. Ele extrai técnicas publicadas e as
condiciona a gates, orçamento e evidência no hardware GJQ.

## 1. Como as referências foram verificadas

- Crossref DOI lookup em 2026-11-09;
- páginas arXiv em 2026-11-09 para os itens sem DOI ou para conferir arXiv ID;
- nenhuma referência foi incluída sem DOI ou arXiv ID verificado nesta sessão.

## 2. Mapa gap → técnica → referência

| Gap | Técnica extraída | Referência principal |
|---|---|---|
| RC / Pauli-frame | twirl de Pauli por porta Clifford; ruído local vira canal de Pauli | Wallman & Emerson 2016, DOI 10.1103/PhysRevA.94.052325 |
| RC + ZNE | combinar RC com extrapolação, sem somar créditos | Kurita et al. 2023, DOI 10.22331/q-2023-11-20-1184 |
| 15 taxas Pauli-Lindblad | cycle benchmarking de portas multi-qubit | Erhard et al. 2019, DOI 10.1038/s41467-019-13068-7 |
| Aprendizado de ruído Pauli | estimação eficiente de canais de Pauli | Harper et al. 2020, DOI 10.1038/s41567-020-0992-8; Flammia & Wallman 2020, DOI 10.1145/3408039 |
| PEC 2q | decomposição quase-probabilística com modelo esparso de Pauli-Lindblad | van den Berg et al. 2023, DOI 10.1038/s41567-023-02042-2 |
| PEC / ZNE | cancelamento probabilístico e extrapolação de ruído | Temme et al. 2017, DOI 10.1103/PhysRevLett.119.180509 |
| ZNE | extrapolação com escalas de ruído | Li & Benjamin 2017, DOI 10.1103/PhysRevX.7.021050 |
| GST / SPAM | caracterização autoconsistente de portas + SPAM; diamond norm | Blume-Kohout et al. 2017, DOI 10.1038/ncomms14485 |
| GST mais barato | GST compressiva e GST linear aleatorizada | Brieger et al. 2023, DOI 10.1103/PRXQuantum.4.010325; Gu et al. 2021, DOI 10.1103/PRXQuantum.2.030328 |
| GST tutorial | guia passo a passo | Greenbaum 2015, arXiv:1509.02921 |
| Readout | matriz de calibração e mitigação model-free | Bravyi et al. 2021, DOI 10.1103/PhysRevA.103.042605; van den Berg et al. 2022, DOI 10.1103/PhysRevA.105.032620 |
| Superfície | decodificador Collision Clustering em FPGA/ASIC | Barber et al. 2025, DOI 10.1038/s41928-024-01319-5; arXiv:2309.05558 |
| Crosstalk | randomized benchmarking simultâneo | Gambetta et al. 2012, DOI 10.1103/PhysRevLett.109.240504 |
| Incerteza | intervalos de confiança para benchmarking | Wallman & Flammia 2014, DOI 10.1088/1367-2630/16/10/103032 |
| Benchmarking universal | dihedral benchmarking | Carignan-Dugas et al. 2015, DOI 10.1103/PhysRevA.92.060302 |

## 3. Resoluções metodológicas

### 3.1 RC real, não transpilação aleatória

1. Aplicar o passe de Pauli-frame (R1119) a cada porta Clifford.
2. Verificar igualdade up to fase global.
3. Rodar duas pernas: baseline e twirlado, com o mesmo layout e o mesmo `n`
   pré-registrado.
4. Comparar a métrica mitigada, não o número bruto de portas.
5. Só chamar de RC validado se o twirlado reduzir erro com IC excluindo zero.

**Gate:** o passe R1119 já existe; falta a validação em hardware.

### 3.2 As 15 taxas Pauli-Lindblad

O modelo de Pauli-Lindblad para uma porta de 2 qubits tem 15 geradores não
identidade. A caracterização publicada usa **cycle benchmarking**:

- preparar autoestados de Pauli;
- aplicar ciclos com twirl de Pauli;
- medir a sobrevivência em função da profundidade;
- ajustar decaimentos exponenciais;
- extrair as fidelidades de Pauli e converter para taxas.

Referências: Erhard et al. 2019; Harper et al. 2020; Flammia & Wallman 2020.

**Orçamento mínimo proposto:** 15 Paulis × 5 profundidades × 2 conjuntos =
150 jobs, 4096 shots. Como o limite é 20 submissões por processo, executar em
8 processos. Ainda assim, 150 jobs é um piso; GST/cycle benchmarking completo
pode exigir mais.

**Gate:** não usar PEC 2q antes de obter as 15 taxas com IC.

### 3.3 GST para separar preparação, porta e leitura

A tomografia de 12 circuitos não é GST. Para separar SPAM de erro de porta:

- usar pyGSTi ou GST compressiva;
- modelar state preparation e measurement como operações livres;
- estimar diamond norm;
- comparar com a calibração Rabi (R1118).

Referências: Blume-Kohout et al. 2017; Brieger et al. 2023; Gu et al. 2021;
Greenbaum 2015.

**Gate:** GST é caro; usar primeiro no qubit gargalo (q1) e no par do CZ.

### 3.4 Leitura

A leitura é o erro dominante atual: r1 ≈ 0,077–0,084. Técnicas:

- matriz de calibração e inversão (Bravyi et al. 2021);
- mitigação model-free para valores esperados (van den Berg et al. 2022);
- medir mais conjuntos para separar drift de erro sistemático.

**Gate atual:** r1 > 0,05; não comparar layouts antes de mitigar leitura.

### 3.5 PEC 2q

PEC com modelo esparso de Pauli-Lindblad:

1. aprender as 15 taxas;
2. construir a decomposição quase-probabilística;
3. estimar o overhead γ;
4. rodar o circuito alvo com amostragem;
5. reportar γ, amostras e IC.

Referências: van den Berg et al. 2023; Temme et al. 2017.

**Gate:** 15 taxas ausentes ⇒ PEC 2q bloqueado.

### 3.6 ZNE

ZNE só é válido se a escala de ruído for monotônica e a extrapolação fizer
sentido. No run atual, a TVD q0 em 1/3/5/7 foi 0,0645 / 0,0747 / 0,0735 /
0,0967 — não monotônica.

**Gate:** ZNE bloqueado até a curva ser monotônica.

### 3.7 Superfície

O código de superfície exige decodificador em tempo real. O decoder Collision
Clustering (Barber et al. 2025) mostra o caminho: FPGA/ASIC, MHz, centenas de
qubits. O Baihua não expõe esse decodificador.

**Gate:** superfície bloqueada; não simular “vantagem” sem decoder real.

## 4. Pilha híbrida ordenada

```
Leitura (matriz/model-free)
   ↓
RC (Pauli-frame) + validação twirlado vs baseline
   ↓
Cycle benchmarking (15 taxas) + GST no q1
   ↓
PEC 2q (modelo esparso) / ZNE (se monotônico)
   ↓
QEC de superfície (somente com decoder em tempo real)
```

Cada camada tem gate e orçamento. Não somar créditos de camadas diferentes.

## 5. Orçamentos e gates

| Etapa | Jobs | Gate |
|---|---:|---|
| RC twirlado vs baseline | 16 (2 pernas × 2 sets × 4 circuitos) | efeito > 0 e IC exclui 0 |
| Cycle benchmarking 15 taxas | 150 | 15 taxas com IC |
| GST q1 | ~100 circuitos | diamond norm com IC |
| PEC 2q | depende de γ | γ e amostras reportados |
| ZNE | 4 escalas | curva monotônica |
| Superfície | — | decoder em tempo real |

Os números de jobs são pisos de planejamento; não são garantia de poder
estatístico. O `n` por circuito deve ser pré-registrado antes de cada run.

## 6. O que não fazer

- Não chamar transpilação aleatória de RC.
- Não inventar as 15 taxas.
- Não declarar PEC 2q sem taxa.
- Não declarar ZNE com curva não monotônica.
- Não declarar superfície sem decoder em tempo real.
- Não prometer “10/10”, Qualis ou vantagem quântica.
- Não somar RC + ZNE + PEC como se fossem independentes.

## 7. Próximos passos concretos

1. Validar RC twirlado vs baseline com `n` pré-registrado.
2. Rodar cycle benchmarking do CZ q0–q1 e extrair as 15 taxas.
3. Rodar GST no q1 com pyGSTi/compressive GST.
4. Repetir a leitura com mitigação e dois conjuntos.
5. Só então reavaliar PEC 2q, ZNE e layouts.

## 8. Referências

As 18 referências com DOI/arXiv, ano, venue e gap estão em
`docs/literatura_mitigacao_r1121.json`. Todas foram verificadas por Crossref
ou página arXiv em 2026-11-09.
