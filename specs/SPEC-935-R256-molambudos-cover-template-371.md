# SPEC-935-R256 — Template TeX da capa completa Amazon/KDP para 371 páginas

## Objetivo

Criar um arquivo `.tex` reprodutível para a capa completa de `Molambudos — O Diário do Paciente 1.260`, com contracapa, lombada e capa frontal separados por guias técnicas, usando as medidas fornecidas para 371 páginas.

## Medidas fornecidas

| # | Descrição | Largura (in) | Altura (in) |
|---|---|---:|---:|
| 1 | Full Cover | 14.635 | 10.417 |
| 2 | Front Cover | 6.197 | 9.236 |
| 3 | Margin | 0.125 | 0.125 |
| 4 | Wrap | 0.591 | 0.591 |
| 5 | Hinge | 0.394 | 10.417 |
| 6 | Spine | 1.060 | 9.236 |
| 7 | Spine Safe Area | 0.935 | 8.986 |
| 8 | Spine Margin | 0.062 | 0.062 |
| 9 | Barcode Margin | 0.250 | 0.375 |

## Interpretação técnica

- O tamanho total de página é fixado em `14.635in × 10.417in`.
- O wrap real usado no posicionamento é `0.5905in`, pois:
  - `(10.417 - 9.236) / 2 = 0.5905`;
  - `(14.635 - 6.197 - 1.060 - 6.197) / 2 = 0.5905`.
- O valor `0.591in` é mantido em comentários/legendas como arredondamento do template.
- Layout horizontal:
  - Contracapa: `x = 0.5905`, `w = 6.197`.
  - Lombada: `x = 6.7875`, `w = 1.060`.
  - Capa frontal: `x = 7.8475`, `w = 6.197`.
- A área de hinge é desenhada como guia sobreposta junto aos dois lados da lombada, sem somar largura ao full cover.

## Artefato esperado

- `projetos/molambudos/Molambudos_VictoriaRegia/capa_kdp_371_full_cover_template.tex`

## Critérios de aceitação

1. O `.tex` compila sem erro mesmo antes de receber as imagens finais.
2. O PDF gerado mede `14.635in × 10.417in`.
3. O template mostra áreas separadas para:
   - Contracapa;
   - Lombada;
   - Capa frontal.
4. O template inclui guias de:
   - wrap;
   - trim das capas;
   - hinge;
   - spine safe area;
   - spine margin;
   - barcode margin.
5. O template possui macros editáveis para inserir imagens posteriormente.

## Resultado verificado

Arquivos criados:

- `projetos/molambudos/Molambudos_VictoriaRegia/capa_kdp_371_full_cover_template.tex`
- `projetos/molambudos/Molambudos_VictoriaRegia/capa_kdp_371_full_cover_template.pdf`

Validação:

- Compilação `latexmk -pdf` concluída sem erro.
- PDF gerado com `1` página.
- Tamanho do PDF: `1053.72 × 750.025 pt`.
- Conversão para polegadas: `14.635in × 10.417in`.
- O template contém placeholders para:
  - `\BackCoverImage`;
  - `\SpineImage`;
  - `\FrontCoverImage`.
- O template contém toggle de guias:
  - `\showguidestrue` para visualização técnica;
  - `\showguidesfalse` para exportação limpa.

Observação: devido ao arredondamento do template Amazon/KDP, o wrap real usado internamente é `0.5905in`, equivalente ao `0.591in` informado.
