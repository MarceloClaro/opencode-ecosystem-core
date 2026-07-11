# R140 — Exclusão do conteúdo de usuário (Molambudos etc.) via .gitignore

## Objetivo

Fechar a última "frente aberta" (Molambudos) da forma decidida pelo
usuário: **manter o conteúdo criativo/de pesquisa fora do ecosystem-core**,
que é um repositório de infraestrutura ("só o código do ecossistema").

## Contexto

Após versionar as três frentes de código (R137 cloud, R138 SPEC-108, R139
pdf2latex), sobrou na árvore de trabalho um grande volume de conteúdo de
usuário: o livro de ficção **Molambudos** (`projetos/molambudos/`,
`templates/livro/molambudos/`, PDFs, `REVISAO_MOLAMBUDOS.md`), specs de
metodologia do livro (`SPEC-911..917-molambudos-*`), e material de pesquisa
(`livro-odontologia-ia/`, `pesquisa/`, `PROJETO 1/`, `artigos_dl_*.json`).

O trabalho Molambudos já está **registrado no ledger** (ciclos R130–R134);
o que estava pendente era apenas o conteúdo bruto do livro. Decisão do
usuário (perguntado explicitamente): **excluir tudo via `.gitignore`**.

## Mudanças Entregues

1. **`.gitignore`**: novo bloco "Conteúdo de usuário" ignorando
   `projetos/`, `pesquisa/`, `livro-odontologia-ia/`, `PROJETO 1/`,
   `REVISAO_MOLAMBUDOS.md`, `artigos_dl_odontologia.json`,
   `templates/livro/molambudos/`, `templates/livro/ia-em-odontologia/`,
   `specs/SPEC-91[0-9]-molambudos-*.md`, `specs/SPEC-950-*`. Mais patterns
   para artefatos binários de templates (`templates/**/*.pdf|*.csv|outputs/`,
   `*:Zone.Identifier`).
2. **`PROGRESS.md`**: marca as frentes R137–R140 como concluídas, com a
   dívida assumida documentada.

## Verificação

- `git check-ignore` confirma que todo o conteúdo de usuário listado está
  ignorado; os 5 PDFs e 25 CSVs **já rastreados** permanecem rastreados
  (gitignore não desrastreia — só afeta novos arquivos).
- Nenhuma spec/arquivo Molambudos estava versionado antes (não há remoção).
- Suíte inalterada (mudança é só de repo-hygiene): 1405 passed, 5 skipped.

## Lições

1. **"Fechar uma frente" nem sempre é commitar — às vezes é decidir,
   explicitamente, não versionar.** Molambudos é conteúdo criativo do
   usuário; forçá-lo no repo de infraestrutura contrariaria "só o
   ecossistema". A decisão foi confirmada com o usuário, não presumida.
2. **Procedência e propósito ditam o versionamento.** Assim como os 324
   scripts cloud (licença não auditada) e diferente dos `.bst` CTAN (LPPL),
   o conteúdo de usuário fica fora — cada caso decidido pelo que o artefato
   é, não por conveniência.
3. **`templates/projects/` (1593 arquivos já rastreados) foi deixado como
   está** — os arquivos avulsos ali são de outras frentes; o CLAUDE.md
   avisa para não misturar, então não entraram neste commit nem no ignore.

## Score

**7.8/10**

- Fecha o ciclo de versionamento de forma honesta e alinhada à decisão do
  usuário, com a dívida documentada.
- É repo-hygiene/processo, não código; baixo risco, sem teste (nada a
  testar num `.gitignore` além de `git check-ignore`, que foi verificado).
- Deixa `templates/projects/` com trabalho avulso não resolvido (fora de
  escopo desta rodada, pertence a outras frentes).
