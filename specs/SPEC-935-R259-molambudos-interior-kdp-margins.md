# SPEC-935-R259 — Miolo KDP com margens e sangria preservadas

## Objetivo

Refazer o miolo Amazon/KDP de `Molambudos — O Diário do Paciente 1.260` conforme a orientação de margens/sangria fornecida pelo usuário, sem esticar o texto do livro.

## Requisitos interpretados

- Trim size escolhido: `6" × 9"`.
- Como há páginas/elementos que chegam à borda visual, usar perfil **com sangria**.
- Tamanho de página com sangria para 6" × 9": `6.125" × 9.25"`.
- A sangria adiciona:
  - `0.125"` no topo;
  - `0.125"` na base;
  - `0.125"` na borda externa.
- A borda externa alterna:
  - páginas ímpares: externa à direita;
  - páginas pares: externa à esquerda.
- A margem interna/calha deve ser preservada; o conteúdo 6" × 9" não deve ser escalado.

## Correção sobre a versão anterior

A versão R255 reempacotou o miolo preenchendo toda a página `6.125" × 9.25"`, o que podia escalar o conteúdo. A versão R259 preserva a página original de trim `6" × 9"` como camada frontal e cria sangria por trás.

## Estratégia técnica

Entrada:

- `main_miolo_sem_capa.pdf` — 368 páginas, `6" × 9"`.

Saída:

- `main_miolo_amazon_kdp_6x9_bleed_margens.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_margens_v1.6_2026-07-26.pdf`

Método por página:

1. Criar canvas `6.125" × 9.25"`.
2. Inserir uma camada de fundo escalada para preencher a sangria, evitando bordas brancas.
3. Inserir por cima a página original `6" × 9"`, sem escala, no retângulo de trim.
4. Alternar o deslocamento horizontal:
   - página ímpar: `x = 0`, `y = 0.125"`;
   - página par: `x = 0.125"`, `y = 0.125"`.

## Critérios de aceitação

1. PDF final existe e compila sem erro.
2. PDF final tem `368` páginas.
3. Tamanho de página final: `6.125" × 9.25"` (`441 × 666 pt`).
4. Criptografia: `no`.
5. Fontes continuam incorporadas.
6. Conteúdo crítico preservado:
   - `Molambudos`;
   - `Passaporte de Leitura`;
   - `MEM-07`;
   - `A Mãe Levada`;
   - `Nota Histórica`;
   - `9798189170492`.
7. ISBN antigo ausente.
8. O conteúdo do trim não é esticado: página original `6" × 9"` é preservada como camada frontal.
