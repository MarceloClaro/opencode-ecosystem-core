# Modelo LaTeX imersivo (híbrido ABNT) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar uma camada visual sensorial/autodidática sobre o abntex2 (notas laterais Tufte, caixas pedagógicas ricas, aberturas com trilha de nível 0→PhD, elementos digitais), mantendo pré/pós-textuais ABNT e a compilação dos 28 capítulos.

**Architecture:** Novo diretório de config modular (`config/design-*.tex`) carregado por `config/design.tex`, que por sua vez é incluído em `config/preambulo.tex` após `pacotes`/`comandos`. Comandos legados são redefinidos (`\renewcommand`) para o novo visual, garantindo retrocompatibilidade. Geometria e fonte do miolo trocam via hooks (`\apptocmd`) em `\textual`/`\pretextual`/`\postextual`.

**Tech Stack:** abntex2 (memoir), XeLaTeX + Biber, tcolorbox, sidenotes, marginnote, fontawesome5, qrcode, tikz. Fontes: Noto Serif (corpo), Inter (títulos/caixas), DejaVu Sans Mono (código), Liberation Serif (ABNT pré/pós).

## Global Constraints

- Engine de compilação: **XeLaTeX** (fontspec) + **Biber**. Nunca pdflatex.
- Todo comando/ambiente já usado nos capítulos deve continuar compilando (retrocompatibilidade): `\spec`, `\teste`, `\testefalha`, `\destaque`, `pratica`, `\citacaoativa`, `\artigofig`, `\notaexplicativa`, `\nivelzero`..`\nivelcinco`, `\codigo`, `\termo`, `\sigla`, `\indice`.
- Pré/pós-textuais permanecem ABNT: margens 3/3/2/2 cm, fonte Liberation Serif.
- Math permanece o padrão do XeLaTeX (Latin Modern) — **não** introduzir `unicode-math` (risco desnecessário).
- Caixas pedagógicas via `tcolorbox`; notas via `sidenotes`/`marginnote`.
- Verificação = compilar sem erros. Critério objetivo: `grep -c '^!' <arquivo>.log` retorna `0`.
- Commits escopados (pathspec explícito). Mensagem termina com a linha `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Diretório de trabalho: `/home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia`.

## File Structure

- Create `config/design.tex` — loader; dá `\input` nos sub-arquivos abaixo, em ordem.
- Create `config/design-cores.tex` — paleta semântica.
- Create `config/design-fontes.tex` — tipografia (Noto/Inter/DejaVu + família Liberation).
- Create `config/design-caixas.tex` — caixas tcolorbox novas + redefinição das legadas.
- Create `config/design-margem.tex` — geometria do miolo + notas laterais + hooks de fonte/geometria.
- Create `config/design-aberturas.tex` — trilha de nível, abertura de capítulo, abertura de parte.
- Create `config/design-digital.tex` — Colab/dataset/repo com QR code.
- Modify `config/pacotes.tex` — adicionar pacotes; remover as 3 linhas `\set*font{Liberation ...}` (fontes migram para design-fontes).
- Modify `config/preambulo.tex` — `\input{config/design}` após comandos.
- Modify `.gitignore` — ignorar harness `_smoke.*`.
- Create `_smoke.tex` — harness mínimo de compilação rápida (gitignored).
- Modify `parte1-fundamentos/01-historia-ia-odontologia.tex` — capítulo-demo (Task 7).
- Modify `main.tex` — Parte I passa a usar `\aberturaparte` (Task 7).

---

### Task 1: Fundação — pacotes, loader, cores e harness de fumaça

**Files:**
- Modify: `config/pacotes.tex`
- Create: `config/design.tex`
- Create: `config/design-cores.tex`
- Modify: `config/preambulo.tex`
- Modify: `.gitignore`
- Create: `_smoke.tex`

**Interfaces:**
- Consumes: nada.
- Produces: cores `corObjetivo, corResumo, corAtencao, corDica, corErro, corPensar, corExercicio, corAnalogia, corDigital, corMargem`; macros `\cornivel{n}` (nível 0–5 → nome de cor) e `\rotulonivel{n}` (nível → rótulo); arquivo loader `config/design.tex`; harness `_smoke.tex`.

- [ ] **Step 1: Adicionar pacotes em `config/pacotes.tex`**

Logo após a linha `\usepackage{mdframed}` (seção "Caixas destacadas"), inserir:

```latex
% --- Camada imersiva (modelo sensorial) ---
\usepackage[most]{tcolorbox}
\usepackage{sidenotes}   % requer/puxa marginnote
\usepackage{fontawesome5}
\usepackage{qrcode}
```

- [ ] **Step 2: Remover as fontes fixas de `config/pacotes.tex`**

Excluir estas três linhas (as fontes migram para `design-fontes.tex`):

```latex
\setmainfont{Liberation Serif}  % Metrically compatible with Times New Roman
\setsansfont{Liberation Sans}   % Metrically compatible with Arial
\setmonofont{Liberation Mono}   % Metrically compatible with Courier New
```

- [ ] **Step 3: Criar `config/design-cores.tex`**

```latex
%==============================================================================
% design-cores.tex — Paleta semântica do modelo imersivo
% (cores de nível corNivel* já definidas em config/pacotes.tex)
%==============================================================================
\definecolor{corObjetivo}{HTML}{1A5276}
\definecolor{corResumo}{HTML}{117A65}
\definecolor{corAtencao}{HTML}{B9770E}
\definecolor{corDica}{HTML}{1F8A70}
\definecolor{corErro}{HTML}{C0392B}
\definecolor{corPensar}{HTML}{6C3483}
\definecolor{corExercicio}{HTML}{2874A6}
\definecolor{corAnalogia}{HTML}{7D6608}
\definecolor{corDigital}{HTML}{0E6655}
\definecolor{corMargem}{HTML}{566573}

% Mapa nível(0..5) → nome de cor (usado pela trilha e pela letra capitular)
\newcommand{\cornivel}[1]{%
  \ifcase#1 corNivelFacil\or corNivelFacil\or corNivelMedio\or
  corNivelDificil\or corNivelAvancado\else corNivelPhD\fi}

% Mapa nível(0..5) → rótulo
\newcommand{\rotulonivel}[1]{%
  \ifcase#1 0\or 1\or 2\or 3\or 4\else PhD\fi}
```

- [ ] **Step 4: Criar `config/design.tex` (loader)**

```latex
%==============================================================================
% design.tex — Loader da camada imersiva/autodidática (híbrido ABNT)
% Carregado por config/preambulo.tex após metadados/pacotes/comandos.
%==============================================================================
\input{config/design-cores}
\input{config/design-fontes}
\input{config/design-caixas}
\input{config/design-margem}
\input{config/design-aberturas}
\input{config/design-digital}
```

Nota: os arquivos `design-fontes`, `design-caixas`, `design-margem`, `design-aberturas` e `design-digital` são criados nas tarefas seguintes. Para o smoke test desta tarefa compilar, comente temporariamente os `\input` ainda inexistentes (Step 6 usa apenas cores). Descomente cada um na sua respectiva tarefa.

Versão desta tarefa (só cores ativas):

```latex
%==============================================================================
% design.tex — Loader da camada imersiva/autodidática (híbrido ABNT)
%==============================================================================
\input{config/design-cores}
%\input{config/design-fontes}
%\input{config/design-caixas}
%\input{config/design-margem}
%\input{config/design-aberturas}
%\input{config/design-digital}
```

- [ ] **Step 5: Incluir o loader em `config/preambulo.tex`**

Após a linha `\input{config/comandos}` (e o comentário acima dela), inserir:

```latex
% Carrega a camada imersiva (modelo sensorial)
\input{config/design}
```

- [ ] **Step 6: Criar harness `_smoke.tex`**

```latex
% Harness de compilação rápida — NÃO versionado (ver .gitignore)
\documentclass[12pt,a4paper,twoside,openright,chapter=TITLE,section=TITLE]{abntex2}
\input{config/preambulo}
\begin{document}
\textual
\chapter{Fumaça}
Texto de corpo para checar a tipografia de leitura.
\textcolor{corObjetivo}{Cor corObjetivo OK.}
\textcolor{corErro}{Cor corErro OK.}
\end{document}
```

- [ ] **Step 7: Ignorar o harness em `.gitignore`**

Adicionar ao final de `.gitignore`:

```
# Harness de compilação (dev)
_smoke.*
```

- [ ] **Step 8: Compilar o smoke test**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
xelatex -interaction=nonstopmode -halt-on-error _smoke.tex >/dev/null 2>&1; echo "erros: $(grep -c '^!' _smoke.log)"
```
Expected: `erros: 0` e `_smoke.pdf` gerado.

- [ ] **Step 9: Commit**

```bash
git add config/pacotes.tex config/design.tex config/design-cores.tex config/preambulo.tex .gitignore
git commit -m "$(cat <<'EOF'
Modelo imersivo: fundação (pacotes, loader, paleta, harness)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Tipografia (Noto Serif / Inter / DejaVu Mono + Liberation ABNT)

**Files:**
- Create: `config/design-fontes.tex`
- Modify: `config/design.tex` (descomentar o `\input`)

**Interfaces:**
- Consumes: fontspec (carregado em pacotes.tex); `lettrine`; macro `\cornivel{n}` (Task 1).
- Produces: fonte principal Noto Serif; `\sffamily`=Inter; `\ttfamily`=DejaVu Sans Mono; família `\abntserif` (Liberation Serif) e `\tituloface` (Inter); comando `\capitular{nível}{Letra}{resto}` (letra capitular colorida por nível).

- [ ] **Step 1: Adicionar `lettrine` em `config/pacotes.tex`**

Na seção "Miscelânea" de `config/pacotes.tex`, adicionar:

```latex
\usepackage{lettrine}   % letra capitular (drop cap) por nível
```

- [ ] **Step 2: Criar `config/design-fontes.tex`**

```latex
%==============================================================================
% design-fontes.tex — Tipografia XeLaTeX (fontspec)
% Corpo de leitura moderno (Noto Serif). Pré/pós-textuais trocam para
% Liberation Serif via hooks em design-margem.tex.
%==============================================================================
\setmainfont{Noto Serif}[Ligatures=TeX]
\setsansfont{Inter}[Ligatures=TeX]
\setmonofont{DejaVu Sans Mono}[Scale=0.92]

% Famílias auxiliares
\newfontfamily\abntserif{Liberation Serif}[Ligatures=TeX] % ABNT pré/pós-textual
\newfontfamily\tituloface{Inter}[Ligatures=TeX]           % títulos/aberturas

%------------------------------------------------------------------
% Letra capitular (drop cap) colorida pelo nível do capítulo
% Uso: \capitular{nível 0-5}{primeira letra}{resto da 1ª palavra}
% A cor da capitular sinaliza o nível (verde=0 ... roxo=PhD).
%------------------------------------------------------------------
\newcommand{\capitular}[3]{%
  \lettrine[lines=3, findent=2pt, nindent=0pt]%
    {\tituloface\bfseries\textcolor{\cornivel{#1}}{#2}}{#3}}
```

- [ ] **Step 3: Ativar o `\input` em `config/design.tex`**

Trocar `%\input{config/design-fontes}` por `\input{config/design-fontes}`.

- [ ] **Step 4: Exercitar fonte + capitular no smoke test**

No `_smoke.tex`, logo após `\chapter{Fumaça}`, inserir (as duas capitulares devem sair com cores diferentes — nível 0 verde, PhD roxo):

```latex
\capitular{0}{A}{ inteligência} artificial começa aqui, no nível iniciante.
\par\medskip
\capitular{5}{O}{ estado} da arte, no nível PhD, é outra história.
```

- [ ] **Step 5: Compilar o smoke test**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
xelatex -interaction=nonstopmode -halt-on-error _smoke.tex >/dev/null 2>&1; echo "erros: $(grep -c '^!' _smoke.log)"
grep -i "Font .* not found\|cannot find font" _smoke.log || echo "fontes OK"
```
Expected: `erros: 0` e `fontes OK`. Abrir `_smoke.pdf`: duas capitulares grandes, a primeira verde (nível 0) e a segunda roxa (PhD).

- [ ] **Step 6: Commit**

```bash
git add config/pacotes.tex config/design-fontes.tex config/design.tex
git commit -m "$(cat <<'EOF'
Modelo imersivo: tipografia + letra capitular colorida por nível

Noto Serif/Inter/DejaVu + Liberation ABNT; \capitular{nível}{L}{resto}
usa a cor do nível (verde 0 → roxo PhD) na drop cap de abertura.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Caixas pedagógicas (tcolorbox) + retrocompatibilidade

**Files:**
- Create: `config/design-caixas.tex`
- Modify: `config/design.tex` (descomentar o `\input`)

**Interfaces:**
- Consumes: cores da Task 1; fontawesome5; tcolorbox.
- Produces: ambientes `objetivos`, `resumocap`, `atencao`, `dica`, `errocomum`, `pareepense`, `exercicio`, `analogia`; redefinições de `\spec{}`, `\teste{}`, `\testefalha{}`, `\destaque{}`, `pratica`.

> **NOTA (implementação R-imersivo):** o ambiente de resumo pedagógico chama-se `resumocap`, **não** `resumo` — o `abntex2.cls` já define `resumo` (ambiente do resumo/abstract pré-textual, usado em `prefacio/06-resumo.tex` e `07-abstract.tex`). Usar `resumo` para a caixa quebraria o abstract. Ícones ajustados à versão instalada do fontawesome5: Exercício usa `\faPencilRuler` (não `\faPencilAlt`) e SDD usa `\faFileContract` (não `\faFileAlt`).

- [ ] **Step 1: Criar `config/design-caixas.tex`**

```latex
%==============================================================================
% design-caixas.tex — Caixas pedagógicas (tcolorbox) + retrocompatibilidade
%==============================================================================
% Estilo base comum
\tcbset{
  caixapedag/.style={
    enhanced, breakable, arc=2pt, boxrule=0.6pt,
    left=8pt, right=8pt, top=6pt, bottom=6pt,
    fonttitle=\sffamily\bfseries\color{white},
    coltext=black
  }
}

% Fábrica: \novacaixa{ambiente}{cor}{ícone}{Título}
\newcommand{\novacaixa}[4]{%
  \newtcolorbox{#1}{caixapedag, colframe=#2, colback=#2!6,
    colbacktitle=#2, title={#3~#4}}%
}

\novacaixa{objetivos}{corObjetivo}{\faBullseye}{Objetivos de aprendizagem}
\novacaixa{resumo}{corResumo}{\faListUl}{Resumo \& checklist}
\novacaixa{atencao}{corAtencao}{\faExclamationTriangle}{Atenção}
\novacaixa{dica}{corDica}{\faLightbulb}{Dica}
\novacaixa{errocomum}{corErro}{\faBug}{Erro comum}
\novacaixa{pareepense}{corPensar}{\faQuestionCircle}{Pare e pense}
\novacaixa{exercicio}{corExercicio}{\faPencilAlt}{Exercício}
\novacaixa{analogia}{corAnalogia}{\faProjectDiagram}{Analogia}

%------------------------------------------------------------------
% Retrocompatibilidade: comandos legados no novo visual
%------------------------------------------------------------------
\renewcommand{\spec}[1]{%
  \begin{tcolorbox}[caixapedag, colframe=corPrimaria, colback=corPrimaria!6,
    colbacktitle=corPrimaria, title={\faFileAlt~SDD — Especificação}]%
  #1
  \end{tcolorbox}}

\renewcommand{\teste}[1]{%
  \begin{tcolorbox}[caixapedag, colframe=corTesteSucesso, colback=corTesteSucesso!6,
    colbacktitle=corTesteSucesso, title={\faCheckCircle~Teste TDD}]%
  #1
  \end{tcolorbox}}

\renewcommand{\testefalha}[1]{%
  \begin{tcolorbox}[caixapedag, colframe=corTesteFalha, colback=corTesteFalha!6,
    colbacktitle=corTesteFalha, title={\faTimesCircle~Teste TDD falhou}]%
  #1
  \end{tcolorbox}}

\renewcommand{\destaque}[1]{%
  \begin{tcolorbox}[caixapedag, colframe=corDestaque, colback=corDestaque!6,
    colbacktitle=corDestaque, title={\faStar~Destaque}]%
  #1
  \end{tcolorbox}}

\renewenvironment{pratica}[1][]{%
  \begin{tcolorbox}[caixapedag, colframe=corSecundaria, colback=corSecundaria!6,
    colbacktitle=corSecundaria, title={\faFlask~Prática: #1}]%
}{%
  \end{tcolorbox}}
```

- [ ] **Step 2: Ativar o `\input` em `config/design.tex`**

Trocar `%\input{config/design-caixas}` por `\input{config/design-caixas}`.

- [ ] **Step 3: Exercitar as caixas no smoke test**

Substituir o corpo de `_smoke.tex` (entre `\chapter{Fumaça}` e `\end{document}`) por:

```latex
\chapter{Fumaça}
\begin{objetivos}Compreender X e aplicar Y.\end{objetivos}
\begin{dica}Use um venv por projeto.\end{dica}
\begin{atencao}Não versione segredos.\end{atencao}
\begin{errocomum}Confundir treino com teste.\end{errocomum}
\begin{pareepense}Por que normalizar os dados?\end{pareepense}
\begin{exercicio}Implemente a função de acurácia.\end{exercicio}
\begin{analogia}Uma CNN é como um funil de detectores.\end{analogia}
\begin{resumo}Vimos X, Y e Z.\end{resumo}
\spec{O sistema deve prever cárie a partir de radiografia.}
\teste{\texttt{assert acc > 0.9}}
\testefalha{\texttt{ValueError}}
\destaque{IA não substitui o cirurgião-dentista.}
\begin{pratica}[Primeiro modelo]Carregue o dataset e treine.\end{pratica}
```

- [ ] **Step 4: Compilar o smoke test**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
xelatex -interaction=nonstopmode -halt-on-error _smoke.tex >/dev/null 2>&1; echo "erros: $(grep -c '^!' _smoke.log)"
```
Expected: `erros: 0`. Abrir `_smoke.pdf` e confirmar as 12 caixas com ícones e cores.

- [ ] **Step 5: Commit**

```bash
git add config/design-caixas.tex config/design.tex
git commit -m "$(cat <<'EOF'
Modelo imersivo: caixas pedagógicas tcolorbox + retrocompat dos legados

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Notas laterais (Tufte) + geometria do miolo + hooks

**Files:**
- Create: `config/design-margem.tex`
- Modify: `config/design.tex` (descomentar o `\input`)

**Interfaces:**
- Consumes: `sidenotes`, `marginnote`, `geometry` (já carregado); famílias `\abntserif` (Task 2); etoolbox (`\apptocmd`, já carregado); comandos abntex2 `\pretextual`, `\textual`, `\postextual`.
- Produces: `\notalateral{txt}`, `\citdoi{chave}{doi}`, `\figmargem{arquivo}{legenda}`; troca de geometria e fonte entre pré/textual/pós.

- [ ] **Step 1: Criar `config/design-margem.tex`**

```latex
%==============================================================================
% design-margem.tex — Geometria do miolo (Tufte) + notas laterais + hooks
%==============================================================================
% Geometria do miolo textual: bloco de texto + coluna externa para notas
\newcommand{\miologeometry}{%
  \newgeometry{a4paper, inner=3cm, outer=5.5cm, top=3cm, bottom=2cm,
    marginparwidth=4cm, marginparsep=0.5cm}%
}

% Hooks: pré/pós-textuais em Liberation Serif (ABNT); miolo em Noto Serif
% + geometria larga. (main font padrão já é Noto Serif — Task 2.)
\apptocmd{\pretextual}{\setmainfont{Liberation Serif}[Ligatures=TeX]}{}{}
\apptocmd{\textual}{\miologeometry\setmainfont{Noto Serif}[Ligatures=TeX]}{}{}
\apptocmd{\postextual}{\restoregeometry\setmainfont{Liberation Serif}[Ligatures=TeX]}{}{}

%------------------------------------------------------------------
% Comandos de margem
%------------------------------------------------------------------
% Nota lateral (texto marginal, sem numeração pesada)
\newcommand{\notalateral}[1]{%
  \marginnote{\sffamily\footnotesize\color{corMargem}#1}}

% Citação DOI na margem (usa biblatex; gera entrada na bibliografia)
\newcommand{\citdoi}[2]{%
  \sidenote{\footnotesize\textcite{#1}\par\url{https://doi.org/#2}}}

% Figura pequena na margem
\newcommand{\figmargem}[2]{%
  \marginnote{\centering
    \includegraphics[width=\marginparwidth]{#1}\par
    {\sffamily\scriptsize #2}}}
```

- [ ] **Step 2: Ativar o `\input` em `config/design.tex`**

Trocar `%\input{config/design-margem}` por `\input{config/design-margem}`.

- [ ] **Step 3: Exercitar notas laterais no smoke test**

No `_smoke.tex`, logo após `\chapter{Fumaça}`, inserir uma linha de texto com nota:

```latex
Texto principal do miolo.\notalateral{Esta é uma nota lateral na margem externa.}
Mais texto para empurrar o parágrafo e testar o fluxo ao lado da coluna de notas.
```

- [ ] **Step 4: Compilar o smoke test**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
xelatex -interaction=nonstopmode -halt-on-error _smoke.tex >/dev/null 2>&1; echo "erros: $(grep -c '^!' _smoke.log)"
grep -i "marginpar.*overflow\|Overfull \\\\hbox (more than 10" _smoke.log | head -3 || true
```
Expected: `erros: 0`. Abrir `_smoke.pdf`: a nota aparece na margem externa e o bloco de texto está mais estreito que a página.

- [ ] **Step 5: Commit**

```bash
git add config/design-margem.tex config/design.tex
git commit -m "$(cat <<'EOF'
Modelo imersivo: notas laterais Tufte + geometria do miolo + hooks ABNT

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Aberturas ilustradas + trilha de nível 0→PhD

**Files:**
- Create: `config/design-aberturas.tex`
- Modify: `config/design.tex` (descomentar o `\input`)

**Interfaces:**
- Consumes: tikz (carregado); cores de nível `corNivelFacil, corNivelMedio, corNivelDificil, corNivelAvancado, corNivelPhD` (pacotes.tex); macros `\cornivel{n}` e `\rotulonivel{n}` (Task 1); `\tituloface` (Task 2).
- Produces: `\trilhanivel{n}` (n=0..5); `\aberturacap{epígrafe}{autor}{nível}{tempo}{prereq}{objetivos}`; `\aberturaparte{romano}{TÍTULO}{epígrafe}{faixa}`.

- [ ] **Step 1: Criar `config/design-aberturas.tex`**

```latex
%==============================================================================
% design-aberturas.tex — Trilha de nível + aberturas de capítulo/parte
% (\cornivel e \rotulonivel vêm de config/design-cores.tex — Task 1)
%==============================================================================
% Trilha de nível: preenche pílulas de 0 até #1 (0..5)
\newcommand{\trilhanivel}[1]{%
  \begin{tikzpicture}[baseline=-0.6ex]
    \foreach \i in {0,...,5} {
      \pgfmathtruncatemacro{\ativo}{\i<=#1 ? 1 : 0}
      \edef\cor{\ifnum\ativo=1 \cornivel{\i}\else lightgray\fi}
      \node[draw=none, fill=\cor, rounded corners=3pt, minimum width=0.9cm,
            minimum height=0.5cm, font=\sffamily\bfseries\scriptsize\color{white}]
           at (\i*1.05,0) {\rotulonivel{\i}};
    }
  \end{tikzpicture}%
}

% Abertura de capítulo (após \chapter{...}):
% #1 epígrafe  #2 autor-epígrafe  #3 nível(0-5)  #4 tempo  #5 pré-requisitos
% #6 objetivos (conteúdo de itemize)
\newcommand{\aberturacap}[6]{%
  \begin{flushright}\itshape\small #1\par\upshape\textmd{--- #2}\end{flushright}
  \medskip
  \noindent\trilhanivel{#3}\hfill{\sffamily\small\faClock~#4}\par
  \smallskip
  {\sffamily\small\textbf{Pré-requisitos:} #5}\par
  \medskip
  \begin{objetivos}
    \begin{itemize}#6\end{itemize}
  \end{objetivos}
  \bigskip
}

% Abertura de parte (usar no lugar de \part{...}):
% #1 romano  #2 TÍTULO  #3 epígrafe  #4 faixa de níveis (texto)
\newcommand{\aberturaparte}[4]{%
  \part{#2}%
  \begin{center}
    {\tituloface\Huge\bfseries\textcolor{corPrimaria}{PARTE #1}}\par\bigskip
    {\itshape\large #3}\par\bigskip
    {\sffamily\small Faixa de nível: #4}
  \end{center}
  \vfill
}
```

- [ ] **Step 2: Ativar o `\input` em `config/design.tex`**

Trocar `%\input{config/design-aberturas}` por `\input{config/design-aberturas}`.

- [ ] **Step 3: Exercitar aberturas no smoke test**

No `_smoke.tex`, substituir a linha `\chapter{Fumaça}` por:

```latex
\chapter{Fumaça}
\aberturacap
  {A inteligência é a arte de resolver problemas.}
  {autor fictício}
  {0}{25 min}{Nenhum}
  {\item Entender o objetivo do capítulo.\item Rodar o primeiro exemplo.}
\noindent Nível PhD para teste: \trilhanivel{5}
```

- [ ] **Step 4: Compilar o smoke test**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
xelatex -interaction=nonstopmode -halt-on-error _smoke.tex >/dev/null 2>&1; echo "erros: $(grep -c '^!' _smoke.log)"
```
Expected: `erros: 0`. Abrir `_smoke.pdf`: epígrafe, trilha (nível 0 aceso), tempo, pré-requisitos e caixa de objetivos.

- [ ] **Step 5: Commit**

```bash
git add config/design-aberturas.tex config/design.tex
git commit -m "$(cat <<'EOF'
Modelo imersivo: aberturas de capítulo/parte + trilha de nível 0→PhD

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Elementos digitais (Colab / dataset / repo com QR)

**Files:**
- Create: `config/design-digital.tex`
- Modify: `config/design.tex` (descomentar o `\input`)

**Interfaces:**
- Consumes: `qrcode`, `fontawesome5`, tcolorbox; cor `corDigital`.
- Produces: `\colab{url}`, `\dataset{url}{nome}`, `\repo{url}`.

- [ ] **Step 1: Criar `config/design-digital.tex`**

```latex
%==============================================================================
% design-digital.tex — Ponte físico→digital (QR + links)
%==============================================================================
% Caixa digital genérica: \caixaqr{ícone}{título}{url}
\newcommand{\caixaqr}[3]{%
  \begin{tcolorbox}[enhanced, breakable, arc=2pt, boxrule=0.6pt,
    colframe=corDigital, colback=corDigital!6,
    left=8pt, right=8pt, top=6pt, bottom=6pt]
    \begin{minipage}[c]{2.4cm}\qrcode[height=2cm]{#3}\end{minipage}%
    \hfill
    \begin{minipage}[c]{\dimexpr\linewidth-2.9cm\relax}
      {\sffamily\bfseries\color{corDigital}#1~#2}\par\smallskip
      {\footnotesize\url{#3}}
    \end{minipage}
  \end{tcolorbox}}

\newcommand{\colab}[1]{\caixaqr{\faGoogle}{Abrir no Google Colab}{#1}}
\newcommand{\repo}[1]{\caixaqr{\faGithub}{Repositório no GitHub}{#1}}
\newcommand{\dataset}[2]{\caixaqr{\faDatabase}{Dataset: #2}{#1}}
```

- [ ] **Step 2: Ativar o `\input` em `config/design.tex`**

Trocar `%\input{config/design-digital}` por `\input{config/design-digital}`.

- [ ] **Step 3: Exercitar elementos digitais no smoke test**

No `_smoke.tex`, antes de `\end{document}`, inserir:

```latex
\colab{https://colab.research.google.com/}
\repo{https://github.com/MarceloClaro/odontoia}
\dataset{https://example.org/dataset}{Radiografias Panorâmicas}
```

- [ ] **Step 4: Compilar o smoke test**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
xelatex -interaction=nonstopmode -halt-on-error _smoke.tex >/dev/null 2>&1; echo "erros: $(grep -c '^!' _smoke.log)"
```
Expected: `erros: 0`. Abrir `_smoke.pdf`: três caixas com QR code + ícone + link.

- [ ] **Step 5: Commit**

```bash
git add config/design-digital.tex config/design.tex
git commit -m "$(cat <<'EOF'
Modelo imersivo: elementos digitais (Colab/dataset/repo com QR)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Capítulo-demo + verificação do livro completo

**Files:**
- Modify: `parte1-fundamentos/01-historia-ia-odontologia.tex`
- Modify: `main.tex`

**Interfaces:**
- Consumes: todos os comandos das Tasks 3–6.
- Produces: capítulo 1 convertido como referência viva; Parte I com `\aberturaparte`; `main.pdf` completo.

- [ ] **Step 1: Backup do capítulo original**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
cp parte1-fundamentos/01-historia-ia-odontologia.tex \
   parte1-fundamentos/01-historia-ia-odontologia.tex.orig
```

- [ ] **Step 2: Inserir abertura no capítulo-demo**

Abrir `parte1-fundamentos/01-historia-ia-odontologia.tex`. Logo após a linha `\chapter{...}` existente, inserir o bloco (ajustar epígrafe/tempo ao conteúdo real do capítulo):

```latex
\aberturacap
  {A melhor forma de prever o futuro é inventá-lo.}
  {Alan Kay}
  {0}{30 min}{Nenhum — capítulo introdutório}
  {\item Situar a IA na história da Odontologia.
   \item Reconhecer os marcos que levaram ao deep learning.
   \item Preparar-se para os fundamentos técnicos das próximas partes.}
```

- [ ] **Step 3: Letra capitular colorida no 1º parágrafo do capítulo**

No mesmo arquivo, no primeiro parágrafo do corpo (após a abertura), converter a primeira palavra para letra capitular no nível do capítulo (cap.1 = nível 0, verde). Exemplo — se o parágrafo começa com "A história...":

```latex
\capitular{0}{A}{ história} da inteligência artificial na Odontologia...
```
(Ajustar letra/resto à primeira palavra real do capítulo.)

- [ ] **Step 4: Converter 1–2 notas de rodapé e 1 citação para a margem**

No mesmo arquivo, escolher uma `\footnote{...}` de contexto e trocar por `\notalateral{...}`; escolher uma citação e adicionar `\citdoi{chave}{doi}` na margem (usando uma chave que já exista em `referencias/bibliografia.bib`). Inserir também, ao final da primeira seção prática (se houver), um elemento digital:

```latex
\colab{https://colab.research.google.com/github/MarceloClaro/odontoia/blob/main/notebooks/01_intro_colab.ipynb}
```

- [ ] **Step 5: Converter a Parte I para abertura ilustrada em `main.tex`**

Em `main.tex`, localizar:

```latex
\part{FUNDAMENTOS HISTÓRICOS E TECNOLÓGICOS}
\label{part:fundamentos}
```
e substituir por:

```latex
\aberturaparte{I}{FUNDAMENTOS HISTÓRICOS E TECNOLÓGICOS}
  {Toda tecnologia suficientemente avançada é indistinguível de magia.}
  {0 a 2 — iniciante a intermediário}
\label{part:fundamentos}
```

- [ ] **Step 6: Compilar o livro completo (com bibliografia)**

Run:
```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
latexmk -xelatex -interaction=nonstopmode main.tex >/dev/null 2>&1
echo "erros: $(grep -c '^!' main.log)"; echo "paginas: $(pdfinfo main.pdf 2>/dev/null | awk '/Pages/{print $2}')"
```
Expected: `erros: 0` e um número de páginas plausível (centenas). Se `latexmk` não resolver o biber, rodar manualmente: `xelatex main && biber main && xelatex main && xelatex main`.

- [ ] **Step 7: Inspeção visual (checklist da spec)**

Abrir `main.pdf` e confirmar:
- Folha de rosto / ficha catalográfica / resumo em Liberation Serif, margens ABNT.
- Abertura da Parte I estilizada.
- Capítulo 1 com abertura (trilha de nível), **letra capitular verde (nível 0)** no 1º parágrafo, nota lateral na margem, citação DOI na margem e caixa Colab (QR).
- Corpo do miolo em Noto Serif, bloco de texto estreito com coluna de notas.
- Referências (NBR 6023), glossário e índice presentes ao final.

- [ ] **Step 8: Regressão — nenhum capítulo não convertido quebrou**

A compilação completa do Step 6 já é o teste de regressão (inclui os 27 capítulos intactos). Confirmar que `grep -c '^!' main.log` = 0. Registrar contagem de warnings relevantes:
```bash
grep -c "Overfull \\\\hbox" main.log; echo "(overfull boxes — aceitável se poucas na coluna de notas)"
```

- [ ] **Step 9: Remover o backup e atualizar PROGRESS**

```bash
cd /home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia
rm -f parte1-fundamentos/01-historia-ia-odontologia.tex.orig
```
Se existir `PROGRESS.md` na raiz do repo do livro, anexar uma linha registrando a conclusão do motor imersivo + capítulo-demo. (Se não existir, pular.)

- [ ] **Step 10: Commit**

```bash
git add parte1-fundamentos/01-historia-ia-odontologia.tex main.tex
git commit -m "$(cat <<'EOF'
Modelo imersivo: capítulo-demo (cap.1) + abertura da Parte I

Aplica o motor sensorial no capítulo 1 como referência viva: abertura com
trilha de nível, nota lateral, citação DOI na margem e caixa Colab (QR).
Parte I passa a usar \aberturaparte. Livro completo compila sem erros.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**1. Cobertura da spec:**
- Layout Tufte / geometria do miolo → Task 4 ✓
- Tipografia (Noto/Inter/DejaVu/Liberation) → Task 2 ✓
- Letra capitular colorida por nível (`\capitular`) → Task 2 (def) + Task 7 (uso) ✓
- Caixas pedagógicas ricas + retrocompat → Task 3 ✓
- Aberturas + trilha de nível → Task 5 ✓
- Elementos digitais (QR) → Task 6 ✓
- Arquitetura modular `config/design*.tex` → Tasks 1–6 ✓
- Capítulo-demo + retrocompat dos 27 → Task 7 ✓
- Critérios de sucesso (compila 0 erros, ABNT pré/pós, notas laterais, abertura, QR) → Task 7 Steps 5–7 ✓

**2. Placeholders:** conteúdo de epígrafe/tempo/pré-requisitos do demo é marcado como "ajustar ao conteúdo real" — é decisão editorial legítima na conversão, não um placeholder de plano. Sem TBD/TODO estruturais.

**3. Consistência de tipos/nomes:** `\aberturacap` (6 args), `\aberturaparte` (4 args), `\trilhanivel` (1 arg), `\notalateral`/`\citdoi`/`\figmargem`, `\colab`/`\repo`/`\dataset`, ambientes de caixa — nomes idênticos entre definição (Tasks 3–6) e uso (Task 7). Cores `corNivel*` vêm de pacotes.tex; `cor*` semânticas de design-cores.tex (Task 1). Consistente.

## Notas de risco (para o executor)

- **Geometria memoir + geometry:** se `\newgeometry`/`\restoregeometry` conflitar com o memoir/abntex2, alternativa é usar `\setlrmarginsandblock` + `\setmarginnotes` + `\checkandfixthelayout` no hook do `\textual`. Testar cedo (Task 4).
- **`\setmainfont` mid-document:** suportado pelo fontspec no XeLaTeX; se causar aviso, aceitável. Se falhar, definir `\newfontfamily\corpofont{Noto Serif}` e aplicar via `\AtBeginDocument`/escopo do textual.
- **Colisão de `\part` em `\aberturaparte`:** usa o `\part` real internamente; o texto extra vem depois. Se o memoir abrir página nova entre eles, mover o bloco `center` para antes ou usar `\part*`.
