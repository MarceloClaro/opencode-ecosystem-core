# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R406: coerência factual entre as três edições.

Até o R405, a busca por contradições era **reativa**: os defeitos apareciam por
acaso, ao medir outra coisa. Foi assim que se descobriu que a edição chinesa
matava o Dr. Oliveira em 1989 e que a portuguesa o matava em 1981 — enquanto o
resto da obra o tem desaparecido em 13/jun/1979, sem corpo, e vivo até 2026,
quando entrega o diário no arquivo.

As três edições contavam finais diferentes para o mesmo personagem, e o elo
que elas quebravam é o central: Oliveira é a ponte entre Joaquim e Lúcia. Se
ele morre em 1981, o diário não chega em 2026 e o ciclo não fecha.

Num livro que se apresenta como arquivo pericial fiel, quem bate na
contradição é o leitor atento — exatamente o leitor que a obra cultiva, porque
a estrutura fragmentária o obriga a montar o caso.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_canone_sem_contradicoes_nas_tres_edicoes():
    from scripts.molambudos_canone import verificar

    resultado = verificar()
    assert resultado["ok"], (
        "contradições factuais encontradas:\n"
        + "\n".join(
            f"  [{p['tipo']}] {p['fato']} — edição {p['edicao']}"
            + (f" — {p.get('arquivos')}" if p.get("arquivos") else "")
            for p in resultado["problemas"]
        )
    )


def test_as_tres_edicoes_tem_o_mesmo_numero_de_fragmentos():
    from scripts.molambudos_canone import verificar

    contagens = set(verificar()["fragmentos_por_edicao"].values())
    assert len(contagens) == 1, f"contagem diverge entre edições: {contagens}"


def test_verificador_detecta_contradicao_reintroduzida(tmp_path, monkeypatch):
    """Um verificador que não falha quando o defeito volta é decoração.

    Reintroduz a afirmação exata que este ciclo removeu — Oliveira morto em
    1981 — e exige que o verificador a acuse, apontando edição e arquivo.
    """
    from scripts import molambudos_canone as canone

    corpo = tmp_path / "livro"
    for edicao in ("fragmentos", "en/fragmentos", "zh/fragmentos"):
        alvo = corpo / edicao
        alvo.mkdir(parents=True)
        (alvo / "DOC-07.tex").write_text(
            "1853 1907 1917 1979 1980 2026 62 72 81 1.263 1,263\n"
            "desapareceu em 13 de junho de 1979\n"
            "disappeared on 13 June 1979\n"
            "1979年6月13日失踪\n"
            "CRM-MG 28.391 CRM-MG 4.892 CRM-MG 3.117\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(canone, "BOOK", corpo)
    assert canone.verificar()["ok"], "o corpus de controle deveria estar limpo"

    (corpo / "fragmentos" / "DOC-07.tex").write_text(
        (corpo / "fragmentos" / "DOC-07.tex").read_text(encoding="utf-8")
        + "\nDr. Heitor Oliveira faleceu em 1981.\n",
        encoding="utf-8",
    )
    r = canone.verificar()
    assert not r["ok"], "contradição reintroduzida passou despercebida"
    tipos = {p["tipo"] for p in r["problemas"]}
    assert "contradição" in tipos, f"tipos detectados: {tipos}"
    atingidos = [p for p in r["problemas"] if p["tipo"] == "contradição"]
    assert any("DOC-07.tex" in p.get("arquivos", []) for p in atingidos), (
        "o verificador não apontou o arquivo culpado"
    )


def test_cli_do_verificador_sai_com_codigo_de_erro():
    """O verificador precisa ser usável como gate: sai != 0 quando há problema."""
    r = subprocess.run(
        [sys.executable, "-m", "scripts.molambudos_canone"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"cânone com problemas:\n{r.stdout}"
    assert "sem contradições" in r.stdout
