#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
expandir_volume.py — Espec R220 (SPEC-935-R220 — EXPANSÃO VOLUMES 2–5)

Gera o pacote completo de cada volume (parte1..parte7 + referencias +
checkpoints + main.tex) no padrão do Volume 1 (648 pp): método híbrido
fônico-kumon, técnica da boquinha, planchetas reproduzíveis e rastreio
integrado entre unidades (SPEC-935-R211).

Uso:
    python3 expandir_volume.py 2          # gera o Volume 2
    python3 expandir_volume.py 2 3 4 5    # gera todos
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
from dados_volumes import PERFIS  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers LaTeX comuns
# ---------------------------------------------------------------------------
def esc(t: str) -> str:
    return t


def plancheta(titulo: str) -> str:
    return (
        "\\plancheta{" + titulo + "}\n"
    )


def exercicio(titulo: str) -> str:
    return f"\\begin{{exercicio}}[{titulo}]\n"


def moldura_folha(nome=None, data=True, nota="/10"):
    s = "\\noindent\\textbf{Nome:} \\underline{\\hspace{3.2cm}}"
    if data:
        s += " \\quad \\textbf{Data:} \\underline{\\hspace{1.6cm}}"
    if nome:
        s += f" \\quad \\textbf{{Motor:}} {nome}"
    s += f" \\quad \\textbf{{Nota:}} \\underline{{\\hspace{{0.9cm}}}}{nota}\n\n"
    return s


def sil_tabela(pares):
    r"""Tabela centralizada de \sil{...}{...} (máx 5 colunas por linha).

    Aceita pares ("CH","A") -> \\sil{CH}{A} ou strings "ZA" -> \\textbf{ZA}.
    """
    cel = []
    for item in pares:
        if isinstance(item, str):
            cel.append(f"\\textbf{{{item}}}")
        else:
            ce1, ce2 = item
            cel.append(f"\\sil{{{ce1}}}{{{ce2}}}")
    linhas = []
    for i in range(0, len(cel), 5):
        chunk = cel[i:i + 5]
        linhas.append("  " + " & ".join(chunk) + " \\\\")
    return (
        "\\begin{center}\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{" + "c" * min(5, len(cel)) + "}\n"
        + "\n".join(linhas) + "\n"
        "  \\end{tabular}}\n"
        "\\end{center}\n"
    )


def sublinhar_palavras(palavras, marcadas):
    r"""Gera lista com \uline nas palavras-alvo marcadas."""
    itens = []
    for p in palavras:
        itens.append("\\uline{" + p + "}" if p in marcadas else p)
    return "\\begin{center}\n  " + " \\quad ".join(itens) + "\n\\end{center}\n"


def linhas_underline(n):
    return " \\quad ".join("\\underline{\\hspace{2.6cm}}" for _ in range(n))


def fechar_enumerate_resume(item):
    pass


# ---------------------------------------------------------------------------
# Templates das partes
# ---------------------------------------------------------------------------
def gerar_parte1(p: dict) -> str:
    ano = p["ano"]
    cap = [
        (f"O Método Híbrido Fônico-Kumon no {ano}º Ano",
         f"No {ano}º ano, o método híbrido fônico-kumon avança da decodificação para a "
         "regulação ortográfica e a fluência. O treino diário e repetitivo (espírito "
         "Kumon) organiza o automatismo; a técnica fônica garante a correspondência "
         "grafema-fonema; a Técnica da Boquinha ancora a articulação correta de cada "
         "som. O professor conduz a sequência didática granular, e os pontos de "
         "rastreio integrado (SPEC-935-R211) entre unidades orientam a observação "
         "pedagógica sem diagnosticar."),
        (f"A Técnica da Boquinha no {ano}º Ano",
         f"No {ano}º ano, a Boquinha deixa de ser apenas visual e passa a ser "
         "metalinguística: o aluno articula, sente a posição dos articuladores, "
         "compara pares mínimos (R/L, S/Z, X/CH) e corrige a própria fala com "
         "apoio do espelho. Cada unidade traz a descrição articulatória dos sons "
         "trabalhados (foco, modo, vozeamento)."),
        ("Alinhamento Curricular: BNCC e Matrizes Externas",
         "Este volume alinha-se às habilidades de Língua Portuguesa da BNCC para o "
         f"{ano}º ano ({p['bncc']}) e prepara o aluno para as matrizes de referência "
         "do SPAECE e dos itens CAEd (leitura, localização de informação, gêneros "
         "textuais, análise linguística e produção)."),
        ("Níveis Internos de Progressão (K0–K5)",
         "A progressão interna organiza o avanço do escolar: da consolidação da "
         "base alfabética à fluência segmental, à ortografia regulada por regras e "
         "à fluência composicional. O aluno circula por rotas 1A–1D conforme o "
         "resultado dos checkpoints, sem rótulos nem diagnóstico."),
        ("Rotas Individualizadas de Aprendizagem (1A–1D)",
         "Rotas 1A (consolidação), 1B (avanço), 1C (desafio) e 1D (enriquecimento) "
         "orientam a diferenciação: escolha de planchetas, sequência de atividades "
         "de sons e ritmo das folhas Kumon, sempre a partir de evidências do "
         "Registro de Progresso."),
        ("Design Neuroinclusivo: Tipografia, Contraste e Ritmo",
         "Fonte cursiva escolar treinável, margens calmas, caixas amigáveis, "
         "instruções curtas e apoio visual. O design reduz sobrecarga cognitiva e "
         "favorece alunos com TDAH, dislexia e transtornos de linguagem, sem "
         "substituir a avaliação especializada."),
        ("Avaliação Formativa: Registro, Rastreio e Encaminhamento",
         "Três camadas: (a) registro de progresso diário; (b) checkpoints de "
         "rastreio entre unidades (autoavaliação do aluno e observação do "
         "professor, S/F/R/N); (c) avaliações diagnósticas do volume. Sinais "
         "persistentes são discutidos com a família e avaliados pelo profissional "
         "habilitado (Volume Profissional de Sondagem e Rastreio)."),
        ("Preparação para SPAECE, CAEd e Avaliações Externas",
         "Itens-modelo no formato das matrizes externas, treino de comando "
         "('Circule', 'Assinale', 'Localize') e de tempo de tarefa, com leitura "
         "mediada em sala e avaliações simuladas ao fim de cada trimestre."),
        (f"Sequência Didática Granular: Lógica Kumon no {ano}º Ano",
         f"Cada unidade fragmenta o objetivo em etapas microsequenciadas: "
         f"5 sessões por semana, 10 a 15 minutos por dia. A gradação é a alma do "
         "método: nenhum aluno avança sem consolidar a etapa anterior; o rastreio "
         "integrado garante a observação sistemática entre as etapas."),
        ("Ciência da Leitura Aplicada ao 2º Ano",
         f"No {ano}º ano, a ciência da leitura (Dehaene, Salles, Capovilla) orienta a "
         "prática: leitura por decodificação automatizada, vocabulário, compreensão "
         "e fluência. O treino Kumon automatiza a via fonológica; a leitura "
         "compartilhada alimenta a compreensão; a escrita diária consolida a "
         "ortografia. O professor conhece a razão de cada etapa."),
        ("Fonologia do Português Brasileiro em Sala",
         f"No {ano}º ano, o professor domina o mapa fonológico do PB: dígrafos "
         "(CH, LH, NH, RR, SS, QU, GU), encontros consonantais, nasalidade "
         "(AM/AN, ÃO, ÃE, ÕE) e polissemia do X. A Técnica da Boquinha traduz "
         "esse mapa em gestos articulatórios observáveis, e as listas de sons "
         "da Parte VII organizam o treino por fonema."),
        ("Planejamento Anual do 2º Ano",
         f"O planejamento anual distribui as {len(p['unidades'])} unidades pelos "
         "quatro bimestres, intercala as folhas Kumon, prevê as avaliações "
         "diagnóstica, formativa e somativa e agenda os checkpoints de rastreio. "
"O quadro de planejamento consta do Guia do Professor (Parte V); cada "
          "bimestre encerra com uma avaliação e uma reunião de pais."),
        ("Avaliação Formativa no Ciclo de Alfabetização",
         "A avaliação formativa acompanha o processo: observa a leitura em voz "
         "alta, o ditado da semana, a escrita espontânea e a folha Kumon do dia. "
         "O registro do professor (S/F/R/N) alimenta o Registro de Progresso e "
         "a reunião de pais. A avaliação somativa do fim do bimestre usa as "
         "atividades da Parte IV e o gabarito; a avaliação diagnóstica inicial "
         "e a triagem de risco usam as fichas do Volume Profissional. Nenhuma "
         "nota é usada para classificar: a nota é devolvida ao aluno em forma "
         "de meta de fluência e de escrita."),
        ("O Papel do Erro na Aprendizagem da Escrita",
         "O erro ortográfico revela a hipótese da criança sobre a escrita. "
         "Trocar P por B ou omitir o M antes de P não é 'falta de atenção': é "
         "uma regularidade a trabalhar com a Boquinha, a grade silábica e o "
         "ditado da semana. O erro deve ser corrigido com devolutiva imediata "
         "e repetição da mesma folha, nunca com punição. O professor que entende "
         "o padrão do erro planeja a próxima unidade com precisão; por isso "
         "cada checkpoint registra o padrão, não o aluno."),
    ]
    out = []
    out.append("%% FUNDAMENTAÇÃO — Volume %d (gerado por expandir_volume.py)\n" % ano)
    for i, (titulo, texto) in enumerate(cap, start=1):
        out.append(f"\\chapter{{{titulo}}}\n")
        for par in _paragrafos(texto, 4):
            out.append(par + "\n\n")
        out.append("\\begin{dica}\n"
                   f"**Sugestão de trabalho:** leia o capítulo na reunião de "
                   f"planejamento do {ano}º ano e adapte as rotas 1A–1D à turma.\n"
                   "\\end{dica}\n")
    return "\n".join(out)


def _paragrafos(texto, n=4):
    """Divide texto em ~n parágrafos mantendo ordem."""
    import re
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    if len(frases) <= n:
        return [" ".join(frases)]
    size = len(frases) // n + 1
    return [" ".join(frases[i:i + size]) for i in range(0, len(frases), size)]


def gerar_parte2(p: dict) -> str:
    out = ["%% SEQUÊNCIA DIDÁTICA — Volume %d (gerado por expandir_volume.py)\n" % p["ano"]]
    for u in p["unidades"]:
        out.append(_unidade_latex(p, u))
    out.append("%% FIM DA PARTE II\n")
    return "\n".join(out)


def _grade_silabas(grafia):
    """Grade 5x5 de sílabas para a grafia-alvo (ex.: CH+A..U). Retorna '' se composta."""
    g = grafia.upper().split("/")[0].strip()
    if g in {"CH", "LH", "NH", "QU", "GU", "BR", "CR", "DR", "FR", "GR", "PR",
             "TR", "VR", "BL", "CL", "FL", "GL", "PL", "TL", "RR", "SS", "Ç",
             "X", "AM", "AN", "S", "Z"}:
        return sil_tabela([(g, v) for v in "AEIOU"])
    return ""


def _completa(w, grafia):
    """Deixa '___xxx' removendo a grafia inicial, ou 'xx__' removendo o final."""
    g = grafia.upper().split("/")[0].strip()
    uw = w.upper()
    if uw.startswith(g) and len(g) >= 2 and len(w) > len(g):
        return "\\underline{~~~}" + w[len(g):]
    return w[: max(1, len(w) - 1)] + "\\underline{~}"


def _unidade_latex(p, u):
    n = u["n"]
    ano = p["ano"]
    out = []
    titulo = u["titulo"]
    out.append(f"%% ============================================\n%% UNIDADE {n} -- {titulo}\n%% ============================================\n")
    out.append(f"\\chapter{{Unidade {n} --- {titulo}}}\n")
    out.append(f"\\metadata{{I-{n:02d}}}{{{u['nivel']}}}{{{u['bncc']}}}{{D1}}{{{u['bncc']}}}{{Resolucao CNE/CEB 7/2010, art. 12}}\n")
    out.append(f"\\textbf{{Regra:}} {u['regra']}\n")
    if u.get("geradora"):
        out.append(f"\\textbf{{Palavra geradora do bloco:}} \\textbf{{{u['geradora']}}} --- {u['geradora_expl']}\n")

    # Lição 1
    out.append(f"\\section{{Lição {n}.1 --- {u['foco']}}}\n")
    out.append(f"\\textbf{{Foco da lição:}} {u['foco']}\n\n")
    out.append("\\begin{boquinha}[Boquinha da Técnica]\n" + u["boquinha"] + "\n\\end{boquinha}\n")
    if u.get("entradas"):
        out.append("\\noindent\\textbf{Formação guiada:}\n")
        out.append(sil_tabela(u["entradas"]))

    # Palavras e frases padrão
    out.append("\\noindent\\textbf{Palavras da unidade:} " + ", ".join(u["palavras"]) + ".\n")
    out.append("\\noindent\\textbf{Frases para leitura oral:}\n\\begin{itemize}[leftmargin=1.6em]\n" +
               "".join("  \\item " + f + "\n" for f in u["frases"]) + "\\end{itemize}\n")

    # Lição 2 — Leitura (texto curto com palavras-alvo)
    out.append(f"\\section{{Lição {n}.2 --- Leitura do texto curto}}\n")
    out.append("\\noindent\\textbf{Leia o texto em voz alta, com atenção às palavras da unidade:}\n\n")
    fr = u["frases"][:4]
    par1 = " ".join(fr[:2])
    par2 = " ".join(fr[2:])
    out.append("\\begin{quote}\n" + par1 + "\n\n" + par2 + "\n\\end{quote}\n")
    out.append("\\textbf{Depois de ler, responda por escrito:}\n\\begin{enumerate}\n")
    out.append("  \\item O que acontece no texto que você leu?\n  \\begin{center}\n  \\underline{\\hspace{12cm}}\n  \\end{center}\n")
    out.append("  \\item Quantas frases o texto tem?\n  \\begin{center}\n  \\underline{\\hspace{12cm}}\n  \\end{center}\n")
    out.append("  \\item Circule no texto as palavras com a grafia " + u["grafia"] + ".\n")
    out.append("  \\item Leia o texto de novo em voz alta, agora sem ajuda.\n")
    out.append("\\end{enumerate}\n")

    # Lição 3 — Escrita
    out.append(f"\\section{{Lição {n}.3 --- Escrita com a grafia {u['grafia']}}}\n")
    out.append("\\noindent\\textbf{Regra da unidade:} " + u["regra"] + "\n\n")
    out.append("\\noindent\\textbf{Ditado guiado:} o professor dita as palavras abaixo; o aluno escreve e depois corrige com o professor.\n")
    out.append("\\begin{center}\n  " + " \\quad ".join("\\underline{\\hspace{2.3cm}}" for _ in range(4)) + "\n\n  " +
               " \\quad ".join("\\underline{\\hspace{2.3cm}}" for _ in range(4)) + "\n\\end{center}\n")
    out.append("\\noindent\\textbf{Complete as palavras com a grafia " + u["grafia"] + ":}\n\\begin{center}\n  " +
               " \\quad ".join(_completa(w, u["grafia"]) for w in u["palavras"][:5]) + "\n\\end{center}\n")
    out.append("\\noindent\\textbf{Escreva a palavra que o professor mostrar (banco de palavras) e separe em sílabas:}\n")
    out.append("\\begin{center}\n  " + " \\quad ".join("\\underline{\\hspace{2cm}} $=$ \\underline{\\hspace{2cm}}" for _ in range(3)) + "\n  \\end{center}\n")

    # Plancheta 1 — Reconhecimento/Produção
    out.append(f"%% PLANCHETA {n}.1\n")
    out.append(plancheta(f"Folha de Prática {n}.1 --- {titulo} (Parte 1)"))
    out.append(exercicio(f"Folha de Prática {n}.1 --- {titulo} (Parte 1)"))
    out.append(moldura_folha())
    out.append("\\subsection*{PARTE 1: RECONHECIMENTO}\n\n\\begin{enumerate}\n")
    if u.get("entradas"):
        out.append("  \\item Forme as sílabas com os sons da unidade:\n")
        out.append(sil_tabela(u["entradas"]))
        grd = _grade_silabas(u.get("grafia", ""))
        if grd:
            out.append("  \\item Complete a tabela de sílabas da unidade:\n")
            out.append(grd)
    out.append("  \\item Sublinhe as palavras da unidade:\n")
    out.append(sublinhar_palavras(u["palavras_misturadas"], u["palavras"][:6]))
    out.append("  \\item Identifique o som-alvo em cada palavra:\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $\\rightarrow$ som-alvo: \\underline{{\\hspace{{1cm}}}}" for w in u["palavras"][:3]) +
               "\n  \\end{center}\n")
    out.append("  \\item Separe em sílabas:\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{1cm}}}}" for w in u["palavras"][:3]) +
               "\n  \\end{center}\n")
    out.append("  \\item Conte as sílabas:\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{0.9cm}}}}" for w in u["palavras"][:3]) +
               "\n  \\end{center}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\subsection*{PARTE 2: PRODUÇÃO GUIADA}\n\n\\begin{enumerate}[resume]\n")
    out.append("  \\item Complete com a grafia da unidade:\n  \\begin{center}\n  " +
               " \\quad ".join(u["grafia"] + "\\underline{~~~}" for _ in range(5)) + "\n  \\end{center}\n")
    out.append("  \\item Escreva 3 palavras com o som-alvo:\n  \\begin{center}\n  1. \\underline{\\hspace{3cm}} \\quad 2. \\underline{\\hspace{3cm}} \\quad 3. \\underline{\\hspace{3cm}}\n  \\end{center}\n")
    out.append("  \\item Copie as palavras:\n  \\begin{center}\n  " + " \\quad ".join(u["palavras"][:5]) + "\n  \\end{center}\n")
    out.append("  \\item Separe em sílabas:\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} = \\underline{{\\hspace{{1cm}}}} \\underline{{\\hspace{{1cm}}}}" for w in u["palavras"][:3]) + "\n  \\end{center}\n")
    out.append("  \\item Escreva 2 frases usando palavras da unidade:\n  \\begin{enumerate}[label=\\alph*)]\n    \\item \\underline{\\hspace{8cm}}\n    \\item \\underline{\\hspace{8cm}}\n  \\end{enumerate}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\end{exercicio}\n")

    # Plancheta 2 — Integração
    out.append(f"%% PLANCHETA {n}.2\n")
    out.append(plancheta(f"Folha de Prática {n}.2 --- {titulo} (Parte 2)"))
    out.append(exercicio(f"Folha de Prática {n}.2 --- {titulo} (Parte 2)"))
    out.append(moldura_folha())
    out.append("\\subsection*{PARTE 3: INTEGRAÇÃO}\n\n\\begin{enumerate}[resume]\n")
    out.append("  \\item Leia as palavras em voz alta:\n  \\begin{center}\n  $\\rightarrow$ " +
               " ~ ".join(u["palavras"][:6]) + "\n  \\end{center}\n")
    out.append("  \\item Leia as frases em voz alta:\n  \\begin{center}\n" +
               "".join("  $\\rightarrow$ " + f + "\\\\\n" for f in u["frases"][:4]) + "  \\end{center}\n")
    out.append("  \\item Circule a opção correta:\n  \\begin{enumerate}[label=(\\alph*)]\n")
    out.append("    \\item O som da unidade é: ( ) oral ( ) nasal " + ("( ) vibrante" if "R" in u["grafia"] or "RR" in u["grafia"] else "") + "\n")
    out.append("    \\item A primeira sílaba de " + u["palavras"][0].upper() + " é: ( ) " +
               u["sila1"] + " ( ) " + u["sila2"] + "\n")
    out.append("    \\item As palavras da unidade aparecem: ( ) no início ( ) no meio ( ) no fim das palavras\n")
    out.append("  \\end{enumerate}\n")
    out.append("  \\item Leia e complete:\n  \\begin{center}\n  " + " \\quad ".join(
        w[:3] + "\\underline{~~~}" for w in u["palavras"][:4]) + "\n  \\end{center}\n")
    out.append("  \\item Leitura em voz alta com o professor:\n  \\begin{center}\n  " +
               " \\quad ".join(u["palavras"][:8]) + "\n  \\end{center}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\end{exercicio}\n")

    # Plancheta 3 — Produção livre (quando definida)
    if u.get("producao"):
        out.append(f"%% PLANCHETA {n}.3\n")
        out.append(plancheta(f"Folha de Prática {n}.3 --- Produção com {u['grafia']}"))
        out.append(exercicio(f"Folha de Prática {n}.3 --- Produção com {u['grafia']}"))
        out.append(moldura_folha(nota="/15"))
        out.append("\\noindent\\textbf{Comando:} " + u["producao"] + "\n\n")
        out.append("\\begin{enumerate}\n")
        out.append("  \\item Planeje: escolha 3 palavras da unidade para usar:\n  \\begin{center}\n  1. \\underline{\\hspace{3cm}} \\quad 2. \\underline{\\hspace{3cm}} \\quad 3. \\underline{\\hspace{3cm}}\n  \\end{center}\n")
        out.append("  \\item Escreva o texto (mínimo 3 frases):\n  \\begin{center}\n  \\underline{\\hspace{12cm}}\\\\\\underline{\\hspace{12cm}}\\\\\\underline{\\hspace{12cm}}\\\\\\underline{\\hspace{12cm}}\\\\\\underline{\\hspace{12cm}}\n  \\end{center}\n")
        out.append("  \\item Releia e corrija: marque palavras com a grafia " + u["grafia"] + " que você usou.\n")
        out.append("  \\item Ilustre o texto:\n  \\begin{center}\n  \\begin{tikzpicture}\n    \\draw[thick, dashed] (0,0) rectangle (12,6);\n  \\end{tikzpicture}\n  \\end{center}\n")
        out.append("\\end{enumerate}\n")
        out.append("\\end{exercicio}\n")

    # Plancheta 4 — Ditado e avaliação da unidade
    out.append(f"%% PLANCHETA {n}.4\n")
    out.append(plancheta(f"Folha de Prática {n}.4 --- Ditado e Avaliação da Unidade {n}"))
    out.append(exercicio(f"Folha de Prática {n}.4 --- Ditado e Avaliação da Unidade {n}"))
    out.append(moldura_folha(nota="/20"))
    out.append("\\subsection*{PARTE 1: DITADO (10 itens)}\n\n"
               "O professor dita as palavras e frases abaixo; o aluno escreve com letra cursiva.\n")
    dt = list(u["palavras"][:4]) + list(u["frases"][:2])
    out.append("\\begin{enumerate}\n")
    for i, _d in enumerate(dt, start=1):
        out.append(f"  \\item \\underline{{\\hspace{{10.5cm}}}}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\subsection*{PARTE 2: AUTOAVALIAÇÃO DO ALUNO}\n\n\\begin{enumerate}[label=\\alph*)]\n")
    for it in ["Eu li as palavras da unidade sem ajuda.",
               "Eu escrevi o ditado com as grafias certas.",
               "Eu separei as palavras em sílabas.",
               "Eu sei explicar a regra com as minhas palavras."]:
        out.append("  \\item " + it + "  \\quad ( ) Sim   ( ) Não\n")
    out.append("\\end{enumerate}\n")
    out.append("\\subsection*{PARTE 3: REGISTRO DO PROFESSOR (S/F/R/N)}\n")
    out.append("\\begin{center}\n\\renewcommand{\\arraystretch}{1.4}\n"
               "\\begin{tabular}{@{}p{9cm}cccc@{}}\n\\toprule\n"
               "Aspecto observado & S & F & R & N \\\\\n\\midrule\n"
               "Lê com precisão as palavras-alvo & & & & \\\\\n"
               "Escreve com ortografia estável & & & & \\\\\n"
               "Generaliza a regra em escrita espontânea & & & & \\\\\n"
               "Mantém atenção durante o ditado & & & & \\\\\n"
               "\\bottomrule\\end{tabular}\\end{center}\n")
    out.append("\\end{exercicio}\n")

    # Plancheta 5 — Leitura e fluência (a cada 3 unidades, calibração ~648 pp)
    if n % 3 == 0:
        out.append(f"%% PLANCHETA {n}.5\n")
        out.append(plancheta(f"Folha de Prática {n}.5 --- Leitura e Fluência da Unidade {n}"))
        out.append(exercicio(f"Folha de Prática {n}.5 --- Leitura e Fluência da Unidade {n}"))
        out.append(moldura_folha(nota="/10"))
        out.append("\\subsection*{PARTE 1: LEITURA EM VOZ ALTA}\n\n"
                   "Leia o texto abaixo três vezes; a cada leitura, marque um círculo no cronômetro do professor.\n")
        out.append("\\begin{quote}\n" + " ".join(fr[:2]) + "\n\n" + " ".join(fr[2:]) + "\n\\end{quote}\n")
        out.append("\\begin{center}\n"
                   "1ª leitura: \\underline{\\hspace{1.5cm}} \\quad 2ª leitura: \\underline{\\hspace{1.5cm}} \\quad 3ª leitura: \\underline{\\hspace{1.5cm}}\n"
                   "\\end{center}\n")
        out.append("\\subsection*{PARTE 2: COMPREENSÃO}\n\n\\begin{enumerate}\n")
        out.append("  \\item Quem são os personagens do texto?\n  \\begin{center}\n  \\underline{\\hspace{12cm}}\n  \\end{center}\n")
        out.append("  \\item Qual é a grafia-alvo que mais aparece no texto? Escreva três exemplos:\n  \\begin{center}\n  \\underline{\\hspace{3.5cm}} \\quad \\underline{\\hspace{3.5cm}} \\quad \\underline{\\hspace{3.5cm}}\n  \\end{center}\n")
        out.append("  \\item Você gostou do texto? Por quê?\n  \\begin{center}\n  \\underline{\\hspace{12cm}}\n  \\end{center}\n")
        out.append("\\end{enumerate}\n")
        out.append("\\subsection*{PARTE 3: DESENHO}\n\nDesenhe uma cena do texto:\n")
        out.append("\\begin{center}\n\\begin{tikzpicture}\n  \\draw[thick, dashed] (0,0) rectangle (12,5);\n\\end{tikzpicture}\n\\end{center}\n")
        out.append("\\end{exercicio}\n")

    out.append("\\begin{dica}\n**Dica para o Professor:** " + u["dica"] + "\n\\end{dica}\n")
    return "\n".join(out)


def gerar_parte3(p: dict) -> str:
    out = ["%% FOLHAS KUMON — Volume %d (gerado por expandir_volume.py)\n" % p["ano"]]
    out.append("\\chapter{Exercícios Kumon --- Folhas de Prática}\n")
    out.append(f"\\textbf{{Instrução:}} no {p['ano']}º ano, cada folha (plancheta reproduzível) dura "
               "10–15 min, com correção imediata e repetição da mesma folha quando o "
               "erro aparecer. O ritmo Kumon: poucas folhas por dia, mas todos os dias.\n")
    for f in p["kumon"]:
        out.append(_folha_kumon(p, f))
    # Tabela geral
    out.append("\\chapter{Tabela de Correlação das Folhas Kumon}\n")
    out.append("\\begin{center}\\renewcommand{\\arraystretch}{1.5}\n"
               "\\begin{tabular}{lll}\n\\toprule\n**Folha** & **Objetivo** & **Habilidade BNCC** \\\\\n\\midrule\n")
    for f in p["kumon"]:
        out.append(f"{f['id']} & {f['titulo']} & {f['bncc']} \\\\\n")
    out.append("\\bottomrule\n\\end{tabular}\\end{center}\n")
    return "\n".join(out)


def _folha_kumon(p, f):
    out = []
    out.append(f"%% FOLHA {f['id']}: {f['titulo'].upper()}\n")
    out.append(plancheta(f"Folha {f['id']} --- {f['titulo']}"))
    out.append(f"\\subsection{{Folha {f['id']} --- {f['titulo']}}}")
    out.append(exercicio(f"Folha de Prática {f['id']} --- {f['titulo']}"))
    out.append(f"\\metadata{{{f['id']}}}{{{f['nivel']}}}{{{f['bncc']}}}{{D1}}{{{f['bncc']}}}{{CNE/CEB nº 2/2012}}\n")
    out.append("\\kumontiming{3}{90}\n")
    out.append(moldura_folha(nota="/15"))
    out.append("\\subsection*{PARTE 1: RECONHECIMENTO (5 itens)}\n\n\\begin{enumerate}\n")
    out.append(f"  \\item \\textbf{{Ler palavras com {f['alvo']} em voz alta:}}\n  \\begin{{center}}\n  $\\rightarrow$ " +
               " ~ ".join(w.upper() for w in f["palavras"][:6]) + "\n  \\end{center}\n")
    out.append(f"  \\item \\textbf{{Sublinhar palavras que têm {f['alvo']}:}}\n")
    out.append(sublinhar_palavras(f["palavras"][:7], f["palavras"][:4]))
    out.append(f"  \\item \\textbf{{Identificar a grafia {f['alvo']} nas palavras:}}\n  \\begin{{center}}\n  " +
               " \\quad ".join(f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{1cm}}}}" for w in f["palavras"][:3]) + "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Separar em sílabas:}\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{1.2cm}}}}" for w in f["palavras"][:3]) + "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Contar sílabas:}\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{0.9cm}}}}" for w in f["palavras"][:3]) + "\n  \\end{center}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\subsection*{PARTE 2: PRODUÇÃO GUIADA (5 itens)}\n\n\\begin{enumerate}[resume]\n")
    out.append(f"  \\item \\textbf{{Completar com {f['grafia']}:}}\n  \\begin{{center}}\n  " +
               " \\quad ".join(f[:3] + "\\underline{~~~}" for f in f["palavras"][:5]) + "\n  \\end{center}\n")
    out.append(f"  \\item \\textbf{{Escrever 3 palavras com {f['alvo']}:}}\n  \\begin{{center}}\n  1. \\underline{{\\hspace{{3cm}}}} \\quad 2. \\underline{{\\hspace{{3cm}}}} \\quad 3. \\underline{{\\hspace{{3cm}}}}\n  \\end{{center}}\n")
    out.append("  \\item \\textbf{Copiar:}\n  \\begin{center}\n  " + " \\quad ".join(f["palavras"][:5]) + "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Separar em sílabas:}\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} = \\underline{{\\hspace{{1cm}}}} \\underline{{\\hspace{{1cm}}}}" for w in f["palavras"][:3]) + "\n  \\end{center}\n")
    out.append(f"  \\item \\textbf{{Escrever uma frase com {f['alvo']}:}}\n  \\begin{{center}}\n  \\underline{{\\hspace{{12cm}}}}\n  \\end{{center}}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\subsection*{PARTE 3: INTEGRAÇÃO (5 itens)}\n\n\\begin{enumerate}[resume]\n")
    out.append(f"  \\item \\textbf{{Ler frases em voz alta:}}\n  \\begin{{center}}\n" +
               "".join("  $\\rightarrow$ " + f2 + "\\\\\n" for f2 in f["frases"][:3]) + "  \\end{center}\n")
    out.append("  \\item \\textbf{Ler e desenhar:}\n  \\begin{center}\n  $\\rightarrow$ " + f["frases"][0] + "\n  \\end{center}\n  \\begin{center}\n  \\begin{tikzpicture}\n    \\draw[thick, dashed] (0,0) rectangle (6,3);\n  \\end{tikzpicture}\n  \\end{center}\n")
    out.append(f"  \\item \\textbf{{Completar:}}\n  \\begin{{center}}\n  " + " \\quad ".join(w[:3] + "\\underline{~~~}" for w in f["palavras"][:4]) + "\n  \\end{center}\n")
    out.append(f"  \\item \\textbf{{Escrever uma frase usando duas palavras com {f['alvo']}:}}\n  \\begin{{center}}\n  \\underline{{\\hspace{{12cm}}}}\n  \\end{{center}}\n")
    out.append(f"  \\item \\textbf{{Avaliação:}} $\\square$ Identifica {f['alvo']} \\quad $\\square$ Lê palavras com {f['alvo']}")
    out.append("  \\begin{center}\n  $\\square$ Escreve frases com o som-alvo \\quad $\\square$ Ortografia estável\n  \\end{center}\n")
    grd = _grade_silabas(f["grafia"])
    if grd:
        out.append("  \\item \\textbf{Complete a tabela de sílabas do som-alvo:}\n")
        out.append(grd)
    else:
        out.append("  \\item \\textbf{Leia as palavras da folha em voz alta e escreva quantas sílabas cada uma tem:}\n")
        out.append("  \\begin{center}\n  " + " \\quad ".join(
            f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{1cm}}}}" for w in f["palavras"][:4]) + "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Separe em sílabas e escreva o número de sílabas:}\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $=$ \\underline{{\\hspace{{1.2cm}}}} $\\rightarrow$ \\underline{{\\hspace{{0.8cm}}}} sílabas" for w in f["palavras"][:3]) + "\n  \\end{center}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\end{exercicio}\n")
    return "\n".join(out)


def gerar_parte4(p: dict) -> str:
    ano = p["ano"]
    out = ["%% AVALIAÇÕES — Volume %d (gerado por expandir_volume.py)\n" % ano]
    out.append("\\chapter{Avaliações Diagnósticas}\n")
    out.append(f"\\textbf{{Sobre as avaliações:}} no {ano}º ano, aplicam-se três avaliações: "
               "diagnóstica (início do ano), formativa (meio) e somativa (fim). Cada "
               "avaliação tem itens no formato das matrizes externas (CAEd/SPAECE) e "
               "gabarito comentado. As avaliações medem o desenvolvimento, não "
               "rotulam o aluno.\n")
    for av in p["avaliacoes"]:
        out.append(_avaliacao_latex(p, av))
    out.append("\\chapter{Gabaritos e Matriz de Correção}\n")
    for av in p["avaliacoes"]:
        out.append(f"\\section{{Gabarito --- {av['titulo']}}}\n")
        out.append("\\begin{center}\n\\renewcommand{\\arraystretch}{1.5}\n"
                   "\\begin{tabular}{lll}\n\\toprule\n**Item** & **Resposta** & **Justificativa** \\\\\n\\midrule\n")
        for it in av["gabarito"]:
            out.append(f"{it[0]} & {it[1]} & {it[2]} \\\\\n")
        out.append("\\bottomrule\n\\end{tabular}\n\\end{center}\n")
    return "\n".join(out)


def _avaliacao_latex(p, av):
    out = []
    out.append(f"\\section{{{av['titulo']}}}\n")
    out.append("\\begin{avaliacao}\n" + av["criterios"] + "\n\\end{avaliacao}\n")
    out.append("\\noindent\\textbf{Nome:} \\underline{\\hspace{4cm}} \\quad \\textbf{Data:} \\underline{\\hspace{2cm}}\n")
    for i, q in enumerate(av["questoes"], start=1):
        out.append(f"\\subsection*{{Questão {i}}}")
        out.append(q.replace("_", r"\_") + "\n")
        out.append("\\begin{center}\n  \\underline{\\hspace{12cm}}\n\\end{center}\n")
    out.append("\\clearpage\n")
    return "\n".join(out)


def gerar_parte5(p: dict) -> str:
    ano = p["ano"]
    caps = [
        ("Organização do Tempo de Ensino",
         f"No {ano}º ano, a rotina diária (10–15 min de fônico, 10–15 min de Kumon, "
         "30 min de leitura e escrita) estrutura o tempo. O quadro de horários "
         "distribui as unidades da sequência didática e as folhas Kumon por semana, "
         "respeitando o ritmo da turma."),
        ("Materiais Necessários",
         "Materiais: livro do aluno, folhas Kumon, espelho pequeno, cartazes da "
         "Boquinha, fichas de palavras, caderno de pauta dupla, cronômetro e o "
         "Registro de Progresso. Cada aluno mantém uma pasta de folhas para "
         "revisão quinzenal."),
        ("Estratégias de Diferenciação",
         "Usar as rotas 1A–1D: alunos que consolidaram avançam; alunos com "
         "dificuldade repetem folhas e recebem apoio da Boquinha e do espelho. "
         "A diferenciação é por evidência (Registro de Progresso), nunca por "
         "adivinhação."),
        ("Registro de Progresso",
         "O Registro é o coração do método: cada folha corrigida entra no registro "
         "com data, acertos e erros; os checkpoints alimentam o quadro S/F/R/N. "
         "Revisão quinzenal orienta as rotas."),
        ("Atividades Complementares",
         "Jogos com fichas de palavras, ditados interativos, caça-palavras e "
         "produção coletiva de textos. Atividades complementares reforçam o som-alvo "
         "sem virar lição de casa mecânica."),
        ("Orientações para Famílias",
         "Pauta da reunião de pais: o que é o método, como ajudar em casa "
         "(5–10 min/dia de leitura compartilhada e ditado de palavras das unidades), "
         "como funciona o rastreio escolar (não é diagnóstico) e quando buscar "
         "avaliação profissional."),
        ("Alinhamento com as Diretrizes Curriculares Nacionais (DCNC)",
         f"As DCNC e a BNCC orientam a progressão do {ano}º ano: leitura e produção "
         "de gêneros do cotidiano, análise linguística e consciência fonológica "
         "avançada. O livro converge com o que a rede já ensina, sem sobreposição."),
        ("Rotas Individualizadas e Neuroinclusão na Prática",
         "Estudos de caso: aluno com dislexia na família (rota 1A + repetição de "
         "planchetas), aluno com TDAH (pausas curtas, apoio visual, checklist de "
         "passos), aluno com altas habilidades (rota 1D, produção ampliada)."),
        ("O Papel do Professor no Rastreio Escolar",
         "O professor observa, registra e encaminha. NUNCA diagnostica. Os "
         "checkpoints de rastreio (SPEC-935-R211) e o guia de triagem ajudam a "
         "organizar a observação; o Volume Profissional de Sondagem e Rastreio é "
         "instrumento do profissional habilitado."),
        ("Avaliação da Própria Prática",
         "Autoavaliação docente mensal: os alunos avançaram nas rotas? Quais folhas "
         "geraram erros repetidos? As reuniões pedagógicas usam o Registro de "
         "Progresso como evidência para ajustar o planejamento."),
        ("Planejamento por Bimestre",
         f"O {ano}º ano se organiza em quatro bimestres. O primeiro bimestre "
         "consolida a base do ano anterior e apresenta os dígrafos CH, LH e NH; o "
         "segundo trabalha QU/GU e os encontros consonantais; o terceiro foca as "
         "regras ortográficas RR, SS, S/Z e Ç; o quarto encerra com AM/AN, X, "
         "revisões e leitura expressiva de gêneros. Cada bimestre encerra com uma "
         "avaliação e um checkpoint de rastreio."),
        ("Exemplos de Aula Passo a Passo",
         "Aula de 45 minutos do dígrafo CH: (1) aquecimento com a Boquinha e o "
         "espelho (5 min); (2) formação guiada das sílabas CHA–CHU com o quadro e "
         "as fichas (10 min); (3) leitura das palavras da unidade com apoio "
         "(10 min); (4) folha de prática 1, itens de reconhecimento (10 min); "
         "(5) fechamento com a autoavaliação oral (5 min). A lição de casa: "
         "reler o texto curto da unidade com um adulto."),
        ("Projetos de Leitura e Biblioteca",
         "O projeto 'Minha Primeira Coleção' leva cada aluno a escolher 5 livros "
         "no ano, registrar o título e o autor no seu caderno de leitor e apresentar "
         "um resumo oral por trimestre. A biblioteca vira ambiente de fluência: "
         "leitura em voz alta em duplas, gravação de recitação e sarau de poesia "
         "no fim do ano. O rastreio observa, sem diagnosticar, quem ainda precisa "
         "de apoio para ler com ritmo e expressividade."),
        ("Avaliando a Fluência na Rotina",
         "A fluência se mede pela precisão, ritmo e expressividade, não pela "
         "velocidade. Na rotina, use leituras de 1 minuto em textos conhecidos e "
         "desconhecidos; registre as palavras lidas corretamente; compare com a "
         "linha de base do início do ano. A meta do 2º ano é ler textos curtos "
         "com ritmo e entonação, com compreensão."),
        ("Jogos com Sílabas e Palavras",
         "Jogos de baixo custo: dominó de sílabas (CHA-CHE-CHI), bingo de "
         "palavras-chave, corrida de leitura em duplas, caça-palavras das grafias "
         "e baralho de encontros consonantais. Cada jogo termina com registro "
         "escrito no caderno: a brincadeira sempre converte em escrita."),
        ("Adaptações para Alunos com Suspeita de Dislexia, TDAH e TDL",
         "Para suspeita de dislexia: mais repetição nas folhas, leitura em voz "
         "alta com apoio, fontes maiores e tempo extra. Para TDAH: instruções "
         "curtas, checklist de passos e pausas programadas. Para transtorno de "
         "linguagem: apoio da Boquinha diário, frases curtas no ditado e "
"repetição com espelho. São adaptações pedagógicas; o diagnóstico é "
          "sempre do profissional habilitado."),
        ("Integração com o Volume Profissional e o Caderno Motor",
         "O Volume Profissional traz a triagem inicial e as fichas de "
         "observação que identificam o aluno em risco; este volume aplica as "
         "rotas 1A–1D e as folhas Kumon; o Caderno Motor desenvolve a "
         "motricidade fina que antecede a letra cursiva. A sequência "
         "recomendada no ano: triagem no início, checkpoints a cada três "
         "unidades e reavaliação no fim de cada bimestre, sempre com a "
         "integralidade do programa, nunca de forma isolada."),
        ("Rotina para Crianças com Atraso na Fala",
         "Quando a fala está em atraso, a consciência fonológica trava: a "
         "criança não diferencia sons que ela mesma não articula. A rotina "
         "recomendada: trabalho diário com a Boquinha no espelho, associação "
         "gesto-som de cada grafia nova, repetição das sílabas da unidade em "
         "voz alta e leitura em eco (o professor lê, a criança repete). "
         "A família deve ser orientada a estimular a fala em casa, e o "
         "professor deve sinalizar à coordenação quando a fala estiver "
         "comprometendo a aprendizagem, para encaminhamento pelo profissional "
         "habilitado."),
    ]
    out = ["%% GUIA DO PROFESSOR — Volume %d (gerado por expandir_volume.py)\n" % ano]
    for titulo, texto in caps:
        out.append(f"\\chapter{{{titulo}}}\n")
        for par in _paragrafos(texto, 3):
            out.append(par + "\n\n")
    return "\n".join(out)


def gerar_parte6(p: dict) -> str:
    ano = p["ano"]
    dom = [
        ("Leitura e Fluência", "Observar precisão, ritmo e prosódia na leitura oral de frases e textos curtos do volume."),
        ("Escrita e Ortografia", "Observar correspondência grafema-fonema, ortografia das grafias-alvo do ano e legibilidade do traçado."),
        ("Consciência Fonológica", "Observar segmentação, aliteração, rima e manipulação de fonemas em palavras com as grafias do ano."),
        ("Linguagem Oral", "Observar vocabulário, narrativa oral, compreensão e articulação na fala espontânea."),
        ("Atenção e Funções Executivas", "Observar manutenção de foco, planejamento da tarefa, inibição e memória de trabalho nas folhas."),
        ("Motricidade Fina e Traçado", "Observar preensão do lápis, pressão, direção e planejamento motor na escrita cursiva."),
        ("Comportamento e Interação", "Observar regulação emocional, cooperação e resposta à frustração nas atividades coletivas."),
    ]
    out = ["%% GUIA DE TRIAGEM — Volume %d (gerado por expandir_volume.py)\n" % ano]
    out.append("\\chapter{Guia de Observação e Encaminhamento}\n")
    out.append(f"**Este guia é de uso pedagógico.** No {ano}º ano, o professor observa "
               "os domínios abaixo ao longo das unidades e registra no Registro de "
               "Progresso. Sinais persistentes (2+ checkpoints com R/N no mesmo "
               "domínio) são discutidos com a família e avaliados pelo profissional "
               "habilitado com o Volume Profissional de Sondagem e Rastreio.\n")
    for nome, desc in dom:
        out.append(f"\\section{{Domínio: {nome}}}\n{desc}\n")
        out.append("\\begin{center}\n\\renewcommand{\\arraystretch}{1.4}\n"
                   "\\begin{tabular}{@{}p{9cm}cccc@{}}\n\\toprule\n"
                   "Indicador observável & S & F & R & N \\\\\n\\midrule\n")
        for ind in p["triagem"].get(nome, [p["triagem"].get("padrao", ["Apresenta o comportamento esperado"])]):
            out.append(f"{ind} & & & & \\\\\n")
        out.append("\\bottomrule\\end{tabular}\\end{center}\n")
    out.append("\\section{Fluxo de Encaminhamento}\n")
    out.append("1) Registrar no Registro de Progresso. 2) Conversar com a família "
                "(nunca dar diagnóstico). 3) Encaminhar ao profissional habilitado "
                "para aplicação das fichas do Volume Profissional. 4) Acompanhar e "
                "manter as rotas diferenciadas em sala.\n")
    out.append("\\section{Modelo de Registro Individual do Aluno}\n")
    out.append("O registro individual acompanha cada aluno ao longo do ano. "
               "Preencha quinzenalmente, anexando as folhas Kumon e os checkpoints.\n")
    out.append("\\begin{center}\n\\renewcommand{\\arraystretch}{1.5}\n"
               "\\begin{tabular}{@{}p{3cm}p{3cm}p{5cm}p{3cm}@{}}\n\\toprule\n"
               "Período & Foco observado & Observação registrada & Encaminhamento \\\\\n\\midrule\n"
               "1º bim. & & & \\\\\n"
               "2º bim. & & & \\\\\n"
               "3º bim. & & & \\\\\n"
               "4º bim. & & & \\\\\n"
               "\\bottomrule\\end{tabular}\\end{center}\n")
    out.append("\\section{Roteiro de Reunião com a Família}\n")
    out.append("1) Acolher e explicar o método (o que o aluno já conquistou). "
               "2) Mostrar o Registro de Progresso e as folhas feitas. "
               "3) Explicar o que é rastreio escolar: observação pedagógica, nunca "
               "diagnóstico. 4) Indicar o profissional habilitado somente se sinais "
               "persistentes aparecerem. 5) Combinar rotina diária de 10 minutos de "
               "leitura compartilhada em casa. 6) Registrar os combinados por escrito.\n")
    return "\n".join(out)


def gerar_parte7(p: dict) -> str:
    ano = p["ano"]
    out = ["%% ATIVIDADES DE SONS — Volume %d (gerado por expandir_volume.py)\n" % ano]
    out.append("\\chapter{Atividades de Cada Som}\n")
    out.append(f"No {ano}º ano, cada atividade trabalha um som-alvo com foco em "
               "consciência fonológica, articulação (Boquinha) e grafia. Cada "
               "atividade é uma plancheta reproduzível de página inteira; guarde as "
               "planchetas feitas: elas mostram o progresso.\n")
    for a in p["sons"]:
        out.append(_atividade_som_latex(p, a))
    return "\n".join(out)


def _atividade_som_latex(p, a):
    ano = p["ano"]
    out = []
    titulo = f"Atividade de Som {a['id']} --- {a['titulo']}"
    out.append(f"%% ATIVIDADE {a['id']}: {a['titulo'].upper()}\n")
    out.append(plancheta(titulo))
    out.append(f"\\subsection{{{titulo}}}")
    out.append(exercicio(f"Atividade de Som {a['id']} --- {a['titulo']}"))
    out.append("\\metadata{" + f"Som{a['id']:02d}" + "}{Silábico-Alfabético}{EF02LP01, EF02LP04}{D1}"
               + "{EF02LP04}{CNE/CEB nº 2/2012}\n")
    out.append("\\kumontiming{2}{90}\n")
    out.append(moldura_folha(nota="/10"))
    out.append("\\noindent\\textbf{Comando:} " + a["texto"].replace("_", r"\_") + "\n\n")
    out.append("\\begin{center}\n\\begin{tikzpicture}\n  \\draw[thick, dashed] (0,0) rectangle (12,6);\n\\end{tikzpicture}\n\\end{center}\n")
    out.append("\\noindent\\textbf{Escreva 2 palavras com o som da atividade:}\n")
    out.append("\\begin{center}\n  \\underline{\\hspace{3cm}} \\quad \\underline{\\hspace{3cm}}\n\\end{center}\n")
    out.append("\\noindent\\textbf{Desenhe uma situação com a palavra da atividade:}\n")
    out.append("\\begin{center}\n\\begin{tikzpicture}\n  \\draw[thick, dashed] (0,0) rectangle (12,4.5);\n\\end{tikzpicture}\n\\end{center}\n")
    out.append("\\end{exercicio}\n")
    return "\n".join(out)


def gerar_apendice(p: dict) -> str:
    ano = p["ano"]
    out = ["%% APÊNDICE — Caderno Complementar (gerado por expandir_volume.py)\n"]
    out.append("\\chapter{Caderno Complementar de Prática}\n")
    out.append(f"No {ano}º ano, o Caderno Complementar reforça cada folha Kumon com "
               "uma folha extra de caligrafia, análise silábica e escrita. Use como "
               "atividade de casa, reforço ou avaliação de apoio; cada folha é "
               "reproduzível (plancheta).\n")
    _cid = 0
    for i, f in enumerate(p["kumon"], start=1):
        _cid += 1
        out.append(_folha_extra(p, f, _cid))
    return "\n".join(out)


def _folha_extra(p, f, i):
    out = []
    titulo = f"Folha Complementar C-{i:02d} --- Reforço da Folha {f['id']} ({f['titulo']})"
    out.append(f"%% COMPLEMENTAR C-{i:02d}: {f['titulo'].upper()}\n")
    out.append(plancheta(titulo))
    out.append(exercicio(titulo))
    out.append("\\metadata{" + f"C-{i:02d}" + "}{Silábico-Alfabético}{EF02LP03, EF02LP04, EF02LP07}{D1}"
               + "{EF02LP04}{CNE/CEB nº 2/2012}\n")
    out.append("\\kumontiming{2}{90}\n")
    out.append(moldura_folha(nota="/10"))
    out.append("\\begin{enumerate}\n")
    out.append("  \\item \\textbf{Copie as palavras em letra cursiva:}\n  \\begin{center}\n  " +
               " \\quad ".join(f["palavras"][:4]) + "\n  \\end{center}\n  \\begin{center}\n  " +
               " \\quad ".join("\\underline{\\hspace{2.4cm}}" for _ in range(4)) + "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Escreva as sílabas das palavras:}\n  \\begin{center}\n  " +
               " \\quad ".join(f"{w.upper()} $=$ \\underline{{\\hspace{{1.5cm}}}} \\underline{{\\hspace{{1.5cm}}}}" for w in f["palavras"][:3]) + "\n  \\end{center}\n")
    grd = _grade_silabas(f["grafia"])
    if grd:
        out.append("  \\item \\textbf{Complete a tabela de sílabas:}\n")
        out.append(grd)
    else:
        out.append("  \\item \\textbf{Leia e escreva o número de sílabas de cada palavra:}\n  \\begin{center}\n  " +
                   " \\quad ".join(f"{w.upper()} $\\rightarrow$ \\underline{{\\hspace{{0.9cm}}}}" for w in f["palavras"][:4]) + "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Copie as frases em letra cursiva:}\n  \\begin{center}\n  " +
               f["frases"][0] + "\\\\\n  \\underline{\\hspace{12cm}}\\\\\n  " +
               (f["frases"][1] + "\\\\\n  \\underline{\\hspace{12cm}}" if len(f["frases"]) > 1 else "") +
               "\n  \\end{center}\n")
    out.append("  \\item \\textbf{Desenhe a frase:}\n  \\begin{center}\n  \\begin{tikzpicture}\n    \\draw[thick, dashed] (0,0) rectangle (12,4);\n  \\end{tikzpicture}\n  \\end{center}\n")
    out.append("\\end{enumerate}\n")
    out.append("\\end{exercicio}\n")
    return "\n".join(out)


def gerar_referencias(p: dict) -> str:
    ano = p["ano"]
    refs = [
        "BRASIL. Ministério da Educação. Base Nacional Comum Curricular. Brasília: MEC, 2018.",
        "BRASIL. Ministério da Educação. Política Nacional de Alfabetização (Decreto nº 9.765, de 11 de abril de 2019). Brasília: MEC, 2019.",
        "KUMON, Toru. Kumon: o segredo da mãe japonesa. Rio de Janeiro: Campus, 1996.",
        "DEHAENE, Stanislas. Os neurônios da leitura: como a ciência explica a nossa capacidade de ler. Porto Alegre: Penso, 2012.",
        "SOARES, Magda. Alfaletrar: toda criança pode aprender a ler e a escrever. São Paulo: Contexto, 2020.",
        "MORAIS, Artur Gomes de. Sistema de escrita alfabética. São Paulo: Melhoramentos, 2012.",
        "SALLES, Jerusa F. et al. Manual de avaliação neuropsicológica infantil. São Paulo: Vetor, 2016.",
        "CAPOVILLA, Alessandra G. S.; CAPOVILLA, Fernando C. Alfabetização: método fônico. São Paulo: Memnon, 2009.",
    ]
    out = ["%% REFERÊNCIAS — Volume %d (gerado por expandir_volume.py)\n" % ano]
    out.append("\\chapter{Referências Bibliográficas}\n")
    out.append("\\begin{itemize}[leftmargin=1.6em]\n" +
               "".join(f"  \\item {r}\n" for r in refs) + "\\end{itemize}\n")
    out.append("\\chapter{Tabela de Correspondência Fonema-Grafema Completa}\n")
    out.append("A tabela lista os fonemas do português brasileiro com suas grafias "
               "principais e as grafias trabalhadas neste volume.\n")
    out.append("\\begin{center}\n\\renewcommand{\\arraystretch}{1.5}\n"
               "\\begin{tabular}{lll}\n\\toprule\n**Fonema** & **Grafias** & **Exemplos** \\\\\n\\midrule\n")
    for fon, gra, ex in p["fonemas"]:
        out.append(f"{fon} & {gra} & {ex} \\\\\n")
    out.append("\\bottomrule\\end{tabular}\\end{center}\n")
    out.append("\\chapter{Glossário de Termos Técnicos}\n")
    out.append("\\begin{description}\n"
               "  \\item[Consciência fonológica] capacidade de refletir sobre os sons da fala, das sílabas aos fonemas.\n"
               "  \\item[Dígrafo] duas letras que representam um único fonema (ch, lh, nh, rr, ss, qu, gu).\n"
               "  \\item[Encontro consonantal] duas consoantes que ocorrem juntas na sílaba, cada uma com seu som (br, cr, bl, cl).\n"
               "  \\item[Fluência] leitura com precisão, ritmo adequado e expressividade, que libera recursos para a compreensão.\n"
               "  \\item[Fonema] menor unidade sonora da língua; o som de CH em chave é um fonema.\n"
               "  \\item[Grafema] representação escrita de um fonema; o dígrafo ch é um grafema de duas letras.\n"
               "  \\item[Nasalidade] passagem do ar pelo nariz na produção de sons (m, n, nh, ÃO, ÃE, ÕE).\n"
               "  \\item[Automatismo] leitura e escrita sem esforço consciente, obtido por treino distribuído e repetitivo.\n"
               "  \\item[Rastreio escolar] observação pedagógica sistemática e sequenciada que orienta o apoio; nunca diagnostica.\n"
               "  \\item[Rotas 1A-1D] percursos internos de progressão usados pelo professor para diferenciar o ensino por evidência.\n"
               "\\end{description}\n")
    out.append("\\chapter{Bibliografia Comentada}\n")
    out.append("Cada obra abaixo fundamenta uma peça do método. O professor pode "
                "ler a obra inteira ou o capítulo indicado para aprofundar.\n")
    biblio = [
        ("KUMON, Toru. Kumon: o segredo da mãe japonesa. Rio de Janeiro: Campus, 1996.",
         "Apresenta a filosofia do treino diário, da gradação mínima e da repetição até o automatismo."),
        ("DEHAENE, Stanislas. Os neurônios da leitura. Porto Alegre: Penso, 2012.",
         "Explica a via fonológica da leitura e por que a decodificação automatizada precede a compreensão."),
        ("SOARES, Magda. Alfaletrar: toda criança pode aprender a ler e a escrever. São Paulo: Contexto, 2020.",
         "Sintetiza a didática da alfabetização e a passagem do alfabético ao ortográfico."),
        ("MORAIS, Artur Gomes de. Sistema de escrita alfabética. São Paulo: Melhoramentos, 2012.",
         "Apoia a exploração das regularidades ortográficas do português, como as trabalhadas no 2º ano."),
        ("CAPOVILLA, Alessandra; CAPOVILLA, Fernando. Alfabetização: método fônico. São Paulo: Memnon, 2009.",
         "Descreve a sequência fônica e os exercícios de consciência fonológica que inspiram a Parte VII."),
        ("SALLES, Jerusa F. et al. Manual de avaliação neuropsicológica infantil. São Paulo: Vetor, 2016.",
         "Fundamenta a observação de leitura, escrita e funções executivas em contexto escolar."),
        ("BRASIL. Base Nacional Comum Curricular. Brasília: MEC, 2018.",
         "Documento oficial que define as habilidades de Língua Portuguesa por ano."),
        ("BRASIL. Política Nacional de Alfabetização (Decreto nº 9.765/2019). Brasília: MEC, 2019.",
         "Orienta a ênfase em evidências científicas e no método fônico na alfabetização."),
        ("CAGLIARI, Luiz Carlos. Alfabetização e linguística. São Paulo: Scipione, 1989.",
         "Discute a consciência fonológica na aquisição da escrita e o papel da variação linguística."),
        ("FERREIRO, Emilia; TEBEROSKY, Ana. Psicogênese da língua escrita. Porto Alegre: Artmed, 1999.",
         "Descreve as hipóteses de escrita que fundamentam a observação diagnóstica do professor."),
    ]
    out.append("\\begin{description}\n")
    for ref, com in biblio:
        out.append(f"  \\item[{ref}] {com}\n")
    out.append("\\end{description}\n")
    out.append("\\chapter{Integridade e Ética no Uso do Livro}\n")
    out.append("Este material é de uso pedagógico e reproduzível para fins "
               "escolares não comerciais. O rastreio integrado é observação "
               "pedagógica e nunca diagnóstico; a triagem não substitui a "
               "avaliação do profissional habilitado. Nenhum dado individual "
               "deve ser compartilhado sem autorização da família, conforme a "
               "LGPD (Lei nº 13.709/2018). O professor que aplicar as fichas do "
               "Volume Profissional deve ter a formação exigida pelo instrumento.\n"
               "Ao reproduzir as planchetas, preserve o cabeçalho com o nome, a "
               "data e o descritor; ao arquivar as folhas, use o Registro de "
               "Progresso individual, nunca comparações públicas entre alunos.\n")
    out.append("\\chapter{Conectividade com a Rede de Ensino}\n")
    out.append("Este volume se integra ao currículo da rede: os descritores "
               "CAEd e as matrizes do SPAECE estão mapeados nas unidades e "
               "avaliações; o planejamento bimestral conversa com o calendário "
               "escolar; o Registro de Progresso alimenta os conselhos de "
               "classe. A família recebe, na reunião de pais, o resumo do "
               "método e o combinado de 10 minutos diários de leitura em casa.\n")
    return "\n".join(out)


def gerar_main(p: dict) -> str:
    return f"""%% ============================================================
%% Volume {p['ano']} — Capa e Páginas Preliminares (gerado por expandir_volume.py)
%% ============================================================
\\documentclass{{alfabetizar}}

\\begin{{document}}

\\begin{{titlepage}}
\\begin{{tikzpicture}}[remember picture, overlay]
  \\fill[primary!10] (current page.south west) rectangle (current page.north east);
  \\fill[primary] (current page.north west) rectangle ([yshift=-4cm]current page.north east);
  \\fill[secondary] ([yshift=3cm]current page.south west) rectangle (current page.south east);
  \\node[anchor=north, font=\\fontsize{{36}}{{44}}\\selectfont\\bfseries\\color{{white}}, text width=14cm, align=center]
    at ([yshift=-2cm]current page.north) {{ALFABETIZAR BEM}};
  \\node[anchor=north, font=\\fontsize{{18}}{{22}}\\selectfont\\color{{white}}, text width=14cm, align=center]
    at ([yshift=-4.5cm]current page.north) {{Método Híbrido Fonico-Kumon\\\\com Técnica da Boquinha}};
  \\node[anchor=center, font=\\fontsize{{28}}{{34}}\\selectfont\\bfseries\\color{{primary}}, text width=12cm, align=center]
    at (current page.center) {{VOLUME {p['ano']}\\\\[0.5em]\\large {p['titulo_ano']}}};
  \\node[anchor=south, font=\\small\\color{{white}}, text width=14cm, align=center]
    at ([yshift=3.5cm]current page.south) {{\\textbf{{Alinhamento Curricular}}\\\\BNCC ({p['bncc']}) \\quad$\\cdot$\\quad Matriz CAEd \\quad$\\cdot$\\quad SPAECE}};
  \\node[anchor=south, font=\\normalsize\\color{{secondary}}, text width=14cm, align=center]
    at ([yshift=1.5cm]current page.south) {{\\textbf{{Autor:}} MarceloClaro\\\\Colaboradores: Agentes Especializados do Ecossistema OpenCode}};
  \\node[anchor=south, font=\\small\\color{{primary}}] at ([yshift=0.5cm]current page.south) {{Versão 1.0 --- Setembro de 2026}};
\\end{{tikzpicture}}
\\end{{titlepage}}

\\noindent\\textbf{{Modelo de escrita cursiva:}}\\\\[0.3em]
{{\\fontecursiva\\Large a b c d e f g h i j k l m n o p q r s t u v w x y z}}\\\\[0.3em]
{{\\fontecursiva\\Large A B C D E F G H I J K L M N O P Q R S T U V W X Y Z}}\\\\[0.5em]
\\hrule
\\vspace{{1em}}

\\pagenumbering{{roman}}
\\tableofcontents
\\clearpage

\\pagenumbering{{arabic}}

\\input{{parte1-fundamentacao}}
\\input{{parte2-sequencia-didatica}}
\\input{{parte3-kumon}}
\\input{{parte4-avaliacoes}}
\\input{{parte5-guia-professor}}
\\input{{parte6-guia-triagem}}
\\input{{parte7-sons-atividades}}
\\input{{referencias}}
\\input{{apendice}}

\\end{{document}}
"""


def gerar_checkpoints(p: dict) -> str:
    """Gera checkpoints do volume (SPEC-935-R211) e devolve texto a injetar."""
    from rastreio_integrado import Checkpoint, gerar_checkpoints as grc
    cps = []
    for i, (u, ficha) in enumerate(p["checkpoints"], start=1):
        cps.append(Checkpoint(
            arquivo=f"rastreio-u{i}",
            rotulo=f"Rastreio Integrado {i} --- após a Unidade {u['n']} ({u['curto']})",
            quando=f"aplicar ao fim da Unidade {u['n']}, antes de iniciar a próxima unidade. Tempo: 10--15 minutos.",
            dominio=u["dominio"],
            fichas=ficha,
            itens_auto=u["auto"],
            indicadores=u["indicadores"],
            encaminhamento=u["encaminhamento"],
        ))
    destino = RAIZ / f"Volume{p['ano']}" / "checkpoints"
    grc(destino=destino, cps=cps)
    return cps


def gerar_volume(ano: int) -> Path:
    p = PERFIS[ano]
    vol = RAIZ / f"Volume{ano}"
    vol.mkdir(exist_ok=True)

    # classe
    shutil.copy(RAIZ / "Volume1" / "alfabetizar.cls", vol / "alfabetizar.cls")

    partes = {
        "main.tex": gerar_main(p),
        "parte1-fundamentacao.tex": gerar_parte1(p),
        "parte2-sequencia-didatica.tex": gerar_parte2(p),
        "parte3-kumon.tex": gerar_parte3(p),
        "parte4-avaliacoes.tex": gerar_parte4(p),
        "parte5-guia-professor.tex": gerar_parte5(p),
        "parte6-guia-triagem.tex": gerar_parte6(p),
        "parte7-sons-atividades.tex": gerar_parte7(p),
        "referencias.tex": gerar_referencias(p),
        "apendice.tex": gerar_apendice(p),
    }
    for nome, conteudo in partes.items():
        (vol / nome).write_text(conteudo, encoding="utf-8")

    # checkpoints + injeção (a CDN das âncoras vem dos títulos das unidades)
    cps = gerar_checkpoints(p)
    _injetar_checkpoints(vol, p, cps)
    return vol


def _injetar_checkpoints(vol: Path, p: dict, cps) -> None:
    p2 = vol / "parte2-sequencia-didatica.tex"
    texto = p2.read_text(encoding="utf-8").split("\n")
    linhas = texto
    # âncoras: capítulo da unidade seguinte a cada checkpoint
    for cp, (u, _ficha) in zip(cps, p["checkpoints"]):
        prox = u["proxima"]
        alvo = ("%% FIM DA PARTE II" if prox is None
                else f"\\chapter{{Unidade {prox} ---")
        for i, linha in enumerate(linhas):
            if linha.startswith(alvo):
                mar = f"\\input{{checkpoints/{cp.arquivo}}}\n"
                if mar.strip() not in "\n".join(linhas):
                    linhas.insert(i, mar.rstrip("\n"))
                break
        else:
            print(f"  aviso: âncora '{alvo}' não encontrada no Volume {p['ano']}")
    p2.write_text("\n".join(linhas), encoding="utf-8")


def main() -> int:
    anos = [int(a) for a in sys.argv[1:]] or [2, 3, 4, 5]
    for ano in anos:
        try:
            vol = gerar_volume(ano)
            print(f"OK: Volume {ano} gerado em {vol}")
        except KeyError as e:
            print(f"ERRO: perfil do Volume {ano} não encontrado ({e})")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())