# R124 — Capa e Contracapa com Arte Vetorial TikZ Real

## Objetivo

Elevar o `publishing/cover_designer.py` de placeholders (blocos de cor
chapada + comentário `% ESPAÇO PARA ILUSTRAÇÃO` + prompt de IA externa)
para **arte vetorial TikZ real, compilável direto no PDF do livro** —
gradientes, formas geométricas por estilo, lombada dimensionada pela
contagem de páginas e ficha catalográfica (CIP) na contracapa.

## Motivação

Pedido do usuário: "capa e contracapa de livros"; na escolha de escopo,
"Melhorar a capa LaTeX existente" com arte TikZ real (gradientes/formas),
lombada e ficha catalográfica, compilável no PDF final.

Estado anterior do `CoverDesigner.design_cover`: `capa.tex` era só
`\pagecolor` + título/autor centralizados e um comentário
`% \includegraphics{...}` apontando para uma arte que ninguém gerava —
a ilustração real ficava delegada a Midjourney/DALL·E. A contracapa não
tinha ficha catalográfica; não havia lombada; e nada carregava os
pacotes necessários (`tikz`, `xcolor` com opção `HTML`). Coerente com o
espírito autocontido do R123 (decks MIRA sem dependência externa), a
arte da capa passa a ser vetorial e local, não um prompt para terceiros.

## Mudanças Entregues

1. **`publishing/cover_designer.py`**:
   - `_tikz_art(style_key, palette)`: corpo TikZ da arte de fundo
     (gradiente `\shade` entre primária/secundária + formas geométricas
     próprias de cada estilo — tecnologia: malha de nós; academico:
     colunas + arco; ficcao: silhueta dramática + raio; didatico: formas
     orgânicas), full-bleed via `remember picture, overlay`.
   - `_spine_mm(page_count)` + `_spine_tex(...)`: lombada vertical com
     título/autor rotacionados; largura = `page_count × MM_PER_PAGE`
     (0.0722 mm/página, estimativa offset 75g, documentada).
   - `_ficha_catalografica(...)`: bloco CIP brasileiro (autor, título,
     edição, ISBN, CDD) embutido na contracapa.
   - `_cover_preamble(...)`: fragmento `cover_preamble.tex` com os
     `\usepackage` necessários (`tikz` + libraries, `xcolor` com `HTML`).
   - `design_cover(...)` ganhou parâmetros **opcionais** `page_count`
     (default 200) e `isbn` (default ""), mantendo a assinatura
     retrocompatível (chamada posicional de `production.py` intacta).
     Passa a embutir a arte na capa, gerar `lombada.tex` e
     `cover_preamble.tex`, e incluir a ficha na contracapa. Retorno ganha
     `spine_mm`, `preamble_file`, `lombada_file` (chaves antigas
     preservadas).
   - `DESIGN_STUDY.md` ganhou a seção 5 explicando como incluir o
     preâmbulo (`\input{cover/cover_preamble}`).
2. **`tests/test_r124_cover_tikz.py` (novo)**: 8 testes TDD escritos
   antes da implementação.

## Verificação

- TDD: testes escritos antes → vermelho (8 failed) → verde (8 passed).
- Retrocompatibilidade: `tests/test_cover_designer.py` (SPEC-019)
  permanece 100% verde — contrato preservado.
- **Compilação real**: capa + preâmbulo + contracapa compilados com
  `pdflatex` num documento mínimo → `main.pdf` (54 KB) gerado com
  sucesso, provando que a arte TikZ, o gradiente e a ficha compilam de
  fato (não só balanceiam sintaticamente).
- `python3 -m pytest tests/ -q` completo.

## Lições

1. O quirk de `_determine_style` (SPEC-019) casa a substring `"ia"`
   dentro de palavras comuns (ex.: "histór**ia**" → classifica como
   *tecnologia*). Não corrigi aqui para não alterar o contrato SPEC-019
   sob teste; apenas evitei a armadilha nos dados de teste do R124.
   Fica como candidato a correção pontual em ciclo futuro (usar
   fronteiras de palavra em vez de `in`).
2. Gerar o `cover_preamble.tex` como fragmento separado (em vez de
   assumir que o preâmbulo do livro já traz `tikz`/`xcolor HTML`) tornou
   os fragmentos de capa autossuficientes e compiláveis isoladamente —
   o que permitiu a verificação de compilação real com `pdflatex`.

## Refino pós-aplicação (capas reais: OdontoIA e Molambudos)

Ao aplicar o R124 a dois livros reais do repositório — `livro-odontologia-ia`
(OdontoIA, tecnologia) e `projetos/molambudos` (romance de terror,
ficção) — e renderizar as capas com `pdflatex` (2 passadas), três
defeitos reais apareceram e foram corrigidos:

1. **Formas geométricas caíam fora da folha.** Com `remember picture,
   overlay`, coordenadas cruas em cm não têm origem na página. Envolvi as
   formas num `\begin{scope}[shift={(current page.south west)}]`, mapeando
   as coordenadas sobre a A4 (21×29,7 cm), e as espalhei por toda a capa.
   Só o gradiente aparecia antes; agora a malha de nós (tecnologia) e a
   silhueta (ficção) renderizam de fato.
2. **Título ilegível em capas escuras.** A tinta do texto usava
   `palette['bg']`, que na paleta de ficção é quase preto (`#121212`) —
   título escuro sobre fundo escuro. Novo `_ink_for(hex)` escolhe
   branco/preto pela luminância relativa da cor primária.
3. **Romance classificado como "tecnologia".** O quirk do `"ia"` como
   substring (adiado como lição na entrega inicial) casava dentro de
   "colônia"/"história". Corrigido de vez: `_determine_style` passou a
   usar correspondência por palavra inteira (`\b...\b`), com um teste de
   regressão dedicado. A lição virou correção.

Verificação do refino: `tests/test_r124_cover_tikz.py` (agora 9 testes,
+1 de regressão) e `tests/test_cover_designer.py` verdes; ambas as capas
recompiladas em PDF e inspecionadas visualmente (malha visível; título
legível; estilos corretos: OdontoIA→tecnologia, Molambudos→ficção).

## Score

**8.6/10**

- Fecha a lacuna real (capa era placeholder + prompt externo) com arte
  vetorial local compilável, verificada por compilação real de PDF, não
  só por balanceamento.
- Retrocompatível com o contrato SPEC-019 (todos os testes antigos
  verdes) e com a chamada posicional de `production.py`.
- Código de barras EAN-13 do ISBN e fontes tipográficas embarcadas
  ficaram explicitamente fora de escopo (a ficha traz o ISBN em texto e
  reserva o espaço) — extensões naturais para ciclo futuro.
