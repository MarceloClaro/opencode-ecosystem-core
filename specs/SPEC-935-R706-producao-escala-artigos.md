# SPEC-935-R706 — Motor de produção em escala de artigos científicos

**Status:** `em implementação`
**Ciclo:** R706
**Data:** 2026-10-07

## 1. Problema

O pipeline do relato TDAH (R689–R705) é pontual: scripts com conteúdo
codificado (`gerar_docx.py` com REFs fixas e quadros fixos, `gerar_pptx.py`
com textos fixos). Produzir *qualquer* artigo solicitado exige generalizar:
mesma estrutura, mesmos gates, conteúdo parametrizável, múltiplos artigos
em lote com isolamento.

## 2. Objetivo

Motor `research/manuscript/` que produz **qualquer artigo científico**
(revisão integrativa, estudo de caso, artigo original, TCC, dissertação)
a partir de `ArticleConfig`, com os mesmos gates do pipeline TDAH e sem
conteúdo codificado no motor.

## 3. Critérios de aceitação

- [ ] AC1 — `ArticleConfig` valida: título, autores[], área, nível, tipo (5 tipos), norma, idioma, periódico-alvo, diretório de saída; tipos inválidos e campos vazios são rejeitados com erro explícito.
- [ ] AC2 — `scaffold_workspace(config)` cria workspace isolado `artigos/<slug>/` com `main.tex` (preâmbulo ABNT genérico), `modulos/` por tipo, `referencias.bib` esqueleto, `triagem.jsonl` vazio e README de pendências; nunca sobrescreve workspace existente sem `force=true`.
- [ ] AC3 — Conversor DOCX genérico: referências lidas do `.bbl` compilado (não de lista fixa) e tabelas lidas dos ambientes `tabular` dos módulos (não de dados fixos); citações reconstruídas do `.aux`.
- [ ] AC4 — `run_gates(diretorio)` executa: citações (undefined=0), força de alegação (relata achados, nunca aprova), artefatos (existência+hash); falha fechada em diretório inexistente.
- [ ] AC5 — `produzir_lote([configs])` processa N artigos em sequência com isolamento (um workspace por artigo) e tabela-resumo por artigo (gates ok/falha + artefatos).
- [ ] AC6 — Helpers PPTX (`pptx_theme.py`) neutros de conteúdo: paleta, cards, barras, tabelas; importação de `pptx` guardada (erro explícito se ausente).
- [ ] AC7 — Testes herméticos `tests/test_r706_manuscript_scale.py` (sem rede/subprocesso/LLM): config, scaffold em tmp, parse de tabular/.bbl em fixtures, gates em fixtures, lote com 2 artigos fictícios.
- [ ] AC8 — Skill `artigo-academico-abnt` M0 aceita modo lote (lista de artigos) além de artigo único.

## 4. Fora de escopo (declarado)

- Geração do *conteúdo* científico (texto dos módulos): pertence ao orquestrador/LLM + agentes; o motor fornece estrutura, validação e montagem.
- Novos MCPs/servidores: reutilizar `artigo-academico-mcp` (7 ferramentas).
- Tradução automática e checagem de similaridade externa (ferramenta institucional).

## 5. Verificação

- `pytest tests/test_r706_manuscript_scale.py -q` verde.
- Demo: scaffold de artigo fictício em /tmp + gates executados.
- Novos arquivos sob `research/manuscript/`; `gerar_docx.py`/`gerar_pptx.py` do TDAH intactos (legado funcional).
