# SPEC-935-R686 — Podcast por módulo em pt-BR (fila progressiva por cota)

**Status:** parcial honesta — 05 out. 2026
**Caderno:** `e05e32a6-5ecc-497d-b262-939f9e4b1073` com 9 fontes PT (uma por grupo de módulos).
**Formato:** `--language pt-BR --length short` (~5-7 min), um áudio por módulo com foco próprio:
detalhe, funcionalidade, justificativas com DOI, interações, agentes/subagentes, specs, hooks e ferramentas.

## Entregue agora (7 episódios em `output/podcast/modulos/`)

02 orquestração 6:46, 03 memória 6:25, 04 qualidade 5:22, 05 raciocínio 6:05,
07 integrações 6:26, 10 catálogo 6:15, 13 ativação 5:11. Índice `indice-modulos.md`
e capítulo `mod-20-podcast-modulos.tex`. Livro 332 pp., check ok, pdflatex 0 `!`.

## Em geração (2)

01 fundações e 06 ciência (criações duplicadas pelo CLI aguardam vez no servidor;
baixar o primeiro concluído de cada foco como `mod-01-fundacoes.m4a` e `mod-06-ciencia.m4a`).

## Fila pós-cota (15 módulos)

00a, 00b, 01b, 01c, 01d, 08, 09, 09a, 12, 14, 15, 16, 17, 18, 19 — após renovar a
janela rolante (20:36 -03; curta consome ~4,5%). Comando por módulo:

    nlm audio create e05e32a6-5ecc-497d-b262-939f9e4b1073 --language pt-BR --length short \
      --focus "Módulo <NOME>: detalhe, funcionalidade, justificativas, interações, agentes, specs, hooks" \
      --source-ids <ID-da-fonte-do-grupo> --confirm

e download para `output/podcast/modulos/mod-<NN>-<nome>.m4a`.

## Limite

Áudio resume fontes; vale texto + DOI. Cota impede os 24 de uma vez — fila documentada, sem overclaim.
