# SPEC-935-R261 — Remoção de hiperlinks/anotações do miolo KDP

## Objetivo

Gerar versões do miolo Amazon/KDP sem hiperlinks clicáveis e sem texto fora das margens, pois o KDP está rejeitando os links internos que levam diretamente às páginas/fragmentos e alertando que há texto fora da área segura.

## Problema

O PDF original contém anotações de link geradas pelo `hyperref`/rotas internas do LaTeX. Mesmo que sejam úteis para leitura digital, essas anotações não devem existir no arquivo de miolo físico para upload na Amazon/KDP.

Além disso, algumas `\margnota` das páginas finais aparecem como texto na margem física do PDF e podem exceder a área aceita pelo previewer KDP. Para o modo de impressão, essas notas devem ser suprimidas sem alterar a versão digital normal.

## Entradas

- `main_miolo_amazon_kdp_6x9_bleed_safe.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_SAFE_v1.7_2026-07-26.pdf`
- `main_miolo_amazon_kdp_6x9_sem_sangria.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_SEM-SANGRIA_v1.7_2026-07-26.pdf`

## Saídas esperadas

- `main_miolo_amazon_kdp_6x9_bleed_safe_SEM-LINKS.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_bleed_SAFE_SEM-LINKS_v1.8_2026-07-26.pdf`
- `main_miolo_amazon_kdp_6x9_sem_sangria_SEM-LINKS.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_6x9_SEM-SANGRIA_SEM-LINKS_v1.8_2026-07-26.pdf`

## Método

Criar modo condicional `KDPPRINT` em `main.tex` para:

- suprimir `\margnota` apenas no PDF de impressão;
- imprimir rotas/índice como texto, sem `\hyperlink` explícito.

Depois usar `pypdf` para remover resíduos de marcação não imprimível:

- `/Annots` de todas as páginas;
- `/OpenAction` do catálogo, se presente;
- `/Names` do catálogo, se presente;
- `/Outlines` do catálogo, se presente.

## Critérios de aceitação

1. Cada PDF de saída existe.
2. Cada PDF de saída preserva número de páginas.
3. Cada PDF de saída preserva tamanho de página.
4. Cada PDF de saída preserva texto crítico:
   - `Molambudos`;
   - `Passaporte`;
   - `MEM-07`;
   - `Nota Histórica`;
   - `9798189170492`.
5. Cada PDF de saída tem `0` anotações (`/Annots`) nas páginas.
6. Cada PDF de saída não possui `/OpenAction`, `/Names` ou `/Outlines` no catálogo.
7. Criptografia: `no`.
8. Nenhum bloco de texto ultrapassa a área de corte do PDF.
9. As notas de margem (`\margnota`) não aparecem no PDF de impressão KDP.
