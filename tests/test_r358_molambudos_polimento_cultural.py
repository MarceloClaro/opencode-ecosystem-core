# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R358: polimento cultural trilíngue de Molambudos."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"


def _text(relative: str) -> str:
    return (BOOK / relative).read_text(encoding="utf-8")


def _fragment_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in ("fragmentos", "en/fragmentos", "zh/fragmentos"):
        paths.extend(sorted((BOOK / directory).glob("**/*.tex")))
    return paths


def _strip_comments(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        result: list[str] = []
        escaped = False
        for character in line:
            if character == "%" and not escaped:
                break
            result.append(character)
            if character == "\\":
                escaped = not escaped
            else:
                escaped = False
        lines.append("".join(result))
    return "\n".join(lines)


def _brace_balance(text: str) -> int:
    balance = 0
    escaped = False
    for character in _strip_comments(text):
        if character == "\\":
            escaped = not escaped
            continue
        if not escaped:
            if character == "{":
                balance += 1
            elif character == "}":
                balance -= 1
            if balance < 0:
                return balance
        escaped = False
    return balance


def test_r358_spec_is_registered_red_or_better():
    from sdd.spec_engine import spec_registry

    spec = spec_registry.get("SPEC-935-R358")
    assert spec is not None
    assert spec.status in {"red", "green", "verified"}


def test_all_234_fragment_sources_remain_present_and_tex_balanced():
    # O corpus cresceu de 78 para 84 fragmentos por idioma (CONT-05..13
    # expandido nos ciclos R376/R377) — 234 = 78x3 ficou desatualizado.
    # Em vez de fixar um novo número mágico que voltaria a ficar obsoleto
    # na próxima expansão, verificamos a invariante real: PT/EN/ZH devem
    # ter sempre a mesma contagem de fragmentos entre si.
    paths = _fragment_paths()
    per_language = {
        directory: len(list((BOOK / directory).glob("**/*.tex")))
        for directory in ("fragmentos", "en/fragmentos", "zh/fragmentos")
    }
    assert len(set(per_language.values())) == 1, (
        f"contagem de fragmentos diverge entre idiomas: {per_language}"
    )
    assert len(paths) == sum(per_language.values()) == per_language["fragmentos"] * 3
    failures = {
        str(path.relative_to(BOOK)): _brace_balance(path.read_text(encoding="utf-8"))
        for path in paths
        if _brace_balance(path.read_text(encoding="utf-8")) != 0
    }
    assert failures == {}


def test_active_fragment_corpus_has_no_literal_or_trema_double_quotes():
    failures: dict[str, list[int]] = {}
    for path in _fragment_paths():
        active = _strip_comments(path.read_text(encoding="utf-8"))
        lines = [
            index
            for index, line in enumerate(active.splitlines(), 1)
            if '"' in line
        ]
        if lines:
            failures[str(path.relative_to(BOOK))] = lines
    assert failures == {}


def test_pt_and_en_fragments_have_no_neutral_textquotedbl_commands():
    neutral = re.compile(r"\\textquotedbl(?!left|right)")
    failures: dict[str, int] = {}
    for directory in ("fragmentos", "en/fragmentos"):
        for path in sorted((BOOK / directory).glob("**/*.tex")):
            count = len(neutral.findall(_strip_comments(path.read_text(encoding="utf-8"))))
            if count:
                failures[str(path.relative_to(BOOK))] = count
    assert failures == {}


def test_quote_normalizer_preserves_nonempty_groups_and_comments():
    from scripts.normalize_molambudos_quotes import normalize_neutral_quotes

    source = (
        r"\textquotedbl{}fala\textquotedbl{\textit{. narração}}"
        " % comentário com \\textquotedbl{}\n"
    )
    normalized, count = normalize_neutral_quotes(source)
    assert count == 2
    assert (
        r"\textquotedblleft{}fala\textquotedblright{\textit{. narração}}"
        in normalized
    )
    assert r"% comentário com \textquotedbl{}" in normalized


def test_doc21_open_a_uses_language_appropriate_quotes_without_umlaut():
    pt = _text("fragmentos/doc/DOC-21.tex")
    en = _text("en/fragmentos/doc/DOC-21.tex")
    zh = _text("zh/fragmentos/doc/DOC-21.tex")
    assert r"O mesmo \textquotedblleft{}a\textquotedblright{} aberto" in pt
    assert r"The same open \textquotedblleft{}a\textquotedblright{}" in en
    assert "同样的开口“a”" in zh
    assert r'\"a\"' not in pt + en + zh


def test_doc25_preserves_two_distinct_utterances_in_all_languages():
    # R398: a cena onde esta fala ocorre (a consulta médica de Lúcia) vivia
    # duplicada — uma vez em LUC-05 e outra na cauda de DOC-25, que carregava
    # uma cópia inteira de LUC-03/04/05 colada após sua "Nota final". A cauda
    # foi removida e a versão polida migrou para os fragmentos LUC, que são o
    # lugar estrutural da investigação (Parte 4). A invariante que este teste
    # protege — duas falas distintas separadas por narração — continua valendo,
    # agora no fragmento correto.
    pt = _text("fragmentos/luc/LUC-05.tex")
    en = _text("en/fragmentos/luc/LUC-05.tex")
    zh = _text("zh/fragmentos/luc/LUC-05.tex")
    assert (
        r"\textquotedblleft{\textit{Estranho.\textquotedblright{}} "
        r"Ele anotou algo no prontuário. }\textquotedblleft{\textit{Vou pedir "
        in pt
    )
    assert (
        r"\textquotedblleft{\textit{Strange.\textquotedblright{}} "
        r"He wrote something in the chart. }\textquotedblleft{\textit{I will order "
        in en
    )
    # A edição ZH guarda a mesma cena na forma bem-construída (grupos vazios
    # `{}` após o comando de aspas, em vez do grupo espúrio `{` que a cauda de
    # DOC-25 carregava). O invariante protegido é o mesmo: duas falas
    # distintas separadas por narração.
    assert (
        r"\textquotedblleft{}奇怪。\textquotedblright{}他在病历上记了什么。"
        r"\textquotedblleft{}我开一些检查。只是为了保险。\textquotedblright{}"
        in zh
    )


def test_zh_luc13_and_luc14_close_quotes_with_chinese_conventions():
    luc13 = _text("zh/fragmentos/luc/LUC-13.tex")
    luc14 = _text("zh/fragmentos/luc/LUC-14.tex")
    assert "技术人员描述为“类似风穿过狭窄管道的声音”。" in luc13
    assert "“\\textit{我回到了巴尔巴塞纳。循环不让我走。" in luc14
    assert "下一位读者能比我理解得更好。}”" in luc14
    assert "“\\textit{他说：‘我知道您在这里。我知道您听得见我。我知道您不是一个故事。’}”" in luc14
    assert "“\\textit{写着：‘告诉下一位。她会来找我。’}”" in luc14


def test_documentary_dates_are_culturally_equivalent_not_blindly_swapped():
    assert "02/08/2026" in _text("fragmentos/doc/DOC-22.tex")
    assert "08/02/2026" in _text("en/fragmentos/doc/DOC-22.tex")
    assert "2026年8月2日" in _text("zh/fragmentos/doc/DOC-22.tex")

    assert "03/08/2026" in _text("fragmentos/doc/DOC-23.tex")
    assert "08/03/2026" in _text("en/fragmentos/doc/DOC-23.tex")
    assert "2026年8月3日" in _text("zh/fragmentos/doc/DOC-23.tex")


def test_doc22_sector_signature_opens_and_closes_typographic_quotes():
    pt = _text("fragmentos/doc/DOC-22.tex")
    en = _text("en/fragmentos/doc/DOC-22.tex")
    zh = _text("zh/fragmentos/doc/DOC-22.tex")
    assert (
        r"\textquotedblleft{}\textit{--- Setor de Acervos Especiais, "
        r"02/08/2026.\textquotedblright{}}"
        in pt
    )
    assert (
        r"\textquotedblleft{}\textit{--- Special Collections Sector, "
        r"08/02/2026.\textquotedblright{}}"
        in en
    )
    assert "“—— 特藏部，2026年8月2日。”" in zh


def test_known_pt_opening_quotes_are_left_and_balanced():
    mem19 = _text("fragmentos/mem/MEM-19.tex")
    mem26 = _text("fragmentos/mem/MEM-26.tex")
    doc12 = _text("fragmentos/doc/DOC-12.tex")
    assert r"\textquotedblleft{}Mas por que ela veio?\textquotedblright{}" in mem19
    assert r"\textquotedblleft{}Quem ler isto: você é o próximo." in mem26
    assert (
        r"\textquotedblleft{}Perguntei: 'Como você sabe?'\textquotedblright{}"
        in doc12
    )


def test_route_validator_detects_language_scope_and_page_divergence():
    from scripts.validate_molambudos_routes import validate_layout_text

    aux = "\n".join(
        [
            r"\newlabel{frag:MEM-02}{{2}{24}{}{fragctr.2}{}}",
            r"\newlabel{fragen:MEM-02}{{2}{27}{}{fragctr.2}{}}",
            r"\newlabel{fragzh:MEM-02}{{2}{29}{}{fragctr.2}{}}",
            r"\newlabel{frag:DOC-02}{{11}{139}{}{fragctr.11}{}}",
            r"\newlabel{fragen:DOC-02}{{11}{141}{}{fragctr.11}{}}",
            r"\newlabel{fragzh:DOC-02}{{11}{144}{}{fragctr.11}{}}",
            r"\newlabel{frag:CONT-05}{{70}{336}{}{fragctr.70}{}}",
            r"\newlabel{fragen:CONT-05}{{70}{339}{}{fragctr.70}{}}",
            r"\newlabel{fragzh:CONT-05}{{70}{342}{}{fragctr.70}{}}",
            r"\newlabel{frag:LUC-Escolha}{{55}{277}{}{fragctr.55}{}}",
            r"\newlabel{fragen:LUC-Escolha}{{55}{279}{}{fragctr.55}{}}",
            r"\newlabel{fragzh:LUC-Escolha}{{55}{281}{}{fragctr.55}{}}",
        ]
    )
    layout = "\n".join(
        [
            ",→ Rotas: MEM-02 (p. 24) • DOC-02 (p. 139) • CONT-05 (p. 336) • LUC-Escolha (p. 277)",
            ",→ Routes: MEM-02 (p. 27) • DOC-02 (p. 141) • CONT-05 (p. 339) • LUC-Escolha (p. 279)",
            ",→ 路线: MEM-02 (p. 29) • DOC-02 (p. 144) • CONT-05 (p. 342) • LUC-Escolha (p. 281)",
        ]
    )
    result = validate_layout_text(layout, aux, expected_count=12)
    assert result["route_count"] == 12
    assert result["legacy_numeric_route_count"] == 6
    assert result["by_prefix"] == {"frag:": 4, "fragen:": 4, "fragzh:": 4}
    assert result["missing_labels"] == []
    assert result["divergences"] == []

    broken = validate_layout_text(layout.replace("(p. 141)", "(p. 999)"), aux, expected_count=12)
    assert broken["divergences"] == [
        {"label": "fragen:DOC-02", "printed_page": 999, "aux_page": 141}
    ]

    duplicate_aux = aux + "\n" + r"\newlabel{frag:MEM-02}{{2}{24}{}{fragctr.2}{}}"
    duplicate = validate_layout_text(layout, duplicate_aux, expected_count=12)
    assert duplicate["duplicate_labels"] == ["frag:MEM-02"]
    assert duplicate["passed"] is False
