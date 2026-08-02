# SPEC-935-R255 — Miolo Amazon/KDP do Molambudos

## Objetivo

Adequar o PDF de miolo de `Molambudos — O Diário do Paciente 1.260` para upload na Amazon/KDP, tomando como referência o manual fornecido pelo usuário:

`projetos/molambudos/Molambudos_VictoriaRegia/15299540919613.pdf`

## Requisitos extraídos do manual

1. O arquivo de miolo deve ser um PDF pronto para upload no KDP.
2. O tamanho de página deve corresponder ao trim size e à escolha de sangria.
3. Para livro 6" × 9" com sangria, o manual orienta usar página `6.125" × 9.25"`.
4. Para livros sem sangria, elementos devem ficar dentro das margens.
5. Como o projeto contém páginas/elementos internos full-bleed, o perfil escolhido é **com sangria**.
6. Para 301–500 páginas, a margem interna mínima do manual é `0.625"`; margens externas mínimas são `0.375"` com sangria.
7. Fontes devem estar incorporadas.
8. O PDF não deve conter capa/contracapa quando usado como interior/manuscript file.
9. O PDF não deve conter criptografia.
10. Conteúdo crítico deve permanecer preservado.

## Estratégia

Entrada:

- `main_miolo_sem_capa.pdf` — PDF de miolo já sem capa e contracapa, 6" × 9".

Saída Amazon/KDP:

- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_v1.5_2026-07-26.pdf`

Transformação:

- Reempacotar cada página em página final `6.125" × 9.25"` por meio de wrapper LaTeX com `pdfpages`.
- Preservar 368 páginas do miolo.
- Usar perfil KDP **com sangria**.

## Critérios de aceitação

1. Arquivo de saída existe e é PDF válido.
2. Tamanho de página: `441 × 666 pt`, equivalente a `6.125" × 9.25"`.
3. Número de páginas: `368`.
4. Sem criptografia.
5. Fontes incorporadas conforme `pdffonts`.
6. O PDF não contém capa/contracapa full-bleed externas; começa pela folha de rosto e termina na Nota Histórica.
7. Conteúdo crítico extraível preservado:
   - `Molambudos`
   - `Passaporte de Leitura`
   - `MEM-07`
   - `A Mãe Levada`
   - `9798189170492`
   - `Nota Histórica`
8. ISBN antigo ausente.
9. Arquivo compatível com a opção KDP: trim `6" × 9"`, **Bleed** ativado.

## Observação operacional

No painel da Amazon/KDP, configurar:

- Trim size: `6" × 9"`.
- Bleed settings: `Bleed` / `com sangria`.
- Interior file: PDF gerado nesta SPEC.

## Resultado verificado

Arquivos gerados:

- `amazon_kdp_miolo_6x9_bleed.tex` — wrapper reprodutível.
- `amazon_kdp_miolo_6x9_bleed.pdf` — saída técnica do wrapper.
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_v1.5_2026-07-26.pdf` — arquivo final nomeado.
- `main_miolo_amazon_kdp_6x9_bleed.pdf` — alias curto para upload.

Validação final:

- `GREEN Amazon/KDP interior`.
- Páginas: `368`.
- Tamanho de página: `441 × 666 pt` (`6.125" × 9.25"`).
- Criptografia: `no`.
- Fontes embutidas: `OK` (`16` linhas em `pdffonts`, todas com `emb yes`).
- Tamanho do arquivo final: `2.540.329` bytes.
- Primeira página: folha de rosto tipográfica.
- Última página: Nota Histórica.
- Conteúdo preservado: `Molambudos`, `Passaporte de Leitura`, `MEM-07`, `A Mãe Levada`, `9798189170492`, `Nota Histórica`.
- ISBN antigo ausente.

Configuração recomendada no KDP:

- Paperback Interior File: `main_miolo_amazon_kdp_6x9_bleed.pdf` ou a versão nomeada longa.
- Trim size: `6" × 9"`.
- Bleed: `Bleed` / `com sangria`.
