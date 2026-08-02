# SPEC-935-R263 — Molambudos: miolo e conteúdo em 160 × 230 mm

## Objetivo

Gerar uma nova variante do miolo físico de `Molambudos — O Diário do Paciente 1.260` com **página final 160 × 230 mm** e **conteúdo refluído nesse formato**, não apenas redimensionado por escala.

## Contexto

As versões anteriores foram preparadas para 6" × 9". O usuário solicitou explicitamente ajuste do **miolo** e do **conteúdo** para **160 × 230 mm**.

## Diretório do projeto

`projetos/molambudos/Molambudos_VictoriaRegia/`

## Método

1. Criar variante de compilação `main_kdp_print_160x230mm.tex`.
2. Tornar `misc/options.sty` parametrizável por macros de papel/margem, preservando o padrão 6" × 9" quando nenhuma macro for definida.
3. Compilar o PDF completo em modo `KDPPRINT` para:
   - suprimir marginália problemática em impressão;
   - impedir hyperlinks explícitos nas rotas;
   - refluír texto no novo tamanho 160 × 230 mm.
4. Extrair apenas o miolo sem capa/contracapa, mantendo o fluxo editorial interno.
5. Sanitizar o PDF físico removendo anotações e marcações não imprimíveis.
6. Validar dimensões, páginas, anotações, metadados críticos e texto fora das margens.

## Saídas esperadas

- `main_kdp_print_160x230mm.pdf` — PDF completo refluído, incluindo capa/contracapa internas do projeto.
- `main_miolo_amazon_kdp_160x230mm_SEM-LINKS_SAFE-MARGINS.pdf` — miolo físico recomendado.
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_160x230mm_SEM-LINKS_SAFE-MARGINS_v1.9_2026-07-26.pdf` — cópia nomeada para entrega.

## Critérios de aceitação

1. O PDF final do miolo existe.
2. O tamanho da página do miolo é **160 × 230 mm**, tolerância máxima de 0,5 mm.
3. O conteúdo foi refluído por LaTeX no novo formato, não apenas escalado a partir do PDF 6" × 9".
4. O PDF físico não possui hyperlinks/anotações (`/Annots = 0`).
5. O catálogo do PDF não possui `/OpenAction`, `/Names`, `/Outlines`, `/PageMode` ou `/AA`.
6. Criptografia: não.
7. Termos críticos preservados no texto extraível:
   - `Molambudos`;
   - `Passaporte`;
   - `MEM-07`;
   - `Nota Histórica`;
   - `9798189170492`.
8. Nenhum bloco de texto ultrapassa o corte da página.
9. Nenhum bloco de texto ultrapassa as margens mínimas KDP para o miolo final de 296 páginas:
   - interna: 12,7 mm (0,5 in);
   - externa: 6,35 mm (0,25 in);
   - superior: 6,35 mm (0,25 in);
   - inferior: 6,35 mm (0,25 in).
10. Cabeçalhos, rodapés e folios podem ser suprimidos na variante física 160 × 230 mm se necessário para evitar alerta de margem no KDP.

## Observação KDP

O tamanho 160 × 230 mm deve ser selecionado no KDP apenas se estiver disponível para o tipo de livro/mercado escolhido. A validação local não substitui o previewer da Amazon.
