# SPEC-935-R257 — Capa completa final com imagens fornecidas

## Objetivo

Gerar a capa completa final de `Molambudos — O Diário do Paciente 1.260` para 371 páginas, usando as imagens fornecidas pelo usuário na pasta:

`projetos/molambudos/Molambudos_VictoriaRegia/capa-lombada-contracapa/`

## Entradas

- Capa frontal: `capa-lombada-contracapa/capa.png`
- Lombada: `capa-lombada-contracapa/lombada.png`
- Contracapa: `capa-lombada-contracapa/contracapa.png`
- Template técnico base: `capa_kdp_371_full_cover_template.tex`

## Saídas esperadas

- `capa_kdp_371_full_cover_final.tex`
- `capa_kdp_371_full_cover_final.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_capa-completa_Amazon-KDP_371p_v1.5_2026-07-26.pdf`

## Critérios de aceitação

1. O `.tex` final referencia explicitamente as três imagens informadas.
2. As guias técnicas ficam ocultas no PDF final (`showguidesfalse`).
3. O PDF compila sem erro.
4. O PDF final tem 1 página.
5. O tamanho de página é `14.635in × 10.417in`.
6. O PDF final contém imagens incorporadas.
7. O arquivo nomeado longo é gerado para entrega/upload.

## Resultado verificado

As três imagens informadas tinham o mesmo canvas completo (`1498 × 1050 px`). Para respeitar as medidas separadas de contracapa/lombada/capa frontal, foram gerados recortes automáticos proporcionais ao template KDP:

- `capa-lombada-contracapa/panels_371/contracapa_panel.png` — recorte da área da contracapa.
- `capa-lombada-contracapa/panels_371/lombada_panel.png` — recorte da área da lombada.
- `capa-lombada-contracapa/panels_371/capa_panel.png` — recorte da área da capa frontal.

Arquivos finais criados:

- `capa_kdp_371_full_cover_final.tex`
- `capa_kdp_371_full_cover_final.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_capa-completa_Amazon-KDP_371p_v1.5_2026-07-26.pdf`

Validação final:

- PDF final: `1` página.
- Tamanho: `1053.72 × 750.025 pt` (`14.635in × 10.417in`).
- Criptografia: `no`.
- Imagens incorporadas: `3` entradas em `pdfimages -list`.
- Guias técnicas ausentes no PDF final (`WRAP`, `SPINE SAFE`, `placeholder` não aparecem no texto extraído).
- ISBN real presente no TeX final: `9798189170492`.
- Arquivo de entrega longo gerado com o mesmo tamanho do PDF final: `2.459.728` bytes.
