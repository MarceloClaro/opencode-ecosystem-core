# SPEC-935-R684 — Podcast em português: apresentação consolidada única (leigo+dev)

**Status:** executada — 05 out. 2026
**Exigência:** áudio EM PORTUGUÊS como apresentação única: o que é, consolidado do livro,
especial, limitação, ajuda ao pesquisador, funcionamento com minúcia e justificativas,
equilíbrio didático leigo-dev.

## Entregas

1. **Faixa principal garantida em pt-BR** `livro-core-apresentacao-ptbr.mp3` (2.086.656 bytes,
MP3 64kbps, 4:20): narração pt-BR do `roteiro-consolidado-ptbr.md` em 6 blocos
(apresentação, consolidado em seis frases, especial, limites, pesquisador, minúcia com Jaccard e PPV).
2. **Episódio longo NotebookLM** `livro-core-consolidado-notebooklm.m4a` (15.299.748 bytes,
AAC 96kbps, 20:56): caderno NOVO `947abff2` com 4 fontes 100% em português
(pipeline multi-format 3/3). Idioma da narração conforme o gerador — conferir ouvindo;
o briefing do NotebookLM sai em template inglês mesmo com fontes PT, sem implicar o áudio.
3. Episódio anterior `livro-core-para-leigos.m4a` (25 min, fontes EN) mantido como bônus.
4. `feed.xml` refeito em pt-BR com 2 itens e lengths reais; `mod-19-podcast` reescrito como
apresentação consolidada; livro 330 pp., check ok, pdflatex 0 `!`.

## Limite declarado

Voz TTS resume o roteiro; NotebookLM resume as fontes. Em divergência vale o impresso com DOI.
Durações e vozes variam por gerador.
