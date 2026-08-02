---
spec_id: SPEC-935-R264
title: Molambudos 160x230mm com folios seguros para KDP
component: projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r264_molambudos_safe_folios.py
---

# SPEC-935-R264 — Molambudos 160 × 230 mm com folios seguros

## Objetivo

Corrigir a variante física **160 × 230 mm** de `Molambudos — O Diário do Paciente 1.260` para restaurar números de página impressos, mantendo:

- ausência de cabeçalhos;
- folios/números de página em rodapé central seguro;
- rotas físicas utilizáveis por referência de página;
- compatibilidade técnica com Amazon KDP;
- PDF sem hyperlinks/anotações clicáveis.

## Problema

A versão R263 removeu cabeçalhos, rodapés e folios para eliminar alertas de margem do KDP. Tecnicamente passou no preflight, mas prejudicou a experiência de leitura não-linear: as rotas continuam com referências de página, porém o leitor físico não tem números impressos para localizar os destinos.

## Estratégia

1. Manter o formato 160 × 230 mm e o conteúdo refluído.
2. Manter `KDPPRINT` para remover hyperlinks e marginália problemática.
3. Remover cabeçalhos corridos.
4. Restaurar apenas o número de página no rodapé central.
5. Posicionar o rodapé dentro da margem inferior mínima KDP.
6. Extrair e sanitizar o miolo final.
7. Validar que o rodapé não causa texto fora das margens.

## Saídas esperadas

- `main_kdp_print_160x230mm.pdf` recompilado com folios seguros.
- `main_miolo_amazon_kdp_160x230mm_COM-FOLIOS_SEM-LINKS_SAFE-MARGINS.pdf`.
- `Molambudos_O-Diario-do-Paciente-1260_miolo_Amazon-KDP_160x230mm_COM-FOLIOS_SEM-LINKS_SAFE-MARGINS_v2.0_2026-07-26.pdf`.

## Critérios de aceitação

1. PDF final existe.
2. Tamanho de página: 160 × 230 mm, tolerância de 0,5 mm.
3. Número de páginas do miolo: 296.
4. Cabeçalhos corridos ausentes no miolo físico.
5. Folios/números de página presentes em rodapé central na maior parte das páginas numeráveis.
6. `/Annots = 0`.
7. Catálogo sem `/OpenAction`, `/Names`, `/Outlines`, `/PageMode` e `/AA`.
8. Criptografia ausente.
9. Termos críticos preservados: `Molambudos`, `Passaporte`, `MEM-07`, `Nota Histórica`, `9798189170492`.
10. Nenhum bloco de texto, incluindo folios, fora do corte.
11. Nenhum bloco de texto fora das margens mínimas KDP para 296 páginas:
    - interna: 12,7 mm;
    - externa: 6,35 mm;
    - superior: 6,35 mm;
    - inferior: 6,35 mm.

## Observação

Esta correção não altera o texto literário nem os destinos das rotas. Altera apenas a apresentação física dos folios no miolo KDP.
