# Design — Modelo LaTeX imersivo e autodidático (híbrido ABNT)

**Data:** 2026-07-14
**Repo:** `livro-odontologia-ia` (livro "OdontoIA")
**Autor da obra:** Edson Laranjeiras
**Status:** aprovado para planejamento

## Objetivo

Reformular o modelo LaTeX do livro para uma experiência **sensorial, imersiva e
autodidática** — do leitor nível 0 (leigo) ao nível PhD — **sem perder a validade
acadêmica**. Solução **híbrida**: elementos pré/pós-textuais permanecem em
conformidade ABNT (NBR 14724/6029/6023/6027/6028); o miolo textual ganha uma
"camada sensorial" moderna.

## Decisões fechadas (brainstorming)

1. **Conformidade:** híbrido — ABNT nos pré/pós-textuais, liberdade no miolo.
2. **Recursos imersivos:** notas laterais (Tufte), caixas pedagógicas ricas,
   aberturas ilustradas, elementos digitais (QR/Colab). Todos os quatro.
3. **Escopo desta rodada:** **motor completo + 1 capítulo-demo**. Os outros 27
   capítulos continuam compilando via compatibilidade retroativa.
4. **Fonte do corpo do miolo:** Noto Serif (moderna). Pré/pós-textuais em
   Liberation Serif (clássica/ABNT).

## Abordagem

**Camada sensorial sobre o abntex2** (classe mantida; engine `xelatex` + `biber`).
Rejeitadas: migrar para `kaobook` (quebraria o scaffolding ABNT e os comandos dos
28 capítulos) e classe memoir custom do zero (esforço desproporcional).

Toolchain verificado presente: `xelatex`, `biber`, `latexmk`, e os pacotes
`tcolorbox`, `sidenotes`, `marginnote`, `fontawesome5`, `qrcode`, `tikz`,
`mdframed`. Fontes presentes: Noto Serif, Inter, DejaVu Sans Mono, DejaVu Math
TeX Gyre, Liberation Serif/Sans/Mono.

## Componentes

### 1. Layout e geometria
- **Pré/pós-textuais:** margens ABNT (esq 3, sup 3, dir 2, inf 2 cm), serifada
  clássica. Inalterados.
- **Miolo textual:** ao entrar em `\textual`, `\newgeometry` para bloco de texto
  ~10,5 cm + **coluna lateral externa ~4,2 cm** (`marginparsep` ~0,6 cm) para
  notas, citações DOI e figuras pequenas. `twoside` → coluna sempre na borda
  externa. `\restoregeometry` (ou geometria ABNT) reaplicada em `\postextual`.
- Notas laterais via `sidenotes` + `marginnote` (robustos no memoir; `marginnote`
  não depende do mecanismo de floats).

### 2. Tipografia e cor (`fontspec`, xelatex)
- Serifada de leitura (corpo do miolo): **Noto Serif**.
- Serifada clássica (pré/pós-textuais ABNT): **Liberation Serif**.
- Sans (títulos, caixas, notas, aberturas): **Inter**.
- Mono (código): **DejaVu Sans Mono**. Matemática: DejaVu Math TeX Gyre
  (`unicode-math`, com fallback para Latin Modern se indisponível).
- **Paleta semântica** unificada — uma cor por tipo de elemento; mantém as cores
  de nível existentes (verde nível 0 → roxo PhD).

### 3. Caixas pedagógicas (tcolorbox + fontawesome5)
Skin único, com ícone/cor/título por tipo. Novos ambientes:
`objetivos`, `resumo` (checklist), `atencao`, `dica`, `errocomum`, `pareepense`,
`exercicio`, `analogia`.
Reescritas no novo visual, **mantendo os nomes de comando atuais**:
`\spec` (SDD), `\teste`/`\testefalha` (TDD), `pratica`, `\destaque`.
→ Retrocompatibilidade: os 27 capítulos não convertidos compilam e já herdam o
visual novo.

### 4. Aberturas e trilha de nível
- **Abertura de PARTE:** número grande, título, epígrafe, arte de fundo opcional,
  lista de capítulos, faixa de nível.
- **Abertura de CAPÍTULO** (`\aberturacap{...}`): título, epígrafe, mini-mapa
  "Neste capítulo você vai…", **trilha de nível 0→PhD** (barra TikZ), tempo
  estimado de leitura, pré-requisitos.
- Comandos inline de nível (`\nivelzero`…`\nivelcinco`) preservados (refinados).

### 5. Elementos digitais
`\colab{url}`, `\dataset{url}{nome}`, `\repo{url}` → tcolorbox com **QR code**
(`qrcode`) + ícone + link clicável.

### 6. Arquitetura de arquivos
- **NOVO** `config/design.tex`: fontes, cores, caixas, notas laterais, aberturas,
  digital. Ponto único da camada sensorial.
- Editar `config/pacotes.tex`: adicionar tcolorbox, sidenotes, marginnote,
  fontawesome5, qrcode, unicode-math.
- Editar `config/preambulo.tex`: `\input{config/design}`; hooks de geometria em
  `\textual`/`\postextual`.
- Editar `config/comandos.tex`: aliases retrocompatíveis apontando ao novo estilo.
- **Demo:** converter `parte1-fundamentos/01-historia-ia-odontologia.tex`
  (backup do original em `.bak` ou via git) exercitando todos os recursos.

## Interfaces (comandos expostos)

| Comando / ambiente | Uso |
|---|---|
| `\notalateral{txt}` | nota na margem externa |
| `\figmargem{arq}{leg}` | figura pequena na margem |
| `\citdoi{chave}{doi}` | citação DOI na margem |
| `\aberturacap{título}{epígrafe}{nível}{tempo}{prereq}{objetivos}` | abre capítulo |
| `\begin{objetivos}…\end{objetivos}` etc. | caixas pedagógicas |
| `\colab{url}` / `\dataset{url}{nome}` / `\repo{url}` | elementos digitais |
| `\spec`,`\teste`,`\testefalha`,`\destaque`,`pratica` | legados (novo visual) |

## Compatibilidade e riscos

- **Risco central:** geometria memoir/abntex2 + `geometry` + notas laterais. Mitigação:
  usar `\newgeometry`/`\restoregeometry` só no bloco textual; testar compilação
  cedo e isoladamente antes de aplicar ao livro todo.
- **Retrocompatibilidade:** nenhum comando existente pode deixar de compilar. Os
  27 capítulos não tocados são o teste de regressão.
- **Fontes:** todas verificadas presentes; math com fallback Latin Modern.

## Critério de sucesso (verificação)

1. `main.pdf` compila com **zero erros** (xelatex → biber → xelatex × 2).
2. Pré/pós-textuais permanecem ABNT (folha de rosto, ficha, resumo, referências
   NBR 6023).
3. Miolo exibe coluna de notas laterais na borda externa.
4. Pelo menos uma abertura de parte e o capítulo-demo renderizam todas as caixas,
   a trilha de nível e um elemento digital (QR).
5. Nenhuma regressão de compilação nos 27 capítulos não convertidos.

## Fora de escopo (esta rodada)

- Converter o corpo dos 27 capítulos restantes (rodadas futuras, por etapas).
- Reescrever conteúdo científico dos capítulos.
- Arte/ilustrações finais de abertura (usar placeholders; arte real depois).
