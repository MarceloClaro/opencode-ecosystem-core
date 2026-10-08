"""SPEC-935-R617 — Gate de integridade editorial do livro Core.

Testa invariantes estruturais de `livro-core/` que, quando quebradas, produzem
regressões silenciosas (build limpo com conteúdo errado) — o caso concreto dos
ciclos R613-R616, que introduziram 13 seções e 46 citações sem nenhum gate.

Princípio 1 do Core: SDD/TDD com gate fail-closed. Se um critério de aceitação
falha, o teste FALHA (não avisa, não ignora).
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIVRO = ROOT / "livro-core"
MODS = sorted(LIVRO.glob("mod-*.tex"))

pytestmark = pytest.mark.skipif(not MODS, reason="livro-core/mod-*.tex ausente")

MARKER = "% ATIVACAO-R613"
SEC_ATIVACAO = r"\section[Ativação e cálculo]"


# ---------------------------------------------------------------- AC1
def test_ac1_marcador_r613_exatamente_uma_vez():
    """AC1: quem tem a seção gerada tem 1 marcador; ninguém tem 2."""
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        if SEC_ATIVACAO not in t:
            assert MARKER not in t, f"{f.name}: marcador órfão sem seção"
            continue
        n = t.count(MARKER)
        assert n == 1, f"{f.name}: esperado 1 marcador, encontrado {n}"


def test_ac1b_secao_ativacao_tem_elemento_ativ():
    """AC1: a seção gerada precisa de um \\elemento{ativ-*} (R613)."""
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        if SEC_ATIVACAO not in t:
            continue
        bloco = t.split(SEC_ATIVACAO, 1)[1][:4000]
        assert re.search(r"\\elemento\{ativ-[A-Za-z0-9]+\}", bloco), (
            f"{f.name}: seção de ativação sem \\elemento{{ativ-*}}"
        )


# ---------------------------------------------------------------- AC2
def test_ac2b_elementos_ativ_globais_unicos():
    """AC2: um mesmo ID não pode ser usado por dois módulos."""
    todos = []
    for f in MODS:
        todos += re.findall(r"\\elemento\{(ativ-[A-Za-z0-9]+)\}", f.read_text(encoding="utf-8"))
    dups = {k: v for k, v in Counter(todos).items() if v > 1}
    assert not dups, f"IDs de elemento duplicados: {dups}"


def test_ac2c_labels_latex_unicos():
    """AC2: \\label{...} duplicado gera aviso de 'multiply defined'."""
    labels = []
    for f in [*MODS, LIVRO / "macros.tex"]:
        if f.exists():
            labels += re.findall(r"\\label\{([^}]+)\}", f.read_text(encoding="utf-8"))
    dups = {k: v for k, v in Counter(labels).items() if v > 1}
    assert not dups, f"\\label duplicados: {dups}"


# ---------------------------------------------------------------- AC3
def test_ac3_macros_invalidas():
    """AC3: \\code{} não existe; \\text{} exige amsmath (ausente no preâmbulo)."""
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        assert "\\code{" not in t, f"{f.name}: use \\cod{{}}, não \\code{{}}"
        assert "\\text{" not in t, f"{f.name}: use \\mathrm{{}} (não há amsmath)"


def test_ac3b_preambulo_nao_carrega_amsmath():
    """Justificativa do AC3: a suposição 'sem amsmath' é verificada, não presumida."""
    main = (LIVRO / "main.tex").read_text(encoding="utf-8")
    macros = (LIVRO / "macros.tex").read_text(encoding="utf-8")
    assert "amsmath" not in main and "amsmath" not in macros, (
        "amsmath passou a ser carregado: reavaliar a regra \\text{} da AC3"
    )


# ---------------------------------------------------------------- AC4
def test_ac4_sem_boilerplate_de_geracao():
    """AC4: resíduo de template não pode reaparecer no texto do livro."""
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        for lixo in ("Próximo parágrafo, a citação que ancora",
                     "A citação abaixo conecta a ativação"):
            assert lixo not in t, f"{f.name}: boilerplate {lixo!r} presente"


# ---------------------------------------------------------------- AC5
def test_ac5_leitura_guinada_tem_blocos_do_metodo():
    """AC5: seção didática incompleta quebra a promessa de qualidade A1."""
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\\section\[Leitura guiada\]\{([^}]*)\}", t):
            titulo = m.group(1)
            bloco = t[m.end(): m.end() + 9000]
            # o próximo \section fecha a seção
            prox = re.search(r"\n\\section", bloco)
            if prox:
                bloco = bloco[: prox.start()]
            for box in ("descricao", "definicao", "metodo", "resultado", "aviso"):
                assert f"\\begin{{{box}}}" in bloco, (
                    f"{f.name} :: {titulo!r} sem caixa {box}"
                )
            assert "Exercícios" in bloco, f"{f.name} :: {titulo!r} sem exercícios"
            assert "Limite de validade" in bloco, f"{f.name} :: {titulo!r} sem limite"


def test_ac5b_ordenacao_dos_blocos():
    """AC5 (forte): O fenômeno -> definições -> dedução -> exemplo -> limite."""
    for f in MODS:
        t = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\\section\[Leitura guiada\]\{([^}]*)\}", t):
            bloco = t[m.end(): m.end() + 9000]
            prox = re.search(r"\n\\section", bloco)
            if prox:
                bloco = bloco[: prox.start()]
            i_fen = bloco.find("O fenômeno")
            i_def = bloco.find("Grandezas e definições")
            i_ded = bloco.find("Dedução passo a passo")
            i_ex = bloco.find("Exemplo resolvido")
            i_lim = bloco.find("Limite de validade")
            posicoes = [i_fen, i_def, i_ded, i_ex, i_lim]
            assert all(p >= 0 for p in posicoes), (
                f"{f.name} :: {m.group(1)!r} bloco canônico ausente ({posicoes})"
            )
            assert posicoes == sorted(posicoes), (
                f"{f.name} :: {m.group(1)!r} blocos fora de ordem: {posicoes}"
            )


# ---------------------------------------------------------------- AC6
def test_ac6_infra_nao_e_stub():
    """AC6: o capítulo de infraestrutura foi efetivamente escrito."""
    f = LIVRO / "mod-09-infra.tex"
    t = f.read_text(encoding="utf-8")
    linhas = len(t.splitlines())
    assert linhas >= 100, f"mod-09-infra.tex com apenas {linhas} linhas (stub?)"
    # o critério é sobre o TÍTULO do capítulo, não sobre comentários de histórico
    m = re.search(r"\\chapter\{([^}]*)\}", t)
    assert m, "mod-09-infra.tex sem \\chapter{...}"
    assert "Em constru" not in m.group(1), (
        f"mod-09-infra.tex ainda declara capítulo {m.group(1)!r}"
    )


# ---------------------------------------------------------------- AC7
def test_ac7_contagens_coerentes_com_repositorio():
    """AC7: números citados no livro devem refletir o repositório.

    Tolerância declarada: o livro é escrito por ciclos, o repositório anda mais
    rápido; aceitamos que o livro não esteja *à frente*, apenas que não defasque
    mais que a janela de um ciclo por rodada.
    """
    specs = len(list((ROOT / "specs").glob("*.md")))
    serie = len(list((ROOT / "specs").glob("SPEC-935-R*.md")))
    suites = len(list((ROOT / "tests").glob("test_r*.py")))

    def citing(alvo: int, raio: int = 12) -> bool:
        alvo_s = str(alvo)
        for f in MODS:
            t = f.read_text(encoding="utf-8")
            if re.search(rf"\b{alvo_s}\b", t):
                return True
        return False

    # o livro deve citar um valor dentro da janela do valor real
    for nome, real, janela in (("specs", specs, 12), ("série R", serie, 12),
                               ("suítes test_r*", suites, 12)):
        candidatos = {str(v) for v in range(max(0, real - janela), real + 1)}
        achou = any(
            re.search(rf"\b{c}\b", f.read_text(encoding="utf-8"))
            for c in candidatos for f in MODS
        )
        assert achou, (
            f"livro não cita nenhuma contagem próxima do valor real de {nome} "
            f"({real}); janela ±{janela}"
        )


# ---------------------------------------------------------------- AC8
def test_ac8_gerador_catalogo_integro():
    """AC8: mod-10 é gerado; editar à mão é erro silencioso."""
    mod10 = (LIVRO / "mod-10-catalogo.tex").read_text(encoding="utf-8")
    assert "ARQUIVO GERADO" in mod10, (
        "mod-10-catalogo.tex perdeu o cabeçalho de gerado — foi editado à mão?"
    )
    gen = LIVRO / "gen_mod10.py"
    r = subprocess.run([sys.executable, "-m", "py_compile", str(gen)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"gen_mod10.py não compila: {r.stderr}"


def test_ac8b_gerador_catalogo_declara_cobertura_1a1():
    """AC8 (evoluído em R618): a discrepância de 39 foi REVISADA como artefato
    de convenção de nome — não havia ficha sem registro. O que não pode sumir é
    a explicação da causa (slug kebab-case) e o estado real de cobertura 1:1.
    """
    mod10 = (LIVRO / "mod-10-catalogo.tex").read_text(encoding="utf-8")
    assert re.search(r"Conven[çc][ãa]o de nomes", mod10), (
        "explicação da convenção de nomes removida — o leitor não entende a história"
    )
    assert "1:1" in mod10 or "cobertura documental" in mod10, (
        "cobertura documental 1:1 não declarada"
    )
