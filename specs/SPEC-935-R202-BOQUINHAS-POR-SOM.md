# SPEC-935-R202 — Boquinhas Ilustradas por Som (Volume 1)

**Status:** CONCLUÍDO
**Data:** 2026-09-12
**Autor:** marceloclaro (orquestrador primário)
**Relação:** R201 (VOLUME1-NEUROINCLUSIVO) — complemento direto
**Gatilho do usuário:** "faltou colocar as boquinhas para cada sons"

## Resultado (evidências de 2026-09-12)

- CA-01 ✓ — `alfabetizar.cls` v3.1 compila; novos comandos `\boca@aberta|sorriso|bico|fechada|
  labiodental|dental|palatal|velar|nasal|muda`, `\bocadiagrama{estilo}{rótulo}{legenda}`,
  `\bocaicona{estilo}`, `\boq[estilo]{letra}{texto}`, `\somipa[estilo]{...}{...}{...}{...}`.
- CA-02 ✓ — 26/26 boquinhas (16 revisadas + 10 novas F,G,J,K,N,P,V,Z,W,Y) e 26/26 pistas
  articulatórias (verificado por contagem no `.tex` e no texto extraído do PDF).
- CA-03 ✓ — 62/62 linhas `\somipa` com estilo mapeado pelo TIPA (0 default residual).
- CA-04 ✓ — 0 ocorrências de "aspirad" em parte1..6 + main; H sempre mudo (título da lição 32,
  boquinha `muda`, pista, regra, checkboxes, dica do professor, seção Kumon e tabela B-11).
- CA-05 ✓ — `pdflatex -interaction=nonstopmode main.tex` 2×, exit 0; 0 Missing character;
  42 overfulls cosméticos pré-existentes (sem novos); 514 páginas.
- CA-06 ✓ — Versão 4.5 na capa, créditos e main.tex.
- CA-07 ✓ — Ciclo R504 registrado no EvolutionRegistry.

## Correção factual adicional (não prevista na spec, exigida pelo gate de integridade)

- `\thispagestyle{planchetarastreio}` era usado sem nunca ter sido definido (erro latente que
  produzia PDF com exit≠0). Adicionada a definição `\fancypagestyle{planchetarastreio}` na classe.

## Problema

O Volume 1 usa a técnica da boquinha apenas como **caixa de texto** ("Posição da Boca")
em 16 letras; as 10 letras do "Alfabeto Completo" (F, G, J, K, N, P, V, Z, W, Y) não têm
boquinha nem pista articulatória; e nenhum som possui **figura ilustrada** de boca.
Adicionalmente, o livro ensina o H como "aspirado no início" — incorreto no português
brasileiro (H é sempre mudo; aparecimento real: dígrafos CH, LH, NH).

## Escopo

1. Criar **figuras originais em TikZ** de posição da boca (estilo didático simples,
   frontão, sem fotografia — não reproduz a marca Boquinha® de terceiros).
2. Aplicar figura + texto + pista articulatória às **26 letras** (16 revisadas + 10 novas).
3. **Ícone de boca pequeno** em cada linha de som IPA (`\somipa`) da caixa
   "Todos os Sons desta Letra", mapeado pelo valor TIPA.
4. **Corrigir o H**: sempre mudo; sem figura de sopro; papel real nos dígrafos.

## Critérios de aceitação

- CA-01: `alfabetizar.cls` compila com novos comandos (`\boca@...`, `\bocadiagrama`,
  `\bocaicona`, `\boq[estilo]{...}`, `\somipa[estilo]{...}`).
- CA-02: 26/26 letras possuem boquinha (figura + texto); 26/26 possuem pista articulatória.
- CA-03: 100% das linhas `\somipa` de parte2 com estilo mapeado pelo TIPA (0 default residual).
- CA-04: H mudo — nenhuma ocorrência de "aspirado" referindo-se ao H sozinho;
  figura `muda` sem seta de ar.
- CA-05: `pdflatex -interaction=nonstopmode main.tex` 2× → exit 0, 0 "Missing character",
  novas páginas contêm figuras (verificação por contagem de figuras no log/PDF).
- CA-06: versão do livro atualizada para 4.5 (capa, créditos, main.tex).
- CA-07: ciclo de evolução registrado (R504) e reflexão no MetaBus.

## Não-objetivo (limites éticos)

- Não há alegação clínica/fonoaudiológica; as figuras são **apoios opcionais**,
  nunca exercício obrigatório de imitação ou contato;
- Não reproduz imagens registradas da metodologia Boquinha®;
- Não modifica conteúdo de psicometria/triagem (parte6).

## Verificação

- Compilação + contagem de ocorrências por script (`grep` textual) antes e depois.
- Registro de ciclo no EvolutionRegistry e lição no MetaBus/confidence ledger.