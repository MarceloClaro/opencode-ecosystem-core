---
name: artigo-academico-abnt
description: Pipeline completo de artigo científico ABNT para a orquestração do Core: busca de artigo-gap com auditoria Crossref, LaTeX modular abnTeX2/BibTeX com compilação verificada, conversão LaTeX→DOCX, deck MIRA de defesa com simulação de banca, scanners de rigor e registro evolutivo. Use para TCC, relato de experiência, revisão integrativa, defesa de banca e auditoria bibliográfica; nunca invente DOI, dados ou aprovação ética; nunca declare Qualis, nota ou aceite como garantidos.
---

# Artigo Acadêmico ABNT (plugin do Core)

## Quando acionar

Quando o usuário pedir artigo, TCC, relato de experiência, revisão, defesa
de banca, conversão LaTeX/DOCX/PPTX, auditoria de referências ou verificação
de citações. O orquestrador `marceloclaro` decompõe a demanda e roteia cada
frente ao agente do catálogo (`tdah-gap-hunter`, `abnt-latex-modular`,
`bibtex-crossref-auditor`, `docx-abnt-converter`, `mira-deck-academico`) ou
às ferramentas do MCP `artigo-academico` (`auditar_referencia`,
`verificar_citacoes`, `pipeline_status`, `validar_deck`).

## Fluxo canônico

1. **M0 — Contrato:** área, nível, pergunta, dados, norma, periódico-alvo, prazo.
   Modo lote: lista de artigos (`research.manuscript.ArticleConfig` por item);
   o motor `produzir_lote` isola um workspace por artigo e devolve tabela-resumo.
2. **M1 — Gap:** artigo-âncora localizado por busca profunda e auditado em fonte primária (Crossref/DOI/SciELO). Sem DOI resolvível: `[NÃO VERIFICADA]`.
3. **M2 — Manuscrito:** módulos LaTeX (main + tópicos + .bib), ordem hyperref→abntex2cite, ciclo pdflatex→bibtex→pdflatex×2 até `undefined=0`.
4. **M3 — Resultados quantitativos (quando houver CSV real):** usar `research/discovery/` (desenho PICO + H0/H1 falsificável + poder; Welch/Pearson/Cohen sempre com n, p, IC e efeito; Holm; pacote de replicação). Estatística corrobora, nunca prova; sem dados, produzir protocolo — nunca fabricar resultados.
4. **M3 — Conversões:** DOCX via parser do .aux (citações reconstruídas), PPTX opcional via efeitos nativos; validar cada formato (XML + conversão + extração).
5. **M4 — Defesa:** deck MIRA (cards, navegação, animações discretas, `prefers-reduced-motion`, `SMOKE_OK`) + roteiro cronometrado + banca simulada com respostas citando a seção do manuscrito.
6. **M5 — Verificação:** scanners de rigor (SRI/falsificabilidade/falácias) + Merkle + Contrato de Força de Alegação (`research/claim_strength/CONTRACT.md`, via MCP `auditar_forca_alegacao`): nenhuma frase acima de "é coerente com / pode sugerir" sem evidência nova e autorização; resultado reportado com anti-overclaim (scanner e guarda são heurísticas, nota final é da banca).
7. **M6 — Reflexão:** SPEC formal em `specs/` quando o artefato nascer sem uma; ciclo no EvolutionRegistry com lições reutilizáveis.

## Bloqueadores

- Não inventar autores, DOI, amostras, instrumentos, aprovação ética ou dados.
- Não declarar Qualis A1, nota 10 ou aceite como garantidos.
- Não remover declaração de uso de IA do manuscrito (integridade prevalece sobre não-detecção).
- Não converter associação em causalidade; estudo N=1 gera hipóteses, não confirma.
- Medicamento/tratamento não informado: registrar literalmente "não declarado", sem presumir ausência.

## Hooks associados

- `latex_cite_guard.sh` (PreToolUse): nega escrita de .tex com chaves `\cite` sem entrada no .bib do projeto.
- `js_smoke_dom.sh` (existente): smoke test de JS inline dos decks (classe R580).
