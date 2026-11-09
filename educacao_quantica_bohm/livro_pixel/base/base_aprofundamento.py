#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aprofundamento específico por conceito e por lente.

A camada usa os campos estruturados de ``base_fichas`` para acrescentar
um dossiê de evidência e um exercício curto a cada lauda. O objetivo é
substituir texto genérico por evidência rastreável, sem repetir o mesmo
dossiê nas dez lentes do mesmo conceito.

O bloco é adaptativo: laudas curtas recebem dossiê e exercício; laudas
já cheias recebem apenas o dossiê compacto. A decisão usa a contagem de
palavras do corpo e o espaço liberado por uma substituição de texto
genérico.
"""
from __future__ import annotations

import html
import re

from .base_fichas import Ficha

GRAU_LABEL = {
    "A": "definição ou teste consolidado",
    "B": "evidência experimental ou metodológica com limites",
    "C": "resultado exploratório ou interpretativo",
}

FAIXA_CURTA = 120
FAIXA_MEDIA = 160
FAIXA_LONGA = 185

LIMITE_PAGINA = {
    "ideia": 220,
    "analogia": 190,
    "pratica": 225,
    "laboratorio": 235,
    "erro": 180,
    "alem": 215,
    "dialogo": 175,
    "etica": 168,
    "vida": 165,
    "checkpoint": 162,
}

MIDIA_LABORATORIO = ("<table", "<figure", "<pre", 'class="resultado"')


def limite_pagina(lente_id: str, corpo: str) -> int:
    """Limite efetivo de palavras por página.

    Laudas de laboratório com tabela, figura, código ou caixa de resultado
    têm menos espaço útil; o limite cai para evitar que a lauda transborde.
    """
    limite = LIMITE_PAGINA.get(lente_id, 10**9)
    if lente_id == "laboratorio" and any(tag in corpo for tag in MIDIA_LABORATORIO):
        return min(limite, 195)
    return limite

ROTULO_DOSSIE = "DOSSIÊ"
ROTULO_EXERCICIO = "EXERCÍCIO"


def esc(valor: str) -> str:
    return html.escape(valor, quote=False)


def _cita(valor: str) -> str:
    """Coloca um campo da ficha entre aspas sem duplicar o ponto final."""
    limpo = valor.strip().rstrip(".")
    return f"“{esc(limpo)}”"


GENERICOS = {
    "A fonte discute o conceito e suas consequências.",
    "Não há garantia de generalização para outros contextos.",
}


def _marca(c: dict, valor: str) -> str:
    """Marca o conceito apenas quando o campo da ficha é genérico."""
    if valor in GENERICOS:
        return f" (conceito: {esc(c['titulo'])})"
    return ""


def _grau(ficha: Ficha) -> str:
    return GRAU_LABEL.get(ficha.grau, "evidência declarada pela ficha")


def _fonte(ficha: Ficha, nivel: int) -> str:
    return esc(ficha.fonte_curta) if nivel == 0 else ficha.fonte_link


def _leitura(ficha: Ficha, nivel: int) -> str:
    return esc(ficha.leitura_curta) if nivel == 0 else ficha.leitura_link


def _dossie(conteudo: str) -> str:
    return (
        f'<div class="dossie"><span class="rotulo-dossie">{ROTULO_DOSSIE}</span>'
        f"{conteudo}</div>"
    )


def _exercicio(conteudo: str) -> str:
    return (
        f'<div class="exercicio"><span class="rotulo-dossie">{ROTULO_EXERCICIO}</span>'
        f"{conteudo}</div>"
    )


def _p(conteudo: str) -> str:
    return f"<p>{conteudo}</p>"


def _corpo_ideia(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    if nivel == 0:
        dossie = _p(
            f"A ficha {ficha.codigo} liga a ideia à fonte {_fonte(ficha, nivel)}; "
            f"a evidência é {esc(_grau(ficha))}."
        )
        exercicio = _p(
            f"Explique com suas palavras por que a frase sobre {titulo} não autoriza "
            f"dizer mais do que a fonte permite."
        )
    elif nivel == 2:
        dossie = _p(
            f"A ficha {ficha.codigo} ancora a proposição em {_fonte(ficha, nivel)}; "
            f"grau {ficha.grau} ({esc(_grau(ficha))}). Limite: "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
        exercicio = _p(
            f"Formule uma consequência testável de {_cita(ficha.frase)} e indique "
            f"qual observação a refutaria."
        )
    else:
        dossie = _p(
            f"A ficha {ficha.codigo} ancora a ideia em {_fonte(ficha, nivel)}; "
            f"grau {ficha.grau} ({esc(_grau(ficha))})."
        )
        exercicio = _p(
            f"Explique por que a frase sobre {titulo} não autoriza mais do que a "
            f"fonte permite."
        )
    return dossie, exercicio


def _corpo_analogia(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    dossie = _p(
        f"Teste da imagem: a ficha registra a prática {_cita(ficha.pratica)} e o "
        f"medido {_cita(ficha.medido)}{_marca(c, ficha.medido)}."
    )
    if nivel == 0:
        exercicio = _p(
            f"Desenhe a analogia de {titulo} e escreva um resultado que ela não "
            f"conseguiria prever."
        )
    else:
        exercicio = _p(
            f"Desenhe a analogia de {titulo} e escreva o resultado que ela não "
            f"conseguiria prever."
        )
    return dossie, exercicio


def _corpo_pratica(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    if nivel == 2:
        dossie = _p(
            f"A ficha {ficha.codigo} registra como medido "
            f"{_cita(ficha.medido)}{_marca(c, ficha.medido)}. "
            f"Resultado bruto: {esc(ficha.resultado)}."
        )
        exercicio = _p(
            f"Repita a prática com outra amostra ou seed e escreva o que a diferença "
            f"não prova sobre {titulo}."
        )
    else:
        dossie = _p(
            f"A ficha {ficha.codigo} registra como medido "
            f"{_cita(ficha.medido)}{_marca(c, ficha.medido)}."
        )
        exercicio = _p(
            f"Repita a prática e explique por que o número não prova "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    return dossie, exercicio


def _corpo_laboratorio(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    if nivel == 2:
        dossie = _p(
            f"Grau {ficha.grau} ({esc(_grau(ficha))}); o número não prova "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}. "
            f"Fonte do protocolo: {_fonte(ficha, nivel)}."
        )
        exercicio = _p(
            f"Proponha uma replicação independente que poderia refutar "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    elif nivel == 0:
        dossie = _p(
            f"A ficha {ficha.codigo} diz que a evidência é {esc(_grau(ficha))}; o "
            f"número não prova {_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
        exercicio = _p(
            f"Explique com suas palavras por que o resultado não autoriza essa "
            f"conclusão sobre {esc(c['titulo'])}."
        )
    else:
        dossie = _p(
            f"Grau {ficha.grau} ({esc(_grau(ficha))}); o número não prova "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
        exercicio = _p(
            f"Explique por que o resultado não autoriza essa conclusão sobre "
            f"{esc(c['titulo'])}."
        )
    return dossie, exercicio


def _corpo_erro(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    if nivel == 0:
        dossie = _p(
            f"A ficha mede {_cita(ficha.medido)} e admite "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.medido)}."
        )
    else:
        dossie = _p(
            f"A ficha mede {_cita(ficha.medido)} e admite "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.medido)}. "
            f"O erro está em tratar esse registro como definição de {titulo}."
        )
    exercicio = _p(
        f"Escreva um contraexemplo que separe esse registro de {titulo}."
    )
    return dossie, exercicio


def _corpo_alem(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    dossie = _p(
        f"Leitura: {_leitura(ficha, nivel)}. Fonte: {_fonte(ficha, nivel)}."
    )
    if nivel == 2:
        exercicio = _p(
            f"Leia a fonte complementar e formule uma pergunta de pesquisa que ela "
            f"deixa aberta sobre {titulo}."
        )
    else:
        exercicio = _p(
            f"Anote uma pergunta que a leitura não responde sobre {titulo}."
        )
    return dossie, exercicio


def _corpo_dialogo(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    if nivel == 0:
        dossie = _p(
            f"Outra explicação possível: "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}. Fonte: "
            f"{_fonte(ficha, nivel)}."
        )
        exercicio = _p(
            f"Defenda essa explicação por dois minutos e peça a alguém para "
            f"refutá-la em {titulo}."
        )
    else:
        dossie = _p(
            f"Hipótese rival: {_cita(ficha.nao_prova)}"
            f"{_marca(c, ficha.nao_prova)}. Fonte: {_fonte(ficha, nivel)}."
        )
        exercicio = _p(
            f"Defenda a hipótese rival e peça a alguém para refutá-la em {titulo}."
        )
    return dossie, exercicio


def _corpo_etica(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    if nivel == 0:
        dossie = _p(
            f"A ficha considera a evidência {esc(_grau(ficha))}; o limite é "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    else:
        dossie = _p(
            f"Grau {ficha.grau} ({esc(_grau(ficha))}); o limite é "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    exercicio = _p(
        f"Liste um grupo afetado por {titulo} e uma mitigação, declarando esse limite."
    )
    return dossie, exercicio


def _corpo_vida(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    dossie = _p(
        f"Prática: {_cita(ficha.pratica)}. Limite: "
        f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
    )
    exercicio = _p(
        f"Aplique a prática a uma situação cotidiana e declare o limite de {titulo}."
    )
    return dossie, exercicio


def _corpo_checkpoint(c: dict, ficha: Ficha, nivel: int) -> tuple[str, str]:
    titulo = esc(c["titulo"])
    if nivel == 0:
        dossie = _p(
            f"A ficha considera a evidência {esc(_grau(ficha))}. Frase: "
            f"{_cita(ficha.frase)}; limite: "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    elif nivel == 2:
        dossie = _p(
            f"Grau {ficha.grau} ({esc(_grau(ficha))}). Frase: "
            f"{_cita(ficha.frase)}; limite: "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    else:
        dossie = _p(
            f"Grau {ficha.grau} ({esc(_grau(ficha))}). Frase: "
            f"{_cita(ficha.frase)}; limite: "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}."
        )
    exercicio = _p(
        f"Responda à tarefa sobre {titulo} e registre uma pergunta aberta."
    )
    return dossie, exercicio


CORPOS = {
    "ideia": _corpo_ideia,
    "analogia": _corpo_analogia,
    "pratica": _corpo_pratica,
    "laboratorio": _corpo_laboratorio,
    "erro": _corpo_erro,
    "alem": _corpo_alem,
    "dialogo": _corpo_dialogo,
    "etica": _corpo_etica,
    "vida": _corpo_vida,
    "checkpoint": _corpo_checkpoint,
}


def contar_palavras(texto_html: str) -> int:
    limpo = re.sub(r"<[^>]+>", " ", texto_html)
    limpo = re.sub(r":::\s*\{[^}]*\}", " ", limpo)
    return len(re.sub(r"\s+", " ", limpo).split())


def _frase_curta(c: dict, ficha: Ficha, nivel: int, lente_id: str) -> str:
    titulo = esc(c["titulo"])
    if lente_id == "laboratorio":
        return (
            f"A ficha {ficha.codigo} declara o limite "
            f"{_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)}; "
            f"o número não prova essa conclusão sobre {titulo}."
        )
    if lente_id == "ideia":
        return (
            f"A ficha {ficha.codigo} ancora a ideia em {_fonte(ficha, nivel)} e "
            f"declara o limite {_cita(ficha.nao_prova)}"
            f"{_marca(c, ficha.nao_prova)}."
        )
    return (
        f"A ficha {ficha.codigo} registra {_cita(ficha.medido)} e declara o "
        f"limite {_cita(ficha.nao_prova)}{_marca(c, ficha.nao_prova)} sobre {titulo}."
    )


def bloco_aprofundamento(
    c: dict,
    ficha: Ficha,
    nivel: int,
    lente_id: str,
    palavras_atuais: int = 0,
    substituiu_generico: bool = False,
    forcar: str | None = None,
) -> str:
    """Monta o dossiê e o exercício conforme o espaço disponível."""
    fabrica = CORPOS.get(lente_id)
    if fabrica is None:
        return ""
    dossie, exercicio = fabrica(c, ficha, nivel)

    if forcar == "dossie":
        return _dossie(dossie)
    if forcar == "frase":
        return _p(_frase_curta(c, ficha, nivel, lente_id))

    if substituiu_generico or palavras_atuais < FAIXA_CURTA:
        return _dossie(dossie) + _exercicio(exercicio)
    if palavras_atuais < FAIXA_MEDIA:
        return _dossie(dossie) + _exercicio(exercicio)
    if palavras_atuais < FAIXA_LONGA:
        return _dossie(dossie)

    # Lauda já cheia: uma única frase específica, sem caixa extra.
    return _p(_frase_curta(c, ficha, nivel, lente_id))


PADRAO_PROTOCOLO = re.compile(
    r"<p><strong>Protocolo de bancada:</strong>.*?</p>\s*",
    flags=re.S,
)
PADRAO_OL = re.compile(
    r"<ol>\s*<li>Escreva a previsão.*?</ol>\s*",
    flags=re.S,
)
PADRAO_OBSERVAR = re.compile(
    r"<p><strong>O que observar:</strong> não basta acertar.*?</p>\s*",
    flags=re.S,
)


def tem_generico(corpo: str) -> bool:
    return bool(PADRAO_PROTOCOLO.search(corpo))


def substituir_generico(corpo: str, bloco: str) -> tuple[str, bool]:
    """Remove o protocolo genérico e insere o bloco após a ponte.

    A remoção é feita em três partes independentes para não engolir a
    ponte sonora, que fica entre o protocolo e a lista de passos.
    """
    removeu = False
    for padrao in (PADRAO_PROTOCOLO, PADRAO_OL, PADRAO_OBSERVAR):
        if padrao.search(corpo):
            corpo = padrao.sub("", corpo, count=1)
            removeu = True
    if not removeu:
        return corpo, False
    ponte = re.search(r'<p class="ponte">.*?</p>', corpo, flags=re.S)
    if ponte:
        posicao = ponte.end()
        return corpo[:posicao] + "\n" + bloco + corpo[posicao:], True
    return corpo.rstrip() + "\n" + bloco, True
