# abntex2-imersivo — Modelo LaTeX imersivo/autodidático (híbrido ABNT)

Camada visual "sensorial" para livros científicos em **abntex2**, do leitor
nível 0 ao PhD. Mantém os elementos pré/pós-textuais em conformidade ABNT
(NBR 14724/6029/6023) e transforma o **miolo** numa experiência imersiva
estilo Tufte.

> Referência viva: `templates/projects/livro-odontologia-ia/` usa este modelo
> (capítulo 1 convertido; livro completo compila com 0 erros / 706 páginas).

## Requisitos

- **Engine:** XeLaTeX + Biber (nunca pdflatex).
- **Classe:** `abntex2` (baseada em memoir).
- **Pacotes TeX Live:** `tcolorbox`, `sidenotes`, `marginnote`, `fontawesome5`,
  `qrcode`, `lettrine`, `tikz`, `adjustbox` (todos no TeX Live padrão).
- **Fontes (fontspec):** Noto Serif, Inter, DejaVu Sans Mono, Liberation Serif.
  Se seu ambiente não as tiver, ajuste `design-fontes.tex`.

## Integração (2 formas)

### Forma A — carregar o kit (recomendada)
No preâmbulo, **depois** de `\documentclass{abntex2}` e do fontspec, **antes**
de `\begin{document}`:

```latex
\newcommand{\imersivocfg}{templates/abntex2-imersivo/}  % caminho até este kit
\input{\imersivocfg preamble-imersivo}
```

`preamble-imersivo.tex` carrega os pacotes, o patch de compatibilidade
`sidenotes`×`abntex2/memoir`, as cores base/nível (via `\providecolor`, sem
sobrescrever as suas) e os seis componentes.

### Forma B — copiar para o seu `config/`
Copie os `design-*.tex` para o `config/` do seu projeto e replique no seu
`pacotes.tex`/`preambulo.tex` os pacotes, o patch e as cores listados em
`preamble-imersivo.tex`. É como o projeto `livro-odontologia-ia` está montado
(loader em `config/design.tex`).

## O que cada componente entrega

| Arquivo | Conteúdo |
|---|---|
| `design-cores.tex` | Paleta semântica + `\cornivel{n}` / `\rotulonivel{n}` (mapa nível→cor/rótulo) |
| `design-fontes.tex` | Noto Serif (corpo) / Inter (títulos) / DejaVu Mono (código) / `\abntserif` (Liberation) + `\capitular{nível}{L}{resto}` (letra capitular colorida por nível) |
| `design-caixas.tex` | Caixas `objetivos`, `resumocap`, `atencao`, `dica`, `errocomum`, `pareepense`, `exercicio`, `analogia` + redefinição de `\spec`/`\teste`/`\testefalha`/`\destaque`/`pratica` |
| `design-margem.tex` | `\notalateral`, `\citdoi{chave}{doi}`, `\figmargem{arq}{leg}` + geometria de miolo estreito com coluna externa; troca fonte/geometria via hooks em `\pretextual`/`\textual`/`\postextual` |
| `design-aberturas.tex` | `\trilhanivel{0..5}`, `\aberturacap{...}` (6 args), `\aberturaparte{romano}{TÍTULO}{epígrafe}{faixa}` (página única) |
| `design-digital.tex` | `\colab{url}`, `\repo{url}`, `\dataset{url}{nome}` com QR code |

## Referência rápida de comandos

```latex
% Abertura de parte (no lugar de \part{...}):
\aberturaparte{I}{FUNDAMENTOS}{Epígrafe da parte.}{0 a 2 — iniciante a intermediário}

% Abertura de capítulo (logo após \chapter{...}):
\aberturacap
  {Epígrafe do capítulo.}{Autor}
  {0}{30 min}{Pré-requisitos}
  {\item Objetivo 1.\item Objetivo 2.}

% Letra capitular colorida pelo nível, no 1º parágrafo:
\capitular{0}{A}{história} da IA na odontologia começa...

% Notas na margem externa:
Texto.\notalateral{Comentário lateral.}
Texto.\citdoi{chave-bib}{10.xxxx/yyyy}

% Caixas pedagógicas:
\begin{dica}...\end{dica}   \begin{atencao}...\end{atencao}
\begin{exercicio}...\end{exercicio}   % etc.

% Digital:
\colab{https://colab.research.google.com/...}
```

## Notas importantes

- **Híbrido ABNT:** pré/pós-textuais ficam em Liberation Serif e margens ABNT
  (3/3/2/2 cm); o miolo troca para Noto Serif + coluna de notas na borda
  externa. As trocas são automáticas via hooks nos comandos `\pretextual`,
  `\textual` e `\postextual` do abntex2.
- **Retrocompatibilidade:** `\spec`/`\teste`/`\testefalha`/`\destaque` são
  **comandos** (`\destaque{...}`), e `pratica` é **ambiente**
  (`\begin{pratica}[título]...`). Não use `\begin{destaque}`/`\begin{spec}`.
- **`resumo` vs `resumocap`:** a caixa de síntese chama-se `resumocap` — o
  abntex2 já usa `resumo` para o resumo/abstract da obra.
- **Figuras largas:** o miolo é mais estreito que o padrão; TikZ/figuras
  desenhadas para largura cheia podem transbordar — envolva em
  `\resizebox{\linewidth}{!}{...}` (adjustbox já é carregado).
- **`\cornivel{n}`** aceita 0–5 (5 = PhD); valores fora da faixa caem em PhD.
