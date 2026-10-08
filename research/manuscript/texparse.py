# -*- coding: utf-8 -*-
"""Parser LaTeX compartilhado do motor (SPEC-935-R706).

Extraído e generalizado de gerar_docx.py (legado TDAH, intacto): escapes,
runs inline, expansão de citações a partir do .aux e iteração de blocos
(seção, subseção, item, quadro, centro, parágrafo).
"""
from __future__ import annotations

import re

ESC = [
    (r"\c{c}", "ç"), (r"\c{C}", "Ç"),
    (r"\~a", "ã"), (r"\~o", "õ"), (r"\~A", "Ã"), (r"\~O", "Õ"),
    (r"\'a", "á"), (r"\'e", "é"), (r"\'i", "í"), (r"\'o", "ó"), (r"\'u", "ú"),
    (r"\'A", "Á"), (r"\'E", "É"), (r"\'I", "Í"), (r"\'O", "Ó"), (r"\'U", "Ú"),
    (r"\^a", "â"), (r"\^e", "ê"), (r"\^o", "ô"), (r"\^A", "Â"), (r"\^E", "Ê"),
    (r"\`a", "à"), (r"\`A", "À"), (r"\%", "%"), (r"\&", "&"), (r"\~", " "),
]

BOLD_RE = re.compile(r"\\(textbf|textit)\{((?:[^{}]|\{[^{}]*\})*)\}")


def deescape(s: str) -> str:
    for antigo, novo in ESC:
        s = s.replace(antigo, novo)
    return s


def inline(s: str) -> str:
    s = s.replace("``", '"').replace("''", '"')
    s = re.sub(r"---", "—", s)
    s = re.sub(r"--", "–", s)
    return s


def runs(texto: str) -> list[tuple[str, bool, bool]]:
    """Divide texto em (trecho, negrito, itálico) respeitando chaves."""
    partes: list[tuple[str, bool, bool]] = []
    for pedaco in re.split(r"(\\(?:textbf|textit)\{(?:[^{}]|\{[^{}]*\})*\})", texto):
        if not pedaco:
            continue
        m = BOLD_RE.match(pedaco)
        if m:
            partes.append((inline(deescape(m.group(2))), m.group(1) == "textbf",
                           m.group(1) == "textit"))
        else:
            partes.append((inline(deescape(pedaco)), False, False))
    return partes


class Citacoes:
    """Rótulos autor-data lidos do .aux (rótulo principal + YEAR)."""

    def __init__(self, aux_texto: str) -> None:
        self.rotulos = dict(re.findall(r"\\bibcite\{([^}]+)\}\{([^}]+)\}", aux_texto))
        self.anos = dict(re.findall(r"\\bibciteYEAR\{([^}]+)\}\{([^}]+)\}", aux_texto))

    def autor(self, chave: str) -> str:
        cru = re.sub(r"[{}]", "", self.rotulos.get(chave, chave))
        cru = re.sub(r"\s+e\s+", "; ", cru)
        cru = re.sub(r"\s+\d{4}[a-z]?\.?$", "", cru)
        saida = []
        for parte in [p.strip() for p in cru.split(";")]:
            baixo = parte.lower()
            if baixo == "et al.":
                saida.append("et al.")
            elif " et al." in baixo:
                base = parte[:baixo.index(" et al.")]
                saida.append(base.upper() + " et al.")
            else:
                saida.append(parte.upper())
        return "; ".join(saida)

    def rotulo(self, chave: str) -> str:
        autor = self.autor(chave)
        ano = self.anos.get(chave, "")
        return autor + (", " + ano if ano else "")

    def expandir(self, texto: str) -> str:
        def _on(m: re.Match) -> str:
            chaves = [k.strip() for k in m.group(1).split(",")]
            return "; ".join(f"{self.autor(k)} ({self.anos.get(k, '')})" for k in chaves)

        def _c(m: re.Match) -> str:
            chaves = [k.strip() for k in m.group(1).split(",")]
            return "(" + "; ".join(self.rotulo(k) for k in chaves) + ")"
        texto = re.sub(r"\\citeonline\{([^}]*)\}", _on, texto)
        return re.sub(r"\\cite\{([^}]*)\}", _c, texto)


COMANDOS_IGNORAR = re.compile(
    r"\\(vspace|thispagestyle|newpage|pagenumbering|setcounter|renewcommand|setlength"
    r"|renewcommand|providecommand|pagestyle|fancyhf|renewcommand|labelsep)\{.*\}|\\newpage"
)


def iter_blocos(tex_texto: str):
    """Gera ('secao'|'subsecao'|'item'|'quadro'|'centro'|'para', ...) sem expandir citações."""
    linhas = tex_texto.splitlines()
    i, n = 0, len(linhas)
    while i < n:
        linha = linhas[i].strip()
        if not linha or linha.startswith("%") or COMANDOS_IGNORAR.match(linha):
            i += 1
            continue
        m = re.match(r"\\section\{(.*)\}\s*$", linha)
        if m:
            yield ("secao", m.group(1)); i += 1; continue
        m = re.match(r"\\subsection\{(.*)\}\s*$", linha)
        if m:
            yield ("subsecao", m.group(1)); i += 1; continue
        if linha.startswith(r"\begin{enumerate}"):
            i += 1; continue
        if linha.startswith(r"\end{enumerate}"):
            i += 1; continue
        if linha.startswith(r"\item"):
            yield ("item", re.sub(r"^\\item\s*", "", linha)); i += 1; continue
        if linha.startswith(r"\begin{center}"):
            i += 1; partes = []
            while i < n and not linhas[i].strip().startswith(r"\end{center}"):
                t = linhas[i].strip()
                if t:
                    partes.append(t)
                i += 1
            i += 1
            txt = " ".join(partes)
            txt = re.sub(r"\{\\bfseries\s*([^}]*)\}", r"\1", txt)
            yield ("centro", txt); continue
        if linha.startswith(r"\begin{quadro}"):
            cap = re.match(r"\\begin\{quadro\}\{(.*)\}\s*$", linha)
            legenda = cap.group(1) if cap else "Quadro"
            i += 1; corpo = []
            while i < n and not linhas[i].strip().startswith(r"\end{quadro}"):
                corpo.append(linhas[i]); i += 1
            i += 1
            yield ("quadro", legenda, "\n".join(corpo)); continue
        if linha.startswith("\\"):
            i += 1; continue
        buf = [linha]; i += 1
        while i < n and linhas[i].strip() and not linhas[i].strip().startswith("\\"):
            buf.append(linhas[i].strip()); i += 1
        yield ("para", " ".join(b for b in buf if not b.startswith("%")))


REGRAS_TABULAR = re.compile(
    r"\\(toprule|midrule|bottomrule|hline|cline\{[^}]*\}|addlinespace(\[[^\]]*\])?)"
)


def _divide_celulas(linha: str) -> list[str]:
    """Divide linha de tabular em células por & (respeitando \\&)."""
    return [c.strip() for c in re.split(r"(?<!\\)&", linha)]


def parse_tabular(bloco: str) -> tuple[list[str], list[list[str]]]:
    """Extrai (cabecalho, linhas) de um ambiente tabular.

    Primeira linha de dados vira cabeçalho; linhas de regra são ignoradas;
    formatação de célula é preservada para runs().
    """
    m = re.search(r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}([\s\S]*?)\\end\{tabular\}", bloco)
    corpo = m.group(2) if m else bloco
    dados: list[list[str]] = []
    for bruta in re.split(r"\\\\", corpo):
        linha = bruta.strip()
        if not linha:
            continue
        linha = REGRAS_TABULAR.sub("", linha).strip()
        if not linha or set(linha) <= {"-", "|", " "}:
            continue
        cels = _divide_celulas(linha)
        if any(c.strip() for c in cels):
            dados.append([c.strip() for c in cels])
    if not dados:
        return [], []
    return dados[0], dados[1:]


def parse_bbl(bbl_texto: str) -> list[str]:
    """Extrai o corpo de cada referência do .bbl (texto ABNT com escapes).

    Retorna lista de strings (uma por \\bibitem), sem o \\abntrefinfo.
    """
    partes = re.split(r"\\bibitem\[[^\]]*\]\{[^}]+\}", bbl_texto)
    refs = []
    for parte in partes[1:]:
        parte = re.sub(r"\\abntrefinfo(\{[^{}]*\}){3}", "", parte)
        parte = re.sub(r"\\providecommand(\{[^{}]*\})(\{[^{}]*\})?", "", parte)
        parte = re.sub(r"\\abntbstabout\{[^}]*\}", "", parte)
        corpo = parte.strip()
        if corpo.startswith("{") and corpo.rstrip().endswith("}"):
            corpo = corpo.strip()[1:].rstrip()
            if corpo.endswith("}"):
                corpo = corpo[:-1]
        corpo = re.sub(r"\s+", " ", corpo).strip()
        if corpo:
            refs.append(corpo)
    return refs
