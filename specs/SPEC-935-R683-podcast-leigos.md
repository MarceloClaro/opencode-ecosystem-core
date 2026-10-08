# SPEC-935-R683 — Podcast do Livro Core para leigos (NotebookLM Audio Overview)

**Status:** executada — 05 out. 2026
**Notebook:** `ba4adef8-84f6-4790-bfcd-1ed1cd25a275` (Livro Core - Atlas Visual E1-E7 para Leigos)
**Fontes do episódio:** texto leigo pt-BR `d0573603` + Nii 1986 `10.1609/aimag.v7i2.537` + Ioannidis 2005 `10.1371/journal.pmed.0020124` (FAIR via DOI falhou 406/captcha; Nii .538 trocado por .537 e excluído).

## Critérios

1. [CA1] Pipeline `multi-format` 3/3 ok: áudio `74cf499b`, report `a4d69f43` (completed), flashcards `d73b0591` (9, completed).
2. [CA2] Arquivos em `livro-core/output/podcast/`: `livro-core-para-leigos.m4a` (áudio), `roteiro-briefing.md` (NotebookLM, EN técnico), `roteiro-leigo-ptbr.md` (roteiro leigo pt-BR do Core, ~8 min), `flashcards.json`, `feed.xml` com enclosure.
3. [CA3] Capítulo `mod-19-podcast.tex` no livro com o que ouvir, roteiro resumido e como reproduzir o episódio (comando `nlm download audio`).
4. [CA4] Limites declarados: áudio gerado por IA a partir das fontes do caderno; pode conter simplificações; vale o texto do livro + fontes com DOI; sem promessa de voz, sotaque ou duração exata antes da conclusão do `unknown`→`completed`.
5. [CA5] Gates técnicos: `check.py` ok, `pdflatex` 0 `!`, `ffprobe` (duração/taxa) registrado quando o m4a concluir; feed com length real e 404 conferido se publicar.
