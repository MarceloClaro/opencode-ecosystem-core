---
spec_id: SPEC-935-R402
title: Molambudos — quatro edições de impressão 160×230mm com jobname próprio, capas por idioma e paginações seladas
component: projetos/molambudos/Molambudos_VictoriaRegia, scripts/molambudos_selo.py, scripts/audit_r362_pdf_layout.py
status: verified
test_file: tests/test_r399_molambudos_selo_e_capa.py
---

# SPEC-935-R402 — Quatro Edições de Impressão

**Data:** 2026-08-05
**Motivação:** *"agora você vai corrigir main_kdp_pt_160x230mm; main_en e main
e main_zh deve estar também corrigido, o manuscrito como
main_kdp_print_160x230mm e o mesmo como o miolo"* — seguido de *"não esqueça
de atualizar as paginações"*.

## 1. Quatro arquivos, um único PDF

Existiam **quatro** wrappers de impressão com o mesmo basename:

| Arquivo | Miolo que carregava |
|---|---|
| `main_kdp_print_160x230mm.tex` (raiz) | `main.tex` (PT) |
| `en/main_kdp_print_160x230mm.tex` | `en/main_en.tex` |
| `zh/main_kdp_print_160x230mm.tex` | `zh/main_zh.tex` |
| `tri/main_kdp_print_160x230mm.tex` | `tri/main_tri.tex` |

Os quatro usam caminhos relativos à raiz do livro (`\input{en/main_en.tex}`),
ou seja, são compilados **de lá** — e o LaTeX nomeia a saída pelo basename do
`.tex`. Os quatro produziam `main_kdp_print_160x230mm.pdf`. Quem compilasse
dois sobrescrevia o outro, sem aviso e sem erro.

Foi exatamente o que o R399 encontrou ao inspecionar o PDF da raiz e achar
texto chinês onde deveria haver português: era o build trilíngue ocupando o
nome do PT. O R399 contornou criando `main_kdp_pt_160x230mm.tex` só para o
português, deixando os outros três ainda colidindo entre si.

**Correção:** um wrapper por edição, com jobname próprio, todos na raiz do
livro (que é de onde já eram compilados):

| Wrapper | Miolo | Páginas | Trim medido |
|---|---|---|---|
| `main_kdp_pt_160x230mm.tex` | `main.tex` | 435 | 160,0 × 230,0 mm |
| `main_kdp_en_160x230mm.tex` | `en/main_en.tex` | 427 | 160,0 × 230,0 mm |
| `main_kdp_zh_160x230mm.tex` | `zh/main_zh.tex` | 397 | 160,0 × 230,0 mm |
| `main_kdp_tri_160x230mm.tex` | `tri/main_tri.tex` | 1115 | 160,0 × 230,0 mm |

Cada um herda integralmente o miolo do seu idioma — mesmo texto, mesmos
fragmentos, mesma navegação. O que muda é só a geometria de impressão.

`scripts/audit_r362_pdf_layout.py` foi atualizado: a edição `kdp_tri` aponta
para `main_kdp_tri_160x230mm.tex`.

## 2. Paginações

O miolo PT passou de **433 para 435 páginas** — o índice ganhou 11 entradas
(R401) e os três mapas foram ampliados. Isso desatualizou a lombada da capa, e
`test_a_paginacao_declarada_na_capa_bate_com_o_miolo` falhou de imediato: era
para isso que ele existia.

Como cada paginação exige lombada própria, foram geradas as capas das outras
duas edições de idioma, a partir do mesmo arquivo parametrizado:

| Capa | Páginas | Lombada | Capa total |
|---|---|---|---|
| `capa_completa_pt_160x230mm` | 435 | 25,93 mm | 352,3 × 236,3 mm |
| `capa_completa_en_160x230mm` | 427 | 25,46 mm | 351,8 × 236,3 mm |
| `capa_completa_zh_160x230mm` | 397 | 23,67 mm | 350,0 × 236,3 mm |

A arte serve às três: a contracapa já traz os blocos em PT, EN e ZH.

O selo passou a registrar e **conferir** oito paginações — quatro miolos
digitais e quatro de impressão — em vez de apenas a do português.

## 3. Zero com aparência de fato medido

Ao gerar o selo enquanto o preflight recompilava as edições, `_paginas()` leu
`main.pdf` em meio à reescrita: o PDF abriu sem erro e reportou **0 páginas**.
O selo gravou esse zero.

Um zero assim é pior que campo ausente, porque tem aparência de medição — e é
a paginação que dimensiona a lombada. Uma capa gerada contra ela seria
recusada pela gráfica, com o selo "confirmando" o número errado.

`_paginas()` passou a devolver `None` quando o PDF não abre ou reporta zero
páginas, e há teste cobrindo o caso com um PDF truncado.

## 4. Guardas novos

Em `tests/test_r399_molambudos_selo_e_capa.py`:

1. `test_selo_nao_grava_paginacao_zero_de_pdf_em_construcao`
2. `test_selo_registra_a_paginacao_das_quatro_edicoes_de_impressao`
3. `test_cada_edicao_de_impressao_tem_wrapper_com_jobname_proprio` — falha se
   um `main_kdp_print_160x230mm.tex` reaparecer no corpus ativo. O teste
   ignora `_archive/`, que guarda os backups de cada ciclo e deve preservá-los
   como estavam.

## 5. Critérios de aceitação

1. Cada edição tem um wrapper de impressão com jobname próprio; nenhum
   basename colide no corpus ativo. ✔
2. As quatro edições compilam com trim medido de 160,0 × 230,0 mm. ✔
3. Cada idioma tem capa com lombada derivada da sua própria paginação. ✔
4. O selo registra e confere as oito paginações. ✔
5. O selo nunca grava paginação zero de um PDF em construção. ✔
6. Preflight R362 com `--build`: `overall_internal_spec_passed=True`,
   648/648 rotas, zero violações nas cinco edições. ✔
