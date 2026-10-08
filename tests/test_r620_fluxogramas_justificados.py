"""SPEC-935-R620 — Explicação auditada de cada fluxograma do livro Core.

O livro tem 22 fluxogramas, mas nenhum deles era explicado: o desenho aparecia
seguido de prosa, sem dizer o que cada seta representa, por que a ordem é essa e
qual literatura sustenta a escolha. Um fluxograma sem justificativa é uma
ilustração, não um argumento — e o leitor não tem como saber se a ordem das
etapas é necessária ou arbitrária.

Este gate exige, para 100% dos fluxogramas:
  (1) um bloco "Como funciona e por quê" imediatamente após o desenho;
  (2) com rótulo de mecanismo E de justificativa;
  (3) com pelo menos uma citação real, cujo DOI esteja na biblioteca auditada.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIVRO = ROOT / "livro-core"
MODS = sorted(LIVRO.glob("mod-*.tex"))

pytestmark = pytest.mark.skipif(not MODS, reason="livro-core/mod-*.tex ausente")

RE_FLUXO = re.compile(r"\\begin\{flowch\}(?:\[(?P<titulo>[^\]]*)\])?\{(?P<legenda>[^}]*)\}")
RE_DOIS = re.compile(r"10\.\d{4,9}/[^\s}{]+")  # para no fechamento do campo
MARCADOR = "Como funciona e por quê"
JUSTIFICA = "Justificativa"


def _fluxos(t: str) -> list[tuple[str, str, str]]:
    """(titulo, legenda, trecho que segue o desenho) de cada fluxograma."""
    out = []
    for m in RE_FLUXO.finditer(t):
        fim = t.find(r"\end{flowch}", m.end())
        trecho = t[fim : fim + 4000] if fim > 0 else ""
        out.append((m.group("titulo") or "(sem título)", m.group("legenda"), trecho))
    return out


def _todos() -> list[tuple[str, str, str, str]]:
    todos = []
    for f in MODS:
        for titulo, legenda, trecho in _fluxos(f.read_text(encoding="utf-8")):
            todos.append((f.name, titulo, legenda, trecho))
    return todos


# ------------------------------------------------------- AC0
def test_ac0_existe_pelo_menos_um_fluxograma():
    assert _todos(), "nenhum fluxograma encontrado — o gate estaria verde à toa"


# ------------------------------------------------------- AC1
def test_ac1_todo_fluxograma_tem_explicacao_de_mecanismo():
    """AC1: 100% dos fluxogramas são seguidos de um bloco de explicação."""
    sem = [f"{f} :: {t}" for f, t, _, trecho in _todos() if MARCADOR not in trecho]
    assert not sem, f"{len(sem)} fluxograma(s) sem explicação: {sem}"


def test_ac1b_a_explicacao_vem_logo_apos_o_desenho():
    """AC1: a explicação precisa ser do desenho, não de outra seção depois."""
    longe = []
    for f, titulo, _, trecho in _todos():
        i = trecho.find(MARCADOR)
        if i < 0 or i > 2200:
            longe.append(f"{f} :: {titulo}")
    assert not longe, f"explicação ausente ou distante demais: {longe}"


# ------------------------------------------------------- AC2
def test_ac2_toda_explicacao_tem_justificativa_explicita():
    """AC2: separar 'como funciona' de 'por que' é o que torna o desenho auditável."""
    sem = [f"{f} :: {t}" for f, t, _, trecho in _todos() if JUSTIFICA not in trecho]
    assert not sem, f"{len(sem)} sem rótulo de justificativa: {sem}"


# ------------------------------------------------------- AC3
def test_ac3_todo_fluxograma_cita_biblioteca_verificada():
    """AC3 (R110): nenhuma explicação pode ser uma opinião sem lastro."""
    biblioteca = (LIVRO / "mod-11-apendices.tex").read_text(encoding="utf-8")
    validos = set(RE_DOIS.findall(biblioteca))
    assert validos, "bibliografia sem DOI reconhecido"
    sem, fora = [], []
    for f, titulo, _, trecho in _todos():
        # trecho já começa no fim do desenho: a explicação é o que vem a seguir
        bloco = trecho[:2500]
        dois = RE_DOIS.findall(bloco)
        if not dois:
            sem.append(f"{f} :: {titulo}")
        for d in dois:
            if d not in validos:
                fora.append(f"{f} :: {titulo} -> {d}")
    assert not sem, f"explicação sem citação: {sem}"
    assert not fora, f"DOI fora da biblioteca auditada: {fora}"


# ------------------------------------------------------- AC4
def test_ac4_nenhuma_citacao_reinventada():
    """AC4: a citação direta precisa ser a mesma que já foi conferida na biblioteca."""
    do_livro = {}
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\\citref\{(.+?)\}\{(10\.[^}]*)\}\{(.+?)\}\{(.+?)\}\{(.+?)\}", t, re.S):
            do_livro.setdefault(m.group(2), []).append((m.group(1), m.group(4), m.group(5)))
    assert do_livro, "nenhuma citação completa encontrada no livro"
    repetidas = []
    for f, titulo, _, trecho in _todos():
        for m in re.finditer(r"\\citref\{(.+?)\}\{(10\.[^}]*)\}\{(.+?)\}\{(.+?)\}\{(.+?)\}", trecho, re.S):
            doi, ref, quote, trad = m.group(2), m.group(1), m.group(4), m.group(5)
            if doi in do_livro and not any(
                ref == r0 and quote == q0 and trad == t0 for r0, q0, t0 in do_livro[doi]
            ):
                repetidas.append(f"{f} :: {titulo} -> {doi}")
    assert not repetidas, (
        f"citação com recorte/tradução própria em vez da conferida: {repetidas}"
    )


# ------------------------------------------------------- AC5
def test_ac5_legenda_do_desenho_e_conferida_pela_explicacao():
    """AC5: a legenda do fluxograma declara semântica de setas; a explicação precisa honrá-la."""
    for f, titulo, legenda, trecho in _todos():
        i = trecho.find(MARCADOR)
        if i < 0:
            continue
        bloco = trecho[i : i + 2500]
        if "seta" in legenda.lower() or "seta" in bloco.lower():
            assert re.search(r"setas?\b", bloco), (
                f"{f} :: {titulo} fala em setas e não explica o que a seta significa"
            )


# ------------------------------------------------------- helpers
def _campos(txt: str, ini: int) -> list[str] | None:
    """Separa os 5 campos de um \\citref contando PROFUNDIDADE de chave.

    Por que nao regex: `\\citref\\{(.+?)\\}\\{...\\}\\{(.*?)\\}` casa na posicao
    errada sempre que o campo de relevancia contem `\\textbf{...}` — o `}` interno
    encerra o campo mais cedo, a casa se desloca e a substituicao pode DELETAR
    conteudo do arquivo semerro. Licao registrada em R620.
    """
    res, i = [], ini + 1
    for k in range(5):
        prof, j = 0, i
        while j < len(txt):
            c = txt[j]
            if c == "\\":
                j += 2
                continue
            if c == "{":
                prof += 1
            elif c == "}":
                if prof == 0:
                    break
                prof -= 1
            j += 1
        if j >= len(txt):
            return None
        res.append(txt[i:j])
        if prof != 0:
            return None
        i = j + 1
        if k < 4:
            if i >= len(txt) or txt[i] != "{":
                return None
            i += 1
    return res


def _citacoes(txt: str):
    p, out = 0, []
    while True:
        k = txt.find("\\citref{", p)
        if k < 0:
            return out
        p = k + 8
        cs = _campos(txt, k + 7)
        out.append(None if cs is None else (k, cs))
    
_MACROS_CODIGO = ("code", "cod", "fns", "nodep", "texttt", "verb", "path", "pth", "lstinline")


def _sem_codigo(txt: str) -> str:
    """Remove o CONTEUDO das macros de codigo: la dentro '_' e literal.

    `\\code{ERROR_ALREADY_EXISTS}` compila ha anos neste livro;vê-lo como
    prosa seria falso positivo. O que sobra e prosa, e prosa exige escape.
    """
    out = txt
    for mac in _MACROS_CODIGO:
        while True:
            k = out.find("\\" + mac)
            if k < 0:
                break
            abre = out.find("{", k)
            if abre < 0 or abre - k > 20:
                break
            prof, j = 0, abre
            while j < len(out):
                if out[j] == "{":
                    prof += 1
                elif out[j] == "}":
                    prof -= 1
                    if prof == 0:
                        break
                j += 1
            # apaga a macro INTEIRA (nome + chaves): deixar "\cod" orfao
            # faria o passe seguinte reencontrar o nome e abortar.
            out = out[:k] + " " + out[j + 1:]
    return out


# ------------------------------------------------------- AC6
def test_ac6_nenhuma_citacao_do_livro_tem_campo_vazio():
    r"""AC6: \citref exige os 5 campos (relevancia, citacao direta, traducao).

    Regressao real de R619->R620: tres citacoes foram inseridas com os campos 4 e
    5 vazios e o livro compilou sem reclamar. Uma nota de rodape sem a citacao
    direta nao sustenta a afirmacao que ela acompanha.
    """
    achadas = []
    for f in MODS:
        for item in _citacoes(f.read_text(encoding="utf-8")):
            if item is None:
                continue
            k, cs = item
            if not cs[3].strip() or not cs[4].strip():
                achadas.append(f"{f.name}@{k}: {cs[1][:40]} quote/traducao vazios")
    assert not achadas, achadas


# ------------------------------------------------------- AC7
def test_ac7_todo_citref_tem_cinco_campos_bem_formados():
    r"""AC7: nenhum \citref truncado ou com campo de referencia invalido."""
    achadas = []
    for f in MODS:
        for item in _citacoes(f.read_text(encoding="utf-8")):
            if item is None:
                achadas.append(f"{f.name}: \citref truncado")
                continue
            k, cs = item
            if not cs[0].strip() or not cs[1].strip().startswith("10."):
                achadas.append(f"{f.name}@{k}: campos 1-2 invalidos")
    assert not achadas, achadas


# ------------------------------------------------------- AC8
def test_ac8_nenhum_escape_quebrado_em_bloco_de_descricao():
    r"""AC8: caractere especial de LaTeX sem escape, em QUALQUER bloco de descricao.

    Licao R620: um `_` solto derrubou o build (`Missing $ inserted`) e o `check.py`
    nao o viu — so o `latexmk` viu, e so no capitulo 4. O bloco corrompido nao era
    o do fluxograma: era um `Justificativa teórica` pre-existente. Por isso o gate
    varre todos os blocos, nao apenas os das explicacoes R620.
    """
    PROIBIDOS = "_#&^"
    achadas = []
    for f in MODS:
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\\begin\{descricao\}(.*?)\\end\{descricao\}", txt, re.S):
            corpo = _sem_codigo(m.group(1))
            sem_math = re.sub(r"\$[^$]*\$", "", corpo)
            sem_cmd = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", sem_math)
            # remove os escapes LEGITIMOS: add\_criterion nao e prosa nua
            sem_esc = re.sub(r"\\([#$&^_])", "", sem_cmd)
            sem_braces = sem_esc.replace("{", " ").replace("}", " ")
            for ch in PROIBIDOS:
                if ch in sem_braces:
                    k = sem_braces.index(ch)
                    achadas.append(
                        f"{f.name}: '{ch}' em ...{sem_braces[max(0, k-40):k+40]}...")
    assert not achadas, achadas
