#!/usr/bin/env python3
"""SPEC-935-R209 — Gera CadernoMotor/main.tex (treino motor pontilhado).
Fontes: Mestra4 (pauta dupla pontilhada), Mestra2 (palavras pontilhadas).
Pedagógico: SEM conteúdo clínico/diagnóstico."""
import os

OUT = os.path.join(os.path.dirname(__file__), "main.tex")

PRE = r"""%% ============================================================
%% CADERNO MOTOR DE ESCRITA CURSIVA PONTILHADA (SPEC-935-R209)
%% Uso exclusivamente pedagogico: treino do gesto de escrita.
%% NAO contem avaliacao clinica; observacao do mediador e registro
%% pedagogico. Diagnostico e ato privativo de profissional habilitado.
%% ============================================================
\documentclass[a4paper,12pt]{book}
\RequirePackage[brazil]{babel}
\RequirePackage{fontspec}
\defaultfontfeatures{Path=../fontes/, Extension=.ttf}
\newfontfamily\papauta{Mestra4(DoblePautaPuntejada)}
\newfontfamily\papalavra{Mestra2(MeMimaPuntejada)}
\RequirePackage{geometry}
\RequirePackage{tikz}
\RequirePackage{titlesec}
\geometry{left=2cm, right=2cm, top=2cm, bottom=2cm}
\pagestyle{plain}

% pauta dupla (duas linhas + linha media tracejada) com modelo a esquerda
\newcommand{\pauta}[1]{%
\par\noindent
\begin{tikzpicture}[baseline=-0.25em]
  \useasboundingbox (0,0) rectangle (16.4,1.15);
  \draw (0,0) -- (16.4,0);
  \draw (0,1.15) -- (16.4,1.15);
  \draw[dotted] (0,0.575) -- (16.4,0.575);
  \node[anchor=west] at (0.1,0.575) {#1};
\end{tikzpicture}\par\vspace{0.55cm}
}

% bloco de 5 pautas: letra modelo pontilhada repetida + espaco de treino
\newcommand{\bloco}[1]{%
  \pauta{#1}
  \pauta{#1}
  \pauta{#1}
  \pauta{#1}
  \pauta{#1}
}

\begin{document}

\begin{titlepage}
\begin{center}
\vspace*{2cm}
{\Huge\bfseries Caderno Motor}\\[0.8cm]
{\Large Escrita Cursiva Pontilhada --- Treino do Gesto}\\[1.5cm]
{\large Alfabetizar Bem --- Metodo Hibrido Fonico-Kumon}\\[0.6cm]
{\large Uso pedagogico; nao diagnostica.}\\[2.5cm]
\noindent\rule{10cm}{0.6pt}\\[1cm]
{\normalsize Letras pontilhadas para contornar (pauta dupla) com base nas
fontes Mestra4 e Mestra2. O registro do mediador e pedagogico e destina-se
a planejar o apoio; em caso de sinais persistentes, encaminhar a profissional
habilitado (psicologo, fonoaudiologo, neurologista pediatrico).}
\end{center}
\end{titlepage}

\tableofcontents
\clearpage
\pagenumbering{arabic}
"""

POST = r"""
\end{document}
"""

def folha_letra(L, folha):
    out = [r"\clearpage" + "\n" + r"\section*{Letra " + L + "}\n" + r"\addcontentsline{toc}{section}{Letra " + L + "}\n",
           r"\noindent\textbf{Nome:} \underline{\hspace{4.5cm}}\quad "
           r"\textbf{Data:} \underline{\hspace{2.5cm}}\quad "
           r"\textbf{Folha:} " + folha + "\n\\vspace{0.4cm}\n",
           r"\begin{center}" + "\n",
           r"\papauta\fontsize{64}{64}\selectfont " + L + L.lower() + "\n",
           r"\end{center}" + "\n",
           r"\vspace{0.3cm}" + "\n",
           r"\bloco{\papauta\fontsize{30}{30}\selectfont " + L + L.lower() + "}" + "\n"]
    return "".join(out)

def folha_itens(titulo, itens, folha):
    """Folha com varias pautas, cada uma com um item pontilhado (Mestra2)."""
    out = [r"\clearpage" + "\n" + r"\section*{" + titulo + "}\n" + r"\addcontentsline{toc}{section}{" + titulo + "}\n",
           r"\noindent\textbf{Nome:} \underline{\hspace{4.5cm}}\quad "
           r"\textbf{Data:} \underline{\hspace{2.5cm}}\quad "
           r"\textbf{Folha:} " + folha + "\n\\vspace{0.5cm}\n"]
    for it in itens:
        out.append(r"\pauta{\papalavra\fontsize{28}{28}\selectfont " + it + "}\n")
    return "".join(out)

def letras():
    out = []
    for i, L in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1):
        out.append(folha_letra(L, f"{i:02d}"))
    return out

def ligacoes():
    """6 folhas com grupos de ligacoes (uma ligacao por pauta)."""
    grupos = [
        ("vogais: aa ee ii oo uu", ["aa", "ee", "ii", "oo", "uu"]),
        ("ba be bi bo bu", ["ba", "be", "bi", "bo", "bu"]),
        ("ca ce ci co cu", ["ca", "ce", "ci", "co", "cu"]),
        ("da de di do du", ["da", "de", "di", "do", "du"]),
        ("fa fe fi fo fu", ["fa", "fe", "fi", "fo", "fu"]),
        ("ma me mi mo mu", ["ma", "me", "mi", "mo", "mu"]),
    ]
    out = []
    for i, (tit, its) in enumerate(grupos, 1):
        out.append(folha_itens("Ligacoes: " + tit, its, f"{i:02d}L"))
    return out

def palavras():
    """6 folhas com palavras reais (uma por pauta), com acentos PT."""
    sets = [
        ["banana", "casa", "dado", "elefante", "foca", "gato"],
        ["janela", "lapis", "mala", "navio", "ovo", "pato"],
        ["queijo", "rato", "sapo", "tigre", "uva", "vaca"],
        ["bola", "chave", "dedo", "escada", "folha", "gente"],
        ["horta", "indio", "jacare", "limao", "macaco", "zebra"],
        ["tartaruga", "bicicleta", "coragem", "felicidade", "amizade", "sabedoria"],
    ]
    out = []
    for i, ws in enumerate(sets, 1):
        out.append(folha_itens(f"Palavras {i}", ws, f"{i:02d}P"))
    return out

body = PRE + "\n" + "".join(letras()) + "\n" + "".join(ligacoes()) + "\n" + "".join(palavras()) + "\n" + POST
with open(OUT, "w", encoding="utf-8") as f:
    f.write(body)
print("gerado:", OUT, "| letras:", 26, "| ligacoes:", 6, "| palavras:", 6)