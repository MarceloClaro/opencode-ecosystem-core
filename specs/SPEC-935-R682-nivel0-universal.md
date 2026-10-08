# SPEC-935-R682 — Nível 0 Universal: todos os elementos e termos para leigos

**Status:** proposta/executada — 05 out. 2026
**Problema:** 378 `\elemento` + dezenas de termos discriminados (gate, Jaccard, PPV, FAIR, MCP, A2A...); E1-E7 leigo (R681) cobre só 7. Leitor nível 0 trava no vocabulário antes do mecanismo.
**Solução sem risco:** não reescrever 378 fichas; criar camada tradutora única `mod-18-nivel0-universal.tex` (Parte Nível 0) com: (a) glossário A-Z ~70 termos em 12 palavras + analogia + onde mora; (b) método de 1 minuto para ler qualquer ficha; (c) 5 fichas-modelo totalmente traduzidas cobrindo todos os tipos de caixa; (d) índice por categoria do catálogo (238 agentes em 14 famílias).
**Aceitação:** CA1 novo módulo + input no main; CA2 ≥60 termos nivel 0, cada um com frase leiga, analogia da casa e rota de código quando houver; CA3 2 fluxogramas (ler ficha em 1 min; termo→analogia→conferência); CA4 nota NotebookLM; CA5 check.py ok + pdflatex 0 `!`; CA6 anti-overclaim preservado.
