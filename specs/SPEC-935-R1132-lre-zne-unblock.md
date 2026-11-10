# SPEC-935-R1132 — LRE como rota para o ZNE não monotônico

**Status:** implementação local, sem hardware
**Fonte:** Russo & Mari, Phys. Rev. A 110, 062420 (2024),
DOI `10.1103/PhysRevA.110.062420`.

## 1. Contexto

O ZNE global no Baihua produziu curvas não monotônicas (TVD 0,0645 / 0,0747 /
0,0735 / 0,0967). A extrapolação global depende de uma única escala e de
monotonicidade; a LRE trata cada camada como variável independente.

## 2. Método

- escalas por camada (1,2,3);
- grade completa de `3^L` configurações;
- coeficientes de Lagrange multivariada para o alvo `0` (zero-ruído);
- estimativa `Σ c_k E(x_k)`.

## 3. Requisitos

- **R1.** `lagrange_coefficients`, `lre_design`, `global_design`, `estimate`.
- **R2.** Validar exatidão no modelo multilinear `E(x)=offset+Σ slope_i x_i`.
- **R3.** Reportar custo `3^L` e limites.
- **R4.** Nenhum hardware, rede ou submissão.
- **R5.** Não declarar que o ZNE está desbloqueado no Baihua.

## 4. Critérios

- coeficientes 1D `[3,-3,1]` para escalas 1,2,3;
- soma dos coeficientes 1;
- LRE exata (erro < 1e-12) no modelo multilinear;
- erro global também exato no modelo linear, sem alegar superioridade geral;
- teste e relatório.

## 5. Limites

A LRE exige mais configurações, supõe modelo multilinear e não corrige drift,
interações ou ruído não linear. É uma rota de desenho, não uma execução.
