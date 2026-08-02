# SPEC-935-R260 — Correção do miolo KDP: texto fora das margens

## Problema reportado

O KDP acusou:

- Arquivo com dimensões `6.13" × 9.25"` ao selecionar trim `6" × 9"`.
- Texto fora das margens.
- Objetos fora das margens.

## Diagnóstico

A versão R259 criou um PDF `6.125" × 9.25"` correto para **com sangria**, mas usou uma camada de fundo contendo a mesma página escalada para preencher todo o canvas. Essa camada duplicava texto dentro da área de sangria/margens, levando o KDP a detectar texto fora das margens.

## Correção

Gerar uma nova versão bleed-safe:

1. Canvas final: `6.125" × 9.25"`.
2. Fundo de sangria: cor sólida, sem texto.
3. Página original `6" × 9"`: inserida sem escala no retângulo de trim.
4. Alternância par/ímpar:
   - ímpar: conteúdo em `x=0`, `y=0.125"`;
   - par: conteúdo em `x=0.125"`, `y=0.125"`.

## Arquivos esperados

- `miolo_kdp_6x9_bleed_margens_sem_texto_bleed.tex`
- `miolo_kdp_6x9_bleed_margens_sem_texto_bleed.pdf`
- `main_miolo_amazon_kdp_6x9_bleed_safe.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_SAFE_v1.7_2026-07-26.pdf`

## Critérios de aceitação

1. PDF final tem `368` páginas.
2. Tamanho de página: `6.125" × 9.25"` (`441 × 666 pt`).
3. Criptografia: `no`.
4. Fontes incorporadas.
5. Texto crítico preservado:
   - `Molambudos`;
   - `Passaporte`;
   - `MEM-07`;
   - `Nota Histórica`;
   - `9798189170492`.
6. O texto extraído não deve apresentar duplicação massiva da primeira página.
7. A camada de sangria não deve conter texto.

## Instrução de upload no KDP

Selecionar:

- Trim size: `6" × 9"`.
- Bleed: `Com sangria` / `Bleed`.

Se for selecionado `sem sangria`, o KDP continuará reclamando que o PDF mede `6.13" × 9.25"`, pois essa medida é justamente o padrão com sangria para trim 6" × 9".

## Resultado verificado

Arquivos gerados:

- `miolo_kdp_6x9_bleed_margens_sem_texto_bleed.tex`
- `miolo_kdp_6x9_bleed_margens_sem_texto_bleed.pdf`
- `main_miolo_amazon_kdp_6x9_bleed_safe.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_SAFE_v1.7_2026-07-26.pdf`

Também foi gerada uma opção sem sangria, caso o usuário configure o KDP como `sem sangria`:

- `main_miolo_amazon_kdp_6x9_sem_sangria.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_SEM-SANGRIA_v1.7_2026-07-26.pdf`

Validação da versão com sangria segura:

- Páginas: `368`.
- Tamanho: `441 × 666 pt` (`6.125" × 9.25"`).
- Criptografia: `no`.
- Tamanho: `5.020.045` bytes.
- Texto extraível preservado em relação ao original (`delta = -3` caracteres, diferença de extração irrelevante).
- Conteúdo confirmado: `Molambudos`, `Passaporte`, `MEM-07`, `Nota Histórica`, `9798189170492`.
- ISBN antigo ausente.
- A camada de sangria não contém texto; é apenas fundo sépia.

Validação da opção sem sangria:

- Páginas: `368`.
- Tamanho: `432 × 648 pt` (`6" × 9"`).
- Criptografia: `no`.
- Tamanho: `2.277.966` bytes.
