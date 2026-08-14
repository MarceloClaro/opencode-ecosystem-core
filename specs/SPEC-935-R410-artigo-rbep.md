# SPEC-935-R410 — Adequação do artigo às normas da Revista Brasileira de Estudos Pedagógicos (RBEP/INEP)

- **Ciclo**: R410
- **Data**: 2026-08-12
- **Status**: em implementação
- **Dependência**: R409 (ARTIGO_PUBLICAVEL.md, teste verde) e R408 (auditoria de reprodutibilidade)

## Objetivo

Produzir a versão de submissão do manuscrito do R409 adequada às diretrizes
editoriais da **Revista Brasileira de Estudos Pedagógicos (RBEP)**, editada pelo
INEP — periódico de educação com **Qualis CAPES A1 na área de Educação**
(quadriênios 2017–2020 e 2021–2024), e-ISSN 2176-6681, acesso aberto CC-BY,
indexada no SciELO.

## Requisitos funcionais

1. **Trilinguismo** — título em português, inglês e espanhol; resumo (PT),
   abstract (EN) e resumen (ES), cada um com densidade informativa (≥ 60
   palavras) e contendo os números centrais do estudo.
2. **Palavras-chave** — 3 a 5 termos por idioma (PT/EN/ES), preferencialmente
   do Thesaurus Brasileiro de Educação (Brased); sem repetição integral de
   termos do título.
3. **Citações** — ABNT NBR 10520/2002 (sistema autor-data, sobrenomes em caixa
   alta nas citações parentéticas); ≥ 10 citações parentéticas no corpo.
4. **Referências** — ABNT NBR 6023/2002, lista única em ordem alfabética, com
   ano e DOI/URL, subconjunto das 33 obras auditadas no R408; ≥ 12
   referências; ≥ 8 com DOI.
5. **Notas de rodapé evitadas** — ≤ 3 ocorrências no corpo.
6. **Corpo sem avisos editoriais** — o manuscrito em si NÃO contém "candidato",
   "aguarda revisão", "revisão por pares", "submissão", "Qualis", "manuscrito
   gerado em", "status:"; esses avisos ficam apenas em `CARTA_AO_EDITOR.md`
   (metadados de submissão).
7. **Anti-overclaim** — todos os termos bloqueados do R408/R409 ausentes
   (causalidade, "AUC", "0,997", "16,06", "percentil", "prova", etc.);
   linguagem associativa; nenhum resultado false-positive da versão original.
8. **Consistência com R409** — números e tabelas idênticos aos do
   `ARTIGO_PUBLICAVEL.md`; todo número do resumo presente em
   `provenance.json` (tolerância 0,005); nenhum placeholder.
9. **Ciência aberta** — carta ao editor declara disponibilidade integral de
   dados (WDI, cache SHA-256), código e proveniência.

## Critérios de aceitação

- `tests/test_r410_artigo_rbep.py` verde (RED → GREEN).
- Suíte acumulada R408 + R409 + R410 verde.
- `doctor` sem falhas novas.
- Ciclo R410 registrado no `evolution/cycles.json` com score e lições.
- PROGRESS.md atualizado.

## Entregáveis

- `academic/papers/arm_education_audit/ARTIGO_RBEP_SUBMISSAO.md` (corpo do
  manuscrito, sem avisos editoriais).
- `academic/papers/arm_education_audit/CARTA_AO_EDITOR.md` (carta de
  submissão com declarações de ciência aberta e conduta).
- `tests/test_r410_artigo_rbep.py`.

## Não escopo

- Não declara o manuscrito "Qualis A1" nem "pronto para publicação" (anti-overclaim).
- Não altera números, dados, método ou resultados do R409.
- Não submete o artigo de fato à RBEP (ação humana).
