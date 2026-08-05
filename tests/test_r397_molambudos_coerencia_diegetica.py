# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R397: coerência diegética de Molambudos.

Os guardas anteriores (R238–R395) validam a camada *mecânica* da obra:
compila, geometria de página, aspas tipográficas, datas, contagem de rotas.
Nenhum deles pergunta se o arquivo **contradiz a si mesmo** de um jeito que o
leitor percebe — que é exatamente o que quebra a imersão em um livro cujo
dispositivo central é um arquivo forense que se apresenta como confiável.

Este módulo cobre essa camada:

1. A cadeia de pacientes (1.259 → 1.260 Joaquim → 1.261 Oliveira →
   1.262 Lúcia → 1.263 leitor) não pode atribuir ao leitor um número que a
   própria obra já deu a um personagem.
2. O protocolo de leitura ("Como Ler Este Livro") não pode mandar o leitor
   procurar uma etiqueta de navegação que os fragmentos não usam.
3. A autocontagem do livro (quantos fragmentos, quantas rotas, quantos modos
   de leitura) tem de bater com o que o livro de fato contém.
4. Nenhum fragmento pode fechar grupos LaTeX despejando chaves no fim do
   arquivo — isso equilibra o arquivo sem corrigir o vazamento e faz a
   ênfase tipográfica vazar pelo resto do fragmento.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"

EDITIONS = {
    "pt": {"fragments": "fragmentos", "front": "frontmatter"},
    "en": {"fragments": "en/fragmentos", "front": "en/frontmatter"},
    "zh": {"fragments": "zh/fragmentos", "front": "zh/frontmatter"},
}

# Etiqueta de navegação que cada edição usa ao final de cada fragmento.
ROUTE_LABEL = {"pt": "↪ Rotas:", "en": "↪ Routes:", "zh": "↪ 路线:"}

# O número do leitor no ciclo. Fixado por LUC-12 ("Paciente 1.262 encerra seu
# ciclo. O paciente 1.263 é quem abrir esta caixa."), por DOC-24, por CONT-09 e
# pelo protocolo em frontmatter/como_ler.tex.
READER_NUMBER = {"pt": "1.263", "en": "1,263", "zh": "1,263"}

# 1.261 é o Dr. Heitor Oliveira (DOC-16: "O paciente 1.261 sou eu", assinado
# "--- Paciente 1.261"); 1.262 é a Dra. Lúcia Mendes (LUC-10, LUC-11).
CHARACTER_NUMBERS = {
    "pt": {"1.261": "Dr. Heitor Oliveira", "1.262": "Dra. Lúcia Mendes"},
    "en": {"1,261": "Dr. Heitor Oliveira", "1,262": "Dr. Lúcia Mendes"},
    "zh": {"1,261": "Dr. Heitor Oliveira", "1,262": "Dra. Lúcia Mendes"},
}

# Fragmentos em que o número aparece endereçando **o leitor** em segunda
# pessoa (formulários preenchidos pelo leitor, laudos emitidos pela leitura).
# São exatamente os que o R397 corrigiu; o teste impede a regressão.
READER_ADDRESSED = ("cont/CONT-04.tex", "cont/CONT-05.tex", "doc/DOC-09.tex")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fragment_paths(edition: str) -> list[Path]:
    return sorted((BOOK / EDITIONS[edition]["fragments"]).glob("**/*.tex"))


def _unclosed_brace_positions(text: str) -> list[int]:
    """Posições dos '{' que nunca fecham, respeitando \\escape e % comentário."""
    stack: list[int] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if character == "%":
            newline = text.find("\n", index)
            index = len(text) if newline < 0 else newline + 1
            continue
        if character == "{":
            stack.append(index)
        elif character == "}" and stack:
            stack.pop()
        index += 1
    return stack


# ---------------------------------------------------------------------------
# 1. Cadeia de pacientes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_fragmentos_que_enderecam_o_leitor_usam_o_numero_do_leitor(edition: str) -> None:
    """CONT-04/CONT-05/DOC-09 falam com o leitor: têm de usar 1.263, não 1.261.

    Antes do R397, os três chamavam o leitor de "paciente 1.261" — o número
    que DOC-16 já havia dado ao Dr. Oliveira. Na leitura linear o leitor
    encontrava "O paciente 1.261 é você" quatro páginas depois de "O paciente
    1.261 sou eu", no clímax do dispositivo central da obra.
    """
    base = BOOK / EDITIONS[edition]["fragments"]
    reader = READER_NUMBER[edition]
    for relative in READER_ADDRESSED:
        path = base / relative
        if not path.exists():
            continue
        text = _text(path)
        assert reader in text, (
            f"{edition}/{relative} endereça o leitor mas não usa o número dele "
            f"({reader}); a cadeia de pacientes ficou incoerente"
        )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_o_numero_do_leitor_nunca_e_atribuido_a_um_personagem(edition: str) -> None:
    """Nenhum fragmento pode dizer que o leitor "é" um número de personagem."""
    claims = []
    for path in _fragment_paths(edition):
        text = _text(path)
        for number, character in CHARACTER_NUMBERS[edition].items():
            # "1.261 é você" / "1,261 is you" / "患者1,261" seguido de 您/你
            patterns = (
                rf"{re.escape(number)}\s+é você",
                rf"{re.escape(number)}\s+is you",
                rf"REGISTRO:\}}\s*{re.escape(number)}",
                rf"RECORD:\}}\s*{re.escape(number)}",
            )
            for pattern in patterns:
                if re.search(pattern, text):
                    claims.append(f"{path.name}: {number} ({character})")
    assert not claims, (
        "fragmento(s) atribuem ao leitor um número que pertence a um "
        f"personagem: {claims}"
    )


def test_a_cadeia_de_pacientes_e_aritmeticamente_continua() -> None:
    """1.259 → 1.260 → 1.261 → 1.262 → 1.263 sem buracos nem repetição de papel."""
    text = "\n".join(_text(path) for path in _fragment_paths("pt"))
    for number in ("1.259", "1.260", "1.261", "1.262", "1.263"):
        assert number in text, f"elo {number} ausente da cadeia de pacientes"


# ---------------------------------------------------------------------------
# 2. Protocolo de leitura versus o que os fragmentos realmente fazem
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_protocolo_manda_procurar_a_etiqueta_que_os_fragmentos_usam(edition: str) -> None:
    """"Como Ler Este Livro" não pode apontar para uma etiqueta inexistente.

    O R389 converteu "↪ Links:" em "↪ Rotas:" nos 84 fragmentos e não
    atualizou o protocolo — o leitor era instruído a procurar uma etiqueta
    que o livro tinha deixado de usar.
    """
    protocol = _text(BOOK / EDITIONS[edition]["front"] / "como_ler.tex")
    # O protocolo cita a etiqueta **sem** o dois-pontos de propósito: "Rotas:"
    # é o marcador legível por máquina de
    # scripts/validate_molambudos_routes.py::MARKERS, e o extrator trata como
    # linha de rotas qualquer linha impressa que comece por ele. Com o
    # dois-pontos, a própria página de instruções passava a ser lida como uma
    # linha de rotas e arrastava 4 rotas curadas para a contagem, quebrando a
    # paridade fonte×impresso do preflight R362.
    label = ROUTE_LABEL[edition].rstrip(":")
    assert label in protocol, (
        f"protocolo {edition} não menciona a etiqueta real {label!r}"
    )
    assert ROUTE_LABEL[edition] not in protocol, (
        f"protocolo {edition} reproduz o marcador {ROUTE_LABEL[edition]!r} com "
        "dois-pontos: o extrator de rotas vai ler a página de instruções como "
        "uma linha de rotas"
    )
    stale = {"pt": "↪ Links", "en": "↪ Links", "zh": "↪ 链接"}[edition]
    assert stale not in protocol, (
        f"protocolo {edition} ainda manda procurar {stale!r}, que nenhum "
        "fragmento usa"
    )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_todos_os_fragmentos_usam_a_etiqueta_de_rota_da_sua_edicao(edition: str) -> None:
    label = ROUTE_LABEL[edition]
    missing = [
        path.name for path in _fragment_paths(edition) if label not in _text(path)
    ]
    assert not missing, f"fragmentos {edition} sem a etiqueta {label!r}: {missing}"


# ---------------------------------------------------------------------------
# 3. A autocontagem do livro bate com o livro
# ---------------------------------------------------------------------------


def _declared_counts(edition: str) -> tuple[int, int]:
    """(fragmentos, rotas) declarados no protocolo daquela edição."""
    protocol = _text(BOOK / EDITIONS[edition]["front"] / "como_ler.tex")
    numbers = [int(value) for value in re.findall(r"\\textbf\{(\d+)", protocol)]
    assert len(numbers) >= 2, f"protocolo {edition} não declara as duas contagens"
    return numbers[0], numbers[1]


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_a_contagem_declarada_de_fragmentos_bate_com_a_real(edition: str) -> None:
    declared, _ = _declared_counts(edition)
    real = len(_fragment_paths(edition))
    assert declared == real, (
        f"protocolo {edition} anuncia {declared} fragmentos, o livro tem {real}"
    )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_a_contagem_declarada_de_rotas_bate_com_as_chamadas_reais(edition: str) -> None:
    _, declared = _declared_counts(edition)
    real = sum(
        len(re.findall(r"\\rota\{", _text(path))) for path in _fragment_paths(edition)
    )
    assert declared == real, (
        f"protocolo {edition} anuncia {declared} rotas, os fragmentos fazem "
        f"{real} chamadas \\rota{{}}"
    )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_o_numero_de_modos_de_leitura_anunciado_bate_com_a_lista(edition: str) -> None:
    """"de quatro formas distintas" seguido de exatamente 4 itens numerados."""
    protocol = _text(BOOK / EDITIONS[edition]["front"] / "como_ler.tex")
    listed = len(re.findall(r"\\noindent\\textbf\{(\d+)\.", protocol))
    words = {
        "pt": {"três": 3, "quatro": 4},
        "en": {"three": 3, "four": 4},
        "zh": {"三种": 3, "四种": 4},
    }[edition]
    announced = next(
        (count for word, count in words.items() if word in protocol), None
    )
    assert announced is not None, f"protocolo {edition} não anuncia o número de modos"
    assert announced == listed, (
        f"protocolo {edition} anuncia {announced} formas de leitura mas lista {listed}"
    )


# ---------------------------------------------------------------------------
# 4. Integridade de grupos LaTeX (ênfase não pode vazar)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_nenhum_fragmento_despeja_chaves_no_fim_do_arquivo(edition: str) -> None:
    """Fechar grupos em bloco no EOF equilibra o arquivo sem corrigir o vazamento.

    DOC-25 acumulava 52 grupos abertos por `\\textquotedblleft{` (que deveria
    ser `\\textquotedblleft{}`) e os fechava todos numa linha de 52 chaves no
    fim. O arquivo compilava limpo e com saldo zero, mas todo o texto após a
    primeira aspa vazada renderizava dentro de \\textit aninhados — a ênfase
    alternava errado até o fim do fragmento.
    """
    offenders = []
    for path in _fragment_paths(edition):
        if re.search(r"\n\}{2,}\s*$", _text(path)):
            offenders.append(path.name)
    assert not offenders, (
        f"fragmentos {edition} fecham grupos despejando chaves no EOF: {offenders}"
    )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_nenhum_fragmento_deixa_grupo_aberto(edition: str) -> None:
    offenders = []
    for path in _fragment_paths(edition):
        unclosed = _unclosed_brace_positions(_text(path))
        if unclosed:
            offenders.append(f"{path.name}({len(unclosed)})")
    assert not offenders, f"fragmentos {edition} com grupo aberto: {offenders}"


# ---------------------------------------------------------------------------
# 5. Convergência da navegação (R400)
# ---------------------------------------------------------------------------
#
# Regra de arquitetura narrativa declarada pelo autor: **todas as rotas levam
# ao Epílogo**, e o leitor nunca pode ficar preso num ciclo infinito. Os ciclos
# em si são temáticos e ficam ("O ciclo recomeça"); o que não pode existir é
# ciclo do qual não haja saída.
#
# Antes do R400 nenhuma rota apontava para o Epílogo em nenhum idioma, e o
# grafo tinha um sorvedouro de 48 fragmentos: quem navegava por saltos
# circulava ali para sempre sem nunca alcançar o fim da obra.

EPILOGO = "EPI-01"


def _grafo_de_rotas(edition: str):
    """(nós, arestas) das rotas de uma edição, incluindo o Epílogo."""
    nos = {path.stem for path in _fragment_paths(edition)}
    nos.add(EPILOGO)
    arestas = []
    for path in _fragment_paths(edition):
        for destino in re.findall(r"\\rota\{([A-Z]{3,4}-(?:\d+|[A-Za-z][A-Za-z-]*))\}", _text(path)):
            if destino in nos:
                arestas.append((path.stem, destino))
    return nos, arestas


def _alcancam_epilogo(nos: set[str], arestas: list[tuple[str, str]]) -> set[str]:
    """Conjunto de fragmentos a partir dos quais o Epílogo é alcançável."""
    reverso: dict[str, list[str]] = {n: [] for n in nos}
    for origem, destino in arestas:
        reverso[destino].append(origem)
    vistos = {EPILOGO}
    pilha = [EPILOGO]
    while pilha:
        atual = pilha.pop()
        for anterior in reverso.get(atual, ()):
            if anterior not in vistos:
                vistos.add(anterior)
                pilha.append(anterior)
    return vistos - {EPILOGO}


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_o_epilogo_e_alcancavel_de_todos_os_fragmentos(edition: str) -> None:
    nos, arestas = _grafo_de_rotas(edition)
    alcancam = _alcancam_epilogo(nos, arestas)
    presos = sorted(nos - alcancam - {EPILOGO})
    assert not presos, (
        f"na edição {edition}, {len(presos)} fragmento(s) não têm percurso de "
        f"rotas até o Epílogo: {presos}"
    )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_o_epilogo_recebe_rotas_e_nao_emite_nenhuma(edition: str) -> None:
    """O Epílogo é o sorvedouro: chega-se nele e não se sai."""
    _, arestas = _grafo_de_rotas(edition)
    entram = [a for a in arestas if a[1] == EPILOGO]
    saem = [a for a in arestas if a[0] == EPILOGO]
    assert entram, f"nenhuma rota chega ao Epílogo na edição {edition}"
    assert not saem, f"o Epílogo emite rotas na edição {edition}: {saem}"


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_nenhum_ciclo_aprisiona_o_leitor(edition: str) -> None:
    """Ciclos podem existir — são o tema da obra — mas todos têm saída.

    A propriedade verificada é mais forte que 'existe saída': como o Epílogo é
    alcançável de todo fragmento (teste acima), todo ciclo necessariamente tem
    uma aresta que sai dele. Aqui a checagem é direta, sem depender disso.
    """
    nos, arestas = _grafo_de_rotas(edition)
    saida: dict[str, set[str]] = {n: set() for n in nos}
    for origem, destino in arestas:
        saida[origem].add(destino)

    # componentes fortemente conexos (Tarjan iterativo simplificado via DFS dupla)
    ordem: list[str] = []
    visto: set[str] = set()

    def _mergulha(inicio: str) -> None:
        pilha = [(inicio, iter(sorted(saida[inicio])))]
        visto.add(inicio)
        while pilha:
            no, it = pilha[-1]
            for prox in it:
                if prox not in visto:
                    visto.add(prox)
                    pilha.append((prox, iter(sorted(saida[prox]))))
                    break
            else:
                ordem.append(pilha.pop()[0])

    for no in sorted(nos):
        if no not in visto:
            _mergulha(no)

    entrada: dict[str, set[str]] = {n: set() for n in nos}
    for origem, destino in arestas:
        entrada[destino].add(origem)

    atribuido: set[str] = set()
    componentes: list[set[str]] = []
    for no in reversed(ordem):
        if no in atribuido:
            continue
        comp, pilha = {no}, [no]
        atribuido.add(no)
        while pilha:
            atual = pilha.pop()
            for anterior in entrada[atual]:
                if anterior not in atribuido and anterior in visto:
                    atribuido.add(anterior)
                    comp.add(anterior)
                    pilha.append(anterior)
        componentes.append(comp)

    presos = [
        sorted(c) for c in componentes
        if len(c) > 1 and not any(d not in c for n in c for d in saida[n])
    ]
    assert not presos, (
        f"edição {edition}: ciclo(s) sem nenhuma saída — o leitor fica preso: {presos}"
    )


@pytest.mark.parametrize("edition", sorted(EDITIONS))
def test_nenhum_fragmento_fica_fora_da_rede_de_rotas(edition: str) -> None:
    """Todo fragmento tem de ser alcançável por navegação, não só na leitura linear.

    Antes do R400, 14 fragmentos não tinham nenhuma rota de entrada — DOC-17,
    DOC-20 a DOC-27, LUC-13, LUC-14, MEM-18, MEM-21 e MEM-27. O leitor que
    seguia as setas jamais chegava a eles; só os encontrava folheando na ordem
    linear. Num livro que se apresenta como hipertexto impresso, isso é
    conteúdo prometido e não entregue por um dos três modos de leitura.
    """
    nos, arestas = _grafo_de_rotas(edition)
    com_entrada = {destino for _, destino in arestas}
    # O Epílogo é destino, nunca origem; os fragmentos é que precisam de entrada.
    orfaos = sorted(n for n in nos if n != EPILOGO and n not in com_entrada)
    assert not orfaos, (
        f"edição {edition}: {len(orfaos)} fragmento(s) sem nenhuma rota de "
        f"entrada, inalcançáveis por navegação livre: {orfaos}"
    )
